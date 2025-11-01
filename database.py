"""
Database schema and management for Directory Manager application.
Handles therapists, directories, and profile information.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import os

class DatabaseManager:
    def __init__(self, db_path: str = "directory_manager.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Therapists table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS therapists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                credentials TEXT,
                email TEXT,
                phone TEXT,
                bio TEXT,
                specialties TEXT,  -- JSON array of specialties
                populations TEXT,  -- JSON array of populations served
                therapy_styles TEXT,  -- JSON array of therapy styles
                techniques TEXT,  -- JSON array of techniques used
                interview_responses TEXT,  -- JSON object of interview responses
                writing_style TEXT,  -- AI-generated writing style profile
                npi TEXT,
                license_numbers TEXT,  -- JSON object of license numbers by state
                blue_numbers TEXT,  -- JSON array of FL Blue numbers
                ssn_last_four TEXT,
                medicaid_id TEXT,
                google_form_url TEXT,
                -- Profile Questions Form Data
                personal_introduction TEXT,  -- "What should your client know about you?"
                therapeutic_approach TEXT,  -- "What is your approach to therapy?"
                client_expectations TEXT,  -- "What can clients expect to take away from sessions?"
                availability TEXT,  -- "What is your availability?"
                insurance_providers TEXT,  -- JSON array of insurance providers
                caqh_username TEXT,
                caqh_password TEXT,
                -- Interview Form Data
                career_motivation TEXT,  -- "How did you decide to become a therapist?"
                guiding_principles TEXT,  -- Core beliefs and values
                target_population TEXT,  -- "What clientele do you work with most frequently?"
                work_history TEXT,  -- "What was your previous work before going into therapy?"
                work_rewards TEXT,  -- "What do you find most rewarding about your work?"
                personal_interests TEXT,  -- "What do you enjoy doing in your free time?"
                book_recommendations TEXT,  -- JSON array of recommended books
                specialty_areas TEXT,  -- JSON array of top 3 practice focus areas
                specialty_details TEXT,  -- JSON object with detailed explanations of each specialty
                session_structure TEXT,  -- "What would our first session together be like?"
                homework_approach TEXT,  -- "Do you assign 'homework' between sessions?"
                progress_tracking TEXT,  -- "How do you help ensure I'm making progress in therapy?"
                treatment_duration TEXT,  -- "How long do clients typically see you for?"
                preparation_guidance TEXT,  -- "How can I prepare for our first session?"
                therapy_philosophy TEXT,  -- Advice for therapy seekers
                -- Therapist Info Form Data
                years_experience INTEGER,  -- Years of experience
                ideal_client TEXT,  -- "What is your ideal client or population?"
                treatment_modalities TEXT,  -- JSON array of comfortable treatment approaches
                expertise_areas TEXT,  -- JSON array of areas of expertise
                ocd_subtypes TEXT,  -- JSON array of OCD subtypes experienced
                therapy_style TEXT,  -- "What is your personality/style during therapy?"
                client_feedback TEXT,  -- "What kind of feedback or comments do clients give you?"
                professional_message TEXT,  -- "What message would you give to clients about working with you?"
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Directories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS directories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                base_url TEXT,
                login_url TEXT,
                profile_url_template TEXT,
                is_free BOOLEAN DEFAULT 1,
                is_premium BOOLEAN DEFAULT 0,
                premium_cost REAL,
                ranking_factors TEXT,  -- JSON object of ranking factors
                requirements TEXT,  -- JSON object of site requirements
                notes TEXT,
                -- Scraper Configuration
                scraper_type TEXT DEFAULT 'generic',  -- generic, custom, none
                search_url TEXT,  -- URL template for searches
                profile_selector TEXT,  -- CSS selector for profile containers
                name_selector TEXT,  -- CSS selector for therapist names
                credentials_selector TEXT,  -- CSS selector for credentials
                location_selector TEXT,  -- CSS selector for location
                specialties_selector TEXT,  -- CSS selector for specialties
                profile_url_selector TEXT,  -- CSS selector for profile URLs
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Therapist profiles table (junction table with additional info)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS therapist_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                therapist_id INTEGER,
                directory_id INTEGER,
                profile_url TEXT,
                username TEXT,
                password TEXT,  -- Encrypted
                status TEXT DEFAULT 'active',  -- active, inactive, needs_update, error, exists_unmanaged, needs_claiming, not_found, incorrect_match
                last_updated TIMESTAMP,
                last_checked TIMESTAMP,
                ranking_position INTEGER,
                profile_views INTEGER,
                contact_requests INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (therapist_id) REFERENCES therapists (id),
                FOREIGN KEY (directory_id) REFERENCES directories (id),
                UNIQUE(therapist_id, directory_id)
            )
        ''')
        
        # Automation tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS automation_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                therapist_id INTEGER,
                directory_id INTEGER,
                task_type TEXT,  -- update_profile, create_profile, check_ranking
                status TEXT DEFAULT 'pending',  -- pending, running, completed, failed
                scheduled_time TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                result_data TEXT,  -- JSON object with results
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (therapist_id) REFERENCES therapists (id),
                FOREIGN KEY (directory_id) REFERENCES directories (id)
            )
        ''')
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                therapist_id INTEGER,
                directory_id INTEGER,
                metric_name TEXT,
                metric_value REAL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (therapist_id) REFERENCES therapists (id),
                FOREIGN KEY (directory_id) REFERENCES directories (id)
            )
        ''')
        
        # Media table for photos and videos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS therapist_media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                therapist_id INTEGER NOT NULL,
                media_type TEXT NOT NULL,  -- 'photo' or 'video'
                filename TEXT NOT NULL,
                original_filename TEXT,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                mime_type TEXT,
                description TEXT,
                is_primary BOOLEAN DEFAULT FALSE,
                directory_usage TEXT,  -- JSON array of directories where this media is used
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (therapist_id) REFERENCES therapists (id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()
        conn.close()
        
        # Run migrations for existing databases
        self._run_migrations()
    
    def _run_migrations(self):
        """Run database migrations for existing databases."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if scraper columns exist in directories table
            cursor.execute("PRAGMA table_info(directories)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Add scraper configuration columns if they don't exist
            scraper_columns = [
                ('scraper_type', 'TEXT DEFAULT "generic"'),
                ('search_url', 'TEXT'),
                ('profile_selector', 'TEXT'),
                ('name_selector', 'TEXT'),
                ('credentials_selector', 'TEXT'),
                ('location_selector', 'TEXT'),
                ('specialties_selector', 'TEXT'),
                ('profile_url_selector', 'TEXT')
            ]
            
            for column_name, column_def in scraper_columns:
                if column_name not in columns:
                    cursor.execute(f'ALTER TABLE directories ADD COLUMN {column_name} {column_def}')
                    print(f"Added column {column_name} to directories table")
            
            conn.commit()
            print("Database migrations completed successfully!")
            
        except Exception as e:
            print(f"Migration error: {e}")
        finally:
            conn.close()
    
    def add_therapist(self, name: str, credentials: str = "", email: str = "", 
                     phone: str = "", bio: str = "", specialties: List[str] = None,
                     populations: List[str] = None, therapy_styles: List[str] = None,
                     techniques: List[str] = None, interview_responses: Dict = None) -> int:
        """Add a new therapist to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO therapists (name, credentials, email, phone, bio, specialties,
                                 populations, therapy_styles, techniques, interview_responses)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, credentials, email, phone, bio,
              json.dumps(specialties or []),
              json.dumps(populations or []),
              json.dumps(therapy_styles or []),
              json.dumps(techniques or []),
              json.dumps(interview_responses or {})))
        
        therapist_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return therapist_id
    
    def add_directory(self, name: str, base_url: str = "", login_url: str = "",
                     profile_url_template: str = "", is_free: bool = True,
                     is_premium: bool = False, premium_cost: float = 0.0,
                     ranking_factors: Dict = None, requirements: Dict = None,
                     notes: str = "") -> int:
        """Add a new directory to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO directories (name, base_url, login_url, profile_url_template,
                                  is_free, is_premium, premium_cost, ranking_factors,
                                  requirements, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, base_url, login_url, profile_url_template,
              is_free, is_premium, premium_cost,
              json.dumps(ranking_factors or {}),
              json.dumps(requirements or {}),
              notes))
        
        directory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return directory_id
    
    def add_therapist_profile(self, therapist_id: int, directory_id: int,
                            profile_url: str = "", username: str = "",
                            password: str = "", status: str = "active",
                            notes: str = "") -> int:
        """Add a therapist profile for a specific directory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO therapist_profiles (therapist_id, directory_id, profile_url,
                                          username, password, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (therapist_id, directory_id, profile_url, username, password, status, notes))
        
        profile_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return profile_id
    
    def get_all_therapists(self) -> List[Dict]:
        """Get all therapists with their information."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM therapists ORDER BY name')
        rows = cursor.fetchall()
        
        therapists = []
        for row in rows:
            therapist = {
                'id': row[0],
                'name': row[1],
                'credentials': row[2],
                'email': row[3],
                'phone': row[4],
                'bio': row[5],
                'specialties': json.loads(row[6]) if row[6] else [],
                'populations': json.loads(row[7]) if row[7] else [],
                'therapy_styles': json.loads(row[8]) if row[8] else [],
                'techniques': json.loads(row[9]) if row[9] else [],
                'interview_responses': json.loads(row[10]) if row[10] else {},
                'writing_style': row[11],
                'created_at': row[12],
                'updated_at': row[13]
            }
            therapists.append(therapist)
        
        conn.close()
        return therapists
    
    def get_all_directories(self) -> List[Dict]:
        """Get all directories with their information."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get column names first to handle dynamic schema
        cursor.execute("PRAGMA table_info(directories)")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        
        cursor.execute('SELECT * FROM directories ORDER BY name')
        rows = cursor.fetchall()
        
        directories = []
        for row in rows:
            directory = {}
            for i, column_name in enumerate(column_names):
                if i < len(row):
                    if column_name in ['ranking_factors', 'requirements']:
                        directory[column_name] = json.loads(row[i]) if row[i] else {}
                    elif column_name in ['is_free', 'is_premium']:
                        directory[column_name] = bool(row[i])
                    else:
                        directory[column_name] = row[i]
            
            # Set default values for scraper configuration if not present
            directory.setdefault('scraper_type', 'generic')
            directory.setdefault('search_url', '')
            directory.setdefault('profile_selector', '')
            directory.setdefault('name_selector', '')
            directory.setdefault('credentials_selector', '')
            directory.setdefault('location_selector', '')
            directory.setdefault('specialties_selector', '')
            directory.setdefault('profile_url_selector', '')
            
            directories.append(directory)
        
        conn.close()
        return directories
    
    def get_therapist_profiles(self, therapist_id: int = None, directory_id: int = None) -> List[Dict]:
        """Get therapist profiles, optionally filtered by therapist or directory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if therapist_id and directory_id:
            cursor.execute('''
                SELECT tp.*, t.name as therapist_name, COALESCE(d.name, 'Unknown Directory') as directory_name
                FROM therapist_profiles tp
                JOIN therapists t ON tp.therapist_id = t.id
                LEFT JOIN directories d ON tp.directory_id = d.id
                WHERE tp.therapist_id = ? AND tp.directory_id = ?
            ''', (therapist_id, directory_id))
        elif therapist_id:
            cursor.execute('''
                SELECT tp.*, t.name as therapist_name, COALESCE(d.name, 'Unknown Directory') as directory_name
                FROM therapist_profiles tp
                JOIN therapists t ON tp.therapist_id = t.id
                LEFT JOIN directories d ON tp.directory_id = d.id
                WHERE tp.therapist_id = ?
            ''', (therapist_id,))
        elif directory_id:
            cursor.execute('''
                SELECT tp.*, t.name as therapist_name, COALESCE(d.name, 'Unknown Directory') as directory_name
                FROM therapist_profiles tp
                JOIN therapists t ON tp.therapist_id = t.id
                LEFT JOIN directories d ON tp.directory_id = d.id
                WHERE tp.directory_id = ?
            ''', (directory_id,))
        else:
            cursor.execute('''
                SELECT tp.*, t.name as therapist_name, COALESCE(d.name, 'Unknown Directory') as directory_name
                FROM therapist_profiles tp
                JOIN therapists t ON tp.therapist_id = t.id
                LEFT JOIN directories d ON tp.directory_id = d.id
            ''')
        
        rows = cursor.fetchall()
        
        # Get column names from the cursor description
        column_names = [description[0] for description in cursor.description]
        
        profiles = []
        for row in rows:
            # Convert row to dictionary for easier access
            row_dict = dict(zip(column_names, row))
            
            # Use the stored status from the database
            profile_url = row_dict.get('profile_url')
            stored_status = row_dict.get('status')
            
            # Use the stored status, but mark as missing if no URL
            if profile_url and profile_url.strip():
                actual_status = stored_status
            else:
                actual_status = 'missing'
            
            profile = {
                'id': row_dict.get('id'),
                'therapist_id': row_dict.get('therapist_id'),
                'directory_id': row_dict.get('directory_id'),
                'profile_url': row_dict.get('profile_url'),
                'username': row_dict.get('username'),
                'password': row_dict.get('password'),
                'status': actual_status,  # Use calculated status
                'stored_status': stored_status,  # Keep original for reference
                'last_updated': row_dict.get('last_updated'),
                'last_checked': row_dict.get('last_checked'),
                'ranking_position': row_dict.get('ranking_position'),
                'profile_views': row_dict.get('profile_views'),
                'contact_requests': row_dict.get('contact_requests'),
                'notes': row_dict.get('notes'),
                'created_at': row_dict.get('created_at'),
                'updated_at': row_dict.get('updated_at'),
                'therapist_name': row_dict.get('therapist_name') or 'Unknown Therapist',
                'directory_name': row_dict.get('directory_name') or 'Unknown Directory'
            }
            profiles.append(profile)
        
        conn.close()
        return profiles
    
    def update_therapist_profile(self, profile_id: int, **kwargs) -> bool:
        """Update a therapist profile with new information."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build dynamic update query
        update_fields = []
        values = []
        
        for field, value in kwargs.items():
            if field in ['profile_url', 'username', 'password', 'status', 'notes',
                        'ranking_position', 'profile_views', 'contact_requests']:
                update_fields.append(f"{field} = ?")
                values.append(value)
        
        if not update_fields:
            return False
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(profile_id)
        
        query = f"UPDATE therapist_profiles SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, values)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    def get_coverage_matrix(self) -> Dict:
        """Get a matrix showing therapist coverage across directories."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all therapists and directories
        therapists = self.get_all_therapists()
        directories = self.get_all_directories()
        
        # Create coverage matrix
        matrix = {}
        for therapist in therapists:
            matrix[therapist['name']] = {}
            for directory in directories:
                # Check if profile exists
                profiles = self.get_therapist_profiles(therapist['id'], directory['id'])
                if profiles:
                    profile = profiles[0]
                    # Use the calculated status from the profile
                    # Show as having profile if it's active, exists_unmanaged, or needs_claiming (but not incorrect_match)
                    has_profile = profile['status'] in ['active', 'exists_unmanaged', 'needs_claiming']
                    matrix[therapist['name']][directory['name']] = {
                        'has_profile': has_profile,
                        'status': profile['status'],
                        'url': profile['profile_url'],
                        'last_updated': profile['last_updated']
                    }
                else:
                    matrix[therapist['name']][directory['name']] = {
                        'has_profile': False,
                        'status': 'missing',
                        'url': '',
                        'last_updated': None
                    }
        
        conn.close()
        return matrix

if __name__ == "__main__":
    # Initialize database and add some sample data
    db = DatabaseManager()
    
    # Add sample directories
    directories = [
        {
            'name': 'Psychology Today',
            'base_url': 'https://www.psychologytoday.com',
            'login_url': 'https://member.psychologytoday.com',
            'is_free': False,
            'is_premium': True,
            'premium_cost': 30.0,
            'ranking_factors': {'videos': 'high', 'photos': 'medium', 'reviews': 'high'},
            'requirements': {'bio': True, 'photo': True, 'specialties': True}
        },
        {
            'name': 'Zencare',
            'base_url': 'https://zencare.co',
            'is_free': True,
            'ranking_factors': {'response_time': 'high', 'availability': 'high'},
            'requirements': {'bio': True, 'photo': True, 'insurance': True}
        },
        {
            'name': 'TherapyDen',
            'base_url': 'https://www.therapyden.com',
            'is_free': True,
            'ranking_factors': {'completeness': 'high', 'reviews': 'medium'},
            'requirements': {'bio': True, 'photo': True, 'specialties': True}
        }
    ]
    
    for directory in directories:
        db.add_directory(**directory)
    
    print("Database initialized with sample data!")
