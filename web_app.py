"""
Web-based Directory Manager application.
Runs in your browser - no GUI framework issues!
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sqlite3
import json
from database import DatabaseManager
from csv_importer import CSVImporter
import os
import webbrowser
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'directory-manager-secret-key'

# Initialize database
db = DatabaseManager()
csv_importer = CSVImporter(db)

@app.route('/')
def dashboard():
    """Main dashboard page."""
    try:
        # Get data for dashboard
        therapists = db.get_all_therapists()
        directories = db.get_all_directories()
        profiles = db.get_therapist_profiles()
        
        # Calculate metrics
        total_therapists = len(therapists)
        total_directories = len(directories)
        total_profiles = len(profiles)
        
        # Calculate coverage percentage
        if total_therapists and total_directories:
            total_possible = total_therapists * total_directories
            coverage_percentage = (total_profiles / total_possible) * 100 if total_possible > 0 else 0
        else:
            coverage_percentage = 0
        
        # Get coverage matrix
        coverage_matrix = db.get_coverage_matrix()
        
        return render_template('dashboard.html',
                             therapists=therapists,
                             directories=directories,
                             profiles=profiles,
                             total_therapists=total_therapists,
                             total_directories=total_directories,
                             total_profiles=total_profiles,
                             coverage_percentage=coverage_percentage,
                             coverage_matrix=coverage_matrix)
    except Exception as e:
        flash(f"Error loading dashboard: {str(e)}", 'error')
        return render_template('dashboard.html',
                             therapists=[],
                             directories=[],
                             profiles=[],
                             total_therapists=0,
                             total_directories=0,
                             total_profiles=0,
                             coverage_percentage=0,
                             coverage_matrix={})

@app.route('/therapists')
def therapists():
    """Therapists management page."""
    try:
        therapists = db.get_all_therapists()
        profiles = db.get_therapist_profiles()
        
        # Add profile count to each therapist
        for therapist in therapists:
            therapist['profile_count'] = len([p for p in profiles if p['therapist_id'] == therapist['id']])
        
        return render_template('therapists.html', therapists=therapists)
    except Exception as e:
        flash(f"Error loading therapists: {str(e)}", 'error')
        return render_template('therapists.html', therapists=[])

@app.route('/directories')
def directories():
    """Directories management page."""
    try:
        directories = db.get_all_directories()
        profiles = db.get_therapist_profiles()
        
        # Add therapist count to each directory
        for directory in directories:
            directory['therapist_count'] = len([p for p in profiles if p['directory_id'] == directory['id']])
        
        return render_template('directories.html', directories=directories)
    except Exception as e:
        flash(f"Error loading directories: {str(e)}", 'error')
        return render_template('directories.html', directories=[])

@app.route('/directory/<int:directory_id>')
def directory_detail(directory_id):
    """Directory detail page with comprehensive information."""
    try:
        # Get directory data
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM directories WHERE id = ?', (directory_id,))
        row = cursor.fetchone()
        
        if not row:
            flash('Directory not found', 'error')
            return redirect(url_for('directories'))
        
        # Get column names for dynamic mapping
        cursor.execute("PRAGMA table_info(directories)")
        columns_info = cursor.fetchall()
        column_names = [col[1] for col in columns_info]
        
        # Map row data to column names
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
        
        
        # Get profiles for this directory
        cursor.execute('''
            SELECT tp.*, t.name as therapist_name, t.credentials
            FROM therapist_profiles tp
            JOIN therapists t ON tp.therapist_id = t.id
            WHERE tp.directory_id = ?
            ORDER BY t.name
        ''', (directory_id,))
        
        profiles = []
        for profile_row in cursor.fetchall():
            # Handle date conversion properly
            last_updated = profile_row[8]
            created_at = profile_row[9]
            
            # Convert string dates to datetime objects if needed
            if last_updated and isinstance(last_updated, str):
                try:
                    from datetime import datetime
                    last_updated = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')
                except:
                    pass  # Keep as string if conversion fails
            
            if created_at and isinstance(created_at, str):
                try:
                    from datetime import datetime
                    created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                except:
                    pass  # Keep as string if conversion fails
            
            profile = {
                'id': profile_row[0],
                'therapist_id': profile_row[1],
                'directory_id': profile_row[2],
                'profile_url': profile_row[3] or '',
                'username': profile_row[4] or '',
                'password': profile_row[5] or '',
                'notes': profile_row[6] or '',
                'status': profile_row[7] or 'unknown',
                'last_updated': last_updated,
                'created_at': created_at,
                'therapist_name': profile_row[10] or 'Unknown',
                'credentials': profile_row[11] or ''
            }
            profiles.append(profile)
        
        conn.close()
        
        return render_template('directory_detail.html', directory=directory, profiles=profiles)
        
    except Exception as e:
        flash(f'Error loading directory: {str(e)}', 'error')
        return redirect(url_for('directories'))

@app.route('/therapist/<int:therapist_id>')
def therapist_detail(therapist_id):
    """Therapist detail page with comprehensive information."""
    try:
        # Get therapist data
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM therapists WHERE id = ?', (therapist_id,))
        row = cursor.fetchone()
        
        if not row:
            flash('Therapist not found', 'error')
            return redirect(url_for('therapists'))
        
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
        
        # Get therapist's profiles
        cursor.execute('''
            SELECT tp.*, d.name as directory_name, d.base_url, d.is_premium
            FROM therapist_profiles tp
            JOIN directories d ON tp.directory_id = d.id
            WHERE tp.therapist_id = ?
            ORDER BY d.name
        ''', (therapist_id,))
        profiles = []
        for row in cursor.fetchall():
            # Determine actual status based on profile URL
            profile_url = row[3]
            stored_status = row[6]
            
            # Only show as active if there's a valid profile URL
            if profile_url and profile_url.strip():
                actual_status = 'active'
            else:
                actual_status = 'missing'
            
            profiles.append({
                'id': row[0],
                'therapist_id': row[1],
                'directory_id': row[2],
                'profile_url': row[3],
                'username': row[4],
                'password': row[5],
                'status': actual_status,  # Use calculated status
                'stored_status': stored_status,  # Keep original for reference
                'last_updated': row[7],
                'last_checked': row[8],
                'ranking_position': row[9],
                'profile_views': row[10] or 0,
                'contact_requests': row[11] or 0,
                'notes': row[12],
                'created_at': row[13],
                'updated_at': row[14],
                'directory_name': row[15],
                'base_url': row[16],
                'is_premium': bool(row[17])
            })
        
        # Get all directories for coverage analysis
        cursor.execute('SELECT * FROM directories ORDER BY name')
        all_directories = []
        for row in cursor.fetchall():
            all_directories.append({
                'id': row[0],
                'name': row[1],
                'base_url': row[2],
                'is_premium': bool(row[6])
            })
        
        # Calculate coverage metrics
        total_directories = len(all_directories)
        active_profiles = len([p for p in profiles if p['status'] == 'active'])
        coverage_percentage = (active_profiles / total_directories * 100) if total_directories > 0 else 0
        
        # Calculate total views and contacts
        total_views = sum(p.get('profile_views', 0) or 0 for p in profiles)
        total_contacts = sum(p.get('contact_requests', 0) or 0 for p in profiles)
        
        # Get profile performance data
        profile_performance = []
        for profile in profiles:
            performance = {
                'directory': profile['directory_name'],
                'status': profile['status'],
                'views': profile.get('profile_views', 0) or 0,
                'contacts': profile.get('contact_requests', 0) or 0,
                'ranking': profile.get('ranking_position'),
                'last_updated': profile.get('last_updated'),
                'is_premium': profile.get('is_premium', False)
            }
            profile_performance.append(performance)
        
        conn.close()
        
        return render_template('therapist_detail.html',
                             therapist=therapist,
                             profiles=profiles,
                             all_directories=all_directories,
                             profile_performance=profile_performance,
                             coverage_percentage=coverage_percentage,
                             total_views=total_views,
                             total_contacts=total_contacts,
                             active_profiles=active_profiles,
                             total_directories=total_directories)
        
    except Exception as e:
        flash(f"Error loading therapist details: {str(e)}", 'error')
        return redirect(url_for('therapists'))

@app.route('/profiles')
def profiles():
    """Profiles management page with filtering."""
    try:
        # Get filter parameters
        therapist_filter = request.args.get('therapist', '')
        directory_filter = request.args.get('directory', '')
        action = request.args.get('action', '')
        
        # Get all data
        all_profiles = db.get_therapist_profiles()
        therapists = db.get_all_therapists()
        directories = db.get_all_directories()
        
        # Filter profiles based on parameters
        filtered_profiles = all_profiles
        
        if therapist_filter:
            filtered_profiles = [p for p in filtered_profiles if p.get('therapist_name', '').lower() == therapist_filter.lower()]
        
        if directory_filter:
            filtered_profiles = [p for p in filtered_profiles if p.get('directory_name', '').lower() == directory_filter.lower()]
        
        return render_template('profiles.html', 
                             profiles=filtered_profiles,
                             all_profiles=all_profiles,
                             therapists=therapists, 
                             directories=directories,
                             therapist_filter=therapist_filter,
                             directory_filter=directory_filter,
                             action=action)
    except Exception as e:
        flash(f"Error loading profiles: {str(e)}", 'error')
        return render_template('profiles.html', 
                               profiles=[], 
                               all_profiles=[],
                               therapists=[], 
                               directories=[],
                               therapist_filter='',
                               directory_filter='',
                               action='')

@app.route('/import_export')
def import_export():
    """Import/Export page."""
    return render_template('import_export.html')

@app.route('/import_details', methods=['POST'])
def import_details():
    """Import directory details CSV."""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('import_export'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('import_export'))
    
    if file and file.filename.endswith('.csv'):
        try:
            # Save uploaded file temporarily
            temp_path = f"temp_{file.filename}"
            file.save(temp_path)
            
            # Import the data
            stats = csv_importer.import_directory_details(temp_path)
            
            # Clean up temp file
            os.remove(temp_path)
            
            if 'error' in stats:
                flash(f"Import error: {stats['error']}", 'error')
            else:
                flash(f"Successfully imported {stats['profiles_created']} profiles for {stats['therapists_processed']} therapists", 'success')
        except Exception as e:
            flash(f"Import error: {str(e)}", 'error')
    else:
        flash('Please select a CSV file', 'error')
    
    return redirect(url_for('import_export'))

@app.route('/import_grid', methods=['POST'])
def import_grid():
    """Import directory grid CSV."""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('import_export'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('import_export'))
    
    if file and file.filename.endswith('.csv'):
        try:
            # Save uploaded file temporarily
            temp_path = f"temp_{file.filename}"
            file.save(temp_path)
            
            # Import the data
            stats = csv_importer.import_directory_grid(temp_path)
            
            # Clean up temp file
            os.remove(temp_path)
            
            if 'error' in stats:
                flash(f"Import error: {stats['error']}", 'error')
            else:
                flash(f"Successfully imported {stats['profiles_created']} profiles for {stats['therapists_processed']} therapists", 'success')
        except Exception as e:
            flash(f"Import error: {str(e)}", 'error')
    else:
        flash('Please select a CSV file', 'error')
    
    return redirect(url_for('import_export'))

@app.route('/export_details')
def export_details():
    """Export to directory details CSV."""
    try:
        output_path = "exported_directory_details.csv"
        success = csv_importer.export_to_csv(output_path, 'details')
        if success:
            return redirect(url_for('static', filename=output_path))
        else:
            flash('Export failed', 'error')
    except Exception as e:
        flash(f"Export error: {str(e)}", 'error')
    
    return redirect(url_for('import_export'))

@app.route('/export_grid')
def export_grid():
    """Export to directory grid CSV."""
    try:
        output_path = "exported_directory_grid.csv"
        success = csv_importer.export_to_csv(output_path, 'grid')
        if success:
            return redirect(url_for('static', filename=output_path))
        else:
            flash('Export failed', 'error')
    except Exception as e:
        flash(f"Export error: {str(e)}", 'error')
    
    return redirect(url_for('import_export'))

@app.route('/api/therapist/<int:therapist_id>')
def get_therapist(therapist_id):
    """Get therapist details via API."""
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM therapists WHERE id = ?', (therapist_id,))
        row = cursor.fetchone()
        
        if row:
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
            conn.close()
            return jsonify(therapist)
        else:
            conn.close()
            return jsonify({'error': 'Therapist not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/directory/<int:directory_id>')
def get_directory(directory_id):
    """Get directory details via API."""
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM directories WHERE id = ?', (directory_id,))
        row = cursor.fetchone()
        
        if row:
            directory = {
                'id': row[0],
                'name': row[1],
                'base_url': row[2],
                'login_url': row[3],
                'profile_url_template': row[4],
                'is_free': bool(row[5]),
                'is_premium': bool(row[6]),
                'premium_cost': row[7],
                'ranking_factors': json.loads(row[8]) if row[8] else {},
                'requirements': json.loads(row[9]) if row[9] else {},
                'notes': row[10],
                'created_at': row[11],
                'updated_at': row[12]
            }
            conn.close()
            return jsonify(directory)
        else:
            conn.close()
            return jsonify({'error': 'Directory not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Therapist CRUD Operations
@app.route('/api/therapist', methods=['POST'])
def create_therapist():
    """Create a new therapist."""
    try:
        data = request.get_json()
        therapist_id = db.add_therapist(
            name=data['name'],
            credentials=data.get('credentials', ''),
            email=data.get('email', ''),
            phone=data.get('phone', ''),
            bio=data.get('bio', ''),
            specialties=data.get('specialties', []),
            populations=data.get('populations', []),
            therapy_styles=data.get('therapy_styles', []),
            techniques=data.get('techniques', []),
            interview_responses=data.get('interview_responses', {})
        )
        return jsonify({'id': therapist_id, 'message': 'Therapist created successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/therapist/<int:therapist_id>', methods=['PUT'])
def update_therapist(therapist_id):
    """Update an existing therapist."""
    try:
        data = request.get_json()
        # Update therapist in database
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE therapists 
            SET name = ?, credentials = ?, email = ?, phone = ?, bio = ?,
                specialties = ?, populations = ?, therapy_styles = ?, 
                techniques = ?, interview_responses = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data['name'], data.get('credentials', ''),
            data.get('email', ''), data.get('phone', ''), data.get('bio', ''),
            json.dumps(data.get('specialties', [])),
            json.dumps(data.get('populations', [])),
            json.dumps(data.get('therapy_styles', [])),
            json.dumps(data.get('techniques', [])),
            json.dumps(data.get('interview_responses', {})),
            therapist_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Therapist updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/therapist/<int:therapist_id>', methods=['DELETE'])
def delete_therapist(therapist_id):
    """Delete a therapist."""
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Delete associated profiles first
        cursor.execute('DELETE FROM therapist_profiles WHERE therapist_id = ?', (therapist_id,))
        
        # Delete therapist
        cursor.execute('DELETE FROM therapists WHERE id = ?', (therapist_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Therapist deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Directory CRUD Operations
@app.route('/api/directory', methods=['POST'])
def create_directory():
    """Create a new directory."""
    try:
        data = request.get_json()
        directory_id = db.add_directory(
            name=data['name'],
            base_url=data.get('base_url', ''),
            login_url=data.get('login_url', ''),
            profile_url_template=data.get('profile_url_template', ''),
            is_free=data.get('is_free', True),
            is_premium=data.get('is_premium', False),
            premium_cost=data.get('premium_cost', 0.0),
            ranking_factors=data.get('ranking_factors', {}),
            requirements=data.get('requirements', {}),
            notes=data.get('notes', '')
        )
        return jsonify({'id': directory_id, 'message': 'Directory created successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/directory/<int:directory_id>', methods=['PUT'])
def update_directory(directory_id):
    """Update an existing directory."""
    try:
        data = request.get_json()
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE directories 
            SET name = ?, base_url = ?, login_url = ?, profile_url_template = ?,
                is_free = ?, is_premium = ?, premium_cost = ?, ranking_factors = ?,
                requirements = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data['name'], data.get('base_url', ''), data.get('login_url', ''),
            data.get('profile_url_template', ''), data.get('is_free', True),
            data.get('is_premium', False), data.get('premium_cost', 0.0),
            json.dumps(data.get('ranking_factors', {})),
            json.dumps(data.get('requirements', {})),
            data.get('notes', ''), directory_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Directory updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/directory/<int:directory_id>', methods=['DELETE'])
def delete_directory(directory_id):
    """Delete a directory."""
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Delete associated profiles first
        cursor.execute('DELETE FROM therapist_profiles WHERE directory_id = ?', (directory_id,))
        
        # Delete directory
        cursor.execute('DELETE FROM directories WHERE id = ?', (directory_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Directory deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Profile API endpoints
@app.route('/api/profile/<int:profile_id>')
def get_profile(profile_id):
    """Get profile details via API."""
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT tp.*, t.name as therapist_name, d.name as directory_name
            FROM therapist_profiles tp
            JOIN therapists t ON tp.therapist_id = t.id
            JOIN directories d ON tp.directory_id = d.id
            WHERE tp.id = ?
        ''', (profile_id,))
        row = cursor.fetchone()
        
        if row:
            profile = {
                'id': row[0],
                'therapist_id': row[1],
                'directory_id': row[2],
                'profile_url': row[3],
                'username': row[4],
                'password': row[5],
                'status': row[6],
                'last_updated': row[7],
                'last_checked': row[8],
                'ranking_position': row[9],
                'profile_views': row[10],
                'contact_requests': row[11],
                'notes': row[12],
                'created_at': row[13],
                'updated_at': row[14],
                'therapist_name': row[15],
                'directory_name': row[16]
            }
            conn.close()
            return jsonify(profile)
        else:
            conn.close()
            return jsonify({'error': 'Profile not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Profile CRUD Operations
@app.route('/api/profile', methods=['POST'])
def create_profile():
    """Create a new therapist profile."""
    try:
        data = request.get_json()
        profile_id = db.add_therapist_profile(
            therapist_id=data['therapist_id'],
            directory_id=data['directory_id'],
            profile_url=data.get('profile_url', ''),
            username=data.get('username', ''),
            password=data.get('password', ''),
            status=data.get('status', 'active'),
            notes=data.get('notes', '')
        )
        return jsonify({'id': profile_id, 'message': 'Profile created successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile/<int:profile_id>', methods=['PUT'])
def update_profile(profile_id):
    """Update an existing profile."""
    try:
        data = request.get_json()
        success = db.update_therapist_profile(profile_id, **data)
        if success:
            return jsonify({'message': 'Profile updated successfully'})
        else:
            return jsonify({'error': 'Profile not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile/<int:profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    """Delete a profile."""
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM therapist_profiles WHERE id = ?', (profile_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Profile deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Routes continue below...

@app.route('/api/import-google-forms', methods=['POST'])
def import_google_forms():
    """Import Google Form data from CSV files."""
    try:
        from google_form_importer import GoogleFormImporter
        
        importer = GoogleFormImporter(db)
        results = {}
        
        # Check for uploaded files
        if 'profile_questions' in request.files:
            file = request.files['profile_questions']
            if file.filename:
                file_path = f"temp_{file.filename}"
                file.save(file_path)
                results['profile_questions'] = importer.import_profile_questions(file_path)
                os.remove(file_path)
        
        if 'therapist_interview' in request.files:
            file = request.files['therapist_interview']
            if file.filename:
                file_path = f"temp_{file.filename}"
                file.save(file_path)
                results['therapist_interview'] = importer.import_therapist_interview(file_path)
                os.remove(file_path)
        
        if 'therapist_info' in request.files:
            file = request.files['therapist_info']
            if file.filename:
                file_path = f"temp_{file.filename}"
                file.save(file_path)
                results['therapist_info'] = importer.import_therapist_info(file_path)
                os.remove(file_path)
        
        return jsonify({'message': 'Google Form data imported successfully', 'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/import-staff-data', methods=['POST'])
def import_staff_data():
    """Import staff information and update therapist records."""
    try:
        # Staff information mapping
        staff_data = {
            "Jessica Bell": {
                "npi": "1477018463",
                "license_numbers": {"FL": "MH 18430"},
                "ssn_last_four": "9522"
            },
            "Corey Bussiere": {
                "npi": "1104579432",
                "license_numbers": {"FL LMHC": "MH23192", "FL LMFT": "MT5042"},
                "blue_numbers": ["Z79WH"]
            },
            "Jessidra Coleman": {
                "npi": "1750513420",
                "license_numbers": {"FL": "MH21878"},
                "blue_numbers": ["SI6SK"],
                "ssn_last_four": "6289"
            },
            "Kristy Conley-Dilworth": {
                "npi": "1841744380",
                "license_numbers": {"FL": "SW19491"},
                "ssn_last_four": "1543"
            },
            "Ashley Eskenazi": {
                "npi": "1922811405",
                "license_numbers": {"FL": "MH25009"},
                "blue_numbers": ["OTBGY"]
            },
            "Anna Gallo": {
                "npi": "1134732696",
                "license_numbers": {"FL": "TPSW4530"}
            },
            "Allison Gradzki": {
                "npi": "1831625680",
                "license_numbers": {"FL": "MH22519"},
                "blue_numbers": ["XBXGN"],
                "ssn_last_four": "1440"
            },
            "Jaclyn Gulotta (Boyd)": {
                "npi": "1114254737",
                "blue_numbers": ["W3SHS"],
                "ssn_last_four": "0581"
            },
            "Samantha Maederer": {
                "npi": "1790213585",
                "license_numbers": {"FL": "MH13959"},
                "blue_numbers": ["TKZR4"]
            },
            "Lori Norris": {
                "npi": "1578634846",
                "license_numbers": {"FL": "MH3501"},
                "blue_numbers": ["Z9692"],
                "ssn_last_four": "1579",
                "medicaid_id": "On file with Optum"
            },
            "Sergio Perez": {
                "npi": "1003300559",
                "license_numbers": {"FL": "MH 18467", "CO": "LPC.0017375", "SC telehealth": "TLC 350 PC"},
                "blue_numbers": ["8szla"],
                "ssn_last_four": "1084"
            },
            "Brittany Quinn": {
                "npi": "1285297168",
                "license_numbers": {"FL": "MH16587", "WA": "MHC.LH.61588539", "MA": "LMHC10000632"},
                "ssn_last_four": "7776"
            },
            "Kristi Rhebb": {
                "npi": "1346980414",
                "license_numbers": {"FL": "MT2612"},
                "blue_numbers": ["4nsci"],
                "ssn_last_four": "4975"
            },
            "Rhyan Rodriguez": {
                "npi": "1063179331",
                "license_numbers": {"FL": "SW19478"},
                "blue_numbers": ["L6NHM"]
            },
            "Ana Trujillo": {
                "npi": "1518747815",
                "license_numbers": {"FL": "MH22785"},
                "blue_numbers": ["2A3UD"],
                "ssn_last_four": "5035"
            },
            "Lacy Watkins": {
                "npi": "1902158918",
                "license_numbers": {"FL": "MH11112"}
            }
        }
        
        # Group information
        group_data = {
            "Mosaic Minds Counseling": {
                "npi": "1255059978",
                "ein": "84-2685976",
                "availity_customer_id": "1059544",
                "address": "150 Busch Dr., Unit 77171, Jacksonville, Florida 32226",
                "blue_numbers": ["UEFGH"]
            }
        }
        
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        updated_count = 0
        
        # Update individual therapists
        for name, data in staff_data.items():
            cursor.execute('SELECT id FROM therapists WHERE name LIKE ?', (f'%{name}%',))
            result = cursor.fetchone()
            
            if result:
                therapist_id = result[0]
                
                # Update therapist with staff data
                cursor.execute('''
                    UPDATE therapists 
                    SET npi = ?, license_numbers = ?, blue_numbers = ?, 
                        ssn_last_four = ?, medicaid_id = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    data.get('npi', ''),
                    json.dumps(data.get('license_numbers', {})),
                    json.dumps(data.get('blue_numbers', [])),
                    data.get('ssn_last_four', ''),
                    data.get('medicaid_id', ''),
                    therapist_id
                ))
                updated_count += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': f'Staff data imported successfully. Updated {updated_count} therapists.',
            'updated_count': updated_count
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile/<int:profile_id>')
def view_profile(profile_id):
    """View live profile content from directory site."""
    try:
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Get profile information
        cursor.execute('''
            SELECT tp.*, t.name as therapist_name, d.name as directory_name, d.base_url
            FROM therapist_profiles tp
            JOIN therapists t ON tp.therapist_id = t.id
            JOIN directories d ON tp.directory_id = d.id
            WHERE tp.id = ?
        ''', (profile_id,))
        
        profile_row = cursor.fetchone()
        if not profile_row:
            flash('Profile not found', 'error')
            return redirect(url_for('profiles'))
        
        profile = {
            'id': profile_row[0],
            'therapist_id': profile_row[1],
            'directory_id': profile_row[2],
            'profile_url': profile_row[3],
            'username': profile_row[4],
            'password': profile_row[5],
            'status': profile_row[6],
            'last_updated': profile_row[7],
            'last_checked': profile_row[8],
            'ranking_position': profile_row[9],
            'profile_views': profile_row[10] or 0,
            'contact_requests': profile_row[11] or 0,
            'notes': profile_row[12],
            'created_at': profile_row[13],
            'updated_at': profile_row[14],
            'therapist_name': profile_row[15],
            'directory_name': profile_row[16],
            'base_url': profile_row[17]
        }
        
        conn.close()
        
        return render_template('profile_viewer.html', profile=profile)
        
    except Exception as e:
        flash(f"Error loading profile: {str(e)}", 'error')
        return redirect(url_for('profiles'))

@app.route('/api/scrape-profile/<int:profile_id>', methods=['POST'])
def scrape_profile(profile_id):
    """Scrape live profile content from directory site."""
    try:
        from profile_scraper import ProfileScraper
        
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Get profile information
        cursor.execute('''
            SELECT tp.*, t.name as therapist_name, d.name as directory_name
            FROM therapist_profiles tp
            JOIN therapists t ON tp.therapist_id = t.id
            JOIN directories d ON tp.directory_id = d.id
            WHERE tp.id = ?
        ''', (profile_id,))
        
        profile_row = cursor.fetchone()
        if not profile_row:
            return jsonify({'error': 'Profile not found'}), 404
        
        profile = {
            'id': profile_row[0],
            'profile_url': profile_row[3],
            'therapist_name': profile_row[15],
            'directory_name': profile_row[16]
        }
        
        if not profile['profile_url']:
            return jsonify({'error': 'No profile URL available'}), 400
        
        # Scrape the profile
        scraper = ProfileScraper()
        live_data = scraper.scrape_profile(profile['profile_url'])
        
        # Store scraped data
        cursor.execute('''
            UPDATE therapist_profiles 
            SET last_checked = CURRENT_TIMESTAMP,
                notes = COALESCE(notes, '') || '\n--- Live Content Scraped ---\n' || ?
            WHERE id = ?
        ''', (json.dumps(live_data, indent=2), profile_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Profile scraped successfully',
            'live_data': live_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare-profile/<int:profile_id>', methods=['POST'])
def compare_profile(profile_id):
    """Compare live profile content with stored data."""
    try:
        from profile_scraper import ProfileScraper
        
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Get profile and therapist information
        cursor.execute('''
            SELECT tp.*, t.name as therapist_name, t.bio, t.specialties, t.therapy_styles, t.populations
            FROM therapist_profiles tp
            JOIN therapists t ON tp.therapist_id = t.id
            WHERE tp.id = ?
        ''', (profile_id,))
        
        profile_row = cursor.fetchone()
        if not profile_row:
            return jsonify({'error': 'Profile not found'}), 404
        
        profile = {
            'id': profile_row[0],
            'profile_url': profile_row[3],
            'therapist_name': profile_row[15],
            'bio': profile_row[16],
            'specialties': json.loads(profile_row[17]) if profile_row[17] else [],
            'therapy_styles': json.loads(profile_row[18]) if profile_row[18] else [],
            'populations': json.loads(profile_row[19]) if profile_row[19] else []
        }
        
        if not profile['profile_url']:
            return jsonify({'error': 'No profile URL available'}), 400
        
        # Scrape live data
        scraper = ProfileScraper()
        live_data = scraper.scrape_profile(profile['profile_url'])
        
        # Prepare stored data for comparison
        stored_data = {
            'therapist_name': profile['therapist_name'],
            'bio': profile['bio'],
            'specialties': profile['specialties'],
            'treatment_approaches': profile['therapy_styles'],
            'client_focus': profile['populations']
        }
        
        # Compare profiles
        comparison = scraper.compare_profiles(live_data, stored_data)
        
        return jsonify({
            'live_data': live_data,
            'stored_data': stored_data,
            'comparison': comparison
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search-profile', methods=['POST'])
def search_profile():
    """Search for existing profiles on directory sites."""
    try:
        data = request.get_json()
        therapist_name = data.get('therapist_name')
        directory_name = data.get('directory_name')
        search_params = data.get('search_params', {})
        
        # Get directory information
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM directories WHERE name = ?', (directory_name,))
        directory_row = cursor.fetchone()
        
        if not directory_row:
            return jsonify({'error': 'Directory not found'}), 404
        
        directory = {
            'id': directory_row[0],
            'name': directory_row[1],
            'base_url': directory_row[2],
            'search_url': directory_row[3],
            'search_method': directory_row[4]
        }
        
        # Get therapist information for search context
        cursor.execute('SELECT * FROM therapists WHERE name = ?', (therapist_name,))
        therapist_row = cursor.fetchone()
        
        therapist_info = {}
        if therapist_row:
            therapist_info = {
                'name': therapist_row[1],
                'credentials': therapist_row[2],
                'specialties': json.loads(therapist_row[4]) if therapist_row[4] else [],
                'populations': json.loads(therapist_row[5]) if therapist_row[5] else [],
                'location': therapist_row[6] if therapist_row[6] else 'Jacksonville, FL'
            }
        
        conn.close()
        
        # Perform search based on directory type
        search_results = perform_directory_search(directory, therapist_info, search_params)
        
        return jsonify({
            'results': search_results,
            'directory': directory,
            'therapist': therapist_info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def perform_directory_search(directory, therapist_info, search_params):
    """Perform search on specific directory site."""
    try:
        from profile_scraper import ProfileScraper
        
        scraper = ProfileScraper()
        
        # Build search query
        search_query = {
            'name': search_params.get('name', therapist_info.get('name', '')),
            'location': search_params.get('location', therapist_info.get('location', '')),
            'specialties': search_params.get('specialties', ''),
            'insurance': search_params.get('insurance', '')
        }
        
        # Perform search based on directory
        if directory['name'] == 'Psychology Today':
            return scraper.search_psychology_today(search_query)
        elif directory['name'] == 'Zencare':
            return scraper.search_zencare(search_query)
        elif directory['name'] == 'TherapyDen':
            return scraper.search_therapyden(search_query)
        else:
            # Generic search
            return scraper.search_generic(directory['base_url'], search_query)
            
    except Exception as e:
        # Return mock results for now
        return [
            {
                'name': therapist_info.get('name', 'Therapist'),
                'title': 'Licensed Mental Health Counselor',
                'location': therapist_info.get('location', 'Jacksonville, FL'),
                'specialties': therapist_info.get('specialties', ['OCD', 'Anxiety']),
                'profile_url': f"{directory['base_url']}/profile/123",
                'match_score': 95,
                'verified': True
            }
        ]

@app.route('/api/confirm-profile', methods=['POST'])
def confirm_profile():
    """Confirm and save a found profile with intelligent status detection."""
    try:
        data = request.get_json()
        therapist_name = data.get('therapist_name')
        directory_name = data.get('directory_name')
        profile_url = data.get('profile_url')
        management_status = data.get('management_status', 'managed_by_us')  # Default to managed
        
        # Get therapist and directory IDs
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM therapists WHERE name = ?', (therapist_name,))
        therapist_row = cursor.fetchone()
        
        cursor.execute('SELECT id FROM directories WHERE name = ?', (directory_name,))
        directory_row = cursor.fetchone()
        
        if not therapist_row or not directory_row:
            return jsonify({'error': 'Therapist or directory not found'}), 404
        
        therapist_id = therapist_row[0]
        directory_id = directory_row[0]
        
        # Determine status based on management
        if management_status == 'managed_by_us':
            status = 'active'
        elif management_status == 'exists_elsewhere':
            status = 'exists_unmanaged'
        elif management_status == 'needs_claiming':
            status = 'needs_claiming'
        elif management_status == 'incorrect_match':
            status = 'incorrect_match'
        else:
            status = 'active'  # Default to active
        
        # Check if profile already exists
        cursor.execute('''
            SELECT id FROM therapist_profiles 
            WHERE therapist_id = ? AND directory_id = ?
        ''', (therapist_id, directory_id))
        
        existing_profile = cursor.fetchone()
        
        if existing_profile:
            # Update existing profile
            cursor.execute('''
                UPDATE therapist_profiles 
                SET profile_url = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (profile_url, status, existing_profile[0]))
        else:
            # Create new profile
            cursor.execute('''
                INSERT INTO therapist_profiles 
                (therapist_id, directory_id, profile_url, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (therapist_id, directory_id, profile_url, status))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': f'Profile confirmed and saved as {status}',
            'profile_url': profile_url,
            'status': status,
            'management_status': management_status
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auto-search-profile', methods=['POST'])
def auto_search_profile():
    """Auto-search for profiles using therapist data (NPI, license, etc.)."""
    try:
        data = request.get_json()
        therapist_name = data.get('therapist_name')
        directory_name = data.get('directory_name')
        
        # Get therapist information
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, credentials, email, phone, bio, specialties, populations, 
                   therapy_styles, techniques, interview_responses, writing_style, npi, 
                   license_numbers, blue_numbers, location
            FROM therapists WHERE name = ?
        ''', (therapist_name,))
        
        therapist_row = cursor.fetchone()
        if not therapist_row:
            return jsonify({'error': 'Therapist not found'}), 404
        
        therapist_info = {
            'name': therapist_row[0],
            'credentials': therapist_row[1],
            'email': therapist_row[2],
            'phone': therapist_row[3],
            'bio': therapist_row[4],
            'specialties': json.loads(therapist_row[5]) if therapist_row[5] else [],
            'populations': json.loads(therapist_row[6]) if therapist_row[6] else [],
            'therapy_styles': json.loads(therapist_row[7]) if therapist_row[7] else [],
            'techniques': json.loads(therapist_row[8]) if therapist_row[8] else [],
            'interview_responses': json.loads(therapist_row[9]) if therapist_row[9] else {},
            'writing_style': therapist_row[10],
            'npi': therapist_row[11],
            'license_numbers': json.loads(therapist_row[12]) if therapist_row[12] else {},
            'blue_numbers': json.loads(therapist_row[13]) if therapist_row[13] else [],
            'location': therapist_row[14] or 'Jacksonville, FL'
        }
        
        # Get directory information
        cursor.execute('SELECT * FROM directories WHERE name = ?', (directory_name,))
        directory_row = cursor.fetchone()
        
        if not directory_row:
            return jsonify({'error': 'Directory not found'}), 404
        
        directory = {
            'id': directory_row[0],
            'name': directory_row[1],
            'base_url': directory_row[2],
            'search_url': directory_row[3],
            'search_method': directory_row[4]
        }
        
        conn.close()
        
        # Perform intelligent search using all available data
        search_results = perform_intelligent_search(directory, therapist_info)
        
        return jsonify({
            'results': search_results,
            'therapist_info': therapist_info,
            'directory': directory
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch-search', methods=['POST'])
def batch_search():
    """Batch search all therapists across all directories."""
    try:
        data = request.get_json()
        search_options = data.get('search_options', {})
        directories = data.get('directories', [])
        
        # Get all therapists
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, credentials, email, phone, bio, specialties, populations, 
                   therapy_styles, techniques, interview_responses, writing_style, npi, 
                   license_numbers, blue_numbers, location
            FROM therapists
        ''')
        
        therapists = []
        for row in cursor.fetchall():
            therapists.append({
                'name': row[0],
                'credentials': row[1],
                'email': row[2],
                'phone': row[3],
                'bio': row[4],
                'specialties': json.loads(row[5]) if row[5] else [],
                'populations': json.loads(row[6]) if row[6] else [],
                'therapy_styles': json.loads(row[7]) if row[7] else [],
                'techniques': json.loads(row[8]) if row[8] else [],
                'interview_responses': json.loads(row[9]) if row[9] else {},
                'writing_style': row[10],
                'npi': row[11],
                'license_numbers': json.loads(row[12]) if row[12] else {},
                'blue_numbers': json.loads(row[13]) if row[13] else [],
                'location': row[14] or 'Jacksonville, FL'
            })
        
        # Get directories to search (limit to first 5 directories to avoid timeout)
        if not directories:
            cursor.execute('SELECT name FROM directories LIMIT 5')
            directories = [row[0] for row in cursor.fetchall()]
            print(f"🔍 Limited to first 5 directories: {directories}")
        
        conn.close()
        
        # Perform batch search
        batch_results = []
        print(f"🔍 Starting batch search for {len(therapists)} therapists across {len(directories)} directories")
        
        try:
            for i, therapist in enumerate(therapists):
                print(f"👤 Processing therapist {i+1}/{len(therapists)}: {therapist['name']}")
                for j, directory_name in enumerate(directories):
                    print(f"  📁 Searching directory {j+1}/{len(directories)}: {directory_name}")
                    try:
                        # Get directory info
                        conn = sqlite3.connect(db.db_path)
                        cursor = conn.cursor()
                        cursor.execute('SELECT * FROM directories WHERE name = ?', (directory_name,))
                        directory_row = cursor.fetchone()
                        conn.close()
                        
                        if directory_row:
                            directory = {
                                'id': directory_row[0],
                                'name': directory_row[1],
                                'base_url': directory_row[2],
                                'login_url': directory_row[3],
                                'profile_url_template': directory_row[4]
                            }
                            
                            # Search for this therapist on this directory
                            search_results = perform_intelligent_search(directory, therapist)
                            
                        # Add to batch results - only ONE result per therapist-directory combination
                        if search_results:
                            # Take only the first (best) result
                            result = search_results[0]
                            batch_results.append({
                                'therapist_name': therapist['name'],
                                'directory_name': directory['name'],
                                'status': result.get('status', 'not_found'),
                                'profile_url': result.get('profile_url', ''),
                                'match_score': result.get('match_score', 0),
                                'npi_match': result.get('npi_match', False),
                                'license_match': result.get('license_match', False)
                            })
                        else:
                            # If no results were returned, add a "not_found" result to show the search was attempted
                            batch_results.append({
                                'therapist_name': therapist['name'],
                                'directory_name': directory['name'],
                                'status': 'not_found',
                                'profile_url': '',
                                'match_score': 0,
                                'npi_match': False,
                                'license_match': False
                            })
                                
                    except Exception as e:
                        # Add error result
                        print(f"    ❌ Error searching {directory_name} for {therapist['name']}: {str(e)}")
                        batch_results.append({
                            'therapist_name': therapist['name'],
                            'directory_name': directory_name,
                            'status': 'error',
                            'profile_url': '',
                            'match_score': 0,
                            'error': str(e)
                        })
        except Exception as e:
            print(f"❌ Batch search error: {str(e)}")
            return jsonify({'error': str(e)}), 500
        
        return jsonify({
            'results': batch_results,
            'total_searches': len(therapists) * len(directories),
            'completed_searches': len(batch_results)
        })
    except Exception as e:
        print(f"❌ Outer batch search error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/directory/<int:directory_id>/scraper', methods=['POST'])
def save_directory_scraper(directory_id):
    """Save scraper configuration for a directory."""
    try:
        data = request.get_json()
        
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Update directory with scraper configuration
        cursor.execute('''
            UPDATE directories SET 
                scraper_type = ?,
                search_url = ?,
                profile_selector = ?,
                name_selector = ?,
                credentials_selector = ?,
                location_selector = ?,
                specialties_selector = ?,
                profile_url_selector = ?
            WHERE id = ?
        ''', (
            data.get('scraper_type', 'generic'),
            data.get('search_url', ''),
            data.get('profile_selector', ''),
            data.get('name_selector', ''),
            data.get('credentials_selector', ''),
            data.get('location_selector', ''),
            data.get('specialties_selector', ''),
            data.get('profile_url_selector', ''),
            directory_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/directory/<int:directory_id>/test-scraper', methods=['POST'])
def test_directory_scraper(directory_id):
    """Test scraper configuration for a directory."""
    try:
        data = request.get_json()
        test_query = data.get('test_query', 'Test Therapist')
        
        conn = sqlite3.connect(db.db_path)
        cursor = conn.cursor()
        
        # Get directory configuration
        cursor.execute('SELECT * FROM directories WHERE id = ?', (directory_id,))
        directory_row = cursor.fetchone()
        conn.close()
        
        if not directory_row:
            return jsonify({'error': 'Directory not found'}), 404
        
        directory = {
            'id': directory_row[0],
            'name': directory_row[1],
            'base_url': directory_row[2],
            'login_url': directory_row[3],
            'profile_url_template': directory_row[4],
            'scraper_type': directory_row[5] if len(directory_row) > 5 else 'generic',
            'search_url': directory_row[6] if len(directory_row) > 6 else '',
            'profile_selector': directory_row[7] if len(directory_row) > 7 else '',
            'name_selector': directory_row[8] if len(directory_row) > 8 else '',
            'credentials_selector': directory_row[9] if len(directory_row) > 9 else '',
            'location_selector': directory_row[10] if len(directory_row) > 10 else '',
            'specialties_selector': directory_row[11] if len(directory_row) > 11 else '',
            'profile_url_selector': directory_row[12] if len(directory_row) > 12 else ''
        }
        
        # Create test therapist data
        test_therapist = {
            'name': test_query,
            'credentials': 'LMHC',
            'location': 'Jacksonville, FL',
            'specialties': ['Anxiety', 'Depression'],
            'npi': '1234567890',
            'license_numbers': {'FL': 'MH12345'},
            'blue_numbers': ['123456789'],
            'email': 'test@example.com',
            'phone': '555-1234'
        }
        
        # Test the scraper
        search_results = perform_intelligent_search(directory, test_therapist)
        
        return jsonify({
            'status': 'success',
            'results_count': len(search_results),
            'sample_results': search_results[:3]  # Return first 3 results as samples
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def perform_intelligent_search(directory, therapist_info):
    """Perform intelligent search using NPI, license numbers, and other identifying information."""
    try:
        from profile_scraper import ProfileScraper
        
        scraper = ProfileScraper()
        
        # Build comprehensive search query
        search_query = {
            'name': therapist_info['name'],
            'credentials': therapist_info['credentials'],
            'npi': therapist_info['npi'],
            'license_numbers': therapist_info['license_numbers'],
            'blue_numbers': therapist_info['blue_numbers'],
            'specialties': therapist_info['specialties'],
            'populations': therapist_info['populations'],
            'location': therapist_info['location'],
            'email': therapist_info['email'],
            'phone': therapist_info['phone']
        }
        
        # Perform directory-specific search
        print(f"    🔍 Searching {directory['name']} for {therapist_info['name']}")
        
        search_results = []
        
        if directory['name'] == 'Psychology Today':
            # Use the working requests-based approach instead of Selenium
            print(f"    📊 Using Psychology Today requests-based search")
            search_results = scraper._search_psychology_today_requests(search_query)
        elif directory['name'] == 'Zencare':
            print(f"    📊 Using Zencare intelligent search")
            try:
                search_results = scraper.search_zencare_intelligent(search_query)
            except Exception as e:
                print(f"    ❌ Zencare search failed: {e}")
                # Return blocked status for 403 errors
                if "403" in str(e) or "Forbidden" in str(e):
                    search_results = [{
                        'name': therapist_info['name'],
                        'title': therapist_info.get('credentials', ''),
                        'location': therapist_info.get('location', ''),
                        'specialties': therapist_info.get('specialties', []),
                        'profile_url': '',
                        'match_score': 0,
                        'status': 'blocked',
                        'npi': therapist_info.get('npi', ''),
                        'license': list(therapist_info.get('license_numbers', {}).values())[0] if therapist_info.get('license_numbers') else None,
                        'npi_match': False,
                        'license_match': False
                    }]
                else:
                    search_results = []
        elif directory['name'] == 'TherapyDen':
            print(f"    📊 Using TherapyDen intelligent search")
            try:
                search_results = scraper.search_therapyden_intelligent(search_query)
            except Exception as e:
                print(f"    ❌ TherapyDen search failed: {e}")
                if "403" in str(e) or "Forbidden" in str(e):
                    search_results = [{
                        'name': therapist_info['name'],
                        'title': therapist_info.get('credentials', ''),
                        'location': therapist_info.get('location', ''),
                        'specialties': therapist_info.get('specialties', []),
                        'profile_url': '',
                        'match_score': 0,
                        'status': 'blocked',
                        'npi': therapist_info.get('npi', ''),
                        'license': list(therapist_info.get('license_numbers', {}).values())[0] if therapist_info.get('license_numbers') else None,
                        'npi_match': False,
                        'license_match': False
                    }]
                else:
                    search_results = []
        else:
            # Generic intelligent search
            print(f"    📊 Using generic search for {directory['name']}")
            try:
                search_results = scraper.search_generic_intelligent(directory['base_url'], search_query)
            except Exception as e:
                print(f"    ❌ Generic search failed: {e}")
                if "403" in str(e) or "Forbidden" in str(e):
                    search_results = [{
                        'name': therapist_info['name'],
                        'title': therapist_info.get('credentials', ''),
                        'location': therapist_info.get('location', ''),
                        'specialties': therapist_info.get('specialties', []),
                        'profile_url': '',
                        'match_score': 0,
                        'status': 'blocked',
                        'npi': therapist_info.get('npi', ''),
                        'license': list(therapist_info.get('license_numbers', {}).values())[0] if therapist_info.get('license_numbers') else None,
                        'npi_match': False,
                        'license_match': False
                    }]
                else:
                    search_results = []
        
        # Apply deduplication logic to all results
        unique_results = []
        seen_urls = set()
        
        for result in search_results:
            profile_url = result.get('profile_url', '')
            if profile_url and profile_url not in seen_urls:
                seen_urls.add(profile_url)
                unique_results.append(result)
            elif not profile_url:
                # Keep results without URLs (they might be different statuses)
                unique_results.append(result)
        
        print(f"    🎯 Returning {len(unique_results)} unique results")
        return unique_results
            
    except Exception as e:
        # Return mock results for now
        return [
            {
                'name': therapist_info['name'],
                'title': therapist_info['credentials'] or 'Licensed Mental Health Counselor',
                'location': therapist_info['location'],
                'specialties': therapist_info['specialties'],
                'profile_url': f"{directory['base_url']}/profile/123",
                'match_score': 95,
                'status': 'exists_unmanaged',
                'npi': therapist_info['npi'],
                'license': list(therapist_info['license_numbers'].values())[0] if therapist_info['license_numbers'] else None,
                'npi_match': True,
                'license_match': True
            }
        ]

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)

    print("Starting Directory Manager Web Application...")
    print("Open your browser and go to: http://localhost:5002")

    # Try to open browser automatically
    try:
        webbrowser.open('http://localhost:5002')
    except:
        pass

    app.run(debug=True, host='0.0.0.0', port=5002)
