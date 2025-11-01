#!/usr/bin/env python3
"""
Minimal Psychology Today login test
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def test_login():
    """Test Psychology Today login with real credentials."""
    
    print("🔧 Setting up Chrome driver...")
    
    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = None
    
    try:
        # Create driver
        print("🚀 Creating Chrome driver...")
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Chrome driver created successfully!")
        
        # Navigate to login page
        print("🔐 Navigating to Psychology Today login page...")
        login_url = "https://member.psychologytoday.com/us/login"
        driver.get(login_url)
        
        # Wait for page to load
        print("⏳ Waiting for page to load...")
        time.sleep(5)
        
        print(f"📄 Current URL: {driver.current_url}")
        print(f"📄 Page title: {driver.title}")
        
        # Find and fill login form
        print("🔍 Looking for login form...")
        
        # Wait for username field
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        print("✅ Found username field!")
        
        # Wait for password field
        password_field = driver.find_element(By.NAME, "password")
        print("✅ Found password field!")
        
        # Fill credentials
        print("🔑 Filling in credentials...")
        username_field.clear()
        username_field.send_keys("coreybussiere")
        
        password_field.clear()
        password_field.send_keys("Mosa1cm1nds!")
        
        print("✅ Credentials filled!")
        
        # Find and click submit button
        print("🔍 Looking for submit button...")
        submit_button = driver.find_element(By.CSS_SELECTOR, "button.submit-btn")
        print("✅ Found submit button!")
        
        # Click submit
        print("🚀 Clicking submit button...")
        submit_button.click()
        
        # Wait for response
        print("⏳ Waiting for login response...")
        time.sleep(5)
        
        print(f"📄 After login URL: {driver.current_url}")
        print(f"📄 After login title: {driver.title}")
        
        # Check if login was successful
        if "home" in driver.current_url.lower() or "profile" in driver.current_url.lower():
            print("🎉 Login successful!")
        else:
            print("❌ Login may have failed - unexpected URL")
        
        # Keep browser open for inspection
        print("🔍 Browser will stay open for 30 seconds for inspection...")
        time.sleep(30)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            print("🔚 Closing browser...")
            driver.quit()

if __name__ == "__main__":
    test_login()


