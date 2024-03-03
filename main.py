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

# Сохранение данных в Excel файл
async def save_excel(data):
    # Преобразование JSON в таблицу pandas DataFrame
    data_frames = []
    for block in data:
        data_frames.append(pd.DataFrame.from_dict(block, orient='index'))

    # Объединение DataFrame'ов и сохранение в Excel
    result = pd.concat(data_frames)
    result.to_excel('output.xlsx', index=False)

# Страница формы ввода
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Обработчик после отправки формы
@app.post("/run_script/")
async def run_script(request: Request, search_query: str = Form(...), search_location: str = Form(...)):
    # Получаем значения из HTML-инпутов
    where = search_query
    what = search_location
    
    # Получаем данные
    result = await get_urls(what, where) if where is not None else await get_urls(what)
    if not result:
        return templates.TemplateResponse('empty.html', {"request": request})
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
    return FileResponse("output.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="output.xlsx")
