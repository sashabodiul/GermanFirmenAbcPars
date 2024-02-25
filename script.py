import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

async def extract_data(what: str, where: str = None):
    # Запускаем браузер в режиме без интерфейса
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome()

    try:
        # Открываем страницу
        driver.get('https://www.firmenabc.at/')

        # Находим поле для ввода и вводим данные
        what_element = driver.find_element(By.ID, 'what')
        what_element.send_keys(what)
        if where is not None:
            where_element = driver.find_element(By.ID, 'where')
            where_element.send_keys(where)

        btnSearch = driver.find_element(By.ID, 'btnSearch')
        btnSearch.click()

        # Ждем пока страница не прогрузится
        WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.CLASS_NAME, 'result-content')))

        # Получаем результаты
        search_results = driver.find_elements(By.CLASS_NAME, 'result-content')
        pg = 0
        # Переходим на следующие страницы, пока они есть
        while True:
            try:
                # Ожидаем появления элемента для следующей страницы
                next_page = WebDriverWait(driver, 4).until(EC.element_to_be_clickable((By.CLASS_NAME, 'css-triangle-right')))
                
                # Прокручиваем страницу, чтобы элемент был виден
                actions = ActionChains(driver)
                actions.move_to_element(next_page).perform()
                
                # Добавляем небольшую задержку перед кликом
                await asyncio.sleep(2)
                
                # Получаем текущий URL
                current_url = driver.current_url
                
                # Кликаем на следующую страницу
                next_page.click()
                pg+=1
                print(f'next page clicked {pg}')
                
                # Ждем загрузки следующей страницы
                WebDriverWait(driver, 4).until(EC.url_changes(current_url))
                
                # Получаем результаты на текущей странице
                search_results += driver.find_elements(By.CLASS_NAME, 'result-content')
            
            except Exception as e:
                # Обработка ошибки element click intercepted
                print("Произошла ошибка:", e)
                break

        print(len(search_results))

    finally:
        # Закрываем браузер
        driver.quit()

asyncio.run(extract_data('wien'))
