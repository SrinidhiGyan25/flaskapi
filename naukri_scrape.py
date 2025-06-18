import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random

def setup_chrome_driver():
    """Setup Chrome driver for Render deployment"""
    options = Options()
    
    # Essential headless options for server deployment
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-plugins')
    options.add_argument('--disable-images')  # Faster loading
    options.add_argument('--disable-javascript')  # If not needed
    
    # Window and memory settings
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--memory-pressure-off')
    options.add_argument('--single-process')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-renderer-backgrounding')
    
    # Anti-detection measures (replace undetected-chromedriver)
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Proxy settings (optional)
    # options.add_argument('--proxy-server=http://proxy:port')
    
    try:
        # Try to create driver with system ChromeDriver
        driver = webdriver.Chrome(options=options)
        
        # Additional anti-detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    except Exception as e:
        print(f"❌ Chrome setup failed: {e}")
        return None

def get_naukri_jobs(query, pages=1):
    """Scrape Naukri jobs with proper error handling for Render"""
    driver = setup_chrome_driver()
    if not driver:
        print("❌ Failed to setup Chrome driver")
        return pd.DataFrame()
    
    wait = WebDriverWait(driver, 20)  # Increased timeout
    job_data = []
    
    try:
        for page in range(1, pages + 1):
            url = f"https://www.naukri.com/{query.replace(' ', '-')}-jobs-{page}?k={query}"
            print(f"\n🔍 Scraping page {page}: {url}")
            
            try:
                driver.get(url)
                
                # Wait for page to load completely
                time.sleep(random.randint(5, 8))
                
                # Check if blocked or captcha
                if "blocked" in driver.page_source.lower() or "captcha" in driver.page_source.lower():
                    print("❌ Blocked or captcha detected")
                    break
                
                # Wait for job cards to load
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "srp-jobtuple-wrapper")]')))
                except:
                    print(f"⚠️ No job cards found on page {page}")
                    continue
                
                # Find job cards
                job_cards = driver.find_elements(By.XPATH, '//div[contains(@class, "srp-jobtuple-wrapper")]')
                print(f"📋 Found {len(job_cards)} job cards on page {page}")
                
                if len(job_cards) == 0:
                    print("⚠️ No job cards found, possibly blocked")
                    break
                
                # Extract job data
                for i, card in enumerate(job_cards):
                    try:
                        # Extract job title
                        try:
                            title = card.find_element(By.XPATH, './/a[contains(@class, "title")]').text.strip()
                        except:
                            title = "N/A"
                        
                        # Extract location
                        try:
                            location = card.find_element(By.XPATH, './/span[contains(@class, "locWdth")]').text.strip()
                        except:
                            location = "N/A"
                        
                        # Extract experience
                        try:
                            experience = card.find_element(By.XPATH, './/span[contains(@class, "expwdth")]').text.strip()
                        except:
                            experience = "N/A"
                        
                        # Extract description
                        try:
                            description = card.find_element(By.XPATH, './/span[contains(@class, "job-desc")]').text.strip()
                        except:
                            description = "N/A"
                        
                        # Extract job URL
                        try:
                            title_element = card.find_element(By.XPATH, './/a[contains(@class, "title")]')
                            job_url = title_element.get_attribute('href')
                        except:
                            job_url = "N/A"
                        
                        # Only add if we have at least title and location
                        if title != "N/A" and location != "N/A":
                            job_data.append({
                                "Job Title": title,
                                "Location": location,
                                "Experience": experience,
                                "Description": description,
                                "Job URL": job_url
                            })
                            print(f"✅ Extracted job {i+1}: {title[:50]}...")
                        
                    except Exception as e:
                        print(f"⚠️ Error extracting job {i+1}: {e}")
                        continue
                
                # Random delay between pages
                if page < pages:
                    delay = random.randint(8, 15)
                    print(f"⏱️ Waiting {delay} seconds before next page...")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"❌ Error on page {page}: {e}")
                continue
                
    except KeyboardInterrupt:
        print("⏹️ Scraping interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        driver.quit()
        print(f"🔒 Browser closed")
    
    print(f"\n📊 Total jobs scraped: {len(job_data)}")
    return pd.DataFrame(job_data)

def test_chrome_setup():
    """Test function to verify Chrome setup"""
    print("🧪 Testing Chrome setup...")
    driver = setup_chrome_driver()
    
    if driver:
        try:
            driver.get("https://httpbin.org/user-agent")
            print("✅ Chrome driver working!")
            print(f"User-Agent: {driver.find_element(By.TAG_NAME, 'body').text}")
            return True
        except Exception as e:
            print(f"❌ Chrome test failed: {e}")
            return False
        finally:
            driver.quit()
    else:
        print("❌ Chrome driver setup failed")
        return False

if __name__ == "__main__":
    # Test Chrome setup first
    if not test_chrome_setup():
        print("❌ Chrome setup test failed. Fix Chrome installation first.")
        exit(1)
    
    # Main scraping
    query = input("Enter job role (e.g., 'Data Scientist'): ").strip()
    pages = int(input("Enter number of pages (e.g., 2): ").strip())
    
    print(f"\n🚀 Starting scrape for '{query}' ({pages} pages)...")
    df = get_naukri_jobs(query, pages=pages)
    
    if df.empty:
        print("❌ No jobs scraped. Possible issues:")
        print("  - Website blocking/captcha")
        print("  - Chrome driver not working")
        print("  - Network issues")
        print("  - Search query returned no results")
    else:
        filename = f"{query.replace(' ', '_')}_jobs.csv"
        df.to_csv(filename, index=False)
        print(f"✅ Successfully saved {len(df)} jobs to {filename}")
        
        # Show sample data
        print(f"\n📋 Sample jobs:")
        for i, job in df.head(3).iterrows():
            print(f"  {i+1}. {job['Job Title']} - {job['Location']}")