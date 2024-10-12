from database import supabase_client

def create_users_table():
    try:
        supabase_client.table('users').select('*').limit(1).execute()
        print("Users table already exists")
    except:
        print("Creating users table...")
        supabase_client.table('users').create({
            'id': {'type': 'uuid', 'primaryKey': True},
            'email': {'type': 'text', 'unique': True},
            'user_type': {'type': 'text'},
            'created_at': {'type': 'timestamp', 'default': {'type': 'now'}},
        }).execute()
        print("Users table created successfully")

if __name__ == "__main__":
    create_users_table()
