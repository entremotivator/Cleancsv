import streamlit as st
import pandas as pd
import html
import re
import io
from typing import List, Optional
import time

# Page configuration
st.set_page_config(
    page_title="Advanced CSV HTML Cleaner for Blogs",
    page_icon="🧼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .cleaning-stats {
        background: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>🧼 Advanced CSV HTML Cleaner for Blog Content</h1><p>Clean HTML entities, tags, and format blog data with advanced processing options</p></div>', unsafe_allow_html=True)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    st.markdown("---")
    
    # Advanced cleaning options
    st.subheader("🔧 Advanced Options")
    preserve_formatting = st.checkbox("📝 Preserve basic formatting (bold, italic)", value=False, help="Keep <b>, <i>, <strong>, <em> tags")
    normalize_whitespace = st.checkbox("📏 Normalize whitespace", value=True, help="Remove extra spaces and line breaks")
    remove_urls = st.checkbox("🔗 Remove URLs", value=False, help="Strip out HTTP/HTTPS links")
    remove_email = st.checkbox("📧 Remove email addresses", value=False, help="Strip out email addresses")
    
    # Encoding options
    st.subheader("📄 File Options")
    encoding_option = st.selectbox("File encoding", ["utf-8", "latin-1", "cp1252"], help="Choose encoding if you have issues loading the CSV")
    delimiter_option = st.selectbox("CSV delimiter", [",", ";", "\t", "|"], help="CSV field separator")

# Caching functions for better performance
@st.cache_data(show_spinner="Loading CSV file...", ttl=300)
def load_csv_file(file_content: bytes, encoding: str = "utf-8", delimiter: str = ",") -> pd.DataFrame:
    """Load CSV file with error handling and encoding options."""
    try:
        return pd.read_csv(io.BytesIO(file_content), encoding=encoding, delimiter=delimiter)
    except UnicodeDecodeError:
        st.warning(f"Failed to decode with {encoding}, trying latin-1...")
        return pd.read_csv(io.BytesIO(file_content), encoding="latin-1", delimiter=delimiter)
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")
        return None

@st.cache_data(show_spinner=False)
def decode_html_entities(text: str) -> str:
    """Decode HTML entities in text."""
    if pd.isna(text) or text == "":
        return ""
    return html.unescape(str(text))

@st.cache_data(show_spinner=False)
def remove_html_tags(text: str, preserve_formatting: bool = False) -> str:
    """Remove HTML tags with option to preserve formatting."""
    if pd.isna(text) or text == "":
        return ""
    
    text = str(text)
    
    if preserve_formatting:
        # Replace formatting tags with markdown equivalents
        text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<b>(.*?)</b>', r'**\1**', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<em>(.*?)</em>', r'*\1*', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<i>(.*?)</i>', r'*\1*', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Remove all HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    return text

@st.cache_data(show_spinner=False)
def normalize_whitespace_func(text: str) -> str:
    """Normalize whitespace in text."""
    if pd.isna(text) or text == "":
        return ""
    
    text = str(text)
    # Replace multiple whitespace characters with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text

@st.cache_data(show_spinner=False)
def remove_urls_func(text: str) -> str:
    """Remove URLs from text."""
    if pd.isna(text) or text == "":
        return ""
    
    text = str(text)
    # Remove HTTP/HTTPS URLs
    text = re.sub(r'https?://[^\s<>"{}|\\^`\[\]]*', '', text)
    return text

@st.cache_data(show_spinner=False)
def remove_email_func(text: str) -> str:
    """Remove email addresses from text."""
    if pd.isna(text) or text == "":
        return ""
    
    text = str(text)
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
    return text

def clean_text_comprehensive(text: str, options: dict) -> str:
    """Apply all cleaning operations to text based on options."""
    if pd.isna(text) or text == "":
        return ""
    
    cleaned_text = str(text)
    
    # Apply cleaning operations in order
    if options.get('decode_html', True):
        cleaned_text = decode_html_entities(cleaned_text)
    
    if options.get('remove_tags', False):
        cleaned_text = remove_html_tags(cleaned_text, options.get('preserve_formatting', False))
    
    if options.get('remove_urls', False):
        cleaned_text = remove_urls_func(cleaned_text)
    
    if options.get('remove_email', False):
        cleaned_text = remove_email_func(cleaned_text)
    
    if options.get('normalize_whitespace', True):
        cleaned_text = normalize_whitespace_func(cleaned_text)
    
    return cleaned_text

def get_cleaning_stats(original_series: pd.Series, cleaned_series: pd.Series) -> dict:
    """Calculate statistics about the cleaning process."""
    stats = {
        'total_rows': len(original_series),
        'empty_original': original_series.isna().sum() + (original_series == "").sum(),
        'empty_cleaned': cleaned_series.isna().sum() + (cleaned_series == "").sum(),
        'avg_length_original': original_series.astype(str).str.len().mean(),
        'avg_length_cleaned': cleaned_series.astype(str).str.len().mean(),
        'html_entities_found': original_series.astype(str).str.contains('&[a-zA-Z]+;|&#\d+;').sum(),
        'html_tags_found': original_series.astype(str).str.contains('<[^>]*>').sum()
    }
    
    stats['size_reduction'] = ((stats['avg_length_original'] - stats['avg_length_cleaned']) / stats['avg_length_original'] * 100) if stats['avg_length_original'] > 0 else 0
    
    return stats

# File uploader
st.subheader("📁 Upload Your Blog Data CSV")
uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    help="Upload a CSV file containing blog content with HTML entities or tags"
)

if uploaded_file is not None:
    # Load the CSV file
    file_content = uploaded_file.read()
    df = load_csv_file(file_content, encoding_option, delimiter_option)
    
    if df is not None:
        # Display file info
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Rows", len(df))
        with col2:
            st.metric("📋 Columns", len(df.columns))
        with col3:
            st.metric("💾 File Size", f"{len(file_content) / 1024:.1f} KB")
        with col4:
            st.metric("📏 Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
        
        st.success("✅ File loaded successfully!")
        
        # Column selection
        st.subheader("🎯 Select Columns to Clean")
        
        # Show data types and preview
        with st.expander("📋 Column Information", expanded=False):
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Data Type': df.dtypes,
                'Non-Null Count': df.count(),
                'Sample Value': [str(df[col].iloc[0])[:50] + "..." if len(str(df[col].iloc[0])) > 50 else str(df[col].iloc[0]) for col in df.columns]
            })
            st.dataframe(col_info, use_container_width=True)
        
        # Multi-select for columns
        columns_to_clean = st.multiselect(
            "Select columns containing HTML content",
            df.columns.tolist(),
            help="You can select multiple columns to clean at once"
        )
        
        # Cleaning options
        st.subheader("🧹 Cleaning Options")
        col1, col2 = st.columns(2)
        
        with col1:
            decode_html = st.checkbox("🔓 Decode HTML Entities", value=True, help="Convert &lt; to <, &amp; to &, etc.")
            remove_tags = st.checkbox("🧽 Remove HTML Tags", value=False, help="Strip <p>, <div>, <span>, etc.")
        
        with col2:
            create_backup = st.checkbox("💾 Keep Original Columns", value=True, help="Preserve original columns alongside cleaned ones")
            add_suffix = st.text_input("📝 Cleaned Column Suffix", value="_cleaned", help="Suffix for new cleaned columns")
        
        # Preview section
        if columns_to_clean:
            st.subheader("👀 Preview")
            preview_rows = st.slider("Number of preview rows", 1, min(20, len(df)), 5)
            
            # Show original data
            with st.expander("📄 Original Data Sample", expanded=True):
                st.dataframe(df[columns_to_clean].head(preview_rows), use_container_width=True)
        
        # Cleaning process
        if columns_to_clean and st.button("🚀 Start Cleaning Process", type="primary"):
            cleaning_options = {
                'decode_html': decode_html,
                'remove_tags': remove_tags,
                'preserve_formatting': preserve_formatting,
                'normalize_whitespace': normalize_whitespace,
                'remove_urls': remove_urls,
                'remove_email': remove_email
            }
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Statistics container
            stats_container = st.empty()
            
            # Process each column
            all_stats = {}
            
            for i, column in enumerate(columns_to_clean):
                status_text.text(f"Cleaning column: {column}")
                
                # Apply cleaning
                original_series = df[column].copy()
                
                with st.spinner(f"Processing {column}..."):
                    cleaned_series = original_series.apply(
                        lambda x: clean_text_comprehensive(x, cleaning_options)
                    )
                
                # Add cleaned column to dataframe
                new_column_name = f"{column}{add_suffix}"
                df[new_column_name] = cleaned_series
                
                # Calculate stats
                column_stats = get_cleaning_stats(original_series, cleaned_series)
                all_stats[column] = column_stats
                
                # Update progress
                progress_bar.progress((i + 1) / len(columns_to_clean))
            
            status_text.text("✅ Cleaning completed!")
            progress_bar.progress(1.0)
            
            # Display comprehensive statistics
            st.subheader("📊 Cleaning Statistics")
            
            for column, stats in all_stats.items():
                with st.expander(f"📈 Statistics for {column}", expanded=True):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("📝 Total Rows", stats['total_rows'])
                        st.metric("📏 Avg Length (Original)", f"{stats['avg_length_original']:.1f}")
                    
                    with col2:
                        st.metric("🔍 HTML Entities Found", stats['html_entities_found'])
                        st.metric("🏷️ HTML Tags Found", stats['html_tags_found'])
                    
                    with col3:
                        st.metric("📏 Avg Length (Cleaned)", f"{stats['avg_length_cleaned']:.1f}")
                        st.metric("📉 Size Reduction", f"{stats['size_reduction']:.1f}%")
                    
                    with col4:
                        st.metric("🗑️ Empty (Original)", stats['empty_original'])
                        st.metric("🗑️ Empty (Cleaned)", stats['empty_cleaned'])
            
            # Show cleaned data preview
            st.subheader("✨ Cleaned Data Preview")
            
            # Create comparison view
            comparison_columns = []
            for column in columns_to_clean:
                comparison_columns.extend([column, f"{column}{add_suffix}"])
            
            st.dataframe(df[comparison_columns].head(10), use_container_width=True)
            
            # Export options
            st.subheader("📥 Export Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Full dataset download
                full_csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Complete Dataset",
                    data=full_csv,
                    file_name=f"cleaned_blog_data_{int(time.time())}.csv",
                    mime="text/csv",
                    help="Download the full dataset with both original and cleaned columns"
                )
            
            with col2:
                # Cleaned columns only
                if not create_backup:
                    cleaned_only_columns = [f"{col}{add_suffix}" for col in columns_to_clean]
                    # Include other columns that weren't cleaned
                    other_columns = [col for col in df.columns if col not in columns_to_clean and not col.endswith(add_suffix)]
                    cleaned_df = df[other_columns + cleaned_only_columns]
                else:
                    cleaned_df = df
                
                cleaned_csv = cleaned_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Cleaned Data Only",
                    data=cleaned_csv,
                    file_name=f"cleaned_only_blog_data_{int(time.time())}.csv",
                    mime="text/csv",
                    help="Download only the processed data"
                )
            
            # Success message
            st.success("🎉 Blog data cleaning completed successfully!")
            
            # Additional insights
            with st.expander("💡 Cleaning Insights", expanded=False):
                total_entities = sum(stats['html_entities_found'] for stats in all_stats.values())
                total_tags = sum(stats['html_tags_found'] for stats in all_stats.values())
                avg_reduction = sum(stats['size_reduction'] for stats in all_stats.values()) / len(all_stats)
                
                st.info(f"""
                **Overall Cleaning Summary:**
                - 🏷️ Total HTML entities processed: {total_entities:,}
                - 📝 Total HTML tags processed: {total_tags:,}
                - 📉 Average content size reduction: {avg_reduction:.1f}%
                - 📊 Columns processed: {len(columns_to_clean)}
                """)

# Footer with usage instructions
with st.expander("📖 Usage Instructions", expanded=False):
    st.markdown("""
    ### How to use this HTML cleaner:
    
    1. **Upload your CSV file** containing blog content with HTML entities or tags
    2. **Select columns** that contain HTML content you want to clean
    3. **Choose cleaning options** based on your needs:
       - **Decode HTML Entities**: Converts encoded characters like `&lt;` to `<`
       - **Remove HTML Tags**: Strips out HTML tags like `<p>`, `<div>`, etc.
       - **Preserve Formatting**: Keeps basic formatting (bold, italic) as markdown
       - **Normalize Whitespace**: Removes extra spaces and line breaks
       - **Remove URLs/Emails**: Strips out links and email addresses
    4. **Preview the results** before downloading
    5. **Download** your cleaned data
    
    ### Common use cases:
    - Cleaning blog post content exported from CMS
    - Processing scraped web content
    - Preparing text data for analysis
    - Converting HTML content to plain text
    """)

# Help section
if st.sidebar.button("❓ Need Help?"):
    st.sidebar.info("""
    **Common Issues:**
    - Try different encoding options if CSV won't load
    - Use different delimiters for non-standard CSV files
    - Large files may take longer to process
    
    **Tips:**
    - Preview your data before cleaning
    - Keep original columns as backup
    - Use preserve formatting for readable output
    """)
