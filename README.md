# Directory Manager

A modern desktop application for managing therapist directory profiles across multiple platforms.

## Features

### Current Features
- **Modern UI**: Clean, professional interface built with CustomTkinter
- **Database Management**: SQLite database for storing therapist and directory information
- **CSV Import/Export**: Import existing spreadsheet data and export back to CSV format
- **Coverage Matrix**: Visual representation of therapist coverage across directories
- **Profile Management**: Track therapist profiles across multiple directory sites

### Planned Features
- **Automated Profile Updates**: Automatically update therapist profiles across directories
- **AI Content Generation**: Generate profile content using therapist information and writing styles
- **Profile Discovery**: Search for existing therapist profiles on directory sites
- **Analytics Dashboard**: Track directory performance and referral sources
- **Scheduling System**: Automated reminders for profile updates
- **Browser Automation**: Direct integration with directory websites

## Installation

1. **Create Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Web Application** (Recommended):
   ```bash
   ./web_launch.sh
   ```
   Then open your browser and go to: http://localhost:5000

4. **Alternative: Desktop Application**:
   ```bash
   ./launch.sh
   ```
   (Note: Requires Tkinter support on your system)

## Usage

### Importing Existing Data

1. Go to the **Import/Export** tab
2. Click **Import Directory Details CSV** to import your existing spreadsheet
3. Click **Import Directory Grid CSV** to import the grid format
4. The application will automatically create therapists, directories, and profiles

### Managing Therapists

1. Go to the **Therapists** tab
2. Use the toolbar to add, edit, or delete therapists
3. View therapist information and profile counts

### Managing Directories

1. Go to the **Directories** tab
2. Add new directory sites with their requirements
3. Track which directories are free vs. premium

### Managing Profiles

1. Go to the **Profiles** tab
2. View all therapist-directory combinations
3. Click **Open Profile** to view profiles in your browser
4. Update profile information as needed

### Dashboard

The dashboard provides an overview of:
- Total therapists, directories, and profiles
- Coverage percentage across all combinations
- Coverage matrix showing which therapists are on which directories
- Recent activity log

## Database Schema

The application uses SQLite with the following main tables:

- **therapists**: Therapist information, credentials, specialties
- **directories**: Directory sites with requirements and ranking factors
- **therapist_profiles**: Junction table linking therapists to directories
- **automation_tasks**: Scheduled automation tasks
- **analytics**: Performance metrics and analytics data

## Directory Sites Supported

Currently tracks profiles for:
- Psychology Today
- Zencare
- TherapyDen
- Headway
- Open Path Collective
- Therapy Route
- ShareCare
- ZocDoc
- CareDash
- Health Grades
- eHealth Scores
- HealthLine
- Bark
- Alignable
- IOCDF
- PSI Directory
- Trauma Therapist Network
- Being Seen
- Jax Therapy Network

## Future Enhancements

- **Browser Automation**: Direct integration with directory websites
- **AI Integration**: ChatGPT API integration for content generation
- **Advanced Analytics**: Referral tracking and ROI analysis
- **Multi-user Support**: Different access levels for team members
- **Cloud Sync**: Optional cloud backup and synchronization
- **API Integration**: Direct API connections to directory sites

## Technical Details

- **Framework**: Python with CustomTkinter for modern UI
- **Database**: SQLite for local data storage
- **Import/Export**: Pandas for CSV processing
- **Future**: Selenium for browser automation, OpenAI API for AI features

## Support

For questions or issues, please refer to the application's built-in help system or contact the development team.
