import streamlit as st
from auth import login, register, logout
from patient import patient_flow
from professional import professional_flow
from admin import admin_flow
from create_users_table import create_users_table
from create_activities_table import create_activities_table
from create_mood_journal_table import create_mood_journal_table

# Initialize the app
st.set_page_config(page_title="Snuggli - Mental Health Support", layout="wide")

# Add custom CSS
st.markdown(
    """
    <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
    <style>
    .stApp {
        background-color: var(--bs-dark);
        color: var(--bs-light);
    }
    .stSidebar {
        background-color: var(--bs-secondary);
    }
    .stButton > button {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def initialize_database():
    create_users_table()
    create_activities_table()
    create_mood_journal_table()

def main():
    initialize_database()
    
    # Sidebar
    with st.sidebar:
        st.image("assets/logo.svg", width=200)
        st.title("Snuggli")
        
        if 'user' in st.session_state and st.session_state.user:
            st.write(f"Logged in as: {st.session_state.user['email']}")
            if st.button("Logout", key="logout_button"):
                logout()
    
    if 'user' not in st.session_state or st.session_state.user is None:
        st.title("Welcome to Snuggli")
        st.write("Your mental health companion")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="card bg-secondary">
                <div class="card-body">
                    <h3 class="card-title">Login</h3>
                    """, unsafe_allow_html=True)
            login()
            st.markdown("</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="card bg-secondary">
                <div class="card-body">
                    <h3 class="card-title">Register</h3>
                    """, unsafe_allow_html=True)
            register()
            st.markdown("</div></div>", unsafe_allow_html=True)
    else:
        if st.session_state.user['user_type'] == 'patient':
            patient_flow()
        elif st.session_state.user['user_type'] == 'professional':
            professional_flow()
        elif st.session_state.user['user_type'] == 'admin':
            admin_flow()
        else:
            st.error("Invalid user type. Please contact support.")

if __name__ == "__main__":
    main()
