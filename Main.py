from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import json
import re
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from selenium.webdriver import ActionChains

# --- Gmail: Get latest 6-digit code ---
def get_security_code_from_gmail():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=5).execute()
    messages = results.get('messages', [])

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        snippet = msg.get('snippet', '')
        match = re.search(r'\b\d{6}\b', snippet)
        if match:
            return match.group(0)
    return None

def run_automation(data):
    CLIENT_NAME = data["client_name"]
    LEAD_NAME = data["lead_name"]
    LEAD_EMAIL = data["email"]
    BUSINESS_NAME = data["business_name"]
    print(CLIENT_NAME, LEAD_NAME, LEAD_EMAIL, BUSINESS_NAME)

    # --- Setup Headless Chrome ---
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 20)

    # --- Open GHL ---
    driver.get("https://app.gohighlevel.com")

    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[class*="location-switcher__trigger"]'))).click()
    except:
        print("You're in Agency Dashboard — switching to sub-account...")
        switch_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "location-switcher-sidbar-v2"))
        )
        switch_btn.click()
        print("✅ Clicked the location switcher")
        time.sleep(1)

    search_input = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//input[@placeholder="Search for a sub-account"]')
    ))
    search_input.clear()
    search_input.send_keys(CLIENT_NAME)
    time.sleep(1)

    client_result = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, 'div.hl_account')
    ))
    client_result.click()
    print(f"✅ Switched to client: {CLIENT_NAME}")

    search_input = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Search for a sub-account"]'))
    )
    search_input.clear()
    search_input.send_keys(CLIENT_NAME)
    time.sleep(2)

    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Opportunities"))).click()

    funnel_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input.n-base-selection-input')))
    funnel_input.click()
    time.sleep(1)
    funnel_input.send_keys("Interview Funnel")
    time.sleep(1)
    funnel_input.send_keys(Keys.RETURN)
    print("✅ Interview Funnel selected")

    time.sleep(2)
    search_input = wait.until(
        EC.element_to_be_clickable((By.ID, 'list-view-record-search'))
    )
    search_input.click()
    search_input.clear()
    search_input.send_keys(LEAD_NAME)
    print(f"🔍 Searched for lead: {LEAD_NAME}")
    time.sleep(2)

    try:
        print(f"Waiting for lead to show up in results: {LEAD_NAME}")
        lead_card = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-contact-id]'))
        )
        lead_card.click()
        print(f"✅ Clicked lead card: {LEAD_NAME}")

        dropdowns = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.n-base-selection-input'))
        )
        stage_dropdown = dropdowns[1]
        driver.execute_script("arguments[0].scrollIntoView(true);", stage_dropdown)
        driver.execute_script("arguments[0].click();", stage_dropdown)
        time.sleep(1)

        option = wait.until(EC.element_to_be_clickable((
            By.XPATH,
            '//p[text()="Interview Call Booked"]/ancestor::div[contains(@class, "n-base-select-option")]'
        )))
        option.click()
        time.sleep(1)

        update_btn = wait.until(EC.element_to_be_clickable((By.ID, 'CreateUpdateOpportunity')))
        update_btn.click()
        print("✅ Stage updated and saved.")

    except Exception as e:
        print(f"❌ Lead not found. Creating new opportunity for: {LEAD_NAME}")

        add_button = wait.until(EC.element_to_be_clickable((By.ID, 'add-record-btn')))
        add_button.click()
        time.sleep(10)

        name_field = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div#OpportunityModalContactNameInput .n-base-selection-label')))
        name_field.click()
        time.sleep(1)

        input_field = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div#OpportunityModalContactNameInput input.n-base-selection-input')))
        input_field.send_keys(LEAD_NAME)
        time.sleep(0.5)

        create_new = wait.until(EC.element_to_be_clickable(
            (By.XPATH, '//div[@class="n-base-select-menu__action" and @data-action="true"]')
        ))
        create_new.click()
        time.sleep(0.5)
        input_field.send_keys(Keys.RETURN)
        time.sleep(1)

        email_field = wait.until(EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Enter Email"]')))
        email_field.click()
        email_field.send_keys(LEAD_EMAIL)

        business_field = wait.until(
            EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Enter Business Name"]')))
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", business_field)
        time.sleep(0.5)
        business_field.click()
        business_field.send_keys(BUSINESS_NAME)
        time.sleep(0.5)

        stage_dropdowns = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.n-base-selection-input')))
        stage_dropdown = stage_dropdowns[1]
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", stage_dropdown)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", stage_dropdown)
        time.sleep(1)

        option = wait.until(EC.element_to_be_clickable((
            By.XPATH, '//p[text()="Interview Call Booked"]/ancestor::div[contains(@class, "n-base-select-option")]'
        )))
        option.click()
        time.sleep(1)

        create_button = wait.until(EC.element_to_be_clickable((By.ID, "CreateUpdateOpportunity")))
        create_button.click()
        print("✅ New lead created and stage set.")

    print("✅ Done — waiting 3 seconds before closing...")
    time.sleep(5)
    driver.quit()
