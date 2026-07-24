from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import urllib.parse
import json

app = FastAPI()

# Cấu hình CORS toàn cầu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

username = "lekhanh230893_db_user"
password = "1234567890qwertyuiop"

# Đã dọn sạch các ký tự rác copy-paste ở đoạn này!
escaped_password = urllib.parse.quote_plus(password)
MONGO_URI = f"mongodb+srv://{username}:{escaped_password}@cluster0.mcyknsl.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["KeepiiDatabase"]
users_collection = db["Users"]

class AccountModel(BaseModel):
    nickname: str
    password: str

class UserDataModel(BaseModel):
    nickname: str
    notes: list = []
    inf_text: str = ""

@app.get("/")
def home():
    return {"status": "Server Keepii Cloud đang chạy online ổn định! 🚀"}

@app.post("/api/signup")
def signup(data: AccountModel):
    existing_user = users_collection.find_one({"nickname": data.nickname})
    if existing_user:
        return {"success": False, "message": "Nickname đã tồn tại trên toàn cầu! 🛑"}
    
    users_collection.insert_one({"nickname": data.nickname, "password": data.password})
    return {"success": True, "message": "Đăng ký tài khoản thành công! 🎉"}

@app.post("/api/signin")
def signin(data: AccountModel):
    user = users_collection.find_one({"nickname": data.nickname, "password": data.password})
    if user:
        return {"success": True, "message": "Đăng nhập thành công! 🔓"}
    else:
        return {"success": False, "message": "Sai nickname hoặc mật khẩu ❌"}

@app.post("/api/save_user_data")
def save_user_data(data: UserDataModel):
    try:
        users_collection.update_one(
            {"nickname": data.nickname},
            {"$set": {
                "notes": data.notes,
                "inf_text": data.inf_text
            }},
            upsert=True
        )
        return {"success": True, "message": "Đã đồng bộ lên MongoDB Atlas thành công!"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/save_user_data_beacon")
async def save_user_data_beacon(request: Request):
    try:
        body = await request.body()
        data = json.loads(body.decode("utf-8"))
        
        users_collection.update_one(
            {"nickname": data.get("nickname")},
            {"$set": {
                "notes": data.get("notes", []),
                "inf_text": data.get("inf_text", "")
            }},
            upsert=True
        )
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.post("/api/get_user_data")
def get_user_data(data: dict):
    try:
        nickname = data.get("nickname")
        user = users_collection.find_one({"nickname": nickname}, {"_id": 0})
        
        if user:
            return {
                "success": True, 
                "notes": user.get("notes", []), 
                "inf_text": user.get("inf_text", "")
            }
        return {"success": True, "notes": [], "inf_text": ""}
    except Exception as e:
        return {"success": False, "error": str(e)}
