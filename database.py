import os
from supabase import create_client, Client
from dotenv import load_dotenv  # Import this

load_dotenv()  # Add this line to load variables from .env

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def initialize_database():
    try:
        # Check if tables exist
        table_exists('users')
        table_exists('reports')
        table_exists('appointments')
        print("Database initialization successful")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

def table_exists(table_name):
    try:
        # Try to fetch a single row from the table
        supabase_client.table(table_name).select('*').limit(1).execute()
        print(f"{table_name} table exists")
        return True
    except Exception as e:
        print(f"{table_name} table does not exist: {str(e)}")
        return False
