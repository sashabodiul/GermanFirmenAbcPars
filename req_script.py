import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re

global_container_data = []

async def get_data_from_container(container):
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

    global_container_data.append({
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
    })


async def extract_data(url:str, session):
    async with session.get(url) as response:
        html_content = await response.text()

    soup = BeautifulSoup(html_content, 'html.parser')
    containers = soup.find_all('div', class_='result-content')
    limit = soup.find('div', class_='info')
    limit = limit.find('strong').text
    match = re.search(r'\d+', str(limit))
    if match:
        limit = int(match.group())

    if containers:
        tasks = []
        for container in containers[:limit]:
            tasks.append(get_data_from_container(container))

        await asyncio.gather(*tasks)


async def get_urls(what: str, where: str = None):
    url = f'https://www.firmenabc.at/result.aspx?what={what}&where={where}&exact=false&inTitleOnly=false&l=&si='
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html_content = await response.text()

        soup = BeautifulSoup(html_content, 'html.parser')
        nav_pagination = soup.find('nav', class_='nav-pagination')
        if nav_pagination:
            limit_element = soup.find('div', class_='info').find('strong')
            if limit_element:
                limit_text = limit_element.text
                limit = int(re.search(r'\d+', limit_text).group())  # Extract numeric part
                pages = (limit // 50) + 1  # Calculate total pages to scrape
                tasks = []
                for i in range(pages):
                    updated_url = f'{url}&p={i + 1}'  # Adjust URL for pagination
                    tasks.append(extract_data(updated_url, session))

                await asyncio.gather(*tasks)

        else:
            await extract_data(url, session)

    global_result = global_container_data.copy()
    global_container_data.clear()
    return global_result

