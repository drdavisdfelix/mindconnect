import streamlit as st
from database import supabase_client
from ai_listener import chat_with_ai
from utils import schedule_appointment
from activity_recommender import activity_recommendation_system
from datetime import datetime

def patient_flow():
    st.title(f"Welcome, {st.session_state.user['email']}")
    
    tabs = ["AI Listener", "Appointments", "Mood Tracker", "Activities"]
    icons = ["chat", "calendar", "emoji-smile", "list-task"]
    
    st.markdown(
        f"""
        <ul class="nav nav-tabs">
            {"".join([f'<li class="nav-item"><a class="nav-link" id="tab-{tab}" data-bs-toggle="tab" href="#{tab.lower().replace(" ", "-")}">'
                      f'<i class="bi bi-{icon}"></i> {tab}</a></li>' for tab, icon in zip(tabs, icons)])}
        </ul>
        """,
        unsafe_allow_html=True
    )
    
    tab1, tab2, tab3, tab4 = st.tabs(tabs)
    
    with tab1:
        chat_with_ai_listener()
    
    with tab2:
        schedule_appointment_tab()
    
    with tab3:
        mood_tracker_and_journal()
    
    with tab4:
        activity_recommendation_system(st.session_state.user['id'])

def chat_with_ai_listener():
    st.subheader("Chat with AI Listener")
    st.markdown('<div class="card bg-secondary"><div class="card-body">', unsafe_allow_html=True)
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What's on your mind?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = chat_with_ai(prompt)
            message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    
    st.markdown('</div></div>', unsafe_allow_html=True)

def schedule_appointment_tab():
    st.subheader("Schedule an Appointment")
    st.markdown('<div class="card bg-secondary"><div class="card-body">', unsafe_allow_html=True)
    
    professionals = supabase_client.table('users').select('id', 'email').eq('user_type', 'professional').execute()
    
    if professionals.data:
        with st.form("schedule_appointment"):
            professional = st.selectbox("Choose a professional", 
                                        options=[p['email'] for p in professionals.data],
                                        format_func=lambda x: x)
            date = st.date_input("Select a date")
            time = st.time_input("Select a time")
            
            if st.form_submit_button("Schedule", use_container_width=True):
                professional_id = next(p['id'] for p in professionals.data if p['email'] == professional)
                if schedule_appointment(st.session_state.user['id'], professional_id, date, time):
                    st.success("Appointment scheduled successfully!")
                else:
                    st.error("Failed to schedule appointment. Please try again.")
    else:
        st.info("No professionals available at the moment. Please check back later.")
    
    st.markdown('</div></div>', unsafe_allow_html=True)

def mood_tracker_and_journal():
    st.subheader("Mood Tracker & Journal")
    st.markdown('<div class="card bg-secondary"><div class="card-body">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("How are you feeling today?")
        mood = st.slider("Mood", 1, 10, 5, help="1 = Very low, 10 = Excellent")
    
    with col2:
        journal_entry = st.text_area("Journal Entry", height=150, help="Write about your day, thoughts, or feelings.")
    
    if st.button("Save Mood & Journal Entry", use_container_width=True):
        save_mood_and_journal(mood, journal_entry)
    
    st.subheader("Mood History")
    display_mood_history()
    
    st.markdown('</div></div>', unsafe_allow_html=True)

def save_mood_and_journal(mood, journal_entry):
    user_id = st.session_state.user['id']

    try:
        supabase_client.table('mood_journal').insert({
            'user_id': user_id,
            'mood': mood,
            'journal_entry': journal_entry,
            'created_at': datetime.now().isoformat()
        }).execute()
        st.success("Your mood and journal entry have been saved.")
    except Exception as e:
        st.error(f"Failed to save mood and journal entry: {str(e)}")

def display_mood_history():
    try:
        mood_history = supabase_client.table('mood_journal').select('*').eq('user_id', st.session_state.user['id']).order('created_at', desc=True).limit(10).execute()
        
        if mood_history.data:
            data = [(entry['created_at'][:10], entry['mood']) for entry in mood_history.data]
            dates, moods = zip(*data)
            
            st.line_chart(dict(zip(dates, moods)))
        else:
            st.info("No mood history available yet. Start tracking your mood to see the chart.")

        st.subheader("Recent Journal Entries")
        for entry in mood_history.data:
            with st.expander(f"Entry from {entry['created_at'][:10]}"):
                st.write(f"Mood: {entry['mood']}/10")
                st.write(entry['journal_entry'])
    except Exception as e:
        st.error(f"Failed to retrieve mood history: {str(e)}")
