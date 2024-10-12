import streamlit as st
from database import supabase_client
from datetime import datetime

def login():
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submit_button = st.form_submit_button("Login", use_container_width=True)
        
    if submit_button:
        try:
            response = supabase_client.auth.sign_in_with_password({"email": email, "password": password})
            user = response.user
            if user:
                st.session_state.user = {
                    'id': user.id,
                    'email': user.email,
                    'user_type': user.user_metadata.get('user_type', 'patient')
                }
                st.success("Logged in successfully!")
                st.rerun()
        except Exception as e:
            st.error(f"Login failed: {str(e)}")

def register():
    with st.form("register_form"):
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        user_type = st.selectbox("User Type", ["patient", "professional"], key="register_user_type")
        submit_button = st.form_submit_button("Register", use_container_width=True)

    if submit_button:
        try:
            # Register user using Supabase Auth
            response = supabase_client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "user_type": user_type
                    }
                }
            })

            # Insert into the custom users table if registration was successful
            if response.user:
                user_id = response.user.id
                email = response.user.email

                # Insert user details into the users table
                supabase_client.table('users').insert({
                    'id': user_id,
                    'email': email,
                    'user_type': user_type
                    # 'created_at': datetime.now().isoformat()  # Optional: if you want to track when the user was created
                }).execute()

                st.success("Registered successfully! Please log in.")
        except Exception as e:
            st.error(f"Registration failed: {str(e)}")

def logout():
    supabase_client.auth.sign_out()
    st.session_state.user = None
    st.rerun()
