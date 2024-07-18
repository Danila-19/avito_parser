import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

driver_path = '/Users/mandreykin/dev/avito_parser/chromedriver-mac-x64/chromedriver'


def get_avito_data(mark, model):
    url = f'https://www.avito.ru/moskva/avtomobili/{mark}/{model}'
    print(f'Открытие URL: {url}')
    service = Service(executable_path=driver_path)
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)
    print('Браузер открыт.')
    try:
        print('Ожидание загрузки объявлений...')
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((
            By.CSS_SELECTOR, 'div[data-marker="item"]')))
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((
            By.CSS_SELECTOR, 'a[data-marker="item-title"]')))
        print('Объявления загружены.')
    except Exception as e:
        print(f'Ошибка во время ожидания загрузки объявлений: {e}')
        driver.quit()
        return None
    page_source = driver.page_source
    driver.quit()
    print('Браузер закрыт.')
    soup = BeautifulSoup(page_source, 'html.parser')
    print('Парсинг HTML.')
    items = soup.find_all('div', {'data-marker': 'item'})
    print(f'Найдено {len(items)} объявлений.')
    data = []
    for item in items:
        title_tag = item.find('a', {'data-marker': 'item-title'})
        if title_tag:
            title = title_tag.get('title')
            link = 'https://www.avito.ru' + title_tag.get('href')
            price_start_index = title.find('цена') + len('цена') + 1
            price_end_index = title.find('руб.')
            price = title[price_start_index:price_end_index].strip()
            if 'Автомобили в Москве' in title:
                data.append([title, price, link])
    if not data:
        print('В Москве нет таких машин')
        return None
    df = pd.DataFrame(data, columns=['Название', 'Цена', 'Ссылка'])

    #также можно сохранять в файл для удобного просмотрa
    file_name = f'{mark}_{model}_avito.csv'
    df.to_csv(file_name, index=False, encoding='utf-8-sig')
    print(f'Данные сохранены в файл: {file_name}')
    return df


pd.set_option('display.max_colwidth', None)
mark = input('Укажите марку: ')
model = input('Укажите модель: ')
df = get_avito_data(mark, model)
if df is not None:
    print(df)
else:
    print('Данные не найдены.')
