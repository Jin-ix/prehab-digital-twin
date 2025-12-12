import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# Configuration
API_URL = "http://127.0.0.1:8000/api/v1"

st.set_page_config(page_title="Prehab 2.0 | Elite Sports Twin", layout="wide")

# === SESSION STATE ===
if 'token' not in st.session_state:
    st.session_state.token = None

# === SIDEBAR: LOGIN ===
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3048/3048122.png", width=100)
    st.title("Prehab 2.0 Enterprise")
    
    if not st.session_state.token:
        email = st.text_input("Email", "coach@keralablasters.com")
        password = st.text_input("Password", "securepassword123", type="password")
        if st.button("Login"):
            try:
                res = requests.post(f"{API_URL}/auth/login", data={"username": email, "password": password})
                if res.status_code == 200:
                    st.session_state.token = res.json()["access_token"]
                    st.success("Logged In!")
                    st.rerun()
                else:
                    st.error("Invalid Credentials")
            except:
                st.error("Server is Offline")
    else:
        st.write("Logged in as **Coach Ivan**")
        if st.button("Logout"):
            st.session_state.token = None
            st.rerun()

# === MAIN DASHBOARD ===
if st.session_state.token:
    st.title("⚽ Player Digital Twin Dashboard")
    
    tab1, tab2 = st.tabs(["🎥 AI Video Analysis", "📊 Team Status"])
    
    # --- TAB 1: VIDEO UPLOAD ---
    with tab1:
        st.write("Upload training footage to detect biomechanical risks.")
        uploaded_file = st.file_uploader("Upload Athlete Video", type=['mp4', 'mov', 'avi'])
        
        if uploaded_file:
            col1, col2 = st.columns(2)
            with col1:
                st.video(uploaded_file)
            
            with col2:
                if st.button("Run Digital Twin Analysis"):
                    with st.spinner("AI is analyzing biomechanics..."):
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        files = {"file": uploaded_file.getvalue()}
                        
                        try:
                            res = requests.post(f"{API_URL}/analytics/analyze/video", headers=headers, files=files)
                            
                            if res.status_code == 200:
                                data = res.json()
                                
                                # 1. DISPLAY SCORE
                                risk_score = data['score']
                                color = "red" if risk_score > 40 else "green"
                                st.markdown(f"## Injury Risk Score: <span style='color:{color}'>{risk_score}/100</span>", unsafe_allow_html=True)
                                
                                st.divider()

                                # 2. DISPLAY ALERTS (LOOP THROUGH ALL)
                                if data['alerts']:
                                    st.subheader("🚨 Detected Risks")
                                    for alert in data['alerts']:
                                        st.error(alert)
                                else:
                                    st.success("✅ Mechanics look safe.")
                                
                                # 3. DISPLAY PRESCRIPTIONS (LOOP THROUGH ALL)
                                if data['recommendations']:
                                    st.subheader("💪 Prescribed Protocol")
                                    for rx in data['recommendations']:
                                        st.info(rx)
                                
                            else:
                                st.error(f"API Error: {res.text}")
                        except Exception as e:
                            st.error(f"Connection Failed: {e}")

    # --- TAB 2: MOCK TEAM DATA ---
    with tab2:
        st.subheader("Team Workload Management")
        mock_data = pd.DataFrame({
            "Player": ["Rona", "Messi", "Neymar", "Chhetri"],
            "Acute Load": [1.5, 0.8, 1.2, 0.9], 
            "Recovery": [40, 90, 60, 85]
        })
        
        fig = go.Figure(data=[
            go.Bar(name='ACWR (Load)', x=mock_data['Player'], y=mock_data['Acute Load'], marker_color='indianred'),
            go.Bar(name='Recovery %', x=mock_data['Player'], y=mock_data['Recovery']/100, marker_color='lightgreen')
        ])
        st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Please login from the sidebar to access the Digital Twin.")