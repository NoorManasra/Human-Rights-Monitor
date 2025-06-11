import streamlit as st
import requests

API_URL = "https://human-rights-monitor.onrender.com"  # Replace with your actual FastAPI Render URL

st.set_page_config(page_title="Human Rights Violation Reports", layout="wide")

st.title("📢 Human Rights Violation Reporting System")

menu = st.sidebar.selectbox("Choose Action", ["📨 Submit Report", "📋 View Reports", "✅ Update Status"])

# Submit Report
if menu == "📨 Submit Report":
    st.header("Submit a New Report")

    title = st.text_input("Report Title")
    description = st.text_area("Description of the Violation")
    location = st.text_input("Location (optional)")
    anonymous = st.checkbox("Submit Anonymously")
    files = st.file_uploader("Attach Media Files (images/videos)", accept_multiple_files=True)

    if st.button("Submit Report"):
        if not title or not description:
            st.warning("Please fill in the title and description.")
        else:
            files_payload = [("files", (file.name, file, file.type)) for file in files] if files else None
            data = {
                "title": title,
                "description": description,
                "location": location,
                "anonymous": str(anonymous).lower(),
            }

            response = requests.post(f"{API_URL}/submit_report/", data=data, files=files_payload)
            if response.status_code == 200:
                st.success("✅ Report submitted successfully!")
                st.json(response.json())
            else:
                st.error("❌ Failed to submit the report.")

# View Reports
elif menu == "📋 View Reports":
    st.header("All Submitted Reports")

    response = requests.get(f"{API_URL}/reports/")
    if response.status_code == 200:
        reports = response.json()
        if not reports:
            st.info("No reports submitted yet.")
        else:
            for report in reports:
                with st.expander(report["title"]):
                    st.write(f"**ID:** {report['id']}")
                    st.write(f"**Description:** {report['description']}")
                    st.write(f"**Location:** {report.get('location', 'N/A')}")
                    st.write(f"**Anonymous:** {'Yes' if report['anonymous'] else 'No'}")
                    st.write(f"**Status:** {report['status']}")
                    if report["media_files"]:
                        st.write("**Media Files:**")
                        for file_path in report["media_files"]:
                            filename = file_path.split("/")[-1]
                            file_url = f"{API_URL}/download/{filename}"
                            st.markdown(f"[📎 {filename}]({file_url})")

# Update Status
elif menu == "✅ Update Status":
    st.header("Update Report Status")

    report_id = st.text_input("Report ID")
    new_status = st.selectbox("Select New Status", ["Under Review", "In Progress", "Resolved", "Rejected"])

    if st.button("Update Status"):
        if not report_id:
            st.warning("Please enter a Report ID.")
        else:
            response = requests.post(f"{API_URL}/update_status/", params={
                "report_id": report_id,
                "new_status": new_status
            })
            if response.status_code == 200:
                st.success("✅ Status updated successfully!")
            else:
                st.error("❌ Failed to update status. Make sure the ID is correct.")
