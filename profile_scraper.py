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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
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
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            print(f"Error creating Chrome driver: {e}")
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