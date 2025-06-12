# Login.py
import streamlit as st

def login_ui():
    st.markdown("""
        <style>
            .logo-title {
                font-size: 3.2rem;
                font-weight: bold;
                color: #2c3e50;
                font-family: 'Trebuchet MS', sans-serif;
                margin-bottom: 1rem;
            }
            .logo-title span.f {
                color: #e74c3c;
                font-size: 4rem;
                font-weight: 900;
            }
            .form-container {
                padding: 2rem;
            }
            .about-section {
                padding: 4rem 3rem;
                font-family: 'Georgia', serif;
                color: #001f3f;
                font-style: italic;
                font-size: 1.2rem;
                line-height: 1.8;
            }
            .stTextInput>div>input {
                border-radius: 6px;
                padding: 0.5rem;
            }
            .main > div {
                padding-top: 0rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.1, 1])

    with col1:
        st.markdown("<div class='form-container'>", unsafe_allow_html=True)
        st.markdown("### Welcome to")
        st.markdown("<div class='logo-title'><span class='f'>F</span>inOptix</div>", unsafe_allow_html=True)

        option = st.radio("Choose an option:", ["Login", "Sign Up"], horizontal=True)

        if option == "Login":
            st.text_input("Email Address", key="login_email")
            st.text_input("Password", type="password", key="login_password")
            if st.button("Login"):
                st.session_state.trigger_login = True
        else:
            st.text_input("First Name", key="signup_first")
            st.text_input("Last Name", key="signup_last")
            st.text_input("Email Address", key="signup_email")
            st.text_input("Password", type="password", key="signup_password")
            if st.button("Sign Up"):
                st.session_state.trigger_signup = True

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='about-section'>", unsafe_allow_html=True)
        st.markdown("""
            FinOptix is an intelligent platform that leverages advanced AI and machine learning 
            algorithms to forecast financial performance and optimize budget allocations.

            It empowers businesses to make data-driven decisions, improve strategic planning, 
            and increase profitability through insightful predictions and automation.
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
