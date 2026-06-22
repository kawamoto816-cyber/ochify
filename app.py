import streamlit as st
import requests
import time

# 🌍 アプリの正式名称を「Ochify」に変更！
st.set_page_config(page_title="Ochify | World Peace through Comedy", page_icon="🌎", layout="centered")

st.markdown("""
<style>
    .main {max-width: 500px; margin: 0 auto;}
    .post-card {background-color: #ffffff; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); border: 1px solid #eee;}
    .my-post {border: 2px solid #4b8bff; background-color: #f8fbff;}
    .main-text {font-size: 1.2rem; font-weight: bold; color: #333; margin-bottom: 10px;}
    .preview-box {border: 2px dashed #ff4b4b; border-radius: 10px; padding: 15px; margin-top: 20px; background-color: #fffaf0;}
    .task-box {background-color: #e6f3ff; border-radius: 10px; padding: 15px; margin-top: 10px; border: 1px solid #b3d9ff; margin-bottom: 15px;}
    .chat-bubble-me {background-color: #DCF8C6; padding: 10px 15px; border-radius: 20px; margin-bottom: 10px; text-align: right; width: fit-content; margin-left: auto;}
    .chat-bubble-other {background-color: #F1F0F0; padding: 10px 15px; border-radius: 20px; margin-bottom: 10px; width: fit-content;}
    .goal-badge {background-color: #ff4b4b; color: white; padding: 5px 10px; border-radius: 15px; font-size: 0.8rem; font-weight: bold; display: inline-block; margin-bottom: 10px;}
    .stTabs [data-baseweb="tab-list"] button {font-weight: bold; font-size: 1.05rem;}
    
    /* 🌟 アプリ名ロゴとビジョンのスタイル */
    .app-title {font-size: 2.8rem; font-weight: 900; background: -webkit-linear-gradient(45deg, #ff4b4b, #ff904b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0px; padding-bottom: 0px; letter-spacing: -1px;}
    .app-subtitle {font-size: 0.95rem; color: #666; font-style: italic; margin-top: -5px; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

if "lang" not in st.session_state: st.session_state.lang = "ja"
st.sidebar.title("🌐 Language / 言語")
lang_choice = st.sidebar.radio("Select Language", ["🇯🇵 日本語", "🌍 English"], index=0 if st.session_state.lang=="ja" else 1, label_visibility="collapsed")
selected_lang = "ja" if "日本語" in lang_choice else "en"

if selected_lang != st.session_state.lang:
    st.session_state.lang = selected_lang
    st.rerun()

is_ja = (st.session_state.lang == "ja")

def t(ja_text, en_text):
    return ja_text if is_ja else en_text

if "user_id" not in st.session_state:
    with st.spinner(t("🚀 アカウントを自動生成中...", "🚀 Booting...")):
        try:
            res = requests.post("http://127.0.0.1:8000/api/init-user", timeout=10)
            if res.status_code == 200:
                data = res.json()
                st.session_state.user_id = data.get("user_id")
                st.session_state.username = data.get("username")
            else:
                st.session_state.user_id = "test_id"
                st.session_state.username = t("名無しユーザー", "Unknown User")
        except Exception as e:
            st.session_state.user_id = "test_id"
            st.session_state.username = t("オフライン", "Offline User")

if "current_page" not in st.session_state: st.session_state.current_page = "✍️ 投稿ルーム / Post"
if "preview_data" not in st.session_state: st.session_state.preview_data = None
if "preview_vector" not in st.session_state: st.session_state.preview_vector = None
if "dm_history" not in st.session_state: st.session_state.dm_history = []
if "input_text" not in st.session_state: st.session_state.input_text = "" 
if "yume_step" not in st.session_state: st.session_state.yume_step = 1
if "my_goal" not in st.session_state: st.session_state.my_goal = ""
if "my_deadline" not in st.session_state: st.session_state.my_deadline = ""
if "ai_tasks" not in st.session_state: st.session_state.ai_tasks = []

st.sidebar.markdown("---")
# 🌟 メニュー名もOchifyに
st.sidebar.title(t("📱 Ochify メニュー", "📱 Ochify Menu"))
st.sidebar.success(t(f"👤 あなたの正体:\n**{st.session_state.username}**", f"👤 Your Identity:\n**{st.session_state.username}**"))

pages = [t("✍️ 投稿ルーム (自分)", "✍️ Post Room"), t("🌍 フィード (みんな)", "🌍 Global Feed"), t("💬 DMチャット", "💬 DM Chat")]
page_index = 0
if "Feed" in st.session_state.current_page or "フィード" in st.session_state.current_page: page_index = 1
elif "DM" in st.session_state.current_page or "チャット" in st.session_state.current_page: page_index = 2

selected_page = st.sidebar.radio(t("モード切替", "Navigation"), pages, index=page_index, label_visibility="collapsed")
if selected_page != st.session_state.current_page:
    st.session_state.current_page = selected_page
    st.rerun()

# 🌟 画面上部にOchifyロゴと世界平和のビジョンを配置！
st.markdown('<div class="app-title">Ochify</div>', unsafe_allow_html=True)
st.markdown(f'<div class="app-subtitle">{t("大阪のお笑いコミュニケーションで、世界平和を。", "World Peace through Osaka Comedy.")}</div>', unsafe_allow_html=True)

# ==========================================
# ✍️ 投稿ルーム
# ==========================================
if page_index == 0:
    
    # 🌟 CEOのビジョンを反映した最終決定のタブ名！
    tab1, tab2, tab3 = st.tabs([t("📝 オチファイ", "📝 Ochify"), t("📸 いじられ映え", "📸 Roast-bae"), t("🚀 シランケド", "🚀 Shirankedo")])
    
    with tab1:
        st.text_area(t("オチのない普通の出来事を書いてや！", "Write an ordinary event with no punchline!"), key="input_text", height=100)
        st.markdown(t("<p style='font-size:0.9rem; font-weight:bold; color:#555; margin-top:10px;'>🎭 どんなテイストでオチファイする？</p>", "<p style='font-size:0.9rem; font-weight:bold; color:#555; margin-top:10px;'>🎭 Choose Comedy Style</p>"), unsafe_allow_html=True)
        boke_type = st.radio("Style", [t("💥 誇張（話を盛る）", "💥 Exaggeration"), t("😭 自虐（悲しいけど笑える）", "😭 Self-deprecating"), t("🤪 勘違い（すっとぼけ）", "🤪 Misunderstanding")], horizontal=True, label_visibility="collapsed")
        
        internal_boke_type = "誇張" if "💥" in boke_type else "自虐" if "😭" in boke_type else "勘違い"
        
        # 🌟 ボタン名も「オチファイする」に変更
        if st.button(t("✨ ① オチファイする（何度でも変更OK！）", "✨ 1. Ochify it! (Redo anytime)"), key="b1", use_container_width=True):
            if st.session_state.input_text:
                with st.spinner(t("AI放送作家が執筆中...", "AI is writing...")):
                    try:
                        res = requests.post("http://127.0.0.1:8000/api/preview-boke", json={"text": st.session_state.input_text, "boke_type": internal_boke_type}, timeout=60).json()
                        st.session_state.preview_data = res.get("boke_data")
                        st.session_state.preview_vector = res.get("boke_vector")
                        st.rerun()
                    except Exception: st.error("Error")
            else: st.warning(t("⚠️ 出来事を入力してください！", "⚠️ Please enter an event!"))

    with tab2:
        uploaded_file = st.file_uploader(t("写真をアップロード", "Upload Photo"), type=["jpg", "jpeg", "png"])
        if uploaded_file and st.button(t("📸 ① いじられ映えさせる", "📸 1. Make it Roast-bae"), key="b2", use_container_width=True):
            with st.spinner(t("AIおかんが画像をガン見中...", "AI is analyzing image...")):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    res = requests.post("http://127.0.0.1:8000/api/preview-ijiri", files=files, timeout=60).json()
                    st.session_state.preview_data = res.get("boke_data")
                    st.session_state.preview_vector = res.get("boke_vector")
                    st.rerun()
                except Exception: st.error("Error")

    with tab3:
        st.info(t("💡 意識高い目標もサボりも、最後は「シランケド」で笑いに変えます！", "💡 AI turns your ambitious goals and lazy realities into comedy. Shirankedo!"))
        if st.session_state.yume_step == 1:
            st.markdown(t("### 🎯 ① やったる（目標宣言）", "### 🎯 1. Declare Goal (Yattaru)"))
            goal_input = st.text_input(t("達成したいガチの目標・夢は？", "Your serious goal?"), value=st.session_state.my_goal)
            deadline_input = st.text_input(t("いつまでに？（期日）", "By when? (Deadline)"), value=st.session_state.my_deadline)
            if st.button(t("🤖 AIに逆算タスクを作らせる", "🤖 Generate Tasks with AI"), type="primary", use_container_width=True):
                if goal_input and deadline_input:
                    with st.spinner(t("AIが最短ルートのタスクを考案中...", "AI is thinking...")):
                        try:
                            res = requests.post("http://127.0.0.1:8000/api/generate-tasks", json={"goal": goal_input, "deadline": deadline_input}, timeout=60).json()
                            st.session_state.ai_tasks = res.get("tasks", [])
                            st.session_state.my_goal = goal_input
                            st.session_state.my_deadline = deadline_input
                            st.session_state.yume_step = 2
                            st.rerun()
                        except Exception: st.error("Error")
                else: st.warning(t("目標と期日を入力してください！", "Please enter goal and deadline!"))
        
        elif st.session_state.yume_step == 2:
            st.success(f"🎯 {t('目標', 'Goal')}: {st.session_state.my_goal}")
            st.markdown(t("#### 🤖 AI提案の逆算タスク", "#### 🤖 AI Suggested Tasks"))
            st.markdown('<div class="task-box">', unsafe_allow_html=True)
            for i, task in enumerate(st.session_state.ai_tasks): st.markdown(f"☑️ **Task {i+1}:** {task}")
            st.markdown('</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button(t("🔥 このタスクにコミットする！", "🔥 Commit!"), type="primary", use_container_width=True):
                    st.session_state.yume_step = 3; st.rerun()
            with c2:
                if st.button(t("🔙 目標を書き直す", "🔙 Rewrite Goal"), use_container_width=True):
                    st.session_state.yume_step = 1; st.rerun()

        elif st.session_state.yume_step == 3:
            st.markdown('<div class="task-box">', unsafe_allow_html=True)
            st.markdown(t("### 🎯 追跡中の目標", "### 🎯 Tracked Goal"))
            st.write(f"**{st.session_state.my_goal}** ({t('期日', 'Deadline')}: {st.session_state.my_deadline})")
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown(t("### 📝 今日のジャーナル（進捗報告）", "### 📝 Today's Journal"))
            report_input = st.text_area(t("タスクに対して今日できたこと（またはサボった現実）を正直に書いてください！サボり大歓迎！", "Report today's progress (or laziness)! Slacking is welcome!"), height=100)
            if st.button(t("✨ 現実を「シランケド」に変換！", "✨ Convert to Shirankedo!"), type="primary", use_container_width=True):
                if report_input:
                    with st.spinner(t("AIおかんが壮大な夢オチを執筆中...", "AI is generating...")):
                        try:
                            res = requests.post("http://127.0.0.1:8000/api/preview-yumeochi", json={"goal": st.session_state.my_goal, "report": report_input}, timeout=60).json()
                            st.session_state.preview_data = res.get("boke_data")
                            st.session_state.preview_vector = res.get("boke_vector")
                            st.rerun()
                        except Exception: st.error("Error")
                else: st.warning(t("今日の現実を報告してください！", "Please report today's reality!"))
            st.markdown("---")
            if st.button(t("🗑 目標を完全にリセットして最初から", "🗑 Reset Goal entirely"), use_container_width=True):
                st.session_state.yume_step = 1
                st.session_state.my_goal = ""
                st.session_state.my_deadline = ""
                st.session_state.ai_tasks = []
                st.session_state.preview_data = None
                st.session_state.preview_vector = None
                st.rerun()

    if st.session_state.preview_data:
        boke = st.session_state.preview_data
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        st.markdown(t("#### 💡 プレビュー (未公開)", "#### 💡 Preview (Private)"))
        
        if boke.get("type") == "yumeochi":
            st.markdown(f'<div class="goal-badge">🎯 {t("目標", "Goal")}: {boke.get("goal")}</div>', unsafe_allow_html=True)
        if boke.get("type") == "image" and "image_url" in boke: 
            st.image(boke["image_url"], use_container_width=True)
            
        display_text = boke.get('boke_jp', '') if is_ja else boke.get('boke_en', '')
        flag = "🇯🇵" if is_ja else "🌍"
        st.markdown(f'<div class="main-text">{flag} {display_text}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button(t("🚀 世界に放流する！", "🚀 Publish to World!"), type="primary", use_container_width=True):
                with st.spinner(t("DBに保存中...", "Saving...")):
                    payload = {
                        "author_id": st.session_state.user_id,
                        "author_name": st.session_state.username,
                        "boke_data": st.session_state.preview_data, 
                        "boke_vector": st.session_state.preview_vector
                    }
                    requests.post("http://127.0.0.1:8000/api/publish", json=payload)
                st.session_state.preview_data = None
                st.session_state.preview_vector = None
                st.toast(t("🎉 投稿完了！閲覧者側フィードに移動します。", "🎉 Published! Moving to Feed."), icon="✅")
                time.sleep(1.5)
                st.session_state.current_page = pages[1]
                st.rerun()
        with c2:
            if st.button(t("🗑 プレビューだけ消す", "🗑 Clear Preview"), use_container_width=True):
                st.session_state.preview_data = None
                st.session_state.preview_vector = None
                st.rerun()

# ==========================================
# 🌍 フィード
# ==========================================
elif page_index == 1:
    st.write(t("③ 他人の投稿が流れてきます。④ ツッコミ・応援を入れてDMを開始！", "3. View others' posts. 4. React to start a DM!"))
    if st.button(t("🔄 フィードを更新", "🔄 Refresh Feed"), use_container_width=True): st.rerun()
        
    with st.spinner(t("最新の投稿を取得中...", "Loading latest posts...")):
        try:
            feed_res = requests.get("http://127.0.0.1:8000/api/feed").json()
            posts = feed_res.get("posts", [])
            if not posts: st.info(t("まだフィードに投稿がありません。", "No posts yet."))
            else:
                for post in posts:
                    boke = post.get("boke_data", {})
                    post_id = post.get("id")
                    is_mine = (post.get("author_id") == st.session_state.user_id)
                    author_name = boke.get("author_name", t("見知らぬユーザー", "Unknown User"))
                    bg_color = "#ffffff" if not is_mine else "#f4f9ff"
                    
                    st.markdown(f'<div class="post-card" style="background-color: {bg_color};">', unsafe_allow_html=True)
                    
                    if is_mine:
                        st.markdown(f"👤 **{author_name} ({t('あなた', 'You')})** <span style='color:green; font-weight:bold; font-size:0.8rem;'>・{t('自分の投稿', 'Your Post')}</span>", unsafe_allow_html=True)
                    else:
                        # 🌟 ここも「Ochify」へブランド名を変更！
                        st.markdown(f"👤 **{author_name}** <span style='color:gray; font-size:0.8rem;'>・Ochify</span>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    if boke.get("type") == "yumeochi":
                        st.markdown(f'<div class="goal-badge">🎯 {t("目標", "Goal")}: {boke.get("goal")}</div><br>', unsafe_allow_html=True)
                    if boke.get("type") == "image" and "image_url" in boke:
                        st.image(boke["image_url"], use_container_width=True)
                        st.markdown("<br>", unsafe_allow_html=True)
                        
                    display_text = boke.get('boke_jp', '') if is_ja else boke.get('boke_en', '')
                    flag = "🇯🇵" if is_ja else "🌍"
                    st.markdown(f'<div class="main-text">{flag} {display_text}</div>', unsafe_allow_html=True)
                    
                    if is_mine:
                        st.markdown(f"<p style='font-size:0.8rem; color:#888;'>👇 {t('自分でツッコむと痛い奴やで！', 'This is your post. Cannot react to yourself.')}</p>", unsafe_allow_html=True)
                    else:
                        msg = t("👇 シランケド応援を入れてDMを開始", "👇 Send Shirankedo to start DM") if boke.get("type") == "yumeochi" else t("👇 ツッコミを入れてDMを開始", "👇 React to start DM")
                        st.markdown(f"<p style='font-size:0.8rem; color:#888;'>{msg}</p>", unsafe_allow_html=True)
                        
                        c1, c2, c3 = st.columns(3)
                        t1, t2, t3 = boke.get('tsukkomi_1',{}), boke.get('tsukkomi_2',{}), boke.get('tsukkomi_3',{})
                        b1_txt = t1.get('jp','') if is_ja else t1.get('en','')
                        b2_txt = t2.get('jp','') if is_ja else t2.get('en','')
                        b3_txt = t3.get('jp','') if is_ja else t3.get('en','')
                        
                        def start_dm(tsukkomi_text, boke_jp):
                            st.session_state.dm_history.append({"me": tsukkomi_text, "other": t("なんでやねん！笑", "Lol, what!")})
                            st.session_state.current_page = pages[2]
                            
                        with c1:
                            if st.button(f"{t1.get('emoji','')} {b1_txt}", key=f"t1_{post_id}", use_container_width=True): start_dm(b1_txt, display_text); st.rerun()
                        with c2:
                            if st.button(f"{t2.get('emoji','')} {b2_txt}", key=f"t2_{post_id}", use_container_width=True): start_dm(b2_txt, display_text); st.rerun()
                        with c3:
                            if st.button(f"{t3.get('emoji','')} {b3_txt}", key=f"t3_{post_id}", use_container_width=True): start_dm(b3_txt, display_text); st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e: st.error("Error loading feed.")

elif page_index == 2:
    st.title(t("💬 DMルーム", "💬 DM Room"))
    if not st.session_state.dm_history: st.info(t("まだ誰ともチャットしていません。", "No chats yet."))
    else:
        with st.container(border=True):
            st.markdown(t("👤 **見知らぬ相手**", "👤 **Stranger**"))
            st.markdown("---")
            for dm in st.session_state.dm_history:
                st.markdown(f"<div class='chat-bubble-me'>{t('あなた', 'You')}: {dm['me']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='chat-bubble-other'>{t('相手', 'Them')}: {dm['other']}</div>", unsafe_allow_html=True)
            st.markdown("---")
            st.text_input(t("メッセージを送信...", "Send message..."), placeholder="※Mock")
            st.button(t("送信", "Send"), type="primary")