import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="CSV Viewer", layout="wide")

st.title("📊 Large CSV Viewer & Filter (No AgGrid)")

# Upload CSV
uploaded_file = st.file_uploader("Upload a large CSV file", type=["csv"])
if uploaded_file:
    try:
        # Load CSV into DataFrame
        file_buffer = StringIO(uploaded_file.getvalue().decode("utf-8"))
        df = pd.read_csv(file_buffer)

        st.success(f"Loaded {len(df):,} rows and {len(df.columns)} columns.")

        # Display column info
        with st.expander("ℹ️ View column info"):
            st.write(df.dtypes)

        # Optional filter
        st.subheader("🔍 Filter Options")

        with st.expander("🧰 Add filters"):
            filter_col = st.selectbox("Choose column to filter", df.columns)
            unique_vals = df[filter_col].dropna().unique().tolist()
            if df[filter_col].dtype == 'object' or df[filter_col].dtype.name == 'category':
                selected_value = st.selectbox("Select value to filter", unique_vals)
                filtered_df = df[df[filter_col] == selected_value]
            elif pd.api.types.is_numeric_dtype(df[filter_col]):
                min_val, max_val = float(df[filter_col].min()), float(df[filter_col].max())
                range_val = st.slider("Select numeric range", min_val, max_val, (min_val, max_val))
                filtered_df = df[df[filter_col].between(*range_val)]
            else:
                st.warning("Filtering not supported for this column type.")
                filtered_df = df
        st.markdown("### 🧾 Filtered Data Preview")
        st.dataframe(filtered_df.head(1000), use_container_width=True)

        # Download filtered data
        csv = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Filtered CSV", csv, "filtered_data.csv", "text/csv")

    except Exception as e:
        st.error(f"Failed to load file: {e}")
else:
    st.info("Please upload a CSV file to begin.")
