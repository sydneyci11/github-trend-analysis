import streamlit as st
import duckdb
import os
import requests
from difflib import get_close_matches

# Load data with caching for performance
@st.cache_data

def load_data():
    # URL to your Hugging Face dataset file
    db_url = "https://huggingface.co/datasets/sydneyci11/github_trend_db/resolve/main/github_trends.duckdb"
    db_path = "/tmp/github_trends.duckdb"  # safe path on Streamlit Cloud

    # Download from Hugging Face if not already in /tmp
    if not os.path.exists(db_path):
        with open(db_path, "wb") as f:
            f.write(requests.get(db_url).content)

    # Connect to the downloaded DuckDB file
    conn = duckdb.connect(db_path)
    df = conn.execute("""
        SELECT 
            *, 
            TRY_CAST(created_at AS TIMESTAMP) AS created_at_ts,
            TRY_CAST(updated_at AS TIMESTAMP) AS updated_at_ts 
        FROM github_trends 
        ORDER BY stars DESC
    """).fetchdf()
    conn.close()
    return df

# Define advanced keyword filter function by applying difflib to get closer matches 
def advanced_keyword_filter(df, keyword, cutoff=0.6):
    # Combine searchable fields into a unique pool
    searchable_texts = (
        df["full_name"].fillna('') + " " +
        df["name"].fillna('') + " " +
        df["description"].fillna('') + " " +
        df["language"].fillna('')
    ).str.lower()

    # Get approximate matches
    matches = [i for i, text in enumerate(searchable_texts)
               if any(get_close_matches(keyword.lower(), text.split(), cutoff=cutoff))]
    
    return df.iloc[matches]

# Load the dataset
df = load_data()

# Create Streamlit app
# UI Header 
st.title("GitHub Trending Repositories Dashboard")
st.markdown("Track top repositories across AI/ML/NLP/CV domains, sorted by GitHub metadata.")

# Keyword-based filtering
with st.form("search_form"):
    st.subheader("🔍 Search and Sort")
    search_term = st.text_input("Search repositories by keyword (e.g. AI, robotics, transformer):", "")
    sort_option = st.selectbox("Sort by", ["stars", "forks", "updated_at_ts"])
    submit_button = st.form_submit_button("Search")

# Filtering and Sorting, Button/Enter push needed 
df_filtered = df.copy()
if submit_button:
    if search_term:
        df_filtered = advanced_keyword_filter(df_filtered, search_term)
df_filtered = df_filtered.sort_values(by=sort_option, ascending=False).reset_index(drop=True)

# Display Filtered Results
st.subheader("Filtered Results")
if df_filtered.empty:
    st.warning("⚠️ No repositories matched your search. Try a different keyword.")
else:
    st.dataframe(df_filtered, use_container_width=True)

# Show top languages
st.subheader("Top 10 Languages")
df_lang = df["language"].value_counts().head(10).reset_index()
df_lang.columns = ["language", "count"]
st.bar_chart(df_lang.set_index("language"))

# Line Chart: Stars over Time (Top 10 by stars)
st.subheader("Star Growth Timeline (Top 10)")
top10 = df.sort_values("stars", ascending=False).head(10)
top10_by_date = top10.sort_values("created_at_ts")
st.line_chart(top10_by_date.set_index("created_at_ts")["stars"])