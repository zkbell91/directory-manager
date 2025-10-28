"""
CSV import functionality for Directory Manager application.
Handles importing existing spreadsheet data into the database.
"""

import pandas as pd
import json
from typing import List, Dict, Tuple
from database import DatabaseManager

class CSVImporter:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def import_directory_details(self, csv_path: str) -> Dict:
        """
        Import the Directory Details CSV file.
        Returns statistics about the import.
        """
        try:
            df = pd.read_csv(csv_path)
            
            # Clean up the data
            df = df.dropna(subset=['Therapist', 'Directory'])
            df = df[df['Therapist'] != '']
            df = df[df['Directory'] != '']
            
            stats = {
                'therapists_processed': 0,
                'profiles_created': 0,
                'directories_found': set(),
                'errors': []
            }
            
            current_therapist = None
            current_therapist_id = None
            
            for _, row in df.iterrows():
                therapist_name = str(row['Therapist']).strip()
                directory_name = str(row['Directory']).strip()
                
                # Skip empty rows or header rows
                if not therapist_name or therapist_name == 'nan':
                    continue
                
                # If this is a new therapist (not a continuation row)
                if pd.notna(row['Therapist']) and row['Therapist'] != '':
                    current_therapist = therapist_name
                    
                    # Check if therapist exists, if not create them
                    existing_therapists = self.db.get_all_therapists()
                    current_therapist_id = None
                    
                    for therapist in existing_therapists:
                        if therapist['name'] == current_therapist:
                            current_therapist_id = therapist['id']
                            break
                    
                    if current_therapist_id is None:
                        # Extract credentials from name if present
                        credentials = ""
                        if "LMHC" in current_therapist:
                            credentials = "LMHC"
                        elif "LMFC" in current_therapist:
                            credentials = "LMFC"
                        
                        current_therapist_id = self.db.add_therapist(
                            name=current_therapist,
                            credentials=credentials
                        )
                        stats['therapists_processed'] += 1
                
                # Process directory information
                if directory_name and directory_name != 'nan':
                    stats['directories_found'].add(directory_name)
                    
                    # Check if directory exists, if not create it
                    existing_directories = self.db.get_all_directories()
                    directory_id = None
                    
                    for directory in existing_directories:
                        if directory['name'] == directory_name:
                            directory_id = directory['id']
                            break
                    
                    if directory_id is None:
                        # Create directory with basic info
                        directory_id = self.db.add_directory(
                            name=directory_name,
                            base_url=self._get_base_url(directory_name)
                        )
                    
                    # Create or update therapist profile
                    if current_therapist_id:
                        profile_url = str(row['Directory URL']) if pd.notna(row['Directory URL']) else ""
                        username = str(row['Username']) if pd.notna(row['Username']) else ""
                        password = str(row['Password']) if pd.notna(row['Password']) else ""
                        notes = str(row['Notes']) if pd.notna(row['Notes']) else ""
                        
                        # Check if profile already exists
                        existing_profiles = self.db.get_therapist_profiles(
                            current_therapist_id, directory_id
                        )
                        
                        if not existing_profiles:
                            # Create new profile
                            self.db.add_therapist_profile(
                                therapist_id=current_therapist_id,
                                directory_id=directory_id,
                                profile_url=profile_url,
                                username=username,
                                password=password,
                                notes=notes
                            )
                            stats['profiles_created'] += 1
                        else:
                            # Update existing profile
                            profile = existing_profiles[0]
                            self.db.update_therapist_profile(
                                profile['id'],
                                profile_url=profile_url,
                                username=username,
                                password=password,
                                notes=notes
                            )
            
            stats['directories_found'] = list(stats['directories_found'])
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def import_directory_grid(self, csv_path: str) -> Dict:
        """
        Import the Directory Grid CSV file.
        This provides a different view of the same data.
        """
        try:
            df = pd.read_csv(csv_path)
            
            stats = {
                'therapists_processed': 0,
                'profiles_created': 0,
                'directories_found': set(),
                'errors': []
            }
            
            # Get directory names from first row (excluding first column)
            directory_names = [col for col in df.columns if col != 'Directory']
            
            for directory_name in directory_names:
                stats['directories_found'].add(directory_name)
                
                # Check if directory exists, if not create it
                existing_directories = self.db.get_all_directories()
                directory_id = None
                
                for directory in existing_directories:
                    if directory['name'] == directory_name:
                        directory_id = directory['id']
                        break
                
                if directory_id is None:
                    directory_id = self.db.add_directory(
                        name=directory_name,
                        base_url=self._get_base_url(directory_name)
                    )
                
                # Process each therapist for this directory
                for _, row in df.iterrows():
                    therapist_name = str(row[directory_name]) if pd.notna(row[directory_name]) else ""
                    
                    if therapist_name and therapist_name != 'nan' and therapist_name.startswith('http'):
                        # This is a URL, find the therapist name from the directory column
                        directory_row = str(row['Directory']) if pd.notna(row['Directory']) else ""
                        
                        if directory_row and directory_row != 'nan':
                            # Find or create therapist
                            existing_therapists = self.db.get_all_therapists()
                            therapist_id = None
                            
                            for therapist in existing_therapists:
                                if therapist['name'] == directory_row:
                                    therapist_id = therapist['id']
                                    break
                            
                            if therapist_id is None:
                                # Extract credentials from name if present
                                credentials = ""
                                if "LMHC" in directory_row:
                                    credentials = "LMHC"
                                elif "LMFC" in directory_row:
                                    credentials = "LMFC"
                                
                                therapist_id = self.db.add_therapist(
                                    name=directory_row,
                                    credentials=credentials
                                )
                                stats['therapists_processed'] += 1
                            
                            # Create or update profile
                            if therapist_id:
                                existing_profiles = self.db.get_therapist_profiles(
                                    therapist_id, directory_id
                                )
                                
                                if not existing_profiles:
                                    self.db.add_therapist_profile(
                                        therapist_id=therapist_id,
                                        directory_id=directory_id,
                                        profile_url=therapist_name
                                    )
                                    stats['profiles_created'] += 1
                                else:
                                    # Update existing profile with URL
                                    profile = existing_profiles[0]
                                    self.db.update_therapist_profile(
                                        profile['id'],
                                        profile_url=therapist_name
                                    )
            
            stats['directories_found'] = list(stats['directories_found'])
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_base_url(self, directory_name: str) -> str:
        """Get the base URL for a directory based on its name."""
        url_mapping = {
            'Psychology Today': 'https://www.psychologytoday.com',
            'Zencare': 'https://zencare.co',
            'TherapyDen': 'https://www.therapyden.com',
            'Headway': 'https://headway.co',
            'Open Path Collective': 'https://openpathcollective.org',
            'Therapy Route': 'https://www.therapyroute.com',
            'Share Care': 'https://www.sharecare.com',
            'ZocDoc': 'https://www.zocdoc.com',
            'Care Dash': 'https://www.caredash.com',
            'Health Grades': 'https://www.healthgrades.com',
            'eHealth Score': 'https://www.ehealthscores.com',
            'Health Line': 'https://www.healthline.com',
            'Bark': 'https://www.bark.com',
            'Alignable': 'https://www.alignable.com',
            'IOCDF': 'https://iocdf.org',
            'PSI Directory': 'https://psidirectory.com',
            'Trauma Therapist Network': 'https://traumatherapistnetwork.com',
            'Being Seen': 'https://beingseen.org',
            'Jax Therapy Network': 'https://jaxtherapynetwork.com'
        }
        
        return url_mapping.get(directory_name, '')
    
    def export_to_csv(self, output_path: str, format_type: str = 'details') -> bool:
        """
        Export current database data back to CSV format.
        format_type can be 'details' or 'grid'
        """
        try:
            if format_type == 'details':
                self._export_details_format(output_path)
            else:
                self._export_grid_format(output_path)
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    def _export_details_format(self, output_path: str):
        """Export in the Directory Details format."""
        therapists = self.db.get_all_therapists()
        directories = self.db.get_all_directories()
        
        rows = []
        for therapist in therapists:
            # Add therapist header row
            rows.append({
                'Therapist': therapist['name'],
                'Directory': '',
                'Directory URL': '',
                'Username': '',
                'Password': '',
                'Notes': ''
            })
            
            # Add profile rows for each directory
            for directory in directories:
                profiles = self.db.get_therapist_profiles(therapist['id'], directory['id'])
                
                if profiles:
                    profile = profiles[0]
                    rows.append({
                        'Therapist': '',
                        'Directory': directory['name'],
                        'Directory URL': profile['profile_url'],
                        'Username': profile['username'],
                        'Password': profile['password'],
                        'Notes': profile['notes']
                    })
                else:
                    rows.append({
                        'Therapist': '',
                        'Directory': directory['name'],
                        'Directory URL': '',
                        'Username': '',
                        'Password': '',
                        'Notes': ''
                    })
        
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False)
    
    def _export_grid_format(self, output_path: str):
        """Export in the Directory Grid format."""
        therapists = self.db.get_all_therapists()
        directories = self.db.get_all_directories()
        
        # Create grid data
        grid_data = []
        for directory in directories:
            row = {'Directory': directory['name']}
            
            for therapist in therapists:
                profiles = self.db.get_therapist_profiles(therapist['id'], directory['id'])
                if profiles and profiles[0]['profile_url']:
                    row[therapist['name']] = profiles[0]['profile_url']
                else:
                    row[therapist['name']] = ''
            
            grid_data.append(row)
        
        df = pd.DataFrame(grid_data)
        df.to_csv(output_path, index=False)

if __name__ == "__main__":
    # Test the importer
    db = DatabaseManager()
    importer = CSVImporter(db)
    
    # Import the provided CSV files
    details_stats = importer.import_directory_details('/Users/zack/Downloads/Directory List/Directory Details-Table 1.csv')
    print("Details import stats:", details_stats)
    
    grid_stats = importer.import_directory_grid('/Users/zack/Downloads/Directory List/Directory Grid-Directory Grid.csv')
    print("Grid import stats:", grid_stats)
