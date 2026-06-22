from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from google import genai
from google.genai import types
from supabase import create_client, Client

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== API Keys ======
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not GEMINI_API_KEY: raise ValueError("GEMINI_API_KEY is missing")
if not SUPABASE_URL or not SUPABASE_KEY: raise ValueError("SUPABASE variables are missing")

client = genai.Client(api_key=GEMINI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ====== Models ======
class BokeRequest(BaseModel):
    text: str
    boke_type: str

class PublishRequest(BaseModel):
    author_id: str
    author_name: str
    boke_data: dict
    boke_vector: list = None

class TaskRequest(BaseModel):
    goal: str
    deadline: str

class YumeochiRequest(BaseModel):
    goal: str
    report: str

def get_boke_prompt(boke_type: str) -> str:
    prompts = {
        "誇張": "ユーザーの日常を、大阪のおばちゃん風に100倍くらい大げさに盛って面白くしてください。",
        "自虐": "ユーザーの日常を、哀愁漂う自虐ネタにして笑いに変えてください。関西弁で。",
        "勘違い": "ユーザーの日常を、盛大に勘違いしたボケにしてください。関西弁で。"
    }
    return prompts.get(boke_type, prompts["誇張"])

def get_json_schema():
    return {
        "type": "OBJECT",
        "properties": {
            "type": {"type": "STRING"},
            "boke_jp": {"type": "STRING"},
            "boke_en": {"type": "STRING"},
            "tsukkomi_1": {"type": "OBJECT", "properties": {"emoji": {"type": "STRING"}, "jp": {"type": "STRING"}, "en": {"type": "STRING"}}},
            "tsukkomi_2": {"type": "OBJECT", "properties": {"emoji": {"type": "STRING"}, "jp": {"type": "STRING"}, "en": {"type": "STRING"}}},
            "tsukkomi_3": {"type": "OBJECT", "properties": {"emoji": {"type": "STRING"}, "jp": {"type": "STRING"}, "en": {"type": "STRING"}}}
        },
        "required": ["type", "boke_jp", "boke_en", "tsukkomi_1", "tsukkomi_2", "tsukkomi_3"]
    }

def handle_ai_error(e):
    error_msg = str(e)
    if "503" in error_msg or "UNAVAILABLE" in error_msg or "high demand" in error_msg:
        raise HTTPException(status_code=503, detail="🤖 AIが現在世界中からひっぱりだこで大混雑しています！数秒待ってからもう一度押してください。")
    raise HTTPException(status_code=500, detail=error_msg)

# ====== Endpoints ======
@app.get("/api/health")
def health(): return {"status": "ok"}

@app.post("/api/init-user")
def init_user():
    import uuid, random
    user_id = str(uuid.uuid4())
    names = ["アホの坂田", "浪速の商人", "たこ焼き職人", "通天閣の虎", "くいだおれ太郎"]
    username = random.choice(names) + str(random.randint(10, 99))
    return {"user_id": user_id, "username": username}

@app.post("/api/preview-boke")
def preview_boke(req: BokeRequest):
    try:
        sys_prompt = get_boke_prompt(req.boke_type) + """
出力は以下のJSON構造にしてください。
type: "text"
boke_jp: (ボケたテキスト 日本語)
boke_en: (ボケたテキスト 英語)
tsukkomi_1, tsukkomi_2, tsukkomi_3: (それに対する3つのツッコミの選択肢。emoji, jp, enを含む)
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=req.text,
            config=types.GenerateContentConfig(system_instruction=sys_prompt, response_mime_type="application/json", response_schema=get_json_schema(), temperature=0.8)
        )
        data = json.loads(response.text)
        return {"boke_data": data, "boke_vector": [0.0]*10}
    except Exception as e:
        handle_ai_error(e)

@app.post("/api/preview-ijiri")
async def preview_ijiri(file: UploadFile = File(...)):
    try:
        img_bytes = await file.read()
        sys_prompt = """
提供された画像を大阪のおばちゃん目線で容赦なくいじり倒してください。出力はJSONでお願いします。
type: "image"
boke_jp: (いじりテキスト 日本語)
boke_en: (いじりテキスト 英語)
tsukkomi_1, tsukkomi_2, tsukkomi_3: (ツッコミ選択肢 emoji, jp, en)
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[types.Part.from_bytes(data=img_bytes, mime_type=file.content_type), "この画像をいじってください。"],
            config=types.GenerateContentConfig(system_instruction=sys_prompt, response_mime_type="application/json", response_schema=get_json_schema(), temperature=0.8)
        )
        data = json.loads(response.text)
        import os, uuid
        file_ext = file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{file_ext}"
        supabase.storage.from_("ijiri_images").upload(file_name, img_bytes, {"content-type": file.content_type})
        public_url = supabase.storage.from_("ijiri_images").get_public_url(file_name)
        data["image_url"] = public_url
        return {"boke_data": data, "boke_vector": [0.0]*10}
    except Exception as e:
        handle_ai_error(e)

@app.post("/api/generate-tasks")
def generate_tasks(req: TaskRequest):
    try:
        sys_prompt = "目標と期日を達成するための具体的なタスクを3〜5個、JSONで出力してください。\n{ \"tasks\": [\"タスク1\", \"タスク2\", ...] }"
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"目標: {req.goal}\n期日: {req.deadline}",
            config=types.GenerateContentConfig(system_instruction=sys_prompt, response_mime_type="application/json", temperature=0.7)
        )
        data = json.loads(response.text)
        return {"tasks": data.get("tasks", [])}
    except Exception as e:
        handle_ai_error(e)

@app.post("/api/preview-yumeochi")
def preview_yumeochi(req: YumeochiRequest):
    try:
        sys_prompt = """
ユーザーの「目標」と「今日やったこと（サボったこと）」を比較し、「シランケド」で終わる夢オチの笑い話にしてください。出力はJSON。
type: "yumeochi"
boke_jp: (シランケドで終わる日本語)
boke_en: (英語。最後は Shirankedo.で締める)
tsukkomi_1, tsukkomi_2, tsukkomi_3: (ツッコミ選択肢 emoji, jp, en)
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"目標: {req.goal}\n今日のこと: {req.report}",
            config=types.GenerateContentConfig(system_instruction=sys_prompt, response_mime_type="application/json", response_schema=get_json_schema(), temperature=0.8)
        )
        data = json.loads(response.text)
        data["goal"] = req.goal
        return {"boke_data": data, "boke_vector": [0.0]*10}
    except Exception as e:
        handle_ai_error(e)

# 🚨 ここから下、全部 boke_posts に直しました！
@app.post("/api/publish")
def publish(req: PublishRequest):
    try:
        record = {
            "author_id": req.author_id,
            "author_name": req.author_name,
            "boke_data": req.boke_data,
            "boke_vector": req.boke_vector,
            "nandeyanen_count": 0
        }
        res = supabase.table("boke_posts").insert(record).execute()
        return {"status": "success", "data": res.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/feed")
def get_feed():
    try:
        res = supabase.table("boke_posts").select("*").order("created_at", desc=True).limit(50).execute()
        return {"posts": res.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trending")
def get_trending():
    try:
        res = supabase.table("boke_posts").select("*").order("nandeyanen_count", desc=True).limit(50).execute()
        return {"posts": res.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/nandeyanen/{post_id}")
def add_nandeyanen(post_id: str):
    try:
        res = supabase.table("boke_posts").select("nandeyanen_count").eq("id", post_id).execute()
        if res.data:
            current = res.data[0].get("nandeyanen_count") or 0
            new_count = current + 1
            supabase.table("boke_posts").update({"nandeyanen_count": new_count}).eq("id", post_id).execute()
            return {"success": True, "new_count": new_count}
        return {"error": "post not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))