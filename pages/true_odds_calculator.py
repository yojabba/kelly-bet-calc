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

# ---------- Streamlit UI ----------
st.title("📊 True Odds + Value Calculator (EM & LOG)")

st.write("""
Input odds for both sides of the sharp market, plus your odds. We'll calculate the true probability,
fair odds, edge %, and suggested Kelly stake using Equal Margin and LOG methods.
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

    for method_name, method_func in methods.items():
        prob_a, prob_b = method_func(sharp_a, sharp_b)
        true_prob = prob_a if side_choice == "Side A" else prob_b
        fair = fair_odds(true_prob)
        edge = calc_edge(true_prob, your_prob)
        kelly = kelly_stake(bankroll, your_odds, true_prob, kelly_fraction)

        color = "green" if edge > 0 else "red"
        edge_display = f"<span style='color:{color}'>{edge}%</span>"

        results.append({
            "Method": method_name,
            "True Prob": round(true_prob * 100, 2),
            "Fair Odds": fair,
            "Edge %": edge_display,
            "Kelly Stake": f"${kelly}"
        })

    st.subheader("📈 Comparison Table")
    df = pd.DataFrame(results)
    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

    # ---------- Editable Bet Log ----------
    if "bet_log" not in st.session_state:
        st.session_state.bet_log = []

    with st.form("log_form"):
        st.subheader("📝 Log This Bet")
        log_this = st.checkbox("Add to Bet Log")
        result_status = st.selectbox("Result (if known)", ["Pending", "Win", "Loss"])
        submitted = st.form_submit_button("Submit Bet")

        if submitted and log_this:
            st.session_state.bet_log.append({
                "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Side": side_choice,
                "Your Odds": your_odds_input,
                "Edge (EM) %": calc_edge(remove_margin_equal(sharp_a, sharp_b)[0 if side_choice == "Side A" else 1], your_prob),
                "Stake (EM)": f"${kelly_stake(bankroll, your_odds, remove_margin_equal(sharp_a, sharp_b)[0 if side_choice == "Side A" else 1], kelly_fraction)}",
                "Result": result_status
            })

    # ---------- Display and Edit Bet Log ----------
    st.subheader("📋 Bet Log")
    log_df = pd.DataFrame(st.session_state.bet_log)

    if not log_df.empty:
        for i in range(len(log_df)):
            cols = st.columns([1.5, 1, 1, 1, 1, 1])
            cols[0].write(log_df.iloc[i]["Date"])
            cols[1].write(log_df.iloc[i]["Side"])
            cols[2].write(log_df.iloc[i]["Your Odds"])
            cols[3].write(log_df.iloc[i]["Edge (EM) %"])
            cols[4].write(log_df.iloc[i]["Stake (EM)"])
            result = cols[5].selectbox("Result", ["Pending", "Win", "Loss"], key=f"result_{i}", index=["Pending", "Win", "Loss"].index(log_df.iloc[i]["Result"]))
            st.session_state.bet_log[i]["Result"] = result
            st.markdown("---")

        delete_index = st.number_input("Enter row # to delete (0-based index)", min_value=0, max_value=len(log_df)-1, step=1)
        if st.button("Delete Entry"):
            st.session_state.bet_log.pop(delete_index)
            st.success("Entry deleted. Reload the page to update.")
    else:
        st.info("No bets logged yet.")
