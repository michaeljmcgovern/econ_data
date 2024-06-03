import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL = 'https://www.iea.org/data-and-statistics/data-tools/energy-statistics-data-browser'
PRINT = True


def get_iea(print_data=False):
    # Load webpage in Chrome
    service = Service(executable_path='IEA/chromedriver')
    driver = webdriver.Chrome(service=service)
    driver.get(URL)

    
    # Select "Browse as tables"
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.XPATH, "//a[@data-tab-id='tables']"))
    )
    element = driver.find_element(By.XPATH, "//a[@data-tab-id='tables']")
    element.click()


    # Select data options (fuel, country, year)
    # TODO
    ...


    # Get table data
    WebDriverWait(driver, 3).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.m-data-table > table"))
    )
    table = driver.find_element(By.CSS_SELECTOR, "div.m-data-table > table").get_attribute("outerHTML")
    df = pd.read_html(table)[0]

    
    # Close Chrome browser
    driver.quit()


    # Process dataset
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
    iea_data = get_iea(print_data=PRINT)