import streamlit as st
import requests
import time
import uuid   # 🚨 追加：自力でUUIDを生成するための魔法の杖
import random # 🚨 追加：自力で名前を生成するための魔法の杖

st.set_page_config(page_title="Ochify | World Peace through Comedy", page_icon="🌎", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    /* 💥 【究極魔法】Streamlitのヘッダーを丸ごと消し去る！これでForkもGitHubも完全に消滅します！ */
    header[data-testid="stHeader"] { display: none !important; }
    
    /* サイドバーも完全に隠す */
    [data-testid="stSidebar"] { display: none !important; }

    /* 👑 右下のStreamlitフッターや不要な帯も完全に消去 */
    footer { display: none !important; }
    [data-testid="manage-app-button"] { display: none !important; }
    div[class^="viewerBadge"] { display: none !important; }
    [id^="viewerBadge"] { display: none !important; }

    /* メインコンテナの上の余白を詰めてスマホアプリっぽくする */
    .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
    
    .main {max-width: 500px; margin: 0 auto;}
    /* 🌙 ダークモード対応 */
    .post-card {background-color: transparent; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(128,128,128,0.1); border: 1px solid rgba(128,128,128,0.3);}
    .my-post {border: 2px solid #4b8bff; background-color: rgba(75, 139, 255, 0.05);}
    .main-text {font-size: 1.2rem; font-weight: bold; margin-bottom: 10px;}
    .preview-box {border: 2px dashed #ff4b4b; border-radius: 10px; padding: 15px; margin-top: 20px; background-color: transparent;}
    .task-box {background-color: transparent; border-radius: 10px; padding: 15px; margin-top: 10px; border: 1px solid #b3d9ff; margin-bottom: 15px;}
    
    .chat-bubble-me {background-color: #DCF8C6; color: #111 !important; padding: 10px 15px; border-radius: 20px; margin-bottom: 10px; text-align: right; width: fit-content; margin-left: auto; font-weight: bold;}
    .chat-bubble-other {background-color: #F1F0F0; color: #111 !important; padding: 10px 15px; border-radius: 20px; margin-bottom: 10px; width: fit-content; font-weight: bold;}
    
    .goal-badge {background-color: #ff4b4b; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.8rem; font-weight: bold; display: inline-block; margin-bottom: 10px;}
    .stTabs [data-baseweb="tab-list"] button {font-weight: bold; font-size: 1.05rem;}
    
    .app-title {font-size: 2.8rem; font-weight: 900; background: -webkit-linear-gradient(45deg, #ff4b4b, #ff904b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px; padding-bottom: 0px; letter-spacing: -1px;}
    .app-subtitle {font-size: 0.95rem; color: #888; font-style: italic; margin-top: -5px; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

# 🚨 【超重要】ここのURLをご自身のRenderのURL（https://...onrender.com）にしてください
API_URL = "https://ochify-api.onrender.com"

# Session State
if "lang" not in st.session_state: st.session_state.lang = "ja"
if "user_id" not in st.session_state: st.session_state.user_id = None
if "username" not in st.session_state: st.session_state.username = "Unknown"
if "current_page" not in st.session_state: st.session_state.current_page = "✍️ 投稿"
if "preview_data" not in st.session_state: st.session_state.preview_data = None
if "preview_vector" not in st.session_state: st.session_state.preview_vector = None
if "dm_history" not in st.session_state: st.session_state.dm_history = []
if "input_text" not in st.session_state: st.session_state.input_text = "" 
if "yume_step" not in st.session_state: st.session_state.yume_step = 1
if "my_goal" not in st.session_state: st.session_state.my_goal = ""
if "my_deadline" not in st.session_state: st.session_state.my_deadline = ""
if "ai_tasks" not in st.session_state: st.session_state.ai_tasks = []
if "ndy_counts" not in st.session_state: st.session_state.ndy_counts = {}

is_ja = (st.session_state.lang == "ja")
def t(ja_text, en_text): return ja_text if is_ja else en_text

def handle_api_error(res):
    try: error_detail = res.json().get('detail', res.text)
    except: error_detail = res.text
    if "503" in error_detail or "UNAVAILABLE" in error_detail or "high demand" in error_detail:
        st.error(t("⚠️ 現在、GoogleのAIサーバーが大混雑しています！数秒待ってからもう一度お試しください🙏", "⚠️ Google AI server is currently experiencing high demand. Please try again in a few seconds🙏"))
    elif "boke_posts" in error_detail or "posts" in error_detail:
        st.error(t(f"データベース設定エラー: {error_detail}", f"DB Schema Error: {error_detail}"))
    else: st.error(f"API Error: {error_detail}")

# 🚨 ここが修正ポイント！ test_id の場合は強制リセットし、通信エラー時でも自力で有効なUUIDを生成する
if st.session_state.user_id is None or st.session_state.user_id == "test_id":
    with st.spinner(t("🚀 起動中...", "🚀 Booting...")):
        fallback_uuid = str(uuid.uuid4())
        names = ["アホの坂田", "浪速の商人", "たこ焼き職人", "通天閣の虎", "くいだおれ太郎"]
        fallback_name = random.choice(names) + str(random.randint(10, 99))
        try:
            res = requests.post(f"{API_URL}/api/init-user", timeout=10)
            if res.status_code == 200:
                data = res.json()
                st.session_state.user_id = data.get("user_id")
                st.session_state.username = data.get("username")
            else:
                st.session_state.user_id = fallback_uuid
                st.session_state.username = fallback_name
        except:
            st.session_state.user_id = fallback_uuid
            st.session_state.username = fallback_name

# ==========================================
# 🌟 新UI：ヘッダー（タイトルとメニューを画面内に配置）
# ==========================================
st.markdown('<div class="app-title">Ochify</div>', unsafe_allow_html=True)
st.markdown(f'<div class="app-subtitle">{t("大阪のお笑いコミュニケーションで、世界平和を。", "World Peace through Osaka Comedy.")}</div>', unsafe_allow_html=True)

# ユーザー情報と設定タブ
c1, c2 = st.columns([1.2, 1])
with c1:
    st.markdown(f"<div style='margin-top:10px; font-size:0.9rem; color:#888;'>👤 {st.session_state.username}</div>", unsafe_allow_html=True)
with c2:
    lang_choice = st.radio("Lang", ["🇯🇵 日本語", "🌍 English"], index=0 if is_ja else 1, horizontal=True, label_visibility="collapsed")
    new_lang = "ja" if "日本語" in lang_choice else "en"
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

st.markdown("---")

# アプリ風タブメニュー
pages = [t("✍️ 投稿", "✍️ Post"), t("🌍 フィード", "🌍 Feed"), t("👑 トレンド", "👑 Trend"), t("💬 DM", "💬 DM")]
page_index = 0
if "Feed" in st.session_state.current_page or "フィード" in st.session_state.current_page: page_index = 1
elif "Trend" in st.session_state.current_page or "トレンド" in st.session_state.current_page: page_index = 2
elif "DM" in st.session_state.current_page or "チャット" in st.session_state.current_page: page_index = 3

selected_page = st.radio("Menu", pages, index=page_index, horizontal=True, label_visibility="collapsed")
if selected_page != st.session_state.current_page:
    st.session_state.current_page = selected_page
    st.rerun()

st.markdown("---")

# ==========================================
# 共通関数: 投稿カード
# ==========================================
def render_post_card(post, is_trend=False, rank=0):
    boke = post.get("boke_data")
    if not isinstance(boke, dict): boke = {}
    post_id = str(post.get("id"))
    is_mine = (post.get("author_id") == st.session_state.user_id)
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
    st.markdown("<br>", unsafe_allow_html=True)
    
    if boke.get("type") == "yumeochi": st.markdown(f'<div class="goal-badge">🎯 {t("目標", "Goal")}: {boke.get("goal")}</div><br>', unsafe_allow_html=True)
    if boke.get("type") == "image" and "image_url" in boke:
        st.image(boke["image_url"], use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
    display_text = boke.get('boke_jp', '') if is_ja else boke.get('boke_en', '')
    if not display_text: display_text = t("（この投稿は現在表示できません）", "(Post not available)")
    st.markdown(f'<div class="main-text">{"🇯🇵" if is_ja else "🌍"} {display_text}</div>', unsafe_allow_html=True)
    
    if is_mine:
        st.markdown(f"<p style='font-size:0.8rem; color:#888;'>👇 {t('自分でツッコむと痛い奴やで！', 'Cannot react to yourself.')}</p>", unsafe_allow_html=True)
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
                    if tsukkomi_text:
                        st.session_state.dm_history.append({"me": tsukkomi_text, "other": t("なんでやねん！笑", "Lol, what!")})
                        st.session_state.current_page = pages[3]
                b1_txt = t1.get('jp','') if is_ja else t1.get('en','')
                b2_txt = t2.get('jp','') if is_ja else t2.get('en','')
                b3_txt = t3.get('jp','') if is_ja else t3.get('en','')
                if b1_txt and st.button(f"{t1.get('emoji','')} {b1_txt}", key=f"t1_{post_id}_{is_trend}", use_container_width=True): start_dm(b1_txt); st.rerun()
                if b2_txt and st.button(f"{t2.get('emoji','')} {b2_txt}", key=f"t2_{post_id}_{is_trend}", use_container_width=True): start_dm(b2_txt); st.rerun()
                if b3_txt and st.button(f"{t3.get('emoji','')} {b3_txt}", key=f"t3_{post_id}_{is_trend}", use_container_width=True): start_dm(b3_txt); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# ✍️ 投稿ルーム
# ==========================================
if page_index == 0:
    tab1, tab2, tab3 = st.tabs([t("📝 オチファイ", "📝 Ochify"), t("📸 いじられ映え", "📸 Roast-bae"), t("🚀 シランケド", "🚀 Shirankedo")])
    with tab1:
        st.text_area(t("オチのない普通の出来事を書いてや！", "Write an ordinary event!"), key="input_text", height=100)
        st.markdown(t("<p style='font-size:0.9rem; font-weight:bold; color:#888; margin-top:10px;'>🎭 どんなテイストでオチファイする？</p>", "<p style='font-size:0.9rem; font-weight:bold; color:#888; margin-top:10px;'>🎭 Choose Comedy Style</p>"), unsafe_allow_html=True)
        boke_type = st.radio("Style", [t("💥 誇張（話を盛る）", "💥 Exaggeration"), t("😭 自虐（悲しいけど笑える）", "😭 Self-deprecating"), t("🤪 勘違い（すっとぼけ）", "🤪 Misunderstanding")], horizontal=True, label_visibility="collapsed")
        internal_boke_type = "誇張" if "💥" in boke_type else "自虐" if "😭" in boke_type else "勘違い"
        if st.button(t("✨ ① オチファイする", "✨ 1. Ochify it!"), key="b1", use_container_width=True):
            if st.session_state.input_text:
                success = False
                with st.spinner(t("AI放送作家が執筆中...", "AI is writing...")):
                    try:
                        res = requests.post(f"{API_URL}/api/preview-boke", json={"text": st.session_state.input_text, "boke_type": internal_boke_type}, timeout=60)
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state.preview_data = data.get("boke_data")
                            st.session_state.preview_vector = data.get("boke_vector")
                            success = True
                        else: handle_api_error(res)
                    except Exception as e: st.error(f"Network Error: {e}")
                if success: st.rerun() 
            else: st.warning(t("出来事を入力してください！", "Please enter an event!"))
            
    with tab2:
        uploaded_file = st.file_uploader(t("写真をアップロード", "Upload Photo"), type=["jpg", "jpeg", "png"])
        if uploaded_file and st.button(t("📸 ① いじられ映えさせる", "📸 1. Make it Roast-bae"), key="b2", use_container_width=True):
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

    with tab3:
        if st.session_state.yume_step == 1:
            goal_input = st.text_input(t("達成したい目標は？", "Your goal?"), value=st.session_state.my_goal)
            deadline_input = st.text_input(t("いつまでに？", "By when?"), value=st.session_state.my_deadline)
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
        elif st.session_state.yume_step == 2:
            st.success(f"🎯 {st.session_state.my_goal}")
            for i, task in enumerate(st.session_state.ai_tasks): st.markdown(f"☑️ **Task {i+1}:** {task}")
            if st.button(t("🔥 このタスクにコミットする！", "🔥 Commit!"), type="primary", use_container_width=True):
                st.session_state.yume_step = 3; st.rerun()
        elif st.session_state.yume_step == 3:
            st.write(f"**{st.session_state.my_goal}** ({t('期日', 'Deadline')}: {st.session_state.my_deadline})")
            report_input = st.text_area(t("今日できたこと（またはサボり）を報告！", "Report today's progress!"), height=80)
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

    if st.session_state.preview_data:
        boke = st.session_state.preview_data
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.markdown(t("#### 💡 プレビュー (未公開)", "#### 💡 Preview (Private)"))
        if boke.get("type") == "yumeochi": st.markdown(f'<div class="goal-badge">🎯 {t("目標", "Goal")}: {boke.get("goal")}</div>', unsafe_allow_html=True)
        if boke.get("type") == "image" and "image_url" in boke: st.image(boke["image_url"], use_container_width=True)
        display_text = boke.get('boke_jp', '') if is_ja else boke.get('boke_en', '')
        st.markdown(f'<div class="main-text">{"🇯🇵" if is_ja else "🌍"} {display_text}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button(t("🚀 世界に放流する！", "🚀 Publish to World!"), type="primary", use_container_width=True):
                success = False
                with st.spinner(t("DBに保存中...", "Saving...")):
                    try:
                        payload = {"author_id": st.session_state.user_id, "author_name": st.session_state.username, "boke_data": st.session_state.preview_data, "boke_vector": st.session_state.preview_vector}
                        res = requests.post(f"{API_URL}/api/publish", json=payload, timeout=10)
                        if res.status_code == 200: success = True
                        else: handle_api_error(res)
                    except Exception as e: st.error(f"通信エラー: {e}")
                if success:
                    st.session_state.preview_data = None; st.session_state.preview_vector = None
                    st.toast(t("🎉 投稿完了！", "🎉 Published!"), icon="✅")
                    time.sleep(1.5)
                    st.session_state.current_page = pages[1]
                    st.rerun()
        with c2:
            if st.button(t("🗑 キャンセル", "🗑 Cancel"), use_container_width=True):
                st.session_state.preview_data = None; st.session_state.preview_vector = None; st.rerun()

elif page_index == 1:
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
                        except: pass
            else: handle_api_error(feed_res)
        except Exception as e: st.error(f"通信エラー: {e}")

elif page_index == 2:
    st.write(t("世界中で一番「なんでやねん！」を集めている猛者たちです。", "The most 'Nandeyanen!' posts in the world."))
    if st.button(t("🔄 ランキングを更新", "🔄 Refresh Ranking"), use_container_width=True): st.rerun()
    with st.spinner(t("ランキングを集計中...", "Calculating trends...")):
        try:
            trend_res = requests.get(f"{API_URL}/api/trending")
            if trend_res.status_code == 200:
                posts = trend_res.json().get("posts", [])
                ranked_posts = [p for p in posts if (p.get("nandeyanen_count") or 0) > 0 or st.session_state.ndy_counts.get(str(p.get("id")), 0) > 0]
                if not ranked_posts: st.info(t("まだ誰も「なんでやねん」されていません！", "No Nandeyanen yet."))
                else:
                    for i, post in enumerate(ranked_posts[:10]):
                        try: render_post_card(post, is_trend=True, rank=i+1)
                        except: pass
            else: handle_api_error(trend_res)
        except Exception as e: st.error(f"通信エラー: {e}")

elif page_index == 3:
    if not st.session_state.dm_history: st.info(t("まだ誰ともチャットしていません。", "No chats yet."))
    else:
        with st.container(border=True):
            st.markdown(t("👤 **見知らぬ相手**", "👤 **Stranger**"))
            st.markdown("---")
            for dm in st.session_state.dm_history:
                st.markdown(f"<div class='chat-bubble-me'>{t('あなた', 'You')}: {dm['me']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='chat-bubble-other'>{t('相手', 'Them')}: {dm['other']}</div>", unsafe_allow_html=True)
            st.markdown("---")
            dm_input = st.text_input(t("メッセージを送信...", "Send message..."), key="dm_input_text")
            if st.button(t("送信", "Send"), type="primary", use_container_width=True):
                if dm_input:
                    st.session_state.dm_history.append({"me": dm_input, "other": t("ほんまそれな！笑（※体験版モック）", "Exactly! lol (Mock)")})
                    st.rerun()