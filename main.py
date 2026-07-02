from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

# 🔐 Cấu hình CORS để web Keepii.vn từ bất cứ đâu cũng gọi tới được
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🌐 DÁN CHUỖI KẾT NỐI MONGODB CỦA BẠN VÀO ĐÂY
# Nhớ thay <password> thành mật khẩu thật và XÓA 2 dấu < > đi nhé!
MONGO_URI = "mongodb+srv://lekhanh230893_db_user:L3ch1kh@nhM@cluster0.mcyknsl.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["KeepiiDatabase"]
users_collection = db["Users"]

class AccountModel(BaseModel):
    nickname: str
    password: str

@app.get("/")
def home():
    return {"status": "Server Keepii Cloud đang chạy online ổn định! 🚀"}

@app.post("/api/signup")
def signup(data: AccountModel):
    # Kiểm tra tài khoản toàn cầu
    existing_user = users_collection.find_one({"nickname": data.nickname})
    if existing_user:
        return {"success": False, "message": "Nickname đã tồn tại trên toàn cầu! 🛑"}
    
    # Lưu vào MongoDB
    users_collection.insert_one({"nickname": data.nickname, "password": data.password})
    return {"success": True, "message": "Đăng ký tài khoản thành công! 🎉"}
  
