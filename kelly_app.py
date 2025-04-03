
import streamlit as st

def kelly_criterion(odds_decimal, win_probability, fraction=1.0, bankroll=1000):
    b = odds_decimal - 1
    p = win_probability
    q = 1 - p
    kelly_fraction = (b * p - q) / b

    if kelly_fraction <= 0:
        return 0.0, 0.0

    bet_fraction = kelly_fraction * fraction
    recommended_bet = bankroll * bet_fraction

    return round(bet_fraction * 100, 2), round(recommended_bet, 2)

st.title("📈 Kelly Criterion Betting Calculator")

odds = st.number_input("Decimal Odds", min_value=1.01, step=0.01, value=2.25)
prob = st.number_input("Your Win Probability (0 - 1)", min_value=0.0, max_value=1.0, step=0.01, value=0.51)
fraction = st.number_input("Fraction of Kelly to Use", min_value=0.0, max_value=1.0, step=0.1, value=0.5)
bankroll = st.number_input("Current Bankroll", min_value=1.0, step=1.0, value=1000.0)

if st.button("Calculate"):
    percent, bet = kelly_criterion(odds, prob, fraction, bankroll)
    if bet > 0:
        st.success(f"✅ Bet ${bet} ({percent}% of your bankroll)")
    else:
        st.warning("❌ No bet recommended (negative or zero EV)")
