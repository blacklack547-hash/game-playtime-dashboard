import os
import zipfile

# Unzip database automatically on Streamlit Cloud startup
if not os.path.exists('backlog.db') and os.path.exists('backlog.zip'):
    with zipfile.ZipFile('backlog.zip', 'r') as zip_ref:
        zip_ref.extractall('.')
import streamlit as st
import sqlite3
import pandas as pd

# Set up dashboard visual workspace with a clean layout
st.set_page_config(page_title="Game Playtime Analytics Dashboard", page_icon="🎮", layout="wide")

# Pull data directly from local relational database tables
@st.cache_data
def load_optimized_data():
    try:
        conn = sqlite3.connect('backlog.db')
        # 💡 FIX: Only pull games that actually have recorded playtime data
        data = pd.read_sql_query("SELECT * FROM playtimes WHERE main_story > 0", conn)
        conn.close()
        return data
    except Exception:
        return pd.DataFrame()

df = load_optimized_data()

if not df.empty:
    st.title("🎮 Video Game Playtime Curation & Analytics Platform")
    st.markdown("Query playtime playstyles, check release records, and browse game information seamlessly.")
    st.markdown("---")

    # High Level Summary Cards (Now filtering out 0-hour placeholder values!)
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.markdown("### 📊 Total Cataloged Titles")
        st.markdown(f"## **{len(df):,}**")
    with kpi2:
        st.markdown("### ⏱️ Average Main Story")
        # 💡 FIX: Only calculate mean for rows where main_story is greater than 0
        true_main_story = df[df['main_story'] > 0]['main_story'].mean()
        st.markdown(f"## **{true_main_story:.1f} Hours**")
    with kpi3:
        st.markdown("### 🏆 Average 100% Run")
        # 💡 FIX: Only calculate mean for rows where completionist is greater than 0
        true_completionist = df[df['completionist'] > 0]['completionist'].mean()
        st.markdown(f"## **{true_completionist:.1f} Hours**")

    st.markdown("---")

    # Analytics Leaderboard Deck (Pure text insights)
    st.subheader("📈 Playtime Records & Data Insights")
    st.markdown("Key structural milestones extracted directly from your database table:")

    c_longest, c_shortest = st.columns(2)
    with c_longest:
        st.markdown("#### 🏆 Top 5 Longest Games (100% Completion)")
        longest_games = df[df['completionist'] > 0].sort_values(by='completionist', ascending=False).head(5)
        for idx, row in longest_games.iterrows():
            st.markdown(f"• **{str(row['name']).title()}** ({str(row['type']).upper()}) — **{row['completionist']} hrs**")

    with c_shortest:
        st.markdown("#### ⚡ Top 5 Quickest Games (Main Story)")
        shortest_games = df[df['main_story'] > 0].sort_values(by='main_story', ascending=True).head(5)
        for idx, row in shortest_games.iterrows():
            st.markdown(f"• **{str(row['name']).title()}** ({str(row['type']).upper()}) — **{row['main_story']} hrs**")

    st.markdown("---")

    # Browse Catalog Layout (Reliable pure text deck)
    st.subheader("🗂️ Browse Your Cataloged Game Profiles")
    st.markdown("Snapshot overview of games extracted directly from your optimized local database storage:")

    preview_df = df.head(40)
    for idx, row in preview_df.iterrows():
        st.markdown(f"### 🕹️ {str(row['name']).title()}")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"• **Main Story:** {row['main_story']} hrs")
            st.markdown(f"• **Main + Sides:** {row['main_plus_sides']} hrs")
        with c2:
            st.markdown(f"• **100% Run:** {row['completionist']} hrs")
            st.markdown(f"• **Average Style:** {row['all_styles']} hrs")
        with c3:
            st.markdown(f"• **Release Date:** {str(row['release_date']).title()}")
            st.markdown(f"• **Category:** {str(row['type']).upper()}")
        st.markdown(" ")

    st.markdown("---")

    # Dataset Spreadsheet View -> Completely static HTML table element
    st.subheader("📋 Curated Dataset Snapshot Table")
    st.table(df[['name', 'type', 'platform', 'main_story', 'completionist', 'release_date']].head(25))

else:
    st.error("⚠️ The SQLite database is empty. Please execute your 'etl_pipeline.py' script cell before launching the app.")
