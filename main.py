import re
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains, Firefox #Replace with your driver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService #Replace with your driver
from typing_extensions import Literal
from webdriver_manager.firefox import GeckoDriverManager #Replace with your driver

from constants import DAMAGE_TYPE_NAMES, PROPERTY_NAMES, WEAPON_TYPE_NAMES


def connect(server: Literal['asia', 'china', 'original', 'beta', 'jporiginal'], driver) -> None:
    driver.get(f'https://redbean.tech/illustrate/v3#@{server}')

    #It's needed to display all the items in one page (easy to parse)
    element = driver.find_element(By.CSS_SELECTOR, '.items-per-page > input:nth-child(1)')
    element.send_keys('00')

    #P.S idk why but WebDriverWait().until doesn't work
    time.sleep(1)
    
    
def open_info(id_: int, driver) -> bool:
    try:
        element = driver.find_element(By.XPATH, f'//*[@id="{id_}"]')
        element.click()
        
    except NoSuchElementException:
        return False

    time.sleep(0.5)
    return True


def close_info(driver) -> None:
    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    time.sleep(0.5)


def get_main_info(driver) -> dict:
    main_info = dict()
    
    element = driver.find_element(By.CSS_SELECTOR, '.detail-no')
    main_info['ID'] = element.text[3:]
    
    element = driver.find_element(By.CSS_SELECTOR, '.detail-equip-img')
    main_info['Icon'] = element.get_attribute('src')
    
    element = driver.find_element(By.CSS_SELECTOR, '.detail-title')
    main_info['Title'] = element.text
    
    try:
        element = driver.find_element(By.CSS_SELECTOR, '.detail-damage-type')
        main_info['Damage Type'] = DAMAGE_TYPE_NAMES[element.get_attribute('src').split('/')[-1][:-4]]

    except NoSuchElementException:
        main_info['Damage Type'] = None

    elements = driver.find_elements(By.CSS_SELECTOR, '.detail-rarity-star')
    main_info['Rarity'] = len(elements)

    return main_info


def get_properties(driver) -> dict:
    server = re.search(r'@([a-z]+)', driver.current_url).group(1)

    elements = driver.find_elements(By.CSS_SELECTOR, 'span.detail-secondary-title')
    names = [element.text[:-1] for element in elements]
    
    elements = driver.find_elements(By.CSS_SELECTOR, 'span.detail-secondary-prop')
    values = [element.text for element in elements]
    
    return {PROPERTY_NAMES.get(name, name) : WEAPON_TYPE_NAMES.get(value, value if value != '特殊-弓' or server != 'asia' else 'Bow') for name, value in zip(names, values)}


def get_skills(driver) -> list:
    elements = driver.find_elements(By.CSS_SELECTOR, '.detail-skill-damage-type')
    damage_types = [element.get_attribute('src').split('/')[-1][:-4] for element in elements]
    damage_types = [DAMAGE_TYPE_NAMES[damage_type] for damage_type in damage_types]
        
    elements = driver.find_elements(By.CSS_SELECTOR, 'p.detail-skill-title')
    titles = [element.text for element in elements]
    elements = driver.find_elements(By.CSS_SELECTOR, 'p.detail-skill-desc')
    descriptions = [element.text.replace('\n', '').replace(' %', '%') for element in elements]
        
    return [(damage_type, title, description.strip()) for damage_type, title, description in zip(damage_types, titles, descriptions)]


def get_item(id_: int, driver) -> tuple[dict, dict, list] | None:
    if not open_info(id_, driver):
        return None, None, None
    main_info = get_main_info(driver)
    properties = get_properties(driver)
    skills = get_skills(driver)
    close_info(driver)
    return main_info, properties, skills
    

def check_item(id_: int, driver) -> None:
    main_info, properties, skills = get_item(id_, driver)
    if not main_info:
        print(f'No.{id_} not found')
    print(f'{main_info}\n{properties}')
    for skill in skills:
        print(skill)
        
        
if __name__ == '__main__':
    #Replace with your driver
    driver = Firefox(service=FirefoxService(GeckoDriverManager().install(), log_output='driver.log'))
    connect('asia', driver)
    print('Start')
    for id_ in range(3000, 3010):
        check_item(id_, driver)
    driver.quit()
    print('End')
    