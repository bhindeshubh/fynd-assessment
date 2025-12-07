import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
import os

class FeedbackDatabase:
    """Handles all database operations for the feedback system"""
    
    def __init__(self, db_path: str = "data/feedback.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._create_tables()
    
    def _create_tables(self):
        """Create feedback table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                rating INTEGER NOT NULL,
                review_text TEXT NOT NULL,
                user_response TEXT,
                admin_summary TEXT,
                recommended_actions TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def insert_feedback(self, 
                       rating: int, 
                       review_text: str,
                       user_response: str = None,
                       admin_summary: str = None,
                       recommended_actions: str = None) -> int:
        """
        Insert a new feedback entry
        
        Args:
            rating: Star rating (1-5)
            review_text: User's review text
            user_response: AI-generated response for user
            admin_summary: AI-generated summary for admin
            recommended_actions: AI-generated action items
            
        Returns:
            ID of inserted record
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO feedback 
            (rating, review_text, user_response, admin_summary, recommended_actions)
            VALUES (?, ?, ?, ?, ?)
        """, (rating, review_text, user_response, admin_summary, recommended_actions))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return feedback_id
    
    def get_all_feedback(self) -> pd.DataFrame:
        """
        Retrieve all feedback entries
        
        Returns:
            DataFrame with all feedback
        """
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT 
                id,
                timestamp,
                rating,
                review_text,
                user_response,
                admin_summary,
                recommended_actions
            FROM feedback
            ORDER BY timestamp DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def get_feedback_by_id(self, feedback_id: int) -> Optional[Dict]:
        """Get a specific feedback entry by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM feedback WHERE id = ?
        """, (feedback_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'timestamp': row[1],
                'rating': row[2],
                'review_text': row[3],
                'user_response': row[4],
                'admin_summary': row[5],
                'recommended_actions': row[6]
            }
        return None
    
    def get_feedback_by_rating(self, rating: int) -> pd.DataFrame:
        """Get all feedback with a specific rating"""
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT * FROM feedback 
            WHERE rating = ?
            ORDER BY timestamp DESC
        """
        
        df = pd.read_sql_query(query, conn, params=(rating,))
        conn.close()
        
        return df
    
    def get_recent_feedback(self, limit: int = 10) -> pd.DataFrame:
        """Get most recent feedback entries"""
        conn = sqlite3.connect(self.db_path)
        
        query = f"""
            SELECT * FROM feedback
            ORDER BY timestamp DESC
            LIMIT {limit}
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def get_statistics(self) -> Dict:
        """
        Calculate various statistics about the feedback
        
        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total count
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total_count = cursor.fetchone()[0]
        
        # Average rating
        cursor.execute("SELECT AVG(rating) FROM feedback")
        avg_rating = cursor.fetchone()[0] or 0
        
        # Rating distribution
        cursor.execute("""
            SELECT rating, COUNT(*) as count 
            FROM feedback 
            GROUP BY rating 
            ORDER BY rating
        """)
        rating_dist = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Recent submissions (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) FROM feedback 
            WHERE datetime(timestamp) >= datetime('now', '-1 day')
        """)
        recent_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_submissions': total_count,
            'average_rating': round(avg_rating, 2),
            'rating_distribution': rating_dist,
            'recent_submissions_24h': recent_count
        }
    
    def delete_feedback(self, feedback_id: int) -> bool:
        """Delete a feedback entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return deleted
    
    def export_to_csv(self, filepath: str):
        """Export all feedback to CSV file"""
        df = self.get_all_feedback()
        df.to_csv(filepath, index=False)
        return len(df)
    
    def clear_all_data(self):
        """Clear all feedback data (use with caution!)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM feedback")
        
        conn.commit()
        conn.close()


# Singleton instance
_db_instance = None

def get_database() -> FeedbackDatabase:
    """Get the database instance (singleton pattern)"""
    global _db_instance
    if _db_instance is None:
        _db_instance = FeedbackDatabase()
    return _db_instance