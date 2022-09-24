from dataclasses import replace
from distutils.command.build import build
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.options import Options
import os, csv, time, shutil, glob
from twilio.rest import Client
from dotenv import load_dotenv


def login():
    USERNAME = os.getenv('USERNAME')
    PASSWORD = os.getenv('PASSWORD')
    
    driver.get(os.getenv('WEBSITE'))
    userID_element = driver.find_element(By.ID, 'userID').send_keys(USERNAME)
    password_element = driver.find_element(By.ID, 'password').send_keys(PASSWORD)
    driver.find_element(By.NAME, 'submitButton').click()
    time.sleep(30)

def get_calendar_download():
    link_click = driver.find_element(By.PARTIAL_LINK_TEXT, 'Crew Calendar')
    link_click.click()
    time.sleep(5)
    driver.find_element(By.ID, 'btnCSV').click()
    time.sleep(5)

def build_schedule(csv_sch):
    schedule_hash = {}
    
    with open(csv_sch, newline='') as new_file:
        csv_reader = csv.reader(new_file, delimiter=',')
        next(new_file)
        for row in csv_reader:
            if row[5] =='':
                pass
            else:
              schedule_hash[row[1]] = row[5]

        return schedule_hash

def twilio_call():
    ACCOUNT_SID = os.getenv('ACCOUNT_SID')
    AUTH_TOKEN = os.getenv('AUTH_TOKEN')
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    call = client.calls.create(to=os.getenv('CALL_TO'),
    from_=os.getenv('CALL_FROM'),
    url='http://demo.twilio.com/docs/voice.xml')
    print(call.sid)

def find_and_move_csv():
    os.chdir('./Download')
    for file in glob.glob('*.csv'):
        os.rename(file, 'new_schedule.csv') ## comment out to test, make /Download/new_schedule.csv
        shutil.move('new_schedule.csv', '..')
        break
    os.chdir('..')


def notify():
    find_and_move_csv()
    new_schedule = build_schedule('new_schedule.csv')
    old_schedule = build_schedule('previous_schedule.csv')

    schedule_change = False

    print('\n\nComparing schedules', end='')

    for i in range(0, 15):
        print('. ', end='')
        time.sleep(0.25)
    

    for key in new_schedule:
        if key not in old_schedule:
            schedule_change = True
            print('\n\nYou have a schedule change, please check CCI\n')
            twilio_call()
            break
    if not schedule_change:
        print('\n\nNo Schedule change\n')

def clean_schedule():
    os.remove('previous_schedule.csv')
    os.rename('new_schedule.csv', 'previous_schedule.csv')
    shutil.rmtree('Download')

    print('Schedules have been cleaned, checks OK\n')


#############################################

load_dotenv()

options = Options()
options.add_experimental_option('prefs', {'download.default_directory': 'C:\\Users\\wisem\\Documents\\Code\\Python\\Selenium\\Download',
        'download.prompt_for_download': False})
driver = webdriver.Edge('msedgedriver.exe', options=options)


login()
get_calendar_download()
notify()
clean_schedule()
