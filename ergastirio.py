import os
import sys
import time
import locale
import platform
from datetime import datetime
from dotenv import load_dotenv
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sys.stdout.reconfigure(encoding='utf-8')
options = uc.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')

if platform.system() == "Linux":
    options.binary_location = "/usr/bin/chromium"
    driver = uc.Chrome(options=options, driver_executable_path="/usr/bin/chromedriver")
else:
    driver = uc.Chrome(options=options)

try:
    # Try Linux/Docker format first
    locale.setlocale(locale.LC_TIME, "el_GR.UTF-8")
except locale.Error:
    try:
        # Try Windows/Mac format
        locale.setlocale(locale.LC_TIME, "el_GR")
    except locale.Error:
        # If both fail, print warning but keep running (don't crash)
        print("Warning: Greek locale not found. Using system default.")

load_dotenv()

ECLASS_USERNAME = os.getenv("ECLASS_USERNAME")
ECLASS_PASSWORD = os.getenv("ECLASS_PASSWORD")

print(f"Eclass Username: {ECLASS_USERNAME}\nEclass Password: {ECLASS_PASSWORD}")

mathimata = { 
    "baseis2":"ICE279",
    "pse":"ICE243",
    "espu":"CS152",
    "dp":"CS131",
    "TexnitiNoumosini":"CS210"
}

REFRESH_TIME = 0.3 
mathima = mathimata["TexnitiNoumosini"]
tmhmata = ["ΔΠΖ3 - Πέμπτη 16:00-18:00 - Κ10.022"]

# START_HOUR = 16
# START_MINUTE = 7

# while True:
#     current_time = datetime.now()
#     if current_time.hour >= START_HOUR and current_time.minute >= START_MINUTE:
#         break

#     wait_time = ((START_HOUR - current_time.hour) * 60 + (START_MINUTE - current_time.minute)) * 60 - current_time.second
    
#     if wait_time <= 0:
#         break
    
#     print(f"\033[33mΤο πρόγραμμα θα ξεκινήσει στις {START_HOUR:02d}:{START_MINUTE:02d}. Αναμονή για {wait_time} δευτερόλεπτα...\033[0m")
#     time.sleep(max(wait_time, 1))




def login(): 
    driver.get("https://eclass.uniwa.gr/main/login_form.php")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "uname")))
    
    username_input = driver.find_element(By.NAME, "uname") 
    password_input = driver.find_element(By.NAME, "pass")
    login_button = driver.find_element(By.NAME, "submit")

    username_input.send_keys(ECLASS_USERNAME)
    password_input.send_keys(ECLASS_PASSWORD)
    login_button.click()

def navigate_to_course(id):
    page_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "all_courses")))
    page_button.click()
    
    try:
        course_link = WebDriverWait(driver, 4).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@href='https://eclass.uniwa.gr/courses/{id}/']"))
        )
        course_link.click()
    except:
         print(f"\033[31mΔεν εισαι εγγεγραμμένος σε αυτό το μάθημα\033[0m")
         sys.exit()

    try:
        omades_xristwn = WebDriverWait(driver, 4).until(
            EC.element_to_be_clickable((By.XPATH, f"//a[@href='/modules/group/index.php?course={id}']"))
        )
    except:
        print(f"\033[31mΑυτό το μάθημα δεν έχει εργαστήριο\033[0m")
        sys.exit()
        
    omades_xristwn.click()
    
    try:
        emfanisi_se_lista = WebDriverWait(driver, 4).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn.submitAdminBtn.d-inline-flex")))
        emfanisi_se_lista.click()
    except:
        pass

login()
navigate_to_course(mathima)
print("Scanning...")

cnt = 1
i = 0

def NextCourseExists():
    global i
    i += 1
    return i < len(tmhmata)

while True:
    try:
        row = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//td[(contains(text(), '{tmhmata[i]}') or .//*[contains(text(), '{tmhmata[i]}')])]")
            )
        )
        
        if row.find_elements(By.XPATH, ".//span[contains(@class, 'pull-right label label-success')]"):
             print(f"\033[33mΈχεις εγγραφεί ήδη στο τμήμα {tmhmata[i]}\033[0m")
             break

        if row.find_elements(By.XPATH, ".//span[contains(@class, 'pull-right label label-warning')]"):
             print(f"\033[33mΤο τμήμα {tmhmata[i]} είναι πλήρης\033[0m")
             if not NextCourseExists():
                print("\033[33mΜου τελειωσαν οι επιλογές\033[0m")
                break
             else:
                driver.refresh()
                continue
    except:
            driver.refresh()
            continue
            
    cols = row.find_elements(By.XPATH, ".//ancestor::tr//td") 
    try:
        button = row.find_element(By.XPATH, ".//following-sibling::td//a[contains(@href, 'group_id=')]")  
        button.click()
        current_time_str = datetime.now().strftime("%H:%M:%S")
        print(f"\033[32m[{current_time_str}] Μπήκα με επιτυχία στο εργαστήριο {tmhmata[i]}\033[0m")
        input("Πάτησε ENTER για τερματισμό...")
        break  
    except:
        third_col_text = cols[2].text.strip()
        if third_col_text.endswith("—"):
            print(f"{cnt}. Οι εγγραφές δεν έχουν ανοίξει ακόμα")
            cnt += 1
            time.sleep(REFRESH_TIME) 
            driver.refresh()
            continue 
        else:
            parts = third_col_text.split('/')
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                if parts[0] == parts[1]:
                    if not NextCourseExists():
                        print("\033[33mΜου τελειωσαν οι επιλογές\033[0m")
                        break
                    else:
                        driver.refresh()
                        continue  

try:
    driver.close()
except:
    pass