import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re

#TODO: clear data
async def extract_data(url:str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html_content = await response.text()
    soup = BeautifulSoup(html_content,'html_parser')
    container_data = {}
    cointainers = soup.find_all('div', class_='result-content')
    counter = 0
    for container in cointainers:
        counter+=1
        bottom_links = container.find("ul",class_="bottom-links")
        links = bottom_links.find_all('a')
        container_data[counter] = {
            "img": container.find("img"),
            "name": container.find("h2"),
            "address": {
                "street":container.find('span', itemprop="streetAddress"),
                "postalCode":container.find('span', itemprop="postalCode"),
                "addressLocality":container.find('span', itemprop="addressLocality")
                        },
            "company_info":container.find('a', class_="bg-light-blue"),
            "video":container.find('a', class_="bg-orange"),
            "rating":container.find('span',class_="rating"),
            "portrait":links[0],
            "contact":links[1],
        }

async def get_urls(what:str,where:str=None):
    if where is not None:
        url = f'https://www.firmenabc.at/result.aspx?what={what}&where={where}'
    else:
        url = f'https://www.firmenabc.at/suchbegriff/{what}'
        
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html_content = await response.text()
    
    # Создаем объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Находим элемент <nav> с классом 'nav-pagination'
    nav_pagination = soup.find('nav', class_='nav-pagination')

    # Если элемент найден, находим все теги <a> внутри него и выводим атрибут href
    if nav_pagination:
        links = nav_pagination.find_all('a')
        last_href = links[-2].get('href')
        # Используем регулярное выражение для поиска числа в строке
        match = re.search(r'\d+', str(last_href))
        # Если число найдено, извлекаем его
        if match:
            number = int(match.group())
            clear_url = re.sub(r'\d+', '', str(last_href))
            for i in range(1,number+1):
                print(clear_url+str(i))
        else:
            print("Число не найдено в строке.")
    else:
        print("Элемент <nav> с классом 'nav-pagination' не найден.")

asyncio.run(get_urls('wien','Tirol'))
