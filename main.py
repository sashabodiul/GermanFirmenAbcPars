
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio

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

#Страница формы ввода
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

#Обработчик после отправки формы
@app.post("/run_script/")
async def run_script(search_query: str = Form(...), search_location: str = Form(...)):
    # Получаем значения из HTML-инпутов
    query = search_query
    location = search_location
    
    # Здесь можно выполнить дополнительные операции с полученными данными, например, передать их в функцию run_external_script
    
    return {"query": query, "location": location}

