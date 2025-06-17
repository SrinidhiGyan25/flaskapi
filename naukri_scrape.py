import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import random


def get_naukri_jobs(query, pages=1):
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    driver = uc.Chrome(version_main=121, options=options)
    driver.minimize_window()
    wait = WebDriverWait(driver, 15)
    job_data = []

    for page in range(1, pages + 1):
        url = f"https://www.naukri.com/{query.replace(' ', '-')}-jobs-{page}?k={query}"
        print(f"\nVisiting: {url}")
        driver.get(url)

        try:
            wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "srp-jobtuple-wrapper")]')))
        except:
            print("No jobs")
            continue

        job_cards = driver.find_elements(By.XPATH, '//div[contains(@class, "srp-jobtuple-wrapper")]')
        print(f"Found {len(job_cards)} job cards")

        for card in job_cards:
            try:
                title = card.find_element(By.XPATH, './/a[contains(@class, "title")]').text.strip()
                location = card.find_element(By.XPATH, './/span[contains(@class, "locWdth")]').text.strip()
                experience = card.find_element(By.XPATH, './/span[contains(@class, "expwdth")]').text.strip()
                description = card.find_element(By.XPATH, './/span[contains(@class, "job-desc")]').text.strip()
                title_element = card.find_element(By.XPATH, './/a[contains(@class, "title")]')
                job_url = title_element.get_attribute('href')
                job_data.append({
                    "Job Title": title,
                    "Location": location,
                    "Experience": experience,
                    "Description": description,
                    "Job URL": job_url
                })
            except Exception as e:
                print(f"Skipping a card: {e}")

        time.sleep(random.randint(3, 6))  # anti-bot delay

    driver.quit()
    return pd.DataFrame(job_data)

if __name__ == "__main__":
    query = input("Enter job role (e.g., 'PCB Design'): ")
    df = get_naukri_jobs(query, pages=2)

    if df.empty:
        print("No jobs scraped. You may be blocked again.")
    else:
        filename = f"{query.replace(' ', '_')}_jobs.csv"
        df.to_csv(filename, index=False)
        print(f"\nSaved {len(df)} jobs to {filename}")
