from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import locale
import random

driver = webdriver.Chrome()
SLEEP_TIME = 2
ECLASS_USERNAME ="UsernameExample"
ECLASS_PASSWORD = "PasswordExample"
MESSAGE = "εδω κυριεεεε"
locale.setlocale(locale.LC_TIME, "el_GR.utf8") 
def login(): 
    driver.get("https://eclass.uniwa.gr")
    driver.maximize_window()
    username_input = driver.find_element(By.NAME, "uname") 
    password_input = driver.find_element(By.NAME, "pass")
    login_button = driver.find_element(By.NAME, "submit")

    username_input.send_keys(ECLASS_USERNAME)
    password_input.send_keys(ECLASS_PASSWORD)
    login_button.click()

def navigate_to_course():
    page_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CLASS_NAME, "all_courses")) # Παταει το κουμπι με όνομα Κλάσης all_courses που εμφανίζει ολα τα μαθηματα
    )
    page_button.click()

    next_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//a[@href='https://eclass.uniwa.gr/courses/ICE271/']")) # Παταει το κουμπι με το αντοισιχο Path που επιλεγει το μαθημα 271, μπορειτε να το αλλαξετε με βαση το δικο σας μαθημα.
    )
    next_button.click()

    next_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//a[@href='/modules/work/?course=ICE271']"))# Παταει το κουμπι cource του αντιστοιχου μαθηματος που ειναι ο καταλογος εργασίες
    )
    next_button.click()


try:
    login()
    navigate_to_course()
    
    wait = WebDriverWait(driver, 5)
    rows = wait.until(
        EC.presence_of_all_elements_located((By.XPATH, "//table[@id='assignment_table']//tbody/tr"))) 

    current_date = datetime.now()
    task_titles = [
        current_date.strftime("%d/%m/%Y"),  
        f"{current_date.day}/{current_date.month}/{current_date.year % 100:02d}",  
        current_date.strftime("%d-%m-%Y"),  
        f"{current_date.day}-{current_date.month}-{current_date.year % 100:02d}",  
        f"{current_date.day:02d}/{current_date.month}/{current_date.year % 100:02d}",  
        f"{current_date.day:02d}-{current_date.month}-{current_date.year % 100:02d}",  
        f"{current_date.day}/{current_date.month:02d}/{current_date.year % 100:02d}",  
        f"{current_date.day}/{current_date.month}/{current_date.year}",  
        f"{current_date.day}-{current_date.month:02d}-{current_date.year}",  
        f"{current_date.day:02d}/{current_date.month}/{current_date.year}",  
        f"{current_date.day}/{current_date.month}/{current_date.year}",  
        f"{current_date.day:02d}/{current_date.month}/{current_date.year % 100:02d}"  
        ]
    # είναι η λιστα με τα πιθανα ονόματα που βάζει ο καθηγητής ως ονομα εργασίας. Συνηθως βάζει τη ημερομηνία.Εχω βαλει ολες τις πιθανες μορφες
    completed = False
    while not completed:
        for row in rows:
            try:
                status_icon = row.find_element(By.XPATH, ".//td[@class='text-center']/i") # βρισκει το checkbox 
                if "fa-square" in status_icon.get_attribute("class"):  # ελεγχω αν δεν ειναι checked
                    task_name = row.find_element(By.XPATH, ".//td[1]/a").text # παιρνω το ονομα της εργασιας που βρισκεται στη πρωτη στυλη
                    try:
                        time_remaining = row.find_element(By.XPATH, ".//td[2]/small").text # επιλεγω το μικρο κειμενο στη δευτερη στυλη που λεει τον απομηναντα χρονο
                        if any(format in task_name for format in task_titles) and not "έχει λήξει" in time_remaining: 
                            task_link = row.find_element(By.XPATH, ".//td[1]/a")
                            task_link.click()
                            
                            keimeno_iframe = driver.find_element(By.ID, "submission_text_ifr") 
                            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(keimeno_iframe))
                            editable_body = driver.find_element(By.CSS_SELECTOR, "body")#επειδη το iframe δεν ειναι μερος του DOM θα πρεπει να το επιλεξω
                            editable_body.send_keys(MESSAGE)

                            driver.switch_to.default_content() # βγαινω απο το iframe και επιστρεφω στο DOM

                            sxolia = driver.find_element(By.ID, "stud_comments") # επιλεγω το πεδιο για τα σχολια και γραφω κατι random
                            sxolia.send_keys("asdfg")

                            #SUBMIT
                            submit_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.NAME, "work_submit"))) #βρισκω το submit κουμπι με βαση το name του
                            submit_button.click() 


                            current_time = datetime.now().strftime("%H:%M:%S")
                            print("Σου πήρα απουσία στις: ",current_time)
                            completed = True
                            break
                    except Exception: # αν ειναι χωρις προθεσμια η ασκηση δεν θα εχει small text αρα πεταει error που παραλειπω
                        pass
    
                    

            except Exception as e:
                print(e)

        if not completed:
            time.sleep(random.randint(10,15))
            driver.refresh()
            rows = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//table[@id='assignment_table']//tbody/tr")))
        if "login" in driver.current_url: # αν τελειωσει το session ξαναπηγαινει στην αρχικη σελιδα και ξανακανει Login
            time.sleep(random.randint(10,15))
            login()
            current_time = datetime.now().strftime("%H:%M:%S")
            print("Relogged at: ",current_time)
            navigate_to_course()

except Exception as e:
    print(f"Παρουσιάστηκε πρόβλημα: {e}")

finally:
    input("Πάτησε ENTER για τερματισμό...")
    driver.quit()
