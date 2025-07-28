import streamlit as st
import pandas as pd
import html
import re
import io

st.set_page_config(page_title="CSV HTML Cleaner", layout="wide")

st.title("🧼 Clean HTML Entities in CSV")
st.markdown("Upload a CSV file with HTML-encoded content (like `&lt;`, `&#039;`, etc.), and clean it for export.")

# File uploader
uploaded_file = st.file_uploader("📁 Upload CSV", type=["csv"])

@st.cache_data(show_spinner=True)
def load_csv(file):
    return pd.read_csv(file)

@st.cache_data(show_spinner=False)
def decode_html(text):
    if pd.isna(text):
        return ""
    return html.unescape(text)

def remove_html_tags(text):
    return re.sub(r'<[^>]*>', '', text)

if uploaded_file:
    df = load_csv(uploaded_file)
    st.success(f"✅ Loaded {len(df)} rows")

    st.subheader("Select the column to clean")
    column_to_clean = st.selectbox("Column with HTML entities", df.columns)

    st.markdown("**Options:**")
    decode = st.checkbox("🔓 Decode HTML Entities (e.g. &lt; to <)", value=True)
    strip_tags = st.checkbox("🧽 Remove HTML Tags (e.g. <p>, <div>)", value=False)

    if st.button("🧹 Clean Column"):
        with st.spinner("Cleaning data..."):
            cleaned_col = df[column_to_clean].astype(str)

            if decode:
                cleaned_col = cleaned_col.apply(decode_html)
            if strip_tags:
                cleaned_col = cleaned_col.apply(remove_html_tags)

            df[column_to_clean + "_cleaned"] = cleaned_col
            st.success("🎉 Cleaning complete!")

            st.subheader("Preview of Cleaned Data")
            st.dataframe(df[[column_to_clean, column_to_clean + "_cleaned"]].head(10))

            # Download cleaned CSV
            cleaned_csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Cleaned CSV",
                data=cleaned_csv,
                file_name="cleaned_blog_data.csv",
                mime="text/csv",
            )
