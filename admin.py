import streamlit as st
from database import supabase_client
from datetime import datetime, timedelta

def admin_flow():
    st.title("Admin Dashboard")
    
    tabs = ["User Management", "System Statistics", "Activity Log"]
    icons = ["people", "graph-up", "clock-history"]
    
    st.markdown(
        f"""
        <ul class="nav nav-tabs">
            {"".join([f'<li class="nav-item"><a class="nav-link" id="tab-{tab}" data-bs-toggle="tab" href="#{tab.lower().replace(" ", "-")}">'
                      f'<i class="bi bi-{icon}"></i> {tab}</a></li>' for tab, icon in zip(tabs, icons)])}
        </ul>
        """,
        unsafe_allow_html=True
    )
    
    tab1, tab2, tab3 = st.tabs(tabs)
    
    with tab1:
        manage_users()
    
    with tab2:
        display_statistics()
    
    with tab3:
        display_activity_log()

def manage_users():
    st.subheader("User Management")
    st.markdown('<div class="card bg-secondary"><div class="card-body">', unsafe_allow_html=True)
    
    users = supabase_client.table('users').select('*').execute()
    
    if users.data:
        for user in users.data:
            with st.expander(f"User: {user['email']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"User Type: {user['user_type']}")
                with col2:
                    st.write(f"Created At: {user['created_at']}")
                with col3:
                    new_status = st.selectbox("Status", ["active", "inactive"], 
                                              index=0 if user.get('status', 'active') == 'active' else 1,
                                              key=f"status_{user['id']}")
                new_user_type = st.selectbox("User Type", ["patient", "professional", "admin"],
                                             index=["patient", "professional", "admin"].index(user['user_type']),
                                             key=f"type_{user['id']}")
                if st.button("Update User", key=f"update_{user['id']}", use_container_width=True):
                    update_user(user['id'], new_status, new_user_type)
                    st.success(f"User {user['email']} updated successfully")
    else:
        st.info("No users found in the system.")
    
    st.markdown('</div></div>', unsafe_allow_html=True)

def update_user(user_id, status, user_type):
    supabase_client.table('users').update({'status': status, 'user_type': user_type}).eq('id', user_id).execute()

def display_statistics():
    st.subheader("System Statistics")
    st.markdown('<div class="card bg-secondary"><div class="card-body">', unsafe_allow_html=True)
    
    total_users = len(supabase_client.table('users').select('id').execute().data)
    total_patients = len(supabase_client.table('users').select('id').eq('user_type', 'patient').execute().data)
    total_professionals = len(supabase_client.table('users').select('id').eq('user_type', 'professional').execute().data)
    total_reports = len(supabase_client.table('reports').select('id').execute().data)
    total_appointments = len(supabase_client.table('appointments').select('id').execute().data)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users", total_users)
    col2.metric("Total Patients", total_patients)
    col3.metric("Total Professionals", total_professionals)
    
    col4, col5 = st.columns(2)
    col4.metric("Total Reports Generated", total_reports)
    col5.metric("Total Appointments Scheduled", total_appointments)
    
    st.subheader("User Growth")
    user_growth = get_user_growth()
    st.line_chart(user_growth)
    
    st.subheader("Activity Distribution")
    activity_distribution = get_activity_distribution()
    st.bar_chart(activity_distribution)
    
    st.markdown('</div></div>', unsafe_allow_html=True)

def get_user_growth():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    user_growth = supabase_client.table('users').select('created_at').gte('created_at', start_date.isoformat()).lte('created_at', end_date.isoformat()).execute()
    
    growth_data = {}
    for user in user_growth.data:
        date = user['created_at'].split('T')[0]
        growth_data[date] = growth_data.get(date, 0) + 1
    
    return growth_data

def get_activity_distribution():
    activities = supabase_client.table('activities').select('status', 'count').execute()
    
    distribution = {activity['status']: activity['count'] for activity in activities.data}
    return distribution

def display_activity_log():
    st.subheader("Recent Activity Log")
    st.markdown('<div class="card bg-secondary"><div class="card-body">', unsafe_allow_html=True)
    
    activities = supabase_client.table('activities').select('*').order('created_at', desc=True).limit(50).execute()
    
    if activities.data:
        for activity in activities.data:
            st.write(f"User ID: {activity['user_id']} - Activity: {activity['activity_name']} - Status: {activity['status']} - Created At: {activity['created_at']}")
    else:
        st.info("No recent activities found.")
    
    st.markdown('</div></div>', unsafe_allow_html=True)
