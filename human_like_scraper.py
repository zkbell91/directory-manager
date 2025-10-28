"""
Human-Like Web Scraper for Directory Management System

Uses human-like mouse movements, clicks, and scrolling to bypass bot detection.
"""

import time
import random
import pyautogui
import pygetwindow as gw
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import math


class HumanLikeScraper:
    """Human-like web scraper that mimics real user behavior."""
    
    def __init__(self):
        # Disable PyAutoGUI failsafe for smoother operation
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.1
        
        # Human-like timing patterns
        self.min_delay = 0.5
        self.max_delay = 2.0
        self.scroll_delay = 0.3
        
    def _get_human_driver(self):
        """Get a Selenium WebDriver configured for human-like behavior."""
        chrome_options = Options()
        
        # Make browser look more human
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Human-like window size
        chrome_options.add_argument('--window-size=1366,768')
        chrome_options.add_argument('--start-maximized')
        
        # Disable images for faster loading (optional)
        # chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to hide automation
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            return driver
        except Exception as e:
            print(f"Error creating Chrome driver: {e}")
            return None
    
    def _human_delay(self, min_time=None, max_time=None):
        """Add human-like random delays."""
        if min_time is None:
            min_time = self.min_delay
        if max_time is None:
            max_time = self.max_delay
            
        delay = random.uniform(min_time, max_time)
        time.sleep(delay)
    
    def _human_mouse_move(self, driver, element):
        """Move mouse to element in a human-like way."""
        try:
            # Get element location
            location = element.location_once_scrolled_into_view
            size = element.size
            
            # Calculate center of element
            center_x = location['x'] + size['width'] // 2
            center_y = location['y'] + size['height'] // 2
            
            # Add some randomness to the target position
            target_x = center_x + random.randint(-5, 5)
            target_y = center_y + random.randint(-5, 5)
            
            # Move mouse in a curved path (human-like)
            self._curved_mouse_move(driver, target_x, target_y)
            
        except Exception as e:
            print(f"Error moving mouse: {e}")
    
    def _curved_mouse_move(self, driver, target_x, target_y):
        """Move mouse in a curved path like a human would."""
        try:
            # Get current mouse position
            current_x, current_y = pyautogui.position()
            
            # Create a curved path with multiple waypoints
            waypoints = self._generate_curved_path(current_x, current_y, target_x, target_y)
            
            # Move through waypoints
            for x, y in waypoints:
                pyautogui.moveTo(x, y, duration=random.uniform(0.05, 0.15))
                time.sleep(random.uniform(0.01, 0.03))
                
        except Exception as e:
            print(f"Error in curved mouse move: {e}")
    
    def _generate_curved_path(self, start_x, start_y, end_x, end_y, num_points=5):
        """Generate a curved path between two points."""
        waypoints = []
        
        for i in range(num_points + 1):
            t = i / num_points
            
            # Linear interpolation
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            
            # Add some curve (sine wave)
            curve_offset = math.sin(t * math.pi) * random.randint(10, 30)
            x += curve_offset * random.choice([-1, 1])
            y += curve_offset * random.choice([-1, 1])
            
            waypoints.append((int(x), int(y)))
        
        return waypoints
    
    def _human_click(self, driver, element):
        """Perform a human-like click on an element."""
        try:
            # Move mouse to element first
            self._human_mouse_move(driver, element)
            self._human_delay(0.1, 0.3)
            
            # Click with slight randomness
            actions = ActionChains(driver)
            actions.move_to_element(element)
            
            # Add small random offset
            offset_x = random.randint(-2, 2)
            offset_y = random.randint(-2, 2)
            actions.move_by_offset(offset_x, offset_y)
            
            # Human-like click timing
            actions.pause(random.uniform(0.05, 0.15))
            actions.click()
            actions.perform()
            
            # Post-click delay
            self._human_delay(0.2, 0.5)
            
        except Exception as e:
            print(f"Error clicking element: {e}")
    
    def _human_scroll(self, driver, direction='down', amount=3):
        """Perform human-like scrolling."""
        try:
            for _ in range(amount):
                # Random scroll amount
                scroll_amount = random.randint(200, 400)
                
                if direction == 'down':
                    driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                else:
                    driver.execute_script(f"window.scrollBy(0, -{scroll_amount});")
                
                # Human-like pause between scrolls
                time.sleep(random.uniform(0.3, 0.8))
                
        except Exception as e:
            print(f"Error scrolling: {e}")
    
    def _human_type(self, element, text, clear_first=True):
        """Type text in a human-like manner."""
        try:
            if clear_first:
                element.clear()
            
            # Click on element first
            element.click()
            self._human_delay(0.1, 0.3)
            
            # Type with human-like timing
            for char in text:
                element.send_keys(char)
                # Random delay between keystrokes
                time.sleep(random.uniform(0.05, 0.15))
                
        except Exception as e:
            print(f"Error typing: {e}")
    
    def _simulate_human_behavior(self, driver):
        """Simulate general human browsing behavior."""
        try:
            # Random mouse movements
            for _ in range(random.randint(2, 5)):
                x = random.randint(100, 1200)
                y = random.randint(100, 600)
                pyautogui.moveTo(x, y, duration=random.uniform(0.5, 1.5))
                time.sleep(random.uniform(0.2, 0.8))
            
            # Random scroll
            if random.random() < 0.3:  # 30% chance
                self._human_scroll(driver, 'down', random.randint(1, 3))
            
            # Random pause
            self._human_delay(1.0, 3.0)
            
        except Exception as e:
            print(f"Error in human behavior simulation: {e}")
    
    def search_psychology_today_human_like(self, search_query):
        """Search Psychology Today using human-like interactions."""
        driver = None
        try:
            print(f"🤖 Starting human-like search for: {search_query.get('name', '')}")
            
            driver = self._get_human_driver()
            if not driver:
                return self._handle_error(search_query, "Psychology Today", "Could not create driver")
            
            # Navigate to Psychology Today
            base_url = "https://www.psychologytoday.com/us/therapists"
            print(f"🌐 Navigating to Psychology Today...")
            driver.get(base_url)
            
            # Simulate human behavior on landing page
            self._simulate_human_behavior(driver)
            
            # Check if we got blocked
            if "403" in driver.page_source or "Forbidden" in driver.page_source:
                print("❌ Blocked by Psychology Today (403 Forbidden)")
                return self._handle_blocked_search(search_query, "Psychology Today")
            
            # Look for search form
            try:
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Find search input field
                search_input = None
                search_selectors = [
                    "input[name='search']",
                    "input[placeholder*='search']",
                    "input[type='text']",
                    "#search",
                    ".search-input"
                ]
                
                for selector in search_selectors:
                    try:
                        search_input = driver.find_element(By.CSS_SELECTOR, selector)
                        if search_input.is_displayed():
                            break
                    except NoSuchElementException:
                        continue
                
                if not search_input:
                    print("❌ Could not find search input field")
                    return self._handle_error(search_query, "Psychology Today", "Search input not found")
                
                # Human-like interaction with search
                print("🔍 Interacting with search field...")
                
                # Move to search field
                self._human_mouse_move(driver, search_input)
                self._human_delay(0.5, 1.0)
                
                # Click on search field
                self._human_click(driver, search_input)
                
                # Type search query
                self._human_type(search_input, search_query.get('name', ''))
                
                # Look for location field
                location_input = None
                location_selectors = [
                    "input[name='location']",
                    "input[placeholder*='location']",
                    "input[placeholder*='city']",
                    "input[placeholder*='zip']"
                ]
                
                for selector in location_selectors:
                    try:
                        location_input = driver.find_element(By.CSS_SELECTOR, selector)
                        if location_input.is_displayed():
                            break
                    except NoSuchElementException:
                        continue
                
                if location_input:
                    print("📍 Setting location...")
                    self._human_click(driver, location_input)
                    self._human_type(location_input, search_query.get('location', 'Jacksonville, FL'))
                
                # Look for search button
                search_button = None
                button_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:contains('Search')",
                    ".search-button",
                    "#search-button"
                ]
                
                for selector in button_selectors:
                    try:
                        search_button = driver.find_element(By.CSS_SELECTOR, selector)
                        if search_button.is_displayed():
                            break
                    except NoSuchElementException:
                        continue
                
                if search_button:
                    print("🔍 Clicking search button...")
                    self._human_click(driver, search_button)
                else:
                    # Try pressing Enter
                    from selenium.webdriver.common.keys import Keys
                    search_input.send_keys(Keys.RETURN)
                
                # Wait for results
                print("⏳ Waiting for search results...")
                self._human_delay(2.0, 4.0)
                
                # Simulate human behavior while waiting
                self._simulate_human_behavior(driver)
                
                # Look for results
                results = self._extract_search_results(driver, search_query)
                
                driver.quit()
                return results
                
            except TimeoutException:
                print("❌ Timeout waiting for search form")
                return self._handle_timeout(search_query, "Psychology Today")
            except Exception as e:
                print(f"❌ Error during search: {e}")
                return self._handle_error(search_query, "Psychology Today", str(e))
                
        except Exception as e:
            print(f"❌ Error in human-like search: {e}")
            if driver:
                driver.quit()
            return self._handle_error(search_query, "Psychology Today", str(e))
    
    def _extract_search_results(self, driver, search_query):
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
                ".search-result"
            ]
            
            profile_elements = []
            for selector in profile_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        profile_elements.extend(elements)
                        break
                except:
                    continue
            
            print(f"📋 Found {len(profile_elements)} potential profile elements")
            
            for element in profile_elements[:5]:  # Limit to first 5
                try:
                    # Extract profile information
                    profile_data = self._extract_profile_data(element, search_query)
                    if profile_data:
                        profiles.append(profile_data)
                        
                except Exception as e:
                    print(f"Error extracting profile: {e}")
                    continue
            
            return profiles
            
        except Exception as e:
            print(f"Error extracting results: {e}")
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
                ".profile-name a"
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
            
            # Extract other details
            credentials = ""
            try:
                cred_elem = element.find_element(By.CSS_SELECTOR, ".credentials, .title, .profile-credentials")
                credentials = cred_elem.text.strip()
            except NoSuchElementException:
                pass
            
            location = search_query.get('location', '')
            try:
                loc_elem = element.find_element(By.CSS_SELECTOR, ".location, .profile-location, .address")
                location = loc_elem.text.strip()
            except NoSuchElementException:
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
            print(f"Error extracting profile data: {e}")
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
