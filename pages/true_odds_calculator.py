import streamlit as st
import pandas as pd
import datetime

# ---------- Helper Functions ----------
def implied_prob(decimal_odds):
    return 1 / decimal_odds

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
st.title("📊 True Odds + Value Calculator")

st.write("""
Compare odds from a sharp book (like Pinnacle) with the odds you can bet on (FanDuel, DraftKings, etc.)
to determine if a bet has positive expected value (+EV), suggested unit size, and track your edges.
""")

sharp_odds = st.number_input("Sharp Book Odds (e.g. Pinnacle)", min_value=1.01, value=1.91, step=0.01)
your_odds = st.number_input("Your Book Odds (e.g. FanDuel, DraftKings)", min_value=1.01, value=2.10, step=0.01)
bankroll = st.number_input("Current Bankroll", min_value=1.0, value=1000.0, step=10.0)
kelly_fraction = st.slider("Fraction of Kelly to Use", min_value=0.1, max_value=1.0, value=0.5, step=0.1)

# ---------- Edge Calculation ----------
if st.button("Calculate"):
    sharp_prob = implied_prob(sharp_odds)
    your_prob = implied_prob(your_odds)
    edge = calc_edge(sharp_prob, your_prob)
    fair_line = fair_odds(sharp_prob)
    kelly_bet = kelly_stake(bankroll, your_odds, sharp_prob, kelly_fraction)

    st.subheader("📈 Results")
    st.write(f"**True Implied Probability (Sharp Book)**: {round(sharp_prob * 100, 2)}%")
    st.write(f"**Your Implied Probability**: {round(your_prob * 100, 2)}%")
    st.write(f"**Fair Odds**: {fair_line}")
    st.write(f"**Edge (Value)**: {edge}%")
    st.write(f"**Recommended Bet (Kelly)**: ${kelly_bet}")

    if edge > 0:
        st.success("✅ This is a +EV (positive expected value) bet!")
    else:
        st.error("❌ This is a -EV bet. Not worth it based on sharp probability.")

    # ---------- Save Edge to Session ----------
    if "edge_history" not in st.session_state:
        st.session_state.edge_history = []
    st.session_state.edge_history.append({
        "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Sharp Odds": sharp_odds,
        "Your Odds": your_odds,
        "Edge %": edge,
        "Suggested Bet": kelly_bet
    })

# ---------- Graph of Edges ----------
if "edge_history" in st.session_state and len(st.session_state.edge_history) > 0:
    df = pd.DataFrame(st.session_state.edge_history)
    st.subheader("📊 Edge History")
    st.line_chart(df.set_index("Date")["Edge %"])

    st.subheader("📋 Bet Log")
    st.dataframe(df[::-1], use_container_width=True)
