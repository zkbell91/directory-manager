#!/usr/bin/env python3
"""
Test script for Psychology Today automation
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_psychology_today_login():
    """Test the Psychology Today login process step by step."""
    
    print("🔧 Setting up Chrome driver...")
    
    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = None
    
    try:
        # Try to create driver
        print("🚀 Creating Chrome driver...")
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("✅ Chrome driver created successfully!")
        
        # Step 1: Navigate to login page
        print("🔐 Step 1: Navigating to Psychology Today login page...")
        login_url = "https://member.psychologytoday.com/us/login"
        driver.get(login_url)
        
        # Wait for page to load and JavaScript to execute
        print("⏳ Waiting for page to fully load...")
        time.sleep(10)
        
        # Try to wait for any dynamic content
        try:
            WebDriverWait(driver, 15).until(
                lambda d: len(d.find_elements(By.TAG_NAME, "input")) > 0 or len(d.find_elements(By.TAG_NAME, "button")) > 0
            )
            print("✅ Dynamic content loaded!")
        except:
            print("⚠️  No dynamic content detected after waiting")
        
        print(f"📄 Current URL: {driver.current_url}")
        print(f"📄 Page title: {driver.title}")
        
        # Check if we can find the login form
        try:
            # Let's inspect the page structure first
            print("🔍 Inspecting page structure...")
            
            # Get page source
            page_source = driver.page_source
            print(f"📄 Page source length: {len(page_source)} characters")
            
            # Check for iframes first
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            print(f"🖼️  Found {len(iframes)} iframes")
            
            # Check inside the iframe for login form
            if len(iframes) > 0:
                print("🔍 Checking inside iframe for login form...")
                try:
                    # Switch to the iframe
                    driver.switch_to.frame(iframes[0])
                    
                    # Now look for input fields inside the iframe
                    iframe_inputs = driver.find_elements(By.TAG_NAME, "input")
                    print(f"📝 Found {len(iframe_inputs)} input fields inside iframe:")
                    for i, field in enumerate(iframe_inputs):
                        field_type = field.get_attribute("type")
                        field_name = field.get_attribute("name")
                        field_id = field.get_attribute("id")
                        field_placeholder = field.get_attribute("placeholder")
                        field_class = field.get_attribute("class")
                        print(f"  {i+1}. Type: {field_type}, Name: {field_name}, ID: {field_id}, Placeholder: {field_placeholder}, Class: {field_class}")
                    
                    # Look for forms inside iframe
                    iframe_forms = driver.find_elements(By.TAG_NAME, "form")
                    print(f"📋 Found {len(iframe_forms)} forms inside iframe:")
                    for i, form in enumerate(iframe_forms):
                        form_action = form.get_attribute("action")
                        form_method = form.get_attribute("method")
                        form_class = form.get_attribute("class")
                        print(f"  {i+1}. Action: {form_action}, Method: {form_method}, Class: {form_class}")
                    
                    # Look for buttons inside iframe
                    iframe_buttons = driver.find_elements(By.TAG_NAME, "button")
                    print(f"🔘 Found {len(iframe_buttons)} buttons inside iframe:")
                    for i, button in enumerate(iframe_buttons):
                        button_type = button.get_attribute("type")
                        button_text = button.text
                        button_class = button.get_attribute("class")
                        print(f"  {i+1}. Type: {button_type}, Text: '{button_text}', Class: {button_class}")
                    
                    # Switch back to main content
                    driver.switch_to.default_content()
                    
                except Exception as e:
                    print(f"❌ Error checking iframe: {e}")
                    driver.switch_to.default_content()
            
            # Look for any input fields
            input_fields = driver.find_elements(By.TAG_NAME, "input")
            print(f"📝 Found {len(input_fields)} input fields:")
            for i, field in enumerate(input_fields):
                field_type = field.get_attribute("type")
                field_name = field.get_attribute("name")
                field_id = field.get_attribute("id")
                field_placeholder = field.get_attribute("placeholder")
                field_class = field.get_attribute("class")
                print(f"  {i+1}. Type: {field_type}, Name: {field_name}, ID: {field_id}, Placeholder: {field_placeholder}, Class: {field_class}")
            
            # Also look for any elements that might contain forms
            forms = driver.find_elements(By.TAG_NAME, "form")
            print(f"📋 Found {len(forms)} forms:")
            for i, form in enumerate(forms):
                form_action = form.get_attribute("action")
                form_method = form.get_attribute("method")
                form_class = form.get_attribute("class")
                print(f"  {i+1}. Action: {form_action}, Method: {form_method}, Class: {form_class}")
            
            # Look for any buttons
            buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"🔘 Found {len(buttons)} buttons:")
            for i, button in enumerate(buttons):
                button_type = button.get_attribute("type")
                button_text = button.text
                button_class = button.get_attribute("class")
                print(f"  {i+1}. Type: {button_type}, Text: '{button_text}', Class: {button_class}")
            
            # Try different selectors for username field (not email!)
            username_selectors = [
                "input[name='username']",
                "input[type='text']", 
                "input[placeholder*='username']",
                "input[placeholder*='Username']",
                "input[placeholder*='email']",
                "input[placeholder*='Email']",
                "#username",
                "#email",
                ".username",
                ".email"
            ]
            
            username_field = None
            for selector in username_selectors:
                try:
                    username_field = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Found username field with selector: {selector}")
                    break
                except:
                    continue
            
            if not username_field:
                print("❌ Could not find username field with any selector")
                return
            
            # Try different selectors for password field
            password_selectors = [
                "input[name='password']",
                "input[type='password']",
                "input[placeholder*='password']",
                "input[placeholder*='Password']",
                "#password",
                ".password"
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    password_field = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Found password field with selector: {selector}")
                    break
                except:
                    continue
            
            if not password_field:
                print("❌ Could not find password field with any selector")
                return
            
            # Try to fill in test credentials
            print("🔑 Filling in test credentials...")
            username_field.clear()
            username_field.send_keys("test@example.com")
            password_field.clear()
            password_field.send_keys("testpassword")
            
            print("✅ Credentials filled successfully!")
            
            # Look for submit button
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button.submit-btn",
                "button:contains('Log In')",
                "button:contains('Sign In')",
                "button:contains('Login')",
                ".submit-btn",
                "button[class*='submit']"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Found submit button with selector: {selector}")
                    break
                except:
                    continue
            
            if submit_button:
                print("✅ Found submit button!")
                print(f"🔘 Button text: '{submit_button.text}'")
                print(f"🔘 Button class: '{submit_button.get_attribute('class')}'")
            else:
                print("❌ Could not find submit button")
                # Let's try to find any button that might be the submit button
                all_buttons = driver.find_elements(By.TAG_NAME, "button")
                print(f"🔍 Checking all {len(all_buttons)} buttons for submit functionality:")
                for i, button in enumerate(all_buttons):
                    button_text = button.text.strip()
                    button_class = button.get_attribute('class')
                    button_type = button.get_attribute('type')
                    if 'log' in button_text.lower() or 'submit' in button_class.lower() or button_type == 'submit':
                        print(f"  {i+1}. Text: '{button_text}', Class: '{button_class}', Type: '{button_type}' - POTENTIAL SUBMIT BUTTON")
            
            print("🎯 Login form analysis complete!")
            
        except Exception as e:
            print(f"❌ Error finding login form elements: {e}")
            
        # Keep browser open for inspection
        print("🔍 Browser will stay open for 30 seconds for inspection...")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        if driver:
            print("🔚 Closing browser...")
            driver.quit()

if __name__ == "__main__":
    test_psychology_today_login()
