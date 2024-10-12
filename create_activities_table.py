from database import supabase_client

def create_activities_table():
    try:
        supabase_client.table('activities').select('*').limit(1).execute()
        print("Activities table already exists")
    except:
        print("Creating activities table...")
        supabase_client.table('activities').create({
            'id': {'type': 'int8', 'primaryKey': True},
            'user_id': {'type': 'uuid', 'foreignKey': {'table': 'users', 'column': 'id'}},
            'activity_name': {'type': 'text'},
            'description': {'type': 'text'},
            'benefit': {'type': 'text'},
            'status': {'type': 'text'},
            'created_at': {'type': 'timestamp', 'default': {'type': 'now'}},
        }).execute()
        print("Activities table created successfully")

if __name__ == "__main__":
    create_activities_table()
