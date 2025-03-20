import streamlit as st
import pandas as pd
import sqlite3

# Connect to database
conn = sqlite3.connect("/Users/sydneyci11/Documents/github-trend-analysis/github_trends.db")

# Fetch data
df = pd.read_sql("SELECT * FROM github_trends ORDER BY stars DESC;", conn)
conn.close()

# Create Streamlit app
st.title("GitHub Trending Repositories Dashboard")
st.dataframe(df)

# Show top languages
df_lang = df["language"].value_counts().head(10)
st.bar_chart(df_lang)