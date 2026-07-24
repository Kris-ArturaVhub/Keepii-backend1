from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pymongo import MongoClient
import urllib.parse
import json

app = FastAPI()

# 🌐 Cấu hình CORS toàn cầu (Giúp Frontend gửi data không bị chặn)[span_4](start_span)[span_4](end_span)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔑 Cấu hình kết nối MongoDB Atlas[span_5](start_span)[span_5](end_span)
username = "lekhanh230893_db_user"
password = "1234567890qwertyuiop"  # 👈 Bạn điền lại mật khẩu thật của bạn vào đây nhé[span_6](start_span)[span_6](end_span)

escaped_password = urllib.parse.quote_plus(password)[span_7](start_span)[span_7](end_span)
MONGO_URI = f"mongodb+srv://{username}:{escaped_password}@cluster0.mcyknsl.mongodb.net/?appName=Cluster0[span_8](start_span)"[span_8](end_span)

client = MongoClient(MONGO_URI)[span_9](start_span)[span_9](end_span)
db = client["KeepiiDatabase"][span_10](start_span)[span_10](end_span)
users_collection = db["Users"][span_11](start_span)[span_11](end_span)


# ==========================================
# 1. MODEL DỮ LIỆU (PYDANTIC)[span_12](start_span)[span_12](end_span)
# ==========================================
class AccountModel(BaseModel):
    nickname: str
    password: str

class UserDataModel(BaseModel):
    nickname: str
    notes: list = []        # Mảng chứa các ghi chú vuông[span_13](start_span)[span_13](end_span)
    inf_text: str = ""      # Chuỗi chứa văn bản vô hạn[span_14](start_span)[span_14](end_span)


# ==========================================
# 2. KHU VỰC ĐĂNG KÝ & ĐĂNG NHẬP (GIỮ NGUYÊN)[span_15](start_span)[span_15](end_span)
# ==========================================
@app.get("/")
def home():
    return {"status": "Server Keepii Cloud đang chạy online ổn định! 🚀"}[span_16](start_span)[span_16](end_span)

@app.post("/api/signup")
def signup(data: AccountModel):
    existing_user = users_collection.find_one({"nickname": data.nickname})[span_17](start_span)[span_17](end_span)
    if existing_user:
        return {"success": False, "message": "Nickname đã tồn tại trên toàn cầu! 🛑"}[span_18](start_span)[span_18](end_span)
    
    users_collection.insert_one({"nickname": data.nickname, "password": data.password})[span_19](start_span)[span_19](end_span)
    return {"success": True, "message": "Đăng ký tài khoản thành công! 🎉"}[span_20](start_span)[span_20](end_span)

@app.post("/api/signin")
def signin(data: AccountModel):
    user = users_collection.find_one({"nickname": data.nickname, "password": data.password})[span_21](start_span)[span_21](end_span)
    if user:
        return {"success": True, "message": "Đăng nhập thành công! 🔓"}[span_22](start_span)[span_22](end_span)
    else:
        return {"success": False, "message": "Sai nickname hoặc mật khẩu ❌"}[span_23](start_span)[span_23](end_span)


# ==========================================
# 3. KHU VỰC ĐỒNG BỘ GHI CHÚ MỚI (TƯƠNG THÍCH FRONTEND)[span_24](start_span)[span_24](end_span)
# ==========================================

# 📝 A. API Lưu dữ liệu thông thường (Fetch tự động mỗi 3s)[span_25](start_span)[span_25](end_span)
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

# 🚨 B. API Khẩn cấp (Nhận dữ liệu từ sendBeacon khi tắt tab/reload)[span_26](start_span)[span_26](end_span)[span_27](start_span)[span_27](end_span)
@app.post("/api/save_user_data_beacon")
async def save_user_data_beacon(request: Request):
    try:
        body = await request.body()[span_28](start_span)[span_28](end_span)
        data = json.loads(body.decode("utf-8"))[span_29](start_span)[span_29](end_span)
        
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

# 🔄 C. API Lấy lại dữ liệu khi User vừa mở App[span_30](start_span)[span_30](end_span)
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
