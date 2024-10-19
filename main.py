from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
import base64
import motor.motor_asyncio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


MONGO_URL = "mongodb+srv://kalkeeshjami:s6TEME9trQYC03LG@kalki.maop5.mongodb.net/?retryWrites=true&w=majority&appName=kalki"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.my_data  
collection = db.items  

class Item(BaseModel):
    title: str
    description: str

@app.post("/upload")
async def upload_item(title: str = Form(...), description: str = Form(...), file: UploadFile = File(...)):
    contents = await file.read()
    image_base64 = base64.b64encode(contents).decode('utf-8')
    current_date = datetime.now().strftime("%d-%m-%Y")
    
    
    new_item = {
        "title": title,
        "image": image_base64,
        "description": description,
        "date": current_date
    }
    
    
    await collection.insert_one(new_item)
    
    return JSONResponse(content={"message": "Item uploaded successfully."})

@app.get("/all_items")
async def get_items():
    items_cursor = collection.find()
    items = await items_cursor.to_list(length=100)  
    
    if items:
        return JSONResponse(content={"items": items})
    else:
        return JSONResponse(content={"message": "No items found."}, status_code=404)

@app.get("/items_by_date")
async def get_items_by_date(date: str):
    try:
        datetime.strptime(date, "%d-%m-%Y")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Please use DD-MM-YYYY.")
    
    
    items_cursor = collection.find({"date": date})
    items = await items_cursor.to_list(length=100)
    
    if items:
        return JSONResponse(content={"items": items})
    else:
        return JSONResponse(content={"message": "No items found for the specified date."}, status_code=404)

@app.get("/all_dates")
async def get_dates():
    
    dates_cursor = collection.distinct("date")
    dates = await dates_cursor
    
    if dates:
        return JSONResponse(content={"dates": dates})
    else:
        return JSONResponse(content={"message": "No items found."}, status_code=404)

@app.get('/')
async def checkk():
    return "successful"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
