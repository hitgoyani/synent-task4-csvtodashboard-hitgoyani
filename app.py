import streamlit as st
import pandas as pd
import plotly.express as px
import io
import os

# Configure the Streamlit page
st.set_page_config(page_title='Dynamic CSV Dashboard', page_icon='📊', layout='wide')

# Inject Premium CSS
def inject_css():
    css = """
    <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Outfit:wght@500;600;700&display=swap');
        
        /* Apply fonts */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
        }
        
        /* Metric Cards Styling */
        div[data-testid="metric-container"] {
            background-color: #1E1E1E;
            border: 1px solid #333333;
            padding: 1rem;
            border-radius: 0.5rem;
            transition: all 0.3s ease;
        }
        div[data-testid="metric-container"]:hover {
            border-color: #4CAF50;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        
        div[data-testid="stMetricValue"] {
            color: #4CAF50 !important;
        }
        
        /* Hide default Streamlit multi-page sidebar navigation */
        div[data-testid="stSidebarNav"] {display: none !important;}
        
        /* Hide Streamlit top decoration line */
        div[data-testid="stDecoration"] {display: none !important;}
        
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

inject_css()

# Sidebar - App Configuration & Data Loading
with st.sidebar:
    st.markdown("### ⚙️ Dashboard Controls")
    st.markdown("---")
    
    st.markdown("**1. Select Data Source**")
    data_source = st.radio("Load Data via:", ["Upload CSV", "Use Sample Data"], label_visibility="collapsed")
    
    df = None
    file_name = "None"
    
    if data_source == "Upload CSV":
        uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])
        if uploaded_file is not window:
            try:
                df = pd.read_csv(uploaded_file)
                file_name = uploaded_file.name
            except Exception as e:
                st.error(f"Error loading CSV: {e}")
    else:
        sample_dataset = st.selectbox("Select Sample Dataset:", ["Titanic", "Iris"])
        try:
            # Construct path to sample data
            current_dir = os.path.dirname(os.path.abspath(__file__))
            sample_path = os.path.join(current_dir, "sample_data", f"{sample_dataset.lower()}.csv")
            df = pd.read_csv(sample_path)
            file_name = f"{sample_dataset.lower()}.csv (Sample)"
            st.success(f"Loaded {sample_dataset} Dataset")
        except Exception as e:
            st.error(f"Sample data not found. Ensure 'sample_data/{sample_dataset.lower()}.csv' exists. {e}")

# Main Layout
st.title("📊 Dynamic CSV Data Dashboard")
st.markdown("Automated Exploratory Data Analysis & Visualization Engine.")
st.markdown("---")

if df is not None:
    # ---------------------------------------------------------
    # Section 1: Dataset Overview
    # ---------------------------------------------------------
    st.markdown("### 🗃️ Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", f"{df.shape[0]:,}")
    col2.metric("Columns", f"{df.shape[1]:,}")
    col3.metric("Missing Values", f"{df.isna().sum().sum():,}")
    col4.metric("Active File", file_name)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Data Preview", "Column Analysis", "Descriptive Statistics"])
    
    with tab1:
        st.dataframe(df.head(100), use_container_width=True)
        
    with tab2:
        # Generate column info
        buffer = io.StringIO()
        df.info(buf=buffer)
        s = buffer.getvalue()
        
        info_col1, info_col2 = st.columns([1, 2])
        with info_col1:
            st.markdown("**Data Types:**")
            st.dataframe(pd.DataFrame(df.dtypes, columns=['Data Type']).astype(str), use_container_width=True)
        with info_col2:
            st.markdown("**Missing Values per Column:**")
            st.dataframe(pd.DataFrame(df.isna().sum(), columns=['Missing Count']), use_container_width=True)
            
    with tab3:
        st.dataframe(df.describe(include='all').T, use_container_width=True)

    st.markdown("---")
    
    # ---------------------------------------------------------
    # Section 2: Dynamic Visualizations
    # ---------------------------------------------------------
    st.markdown("### 📈 Visual Exploration Studio")
    
    # Separate columns by data type for smarter selections
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    all_cols = df.columns.tolist()
    
    if len(numeric_cols) == 0:
        st.warning("No numeric columns found in the dataset for charting.")
    else:
        viz_type = st.selectbox("Select Visualization Type:", ["Scatter Plot", "Histogram", "Bar Chart", "Box Plot", "Correlation Heatmap"])
        
        chart_col1, chart_col2 = st.columns([1, 3])
        
        with chart_col1:
            st.markdown("#### Axis Configuration")
            if viz_type in ["Scatter Plot", "Bar Chart", "Box Plot"]:
                x_axis = st.selectbox("X-Axis Feature", all_cols, index=0)
                y_axis = st.selectbox("Y-Axis Feature (Numeric)", numeric_cols, index=len(numeric_cols)-1 if len(numeric_cols) > 1 else 0)
                color_col = st.selectbox("Color By (Optional)", ["None"] + all_cols, index=0)
            
            elif viz_type == "Histogram":
                x_axis = st.selectbox("Distribution Feature (Numeric)", numeric_cols, index=0)
                color_col = st.selectbox("Color By (Optional)", ["None"] + categorical_cols, index=0)
                bins = st.slider("Number of Bins", 5, 100, 30)
                
            elif viz_type == "Correlation Heatmap":
                st.info("Correlation heatmaps automatically use all numeric columns.")
                
        with chart_col2:
            st.markdown("#### Generated Visualization")
            color_param = color_col if viz_type != "Correlation Heatmap" and color_col != "None" else None
            
            try:
                if viz_type == "Scatter Plot":
                    fig = px.scatter(df, x=x_axis, y=y_axis, color=color_param, template="plotly_dark", opacity=0.7)
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif viz_type == "Histogram":
                    fig = px.histogram(df, x=x_axis, color=color_param, nbins=bins, template="plotly_dark", marginal="box")
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif viz_type == "Bar Chart":
                    # For bar charts, group and aggregate if X is categorical
                    if x_axis in categorical_cols:
                        agg_df = df.groupby(x_axis, as_index=False)[y_axis].mean()
                        fig = px.bar(agg_df, x=x_axis, y=y_axis, template="plotly_dark", title=f"Average {y_axis} by {x_axis}")
                    else:
                        fig = px.bar(df, x=x_axis, y=y_axis, color=color_param, template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif viz_type == "Box Plot":
                    fig = px.box(df, x=x_axis, y=y_axis, color=color_param, template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                    
                elif viz_type == "Correlation Heatmap":
                    if len(numeric_cols) > 1:
                        corr = df[numeric_cols].corr()
                        fig = px.imshow(corr, text_auto=True, aspect="auto", template="plotly_dark", color_continuous_scale="Viridis")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Need at least 2 numeric columns for a correlation heatmap.")
            except Exception as e:
                st.error(f"Error generating chart: {e}")

else:
    # Empty state
    st.info("👈 Please upload a CSV file or select a sample dataset from the sidebar to begin analysis.")
    
st.markdown('<br><hr>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #888888; font-size: 0.8em;">Built by Hit Goyani | Synent Technologies Data Science Internship | Candidate ID: SYN/M2/IP1050</div>', unsafe_allow_html=True)
