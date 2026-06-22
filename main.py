import os
import json
import uuid
import random
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from supabase import create_client, Client
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 🔒 金庫(.env)からキーを安全に読み込む！
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI(title="BokeCha API V8", description="匿名ログイン＆金庫対応")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    ai_client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"接続エラー: {e}")

class DailyInput(BaseModel):
    text: str
    boke_type: str = "誇張"

class TaskRequest(BaseModel):
    goal: str
    deadline: str

class YumeochiRequest(BaseModel):
    goal: str
    report: str

class PublishInput(BaseModel):
    author_id: str  # 👈 新機能: 誰の投稿かを受け取る箱
    author_name: str # 👈 投稿者の名前も受け取る
    boke_data: dict
    boke_vector: list

def clean_json(text: str) -> str:
    text = text.replace("```json", "")
    text = text.replace("```", "")
    return text.strip()

# ==========================================
# 🆕 アプリを開いた瞬間に匿名ユーザーを自動発行！
# ==========================================
@app.post("/api/init-user")
async def init_user():
    try:
        # ランダムで面白い仮の名前を付ける
        names = ["見知らぬオカン", "さまようツッコミ師", "匿名ボケ担当", "大阪の妖精", "意識低い系勇者", "夢見るサボり魔"]
        username = f"{random.choice(names)}{random.randint(10, 99)}号"
        
        # データベースにひっそりユーザー登録
        res = supabase.table("users").insert({"username": username, "humor_dna": [0.0]*768}).execute()
        new_user = res.data[0]
        
        return {"status": "success", "user_id": new_user["id"], "username": new_user["username"]}
    except Exception as e:
        print(f"ユーザー生成エラー: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/preview-boke")
async def preview_boke(req: DailyInput):
    boke_data = {"type": "text", "boke_jp": f"「{req.text}」…って思ってたけど、気づいたら全裸でアマゾン川泳いでたわ！", "boke_en": "Amazon!", "tsukkomi_1": {"emoji": "🐊", "jp": "ワニに食われろ！", "en": "Croc!"}, "tsukkomi_2": {"emoji": "🤦", "jp": "盛大にウソつくな！", "en": "Liar!"}, "tsukkomi_3": {"emoji": "🤷‍♂️", "jp": "知らんがな", "en": "Who cares!"}}
    boke_vector = [0.1] * 768
    style_instruction = "事実を宇宙規模やあり得ないレベルまで大げさに盛ってください。" if "誇張" in req.boke_type else "言葉の意味や状況を全く別の斜め上の方向に勘違い・すっとぼけ解釈してボケてください。" if "勘違い" in req.boke_type else "自分のさらに悲惨で情けないエピソードにすり替えて哀愁漂う自虐ボケにしてください。"

    prompt = f"""
    あなたは天才的なお笑い放送作家です。ユーザーが入力した「オチのない平凡な日記」を、指定された【ボケのテイスト】に合わせて、ユーザー自身がつぶやいているような『関西弁の面白いボケ（独り言）』に変換・脚色してください。
    【重要】絶対に他人へのツッコミにはしないでください。投稿者本人の発言として書いてください。
    【指定されたボケのテイスト】: {req.boke_type} ({style_instruction})
    【入力された日常】: {req.text}
    その後、このボケを見た第三者が思わず押したくなる「的確なツッコミボタン」を3つ提案してください。必ず以下のJSONのみで返してください。
    {{"boke_jp": "関西弁での一人称のボケ", "boke_en": "英語でのボケ訳", "tsukkomi_1": {{"emoji": "絵文字", "jp": "的確なツッコミ1", "en": "English 1"}}, "tsukkomi_2": {{"emoji": "絵文字", "jp": "的確なツッコミ2", "en": "English 2"}}, "tsukkomi_3": {{"emoji": "🤷‍♂️", "jp": "知らんがな", "en": "Who cares!"}}}}
    """
    try:
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt, config=types.GenerateContentConfig(response_mime_type="application/json"))
        boke_data_ai = json.loads(clean_json(response.text))
        boke_data_ai["type"] = "text"
        boke_data = boke_data_ai
    except Exception as e: print(f"⚠️ 文章エラー: {e}")

    try:
        emb_res = ai_client.models.embed_content(model='text-embedding-004', contents=boke_data.get("boke_en", "test"))
        boke_vector = emb_res.embeddings[0].values
    except Exception: pass
    return {"status": "success", "boke_data": boke_data, "boke_vector": boke_vector}

@app.post("/api/preview-ijiri")
async def preview_ijiri(file: UploadFile = File(...)):
    file_bytes = await file.read()
    file_ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    supabase.storage.from_("boke_images").upload(file=file_bytes, path=unique_filename, file_options={"content-type": file.content_type})
    image_url = supabase.storage.from_("boke_images").get_public_url(unique_filename)
    
    ijiri_data = {"type": "image", "image_url": image_url, "boke_jp": "えらい個性的な写真やな！", "boke_en": "What a unique photo!", "tsukkomi_1": {"emoji": "📸", "jp": "画角！", "en": "Angle!"}, "tsukkomi_2": {"emoji": "👗", "jp": "クセがすごい！", "en": "Crazy!"}, "tsukkomi_3": {"emoji": "🤷‍♂️", "jp": "知らんがな", "en": "Who cares!"}}
    ijiri_vector = [0.2] * 768
    
    image_part = types.Part.from_bytes(data=file_bytes, mime_type=file.content_type)
    prompt = "あなたは愛のある大阪のおかんです。ユーザーがアップロードした写真の「おいしい部分」を見つけ関西弁で「いじって」ください。その後いじりボタンを3つ提案してください。\n必ず以下のJSONのみで返してください。{\"boke_jp\": \"...\", \"boke_en\": \"...\", \"tsukkomi_1\": {\"emoji\": \"...\", \"jp\": \"...\", \"en\": \"...\"}, \"tsukkomi_2\": {...}, \"tsukkomi_3\": {...}}"
    
    try:
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=[prompt, image_part], config=types.GenerateContentConfig(response_mime_type="application/json"))
        ai_data = json.loads(clean_json(response.text))
        ai_data["type"] = "image"
        ai_data["image_url"] = image_url 
        ijiri_data = ai_data
    except Exception as e: print(f"⚠️ 画像解析エラー: {e}")

    try:
        emb_res = ai_client.models.embed_content(model='text-embedding-004', contents=ijiri_data.get("boke_en", "test"))
        ijiri_vector = emb_res.embeddings[0].values
    except Exception: pass
    return {"status": "success", "boke_data": ijiri_data, "boke_vector": ijiri_vector}

@app.post("/api/generate-tasks")
async def generate_tasks(req: TaskRequest):
    prompt = f"""
    ユーザーの目標: 「{req.goal}」
    期日: {req.deadline}
    この目標を達成するための、現実的で具体的な「逆算タスク（最初の一歩の行動）」を3つ提案してください。
    必ず以下のJSON形式のみで返してください。
    {{"tasks": ["タスク1", "タスク2", "タスク3"]}}
    """
    try:
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt, config=types.GenerateContentConfig(response_mime_type="application/json"))
        tasks_data = json.loads(clean_json(response.text))
        return {"status": "success", "tasks": tasks_data.get("tasks", [])}
    except Exception as e:
        return {"status": "error", "tasks": ["とりあえず目標を紙に書く", "関連するYouTube動画を見る", "明日から本気出す"]}

@app.post("/api/preview-yumeochi")
async def preview_yumeochi(req: YumeochiRequest):
    boke_data = {
        "type": "yumeochi",
        "goal": req.goal,
        "boke_jp": f"ついに「{req.goal}」達成して世界中から賞賛されてるわ！…って夢見て起きたら、現実は「{req.report}」やったわ！泣けるで！",
        "boke_en": "Dreamt I achieved my goal, but reality is harsh!",
        "tsukkomi_1": {"emoji": "🔥", "jp": "知らんけど頑張れや！", "en": "Do your best!"},
        "tsukkomi_2": {"emoji": "💧", "jp": "よだれ拭けや！", "en": "Wipe your drool!"},
        "tsukkomi_3": {"emoji": "🤣", "jp": "夢は見れたな！", "en": "Nice dream!"}
    }
    boke_vector = [0.3] * 768
    
    prompt = f"""
    あなたは天才的なお笑い放送作家です。ユーザーが目標に向けた今日の進捗を報告しました。これを関西弁の一人称の『夢オチ』のボケ投稿に変換してください。
    
    【目標】: {req.goal}
    【今日の現実の報告】: {req.report}
    
    前半：「目標を達成して無双している最高の自分」を大げさに妄想してください。
    後半：「…ってニヤニヤしてたら目が覚めたわ！現実は（{req.report}）やんけ！」と情けなくオチをつけてください。
    
    その後、この投稿を見た人が気軽に押せる「知らんけど応援（優しめのツッコミ兼応援）」ボタンを3つ提案してください。
    必ず以下のJSONのみで返してください。
    {{
        "boke_jp": "関西弁の夢オチ投稿",
        "boke_en": "英語訳",
        "tsukkomi_1": {{"emoji": "絵文字", "jp": "応援ボタン1", "en": "Cheer 1"}},
        "tsukkomi_2": {{"emoji": "絵文字", "jp": "応援ボタン2", "en": "Cheer 2"}},
        "tsukkomi_3": {{"emoji": "絵文字", "jp": "応援ボタン3", "en": "Cheer 3"}}
    }}
    """
    
    try:
        response = ai_client.models.generate_content(model='gemini-2.5-flash', contents=prompt, config=types.GenerateContentConfig(response_mime_type="application/json"))
        ai_data = json.loads(clean_json(response.text))
        ai_data["type"] = "yumeochi"
        ai_data["goal"] = req.goal
        boke_data = ai_data
    except Exception as e: print(f"⚠️ 夢オチ生成エラー: {e}")

    try:
        emb_res = ai_client.models.embed_content(model='text-embedding-004', contents=boke_data.get("boke_en", "test"))
        boke_vector = emb_res.embeddings[0].values
    except Exception: pass
        
    return {"status": "success", "boke_data": boke_data, "boke_vector": boke_vector}


@app.post("/api/publish")
async def publish_post(req: PublishInput):
    boke_data = req.boke_data
    boke_data["author_name"] = req.author_name # 👈 JSONの中に投稿者の名前を埋め込む！
    
    db_res = supabase.table("boke_posts").insert({
        "author_id": req.author_id, 
        "boke_data": boke_data, 
        "boke_vector": req.boke_vector, 
        "is_mirai_nikki": False
    }).execute()
    return {"status": "success", "message": "世界に放流されました！", "post_id": db_res.data[0]["id"]}

@app.get("/api/feed")
async def get_feed():
    res = supabase.table("boke_posts").select("*").order("created_at", desc=True).limit(20).execute()
    return {"status": "success", "posts": res.data}