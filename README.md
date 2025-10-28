# Directory Manager

A modern web application for managing therapist directory profiles across multiple platforms with intelligent web scraping and automated profile management.

## Features

### ✅ Current Features
- **Modern Web UI**: Clean, Apple-inspired interface built with Flask and Bootstrap 5
- **Intelligent Web Scraping**: Automated profile discovery across multiple directory sites
- **Anti-Bot Protection**: Advanced handling of 403 errors and bot detection systems
- **Batch Search**: Search all directories for all therapists with one click
- **Profile Status Management**: Track profiles as active, exists_unmanaged, needs_claiming, etc.
- **Real-time Profile Viewing**: Live profile content comparison and management
- **Directory-Specific Scrapers**: Custom scraping logic for each directory platform
- **Database Management**: SQLite database with automated migrations
- **CSV Import/Export**: Import existing spreadsheet data and export back to CSV format
- **Coverage Matrix**: Visual representation of therapist coverage across directories
- **Google Forms Integration**: Import therapist data from Google Forms responses
- **Responsive Design**: Works on desktop, tablet, and mobile devices

### 🚀 Advanced Features
- **Psychology Today Integration**: Sophisticated requests-based scraper with deduplication
- **Zencare Integration**: Custom scraper with anti-bot protection handling
- **TherapyDen Integration**: Directory-specific search and profile extraction
- **Profile Confirmation Workflow**: Streamlined process for confirming and managing profiles
- **Error Handling**: Comprehensive error handling for network issues and blocked requests
- **Modern Styling**: Apple-inspired color palette with subtle grays and minimal accents

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/zkbell91/directory-manager.git
   cd directory-manager
   ```

2. **Create Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   ./web_launch.sh
   ```
   Or manually:
   ```bash
   python web_app.py
   ```

5. **Open in Browser**:
   Navigate to: http://localhost:5002

## Usage

### Dashboard Overview
- **Metric Cards**: View total therapists, directories, profiles, and coverage percentage
- **Coverage Matrix**: Interactive grid showing therapist-directory combinations
- **Batch Search**: Search all directories for all therapists with one click
- **Smart Search**: Intelligent profile discovery using NPI, license numbers, and location

### Profile Management
1. **Search for Profiles**: Use the "Search for Existing Profile" button on the dashboard
2. **Confirm Matches**: Review search results and confirm correct profiles
3. **Status Management**: Mark profiles as "We Manage This", "Therapist-Managed", or "Needs Claiming"
4. **Batch Processing**: Handle multiple search results without closing the modal

### Directory Management
1. **View Directories**: Click on directory rows to view detailed information
2. **Configure Scrapers**: Set up custom scraping logic for each directory
3. **Test Scrapers**: Test scraper configurations before deploying
4. **Monitor Performance**: Track scraper success rates and error handling

### Therapist Management
1. **View Therapist Details**: Click on therapist names to see comprehensive profiles
2. **Profile Overview**: See all directory profiles for each therapist
3. **Contact Information**: Manage therapist contact details and credentials
4. **Specialty Tracking**: Track therapist specialties and populations served

## Supported Directory Sites

The application currently supports intelligent scraping for:

- **Psychology Today** - Sophisticated requests-based scraper with deduplication
- **Zencare** - Custom scraper with anti-bot protection handling  
- **TherapyDen** - Directory-specific search and profile extraction
- **Headway** - Generic scraper with error handling
- **Open Path Collective** - Generic scraper implementation
- **Therapy Route** - Generic scraper implementation
- **ShareCare** - Generic scraper implementation
- **ZocDoc** - Generic scraper implementation
- **CareDash** - Generic scraper implementation
- **Health Grades** - Generic scraper implementation
- **eHealth Scores** - Generic scraper implementation
- **HealthLine** - Generic scraper implementation
- **Bark** - Generic scraper implementation
- **Alignable** - Generic scraper implementation
- **IOCDF** - Generic scraper implementation
- **PSI Directory** - Generic scraper implementation
- **Trauma Therapist Network** - Generic scraper implementation
- **Being Seen** - Generic scraper implementation
- **Jax Therapy Network** - Generic scraper implementation

## Technical Architecture

### Backend
- **Flask**: Web framework with RESTful API endpoints
- **SQLite**: Local database with automated migrations
- **Requests/BeautifulSoup**: Web scraping with anti-bot protection
- **Selenium**: Browser automation for JavaScript-heavy sites
- **Undetected ChromeDriver**: Advanced bot detection bypass

### Frontend
- **Bootstrap 5**: Responsive UI framework
- **JavaScript/jQuery**: Interactive components and API calls
- **Font Awesome**: Professional iconography
- **Modern CSS**: Apple-inspired design system with CSS custom properties

### Database Schema
- **therapists**: Therapist information, credentials, specialties, NPI numbers
- **directories**: Directory sites with scraper configurations and requirements
- **therapist_profiles**: Profile status, URLs, and management information
- **automation_tasks**: Scheduled tasks and automation settings

## API Endpoints

- `GET /` - Dashboard overview
- `GET /therapists` - Therapist management
- `GET /directories` - Directory management  
- `GET /profiles` - Profile management
- `POST /api/auto-search-profile` - Intelligent profile search
- `POST /api/batch-search` - Batch search across directories
- `POST /api/confirm-profile` - Confirm profile matches
- `GET /api/directory/<id>` - Directory details
- `POST /api/directory/<id>/scraper` - Configure directory scraper

## Development

### Project Structure
```
directory-manager/
├── web_app.py              # Main Flask application
├── database.py             # Database management and migrations
├── profile_scraper.py      # Web scraping logic
├── human_like_scraper.py   # Advanced bot detection bypass
├── undetected_scraper.py   # Undetected ChromeDriver integration
├── google_form_importer.py # Google Forms data import
├── csv_importer.py         # CSV import/export functionality
├── templates/              # HTML templates
├── requirements.txt        # Python dependencies
└── web_launch.sh          # Application launcher
```

### Adding New Directory Support
1. Add directory to database with scraper configuration
2. Implement directory-specific search method in `profile_scraper.py`
3. Add error handling for directory-specific issues
4. Test scraper with various therapist profiles
5. Update UI to show directory-specific status

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions, issues, or feature requests, please open an issue on GitHub or contact the development team.
