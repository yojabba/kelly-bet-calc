import streamlit as st
import pandas as pd
import datetime
import math

# ---------- Helper Functions ----------
def american_to_decimal(odds):
    if odds > 0:
        return round((odds / 100) + 1, 4)
    else:
        return round((100 / abs(odds)) + 1, 4)

def decimal_to_american(odds):
    if odds >= 2.0:
        return f"+{int((odds - 1) * 100)}"
    else:
        return f"-{int(100 / (odds - 1))}"

def implied_prob(decimal_odds):
    return 1 / decimal_odds

def remove_margin_equal(odds_a, odds_b):
    imp_a, imp_b = implied_prob(odds_a), implied_prob(odds_b)
    total = imp_a + imp_b
    return imp_a / total, imp_b / total

def remove_margin_log(odds_a, odds_b):
    log_a, log_b = math.log(odds_a), math.log(odds_b)
    total_log = log_a + log_b
    return log_b / total_log, log_a / total_log

def fair_odds(prob):
    return round(1 / prob, 2)

def calc_edge(true_prob, your_prob):
    return round((true_prob - your_prob) * 100, 2)

def kelly_stake(bankroll, odds, win_prob, fraction):
    b = odds - 1
    q = 1 - win_prob
    kelly_fraction = ((b * win_prob) - q) / b
    if kelly_fraction <= 0:
        return 0.0
    return round(bankroll * kelly_fraction * fraction, 2)

def classify_message(prob, edge):
    if edge >= 5 and prob >= 60:
        return "💣 Nuke"
    elif edge >= 2 and prob >= 50:
        return "✨ Sprinkle"
    elif edge <= 0:
        return "🗑️ Trash"
    else:
        return "🔍 Worth a Look"

# ---------- Streamlit UI ----------
st.title("📊 True Odds + Value Calculator (EM, LOG & Avg)")

st.write("""
Input odds for both sides of the sharp market, plus your odds. We'll calculate the true probability,
fair odds, edge %, and suggested Kelly stake using Equal Margin, LOG, and an average of both.
""")

# Input Section
col1, col2 = st.columns(2)
with col1:
    sharp_odds_a_input = st.number_input("Sharp Book Odds - Side A (American)", value=-104)
with col2:
    sharp_odds_b_input = st.number_input("Sharp Book Odds - Side B (American)", value=-110)

side_choice = st.radio("Which side are you betting on?", ["Side A", "Side B"])
your_odds_input = st.number_input("Your Odds (American)", value=125)
bankroll = st.number_input("Bankroll", min_value=1.0, value=1000.0, step=10.0)
kelly_fraction = st.slider("Fraction of Kelly to Use", min_value=0.1, max_value=1.0, value=0.5, step=0.1)

calculate = st.button("Calculate")

if calculate:
    sharp_a = american_to_decimal(sharp_odds_a_input)
    sharp_b = american_to_decimal(sharp_odds_b_input)
    your_odds = american_to_decimal(your_odds_input)
    your_prob = implied_prob(your_odds)

    results = []
    methods = {
        "Equal Margin": remove_margin_equal,
        "LOG Method": remove_margin_log
    }

    method_probs = []
    for method_name, method_func in methods.items():
        prob_a, prob_b = method_func(sharp_a, sharp_b)
        true_prob = prob_a if side_choice == "Side A" else prob_b
        method_probs.append(true_prob)
        fair = fair_odds(true_prob)
        edge = calc_edge(true_prob, your_prob)
        kelly = kelly_stake(bankroll, your_odds, true_prob, kelly_fraction)
        msg = classify_message(true_prob * 100, edge)

        color_edge = "green" if edge >= 0 else "red"
        color_prob = "green" if true_prob * 100 >= 60 else "black"

        results.append({
            "Method": method_name,
            "True Prob": f"<span style='color:{color_prob}'>{round(true_prob * 100, 2)}%</span>",
            "Fair Odds": decimal_to_american(fair),
            "Edge %": f"<span style='color:{color_edge}'>{edge}%</span>",
            "Kelly Stake": f"${kelly}",
            "Message": msg
        })

    # Average Method
    avg_prob = sum(method_probs) / len(method_probs)
    fair = fair_odds(avg_prob)
    edge = calc_edge(avg_prob, your_prob)
    kelly = kelly_stake(bankroll, your_odds, avg_prob, kelly_fraction)
    msg = classify_message(avg_prob * 100, edge)
    color_edge = "green" if edge >= 0 else "red"
    color_prob = "green" if avg_prob * 100 >= 60 else "black"

    results.append({
        "Method": "Average (EM + LOG)",
        "True Prob": f"<span style='color:{color_prob}'>{round(avg_prob * 100, 2)}%</span>",
        "Fair Odds": decimal_to_american(fair),
        "Edge %": f"<span style='color:{color_edge}'>{edge}%</span>",
        "Kelly Stake": f"${kelly}",
        "Message": msg
    })

    st.subheader("📈 Comparison Table")
    df = pd.DataFrame(results)
    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

    # ---------- Export to CSV ----------
    if st.download_button("📥 Export Bet Log to CSV", data=df.to_csv(index=False), file_name="bet_analysis.csv", mime="text/csv"):
        st.success("CSV downloaded!")
