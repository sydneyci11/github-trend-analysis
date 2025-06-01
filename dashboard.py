import streamlit as st
import duckdb

# Load data with caching for performance
@st.cache_data

def load_data():
    conn = duckdb.connect("/Users/sydneyci11/Documents/github-trend-analysis/github_trends.duckdb")
    df = conn.execute("""
        SELECT 
            *, 
            TRY_CAST(created_at AS TIMESTAMP) AS created_at_ts 
        FROM github_trends 
        ORDER BY stars DESC
    """).fetchdf()
    conn.close()
    return df

# Load the dataset
df = load_data()

# Create Streamlit app
st.title("GitHub Trending Repositories Dashboard")
st.dataframe(df)

# Keyword-based filtering
search_term = st.text_input("Input the keyword you want to look for (e.g.AI, robotics, transformer)")
if search_term:
    df_filtered = df[df["full_name"].str.contains(search_term, case=False, na=False)]
else:
    df_filtered = df

st.dataframe(df_filtered)

# Show top languages
df_lang = df["language"].value_counts().head(10)
st.bar_chart(df_lang)

# Line Chart: Stars over Time (Top 10 by stars)
st.subheader("Star Growth Timeline (Top 10)")
top10 = df.sort_values("stars", ascending=False).head(10)
top10_by_date = top10.sort_values("created_at_ts")
st.line_chart(top10_by_date.set_index("created_at_ts")["stars"])