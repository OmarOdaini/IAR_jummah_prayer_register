from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os.path import dirname, abspath
from time import sleep


# Chrome
chromePath = "{}/chromedriver".format(dirname(abspath(__file__)))
options = Options()
# silent mode
options.add_argument('--headless')
options.add_argument('--disable-gpu') 

# create a chrome driver instance
driver = Chrome(chromePath, options=options)

# People to register
Registrants = [
    # FOLLOW THE EXAMPLE BELOW FOR PESONAL INFO FORMAT (only update the right side after colon):
    # {
    #     "catagory": "men or women",
    #     "timeslot": "timeslot",
    #     "firstname": "firstname", 
    #     "lastname": "lastname",
    #     "email": "email to get tickets",
    #     "phone": "phone #"
    # }
]

# Shifts details
Shifts = {
    "men": {
        "11:00": "Men 1st Shift (11:00 AM)",
        "12:00": "Men 2nd Shift (12:00 PM)",
        "1:00": "Men 3rd Shift (1:00 PM)",
        "2:15": "Men 4th Shift (2:15 PM)"
    },
    "women": {
        "11:00": "Women 1st Shift (11:00 AM)",
        "12:00": "Women 2nd Shift (12:00 PM)",
        "1:00": "Women 3rd Shift (1:00 PM)",
        "2:15": "Women 4th Shift (2:15 PM)"
    }
}


def Register():
    for person in Registrants:
        try:
            # get to IAR Jummah page
            driver.get("https://raleighmasjid.org/jumaa")
            assert "The Islamic Association of Raleigh - Jumuah Registration" in driver.title

            # get to eventbrite page
            driver.get(GetLinkfromBtn("Register for Jumuah Shifts"))
            assert "IAR Jumu'ah Registration" in driver.title
            ClickRegister()

            # switch iframe (to access pop-ups)
            driver.switch_to.frame(driver.find_element_by_xpath("//iframe[starts-with(@id, 'eventbrite-widget-modal-')]"))
            sleep(3)

            # Increment to specified catagory
            IncrementCatagory(Shifts[person['catagory']][person['timeslot']], 1)
            ClickRegister()

            # Fill out form 
            FillContactInfo(person['firstname'], person['lastname'], person['email'], person['phone'])
            ClickRegister()

        except Exception as error:
            print("Failed to Register, Error: {}".format(error))
        else:
            sleep(3) 
            print("Tickets were sent to: {}".format(person['email']))
            driver.quit() 
       
def IncrementCatagory(catagory, numberOfPpl):
    # Select dropdown XPATH relative to catagory title
    TitletoSelectPath = "../../div[2]/div/div/div/div/div[2]/select"
    # Relateive XPATH based on catagory name
    incrementXPATH = "//h3[text()='{}']/{}/option[text()='{}']".format(catagory, TitletoSelectPath, numberOfPpl)
    # Increment 
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, incrementXPATH))).click()

def FillContactInfo(fname, lname, email, phone):
     # Text feild IDs
    inputForm = {
            "buyer.N-first_name" : fname,
            "buyer.N-last_name" : lname,
            "buyer.N-email" : email,
            "buyer.confirmEmailAddress" : email,
            "buyer.N-cell_phone" : phone
        }

    # clickables IDs
    clickables = [
        # COVID Questionnaire
        "radio-buyer.U-33803592-0",
        "radio-buyer.U-33803594-0",
        "radio-buyer.U-33803598-0",
        "radio-buyer.U-33956774-0",
        "radio-buyer.U-37596875-0",

        # marketing subscription
        "organizer-marketing-opt-in",
         "eb-marketing-opt-in"
        ]

    for key in inputForm:
        textFeild = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, key)))
        textFeild.send_keys(inputForm[key])  
        
    for clickable in clickables:
        checkbox = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, clickable)))
        driver.execute_script("arguments[0].click();", checkbox)

def ClickRegister():
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[text()='Register']"))
    ).click()
    sleep(3)

def GetLinkfromBtn(text):
    return WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, text))
    ).get_attribute('href')

Register()
