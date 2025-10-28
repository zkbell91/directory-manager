"""
Google Form Data Importer for Directory Manager
Parses and imports therapist data from Google Form CSV exports
"""

import pandas as pd
import json
import re
from typing import Dict, List, Optional
from database import DatabaseManager

class GoogleFormImporter:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def import_profile_questions(self, csv_path: str) -> Dict:
        """Import Profile Questions form data."""
        try:
            df = pd.read_csv(csv_path)
            stats = {'therapists_updated': 0, 'errors': []}
            
            for _, row in df.iterrows():
                try:
                    # Extract therapist name from timestamp or other identifier
                    therapist_name = self._extract_therapist_name(row)
                    if not therapist_name:
                        continue
                    
                    # Find therapist in database
                    therapist_id = self._find_therapist_by_name(therapist_name)
                    if not therapist_id:
                        stats['errors'].append(f"Therapist not found: {therapist_name}")
                        continue
                    
                    # Extract form data
                    form_data = {
                        'personal_introduction': self._clean_text(row.get('What should your client know about you?', '')),
                        'therapeutic_approach': self._clean_text(row.get('What is your approach to therapy?', '')),
                        'client_expectations': self._clean_text(row.get('What can clients expect to take away from sessions with you?', '')),
                        'availability': self._clean_text(row.get('What is your availability?', '')),
                        'insurance_providers': self._parse_insurance_providers(row.get('Please list any insurers that you are in-network with.', '')),
                        'caqh_username': self._clean_text(row.get('CAQH Username:', '')),
                        'caqh_password': self._clean_text(row.get('CAQH Password:', '')),
                        'npi': self._clean_text(row.get('What is your NPI?', '')),
                        'place_of_birth': self._clean_text(row.get('What is your place of birth (city, state, country)?', ''))
                    }
                    
                    # Update therapist with form data
                    self._update_therapist_form_data(therapist_id, form_data)
                    stats['therapists_updated'] += 1
                    
                except Exception as e:
                    stats['errors'].append(f"Error processing row: {str(e)}")
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def import_therapist_interview(self, csv_path: str) -> Dict:
        """Import Therapist Interview form data."""
        try:
            df = pd.read_csv(csv_path)
            stats = {'therapists_updated': 0, 'errors': []}
            
            for _, row in df.iterrows():
                try:
                    therapist_name = self._clean_text(row.get('Your full name:', ''))
                    if not therapist_name:
                        continue
                    
                    # Find therapist in database
                    therapist_id = self._find_therapist_by_name(therapist_name)
                    if not therapist_id:
                        stats['errors'].append(f"Therapist not found: {therapist_name}")
                        continue
                    
                    # Extract interview data
                    interview_data = {
                        'career_motivation': self._clean_text(row.get('How did you decide to become a therapist?', '')),
                        'guiding_principles': self._clean_text(row.get('What guiding principles inform your work?', '')),
                        'target_population': self._clean_text(row.get('What clientele do you work with most frequently?', '')),
                        'work_history': self._clean_text(row.get('What was your previous work before going into therapy?', '')),
                        'work_rewards': self._clean_text(row.get('What do you find most rewarding about your work?', '')),
                        'personal_interests': self._clean_text(row.get('What do you enjoy doing in your free time?', '')),
                        'book_recommendations': self._parse_book_recommendations(row.get('Are there any books you often recommend to clients?', '')),
                        'specialty_areas': self._parse_specialty_areas(row),
                        'specialty_details': self._parse_specialty_details(row),
                        'session_structure': self._clean_text(row.get('What would our first session together be like? What happens in ongoing sessions?', '')),
                        'homework_approach': self._clean_text(row.get('Do you assign "homework" between sessions?', '')),
                        'progress_tracking': self._clean_text(row.get('How do you help ensure I\'m making progress in therapy?', '')),
                        'treatment_duration': self._clean_text(row.get('How long do clients typically see you for?', '')),
                        'preparation_guidance': self._clean_text(row.get('How can I prepare for our first session?', '')),
                        'therapy_philosophy': self._clean_text(row.get('What advice would you share with therapy seekers?', ''))
                    }
                    
                    # Update therapist with interview data
                    self._update_therapist_interview_data(therapist_id, interview_data)
                    stats['therapists_updated'] += 1
                    
                except Exception as e:
                    stats['errors'].append(f"Error processing row: {str(e)}")
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def import_therapist_info(self, csv_path: str) -> Dict:
        """Import Therapist Info form data."""
        try:
            df = pd.read_csv(csv_path)
            stats = {'therapists_updated': 0, 'errors': []}
            
            for _, row in df.iterrows():
                try:
                    # Extract username/email to match therapist
                    username = self._clean_text(row.get('Username', ''))
                    if not username:
                        continue
                    
                    # Find therapist by email/username
                    therapist_id = self._find_therapist_by_email(username)
                    if not therapist_id:
                        stats['errors'].append(f"Therapist not found: {username}")
                        continue
                    
                    # Extract years of experience
                    years_exp = self._parse_years_experience(row.get('How many years of experience as a therapist do you have?', ''))
                    
                    # Extract form data
                    info_data = {
                        'years_experience': years_exp,
                        'ideal_client': self._clean_text(row.get('What is your ideal client or population?', '')),
                        'treatment_modalities': self._parse_treatment_approaches(row.get('Treatment approaches that you are comfortable with:', '')),
                        'expertise_areas': self._parse_expertise_areas(row.get('Areas of Expertise:', '')),
                        'ocd_subtypes': self._parse_ocd_subtypes(row.get('What subtypes of OCD do you have experience treating?', '')),
                        'therapy_style': self._clean_text(row.get('What is your personality/style during therapy?', '')),
                        'client_feedback': self._clean_text(row.get('What kind of feedback or comments do clients give you?', '')),
                        'professional_message': self._clean_text(row.get('What message would you give to clients about working with you?', ''))
                    }
                    
                    # Update therapist with info data
                    self._update_therapist_info_data(therapist_id, info_data)
                    stats['therapists_updated'] += 1
                    
                except Exception as e:
                    stats['errors'].append(f"Error processing row: {str(e)}")
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_therapist_name(self, row) -> Optional[str]:
        """Extract therapist name from various possible fields."""
        # Try different name fields
        name_fields = ['Your full name:', 'Name', 'Therapist Name']
        for field in name_fields:
            if field in row and pd.notna(row[field]):
                return self._clean_text(row[field])
        return None
    
    def _find_therapist_by_name(self, name: str) -> Optional[int]:
        """Find therapist by name in database."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM therapists WHERE name LIKE ?', (f'%{name}%',))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def _find_therapist_by_email(self, email: str) -> Optional[int]:
        """Find therapist by email in database."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM therapists WHERE email = ?', (email,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def _clean_text(self, text) -> str:
        """Clean and normalize text data."""
        if pd.isna(text) or text == '':
            return ''
        return str(text).strip()
    
    def _parse_insurance_providers(self, text: str) -> List[str]:
        """Parse insurance providers from text."""
        if not text or pd.isna(text):
            return []
        
        # Split by common delimiters
        providers = re.split(r'[,;]', str(text))
        return [p.strip() for p in providers if p.strip()]
    
    def _parse_book_recommendations(self, text: str) -> List[str]:
        """Parse book recommendations from text."""
        if not text or pd.isna(text):
            return []
        
        # Split by newlines or common delimiters
        books = re.split(r'[\n;]', str(text))
        return [b.strip() for b in books if b.strip()]
    
    def _parse_specialty_areas(self, row) -> List[str]:
        """Parse top 3 specialty areas."""
        specialties = []
        for i in range(1, 4):
            field = f'What are your top 3 practice focus areas?'
            if field in row and pd.notna(row[field]):
                specialties.append(self._clean_text(row[field]))
        return specialties
    
    def _parse_specialty_details(self, row) -> Dict:
        """Parse detailed explanations of specialty areas."""
        details = {}
        for i in range(1, 4):
            field = f'Can you tell us more about focus area #{i}?'
            if field in row and pd.notna(row[field]):
                details[f'focus_area_{i}'] = self._clean_text(row[field])
        return details
    
    def _parse_treatment_approaches(self, text: str) -> List[str]:
        """Parse treatment approaches from text."""
        if not text or pd.isna(text):
            return []
        
        # Split by semicolons
        approaches = re.split(r';', str(text))
        return [a.strip() for a in approaches if a.strip()]
    
    def _parse_expertise_areas(self, text: str) -> List[str]:
        """Parse expertise areas from text."""
        if not text or pd.isna(text):
            return []
        
        # Split by semicolons
        areas = re.split(r';', str(text))
        return [a.strip() for a in areas if a.strip()]
    
    def _parse_ocd_subtypes(self, text: str) -> List[str]:
        """Parse OCD subtypes from text."""
        if not text or pd.isna(text):
            return []
        
        # Split by semicolons
        subtypes = re.split(r';', str(text))
        return [s.strip() for s in subtypes if s.strip()]
    
    def _parse_years_experience(self, text: str) -> Optional[int]:
        """Parse years of experience from text."""
        if not text or pd.isna(text):
            return None
        
        # Extract number from text
        numbers = re.findall(r'\d+', str(text))
        return int(numbers[0]) if numbers else None
    
    def _update_therapist_form_data(self, therapist_id: int, form_data: Dict):
        """Update therapist with profile questions form data."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE therapists 
            SET personal_introduction = ?, therapeutic_approach = ?, client_expectations = ?,
                availability = ?, insurance_providers = ?, caqh_username = ?, caqh_password = ?,
                npi = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            form_data.get('personal_introduction', ''),
            form_data.get('therapeutic_approach', ''),
            form_data.get('client_expectations', ''),
            form_data.get('availability', ''),
            json.dumps(form_data.get('insurance_providers', [])),
            form_data.get('caqh_username', ''),
            form_data.get('caqh_password', ''),
            form_data.get('npi', ''),
            therapist_id
        ))
        
        conn.commit()
        conn.close()
    
    def _update_therapist_interview_data(self, therapist_id: int, interview_data: Dict):
        """Update therapist with interview form data."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE therapists 
            SET career_motivation = ?, guiding_principles = ?, target_population = ?,
                work_history = ?, work_rewards = ?, personal_interests = ?,
                book_recommendations = ?, specialty_areas = ?, specialty_details = ?,
                session_structure = ?, homework_approach = ?, progress_tracking = ?,
                treatment_duration = ?, preparation_guidance = ?, therapy_philosophy = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            interview_data.get('career_motivation', ''),
            interview_data.get('guiding_principles', ''),
            interview_data.get('target_population', ''),
            interview_data.get('work_history', ''),
            interview_data.get('work_rewards', ''),
            interview_data.get('personal_interests', ''),
            json.dumps(interview_data.get('book_recommendations', [])),
            json.dumps(interview_data.get('specialty_areas', [])),
            json.dumps(interview_data.get('specialty_details', {})),
            interview_data.get('session_structure', ''),
            interview_data.get('homework_approach', ''),
            interview_data.get('progress_tracking', ''),
            interview_data.get('treatment_duration', ''),
            interview_data.get('preparation_guidance', ''),
            interview_data.get('therapy_philosophy', ''),
            therapist_id
        ))
        
        conn.commit()
        conn.close()
    
    def _update_therapist_info_data(self, therapist_id: int, info_data: Dict):
        """Update therapist with info form data."""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE therapists 
            SET years_experience = ?, ideal_client = ?, treatment_modalities = ?,
                expertise_areas = ?, ocd_subtypes = ?, therapy_style = ?,
                client_feedback = ?, professional_message = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            info_data.get('years_experience'),
            info_data.get('ideal_client', ''),
            json.dumps(info_data.get('treatment_modalities', [])),
            json.dumps(info_data.get('expertise_areas', [])),
            json.dumps(info_data.get('ocd_subtypes', [])),
            info_data.get('therapy_style', ''),
            info_data.get('client_feedback', ''),
            info_data.get('professional_message', ''),
            therapist_id
        ))
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """Get database connection."""
        return self.db.get_connection()
