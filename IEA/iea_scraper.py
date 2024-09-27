import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL_DATA = 'https://www.iea.org/data-and-statistics/data-tools/energy-statistics-data-browser'
URL_COUNTRIES = 'https://www.iea.org/countries'
PRINT_DATA = True
PRINT_COUNTRIES = True


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
        countries = pd.read_csv('IEA/iea_countries.csv')
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
        fuels = pd.read_csv('IEA/iea_fuels.csv')
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
        years = pd.read_csv('IEA/iea_years.csv')
        years = years['Year'].tolist()

    except FileNotFoundError:
        driver = open_iea_data_browser_tables()

        # Get year list
        year_select = driver.find_elements(By.CSS_SELECTOR, "select")[3]
        year_options = year_select.find_elements(By.CSS_SELECTOR, 'option')
        years = [option.get_attribute('innerHTML').strip() for option in year_options]

        driver.quit()

        if print_years:
            years = pd.Series(years, name='Year').to_csv('IEA/iea_years.csv', index=None)

    return years


def get_iea_data(fuel:   list[str]=None, 
                 country:list[str]=None, 
                 year:   list[str]=None, 
                 print_data:bool=False) -> pd.DataFrame:
    # Open webpage
    driver = open_iea_data_browser_tables()
    
    # Select data options (fuel, country, year)
    # Fuel
    # TODO: select fuel
    if fuel:
        ...
    
    # TODO: select country
    if country:
        ...
    
    # TODO: select year
    if year:
        ...


    # Get table data
    table = driver.find_element(By.CSS_SELECTOR, "div.m-data-table > table").get_attribute("outerHTML")
    df = pd.read_html(table)[0]

    
    # Close Chrome browser
    driver.quit()


    # Clean dataset
    df = df.rename(columns={'Unnamed: 0': ''})
    df = df.set_index('')
    df = df.iloc[1:]
    df = df.fillna('0')
    df = df.astype(str)
    df = df.apply(lambda x: x.str.replace(r'\s+', '', regex=True))
    df = df.astype(float)


    # Print to CSV
    if print_data:
        df.to_csv('IEA/iea_data.csv')


    return df


if __name__ == '__main__':
    iea_countries = get_iea_countries(print_countries=PRINT_COUNTRIES)    
    iea_fuels = get_iea_fuels(print_fuels=True)
    iea_years = get_iea_years(print_years=True)    
    iea_data  = get_iea_data(print_data=PRINT_DATA)