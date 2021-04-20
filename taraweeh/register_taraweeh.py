from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os.path import dirname, abspath, join, pardir
from datetime import date
import json
from time import sleep

def main(Registrants, Shifts):
    for person in Registrants:
        try:
            # New Chrome driver
            try: 
                driver = GetDriver()
            except Exception as error:
                print("Failed create a driver instance while trying to register, Error: {}".format(error))
                exit(1)

            ##### 1) Get to main IAR page
            driver.get("https://raleighmasjid.org")
            assert "The Islamic Association of Raleigh" in driver.title

            ##### 2) Get to eventbrite registration page
            driver.get(GetLinkfromElement("Register for Isha & Taraweeh", driver))
            assert "IAR Ishaa' & Taraweeh Registration" in driver.title

            ##### 3) Click "Select A Date" (TODO: make it based on text instead)
            try: 
                GetElementByXPATH("//button[starts-with(@id, 'eventbrite-widget-modal-trigger-')]", driver).click()
            except Exception as error:
                print("Failed to find or click 'Select A Date' while trying to register: {}".format(person['email'])) # , Error: {}".format(error))
                continue

            # switch iframe (to access pop-ups)
            try: 
                driver.switch_to.frame(driver.find_element_by_xpath("//iframe[starts-with(@id, 'eventbrite-widget-modal-')]"))
            except Exception as error:
                print("Failed to switch iframe while trying to register: {}".format(person['email'])) # , Error: {}".format(error))
                continue

            ##### 4) Select tickets for Taraweeh
            try: 
                ClickCatagory("9:", driver)
            except Exception as error:
                print("Failed to select tickets while trying to register: {}".format(person['email'])) # , Error: {}".format(error))
                continue

            ##### 5) Select a shift
            try: 
                SelectCatagory(Shifts[person['catagory']][person['timeslot']], driver)
                ClickBtnByText("Checkout", driver)
            except Exception as error:
                print("Failed to select shift: '{} {}' (might be soldout)".format(person['catagory'], person['timeslot'])) # , Error: {}".format(error))
                continue

            ##### 6) Fill out form
            try: 
                FillContactInfo(person['firstname'], person['lastname'], person['email'], driver)
                ClickBtnByText("Register", driver)
            except Exception as error:
                print("Failed to fill out personal info page while trying to register Error: {}".format(error))
                continue 

        except Exception as error:
            print("Failed to Register while trying to register: {}".format(person['email'])) # , Error: {}".format(error))
            continue
        else:
            sleep(3) 
            print("Tickets were sent to: {} on: {}".format(person['email'], date.today()))
            driver.quit()

def GetDriver():
    # Chrome (chrome driver is assumed to be inside the same dir)
    chromePath = "{}/chromedriver".format(abspath(join(dirname(abspath(__file__)), pardir)))

    # options object
    options = Options()

    # # silent mode
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu') 
    
    return Chrome(chromePath, options=options)

def SelectCatagory(catagory, driver):
    # Select dropdown XPATH relative to catagory title
    TitletoSelectPath = "../../div[2]/div/div/div/div/div[2]/select"
    number = 1
  
    # Relateive XPATH based on catagory name
    incrementXPATH = "//h3[text()='{}']/{}/option[text()='{}']".format(catagory, TitletoSelectPath, number)

    # Increment 
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, incrementXPATH))).click()
 
def ClickCatagory(catagory, driver):
    btnText = "Tickets"
    # Relateive XPATH based on catagory name
    incrementXPATH = "//div[contains(text(),'{}')]/../../../div[2]/div/button[text()='{}']".format(catagory, btnText)
    # click 
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, incrementXPATH))).click()

def FillContactInfo(fname, lname, email, driver):

    # Text feild IDs
    inputForm = {
        "//input[@id='buyer.N-first_name']" : fname,
        "//input[@id='buyer.N-last_name']" : lname,
        "//input[@id='buyer.N-email']" : email,
        "//input[@id='buyer.confirmEmailAddress']" : email,
        "//input[starts-with(@id,'A-') and @data-automation='checkout-form-N-first_name']": fname,
        "//input[starts-with(@id,'A-') and @data-automation='checkout-form-N-last_name']": lname
    }

    # clickables IDs
    clickables = [
        # COVID Questionnaire
        "//input[contains(@id, '.U-42134541-0') and starts-with(@data-automation, 'radio')]",
        "//input[contains(@id, '.U-42134543-0') and starts-with(@data-automation, 'radio')]",
        "//input[contains(@id, '.U-42134545-0') and starts-with(@data-automation, 'radio')]",
        "//input[contains(@id, '.U-42134547-0') and starts-with(@data-automation, 'radio')]",
        "//input[contains(@id, '.U-42134549-1') and starts-with(@data-automation, 'radio')]",

        # marketing subscription (uncheck)
        "//input[contains(@id, 'organizer-marketing-opt-in') and starts-with(@data-automation, 'checkbox')]",
        "//input[contains(@id, 'eb-marketing-opt-in') and starts-with(@data-automation, 'checkbox')]",
    ]

    for feild in inputForm:
        try:
            text_feild = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, feild)))
            text_feild.send_keys(inputForm[feild])
        except Exception as error:
            print("Failed to fill out: {}".format(feild))
            continue
 

    for clickable in clickables:
        try:
            checkbox = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, clickable)))
            driver.execute_script("arguments[0].click();", checkbox)
        except Exception as error:
            print("Failed to click radio/checkbox: {}".format(clickable))
            continue

def ClickBtnByText(text, driver):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[text()='{}']".format(text)))
    ).click()
    sleep(4)

def GetLinkfromElement(text, driver):
    return WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, text))
    ).get_attribute('href')

def GetElementByXPATH(xpath, driver):
    return WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, xpath))
    )

if __name__ == "__main__":
    # People to register
    try:
        registrants_json_file = "{}/registrants.json".format(dirname(abspath(__file__)))
        Registrants =  json.load(open(registrants_json_file))['registrants']
    except: 
        print(''' Failed to load taraweeh_registrants.json file. Please make sure this the .json file exists to continue!
                #################################################################################
                # FOLLOW THE EXAMPLE BELOW FOR PESONAL INFO FORMAT in the registrants.json file
                # (only update the value of the attributes:
                # {
                #     "catagory": "men or women",
                #     "timeslot": "timeslot",
                #     "firstname": "firstname",
                #     "lastname": "lastname",
                #     "email": "email to get tickets"
                # }
                #################################################################################
            ''')
        exit(1)

    # Shifts details
    Shifts = {
        "men": {
            "9:30": "Men 1st Shift (9:30-10:30PM)",
            "11:00": "Men 2nd Shift (11PM-12AM)"
        },
        "women": {
            "9:30": "Women 1st Shift (9:30-10:30PM)",
            "11:00": "Women 2nd Shift (11PM-12AM)"
        }
    }

    # call main function
    main(Registrants, Shifts)