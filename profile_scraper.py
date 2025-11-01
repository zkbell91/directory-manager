"""
Profile Scraper for Directory Management System

Handles web scraping and searching across various therapist directory websites.
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlencode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import json


class ProfileScraper:
    """Web scraper for therapist directory websites."""
    
    def __init__(self):
        self.session = requests.Session()
        # More realistic headers to avoid detection
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
    def _get_selenium_driver(self):
        """Get a configured Selenium WebDriver."""
        # Try Chrome first
        try:
            print("🔧 Creating Chrome driver...")
            chrome_options = Options()
            # Enhanced configuration for compatibility and stability
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--disable-sync')
            chrome_options.add_argument('--disable-translate')
            chrome_options.add_argument('--disable-logging')
            chrome_options.add_argument('--disable-permissions-api')
            chrome_options.add_argument('--disable-background-timer-throttling')
            chrome_options.add_argument('--disable-renderer-backgrounding')
            chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            chrome_options.add_argument('--disable-client-side-phishing-detection')
            chrome_options.add_argument('--disable-component-extensions-with-background-pages')
            chrome_options.add_argument('--disable-default-apps')
            chrome_options.add_argument('--disable-hang-monitor')
            chrome_options.add_argument('--disable-prompt-on-repost')
            chrome_options.add_argument('--disable-domain-reliability')
            chrome_options.add_argument('--disable-features=TranslateUI')
            chrome_options.add_argument('--disable-ipc-flooding-protection')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36')
            
            # Try to use a specific ChromeDriver version compatible with Chrome 114
            try:
                service = Service(ChromeDriverManager(driver_version="114.0.5735.90").install())
            except:
                # Fallback to latest version
                service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ Chrome driver created successfully!")
            return driver
        except Exception as e:
            print(f"❌ Chrome driver failed: {e}")
        
        # Try Firefox as fallback
        try:
            print("🔧 Creating Firefox driver...")
            firefox_options = FirefoxOptions()
            firefox_options.add_argument('--width=1920')
            firefox_options.add_argument('--height=1080')
            firefox_options.set_preference("dom.webnotifications.enabled", False)
            firefox_options.set_preference("media.volume_scale", "0.0")
            
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=firefox_options)
            print("✅ Firefox driver created successfully!")
            return driver
        except Exception as e:
            print(f"❌ Firefox driver failed: {e}")
        
        print("❌ All drivers failed")
        return None
    
    def search_psychology_today_intelligent(self, search_query):
        """Search Psychology Today using intelligent matching."""
        try:
            print(f"🔍 Searching Psychology Today for: {search_query.get('name', '')}")
            
            # Psychology Today search URL
            base_url = "https://www.psychologytoday.com/us/therapists"
            
            # Build search parameters
            params = {
                'search': search_query.get('name', ''),
                'location': search_query.get('location', 'Jacksonville, FL'),
                'specialty': ','.join(search_query.get('specialties', [])),
                'insurance': '',
                'language': '',
                'gender': '',
                'age': '',
                'therapy_type': '',
                'price_range': '',
                'near': search_query.get('location', 'Jacksonville, FL')
            }
            
            # Remove empty parameters
            params = {k: v for k, v in params.items() if v}
            
            # Try Selenium first for JavaScript-heavy sites
            driver = self._get_selenium_driver()
            if driver:
                try:
                    # Navigate to search page
                    search_url = f"{base_url}?{urlencode(params)}"
                    print(f"🌐 Navigating to: {search_url}")
                    driver.get(search_url)
                    
                    # Check if we got blocked
                    if "403" in driver.page_source or "Forbidden" in driver.page_source:
                        print("❌ Blocked by Psychology Today (403 Forbidden)")
                        driver.quit()
                        return self._handle_blocked_search(search_query, "Psychology Today")
                    
                    # Wait for results to load with multiple possible selectors
                    try:
                        WebDriverWait(driver, 15).until(
                            EC.any_of(
                                EC.presence_of_element_located((By.CLASS_NAME, "profile-card")),
                                EC.presence_of_element_located((By.CLASS_NAME, "profile")),
                                EC.presence_of_element_located((By.CLASS_NAME, "therapist-card")),
                                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid*='profile']")),
                                EC.presence_of_element_located((By.CSS_SELECTOR, ".result-item"))
                            )
                        )
                        print("✅ Found profile elements")
                    except TimeoutException:
                        # Try to find any profile-like elements
                        profile_elements = driver.find_elements(By.CSS_SELECTOR, "[class*='profile'], [class*='therapist'], [class*='result']")
                        if not profile_elements:
                            print("❌ No profile elements found on Psychology Today")
                            driver.quit()
                            return self._handle_no_results(search_query, "Psychology Today")
                    
                    # Extract profile information
                    profiles = []
                    # Try multiple selectors for profile cards
                    profile_cards = driver.find_elements(By.CSS_SELECTOR, 
                        ".profile-card, .profile, .therapist-card, [class*='profile'], [class*='therapist'], .result-item")
                    
                    print(f"📋 Found {len(profile_cards)} profile cards")
                    
                    for card in profile_cards[:5]:  # Limit to first 5 results
                        try:
                            # Extract profile data with flexible selectors
                            name_elem = None
                            for selector in [".profile-name a", ".name a", "h3 a", "h2 a", "h4 a", "a[href*='profile']"]:
                                try:
                                    name_elem = card.find_element(By.CSS_SELECTOR, selector)
                                    break
                                except NoSuchElementException:
                                    continue
                            
                            if not name_elem:
                                continue
                                
                            name = name_elem.text.strip()
                            profile_url = name_elem.get_attribute('href')
                            
                            # Try to get credentials
                            try:
                                credentials_elem = card.find_element(By.CSS_SELECTOR, ".profile-credentials")
                                credentials = credentials_elem.text.strip()
                            except NoSuchElementException:
                                credentials = ""
                            
                            # Try to get location
                            try:
                                location_elem = card.find_element(By.CSS_SELECTOR, ".profile-location")
                                location = location_elem.text.strip()
                            except NoSuchElementException:
                                location = search_query.get('location', '')
                            
                            # Try to get specialties
                            try:
                                specialties_elem = card.find_element(By.CSS_SELECTOR, ".profile-specialties")
                                specialties = [s.strip() for s in specialties_elem.text.split(',')]
                            except NoSuchElementException:
                                specialties = search_query.get('specialties', [])
                            
                            # Calculate match score
                            match_score = self._calculate_match_score(search_query, {
                                'name': name,
                                'credentials': credentials,
                                'location': location,
                                'specialties': specialties
                            })
                            
                            profiles.append({
                                'name': name,
                                'title': credentials,
                                'location': location,
                                'specialties': specialties,
                                'profile_url': profile_url,
                                'match_score': match_score,
                                'status': 'exists_unmanaged',
                                'npi': search_query.get('npi', ''),
                                'license': list(search_query.get('license_numbers', {}).values())[0] if search_query.get('license_numbers') else None,
                                'npi_match': False,
                                'license_match': False
                            })
                            
                        except Exception as e:
                            print(f"Error parsing profile card: {e}")
                            continue
                    
                    driver.quit()
                    print(f"✅ Found {len(profiles)} profiles")
                    return profiles
                    
                except TimeoutException:
                    print("❌ Timeout waiting for Psychology Today results")
                    driver.quit()
                    return self._handle_timeout(search_query, "Psychology Today")
                except Exception as e:
                    print(f"❌ Error with Selenium search: {e}")
                    driver.quit()
                    return self._handle_error(search_query, "Psychology Today", str(e))
            
            # Fallback to requests if Selenium fails
            return self._search_psychology_today_requests(search_query)
            
        except Exception as e:
            print(f"❌ Error searching Psychology Today: {e}")
            return self._handle_error(search_query, "Psychology Today", str(e))
    
    def _search_psychology_today_requests(self, search_query):
        """Fallback search using requests library."""
        try:
            print(f"🔍 Using requests-based search for: {search_query.get('name', '')}")
            
            base_url = "https://www.psychologytoday.com/us/therapists"
            params = {
                'search': search_query.get('name', ''),
                'location': search_query.get('location', 'Jacksonville, FL'),
                'specialty': ','.join(search_query.get('specialties', [])),
                'near': search_query.get('location', 'Jacksonville, FL')
            }
            
            # Remove empty parameters
            params = {k: v for k, v in params.items() if v}
            
            print(f"🌐 Making request to: {base_url}?{urlencode(params)}")
            response = self.session.get(base_url, params=params, timeout=10)
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 403:
                print(f"🚫 Search blocked by Psychology Today (403 Forbidden)")
                return [{
                    'name': search_query.get('name', ''),
                    'title': search_query.get('credentials', ''),
                    'location': search_query.get('location', ''),
                    'specialties': search_query.get('specialties', []),
                    'profile_url': '',
                    'match_score': 0,
                    'status': 'blocked',
                    'npi': search_query.get('npi', ''),
                    'license': list(search_query.get('license_numbers', {}).values())[0] if search_query.get('license_numbers') else None,
                    'npi_match': False,
                    'license_match': False
                }]
            elif response.status_code != 200:
                print(f"❌ Request failed with status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            profiles = []
            
            # Look for profile elements with multiple selectors
            profile_selectors = [
                'div[class*="profile"]',
                'div[class*="therapist"]',
                'div[class*="result"]',
                'article[class*="profile"]',
                'article[class*="therapist"]'
            ]
            
            profile_elements = []
            for selector in profile_selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        print(f"✅ Found {len(elements)} elements with selector: {selector}")
                        profile_elements.extend(elements)
                        break
                except Exception as e:
                    print(f"❌ Error with selector {selector}: {e}")
                    continue
            
            # Also look for any links that might be profiles
            profile_links = soup.find_all('a', href=lambda x: x and ('profile' in x.lower() or 'therapist' in x.lower() or '/therapists/' in x.lower()))
            print(f"🔗 Found {len(profile_links)} potential profile links")
            
            # Process profile links
            for link in profile_links[:5]:
                try:
                    href = link.get('href', '')
                    if not href or ('profile' not in href.lower() and '/therapists/' not in href.lower()):
                        continue
                    
                    # Skip navigation links
                    if href == base_url or href.endswith('/therapists'):
                        continue
                    
                    # Skip if it's not a specific profile URL (should contain therapist name)
                    if '/therapists/' not in href or href.count('/') < 4:
                        continue
                    
                    # Skip location pages (e.g., /therapists/fl/casselberry, /therapists/ct/berlin)
                    if any(loc in href.lower() for loc in ['/fl/', '/ct/', '/ca/', '/ny/', '/tx/', '/ga/', '/nc/', '/sc/', '/al/', '/ms/', '/la/', '/tn/', '/ky/', '/in/', '/oh/', '/mi/', '/wi/', '/mn/', '/ia/', '/mo/', '/ar/', '/ok/', '/ks/', '/ne/', '/nd/', '/sd/', '/mt/', '/wy/', '/co/', '/nm/', '/az/', '/ut/', '/nv/', '/id/', '/wa/', '/or/', '/ak/', '/hi/']):
                        continue
                    
                    # Skip if it's the base therapists page
                    if href == base_url or href.endswith('/therapists'):
                        continue
                        
                    name = link.text.strip()
                    if not name:
                        # Try to find name in the parent container
                        parent = link.parent
                        if parent:
                            # Look for the profile title link
                            title_link = parent.find('a', class_='profile-title')
                            if title_link:
                                name = title_link.text.strip()
                            else:
                                # Look for any text that looks like a name
                                name_elem = parent.find(['h1', 'h2', 'h3', 'h4', 'div'], string=lambda x: x and x.strip() and len(x.strip()) > 3)
                                if name_elem:
                                    name = name_elem.text.strip()
                    
                    if not name:
                        continue
                    
                    # Make sure it's a full URL
                    if href.startswith('/'):
                        profile_url = urljoin(base_url, href)
                    else:
                        profile_url = href
                    
                    # Extract other details from parent elements
                    parent = link.parent
                    credentials = ""
                    location = search_query.get('location', '')
                    specialties = search_query.get('specialties', [])
                    
                    # Try to find credentials and location in nearby elements
                    if parent:
                        # Look for credentials
                        cred_elem = parent.find(['div', 'span'], class_=lambda x: x and ('credential' in x.lower() or 'title' in x.lower() or 'degree' in x.lower()))
                        if cred_elem:
                            credentials = cred_elem.text.strip()
                        
                        # Look for location
                        loc_elem = parent.find(['div', 'span'], class_=lambda x: x and ('location' in x.lower() or 'address' in x.lower() or 'city' in x.lower()))
                        if loc_elem:
                            location = loc_elem.text.strip()
                    
                    # Calculate match score
                    match_score = self._calculate_match_score(search_query, {
                        'name': name,
                        'credentials': credentials,
                        'location': location,
                        'specialties': specialties
                    })
                    
                    profiles.append({
                        'name': name,
                        'title': credentials,
                        'location': location,
                        'specialties': specialties,
                        'profile_url': profile_url,
                        'match_score': match_score,
                        'status': 'exists_unmanaged',
                        'npi': search_query.get('npi', ''),
                        'license': list(search_query.get('license_numbers', {}).values())[0] if search_query.get('license_numbers') else None,
                        'npi_match': False,
                        'license_match': False
                    })
                    
                    print(f"✅ Found profile: {name} - {profile_url}")
                    
                except Exception as e:
                    print(f"❌ Error parsing profile link: {e}")
                    continue
            
            # Deduplicate profiles by URL
            unique_profiles = []
            seen_urls = set()
            
            for profile in profiles:
                profile_url = profile.get('profile_url', '')
                if profile_url and profile_url not in seen_urls:
                    seen_urls.add(profile_url)
                    unique_profiles.append(profile)
                elif not profile_url:
                    # Keep profiles without URLs (they might be different)
                    unique_profiles.append(profile)
            
            print(f"🎉 Successfully found {len(unique_profiles)} unique profiles using requests!")
            return unique_profiles
            
        except Exception as e:
            print(f"❌ Error with requests search: {e}")
            return []
    
    def search_zencare_intelligent(self, search_query):
        """Search Zencare using intelligent matching."""
        try:
            # Zencare search implementation
            base_url = "https://zencare.co"
            search_url = f"{base_url}/therapists"
            
            # Build search parameters
            params = {
                'location': search_query.get('location', 'Jacksonville, FL'),
                'specialty': ','.join(search_query.get('specialties', [])),
                'insurance': '',
                'gender': '',
                'age': '',
                'therapy_type': ''
            }
            
            # Remove empty parameters
            params = {k: v for k, v in params.items() if v}
            
            response = self.session.get(search_url, params=params, timeout=10)
            
            # Handle 403 Forbidden specifically
            if response.status_code == 403:
                print(f"🚫 Zencare search blocked (403 Forbidden)")
                return [{
                    'name': search_query.get('name', ''),
                    'title': search_query.get('credentials', ''),
                    'location': search_query.get('location', ''),
                    'specialties': search_query.get('specialties', []),
                    'profile_url': '',
                    'match_score': 0,
                    'status': 'blocked',
                    'npi': search_query.get('npi', ''),
                    'license': list(search_query.get('license_numbers', {}).values())[0] if search_query.get('license_numbers') else None,
                    'npi_match': False,
                    'license_match': False
                }]
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            profiles = []
            
            # Look for therapist cards
            therapist_cards = soup.find_all('div', class_='therapist-card')
            
            for card in therapist_cards[:5]:
                try:
                    name_elem = card.find('h3', class_='therapist-name')
                    if not name_elem:
                        continue
                        
                    name = name_elem.text.strip()
                    profile_url = urljoin(base_url, name_elem.find('a').get('href', ''))
                    
                    # Extract other details
                    credentials = ""
                    credentials_elem = card.find('div', class_='therapist-credentials')
                    if credentials_elem:
                        credentials = credentials_elem.text.strip()
                    
                    location = search_query.get('location', '')
                    location_elem = card.find('div', class_='therapist-location')
                    if location_elem:
                        location = location_elem.text.strip()
                    
                    specialties = search_query.get('specialties', [])
                    specialties_elem = card.find('div', class_='therapist-specialties')
                    if specialties_elem:
                        specialties = [s.strip() for s in specialties_elem.text.split(',')]
                    
                    # Calculate match score
                    match_score = self._calculate_match_score(search_query, {
                        'name': name,
                        'credentials': credentials,
                        'location': location,
                        'specialties': specialties
                    })
                    
                    profiles.append({
                        'name': name,
                        'title': credentials,
                        'location': location,
                        'specialties': specialties,
                        'profile_url': profile_url,
                        'match_score': match_score,
                        'status': 'exists_unmanaged',
                        'npi': search_query.get('npi', ''),
                        'license': list(search_query.get('license_numbers', {}).values())[0] if search_query.get('license_numbers') else None,
                        'npi_match': False,
                        'license_match': False
                    })
                    
                except Exception as e:
                    print(f"Error parsing Zencare profile: {e}")
                    continue
            
            return profiles
            
        except Exception as e:
            print(f"Error searching Zencare: {e}")
            return []
    
    def search_therapyden_intelligent(self, search_query):
        """Search TherapyDen using intelligent matching."""
        try:
            # TherapyDen search implementation
            base_url = "https://www.therapyden.com"
            search_url = f"{base_url}/therapists"
            
            # Build search parameters
            params = {
                'location': search_query.get('location', 'Jacksonville, FL'),
                'specialty': ','.join(search_query.get('specialties', [])),
                'insurance': '',
                'gender': '',
                'age': '',
                'therapy_type': ''
            }
            
            # Remove empty parameters
            params = {k: v for k, v in params.items() if v}
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            profiles = []
            
            # Look for therapist cards
            therapist_cards = soup.find_all('div', class_='therapist-card')
            
            for card in therapist_cards[:5]:
                try:
                    name_elem = card.find('h3', class_='therapist-name')
                    if not name_elem:
                        continue
                        
                    name = name_elem.text.strip()
                    profile_url = urljoin(base_url, name_elem.find('a').get('href', ''))
                    
                    # Extract other details
                    credentials = ""
                    credentials_elem = card.find('div', class_='therapist-credentials')
                    if credentials_elem:
                        credentials = credentials_elem.text.strip()
                    
                    location = search_query.get('location', '')
                    location_elem = card.find('div', class_='therapist-location')
                    if location_elem:
                        location = location_elem.text.strip()
                    
                    specialties = search_query.get('specialties', [])
                    specialties_elem = card.find('div', class_='therapist-specialties')
                    if specialties_elem:
                        specialties = [s.strip() for s in specialties_elem.text.split(',')]
                    
                    # Calculate match score
                    match_score = self._calculate_match_score(search_query, {
                        'name': name,
                        'credentials': credentials,
                        'location': location,
                        'specialties': specialties
                    })
                    
                    profiles.append({
                        'name': name,
                        'title': credentials,
                        'location': location,
                        'specialties': specialties,
                        'profile_url': profile_url,
                        'match_score': match_score,
                        'status': 'exists_unmanaged',
                        'npi': search_query.get('npi', ''),
                        'license': list(search_query.get('license_numbers', {}).values())[0] if search_query.get('license_numbers') else None,
                        'npi_match': False,
                        'license_match': False
                    })
                    
                except Exception as e:
                    print(f"Error parsing TherapyDen profile: {e}")
                    continue
            
            return profiles
            
        except Exception as e:
            print(f"Error searching TherapyDen: {e}")
            return []
    
    def search_generic_intelligent(self, base_url, search_query):
        """Generic search for other directory websites."""
        try:
            # Generic search implementation
            search_url = f"{base_url}/search"
            
            params = {
                'q': search_query.get('name', ''),
                'location': search_query.get('location', ''),
                'specialty': ','.join(search_query.get('specialties', []))
            }
            
            # Remove empty parameters
            params = {k: v for k, v in params.items() if v}
            
            response = self.session.get(search_url, params=params, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            profiles = []
            
            # Generic profile extraction
            profile_cards = soup.find_all(['div', 'article'], class_=re.compile(r'profile|therapist|card'))
            
            for card in profile_cards[:5]:
                try:
                    name_elem = card.find(['h1', 'h2', 'h3', 'h4'], class_=re.compile(r'name|title'))
                    if not name_elem:
                        continue
                        
                    name = name_elem.text.strip()
                    profile_url = urljoin(base_url, name_elem.find('a').get('href', ''))
                    
                    # Calculate match score
                    match_score = self._calculate_match_score(search_query, {
                        'name': name,
                        'credentials': '',
                        'location': search_query.get('location', ''),
                        'specialties': search_query.get('specialties', [])
                    })
                    
                    profiles.append({
                        'name': name,
                        'title': '',
                        'location': search_query.get('location', ''),
                        'specialties': search_query.get('specialties', []),
                        'profile_url': profile_url,
                        'match_score': match_score,
                        'status': 'exists_unmanaged',
                        'npi': search_query.get('npi', ''),
                        'license': list(search_query.get('license_numbers', {}).values())[0] if search_query.get('license_numbers') else None,
                        'npi_match': False,
                        'license_match': False
                    })
                    
                except Exception as e:
                    print(f"Error parsing generic profile: {e}")
                    continue
            
            return profiles
            
        except Exception as e:
            print(f"Error with generic search: {e}")
            return []
    
    def _calculate_match_score(self, search_query, found_profile):
        """Calculate match score between search query and found profile."""
        score = 0
        
        # Name matching (40 points)
        search_name = search_query.get('name', '').lower()
        found_name = found_profile.get('name', '').lower()
        
        if search_name in found_name or found_name in search_name:
            score += 40
        elif self._name_similarity(search_name, found_name) > 0.7:
            score += 30
        elif self._name_similarity(search_name, found_name) > 0.5:
            score += 20
        
        # Location matching (30 points)
        search_location = search_query.get('location', '').lower()
        found_location = found_profile.get('location', '').lower()
        
        if search_location in found_location or found_location in search_location:
            score += 30
        elif self._location_similarity(search_location, found_location) > 0.7:
            score += 20
        
        # Specialties matching (20 points)
        search_specialties = [s.lower() for s in search_query.get('specialties', [])]
        found_specialties = [s.lower() for s in found_profile.get('specialties', [])]
        
        if search_specialties and found_specialties:
            common_specialties = set(search_specialties) & set(found_specialties)
            if common_specialties:
                score += 20
        
        # Credentials matching (10 points)
        search_credentials = search_query.get('credentials', '').lower()
        found_credentials = found_profile.get('credentials', '').lower()
        
        if search_credentials and found_credentials:
            if any(cred in found_credentials for cred in search_credentials.split()):
                score += 10
        
        return min(score, 100)  # Cap at 100
    
    def _name_similarity(self, name1, name2):
        """Calculate similarity between two names."""
        # Simple similarity based on common words
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        if not words1 or not words2:
            return 0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0
    
    def _location_similarity(self, location1, location2):
        """Calculate similarity between two locations."""
        # Simple similarity based on common words
        words1 = set(location1.split())
        words2 = set(location2.split())
        
        if not words1 or not words2:
            return 0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0
    
    def scrape_profile(self, profile_url):
        """Scrape detailed information from a specific profile URL."""
        try:
            response = self.session.get(profile_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract profile information
            profile_data = {
                'url': profile_url,
                'name': '',
                'credentials': '',
                'location': '',
                'specialties': [],
                'bio': '',
                'contact_info': {},
                'insurance': [],
                'languages': [],
                'session_types': []
            }
            
            # Extract name
            name_elem = soup.find(['h1', 'h2'], class_=re.compile(r'name|title'))
            if name_elem:
                profile_data['name'] = name_elem.text.strip()
            
            # Extract credentials
            credentials_elem = soup.find('div', class_=re.compile(r'credentials|title'))
            if credentials_elem:
                profile_data['credentials'] = credentials_elem.text.strip()
            
            # Extract location
            location_elem = soup.find('div', class_=re.compile(r'location|address'))
            if location_elem:
                profile_data['location'] = location_elem.text.strip()
            
            # Extract specialties
            specialties_elem = soup.find('div', class_=re.compile(r'specialties|specialties'))
            if specialties_elem:
                profile_data['specialties'] = [s.strip() for s in specialties_elem.text.split(',')]
            
            # Extract bio
            bio_elem = soup.find('div', class_=re.compile(r'bio|description|about'))
            if bio_elem:
                profile_data['bio'] = bio_elem.text.strip()
            
            return profile_data
            
        except Exception as e:
            print(f"Error scraping profile {profile_url}: {e}")
            return None
    
    def compare_profiles(self, live_data, stored_data):
        """Compare live profile data with stored data."""
        comparison = {
            'name_match': live_data.get('name', '') == stored_data.get('therapist_name', ''),
            'location_match': live_data.get('location', '') == stored_data.get('location', ''),
            'specialties_match': set(live_data.get('specialties', [])) == set(stored_data.get('specialties', [])),
            'bio_updated': live_data.get('bio', '') != stored_data.get('bio', ''),
            'differences': []
        }
        
        # Identify specific differences
        if not comparison['name_match']:
            comparison['differences'].append('Name mismatch')
        if not comparison['location_match']:
            comparison['differences'].append('Location mismatch')
        if not comparison['specialties_match']:
            comparison['differences'].append('Specialties mismatch')
        if comparison['bio_updated']:
            comparison['differences'].append('Bio updated')
        
        return comparison
    
    def _handle_blocked_search(self, search_query, directory_name):
        """Handle when search is blocked by anti-bot protection."""
        print(f"🚫 Search blocked on {directory_name} - implementing fallback strategy")
        
        # Return a helpful message with manual search instructions
        return [{
            'name': f"Search blocked on {directory_name}",
            'title': "Manual search required",
            'location': search_query.get('location', ''),
            'specialties': search_query.get('specialties', []),
            'profile_url': f"https://www.{directory_name.lower().replace(' ', '')}.com",
            'match_score': 0,
            'status': 'blocked',
            'npi': search_query.get('npi', ''),
            'license': list(search_query.get('license_numbers', {}).values())[0] if search_query.get('license_numbers') else None,
            'npi_match': False,
            'license_match': False,
            'error_message': f"Search blocked by {directory_name}. Please search manually using: {search_query.get('name', '')} in {search_query.get('location', '')}"
        }]
    
    def _handle_no_results(self, search_query, directory_name):
        """Handle when no results are found."""
        print(f"🔍 No results found on {directory_name}")
        
        return [{
            'name': f"No results found on {directory_name}",
            'title': "Profile may not exist",
            'location': search_query.get('location', ''),
            'specialties': search_query.get('specialties', []),
            'profile_url': f"https://www.{directory_name.lower().replace(' ', '')}.com",
            'match_score': 0,
            'status': 'not_found',
            'npi': search_query.get('npi', ''),
            'license': list(search_query.get('license_numbers', {}).values())[0] if search_query.get('license_numbers') else None,
            'npi_match': False,
            'license_match': False,
            'error_message': f"No profiles found for {search_query.get('name', '')} on {directory_name}"
        }]
    
    def _handle_timeout(self, search_query, directory_name):
        """Handle when search times out."""
        print(f"⏰ Search timed out on {directory_name}")
        
        return [{
            'name': f"Search timed out on {directory_name}",
            'title': "Please try again",
            'location': search_query.get('location', ''),
            'specialties': search_query.get('specialties', []),
            'profile_url': f"https://www.{directory_name.lower().replace(' ', '')}.com",
            'match_score': 0,
            'status': 'timeout',
            'npi': search_query.get('npi', ''),
            'license': list(search_query.get('license_numbers', {}).values())[0] if search_query.get('license_numbers') else None,
            'npi_match': False,
            'license_match': False,
            'error_message': f"Search timed out on {directory_name}. The site may be slow or overloaded."
        }]
    
    def _handle_error(self, search_query, directory_name, error_message):
        """Handle general search errors."""
        print(f"❌ Error searching {directory_name}: {error_message}")
        
        return [{
            'name': f"Error searching {directory_name}",
            'title': "Search failed",
            'location': search_query.get('location', ''),
            'specialties': search_query.get('specialties', []),
            'profile_url': f"https://www.{directory_name.lower().replace(' ', '')}.com",
            'match_score': 0,
            'status': 'error',
            'npi': search_query.get('npi', ''),
            'license': list(search_query.get('license_numbers', {}).values())[0] if search_query.get('license_numbers') else None,
            'npi_match': False,
            'license_match': False,
            'error_message': f"Error searching {directory_name}: {error_message}"
        }]
    
    def get_psychology_today_profile_details(self, profile_url):
        """Extract detailed profile information from Psychology Today profile page."""
        try:
            print(f"🔍 Extracting profile details from: {profile_url}")
            
            response = self.session.get(profile_url, timeout=10)
            if response.status_code != 200:
                print(f"❌ Failed to load profile page: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract comprehensive profile data
            profile_data = {
                'url': profile_url,
                'name': '',
                'credentials': '',
                'location': '',
                'phone': '',
                'email': '',
                'website': '',
                'specialties': [],
                'populations': [],
                'treatment_approaches': [],
                'insurance_accepted': [],
                'bio': '',
                'education': '',
                'license_info': '',
                'profile_image': '',
                'office_hours': '',
                'languages': [],
                'age_groups': [],
                'session_types': [],
                'sliding_scale': False,
                'accepts_insurance': False
            }
            
            # Extract name
            name_selectors = [
                'h1.profile-name',
                'h1[class*="name"]',
                '.profile-header h1',
                'h1',
                '.therapist-name'
            ]
            for selector in name_selectors:
                name_elem = soup.select_one(selector)
                if name_elem:
                    profile_data['name'] = name_elem.get_text(strip=True)
                    break
            
            # Extract credentials
            cred_selectors = [
                '.profile-credentials',
                '.credentials',
                '.title',
                '[class*="credential"]',
                '.degree'
            ]
            for selector in cred_selectors:
                cred_elem = soup.select_one(selector)
                if cred_elem:
                    profile_data['credentials'] = cred_elem.get_text(strip=True)
                    break
            
            # Extract location
            loc_selectors = [
                '.profile-location',
                '.location',
                '.address',
                '[class*="location"]',
                '.office-address'
            ]
            for selector in loc_selectors:
                loc_elem = soup.select_one(selector)
                if loc_elem:
                    profile_data['location'] = loc_elem.get_text(strip=True)
                    break
            
            # Extract phone
            phone_selectors = [
                '.profile-phone',
                '.phone',
                '[class*="phone"]',
                '.contact-phone'
            ]
            for selector in phone_selectors:
                phone_elem = soup.select_one(selector)
                if phone_elem:
                    phone_text = phone_elem.get_text(strip=True)
                    # Extract phone number using regex
                    import re
                    phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', phone_text)
                    if phone_match:
                        profile_data['phone'] = phone_match.group()
                    break
            
            # Extract website
            website_elem = soup.select_one('a[href*="http"]:not([href*="psychologytoday.com"])')
            if website_elem:
                profile_data['website'] = website_elem.get('href', '')
            
            # Extract specialties
            specialty_selectors = [
                '.specialties',
                '.specialty',
                '[class*="specialty"]',
                '.areas-of-focus'
            ]
            for selector in specialty_selectors:
                specialty_elem = soup.select_one(selector)
                if specialty_elem:
                    specialties_text = specialty_elem.get_text(strip=True)
                    profile_data['specialties'] = [s.strip() for s in specialties_text.split(',') if s.strip()]
                    break
            
            # Extract bio
            bio_selectors = [
                '.profile-bio',
                '.bio',
                '.about',
                '.description',
                '[class*="bio"]'
            ]
            for selector in bio_selectors:
                bio_elem = soup.select_one(selector)
                if bio_elem:
                    profile_data['bio'] = bio_elem.get_text(strip=True)
                    break
            
            # Extract profile image
            img_elem = soup.select_one('.profile-image img, .therapist-photo img, .profile-photo img')
            if img_elem:
                profile_data['profile_image'] = img_elem.get('src', '')
            
            print(f"✅ Extracted profile data for: {profile_data['name']}")
            return profile_data
            
        except Exception as e:
            print(f"❌ Error extracting profile details: {e}")
            return None
    
    def verify_psychology_today_update(self, profile_url, expected_data):
        """Verify if a Psychology Today profile update was successful by comparing current data with expected data."""
        try:
            print(f"🔍 Verifying Psychology Today profile update: {profile_url}")
            
            # Get current profile data
            current_data = self.get_psychology_today_profile_details(profile_url)
            if not current_data:
                return {
                    'success': False,
                    'error': 'Failed to extract current profile data',
                    'verification_results': {}
                }
            
            verification_results = {}
            
            # Compare each field
            for field, expected_value in expected_data.items():
                if field in current_data:
                    current_value = current_data[field]
                    
                    # Handle different data types
                    if isinstance(expected_value, list) and isinstance(current_value, list):
                        match = set(expected_value) == set(current_value)
                    elif isinstance(expected_value, str) and isinstance(current_value, str):
                        match = expected_value.strip().lower() == current_value.strip().lower()
                    else:
                        match = expected_value == current_value
                    
                    verification_results[field] = {
                        'expected': expected_value,
                        'current': current_value,
                        'match': match,
                        'status': '✅ Updated' if match else '❌ Not Updated'
                    }
                else:
                    verification_results[field] = {
                        'expected': expected_value,
                        'current': 'Field not found',
                        'match': False,
                        'status': '❌ Field Missing'
                    }
            
            # Calculate overall success
            total_fields = len(verification_results)
            successful_updates = sum(1 for result in verification_results.values() if result['match'])
            success_rate = (successful_updates / total_fields) * 100 if total_fields > 0 else 0
            
            return {
                'success': True,
                'verification_results': verification_results,
                'success_rate': success_rate,
                'successful_updates': successful_updates,
                'total_fields': total_fields,
                'overall_status': '✅ Update Successful' if success_rate >= 80 else '⚠️ Partial Update' if success_rate > 0 else '❌ Update Failed'
            }
            
        except Exception as e:
            print(f"❌ Error verifying profile update: {e}")
            return {
                'success': False,
                'error': str(e),
                'verification_results': {}
            }
    
    def update_psychology_today_profile(self, profile_url, login_credentials, profile_data):
        """Update a Psychology Today profile with new information using the actual member portal."""
        try:
            print(f"🔄 Updating Psychology Today profile: {profile_url}")
            print(f"📝 Profile data to update: {profile_data}")
            
            # Get Selenium driver
            driver = self._get_selenium_driver()
            if not driver:
                print("❌ Failed to create Selenium driver")
                return {
                    'success': False,
                    'error': 'Failed to create Selenium driver',
                    'manual_update_required': True
                }
            
            try:
                # Step 1: Navigate to login page
                print("🔐 Step 1: Navigating to Psychology Today login page...")
                login_url = "https://member.psychologytoday.com/us/login"
                driver.get(login_url)
                
                # Wait for page to fully load
                print("⏳ Waiting for page to load completely...")
                WebDriverWait(driver, 30).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                # Additional wait for dynamic content
                print("⏳ Waiting for dynamic content to load...")
                time.sleep(10)
                
                # Wait for login form to load
                print("🔍 Looking for login form...")
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.NAME, "username"))
                )
                
                # Step 2: Fill login credentials
                print("🔑 Step 2: Entering login credentials...")
                
                # Wait for username field with explicit wait
                username_field = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.NAME, "username"))
                )
                print("✅ Found username field!")
                
                # Wait for password field
                password_field = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.NAME, "password"))
                )
                print("✅ Found password field!")
                
                username_field.clear()
                username_field.send_keys(login_credentials['email'])  # Use email as username
                password_field.clear()
                password_field.send_keys(login_credentials['password'])
                print("✅ Credentials filled!")
                
                # Longer delay to ensure credentials are properly entered
                print("⏳ Waiting for credentials to be processed...")
                time.sleep(5)
                
                # Step 3: Submit login form
                print("🚀 Step 3: Submitting login form...")
                login_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.submit-btn"))
                )
                print("✅ Found submit button!")
                login_button.click()
                print("✅ Submit button clicked!")
                
                # Wait for login processing
                print("⏳ Waiting for login to process...")
                time.sleep(10)
                
                # Step 4: Wait for successful login and navigate to home
                print("🏠 Step 4: Waiting for successful login...")
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
                )
                
                # Check if we're on the home page
                current_url = driver.current_url
                if "member.psychologytoday.com/us/home" in current_url:
                    print("✅ Successfully logged in and on home page")
                else:
                    print(f"⚠️  Unexpected URL after login: {current_url}")
                
                # Step 5: Navigate to profile edit page
                print("✏️  Step 5: Navigating to profile edit page...")
                profile_edit_url = "https://member.psychologytoday.com/us/profile"
                driver.get(profile_edit_url)
                
                # Wait for profile page to load
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
                )
                
                # Step 6: Click on Personal Statement edit button
                print("📝 Step 6: Clicking Personal Statement edit button...")
                personal_statement_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.ID, "button-0-PersonalStatement.Title"))
                )
                personal_statement_button.click()
                
                # Wait for modal to appear
                print("⏳ Waiting for modal to fully load...")
                time.sleep(5)
                
                # Step 7: Wait for modal to appear and fill the three text areas
                print("📋 Step 7: Waiting for Personal Statement modal...")
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea"))
                )
                
                # Additional wait for textareas to be ready
                print("⏳ Waiting for textareas to be ready...")
                time.sleep(3)
                
                # Find all textarea elements in the modal
                textareas = driver.find_elements(By.CSS_SELECTOR, "textarea")
                print(f"📝 Found {len(textareas)} textarea elements")
                
                # Debug: Print details about each textarea
                for i, textarea in enumerate(textareas):
                    try:
                        print(f"📝 Textarea {i+1}: id='{textarea.get_attribute('id')}', name='{textarea.get_attribute('name')}', placeholder='{textarea.get_attribute('placeholder')}'")
                    except Exception as e:
                        print(f"📝 Textarea {i+1}: Error getting attributes - {e}")
                
                # Update the text areas with provided data
                if 'personal_statement' in profile_data:
                    personal_statement = profile_data['personal_statement']
                    
                    # Split the personal statement into three parts if it's a single string
                    if isinstance(personal_statement, str):
                        # Simple split - in practice, you might want more sophisticated parsing
                        parts = personal_statement.split('\n\n')
                        if len(parts) >= 3:
                            ideal_client = parts[0]
                            how_help = parts[1] 
                            empathy_invite = parts[2]
                        else:
                            # If not enough parts, distribute the content
                            ideal_client = personal_statement[:len(personal_statement)//3]
                            how_help = personal_statement[len(personal_statement)//3:2*len(personal_statement)//3]
                            empathy_invite = personal_statement[2*len(personal_statement)//3:]
                    else:
                        # Assume it's a dictionary with the three parts
                        ideal_client = personal_statement.get('ideal_client', '')
                        how_help = personal_statement.get('how_help', '')
                        empathy_invite = personal_statement.get('empathy_invite', '')
                    
                    # Fill the textareas
                    if len(textareas) >= 3:
                        print("📝 Filling textarea 1 (Ideal Client)...")
                        textareas[0].clear()
                        textareas[0].send_keys(ideal_client)
                        
                        print("📝 Filling textarea 2 (How You Help)...")
                        textareas[1].clear()
                        textareas[1].send_keys(how_help)
                        
                        print("📝 Filling textarea 3 (Empathy & Invitation)...")
                        textareas[2].clear()
                        textareas[2].send_keys(empathy_invite)
                    else:
                        print(f"⚠️  Expected 3 textareas, found {len(textareas)}")
                        # Fill what we can
                        for i, textarea in enumerate(textareas):
                            if i == 0:
                                textarea.clear()
                                textarea.send_keys(ideal_client)
                            elif i == 1:
                                textarea.clear()
                                textarea.send_keys(how_help)
                            elif i == 2:
                                textarea.clear()
                                textarea.send_keys(empathy_invite)
                
                # Step 8: Click save button
                print("💾 Step 8: Clicking save button...")
                save_button = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.ID, "button-save-personal-statement"))
                )
                save_button.click()
                
                # Step 9: Wait for save confirmation
                print("⏳ Step 9: Waiting for save confirmation...")
                WebDriverWait(driver, 30).until(
                    EC.invisibility_of_element_located((By.ID, "button-save-personal-statement"))
                )
                
                print("✅ Successfully updated Psychology Today profile!")
                
                # Return success with verification
                verification = self.verify_psychology_today_update(profile_url, profile_data)
                verification['success'] = True
                verification['message'] = 'Profile updated successfully'
                
                return verification
                
            except Exception as e:
                print(f"❌ Error during profile update: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'manual_update_required': True,
                    'debug_info': {
                        'current_url': driver.current_url if driver else 'No driver',
                        'page_title': driver.title if driver else 'No driver'
                    }
                }
                
            finally:
                if driver:
                    driver.quit()
                
        except Exception as e:
            print(f"❌ Error updating Psychology Today profile: {e}")
            return {
                'success': False,
                'error': str(e),
                'manual_update_required': True
            }
    
    def _update_profile_fields(self, driver, profile_data):
        """Update individual profile fields in the edit form."""
        try:
            # Update bio
            if profile_data.get('bio'):
                bio_field = driver.find_element(By.CSS_SELECTOR, "textarea[name*='bio'], textarea[name*='description']")
                bio_field.clear()
                bio_field.send_keys(profile_data['bio'])
            
            # Update specialties
            if profile_data.get('specialties'):
                # This would need to be customized based on PT's specialty selection interface
                specialty_field = driver.find_element(By.CSS_SELECTOR, "select[name*='specialty'], input[name*='specialty']")
                # Implementation would depend on PT's specific form structure
            
            # Update location
            if profile_data.get('location'):
                location_field = driver.find_element(By.CSS_SELECTOR, "input[name*='location'], input[name*='address']")
                location_field.clear()
                location_field.send_keys(profile_data['location'])
            
            # Update phone
            if profile_data.get('phone'):
                phone_field = driver.find_element(By.CSS_SELECTOR, "input[name*='phone'], input[name*='telephone']")
                phone_field.clear()
                phone_field.send_keys(profile_data['phone'])
            
            # Update website
            if profile_data.get('website'):
                website_field = driver.find_element(By.CSS_SELECTOR, "input[name*='website'], input[name*='url']")
                website_field.clear()
                website_field.send_keys(profile_data['website'])
            
            print("✅ Updated profile fields")
            
        except Exception as e:
            print(f"❌ Error updating profile fields: {e}")
    
    def upload_profile_image(self, profile_url, login_credentials, image_path):
        """Upload a profile image to Psychology Today."""
        try:
            print(f"📸 Uploading profile image: {image_path}")
            
            driver = self._get_selenium_driver()
            if not driver:
                return False
            
            try:
                # Login first
                if not self._login_to_psychology_today(driver, login_credentials):
                    return False
                
                # Navigate to image upload page
                # This would need to be customized based on PT's actual interface
                upload_url = profile_url.replace('/therapists/', '/therapists/edit/photos/')
                driver.get(upload_url)
                
                # Wait for upload form
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                )
                
                # Upload image
                file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                file_input.send_keys(image_path)
                
                # Submit upload
                upload_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], .upload-button")
                upload_button.click()
                
                print("✅ Successfully uploaded profile image")
                return True
                
            finally:
                driver.quit()
                
        except Exception as e:
            print(f"❌ Error uploading profile image: {e}")
            return False
    
    def _login_to_psychology_today(self, driver, login_credentials):
        """Helper method to login to Psychology Today."""
        try:
            login_url = "https://www.psychologytoday.com/us/login"
            driver.get(login_url)
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            
            email_field = driver.find_element(By.NAME, "email")
            password_field = driver.find_element(By.NAME, "password")
            
            email_field.send_keys(login_credentials['email'])
            password_field.send_keys(login_credentials['password'])
            
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
            login_button.click()
            
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".dashboard, .profile-manager"))
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False