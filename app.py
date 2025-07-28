import streamlit as st
import pandas as pd
from streamlit_aggrid import AgGrid, GridOptionsBuilder
import io

st.set_page_config(page_title="Large CSV Viewer", layout="wide")

st.title("📊 Large CSV File Viewer")

# --- Upload CSV File ---
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file:
    try:
        # Read file in chunks for large CSVs
        CHUNK_SIZE = 50000
        st.info("Loading in chunks...")

        chunks = pd.read_csv(uploaded_file, chunksize=CHUNK_SIZE)
        df = pd.concat(chunks)

        st.success(f"Loaded {len(df):,} rows × {len(df.columns)} columns.")

        # --- Search and Filter ---
        with st.expander("🔍 Search / Filter Options"):
            column = st.selectbox("Select column to filter", df.columns)
            search_value = st.text_input("Enter value to search")
            if search_value:
                df = df[df[column].astype(str).str.contains(search_value, case=False, na=False)]
                st.write(f"Filtered down to {len(df):,} rows")

        # --- AgGrid for display ---
        st.subheader("📋 Data Preview")
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=20)
        gb.configure_side_bar()
        gb.configure_default_column(filterable=True, sortable=True, resizable=True)
        grid_options = gb.build()

        AgGrid(df, gridOptions=grid_options, height=600, fit_columns_on_grid_load=True)

        # --- Download filtered results ---
        st.download_button(
            label="📥 Download Filtered CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="filtered_data.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"Error loading file: {e}")
else:
    st.warning("Please upload a CSV file to begin.")
