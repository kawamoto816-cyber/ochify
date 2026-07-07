import streamlit as st
import requests
import time
import uuid
import random
import urllib.parse
from streamlit_cookies_manager import EncryptedCookieManager

st.set_page_config(page_title="Ochify | World Peace through Comedy", page_icon="🌎", layout="centered", initial_sidebar_state="collapsed")

# 🚨 ブラウザのCookieを使って記憶を永続化
cookies = EncryptedCookieManager(prefix="ochify", password="super_secret_password_for_ochify_2026")
if not cookies.ready():
    st.stop()

st.markdown("""
<style>
    header[data-testid="stHeader"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    footer { display: none !important; }
    [data-testid="manage-app-button"], div[class^="viewerBadge"], [id^="viewerBadge"] { display: none !important; }
    .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
    .main {max-width: 500px; margin: 0 auto;}
    .post-card {background-color: transparent; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(128,128,128,0.1); border: 1px solid rgba(128,128,128,0.3);}
    .my-post {border: 2px solid #4b8bff; background-color: rgba(75, 139, 255, 0.05);}
    .main-text {font-size: 1.2rem; font-weight: bold; margin-bottom: 10px;}
    .preview-box {border: 2px dashed #ff4b4b; border-radius: 10px; padding: 15px; margin-top: 20px; background-color: transparent;}
    .task-box {background-color: transparent; border-radius: 10px; padding: 15px; margin-top: 10px; border: 1px solid #b3d9ff; margin-bottom: 15px;}
    .chat-bubble-me {background-color: #DCF8C6; color: #111 !important; padding: 10px 15px; border-radius: 20px; margin-bottom: 10px; text-align: right; width: fit-content; margin-left: auto; font-weight: bold;}
    .chat-bubble-other {background-color: #F1F0F0; color: #111 !important; padding: 10px 15px; border-radius: 20px; margin-bottom: 10px; width: fit-content; font-weight: bold;}
    .goal-badge {background-color: #ff4b4b; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.8rem; font-weight: bold; display: inline-block; margin-bottom: 10px;}
    .original-badge {background-color: #4b8bff; color: white; padding: 3px 8px; border-radius: 10px; font-size: 0.7rem; font-weight: bold; display: inline-block; margin-bottom: 5px;}
    .stTabs [data-baseweb="tab-list"] button {font-weight: bold; font-size: 1.05rem;}
    .app-title {font-size: 2.8rem; font-weight: 900; background: -webkit-linear-gradient(45deg, #ff4b4b, #ff904b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px; padding-bottom: 0px; letter-spacing: -1px;}
    .app-subtitle {font-size: 0.95rem; color: #888; font-style: italic; margin-top: -5px; margin-bottom: 15px;}
    .tutorial-box {background-color: #fff9e6; border-left: 5px solid #ffcc00; padding: 15px; margin-bottom: 20px; border-radius: 5px; color: #333;}
    .btn-ochify button { background: linear-gradient(45deg, #ff4b4b, #ff904b) !important; color: white !important; font-weight: 900 !important; font-size: 1.1rem !important; border: none !important; box-shadow: 0 4px 6px rgba(255, 75, 75, 0.4) !important;}
    .btn-ochify button:hover { opacity: 0.9; transform: scale(1.02); }
    div[data-testid="stRadio"] > div { flex-wrap: nowrap; overflow-x: auto; -webkit-overflow-scrolling: touch; padding-bottom: 5px; }
    div[data-testid="stRadio"] > div::-webkit-scrollbar { height: 4px; }
    div[data-testid="stRadio"] > div::-webkit-scrollbar-thumb { background-color: #ccc; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# 🚨 ご自身のRender URL
API_URL = "https://ochify-api.onrender.com"

if "user_id" not in st.session_state or st.session_state.user_id is None or st.session_state.user_id == "test_id":
    if cookies.get("user_id"):
        st.session_state.user_id = cookies.get("user_id")
        st.session_state.username = cookies.get("username")
    else:
        with st.spinner("🚀 Booting..."):
            try:
                res = requests.post(f"{API_URL}/api/init-user", timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.user_id = data.get("user_id")
                    st.session_state.username = data.get("username")
                else:
                    st.session_state.user_id = str(uuid.uuid4())
                    st.session_state.username = "名無しユーザー" + str(random.randint(10, 99))
            except:
                st.session_state.user_id = str(uuid.uuid4())
                st.session_state.username = "オフライン" + str(random.randint(10, 99))
            
            cookies["user_id"] = st.session_state.user_id
            cookies["username"] = st.session_state.username
            cookies.save()

if "lang" not in st.session_state: st.session_state.lang = "ja"
if "current_page" not in st.session_state: st.session_state.current_page = "🌍 フィード" 
if "tutorial_shown" not in st.session_state: st.session_state.tutorial_shown = False
if "preview_data" not in st.session_state: st.session_state.preview_data = None
if "preview_vector" not in st.session_state: st.session_state.preview_vector = None
if "chat_target" not in st.session_state: st.session_state.chat_target = None 
if "ndy_counts" not in st.session_state: st.session_state.ndy_counts = {}
if "my_goal" not in st.session_state: st.session_state.my_goal = ""
if "my_deadline" not in st.session_state: st.session_state.my_deadline = ""
if "ai_tasks" not in st.session_state: st.session_state.ai_tasks = []
if "input_text" not in st.session_state: st.session_state.input_text = ""
if "yume_step" not in st.session_state: st.session_state.yume_step = 1

is_ja = (st.session_state.lang == "ja")
def t(ja_text, en_text): return ja_text if is_ja else en_text

def handle_api_error(res):
    try: error_detail = res.json().get('detail', res.text)
    except: error_detail = res.text
    if "UNAVAILABLE" in error_detail or "high demand" in error_detail:
        st.error(t("⚠️ 現在、GoogleのAIサーバーが大混雑しています！数秒待ってからもう一度お試しください🙏", "⚠️ Google AI server is high demand. Please try again🙏"))
    else: 
        st.error(f"API Error: {error_detail}")

# --- ヘッダー領域 ---
st.markdown('<div class="app-title">Ochify</div>', unsafe_allow_html=True)
st.markdown(f'<div class="app-subtitle">{t("大阪のお笑いコミュニケーションで、世界平和を。", "World Peace through Osaka Comedy.")}</div>', unsafe_allow_html=True)

if not st.session_state.tutorial_shown:
    st.markdown(f"""
    <div class="tutorial-box">
        <h4 style="margin-top:0;">🔰 {t('Ochifyの遊び方', 'How to play Ochify')}</h4>
        <ol style="margin-bottom:0;">
            <li><b>{t('読む', 'Read')}</b>: {t('「🌍 フィード」で他人のボケに『✋なんでやねん！』とツッコミましょう。', 'Read posts and react with Nandeyanen!')}</li>
            <li><b>{t('書く', 'Post')}</b>: {t('「✍️ 投稿」から、普通の出来事をAIに「オチファイ」させて放流しましょう。', 'Write your story and let AI Ochify it.')}</li>
            <li><b>{t('繋がる', 'Connect')}</b>: {t('ツッコミをきっかけに、DMチャットで盛り上がりましょう！', 'Start DM chats from reactions!')}</li>
        </ol>
        <p style="margin-top:10px; font-size:0.8rem; color:#666;">{t('※既存SNSの「映え」のプレッシャーは捨てて、気楽に遊んでや！', '*Forget SNS pressure, just have fun!')}</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button(t("👍 わかった！(Let's Go!)", "Got it!"), type="primary", use_container_width=True):
        st.session_state.tutorial_shown = True
        st.rerun()

c1, c2 = st.columns([1.2, 1])
with c1: 
    st.markdown(f"<div style='margin-top:10px; font-size:0.9rem; color:#888;'>👤 {st.session_state.username}</div>", unsafe_allow_html=True)
with c2:
    lang_choice = st.radio("Lang", ["🇯🇵 日本語", "🌍 English"], index=0 if is_ja else 1, horizontal=True, label_visibility="collapsed")
    new_lang = "ja" if "日本語" in lang_choice else "en"
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

with st.expander(t("🔗 友達を招待・URLシェア", "🔗 Share with friends!")):
    share_url = "https://ochify-world.streamlit.app"
    share_text = t("Ochifyで大阪のお笑いコミュニケーションを体験しよう！😂", "Experience Osaka comedy communication on Ochify!😂")
    encoded_text = urllib.parse.quote(share_text)
    encoded_url = urllib.parse.quote(share_url)
    line_url = f"https://line.me/R/msg/text/?{encoded_text}%20{encoded_url}"
    x_url = f"https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}"
    fb_url = f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}"
    wa_url = f"https://api.whatsapp.com/send?text={encoded_text}%20{encoded_url}"
    ig_url = "https://www.instagram.com/" 
    
    st.write(t("👇 各種SNSへシェア！(Click to share)", "👇 Click to share!"))
    c_l, c_x, c_fb = st.columns(3)
    with c_l: st.link_button("💬 LINE", line_url, use_container_width=True)
    with c_x: st.link_button("𝕏 (X)", x_url, use_container_width=True)
    with c_fb: st.link_button("📘 FB", fb_url, use_container_width=True)
    c_w, c_i, c_e = st.columns(3)
    with c_w: st.link_button("🟩 WhatsApp", wa_url, use_container_width=True)
    with c_i: st.link_button("📸 Insta", ig_url, use_container_width=True)
    with c_e: st.empty() 
    st.markdown(t("<p style='font-size:0.75rem; color:#ff4b4b; margin-top:5px; font-weight:bold; line-height:1.2;'>※Instagramは仕様上、文字が自動入力されません。下の枠からURLをコピーしてストーリーズ等に貼り付けてください🙏</p>", "<p style='font-size:0.75rem; color:#ff4b4b; margin-top:5px; font-weight:bold; line-height:1.2;'>*Instagram doesn't support auto-text. Please copy the URL below and paste it🙏</p>"), unsafe_allow_html=True)
    st.code(share_url, language="text")

st.markdown("---")

pages = [t("🌍 フィード", "🌍 Feed"), t("✍️ 投稿", "✍️ Post"), t("👑 トレンド", "👑 Trend"), t("💬 DM", "💬 DM"), t("👤 マイページ", "👤 Profile")]
page_index = 0
if "Feed" in st.session_state.current_page or "フィード" in st.session_state.current_page: page_index = 0
elif "Post" in st.session_state.current_page or "投稿" in st.session_state.current_page: page_index = 1
elif "Trend" in st.session_state.current_page or "トレンド" in st.session_state.current_page: page_index = 2
elif "DM" in st.session_state.current_page or "チャット" in st.session_state.current_page: page_index = 3
elif "Profile" in st.session_state.current_page or "マイページ" in st.session_state.current_page: page_index = 4

selected_page = st.radio("Menu", pages, index=page_index, horizontal=True, label_visibility="collapsed")
if selected_page != st.session_state.current_page:
    st.session_state.current_page = selected_page
    st.rerun()

st.markdown("---")

def render_post_card(post, is_trend=False, rank=0, hide_actions=False):
    boke = post.get("boke_data")
    if not isinstance(boke, dict): boke = {}
    post_id = str(post.get("id"))
    author_id = str(post.get("author_id"))
    is_original = boke.get("is_original", False)
    is_mine = (author_id == st.session_state.user_id)
    author_name = post.get("author_name") or boke.get("author_name") or t("見知らぬユーザー", "Unknown User")
    
    db_count = post.get("nandeyanen_count") or 0
    local_count = st.session_state.ndy_counts.get(post_id, db_count)
    if db_count > local_count:
        local_count = db_count
        st.session_state.ndy_counts[post_id] = local_count

    st.markdown(f'<div class="post-card {"my-post" if is_mine else ""}">', unsafe_allow_html=True)
    if is_trend:
        medal = "🥇" if rank==1 else "🥈" if rank==2 else "🥉" if rank==3 else f"{rank}位"
        st.markdown(f"### {medal}", unsafe_allow_html=True)

    if is_mine: st.markdown(f"👤 **{author_name} ({t('あなた', 'You')})** <span style='color:#4b8bff; font-weight:bold; font-size:0.8rem;'>・{t('自分の投稿', 'Your Post')}</span>", unsafe_allow_html=True)
    else: st.markdown(f"👤 **{author_name}** <span style='color:gray; font-size:0.8rem;'>・Ochify</span>", unsafe_allow_html=True)
    
    if is_original:
        st.markdown(f'<div class="original-badge">✍️ {t("オリジナル投稿", "Original Post")}</div>', unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    if boke.get("type") == "yumeochi": st.markdown(f'<div class="goal-badge">🎯 {t("目標", "Goal")}: {boke.get("goal")}</div><br>', unsafe_allow_html=True)
    if boke.get("type") == "image" and "image_url" in boke:
        st.image(boke["image_url"], use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
    display_text = boke.get('boke_jp', '') if is_ja else boke.get('boke_en', '')
    if not display_text: display_text = t("（この投稿は現在表示できません）", "(Post not available)")
    st.markdown(f'<div class="main-text">{"🇯🇵" if is_ja else "🌍"} {display_text}</div>', unsafe_allow_html=True)
    
    if not hide_actions:
        if is_mine:
            st.markdown(f"<p style='font-size:0.8rem; color:#888;'>👇 {t('自分が集めたなんでやねんの数', 'Nandeyanen you received')}</p>", unsafe_allow_html=True)
            st.button(f"✋ {t('なんでやねん！', 'Nandeyanen!')} ({local_count})", key=f"nande_mine_{post_id}_{is_trend}", disabled=True)
        else:
            st.markdown(f"<p style='font-size:0.8rem; color:#888; margin-top:10px;'>👇 {t('いいねの代わりに愛のあるツッコミを！', 'Send Nandeyanen instead of Like!')}</p>", unsafe_allow_html=True)
            c1, c2 = st.columns([1, 1.5])
            with c1:
                if st.button(f"✋ {t('なんでやねん！', 'Nandeyanen!')} ({local_count})", key=f"nande_{post_id}_{is_trend}"):
                    st.session_state.ndy_counts[post_id] = local_count + 1
                    try: requests.post(f"{API_URL}/api/nandeyanen/{post_id}", timeout=2)
                    except: pass
                    st.rerun()
            with c2:
                with st.expander(t("💬 DMで直接ツッコむ", "💬 Reply in DM")):
                    t1, t2, t3 = boke.get('tsukkomi_1',{}), boke.get('tsukkomi_2',{}), boke.get('tsukkomi_3',{})
                    def start_dm(tsukkomi_text):
                        if author_id == st.session_state.user_id: return
                        if tsukkomi_text:
                            st.session_state.chat_target = {"id": author_id, "name": author_name}
                            payload = {"sender_id": st.session_state.user_id, "receiver_id": author_id, "sender_name": st.session_state.username, "receiver_name": author_name, "message_text": f"【ツッコミ】{tsukkomi_text}"}
                            try: requests.post(f"{API_URL}/api/send-message", json=payload, timeout=5)
                            except: pass
                            st.session_state.current_page = pages[3] 
                            
                    b1_txt = t1.get('jp','') if is_ja else t1.get('en','')
                    b2_txt = t2.get('jp','') if is_ja else t2.get('en','')
                    b3_txt = t3.get('jp','') if is_ja else t3.get('en','')
                    if b1_txt and st.button(f"{t1.get('emoji','')} {b1_txt}", key=f"t1_{post_id}_{is_trend}", use_container_width=True): start_dm(b1_txt); st.rerun()
                    if b2_txt and st.button(f"{t2.get('emoji','')} {b2_txt}", key=f"t2_{post_id}_{is_trend}", use_container_width=True): start_dm(b2_txt); st.rerun()
                    if b3_txt and st.button(f"{t3.get('emoji','')} {b3_txt}", key=f"t3_{post_id}_{is_trend}", use_container_width=True): start_dm(b3_txt); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if page_index == 0:
    if st.button(t("🔄 フィードを更新", "🔄 Refresh Feed"), use_container_width=True): st.rerun()
    with st.spinner(t("最新の投稿を取得中...", "Loading latest posts...")):
        try:
            feed_res = requests.get(f"{API_URL}/api/feed")
            if feed_res.status_code == 200:
                posts = feed_res.json().get("posts", [])
                if not posts: st.info(t("まだ投稿がありません。", "No posts yet."))
                else:
                    for post in posts:
                        try: render_post_card(post, is_trend=False)
                        except Exception: pass
            else: handle_api_error(feed_res)
        except Exception as e: st.error(f"通信エラー: {e}")

elif page_index == 1:
    tab1, tab2, tab3 = st.tabs([t("📝 オチファイ", "📝 Ochify"), t("📸 いじられ映え", "📸 Roast-bae"), t("🚀 シランケド", "🚀 Shirankedo")])
    with tab1:
        st.text_area(t("日常の出来事や、自分の最高のボケを書いてや！", "Write an event or your original joke!"), key="input_text", height=100)
        
        st.markdown(t("<p style='font-size:0.9rem; font-weight:bold; color:#888; margin-top:10px;'>💡 投稿のスタイルは？</p>", "<p style='font-size:0.9rem; font-weight:bold; color:#888; margin-top:10px;'>💡 Post Style</p>"), unsafe_allow_html=True)
        post_style = st.radio("Style", [
            t("🤖 AIにお任せ（誇張）", "🤖 AI: Exaggeration"), 
            t("🤖 AIにお任せ（自虐）", "🤖 AI: Self-deprecating"), 
            t("🤖 AIにお任せ（すっとぼけ）", "🤖 AI: Misunderstanding"),
            t("✍️ 自分のボケのまま（オリジナル）", "✍️ Keep my original joke")
        ], label_visibility="collapsed")
        
        is_original = "✍️" in post_style
        internal_boke_type = "オリジナル" if is_original else "誇張" if "💥" in post_style else "自虐" if "😭" in post_style else "勘違い"
        btn_text = t("✨ ① オチファイする", "✨ 1. Ochify it!") if not is_original else t("🚀 ① そのまま送信（翻訳とボタンだけ作る）", "🚀 1. Keep original (Generate buttons)")
        
        st.markdown('<div class="btn-ochify">', unsafe_allow_html=True)
        if st.button(btn_text, key="b1", type="primary", use_container_width=True):
            if st.session_state.input_text:
                success = False
                with st.spinner(t("AI放送作家が執筆中...", "AI is writing...")):
                    try:
                        payload = {"text": st.session_state.input_text, "boke_type": internal_boke_type, "is_original": is_original}
                        res = requests.post(f"{API_URL}/api/preview-boke", json=payload, timeout=60)
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state.preview_data = data.get("boke_data")
                            st.session_state.preview_vector = data.get("boke_vector")
                            success = True
                        else: handle_api_error(res)
                    except Exception as e: st.error(f"Network Error: {e}")
                if success: st.rerun() 
            else: st.warning(t("出来事を入力してください！", "Please enter an event!"))
        st.markdown('</div>', unsafe_allow_html=True)
            
    with tab2:
        uploaded_file = st.file_uploader(t("写真をアップロード", "Upload Photo"), type=["jpg", "jpeg", "png"])
        st.markdown('<div class="btn-ochify">', unsafe_allow_html=True)
        if uploaded_file and st.button(t("📸 ① いじられ映えさせる", "📸 1. Make it Roast-bae"), key="b2", type="primary", use_container_width=True):
            success = False
            with st.spinner(t("AIおかんがガン見中...", "AI analyzing image...")):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    res = requests.post(f"{API_URL}/api/preview-ijiri", files=files, timeout=60)
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.preview_data = data.get("boke_data")
                        st.session_state.preview_vector = data.get("boke_vector")
                        success = True
                    else: handle_api_error(res)
                except Exception as e: st.error(f"Network Error: {e}")
            if success: st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        if st.session_state.yume_step == 1:
            goal_input = st.text_input(t("達成したい目標は？", "Your goal?"), value=st.session_state.my_goal)
            deadline_input = st.text_input(t("いつまでに？", "By when?"), value=st.session_state.my_deadline)
            st.markdown('<div class="btn-ochify">', unsafe_allow_html=True)
            if st.button(t("🤖 AIに逆算タスクを作らせる", "🤖 Generate Tasks"), type="primary", use_container_width=True):
                if goal_input and deadline_input:
                    success = False
                    with st.spinner(t("考案中...", "Thinking...")):
                        try:
                            res = requests.post(f"{API_URL}/api/generate-tasks", json={"goal": goal_input, "deadline": deadline_input}, timeout=60)
                            if res.status_code == 200:
                                st.session_state.ai_tasks = res.json().get("tasks", [])
                                st.session_state.my_goal = goal_input
                                st.session_state.my_deadline = deadline_input
                                success = True
                            else: handle_api_error(res)
                        except Exception as e: st.error(f"Network Error: {e}")
                    if success: st.session_state.yume_step = 2; st.rerun()
                else: st.warning(t("目標と期日を入力してください！", "Please enter goal and deadline!"))
            st.markdown('</div>', unsafe_allow_html=True)
        elif st.session_state.yume_step == 2:
            st.success(f"🎯 {st.session_state.my_goal}")
            for i, task in enumerate(st.session_state.ai_tasks): st.markdown(f"☑️ **Task {i+1}:** {task}")
            st.markdown('<div class="btn-ochify">', unsafe_allow_html=True)
            if st.button(t("🔥 このタスクにコミットする！", "🔥 Commit!"), type="primary", use_container_width=True):
                st.session_state.yume_step = 3; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        elif st.session_state.yume_step == 3:
            st.write(f"**{st.session_state.my_goal}** ({t('期日', 'Deadline')}: {st.session_state.my_deadline})")
            report_input = st.text_area(t("今日できたこと（またはサボり）を報告！", "Report today's progress!"), height=80)
            st.markdown('<div class="btn-ochify">', unsafe_allow_html=True)
            if st.button(t("✨ 現実を「シランケド」に変換！", "✨ Convert to Shirankedo!"), type="primary", use_container_width=True):
                success = False
                with st.spinner(t("現実を笑いに変換中...", "Converting...")):
                    try:
                        res = requests.post(f"{API_URL}/api/preview-yumeochi", json={"goal": st.session_state.my_goal, "report": report_input}, timeout=60)
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state.preview_data = data.get("boke_data")
                            st.session_state.preview_vector = data.get("boke_vector")
                            success = True
                        else: handle_api_error(res)
                    except Exception as e: st.error(f"Network Error: {e}")
                if success: st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.preview_data:
        boke = st.session_state.preview_data
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.markdown(t("#### 💡 プレビュー (未公開)", "#### 💡 Preview (Private)"))
        
        if boke.get("is_original"): st.markdown(f'<div class="original-badge">✍️ {t("オリジナル投稿", "Original Post")}</div>', unsafe_allow_html=True)
        if boke.get("type") == "yumeochi": st.markdown(f'<div class="goal-badge">🎯 {t("目標", "Goal")}: {boke.get("goal")}</div>', unsafe_allow_html=True)
        if boke.get("type") == "image" and "image_url" in boke: 
            st.image(boke["image_url"], use_container_width=True)
            
        display_text = boke.get('boke_jp', '') if is_ja else boke.get('boke_en', '')
        st.markdown(f'<div class="main-text">{"🇯🇵" if is_ja else "🌍"} {display_text}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="btn-ochify">', unsafe_allow_html=True)
            if st.button(t("🚀 世界に放流する！", "🚀 Publish!"), type="primary", use_container_width=True):
                success = False
                with st.spinner(t("DBに保存中...", "Saving...")):
                    try:
                        payload = {
                            "author_id": st.session_state.user_id,
                            "author_name": st.session_state.username,
                            "boke_data": st.session_state.preview_data, 
                            "boke_vector": st.session_state.preview_vector
                        }
                        res = requests.post(f"{API_URL}/api/publish", json=payload, timeout=10)
                        if res.status_code == 200:
                            success = True
                        else: handle_api_error(res)
                    except Exception as e: st.error(f"通信エラー: {e}")
                if success:
                    st.session_state.preview_data = None
                    st.session_state.preview_vector = None
                    # 🚨 修正ポイント: ここにあった st.session_state.input_text = "" の強制リセットを完全に削除しました！
                    st.toast(t("🎉 投稿完了！", "🎉 Published!"), icon="✅")
                    time.sleep(1.5)
                    st.session_state.current_page = pages[0] 
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            if st.button(t("🗑 キャンセル", "🗑 Cancel"), use_container_width=True):
                st.session_state.preview_data = None
                st.session_state.preview_vector = None
                st.rerun()

elif page_index == 2:
    st.markdown(t("### 👑 トレンド", "### 👑 Trending"))
    st.write(t("世界中で一番「なんでやねん！」を集めている猛者たちです。", "The most 'Nandeyanen!' posts in the world."))
    if st.button(t("🔄 ランキングを更新", "🔄 Refresh Ranking"), use_container_width=True): st.rerun()
    with st.spinner(t("ランキングを集計中...", "Calculating trends...")):
        try:
            trend_res = requests.get(f"{API_URL}/api/trending")
            if trend_res.status_code == 200:
                posts = trend_res.json().get("posts", [])
                ranked_posts = [p for p in posts if (p.get("nandeyanen_count") or 0) > 0 or st.session_state.ndy_counts.get(str(p.get("id")), 0) > 0]
                if not ranked_posts: st.info(t("まだ誰も「なんでやねん」されていません！フィードでツッコミを入れてみよう。", "No Nandeyanen yet. Go to Feed and react!"))
                else:
                    for i, post in enumerate(ranked_posts[:10]):
                        try: render_post_card(post, is_trend=True, rank=i+1)
                        except Exception as e: pass
            else: handle_api_error(trend_res)
        except Exception as e: st.error(f"通信エラー: {e}")

elif page_index == 3:
    st.markdown(t("### 💬 DMルーム", "### 💬 DM Room"))
    messages = []
    try:
        res = requests.get(f"{API_URL}/api/messages/{st.session_state.user_id}", timeout=10)
        if res.status_code == 200: messages = res.json().get("messages", [])
    except: pass
        
    contacts = {}
    for m in messages:
        if m["sender_id"] != st.session_state.user_id: contacts[m["sender_id"]] = m["sender_name"]
        if m["receiver_id"] != st.session_state.user_id: contacts[m["receiver_id"]] = m["receiver_name"]
            
    if st.session_state.chat_target:
        tgt_id = st.session_state.chat_target["id"]
        if tgt_id not in contacts: contacts[tgt_id] = st.session_state.chat_target["name"]

    if not contacts:
        st.info(t("まだ誰ともチャットしていません。フィードで誰かの投稿にツッコミを入れてみましょう！", "No chats yet. React to a feed post!"))
    else:
        contact_options = [f"{v} (ID: {k[:4]})" for k, v in contacts.items()]
        default_index = 0
        if st.session_state.chat_target:
            tgt_str = f"{st.session_state.chat_target['name']} (ID: {st.session_state.chat_target['id'][:4]})"
            if tgt_str in contact_options: default_index = contact_options.index(tgt_str)
                
        selected_contact_str = st.selectbox(t("📩 トーク相手を選択", "Select contact"), contact_options, index=default_index)
        target_id = None
        for k, v in contacts.items():
            if f"{v} (ID: {k[:4]})" == selected_contact_str:
                target_id = k; break
                
        if target_id:
            st.session_state.chat_target = {"id": target_id, "name": contacts[target_id]}
            st.markdown(f"#### 👤 **{contacts[target_id]}**")
            
            if hasattr(st, "fragment"):
                @st.fragment(run_every=5)
                def auto_refresh_chat():
                    try:
                        r = requests.get(f"{API_URL}/api/messages/{st.session_state.user_id}", timeout=5)
                        all_msgs = r.json().get("messages", []) if r.status_code == 200 else []
                    except: all_msgs = []
                    
                    chat_msgs = [m for m in all_msgs if (m["sender_id"] == target_id and m["receiver_id"] == st.session_state.user_id) or (m["sender_id"] == st.session_state.user_id and m["receiver_id"] == target_id)]
                    with st.container(border=True, height=350):
                        if not chat_msgs: st.write("No messages.")
                        else:
                            for m in chat_msgs:
                                if m["sender_id"] == st.session_state.user_id: st.markdown(f"<div class='chat-bubble-me'>{m['message_text']}</div>", unsafe_allow_html=True)
                                else: st.markdown(f"<div class='chat-bubble-other'>{m['message_text']}</div>", unsafe_allow_html=True)
                auto_refresh_chat()
            else:
                chat_msgs = [m for m in messages if (m["sender_id"] == target_id and m["receiver_id"] == st.session_state.user_id) or (m["sender_id"] == st.session_state.user_id and m["receiver_id"] == target_id)]
                with st.container(border=True, height=350):
                    if not chat_msgs: st.write("No messages.")
                    else:
                        for m in chat_msgs:
                            if m["sender_id"] == st.session_state.user_id: st.markdown(f"<div class='chat-bubble-me'>{m['message_text']}</div>", unsafe_allow_html=True)
                            else: st.markdown(f"<div class='chat-bubble-other'>{m['message_text']}</div>", unsafe_allow_html=True)
                if st.button("🔄 手動更新"): st.rerun()

            st.markdown("---")
            with st.form("dm_form", clear_on_submit=True):
                dm_input = st.text_input(t("メッセージを送信...", "Send message..."))
                submit_btn = st.form_submit_button(t("送信", "Send"), type="primary", use_container_width=True)
                if submit_btn and dm_input:
                    payload = {"sender_id": st.session_state.user_id, "receiver_id": target_id, "sender_name": st.session_state.username, "receiver_name": contacts[target_id], "message_text": dm_input}
                    try: requests.post(f"{API_URL}/api/send-message", json=payload, timeout=5)
                    except: pass
                    st.rerun()

elif page_index == 4:
    st.markdown(t("### 👤 マイページ", "### 👤 My Profile"))
    
    with st.expander(t("⚙️ アカウント設定（名前変更・復元）", "⚙️ Account Settings"), expanded=True):
        new_name = st.text_input(t("ニックネームを変更", "Change Nickname"), value=st.session_state.username)
        if st.button(t("名前を変更する", "Update Name"), type="primary"):
            if new_name and len(new_name.strip()) > 0:
                with st.spinner("Saving..."):
                    try:
                        res = requests.post(f"{API_URL}/api/update-user", json={"user_id": st.session_state.user_id, "new_name": new_name.strip()}, timeout=10)
                        if res.status_code == 200:
                            st.session_state.username = new_name.strip()
                            cookies["username"] = st.session_state.username
                            cookies.save()
                            st.success(t("✅ ニックネームを変更しました！", "✅ Nickname updated!"))
                            time.sleep(1)
                            st.rerun()
                        else: handle_api_error(res)
                    except Exception as e: st.error("Error")
        
        st.markdown("---")
        st.write(t("タブを閉じて別人になってしまった時のための『復元コード』です。メモしておいてください。", "Save this restore code to recover your account if you close the tab."))
        st.code(f"{st.session_state.user_id}:::{st.session_state.username}", language="text")
        restore_input = st.text_input(t("復元コードを入力して元に戻る", "Enter restore code to recover"))
        if st.button(t("アカウントを復元する", "Restore Account")):
            if ":::" in restore_input:
                parts = restore_input.split(":::")
                if len(parts) == 2:
                    st.session_state.user_id = parts[0].strip()
                    st.session_state.username = parts[1].strip()
                    cookies["user_id"] = st.session_state.user_id
                    cookies["username"] = st.session_state.username
                    cookies.save()
                    st.success(t("✅ 過去の自分を取り戻しました！", "✅ Restored!"))
                    time.sleep(1.5)
                    st.rerun()

    st.markdown("---")
    st.markdown(t("#### 📜 あなたの過去の投稿", "#### 📜 Your Past Posts"))
    if st.button(t("🔄 履歴を更新", "🔄 Refresh History"), use_container_width=True): st.rerun()
    with st.spinner(t("読み込み中...", "Loading...")):
        try:
            feed_res = requests.get(f"{API_URL}/api/my-posts/{st.session_state.user_id}")
            if feed_res.status_code == 200:
                posts = feed_res.json().get("posts", [])
                if not posts: st.info(t("まだ投稿がありません。最初のオチファイを放流しましょう！", "No posts yet. Let's Ochify something!"))
                else:
                    for post in posts:
                        try: render_post_card(post, is_trend=False, hide_actions=True)
                        except Exception: pass
            else: handle_api_error(feed_res)
        except Exception as e: st.error(f"Error: {e}")