from fastapi import FastAPI
import urllib.parse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient

app = FastAPI()

# Cấu hình CORS toàn cầu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🌐 Khai báo mật khẩu riêng ra để mã hóa ký tự đặc biệt (@)
username = "lekhanh230893_db_user"
password = "L3ch1kh@nhM" 

# Sử dụng quote_plus để biến dấu @ thành định dạng mã hóa an toàn (%40)
escaped_password = urllib.parse.quote_plus(password)

# Ghép vào chuỗi kết nối chuẩn
MONGO_URI = f"mongodb+srv://{username}:{escaped_password}@cluster0.mcyknsl.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["KeepiiDatabase"]
users_collection = db["Users"]
class AccountModel(BaseModel):
    nickname: str
    password: str

@app.get("/")
def home():
    return {"status": "Server Keepii Cloud đang chạy online ổn định! 🚀"}

# 📝 1. CỔNG XỬ LÝ ĐĂNG KÝ
@app.post("/api/signup")
def signup(data: AccountModel):
    existing_user = users_collection.find_one({"nickname": data.nickname})
    if existing_user:
        return {"success": False, "message": "Nickname đã tồn tại trên toàn cầu! 🛑"}
    
    users_collection.insert_one({"nickname": data.nickname, "password": data.password})
    return {"success": True, "message": "Đăng ký tài khoản thành công! 🎉"}

# 🔑 2. CỔNG XỬ LÝ ĐĂNG NHẬP (MỚI THÊM)
@app.post("/api/signin")
def signin(data: AccountModel):
    # Tìm tài khoản trên MongoDB Atlas theo Nickname và Mật khẩu
    user = users_collection.find_one({"nickname": data.nickname, "password": data.password})
    
    if user:
        return {"success": True, "message": "Đăng nhập thành công! 🔓"}
    else:
        return {"success": False, "message": "Sai nickname hoặc mật khẩu ❌"}
                                      
