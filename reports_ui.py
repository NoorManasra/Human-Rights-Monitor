def render():


    
    import streamlit as st
    import requests
    
    API_URL = "https://human-rights-monitor.onrender.com"  # ضع رابط الـAPI الخاص بك هنا
    
    
    menu = st.sidebar.selectbox("Choose Action", ["📨 Submit Report", "📋 View Reports", "✅ Update Status", "📊 Reports Analytics"])
    
    if menu == "📨 Submit Report":
        st.header("Submit a New Report")
    
        reporter_type = st.selectbox("Reporter Type", ["witness", "victim", "other"])
        anonymous = st.checkbox("Submit Anonymously")
    
        email = st.text_input("Email (optional)")
        phone = st.text_input("Phone (optional)")
        preferred_contact = st.selectbox("Preferred Contact Method (optional)", ["", "email", "phone"])
    
        incident_date = st.date_input("Date of Incident")
        country = st.text_input("Country")
        city = st.text_input("City")
        longitude = st.number_input("Longitude (optional)", format="%.6f")
        latitude = st.number_input("Latitude (optional)", format="%.6f")
    
        description = st.text_area("Description of the Violation")
    
        violation_types = st.multiselect("Violation Types", [
            "indiscriminate_attacks", "civilian_casualties", "torture", "detention", "forced_displacement",
            "sexual_violence", "child_soldiers", "other"
        ])
    
        files = st.file_uploader("Attach Media Files (images/videos/documents)", accept_multiple_files=True)
    
        if st.button("Submit Report"):
            if not description or not violation_types:
                st.warning("Please fill in the description and select at least one violation type.")
            else:
                files_payload = [("files", (file.name, file, file.type)) for file in files] if files else None
                data = {
                    "reporter_type": reporter_type,
                    "anonymous": str(anonymous).lower(),
                    "email": email,
                    "phone": phone,
                    "preferred_contact": preferred_contact,
                    "incident_date": incident_date.isoformat(),
                    "country": country,
                    "city": city,
                    "longitude": longitude if longitude != 0 else None,
                    "latitude": latitude if latitude != 0 else None,
                    "description": description,
                    "violation_types": violation_types
                }
    
                response = requests.post(f"{API_URL}/reports/", data=data, files=files_payload)
                if response.status_code == 200:
                    st.success("✅ Report submitted successfully!")
                    st.json(response.json())
                else:
                    st.error(f"❌ Failed to submit the report: {response.text}")
    
    elif menu == "📋 View Reports":
        st.header("All Submitted Reports")
    
        status_filter = st.selectbox("Filter by Status", ["", "new", "under review", "in progress", "resolved", "rejected"])
        start_date = st.date_input("Start Date", value=None)
        end_date = st.date_input("End Date", value=None)
        country_filter = st.text_input("Filter by Country")
        city_filter = st.text_input("Filter by City")
    
        # Build query params
        params = {}
        if status_filter:
            params["status"] = status_filter
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        if country_filter:
            params["country"] = country_filter
        if city_filter:
            params["city"] = city_filter
    
        response = requests.get(f"{API_URL}/reports/", params=params)
        if response.status_code == 200:
            reports = response.json()
            if not reports:
                st.info("No reports found.")
            else:
                for report in reports:
                    with st.expander(f"{report['incident_details']['description']} ({report['incident_details']['date']})"):
                        st.write(f"**Report ID:** {report['report_id']}")
                        st.write(f"**Reporter Type:** {report.get('reporter_type', 'N/A')}")
                        st.write(f"**Anonymous:** {'Yes' if report['anonymous'] else 'No'}")
                        st.write(f"**Status:** {report['status']}")
                        loc = report['incident_details']['location']
                        st.write(f"**Location:** {loc.get('city','')} - {loc.get('country','')}")
                        st.write(f"**Violation Types:** {', '.join(report['incident_details']['violation_types'])}")
    
                        if report["media_files"]:
                            st.write("Media Files:")
                            for filename in report["media_files"]:
                                st.write(f"- [Download]({API_URL}/download/{filename})")
    
        else:
            st.error("Failed to load reports")
    
    elif menu == "✅ Update Status":
        st.header("Update Report Status")
        report_id = st.text_input("Enter Report ID")
        new_status = st.selectbox("New Status", ["new", "under review", "in progress", "resolved", "rejected"])
        if st.button("Update Status"):
            if not report_id:
                st.warning("Please enter a valid Report ID.")
            else:
                response = requests.patch(f"{API_URL}/reports/{report_id}", data={"new_status": new_status})
                if response.status_code == 200:
                    st.success("Status updated successfully!")
                else:
                    st.error(f"Failed to update status: {response.text}")
    
    elif menu == "📊 Reports Analytics":
        st.header("Reports Analytics")
        response = requests.get(f"{API_URL}/reports/analytics")
        if response.status_code == 200:
            analytics = response.json()
            st.bar_chart(analytics)
        else:
            st.error("Failed to fetch analytics data.")
