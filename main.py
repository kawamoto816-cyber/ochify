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
    is_original: bool = False

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

class MessageRequest(BaseModel):
    sender_id: str
    receiver_id: str
    sender_name: str
    receiver_name: str
    message_text: str

class UpdateUserRequest(BaseModel):
    user_id: str
    new_name: str

OSAKA_ESSENCE = """
【重要コンテキスト：大阪の笑いの本質とペルソナ】
あなたは単なる関西弁を喋るAIではありません。上方落語に息づく「大阪の商売人気質」をベースにした人格を持っています。
大阪の笑いの本質は「相手に絶対に損をさせない」と、「限られた資源を最大化してお互いに面白がる関係性の構築」にあります。
桂米朝師匠のような「知的で品のある俯瞰した目線」と、笑福亭鶴瓶師匠のような「人懐っこく相手の懐に入り込む愛と包容力」を意識してください。
"""

# 🚨 【修正】AIの長文暴走を止める絶対命令（Hard Limit）とFew-Shot（具体例）！
def get_boke_prompt(boke_type: str, text_len: int, is_original: bool) -> str:
    base = OSAKA_ESSENCE + "\n"
    
    if is_original:
        base += """
【タスク】
ユーザーの入力文章はすでに完成された「ボケ（オチ）」です。
文章の内容（日本語）は『絶対に一切変更せず、一文字もいじらずにそのまま』出力してください。
あなたの仕事は、その日本語のニュアンスを汲み取った完璧な「英語への翻訳」と、それに対する最適な「3つのツッコミボタン」を提案することだけです。
"""
        return base

    length_hint = f"\n【🚨絶対遵守ルール（CRITICAL）🚨】\nユーザーの入力は「{text_len}文字」です。\n"
    if text_len <= 15:
        length_hint += """
👉 入力が非常に短いため、出力の『boke_jp』も必ず【1文のみ、最大40文字以内】の短く鋭い一言ボケにしてください！
（良い例：「パン食べたいやと！？ワイの頭のコッペパンでもかじっとけ！」）
絶対に長文でダラダラ語らないこと！長文はシステムエラーを引き起こすため固く禁じます！
"""
    elif text_len <= 30:
        length_hint += "👉 出力の『boke_jp』は【絶対に60文字程度（2〜3文以内）のテンポの良いボケ】にしてください。"
    else:
        length_hint += "👉 ユーザーの入力が長いため、出力の『boke_jp』は【情景が浮かぶ上方落語のようなしっかりとした長文のボケ】にしてください。"

    base += length_hint + "\n【タスク】\n"
    
    prompts = {
        "誇張": base + "ユーザーの日常を、上方落語の『東の旅 発端』のような見事なホラ話（大げさな誇張）に昇華させ、笑福亭鶴瓶師匠のように人懐っこく相手を巻き込んで笑わせてください。",
        "自虐": base + "ユーザーの悲しい出来事や失敗を、上方落語の『貧乏花見』のように明るく逞しく笑い飛ばし、相手を笑顔にする桂米朝師匠のような知的な自虐ネタに変えてください。",
        "勘違い": base + "ユーザーの日常を、上方落語の『阿弥陀池』のように理屈は通っているが盛大に勘違いしている愛すべきすっとぼけネタにしてください。"
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

def clean_json(text: str) -> str:
    text = text.replace("```json", "")
    text = text.replace("```", "")
    return text.strip()

def handle_ai_error(e):
    error_msg = str(e)
    if "503" in error_msg or "UNAVAILABLE" in error_msg or "high demand" in error_msg:
        raise HTTPException(status_code=503, detail="🤖 AIが現在世界中からひっぱりだこで大混雑しています！数秒待ってからもう一度押してください🙏")
    raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/health")
def health(): return {"status": "ok"}

@app.post("/api/init-user")
def init_user():
    import uuid, random
    user_id = str(uuid.uuid4())
    names = ["アホの坂田", "浪速の商人", "たこ焼き職人", "通天閣の虎", "くいだおれ太郎"]
    username = random.choice(names) + str(random.randint(10, 99))
    try: supabase.table("users").insert({"id": user_id, "username": username, "humor_dna": [0.0]*768}).execute()
    except: pass
    return {"user_id": user_id, "username": username}

@app.post("/api/update-user")
def update_user(req: UpdateUserRequest):
    try:
        supabase.table("users").update({"username": req.new_name}).eq("id", req.user_id).execute()
        return {"status": "success"}
    except Exception as e:
        return {"status": "error"}

@app.post("/api/preview-boke")
def preview_boke(req: BokeRequest):
    try:
        sys_prompt = get_boke_prompt(req.boke_type, len(req.text), req.is_original) + """
\n出力は以下のJSON構造にしてください。
type: "text"
boke_jp: (ボケたテキスト 日本語)
boke_en: (ボケたテキスト 英語)
tsukkomi_1, tsukkomi_2, tsukkomi_3: (ツッコミの選択肢 emoji, jp, en)
"""
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=req.text,
            config=types.GenerateContentConfig(system_instruction=sys_prompt, response_mime_type="application/json", response_schema=get_json_schema(), temperature=0.7) # 🚨 温度を下げてルールを厳格に守らせる
        )
        data = json.loads(clean_json(response.text))
        data["type"] = "text"
        
        if req.is_original:
            data["boke_jp"] = req.text
            data["is_original"] = True 

        try:
            emb_res = client.models.embed_content(model='text-embedding-004', contents=data.get("boke_en", "test"))
            boke_vector = emb_res.embeddings[0].values
        except Exception: 
            boke_vector = [0.0] * 768
            
        return {"boke_data": data, "boke_vector": boke_vector}
    except Exception as e:
        handle_ai_error(e)

@app.post("/api/preview-ijiri")
async def preview_ijiri(file: UploadFile = File(...)):
    try:
        img_bytes = await file.read()
        sys_prompt = OSAKA_ESSENCE + "\n【タスク】提供された画像を元に、笑福亭鶴瓶師匠のような人懐っこさと、商売人のような「相手をおいしくする（損させない）」愛のあるいじりを展開してください。出力はJSON。"
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[types.Part.from_bytes(data=img_bytes, mime_type=file.content_type), "この画像を上方落語のユーモアを交えていじってください。"],
            config=types.GenerateContentConfig(system_instruction=sys_prompt, response_mime_type="application/json", response_schema=get_json_schema(), temperature=0.85)
        )
        data = json.loads(clean_json(response.text))
        data["type"] = "image"
        import os, uuid
        file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        file_name = f"{uuid.uuid4()}.{file_ext}"
        supabase.storage.from_("ijiri_images").upload(file_name, img_bytes, {"content-type": file.content_type})
        data["image_url"] = supabase.storage.from_("ijiri_images").get_public_url(file_name)
        try:
            emb_res = client.models.embed_content(model='text-embedding-004', contents=data.get("boke_en", "test"))
            boke_vector = emb_res.embeddings[0].values
        except Exception: boke_vector = [0.0] * 768
        return {"boke_data": data, "boke_vector": boke_vector}
    except Exception as e:
        handle_ai_error(e)

@app.post("/api/generate-tasks")
def generate_tasks(req: TaskRequest):
    try:
        sys_prompt = "目標と期日を達成するための具体的なタスクを3〜5個、JSONで出力してください。\n{ \"tasks\": [\"タスク1\", \"タスク2\", ...] }"
        response = client.models.generate_content(model='gemini-2.5-flash', contents=f"目標: {req.goal}\n期日: {req.deadline}", config=types.GenerateContentConfig(system_instruction=sys_prompt, response_mime_type="application/json", temperature=0.7))
        return {"tasks": json.loads(clean_json(response.text)).get("tasks", [])}
    except Exception as e:
        handle_ai_error(e)

@app.post("/api/preview-yumeochi")
def preview_yumeochi(req: YumeochiRequest):
    try:
        sys_prompt = OSAKA_ESSENCE + "\n【タスク】ユーザーの「目標」と「今日やったこと（サボったこと）」を比較し、上方落語の「サゲ（オチ）」のように見事に話をまとめ、最後は必ず「シランケド」で終わる笑い話にしてください。出力はJSON。"
        response = client.models.generate_content(model='gemini-2.5-flash', contents=f"目標: {req.goal}\n今日のこと: {req.report}", config=types.GenerateContentConfig(system_instruction=sys_prompt, response_mime_type="application/json", response_schema=get_json_schema(), temperature=0.85))
        data = json.loads(clean_json(response.text))
        data["type"] = "yumeochi"
        data["goal"] = req.goal
        try:
            emb_res = client.models.embed_content(model='text-embedding-004', contents=data.get("boke_en", "test"))
            boke_vector = emb_res.embeddings[0].values
        except Exception: boke_vector = [0.0] * 768
        return {"boke_data": data, "boke_vector": boke_vector}
    except Exception as e:
        handle_ai_error(e)

@app.post("/api/publish")
def publish(req: PublishRequest):
    try:
        boke_data_to_save = req.boke_data.copy() if req.boke_data else {}
        boke_data_to_save["author_name"] = req.author_name
        record = {"author_id": req.author_id, "boke_data": boke_data_to_save, "boke_vector": req.boke_vector, "nandeyanen_count": 0}
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

@app.get("/api/my-posts/{user_id}")
def get_my_posts(user_id: str):
    try:
        res = supabase.table("boke_posts").select("*").eq("author_id", user_id).order("created_at", desc=True).limit(50).execute()
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

@app.post("/api/send-message")
def send_message(req: MessageRequest):
    try:
        record = {"sender_id": req.sender_id, "receiver_id": req.receiver_id, "sender_name": req.sender_name, "receiver_name": req.receiver_name, "message_text": req.message_text}
        supabase.table("messages").insert(record).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/messages/{user_id}")
def get_messages(user_id: str):
    try:
        res = supabase.table("messages").select("*").or_(f"sender_id.eq.{user_id},receiver_id.eq.{user_id}").order("created_at", desc=False).execute()
        return {"messages": res.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))