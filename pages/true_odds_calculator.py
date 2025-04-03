import streamlit as st

st.title("🎯 True Odds Calculator")

st.write("""
Enter the bookmaker's odds for each outcome below. This calculator will remove the bookmaker's margin
(using the Equal Margin method) and show the true probabilities and fair odds.
""")

# Step 1: Ask how many outcomes there are (2 for most head-to-head bets)
num_outcomes = st.number_input("Number of Outcomes", min_value=2, value=2, step=1)

# Step 2: Get the odds for each outcome
odds = []
for i in range(num_outcomes):
    odds.append(st.number_input(f"Odds for Outcome {i+1}", min_value=1.01, value=2.00, step=0.01))

# Step 3: When user clicks "Calculate"
if st.button("Calculate True Odds"):
    # Calculate the bookmaker margin
    total_implied_prob = sum([1/o for o in odds])
    margin = total_implied_prob - 1

    # Adjusted probabilities using Equal Margin Method
    true_probs = [(1/o) / total_implied_prob for o in odds]
    true_odds = [round(1/p, 2) for p in true_probs]

    st.subheader("📊 Results")
    for i in range(num_outcomes):
        st.write(f"Outcome {i+1} → True Probability: {round(true_probs[i]*100, 2)}% | Fair Odds: {true_odds[i]}")

    st.caption(f"Bookmaker Margin: {round(margin*100, 2)}% included in original odds")
