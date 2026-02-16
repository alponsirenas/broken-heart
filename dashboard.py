"""Interactive dashboard for visualizing Whoop and lab data correlations."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os
import json
import config
from whoop_auth import WhoopAuth
from whoop_client import WhoopClient
from lab_parser import LabDataParser
from data_processor import HealthDataProcessor
from streamlit_oauth import handle_oauth_flow, show_login_button, show_logout_button


# Page configuration
st.set_page_config(
    page_title="Whoop Health Data Analysis",
    page_icon="❤️",
    layout="wide"
)

# Handle OAuth flow first
is_authenticated = handle_oauth_flow()

st.title("❤️ Whoop Health Data Comparison Dashboard")
st.markdown("### Comparing Whoop metrics with lab test results during cardiac events")


@st.cache_data
def load_data():
    """Load processed data from files."""
    data_dir = config.DATA_OUTPUT_DIR
    
    daily_metrics = None
    lab_data = None
    
    # Try to load existing processed data
    daily_path = os.path.join(data_dir, 'daily_metrics.csv')
    lab_path = os.path.join(data_dir, 'lab_data.csv')
    
    if os.path.exists(daily_path):
        daily_metrics = pd.read_csv(daily_path)
        daily_metrics['date'] = pd.to_datetime(daily_metrics['date'])
    
    if os.path.exists(lab_path):
        lab_data = pd.read_csv(lab_path)
        lab_data['date'] = pd.to_datetime(lab_data['date'])
    
    return daily_metrics, lab_data


def create_timeline_chart(daily_metrics: pd.DataFrame, metric_name: str, 
                          metric_column: str, color: str = 'blue'):
    """Create a timeline chart for a specific metric with event markers."""
    fig = go.Figure()
    
    # Add metric line
    fig.add_trace(go.Scatter(
        x=daily_metrics['date'],
        y=daily_metrics[metric_column],
        mode='lines+markers',
        name=metric_name,
        line=dict(color=color, width=2),
        marker=dict(size=6)
    ))
    
    # Add event markers
    for event in config.CRITICAL_EVENTS:
        event_date = datetime.strptime(event['date'], '%Y-%m-%d')
        
        fig.add_vline(
            x=event_date,
            line=dict(color='red', width=2, dash='dash'),
            annotation_text=event['name'],
            annotation_position='top'
        )
    
    fig.update_layout(
        title=metric_name,
        xaxis_title='Date',
        yaxis_title=metric_name,
        hovermode='x unified',
        height=400
    )
    
    return fig


def create_correlation_chart(daily_metrics: pd.DataFrame, lab_data: pd.DataFrame):
    """Create a multi-axis chart showing correlations between Whoop and lab data."""
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Recovery & HRV', 'Sleep Quality', 'Day Strain & Heart Rate'),
        vertical_spacing=0.1,
        shared_xaxes=True
    )
    
    # Recovery & HRV
    fig.add_trace(
        go.Scatter(x=daily_metrics['date'], y=daily_metrics['recovery_score'],
                   name='Recovery Score', line=dict(color='green')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=daily_metrics['date'], y=daily_metrics['hrv_rmssd'],
                   name='HRV (ms)', line=dict(color='lightgreen'),
                   yaxis='y2'),
        row=1, col=1
    )
    
    # Sleep Quality
    fig.add_trace(
        go.Scatter(x=daily_metrics['date'], y=daily_metrics['sleep_performance'],
                   name='Sleep Performance', line=dict(color='purple')),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=daily_metrics['date'], y=daily_metrics['deep_sleep_hours'],
                   name='Deep Sleep (hrs)', line=dict(color='indigo')),
        row=2, col=1
    )
    
    # Strain & HR
    fig.add_trace(
        go.Scatter(x=daily_metrics['date'], y=daily_metrics['day_strain'],
                   name='Day Strain', line=dict(color='orange')),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=daily_metrics['date'], y=daily_metrics['resting_hr'],
                   name='Resting HR', line=dict(color='red')),
        row=3, col=1
    )
    
    # Add event markers
    for event in config.CRITICAL_EVENTS:
        event_date = datetime.strptime(event['date'], '%Y-%m-%d')
        for i in range(1, 4):
            fig.add_vline(
                x=event_date,
                line=dict(color='red', width=2, dash='dash'),
                row=i, col=1
            )
    
    fig.update_layout(height=900, hovermode='x unified', showlegend=True)
    fig.update_xaxes(title_text='Date', row=3, col=1)
    
    return fig


def create_lab_comparison_chart(daily_metrics: pd.DataFrame, lab_data: pd.DataFrame):
    """Create charts comparing lab values with Whoop metrics."""
    if lab_data is None or lab_data.empty:
        return None
    
    # Get unique test names
    test_names = lab_data['test_name'].unique()
    
    charts = {}
    
    # For key biomarkers, create comparison charts
    key_biomarkers = {
        'Glucose': ['recovery_score', 'hrv_rmssd'],
        'Hemoglobin': ['resting_hr', 'spo2'],
        'WBC': ['recovery_score', 'sleep_performance']
    }
    
    for biomarker, whoop_metrics in key_biomarkers.items():
        if biomarker in test_names:
            biomarker_data = lab_data[lab_data['test_name'] == biomarker]
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Add lab values as scatter points
            fig.add_trace(
                go.Scatter(
                    x=biomarker_data['date'],
                    y=biomarker_data['value'],
                    mode='markers',
                    name=f'{biomarker} (Lab)',
                    marker=dict(size=12, color='red', symbol='diamond')
                ),
                secondary_y=False
            )
            
            # Add Whoop metrics
            for i, metric in enumerate(whoop_metrics):
                if metric in daily_metrics.columns:
                    colors = ['blue', 'green', 'purple']
                    fig.add_trace(
                        go.Scatter(
                            x=daily_metrics['date'],
                            y=daily_metrics[metric],
                            name=metric.replace('_', ' ').title(),
                            line=dict(color=colors[i % len(colors)])
                        ),
                        secondary_y=True
                    )
            
            # Add event markers
            for event in config.CRITICAL_EVENTS:
                event_date = datetime.strptime(event['date'], '%Y-%m-%d')
                fig.add_vline(
                    x=event_date,
                    line=dict(color='red', width=2, dash='dash'),
                    annotation_text=event['name']
                )
            
            fig.update_layout(
                title=f'{biomarker} Lab Results vs Whoop Metrics',
                hovermode='x unified',
                height=400
            )
            fig.update_yaxes(title_text=f"{biomarker} (Lab)", secondary_y=False)
            fig.update_yaxes(title_text="Whoop Metrics", secondary_y=True)
            
            charts[biomarker] = fig
    
    return charts


# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select View", ["Overview", "Detailed Metrics", "Lab Correlations", "Data Management"])

# Load data
daily_metrics, lab_data = load_data()

if page == "Overview":
    st.header("Overview")
    
    # Show critical events
    st.subheader("Critical Health Events")
    for event in config.CRITICAL_EVENTS:
        st.markdown(f"**{event['date']}** - {event['name']}")
        st.markdown(f"_{event['description']}_")
        st.markdown("---")
    
    # Show data status
    st.subheader("Data Status")
    col1, col2 = st.columns(2)
    
    with col1:
        if daily_metrics is not None:
            st.success(f"✓ Whoop data loaded ({len(daily_metrics)} days)")
            st.metric("Date Range", f"{daily_metrics['date'].min().date()} to {daily_metrics['date'].max().date()}")
        else:
            st.warning("⚠️ No Whoop data available. Please fetch data first.")
    
    with col2:
        if lab_data is not None:
            st.success(f"✓ Lab data loaded ({len(lab_data)} tests)")
            unique_dates = lab_data['date'].nunique()
            st.metric("Test Dates", unique_dates)
        else:
            st.warning("⚠️ No lab data available. Please parse PDFs first.")

elif page == "Detailed Metrics":
    st.header("Detailed Whoop Metrics")
    
    if daily_metrics is not None:
        # Recovery metrics
        st.subheader("Recovery Metrics")
        col1, col2 = st.columns(2)
        
        with col1:
            if 'recovery_score' in daily_metrics.columns:
                fig = create_timeline_chart(daily_metrics, 'Recovery Score', 'recovery_score', 'green')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'hrv_rmssd' in daily_metrics.columns:
                fig = create_timeline_chart(daily_metrics, 'HRV (RMSSD)', 'hrv_rmssd', 'lightgreen')
                st.plotly_chart(fig, use_container_width=True)
        
        # Sleep metrics
        st.subheader("Sleep Metrics")
        col1, col2 = st.columns(2)
        
        with col1:
            if 'sleep_performance' in daily_metrics.columns:
                fig = create_timeline_chart(daily_metrics, 'Sleep Performance', 'sleep_performance', 'purple')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'deep_sleep_hours' in daily_metrics.columns:
                fig = create_timeline_chart(daily_metrics, 'Deep Sleep (hours)', 'deep_sleep_hours', 'indigo')
                st.plotly_chart(fig, use_container_width=True)
        
        # Cardiovascular metrics
        st.subheader("Cardiovascular Metrics")
        col1, col2 = st.columns(2)
        
        with col1:
            if 'resting_hr' in daily_metrics.columns:
                fig = create_timeline_chart(daily_metrics, 'Resting Heart Rate', 'resting_hr', 'red')
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'day_strain' in daily_metrics.columns:
                fig = create_timeline_chart(daily_metrics, 'Day Strain', 'day_strain', 'orange')
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available. Please fetch Whoop data first.")

elif page == "Lab Correlations":
    st.header("Lab Test Correlations")
    
    if daily_metrics is not None and lab_data is not None:
        # Multi-metric correlation chart
        st.subheader("Whoop Metrics Timeline")
        fig = create_correlation_chart(daily_metrics, lab_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Lab comparison charts
        st.subheader("Lab Results vs Whoop Metrics")
        charts = create_lab_comparison_chart(daily_metrics, lab_data)
        
        if charts:
            for biomarker, fig in charts.items():
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No matching lab biomarkers found for correlation analysis.")
        
        # Lab data table
        st.subheader("Lab Test Results")
        st.dataframe(lab_data)
    else:
        st.warning("Both Whoop and Lab data are required for correlation analysis.")

elif page == "Data Management":
    st.header("Data Management")
    
    # Show authentication status
    auth = WhoopAuth()
    
    if is_authenticated:
        st.success("✓ Authenticated with Whoop")
        col1, col2 = st.columns([3, 1])
        with col2:
            show_logout_button()
    else:
        st.warning("⚠️ Not authenticated with Whoop")
        st.info("Click the button below to authenticate with your Whoop account")
        show_login_button()
        st.stop()  # Don't show rest of page if not authenticated
    
    # Whoop data fetching
    st.subheader("Fetch Whoop Data")
        
        if st.button("Fetch Whoop Data"):
            with st.spinner("Fetching data from Whoop API..."):
                try:
                    client = WhoopClient(auth)
                    processor = HealthDataProcessor()
                    
                    # Fetch all data
                    whoop_data = client.get_all_health_data(
                        config.DATA_START_DATE,
                        config.DATA_END_DATE
                    )
                    
                    # Process data
                    recovery_df = processor.process_whoop_recovery(whoop_data['recovery'])
                    sleep_df = processor.process_whoop_sleep(whoop_data['sleep'])
                    cycles_df = processor.process_whoop_cycles(whoop_data['cycles'])
                    
                    # Combine into daily metrics
                    daily_df = processor.combine_daily_metrics(recovery_df, sleep_df, cycles_df)
                    
                    # Save
                    processor.save_dataframe(daily_df, 'daily_metrics.csv')
                    processor.save_data(whoop_data, 'whoop_raw_data.json')
                    
                    st.success("✓ Data fetched and saved successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error fetching data: {e}")
    
    # Lab data parsing
    st.subheader("Parse Lab Test PDFs")
    
    if st.button("Parse Lab PDFs"):
        with st.spinner("Parsing PDF files..."):
            try:
                parser = LabDataParser()
                processor = HealthDataProcessor()
                
                lab_results = parser.parse_all_pdfs()
                lab_df = processor.process_lab_data(lab_results)
                
                processor.save_dataframe(lab_df, 'lab_data.csv')
                processor.save_data(lab_results, 'lab_raw_data.json')
                
                st.success(f"✓ Parsed {len(lab_results)} PDF files successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error parsing PDFs: {e}")
    
    # Show raw files
    st.subheader("Data Files")
    data_dir = config.DATA_OUTPUT_DIR
    if os.path.exists(data_dir):
        files = os.listdir(data_dir)
        if files:
            for file in files:
                st.text(f"📄 {file}")
        else:
            st.info("No data files yet")
