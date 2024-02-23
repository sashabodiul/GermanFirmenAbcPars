
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import subprocess
import asyncio

app = FastAPI()

# Подключаем папку со статическими файлами (CSS, JS и т.д.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключаем папку с шаблонами Jinja2
templates = Jinja2Templates(directory="templates")


async def run_external_script(script_path):
    """
    Функция для запуска внешнего скрипта
    """
    process = await asyncio.create_subprocess_exec(
        "python", script_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return stdout.decode(), stderr.decode()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Главная страница с формой для ввода
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/run_script/")
async def run_script(request: Request, script_path: str = Form(...)):
    """
    Обработчик для запуска скрипта после отправки формы
    """
    stdout, stderr = await run_external_script(script_path)
    return {"stdout": stdout, "stderr": stderr}
