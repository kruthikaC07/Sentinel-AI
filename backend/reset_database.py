from app.database import init_db, reset_database


if __name__ == "__main__":
    init_db()
    reset_database()
    print("Supabase PostgreSQL database reset complete.")
