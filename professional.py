import streamlit as st
from database import supabase_client
from utils import get_patient_reports, update_report_status, schedule_appointment
from activity_recommender import professional_input_form, get_user_activities
from datetime import datetime, timedelta

def professional_flow():
    st.title(f"Welcome, Dr. {st.session_state.user['email']}")
    
    tabs = ["Patient Reports", "Appointments", "Activity Recommendations"]
    icons = ["file-text", "calendar", "list-task"]
    
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
        review_patient_reports()
    
    with tab2:
        manage_appointments()
    
    with tab3:
        manage_activity_recommendations()

def review_patient_reports():
    st.subheader("Patient Reports")
    st.markdown('<div class="card bg-secondary"><div class="card-body">', unsafe_allow_html=True)
    
    reports = get_patient_reports()
    
    if reports:
        for report in reports:
            with st.expander(f"Report for {report['user_email']} - {report['created_at']}"):
                st.write("Summary:", report['summary'])
                st.write("Created at:", report['created_at'])
                st.write("Last updated:", report.get('updated_at', 'Not updated'))
                
                col1, col2 = st.columns(2)
                with col1:
                    status = st.selectbox("Status", ["unreviewed", "reviewed", "requires_followup"], 
                                          index=["unreviewed", "reviewed", "requires_followup"].index(report['status']),
                                          key=f"status_{report['id']}")
                with col2:
                    urgency = st.selectbox("Urgency", ["low", "medium", "high"],
                                           index=["low", "medium", "high"].index(report.get('urgency', 'low')),
                                           key=f"urgency_{report['id']}")
                
                notes = st.text_area("Professional Notes", value=report.get('professional_notes', ''), 
                                     key=f"notes_{report['id']}")
                if st.button("Update Report", key=f"update_{report['id']}", use_container_width=True):
                    if update_report_status(report['id'], status, notes, urgency):
                        st.success("Report updated successfully!")
                    else:
                        st.error("Failed to update report. Please try again.")
    else:
        st.info("No patient reports to review at this time.")
    
    st.markdown('</div></div>', unsafe_allow_html=True)

def manage_appointments():
    st.subheader("Appointment Management")
    st.markdown('<div class="card bg-secondary"><div class="card-body">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Schedule New Appointment")
        patients = supabase_client.table('users').select('id', 'email').eq('user_type', 'patient').execute()
        
        if patients.data:
            with st.form("schedule_appointment"):
                patient_email = st.selectbox("Select Patient", options=[p['email'] for p in patients.data])
                patient_id = next(p['id'] for p in patients.data if p['email'] == patient_email)
                
                date = st.date_input("Select Date", min_value=datetime.now().date())
                time = st.time_input("Select Time")
                
                if st.form_submit_button("Schedule Appointment", use_container_width=True):
                    if schedule_appointment(patient_id, st.session_state.user['id'], date, time):
                        st.success("Appointment scheduled successfully!")
                    else:
                        st.error("Failed to schedule appointment. Please try again.")
        else:
            st.info("No patients found in the system.")
    
    with col2:
        st.write("Upcoming Appointments")
        appointments = (
            supabase_client
            .table('appointments')
            .select('*')
            .eq('professional_id', st.session_state.user['id'])
            .gte('appointment_date', datetime.now().date().isoformat())
            .order('appointment_date')
            .order('appointment_time')
            .execute()
        )
        
        if appointments.data:
            for appointment in appointments.data:
                patient = supabase_client.table('users').select('email').eq('id', appointment['patient_id']).single().execute()
                with st.expander(f"{appointment['appointment_date']} - {appointment['appointment_time']}"):
                    st.write(f"Patient: {patient.data['email']}")
                    st.write(f"Status: {appointment['status']}")
                    new_status = st.selectbox("Update Status", ["scheduled", "completed", "cancelled"], 
                                              index=["scheduled", "completed", "cancelled"].index(appointment['status']),
                                              key=f"appt_status_{appointment['id']}")
                    if st.button("Update Appointment", key=f"update_appt_{appointment['id']}", use_container_width=True):
                        supabase_client.table('appointments').update({'status': new_status}).eq('id', appointment['id']).execute()
                        st.success("Appointment status updated successfully!")
        else:
            st.info("No upcoming appointments scheduled.")
    
    st.markdown('</div></div>', unsafe_allow_html=True)

def manage_activity_recommendations():
    st.subheader("Activity Recommendations")
    st.markdown('<div class="card bg-secondary"><div class="card-body">', unsafe_allow_html=True)
    
    patients = supabase_client.table('users').select('id', 'email').eq('user_type', 'patient').execute()
    
    if patients.data:
        selected_patient = st.selectbox("Select a patient", options=[p['email'] for p in patients.data], format_func=lambda x: x)
        selected_patient_id = next(p['id'] for p in patients.data if p['email'] == selected_patient)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Provide Professional Input")
            professional_input_form(selected_patient_id)
        
        with col2:
            st.write("Patient's Current Activities")
            activities = get_user_activities(selected_patient_id)
            if activities.data:
                for activity in activities.data:
                    with st.expander(f"{activity['activity_name']} - {activity['status']}"):
                        st.write(f"Description: {activity['description']}")
                        st.write(f"Benefit: {activity['benefit']}")
                        st.write(f"Created at: {activity['created_at']}")
                        new_status = st.selectbox("Update status", ["pending", "in_progress", "completed"], 
                                                  index=["pending", "in_progress", "completed"].index(activity['status']),
                                                  key=f"act_status_{activity['id']}")
                        if st.button("Update Activity Status", key=f"update_act_{activity['id']}", use_container_width=True):
                            supabase_client.table('activities').update({'status': new_status}).eq('id', activity['id']).execute()
                            st.success("Activity status updated successfully!")
            else:
                st.info("No activities found for this patient.")
    else:
        st.info("No patients found in the system.")
    
    st.markdown('</div></div>', unsafe_allow_html=True)
