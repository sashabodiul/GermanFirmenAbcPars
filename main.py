from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import pandas as pd
from tempfile import NamedTemporaryFile
from req_script import get_urls

app = FastAPI(host="0.0.0.0")

# Подключаем папку со статическими файлами (CSS, JS и т.д.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем папку с шаблонами Jinja2
templates = Jinja2Templates(directory="templates")

# Сохранение данных в JSON файл
async def save_json(data):
    return json.dumps(data, ensure_ascii=False, indent=4)


async def save_excel(data):
    # Создайте DataFrame из списка словарей
    # Создайте DataFrame из списка словарей
    df = pd.DataFrame(data)

    # Укажите новые заголовки
    new_columns = ['img', 'name', 'address', 'company_info', 'video', 'rating', 'portrait', 'contact']

    # Переименуйте столбцы
    df.columns = new_columns

    # Замените все значения None на пустые значения в DataFrame
    df = df.where(pd.notnull(df), None)

    # Отсортируйте DataFrame по столбцу 'name'
    df = df.sort_values(by='name')

    # Сохраните DataFrame в файл Excel
    df.to_excel('data.xlsx', index=False)


# Страница формы ввода
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Обработчик после отправки формы
@app.post("/run_script/")
async def run_script(request: Request, search_query: str = Form(...), search_location: str = Form(...)):
    # Получаем значения из HTML-инпутов
    what = search_query
    where = search_location
    
    # Получаем данные
    result = await get_urls(what, where) if where is not None else await get_urls(what)
    if where is not None and what is not None:
        result = await get_urls(what, where)
    if what is not None and where is None:
        result = await get_urls(what)
    if not result:
        return templates.TemplateResponse('empty.html', {"request": request})
    with open('result.json', 'w') as file:
        # Assuming result is a list
        result_str = json.dumps(result)

        # Now you can write result_str to the file
        file.write(result_str)
    # Сохраняем данные в JSON и Excel
    json_data = await save_json(result)
    await save_excel(result)
    
    # Возвращаем HTML с результатами и ссылками на файлы для скачивания
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "data": result,
            "json_data": json_data
        }
    )

# Обработчик для скачивания JSON файла
@app.get("/download_json/")
async def download_json(json_data: str = Query(...)):
    temp_file = NamedTemporaryFile(delete=False, suffix=".json")
    temp_file.write(json_data.encode())
    temp_file.close()
    return FileResponse(temp_file.name, media_type="application/json", filename="data.json")

# Обработчик для скачивания Excel файла
@app.get("/download_excel/")
async def download_excel():
    return FileResponse("data.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="data.xlsx")
