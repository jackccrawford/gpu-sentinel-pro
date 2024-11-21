import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def test_supabase_connection():
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("Error: Missing Supabase credentials in .env file")
            return False

        # Initialize Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Try a simple query to test connection
        test_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "test": True,
            "message": "Connection test"
        }
        
        print("Attempting to connect to Supabase...")
        result = supabase.table('gpu_metrics').insert(test_data).execute()
        
        print("Successfully connected to Supabase!")
        print("\nTest record inserted:")
        print(result)
        return True

    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        return False

if __name__ == "__main__":
    test_supabase_connection()