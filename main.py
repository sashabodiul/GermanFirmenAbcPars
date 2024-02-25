from fastapi import FastAPI, Request, Form, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import aiofiles
import json
from openpyxl import Workbook
from req_script import get_urls, extract_data

app = FastAPI()

# Подключаем папку со статическими файлами (CSS, JS и т.д.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем папку с шаблонами Jinja2
templates = Jinja2Templates(directory="templates")

#Функция запуска внешнего скрипта
async def run_external_script(script_path):
    process = await asyncio.create_subprocess_exec(
        "python", script_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode(), stderr.decode()

# Сохранение данных в JSON файл
async def save_json(data):
    async with aiofiles.open("static/data.json", mode="w") as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=4))

# Сохранение данных в Excel файл
async def save_excel(data):
    wb = Workbook()
    ws = wb.active
    # Записываем заголовки
    headers = list(data[0].keys())
    ws.append(headers)
    # Записываем данные
    for row in data:
        row_data = [str(value) if not isinstance(value, dict) else str(value) for value in row.values()]
        ws.append(row_data)
    wb.save("static/data.xlsx")


#Страница формы ввода
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

#Обработчик после отправки формы
@app.post("/run_script/")
async def run_script(request: Request, search_query: str = Form(...), search_location: str = Form(...)):
    # Получаем значения из HTML-инпутов
    where = search_query
    what = search_location
    
    # Получаем данные
    result = await get_urls(what, where) if where is not None else await get_urls(what)

    # Сохраняем данные в JSON и Excel
    await save_json(result)
    await save_excel(result)

    # Возвращаем HTML с результатами и ссылками на файлы для скачивания
    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "data": result
        }
    )
