import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Human Rights Monitor", layout="wide")

st.title("🕊️ Human Rights Monitor – Victim & Witness Management")

menu = st.sidebar.radio("📂 Select Action", [
    "➕ Add New Victim/Witness",
    "⚠️ Update Risk Level",
    "🔍 View Victim Details",
    "📋 View All Victims in Case",
    "📤 Export Victim Report"
])

# 1️⃣ Add Victim
if menu == "➕ Add New Victim/Witness":
    st.header("➕ Add a New Victim or Witness")
    with st.form("add_victim_form"):
        alias = st.text_input("Pseudonym (optional)")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        age = st.number_input("Age", min_value=0)
        occupation = st.text_input("Occupation")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        case_id = st.text_input("Related Case ID")
        risk_level = st.selectbox("Risk Level", ["low", "medium", "high"])
        threats = st.text_area("Threats (comma-separated)", placeholder="e.g. surveillance, harassment")
        protection = st.checkbox("Needs Protection?")
        submitted = st.form_submit_button("🚀 Submit")
        if submitted:
            data = {
                "type": "victim",
                "anonymous": False if alias else True,
                "demographics": {
                    "gender": gender,
                    "age": age,
                    "occupation": occupation
                },
                "contact_info": {
                    "email": email,
                    "phone": phone
                },
                "cases_involved": [case_id],
                "risk_assessment": {
                    "level": risk_level,
                    "threats": [t.strip() for t in threats.split(",") if t.strip()],
                    "protection_needed": protection
                }
            }
            res = requests.post(f"{API_BASE_URL}/victims/", json=data)
            if res.status_code == 200:
                st.success("✅ Victim added successfully!")
                st.json(res.json())
            else:
                st.error("❌ Failed to add victim.")

# 2️⃣ Update Risk
elif menu == "⚠️ Update Risk Level":
    st.header("⚠️ Update Risk Assessment")
    with st.form("update_risk_form"):
        victim_id = st.text_input("Victim ID")
        new_risk = st.selectbox("New Risk Level", ["low", "medium", "high"])
        new_threats = st.text_area("New Threats (comma-separated)")
        needs_protection = st.checkbox("Still Needs Protection?")
        update_btn = st.form_submit_button("💾 Update")
        if update_btn:
            payload = {
                "level": new_risk,
                "threats": [t.strip() for t in new_threats.split(",") if t.strip()],
                "protection_needed": needs_protection
            }
            res = requests.patch(f"{API_BASE_URL}/victims/{victim_id}", json=payload)
            if res.status_code == 200:
                st.success("✅ Risk level updated.")
            else:
                st.error("❌ Update failed.")

# 3️⃣ View Single Victim
elif menu == "🔍 View Victim Details":
    st.header("🔍 View Victim Information")
    victim_id = st.text_input("Enter Victim ID")
    if st.button("🔍 Search"):
        res = requests.get(f"{API_BASE_URL}/victims/{victim_id}")
        if res.status_code == 200:
            victim = res.json()
            with st.expander("📄 Victim Details"):
                st.json(victim)
        else:
            st.error("❌ Victim not found.")

# 4️⃣ View All Victims in a Case
elif menu == "📋 View All Victims in Case":
    st.header("📋 Victims Linked to a Case")
    case_id = st.text_input("Enter Case ID")
    if st.button("🔍 Fetch Victims"):
        res = requests.get(f"{API_BASE_URL}/victims/case/{case_id}")
        if res.status_code == 200:
            victims = res.json()
            if victims:
                st.success(f"Found {len(victims)} victim(s).")
                for v in victims:
                    with st.expander(f"🧍 Victim ID: {v['id']}"):
                        st.write(v)
            else:
                st.warning("No victims found for this case.")
        else:
            st.error("❌ Failed to fetch victims.")

# 5️⃣ Export Report (placeholder)
elif menu == "📤 Export Victim Report":
    st.header("📤 Export Report (Coming Soon...)")
    st.info("This feature will allow you to generate downloadable PDF or Excel reports of victim data.")
