"""
CareerCompass AI — Local Data Storage Manager
Thread-safe, parameterized SQLite3 persistence for student profiles, recommendations, and roadmap progress.
"""

import os
import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "careercompass.db")

class StorageManager:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        # Ensure parent directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initializes tables using safe DDL."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Profiles table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    education_level TEXT,
                    current_year TEXT,
                    academic_stream TEXT,
                    experience_level TEXT,
                    preferred_category TEXT,
                    learning_preference TEXT,
                    available_hours_per_day REAL,
                    interests_json TEXT,
                    subjects_json TEXT,
                    skills_json TEXT,
                    activities_json TEXT,
                    work_style TEXT,
                    work_focus TEXT,
                    recommendations_json TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)

            # Roadmap progress table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roadmap_progress (
                    profile_id TEXT,
                    career_id TEXT,
                    completed_stages_json TEXT,
                    updated_at TEXT,
                    PRIMARY KEY (profile_id, career_id)
                )
            """)
            conn.commit()

    def save_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Saves or updates a student profile with full JSON serialization."""
        profile_id = profile_data.get("id") or str(uuid.uuid4())
        name = (profile_data.get("name") or "Anonymous Student").strip()
        education_level = profile_data.get("education_level", "")
        current_year = profile_data.get("current_year", "")
        academic_stream = profile_data.get("academic_stream", "")
        experience_level = profile_data.get("experience_level", "Beginner")
        preferred_category = profile_data.get("preferred_category", "All")
        learning_preference = profile_data.get("learning_preference", "Hands-on projects")
        available_hours = float(profile_data.get("available_hours_per_day", 2.0) or 2.0)

        interests = json.dumps(profile_data.get("interests", []))
        subjects = json.dumps(profile_data.get("favourite_subjects", profile_data.get("subjects", [])))
        skills = json.dumps(profile_data.get("existing_skills", profile_data.get("skills", [])))
        activities = json.dumps(profile_data.get("activities", []))
        work_style = profile_data.get("work_style", "Team-based")
        work_focus = profile_data.get("work_focus", "Analytical")
        recommendations = json.dumps(profile_data.get("recommendations", []))

        now_str = datetime.utcnow().isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, created_at FROM profiles WHERE id = ?", (profile_id,))
            existing = cursor.fetchone()

            if existing:
                cursor.execute("""
                    UPDATE profiles SET
                        name = ?, education_level = ?, current_year = ?, academic_stream = ?,
                        experience_level = ?, preferred_category = ?, learning_preference = ?,
                        available_hours_per_day = ?, interests_json = ?, subjects_json = ?,
                        skills_json = ?, activities_json = ?, work_style = ?, work_focus = ?,
                        recommendations_json = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    name, education_level, current_year, academic_stream,
                    experience_level, preferred_category, learning_preference,
                    available_hours, interests, subjects, skills, activities,
                    work_style, work_focus, recommendations, now_str, profile_id
                ))
                created_at = existing["created_at"]
            else:
                created_at = now_str
                cursor.execute("""
                    INSERT INTO profiles (
                        id, name, education_level, current_year, academic_stream,
                        experience_level, preferred_category, learning_preference,
                        available_hours_per_day, interests_json, subjects_json,
                        skills_json, activities_json, work_style, work_focus,
                        recommendations_json, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile_id, name, education_level, current_year, academic_stream,
                    experience_level, preferred_category, learning_preference,
                    available_hours, interests, subjects, skills, activities,
                    work_style, work_focus, recommendations, created_at, now_str
                ))
            conn.commit()

        return self.get_profile(profile_id)

    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single profile by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_profile(row)

    def list_profiles(self) -> List[Dict[str, Any]]:
        """Returns all saved profiles sorted by most recently updated."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM profiles ORDER BY updated_at DESC")
            rows = cursor.fetchall()
            return [self._row_to_profile(r) for r in rows]

    def delete_profile(self, profile_id: str) -> bool:
        """Deletes a profile and associated roadmap progress."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
            deleted = cursor.rowcount > 0
            cursor.execute("DELETE FROM roadmap_progress WHERE profile_id = ?", (profile_id,))
            conn.commit()
            return deleted

    def update_roadmap_progress(self, profile_id: str, career_id: str, completed_stages: List[int]) -> Dict[str, Any]:
        """Saves completed roadmap stage IDs for a specific career."""
        now_str = datetime.utcnow().isoformat()
        stages_json = json.dumps(completed_stages)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO roadmap_progress (profile_id, career_id, completed_stages_json, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(profile_id, career_id) DO UPDATE SET
                    completed_stages_json = excluded.completed_stages_json,
                    updated_at = excluded.updated_at
            """, (profile_id, career_id, stages_json, now_str))
            conn.commit()

        return {
            "profile_id": profile_id,
            "career_id": career_id,
            "completed_stages": completed_stages,
            "updated_at": now_str
        }

    def get_roadmap_progress(self, profile_id: str, career_id: str) -> List[int]:
        """Retrieves list of completed stage numbers."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT completed_stages_json FROM roadmap_progress
                WHERE profile_id = ? AND career_id = ?
            """, (profile_id, career_id))
            row = cursor.fetchone()
            if row and row["completed_stages_json"]:
                try:
                    return json.loads(row["completed_stages_json"])
                except Exception:
                    return []
            return []

    def _row_to_profile(self, row: sqlite3.Row) -> Dict[str, Any]:
        try:
            interests = json.loads(row["interests_json"] or "[]")
        except Exception:
            interests = []
        try:
            subjects = json.loads(row["subjects_json"] or "[]")
        except Exception:
            subjects = []
        try:
            skills = json.loads(row["skills_json"] or "[]")
        except Exception:
            skills = []
        try:
            activities = json.loads(row["activities_json"] or "[]")
        except Exception:
            activities = []
        try:
            recs = json.loads(row["recommendations_json"] or "[]")
        except Exception:
            recs = []

        return {
            "id": row["id"],
            "name": row["name"],
            "education_level": row["education_level"],
            "current_year": row["current_year"],
            "academic_stream": row["academic_stream"],
            "experience_level": row["experience_level"],
            "preferred_category": row["preferred_category"],
            "learning_preference": row["learning_preference"],
            "available_hours_per_day": row["available_hours_per_day"],
            "interests": interests,
            "favourite_subjects": subjects,
            "existing_skills": skills,
            "activities": activities,
            "work_style": row["work_style"],
            "work_focus": row["work_focus"],
            "recommendations": recs,
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
