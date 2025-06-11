import streamlit as st


# Set wide layout and page title
st.set_page_config(page_title="Human Rights MIS Dashboard", layout="wide")

# Sidebar Navigation
st.sidebar.title("📊 Human Rights MIS")
st.sidebar.markdown("Navigate between system modules")
selected_tab = st.sidebar.radio("Modules", [
    "Case Management",
    "Incident Reporting",
    "Victims/Witnesses",
    "Analytics"
])

# Render each page based on selection
if selected_tab == "Case Management":
    st.title("📝 Case Management System")
    try:
        from app import render as render_case_management
        render_case_management()
    except ImportError:
        st.warning("Case Management module not found or render() missing.")

elif selected_tab == "Incident Reporting":
    st.title("📮 Incident Reporting")
    try:
        from reports_ui import render as render_incident_reporting
        render_incident_reporting()
    except ImportError:
        st.warning("Incident Reporting module not found or render() missing.")

elif selected_tab == "Victims/Witnesses":
    st.title("🧍 Victim/Witness Database")
    try:
        from victims import render as render_victims
        render_victims()
    except ImportError:
        st.warning("Victims module not found or render() missing.")

elif selected_tab == "Analytics":
    st.title("📈 Data Analysis & Visualization")
    try:
        from analytics_ui import render as render_analytics
        render_analytics()
    except ImportError:
        st.warning("Analytics module not found or render() missing.")
