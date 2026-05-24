import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Replace with your actual Google Form URL
FORM_URL = "https://docs.google.com/forms/"

def fill_google_form():
    # Initialize the Chrome driver (Selenium 4 handles driver binaries automatically)
    driver = webdriver.Chrome()
    
    try:
        driver.get(FORM_URL)
        print("Page opened. Starting multi-page automation...")
        
        page_number = 1
        
        while True:
            print(f"\n--- Processing Page {page_number} ---")
            
            # Wait for the main structural form element to load on the current page
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//form[@id='mG61Hd']"))
            )
            time.sleep(1.5)  # Let elements fully render after transition animations
            
            # 1. Gather all question container blocks visible on this page
            question_cards = driver.find_elements(By.XPATH, "//div[@role='listitem'] | //div[contains(@class, 'Qr7Oae')]")
            print(f"Found {len(question_cards)} base question blocks on this page.")
            
            # 2. Loop through and process each question card
            for index, card in enumerate(question_cards, start=1):
                # Look for explicit radiogroup roles inside the card (used in advanced layout versions)
                radio_groups = card.find_elements(By.XPATH, ".//div[@role='radiogroup']")
                
                # If nested radiogroups exist, evaluate them individually. Otherwise, evaluate the card itself.
                targets = radio_groups if radio_groups else [card]
                
                for target in targets:
                    options = target.find_elements(By.XPATH, ".//div[@role='radio']")
                    
                    if options:
                        filtered_options = []
                        for opt in options:
                            data_value = opt.get_attribute("data-value")
                            aria_label = opt.get_attribute("aria-label")
                            opt_text = opt.text.lower() if opt.text else ""
                            
                            # REMOVE 'OTHER' OPTION: Skip if it matches Google's internal naming or labels
                            if (data_value == "__other_option__" or data_value == "Doctor Falsafah" or
                                "other" in opt_text or 
                                (aria_label and "other" in aria_label.lower())):
                                continue
                            
                            filtered_options.append(opt)
                        
                        # Click a random valid selection from the filtered objective choices
                        if filtered_options:
                            chosen_option = random.choice(filtered_options)
                            
                            # Scroll smoothly into view to prevent element click interceptions
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", chosen_option)
                            time.sleep(0.1)
                            
                            chosen_option.click()
                            print(f"Question block {index}: Selected a standard objective option.")
            
            # 3. Page Navigation (Next page vs. Submit)
            nav_buttons = driver.find_elements(By.XPATH, "//div[contains(@class, 'lRwqcd')]//div[@role='button']")
            
            if not nav_buttons:
                print("Critical Error: Could not find any navigation control buttons at the bottom.")
                break
                
            # The action button moving you forward (Next/Submit) is always the last item in the control row
            primary_button = nav_buttons[-1]
            button_text = primary_button.text.strip().lower()
            
            # Check for international variations of final step submissions
            is_submit = any(word in button_text for word in ["submit", "kirim", "enviar", "finish", "done"])
            
            # Scroll to navigation controls safely
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", primary_button)
            time.sleep(0.5)
            
            if is_submit:
                primary_button.click()
                print("Final page reached! Clicked the Submit button.")
                time.sleep(3)  # Let the confirmation page finish rendering
                break  # Complete execution
            else:
                primary_button.click()
                print(f"Clicked 'Next' button. Advancing past Page {page_number}...")
                page_number += 1
                time.sleep(0.5)  # Critical cushion to allow the DOM to clear and load the next page
                
    except Exception as e:
        print(f"\nAn error occurred during automation: {e}")
        
    finally:
        print("Closing the browser window.")
        driver.quit()

if __name__ == "__main__":
    i = 0
    while i < 80:  # Adjust the loop condition as needed
        fill_google_form()
        i += 1
        print(f"Completed iteration {i}. Restarting the form filling process...\n")
        time.sleep(2)  # Short break between iterations to avoid overwhelming the server