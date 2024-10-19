from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import base64
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
class Item(BaseModel):
    title: str
    description: str

CSV_FILE_PATH = "items.csv"


@app.post("/upload")
async def upload_item( title: str = Form(...), description: str = Form(...), file: UploadFile = File(...)):
    if not os.path.exists(CSV_FILE_PATH):
        df = pd.DataFrame(columns=["title", "image", "description", "date"])
        df.to_csv(CSV_FILE_PATH, index=False)
    contents = await file.read()
    image_base64 = base64.b64encode(contents).decode('utf-8')
    current_date = datetime.now().strftime("%d-%m-%Y")
    new_data = pd.DataFrame({
        "title": [title],
        "image": [image_base64],
        "description": [description],
        "date": [current_date]
    })
    new_data.to_csv(CSV_FILE_PATH, mode='a', header=False, index=False)
    return JSONResponse(content={"message": "Item uploaded successfully."})

@app.get("/all_items")
async def get_items():
    if os.path.exists(CSV_FILE_PATH):
        df = pd.read_csv(CSV_FILE_PATH)
        items = df.to_dict(orient="records")
        return JSONResponse(content={"items": items})
    else:
        return JSONResponse(content={"message": "No items found."}, status_code=404)


@app.get('/')
async def checkk():
    return "successful"


# @app.get("/items_by_date")
# async def get_items_by_date(date: str):
#     try:
#         datetime.strptime(date, "%d-%m-%Y")
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid date format. Please use DD-MM-YYYY.")
#     if os.path.exists(CSV_FILE_PATH):
#         df = pd.read_csv(CSV_FILE_PATH)
#         filtered_items = df[df['date'] == date]
#         if not filtered_items.empty:
#             items = filtered_items.to_dict(orient="records")
#             return JSONResponse(content={"items": items})
#         else:
#             return JSONResponse(content={"message": "No items found for the specified date."}, status_code=404)
#     else:
#         return JSONResponse(content={"message": "No items found."}, status_code=404)


# @app.get("/all_dates")
# async def get_dates():
#     if os.path.exists(CSV_FILE_PATH):
#         df = pd.read_csv(CSV_FILE_PATH)
#         df =pd.DataFrame(df)
#         dates = df['date'].unique().tolist()
#         return JSONResponse(content={"dates": dates})
#     else:
#         return JSONResponse(content={"message": "No items found."}, status_code=404)


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)