"""
Undetected Web Scraper for Directory Management System

Uses undetected-chromedriver to bypass sophisticated bot detection systems.
"""

import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import math


class UndetectedScraper:
    """Undetected web scraper that bypasses bot detection."""
    
    def __init__(self):
        self.driver = None
        
    def _get_undetected_driver(self):
        """Get an undetected Chrome driver."""
        try:
            options = uc.ChromeOptions()
            
            # Advanced stealth options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # Human-like window size
            options.add_argument('--window-size=1366,768')
            
            # Create undetected driver
            driver = uc.Chrome(options=options, version_main=None)
            
            # Additional stealth measures
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
            driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})")
            
            return driver
            
        except Exception as e:
            print(f"Error creating undetected driver: {e}")
            return None
    
    def _human_delay(self, min_time=0.5, max_time=2.0):
        """Add human-like random delays."""
        delay = random.uniform(min_time, max_time)
        time.sleep(delay)
    
    def _simulate_human_typing(self, element, text):
        """Type text with human-like timing."""
        try:
            element.clear()
            element.click()
            self._human_delay(0.1, 0.3)
            
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))
                
        except Exception as e:
            print(f"Error typing: {e}")
    
    def _simulate_human_scroll(self, driver, direction='down', amount=3):
        """Simulate human-like scrolling."""
        try:
            for _ in range(amount):
                scroll_amount = random.randint(200, 400)
                
                if direction == 'down':
                    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                else:
                    driver.execute_script(f"window.scrollBy(0, -{scroll_amount});")
                
                time.sleep(random.uniform(0.3, 0.8))
                
        except Exception as e:
            print(f"Error scrolling: {e}")
    
    def _simulate_mouse_movement(self, driver):
        """Simulate random mouse movements."""
        try:
            # Get window size
            size = driver.get_window_size()
            width = size['width']
            height = size['height']
            
            # Random mouse movements
            for _ in range(random.randint(2, 5)):
                x = random.randint(100, width - 100)
                y = random.randint(100, height - 100)
                
                # Move mouse using JavaScript
                driver.execute_script(f"""
                    var event = new MouseEvent('mousemove', {{
                        'view': window,
                        'bubbles': true,
                        'cancelable': true,
                        'clientX': {x},
                        'clientY': {y}
                    }});
                    document.dispatchEvent(event);
                """)
                
                time.sleep(random.uniform(0.2, 0.8))
                
        except Exception as e:
            print(f"Error simulating mouse movement: {e}")
    
    def search_psychology_today_undetected(self, search_query):
        """Search Psychology Today using undetected browser."""
        try:
            print(f"🕵️ Starting undetected search for: {search_query.get('name', '')}")
            
            self.driver = self._get_undetected_driver()
            if not self.driver:
                return self._handle_error(search_query, "Psychology Today", "Could not create undetected driver")
            
            # Navigate to Psychology Today
            base_url = "https://www.psychologytoday.com/us/therapists"
            print(f"🌐 Navigating to Psychology Today...")
            self.driver.get(base_url)
            
            # Simulate human behavior
            self._simulate_mouse_movement(self.driver)
            self._human_delay(2.0, 4.0)
            
            # Check if we got blocked
            if "403" in self.driver.page_source or "Forbidden" in self.driver.page_source:
                print("❌ Still blocked by Psychology Today")
                return self._handle_blocked_search(search_query, "Psychology Today")
            
            print("✅ Successfully bypassed initial detection!")
            
            # Look for search form
            try:
                # Wait for page to load
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Find search input field
                search_input = None
                search_selectors = [
                    "input[name='search']",
                    "input[placeholder*='search']",
                    "input[placeholder*='therapist']",
                    "input[type='text']",
                    "#search",
                    ".search-input",
                    "input[class*='search']"
                ]
                
                for selector in search_selectors:
                    try:
                        search_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if search_input.is_displayed():
                            print(f"✅ Found search input with selector: {selector}")
                        break
                    except NoSuchElementException:
                        continue
                
                if not search_input:
                    print("❌ Could not find search input field")
                    return self._handle_error(search_query, "Psychology Today", "Search input not found")
                
                # Human-like interaction with search
                print("🔍 Interacting with search field...")
                
                # Scroll to search field
                self.driver.execute_script("arguments[0].scrollIntoView(true);", search_input)
                self._human_delay(0.5, 1.0)
                
                # Click on search field
                search_input.click()
                self._human_delay(0.3, 0.8)
                
                # Type search query
                self._simulate_human_typing(search_input, search_query.get('name', ''))
                
                # Look for location field
                location_input = None
                location_selectors = [
                    "input[name='location']",
                    "input[placeholder*='location']",
                    "input[placeholder*='city']",
                    "input[placeholder*='zip']",
                    "input[placeholder*='address']"
                ]
                
                for selector in location_selectors:
                    try:
                        location_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if location_input.is_displayed():
                            print(f"✅ Found location input with selector: {selector}")
                            break
                    except NoSuchElementException:
                        continue
                
                if location_input:
                    print("📍 Setting location...")
                    location_input.click()
                    self._human_delay(0.2, 0.5)
                    self._simulate_human_typing(location_input, search_query.get('location', 'Jacksonville, FL'))
                
                # Look for search button
                search_button = None
                button_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:contains('Search')",
                    ".search-button",
                    "#search-button",
                    "button[class*='search']",
                    "input[value*='Search']"
                ]
                
                for selector in button_selectors:
                    try:
                        search_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if search_button.is_displayed():
                            print(f"✅ Found search button with selector: {selector}")
                            break
                    except NoSuchElementException:
                        continue
                
                if search_button:
                    print("🔍 Clicking search button...")
                    search_button.click()
                else:
                    # Try pressing Enter
                    print("🔍 Pressing Enter to search...")
                    search_input.send_keys(Keys.RETURN)
                
                # Wait for results
                print("⏳ Waiting for search results...")
                self._human_delay(3.0, 5.0)
                
                # Simulate human behavior while waiting
                self._simulate_mouse_movement(self.driver)
                self._simulate_human_scroll(self.driver, 'down', random.randint(1, 3))
                
                # Look for results
                results = self._extract_search_results(search_query)
                
                self.driver.quit()
                return results
                
            except TimeoutException:
                print("❌ Timeout waiting for search form")
                return self._handle_timeout(search_query, "Psychology Today")
            except Exception as e:
                print(f"❌ Error during search: {e}")
                return self._handle_error(search_query, "Psychology Today", str(e))
                
        except Exception as e:
            print(f"❌ Error in undetected search: {e}")
            if self.driver:
                self.driver.quit()
            return self._handle_error(search_query, "Psychology Today", str(e))
    
    def _extract_search_results(self, search_query):
        """Extract search results from the page."""
        try:
            profiles = []
            
            # Look for profile elements with multiple selectors
            profile_selectors = [
                ".profile-card",
                ".profile",
                ".therapist-card",
                "[class*='profile']",
                "[class*='therapist']",
                ".result-item",
                ".search-result",
                ".listing",
                ".provider-card"
            ]
            
            profile_elements = []
            for selector in profile_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"✅ Found {len(elements)} elements with selector: {selector}")
                        profile_elements.extend(elements)
                        break
                except:
                    continue
            
            if not profile_elements:
                print("❌ No profile elements found")
                return self._handle_no_results(search_query, "Psychology Today")
            
            print(f"📋 Processing {len(profile_elements)} profile elements")
            
            for i, element in enumerate(profile_elements[:5]):  # Limit to first 5
                try:
                    print(f"🔍 Processing profile {i+1}...")
                    
                    # Extract profile information
                    profile_data = self._extract_profile_data(element, search_query)
                    if profile_data:
                        profiles.append(profile_data)
                        print(f"✅ Extracted: {profile_data['name']}")
                    else:
                        print(f"❌ Could not extract data from profile {i+1}")
                        
                except Exception as e:
                    print(f"❌ Error extracting profile {i+1}: {e}")
                    continue
            
            print(f"✅ Successfully extracted {len(profiles)} profiles")
            return profiles
            
        except Exception as e:
            print(f"❌ Error extracting results: {e}")
            return []
    
    def _extract_profile_data(self, element, search_query):
        """Extract data from a profile element."""
        try:
            # Find name link
            name_elem = None
            name_selectors = [
                "a[href*='profile']",
                "h3 a",
                "h2 a",
                "h4 a",
                ".name a",
                ".profile-name a",
                "a[class*='name']",
                "a[class*='profile']"
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
            
            if not name_elem:
                return None
            
            name = name_elem.text.strip()
            profile_url = name_elem.get_attribute('href')
            
            if not name or not profile_url:
                return None
            
            # Extract other details
            credentials = ""
            try:
                cred_selectors = [".credentials", ".title", ".profile-credentials", ".degree", ".license"]
                for selector in cred_selectors:
                    try:
                        cred_elem = element.find_element(By.CSS_SELECTOR, selector)
                        credentials = cred_elem.text.strip()
                        break
                    except NoSuchElementException:
                        continue
            except:
                pass
            
            location = search_query.get('location', '')
            try:
                loc_selectors = [".location", ".profile-location", ".address", ".city", ".zip"]
                for selector in loc_selectors:
                    try:
                        loc_elem = element.find_element(By.CSS_SELECTOR, selector)
                        location = loc_elem.text.strip()
                        break
                    except NoSuchElementException:
                        continue
            except:
                pass
            
            # Calculate match score
            match_score = self._calculate_match_score(search_query, {
                'name': name,
                'credentials': credentials,
                'location': location,
                'specialties': search_query.get('specialties', [])
            })
            
            return {
                'name': name,
                'title': credentials,
                'location': location,
                'specialties': search_query.get('specialties', []),
                'profile_url': profile_url,
                'match_score': match_score,
                'status': 'exists_unmanaged',
                'npi': search_query.get('npi', ''),
                'license': list(search_query.get('license_numbers', {}).values())[0] if search_query.get('license_numbers') else None,
                'npi_match': False,
                'license_match': False
            }
            
        except Exception as e:
            print(f"❌ Error extracting profile data: {e}")
            return None
    
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
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        if not words1 or not words2:
            return 0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0
    
    def _location_similarity(self, location1, location2):
        """Calculate similarity between two locations."""
        words1 = set(location1.split())
        words2 = set(location2.split())
        
        if not words1 or not words2:
            return 0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0
    
    def _handle_blocked_search(self, search_query, directory_name):
        """Handle when search is blocked by anti-bot protection."""
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
