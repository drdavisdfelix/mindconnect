from database import supabase_client

def create_mood_journal_table():
    try:
        supabase_client.table('mood_journal').select('*').limit(1).execute()
        print("Mood journal table already exists")
    except:
        print("Creating mood journal table...")
        supabase_client.table('mood_journal').create({
            'id': {'type': 'int8', 'primaryKey': True},
            'user_id': {'type': 'uuid', 'foreignKey': {'table': 'users', 'column': 'id'}},
            'mood': {'type': 'int2'},
            'journal_entry': {'type': 'text'},
            'created_at': {'type': 'timestamp', 'default': {'type': 'now'}},
        }).execute()
        print("Mood journal table created successfully")

if __name__ == "__main__":
    create_mood_journal_table()
