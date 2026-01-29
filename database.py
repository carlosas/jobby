import os
import psycopg2
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = None
        self.connect()
        self.init_db()

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "db"), # Defaulting to 'db' which is likely the service name in docker-compose
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASS"),
                port=os.getenv("DB_PORT", "5432")
            )
        except Exception as e:
            print(f"Database connection failed: {e}")
            self.conn = None

    def init_db(self):
        if not self.conn:
            return
        
        query = """
        CREATE TABLE IF NOT EXISTS interviews (
            id SERIAL PRIMARY KEY,
            audio_filename TEXT NOT NULL,
            transcription TEXT,
            analysis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query)
            self.conn.commit()
        except Exception as e:
            print(f"Error initializing DB: {e}")
            self.conn.rollback()

    def save_transcription(self, filename, text):
        if not self.conn:
            return None
        
        query = """
        INSERT INTO interviews (audio_filename, transcription)
        VALUES (%s, %s)
        RETURNING id;
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (filename, text))
                interview_id = cur.fetchone()[0]
            self.conn.commit()
            return interview_id
        except Exception as e:
            print(f"Error saving transcription: {e}")
            self.conn.rollback()
            return None

    def update_analysis(self, interview_id, analysis_text):
        if not self.conn:
            return
        
        query = """
        UPDATE interviews
        SET analysis = %s
        WHERE id = %s;
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (analysis_text, interview_id))
            self.conn.commit()
        except Exception as e:
            print(f"Error updating analysis: {e}")
            self.conn.rollback()

    def get_interview(self, interview_id):
        if not self.conn:
            return None
            
        query = "SELECT * FROM interviews WHERE id = %s;"
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (interview_id,))
                return cur.fetchone()
        except Exception as e:
            print(f"Error getting interview: {e}")
            return None
