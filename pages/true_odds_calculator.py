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

def remove_margin_mpto(odds_a, odds_b):
    imp_a, imp_b = implied_prob(odds_a), implied_prob(odds_b)
    total = imp_a + imp_b
    weight_a = odds_a / (odds_a + odds_b)
    weight_b = 1 - weight_a
    margin = total - 1
    return (imp_a - margin * weight_a), (imp_b - margin * weight_b)

def remove_margin_shin(odds_a, odds_b):
    imp_a, imp_b = implied_prob(odds_a), implied_prob(odds_b)
    z = imp_a + imp_b
    k = 2 - z
    true_prob_a = (imp_a - ((imp_a ** 2) - ((k - 1) * imp_a)) ** 0.5) / (1 - k)
    true_prob_b = 1 - true_prob_a
    return true_prob_a, true_prob_b

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
st.title("📊 True Odds + Value Calculator (All Methods)")

st.write("""
Input odds for both sides of the sharp market, plus your odds. We'll calculate the true probability,
fair odds, edge %, and suggested Kelly stake across 4 methods: Equal Margin, LOG, MPTO, and Shin.
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

# Convert to decimal
sharp_a = american_to_decimal(sharp_odds_a_input)
sharp_b = american_to_decimal(sharp_odds_b_input)
your_odds = american_to_decimal(your_odds_input)
your_prob = implied_prob(your_odds)

# Apply all methods
results = []
methods = {
    "Equal Margin": remove_margin_equal,
    "LOG Method": remove_margin_log,
    "MPTO Method": remove_margin_mpto,
    "Shin Method": remove_margin_shin
}

for method_name, method_func in methods.items():
    prob_a, prob_b = method_func(sharp_a, sharp_b)
    true_prob = prob_a if side_choice == "Side A" else prob_b
    fair = fair_odds(true_prob)
    edge = calc_edge(true_prob, your_prob)
    kelly = kelly_stake(bankroll, your_odds, true_prob, kelly_fraction)
    results.append({
        "Method": method_name,
        "True Prob": round(true_prob * 100, 2),
        "Fair Odds": fair,
        "Edge %": edge,
        "Kelly Stake": f"${kelly}"
    })

# Display table
st.subheader("📈 Comparison Table")
df = pd.DataFrame(results)
st.dataframe(df, use_container_width=True)

# Save to session log
if "edge_history" not in st.session_state:
    st.session_state.edge_history = []
st.session_state.edge_history.append({
    "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    "Side": side_choice,
    "Your Odds": your_odds_input,
    "Edge (EM)": df.iloc[0]["Edge %"],
    "Stake (EM)": df.iloc[0]["Kelly Stake"]
})

# History and Chart
hist_df = pd.DataFrame(st.session_state.edge_history)

st.subheader("📊 Edge Over Time (EM Only)")
st.line_chart(hist_df.set_index("Date")["Edge (EM)"])

st.subheader("📋 Bet Log")
st.dataframe(hist_df[::-1], use_container_width=True)
