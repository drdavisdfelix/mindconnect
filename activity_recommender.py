import streamlit as st
from database import supabase_client
import openai
import os
from datetime import datetime
from dotenv import load_dotenv  # Import this

load_dotenv()  # Add this line to load variables from .env


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

def get_ai_recommendation(user_data, recent_moods, professional_input):
    prompt = f"""
    Based on the following user data, recent moods, and professional input, suggest 3 activities that could help improve the user's mental health:
    User Data: {user_data}
    Recent Moods: {recent_moods}
    Professional Input: {professional_input}
    
    Provide recommendations in the following format:
    1. Activity Name: [activity]
    Description: [brief description]
    Benefit: [how it can help]
    
    2. Activity Name: [activity]
    Description: [brief description]
    Benefit: [how it can help]
    
    3. Activity Name: [activity]
    Description: [brief description]
    Benefit: [how it can help]
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI trained to recommend mental health activities, taking into account professional input."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )
    
    return response.choices[0].message.content

def insert_activity(user_id, activity_name, description, benefit, status):
    try:
        supabase_client.table('activities').insert({
            'user_id': user_id,
            'activity_name': activity_name,
            'description': description,
            'benefit': benefit,
            'status': status,
            'created_at': datetime.now().isoformat()
        }).execute()
        print('Activity inserted successfully')
        return True
    except Exception as e:
        print(f'Error inserting activity: {str(e)}')
        return False

def get_user_activities(user_id):
    return supabase_client.table('activities').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()

def update_activity_status(activity_id, new_status):
    try:
        supabase_client.table('activities').update({'status': new_status}).eq('id', activity_id).execute()
        return True
    except Exception as e:
        st.error(f"Failed to update activity status: {str(e)}")
        return False

def get_professional_input(user_id):
    professional_input = supabase_client.table('professional_inputs').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(1).execute()
    if professional_input.data:
        return professional_input.data[0]['input']
    return "No professional input available."

def activity_recommendation_system(user_id):
    st.subheader("Activity Recommendations")
    
    # Fetch user data
    user_data_response = supabase_client.table('users').select('*').eq('id', user_id).execute()

    if not user_data_response.data or len(user_data_response.data) != 1:
        st.warning('Unable to fetch user data or multiple users found. Please try again later.')
        return
    
    user_data = user_data_response.data[0]  # Extract user data from the response
    
    # Fetch recent moods
    recent_moods_response = supabase_client.table('mood_journal').select('mood').eq('user_id', user_id).order('created_at', desc=True).limit(5).execute()

    if not recent_moods_response.data:
        st.warning('No recent mood data available. Please log your moods to get personalized recommendations.')
        return
    
    recent_moods = recent_moods_response.data  # Get mood data
    
    # Fetch professional input
    professional_input = get_professional_input(user_id)
    
    # Get AI recommendations
    ai_recommendations = get_ai_recommendation(user_data, recent_moods, professional_input)
    
    st.write("Based on your recent moods, profile, and professional input, here are some recommended activities:")
    st.write(ai_recommendations)
    
    # Display user's existing activities
    st.subheader("Your Activities")
    activities = get_user_activities(user_id)
    
    if activities.data:
        for activity in activities.data:
            with st.expander(f"{activity['activity_name']} - {activity['status']}"):
                st.write(f"Description: {activity['description']}")
                st.write(f"Benefit: {activity['benefit']}")
                new_status = st.selectbox("Update status", ["pending", "in_progress", "completed"], 
                                          index=["pending", "in_progress", "completed"].index(activity['status']),
                                          key=f"status_{activity['id']}")
                if st.button("Update Status", key=f"update_{activity['id']}"):
                    if update_activity_status(activity['id'], new_status):
                        st.success("Activity status updated successfully!")
    else:
        st.info("You haven't added any activities yet. Try adding some from the recommendations above!")
    
    # Allow user to add new activity
    st.subheader("Add New Activity")
    new_activity_name = st.text_input("Activity Name")
    new_activity_description = st.text_area("Description")
    new_activity_benefit = st.text_area("Benefit")
    
    if st.button("Add Activity"):
        if insert_activity(user_id, new_activity_name, new_activity_description, new_activity_benefit, 'pending'):
            st.success("New activity added successfully!")
        else:
            st.error("Failed to add new activity. Please try again.")

def professional_input_form(user_id):
    st.subheader("Professional Input")
    input_text = st.text_area("Provide your professional input for the patient's activities:")
    if st.button("Submit Professional Input"):
        try:
            supabase_client.table('professional_inputs').insert({
                'user_id': user_id,
                'input': input_text,
                'created_at': datetime.now().isoformat()
            }).execute()
            st.success("Professional input submitted successfully!")
        except Exception as e:
            st.error(f"Failed to submit professional input: {str(e)}")
