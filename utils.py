from database import supabase_client
from datetime import datetime

def schedule_appointment(patient_id, professional_id, date, time):
    try:
        appointment_data = {
            'patient_id': patient_id,
            'professional_id': professional_id,
            'appointment_date': date.isoformat(),
            'appointment_time': time.isoformat(),
            'status': 'scheduled'
        }
        
        supabase_client.table('appointments').insert(appointment_data).execute()
        return True
    except Exception as e:
        print(f"Error scheduling appointment: {str(e)}")
        return False

def get_patient_reports():
    try:
        reports = supabase_client.table('reports').select('*').execute()
        enhanced_reports = []
        for report in reports.data:
            user = supabase_client.table('users').select('email').eq('id', report['user_id']).single().execute()
            report['user_email'] = user.data['email']
            enhanced_reports.append(report)
        return enhanced_reports
    except Exception as e:
        print(f"Error fetching patient reports: {str(e)}")
        return []

def update_report_status(report_id, status, notes, urgency):
    try:
        supabase_client.table('reports').update({
            'status': status,
            'professional_notes': notes,
            'urgency': urgency,
            'updated_at': datetime.now().isoformat()
        }).eq('id', report_id).execute()
        return True
    except Exception as e:
        print(f"Error updating report status: {str(e)}")
        return False

def get_user_activities(user_id):
    try:
        activities = supabase_client.table('activities').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return activities
    except Exception as e:
        print(f"Error fetching user activities: {str(e)}")
        return None
