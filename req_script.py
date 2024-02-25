import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re

async def extract_data(url:str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html_content = await response.text()
    soup = BeautifulSoup(html_content, 'html.parser')
    container_data = {}
    containers = soup.find_all('div', class_='result-content')
    limit = soup.find('div', class_='info')
    limit = limit.find('strong').text
    match = re.search(r'\d+', str(limit))
    if match:
        limit = int(match.group())
    counter = 0
    
    for container in containers[:limit+1]:
        counter += 1
        bottom_links = container.find("ul", class_="bottom-links")
        links = bottom_links.find_all('a')

        # Rating logic
        rating_element = container.find('span', class_='rating')
        rating = None
        if rating_element:
            rating_class = rating_element.get('class', [])
            for class_name in rating_class:
                if class_name.startswith('perc-'):
                    rating_value = int(class_name.split('-')[1].split('-')[0]) // 20
                    rating = rating_value if rating_value > 0 else 1
                    break

        # Using lambda functions with checks for existence
        container_data[counter] = {
            "img": (lambda x: x.get('src') if x else None)(container.find("img")),
            "name": (lambda x: x.text if x else None)(container.find("h2")),
            "address": {
                "street": (lambda x: x.text if x else None)(container.find('span', itemprop="streetAddress")),
                "postalCode": (lambda x: x.text if x else None)(container.find('span', itemprop="postalCode")),
                "addressLocality": (lambda x: x.text if x else None)(container.find('span', itemprop="addressLocality"))
            },
            "company_info": (lambda x: x.get('href') if x else None)(container.find('a', class_="bg-light-blue")),
            "video": (lambda x: x.get('href') if x else None)(container.find('a', class_="bg-orange")),
            "rating": rating,
            "portrait": (lambda x: x.get('href') if x else None)(links[0]),
            "contact": (lambda x: x.get('href') if x else None)(links[1]),
        }

    return container_data


async def get_urls(what: str, where: str = None):
    if where is not None:
        url = f'https://www.firmenabc.at/result.aspx?what={what}&where={where}'
    else:
        url = f'https://www.firmenabc.at/suchbegriff/{what}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html_content = await response.text()

    soup = BeautifulSoup(html_content, 'html.parser')
    nav_pagination = soup.find('nav', class_='nav-pagination')

    if nav_pagination:
        links = nav_pagination.find_all('a')
        last_href = links[-2].get('href')
        match = re.search(r'\d+', str(last_href))
        if match:
            number = int(match.group())
            clear_url = re.sub(r'\d+', '', str(last_href))
            result = []
            for i in range(1, number+1):
                data = await extract_data(clear_url + str(i))  # Исправлено здесь
                result.append(data)
    else:
        result = await extract_data(url)

    return result
