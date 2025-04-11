import streamlit as st
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
import pandas as pd
import random

st.set_page_config(page_title="NBA Dream Matchup", layout="wide") st.markdown("🕹️ Loading NBA Dream Matchup Simulator...")
st.title("🏀 NBA Dream Matchup Simulator")

st.markdown("""
<style>
@keyframes fadeIn {
    0% { opacity: 0; transform: translateY(10px); }
    100% { opacity: 1; transform: translateY(0); }
}
.fade {
    animation: fadeIn 1s ease-in-out;
}
.big-font {
    font-size:25px !important;
    font-weight: bold;
    color: #1f77b4;
}
.result-box {
    background-color: #f0f2f6;
    border-left: 5px solid #1f77b4;
    padding: 10px;
    margin-top: 10px;
    border-radius: 10px;
    animation: fadeIn 1s ease-in-out;
}
</style>
""", unsafe_allow_html=True)

# Dummy player images (replace with more or dynamic fetching if needed)
player_images = {
    "LeBron James": "https://cdn.nba.com/headshots/nba/latest/1040x760/2544.png",
    "Stephen Curry": "https://cdn.nba.com/headshots/nba/latest/1040x760/201939.png"
}

# Get NBA players
nba_players = players.get_players()
player_names = sorted([p['full_name'] for p in nba_players])

# Select Teams
st.header("Select Players by Position")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Team A")
    team_a = [st.selectbox(f"{pos} (Team A)", player_names, key=f"A{i}") 
              for i, pos in enumerate(["PG", "SG", "SF", "PF", "C"])]

with col2:
    st.subheader("Team B")
    team_b = [st.selectbox(f"{pos} (Team B)", player_names, key=f"B{i}") 
              for i, pos in enumerate(["PG", "SG", "SF", "PF", "C"])]

# Get career average stats
def get_player_career_stats(name):
    try:
        player_id = next(p['id'] for p in nba_players if p['full_name'] == name)
        stats = playercareerstats.PlayerCareerStats(player_id=player_id).get_data_frames()[0]
        career_avg = stats.mean(numeric_only=True)
        return career_avg
    except:
        return pd.Series(dtype='float64')

# Smart scoring with all available metrics
def calculate_score(stats):
    if stats.empty:
        return 0, 1

    PTS     = stats.get('PTS', 0)
    REB     = stats.get('REB', 0)
    AST     = stats.get('AST', 0)
    STL     = stats.get('STL', 0)
    BLK     = stats.get('BLK', 0)
    FG_PCT  = stats.get('FG_PCT', 0)
    FT_PCT  = stats.get('FT_PCT', 0)
    FG3_PCT = stats.get('FG3_PCT', 0)
    TOV     = stats.get('TOV', 0)

    score = (
        (PTS * 1.0) +
        (REB * 0.8) +
        (AST * 0.8) +
        (STL * 1.5) +
        (BLK * 1.5) +
        (FG_PCT * 100 * 1.2) +
        (FT_PCT * 100 * 0.8) +
        (FG3_PCT * 100 * 0.6) -
        (TOV * 1.5)
    )
    clutch_multiplier = random.uniform(0.85, 1.15)
    score *= clutch_multiplier

    return round(score, 2), clutch_multiplier

# Simulate match
if st.button("Simulate Matchup"):
    team_a_score = 0
    team_b_score = 0

    st.markdown("<div class='big-font fade'>Team A Player Stats & Scores</div>", unsafe_allow_html=True)
    for player in team_a:
        stats = get_player_career_stats(player)
        score, clutch = calculate_score(stats)
        team_a_score += score
        with st.expander(f"{player} - Score: {score} | Clutch: {round(clutch,2)}"):
            if player in player_images:
                st.image(player_images[player], caption=player, use_column_width=False, output_format="PNG", width=100)
            st.dataframe(stats.to_frame().rename(columns={0: "Career Avg"}))

    st.markdown("<div class='big-font fade'>Team B Player Stats & Scores</div>", unsafe_allow_html=True)
    for player in team_b:
        stats = get_player_career_stats(player)
        score, clutch = calculate_score(stats)
        team_b_score += score
        with st.expander(f"{player} - Score: {score} | Clutch: {round(clutch,2)}"):
            if player in player_images:
                st.image(player_images[player], caption=player, use_column_width=False, output_format="PNG", width=100)
            st.dataframe(stats.to_frame().rename(columns={0: "Career Avg"}))

    st.markdown("---")
    st.subheader("🏆 Final Results")
    st.markdown(
        f"""
        <div class='result-box'>
            <strong>Team A Total Score:</strong> {round(team_a_score, 2)}<br>
            <strong>Team B Total Score:</strong> {round(team_b_score, 2)}
        </div>
        """, unsafe_allow_html=True
    )

    if team_a_score > team_b_score:
        st.success("🎉 Team A Wins!")
    elif team_b_score > team_a_score:
        st.success("🎉 Team B Wins!")
    else:
        st.info("🤝 It's a Tie!")
