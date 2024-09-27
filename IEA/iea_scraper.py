import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
import time

URL_DATA = 'https://www.iea.org/data-and-statistics/data-tools/energy-statistics-data-browser'
URL_COUNTRIES = 'https://www.iea.org/countries'

PRINT_DATA = True
PRINT_COUNTRIES = True
PRINT_YEARS = True
PRINT_FUELS = True


def open_iea_webpage_in_chrome(url) -> webdriver.Chrome:
    # Load webpage in Chrome
    driver = webdriver.Chrome()
    driver.get(url)
    return driver


def open_iea_data_browser_tables() -> webdriver.Chrome:
    # Open data browser webpage
    driver = open_iea_webpage_in_chrome(URL_DATA)

    # Select "Browse as tables" button
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.XPATH, "//a[@data-tab-id='tables']"))
    )
    element = driver.find_element(By.XPATH, "//a[@data-tab-id='tables']")
    element.click()

    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.m-data-table > table"))
    )

    return driver


def get_iea_countries(print_countries: bool) -> list:
    try:
        countries = pd.read_csv('iea_countries.csv')
        countries = countries['Country'].tolist()

    except FileNotFoundError:
        driver = open_iea_webpage_in_chrome(URL_COUNTRIES)
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#countries h6 span"))
        )
        countries = [element.text for element in driver.find_elements(By.CSS_SELECTOR, "div#countries h6 span")]
        driver.quit()

        if print_countries:
            countries = pd.Series(countries, name='Country').to_csv('IEA/iea_countries.csv', index=None)

    return countries


def get_iea_fuels(print_fuels: bool) -> list:
    try:
        fuels = pd.read_csv('iea_fuels.csv')
        fuels = fuels['Fuel'].tolist()

    except FileNotFoundError:
        driver = open_iea_data_browser_tables()

        # Get fuel list
        fuel_div = driver.find_elements(By.CLASS_NAME, "a-button-group")[1]
        fuel_buttons = fuel_div.find_elements(By.CLASS_NAME, 'a-button__label')
        fuels = [option.get_attribute('innerHTML').strip() for option in fuel_buttons]

        driver.quit()

        if print_fuels:
            fuels = pd.Series(fuels, name='Fuel').to_csv('IEA/iea_fuels.csv', index=None)

    return fuels


def get_iea_years(print_years: bool) -> list:
    try:
        years = pd.read_csv('iea_years.csv')
        years = years['Year'].tolist()

    except FileNotFoundError:
        driver = open_iea_data_browser_tables()

        # Get year list
        year_select_div = (driver.find_elements(By.CLASS_NAME, "a-dropdown")[2]
                                 .find_element(By.CLASS_NAME, "a-dropdown__options"))
        year_buttons = year_select_div.find_elements(By.CSS_SELECTOR, "button")
        years = [button.get_attribute('innerHTML').strip() for button in year_buttons]

        driver.quit()

        if print_years:
            years = pd.Series(years, name='Year').to_csv('IEA/iea_years.csv', index=None)

    return years


def get_iea_table(driver):
    # Get table data
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.m-data-table > table"))
    )
    table = driver.find_element(By.CSS_SELECTOR, "div.m-data-table > table").get_attribute("outerHTML")
    df = pd.read_html(table)[0]

    # Clean dataset
    df = df.rename(columns={'Unnamed: 0': ''})
    df = df.set_index('')
    df = df.iloc[1:]
    df = df.fillna('0')
    df = df.astype(str)
    df = df.apply(lambda x: x.str.replace(r'\s+', '', regex=True))
    df = df.astype(float)
    df = df.stack().reset_index()
    df.columns = 'Flow', 'Fuel', 'Value'
    
    return df


def get_iea_data(fuels:     list[str]=None, 
                 countries: list[str]=None, 
                 years:     list[str]=None, 
                 print_data:bool=False) -> pd.DataFrame:
    # Open webpage
    driver = open_iea_data_browser_tables()
    
    # Set default options if none selected
    # fuels = [''] if not fuels else fuels
    years = [2021] if not years else years
    countries = ['World'] if not countries else countries

    # Select data options (fuel, country, year)
    # Fuels
    # TODO
    

    # Countries
    
    data = {}
    for ctry in countries:
        data[ctry] = {}

        ## Open country list
        ctry_select_div = driver.find_elements(By.CLASS_NAME, "a-dropdown")[1]    
        ctry_select_button = ctry_select_div.find_element(By.TAG_NAME, "button")
        ctry_select_button.click()

        ctry_select_div2 = ctry_select_div.find_elements(By.CLASS_NAME, "a-dropdown__options")[1]  
    
        ## Enter country name
        WebDriverWait(ctry_select_div2, 3).until(
            EC.visibility_of_element_located((By.TAG_NAME, 'input'))
        )
        ctry_item_input = ctry_select_div2.find_element(By.TAG_NAME, 'input')
        ctry_item_input.clear()
        ctry_item_input.send_keys(ctry)
        
        ## Select country
        WebDriverWait(ctry_select_div2, 3).until(
            EC.visibility_of_element_located((By.TAG_NAME, 'button'))
        )
        ctry_select_button = ctry_select_div2.find_element(By.TAG_NAME, "button")
        ctry_select_button.click()

    
        # Years
        
        for year in years:
            ## Open year list
            year_select_div = driver.find_elements(By.CLASS_NAME, "a-dropdown")[2]
            year_select_button = year_select_div.find_element(By.TAG_NAME, "button")
            year_select_button.click()

            ## Select year from list
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, f"//button[normalize-space()='{year}']"))
            )
            year_item_button = year_select_div.find_element(By.XPATH, f"//button[normalize-space()='{year}']")
            WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[normalize-space()='{year}']"))
            )
            year_item_button.click()


            # Scrape the table
            df = get_iea_table(driver)

            # Add country & year dimensions
            df.insert(0, 'Country', ctry)
            df.insert(-2, 'Unit', year)
            df.insert(-3, 'Year', year)

            data[ctry][year] = df.copy()
        data[ctry] = pd.concat(data[ctry])
    data = pd.concat(data)

    # Close Chrome browser
    driver.close()
    driver.quit()


    # Print to CSV
    if print_data:
        data.to_csv('iea_data.csv', index=False)


    return df


if __name__ == '__main__':


    iea_countries = get_iea_countries(print_countries=PRINT_COUNTRIES)    
    iea_fuels = get_iea_fuels(print_fuels=True)
    iea_years = get_iea_years(print_years=True)    
    
    years = [2018, 2019]
    countries = ['France', 'Germany']
    
    iea_data  = get_iea_data(print_data=PRINT_DATA, 
                             years=years,
                             countries=countries)
