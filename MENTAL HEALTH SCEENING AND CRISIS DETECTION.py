import streamlit as st
import hashlib, hmac, secrets
from datetime import date, datetime, timedelta
import pandas as pd

st.set_page_config(page_title="MindCare AI", page_icon="🧠", layout="wide")

# ---------- COLOURFUL CSS ----------
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.main-card {
    background: white;
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    margin-bottom: 20px;
}
.metric-card {
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
}
.mood-low { background: linear-gradient(135deg, #ff9a9e, #fecfef); }
.mood-mid { background: linear-gradient(135deg, #ffecd2, #fcb69f); }
.mood-high { background: linear-gradient(135deg, #a1c4fd, #c2e9fb); }
h1, h2, h3 { color: #2d3436 !important; }
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if 'users' not in st.session_state:
    st.session_state.users = []
    st.session_state.journal = []
    st.session_state.q_records = []
    st.session_state.user_id = None
    st.session_state.next_user_id = 1

ADMIN_PASSWORD = "admin123"

def hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 200_000).hex()

# ---------- HEADER ----------
st.markdown("<h1 style='text-align:center; color:white !important;'>🧠 MindCare AI - Your Personal Wellbeing Helper ✨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:white;'>Hackathon Demo | Colourful & Interactive</p>", unsafe_allow_html=True)

# ---------- AUTH ----------
if st.session_state.user_id is None:
    tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Sign Up", "👑 Admin"])
    
    with tab1:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("Welcome Back!")
        u = st.text_input("Username", key="l1")
        p = st.text_input("Password", type="password", key="l2")
        if st.button("Login 🚀", use_container_width=True):
            for user in st.session_state.users:
                if user["username"].lower() == u.lower():
                    if hmac.compare_digest(hash_password(p, user["salt"]), user["password_hash"]):
                        st.session_state.user_id = user["user_id"]
                        st.success(f"Welcome {user['username']}! 🎉")
                        st.rerun()
            st.error("Invalid credentials")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.subheader("Create Account")
        u = st.text_input("New Username")
        e = st.text_input("Email (optional)")
        p = st.text_input("New Password", type="password")
        if st.button("Create Account ✨", use_container_width=True):
            if any(x["username"].lower()==u.lower() for x in st.session_state.users):
                st.error("Username exists")
            else:
                salt = secrets.token_hex(16)
                st.session_state.users.append({
                    "user_id": st.session_state.next_user_id,
                    "username": u, "email": e,
                    "password_hash": hash_password(p, salt), "salt": salt,
                    "created_at": datetime.now().strftime("%Y-%m-%d")
                })
                st.session_state.next_user_id+=1
                st.success("Account Created! Go to Login Tab")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        pw = st.text_input("Admin Password", type="password")
        if st.button("Admin Login"):
            if hmac.compare_digest(pw, ADMIN_PASSWORD):
                st.session_state.user_id = 0
                st.rerun()
            else: st.error("Wrong password")
    st.stop()

# ---------- LOGGED IN ----------
user_obj = next((u for u in st.session_state.users if u["user_id"]==st.session_state.user_id), None) if st.session_state.user_id!=0 else {"username":"Admin"}

st.sidebar.markdown(f"### 👋 Hi, {user_obj['username']}")
if st.sidebar.button("Logout"):
    st.session_state.user_id=None
    st.rerun()

# ADMIN VIEW
if st.session_state.user_id==0:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.header("👑 Admin Dashboard")
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Users", len(st.session_state.users))
    c2.metric("Journals", len(st.session_state.journal))
    c3.metric("Questionnaires", len(st.session_state.q_records))
    st.dataframe(pd.DataFrame(st.session_state.users))
    st.dataframe(pd.DataFrame(st.session_state.journal))
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# USER DASHBOARD
menu = st.sidebar.radio("Navigate", ["📊 Dashboard", "📝 Mood Journal", "🤖 AI Chatbot", "🧘 Stress Relief", "🎮 Mini Game", "📋 Questionnaire", "📈 7-Day Report"])

if menu=="📊 Dashboard":
    entries = [e for e in st.session_state.journal if e["user_id"]==st.session_state.user_id]
    col1,col2,col3 = st.columns(3)
    avg = sum(e["mood_rating"] for e in entries)/len(entries) if entries else 0
    col1.markdown(f'<div class="metric-card"><h3>📝 Check-ins</h3><h1>{len(entries)}</h1></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="metric-card"><h3>😊 Avg Mood</h3><h1>{avg:.1f}/10</h1></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="metric-card"><h3>🔥 Streak</h3><h1>{len(entries)} Days</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    if entries:
        df = pd.DataFrame(entries)
        st.line_chart(df.set_index("entry_date")["mood_rating"])
    else: st.info("Start journaling to see your mood graph!")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu=="📝 Mood Journal":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Daily Mood Journal 💭")
    mood = st.slider("Rate your mood 1 (low) to 10 (great)", 1, 10, 5)
    text = st.text_area("How was your day?")
    if st.button("Save Entry 💾", type="primary"):
        st.session_state.journal.append({
            "entry_id": len(st.session_state.journal)+1,
            "user_id": st.session_state.user_id,
            "entry_date": date.today().isoformat(),
            "mood_rating": mood, "journal_text": text
        })
        if mood<=3: st.warning("🤗 Consider talking with someone you trust. You matter!")
        elif mood<=6: st.info("🌿 Try a short walk or creative activity!")
        else: st.success("🌟 Amazing! Keep doing what makes you happy!")
        st.balloons()
    st.markdown('</div>', unsafe_allow_html=True)

elif menu=="🤖 AI Chatbot":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("MindCare Support Chatbot")
    if "chat" not in st.session_state: st.session_state.chat=[]
    for m in st.session_state.chat: st.chat_message(m["role"]).write(m["content"])
    prompt = st.chat_input("Tell me how you feel...")
    if prompt:
        st.session_state.chat.append({"role":"user","content":prompt})
        msg = prompt.lower()
        if "stress" in msg: ans="🧘 Take a comfortable pause, breathe naturally. You've got this!"
        elif "sleep" in msg: ans="😴 Try a regular sleep schedule. No screens before bed helps!"
        elif "sad" in msg: ans="💙 It's okay to feel sad. Consider speaking with someone you trust."
        elif "exam" in msg or "study" in msg: ans="📚 Break work into 25 min chunks! Pomodoro works great!"
        elif "happy" in msg: ans="🎉 Wonderful! Notice what helped you feel this way!"
        else: ans="🌈 Thank you for sharing. What small thing might help you right now?"
        st.session_state.chat.append({"role":"assistant","content":ans + " (Not a medical diagnosis)"})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif menu=="🧘 Stress Relief":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Stress-Relief Activities")
    c1,c2 = st.columns(2)
    if c1.button("🌬️ Breathing Pause"): c1.success("Breathe in 4s, hold 4s, out 4s. Relax shoulders.")
    if c2.button("👀 Grounding 5-4-3-2-1"): c2.info("Notice 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste.")
    if c1.button("🎵 Calming Music"): c1.info("Play lo-fi or nature sounds for 2 mins.")
    if c2.button("☕ Short Break"): c2.success("Take a 5 min break, stretch!")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu=="🎮 Mini Game":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Mindful Mini-Game 🧩")
    st.write("Find the missing number: **2, 4, 6, 8, ?**")
    ans = st.text_input("Your answer")
    if st.button("Check"):
        if ans.strip()=="10": st.success("Correct! 🎉 Pattern adds 2 each time."); st.balloons()
        else: st.error("Answer is 10 - adds 2 each time!")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu=="📋 Questionnaire":
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("Wellbeing Questionnaire")
    with st.form("q"):
        q1 = st.text_input("How have you been feeling?")
        q2 = st.text_input("Feeling stressed?")
        q3 = st.text_input("Sleep/appetite changes?")
        q4 = st.text_input("What do you do when sad?")
        q5 = st.text_input("Someone you trust to talk to?")
        q6 = st.text_input("Do you feel safe?")
        q7 = st.text_input("What helps you feel better?")
        submit = st.form_submit_button("Submit 📨")
        if submit:
            st.session_state.q_records.append({"user":user_obj["username"], "date":date.today().isoformat(), "mood":q1})
            st.success("Saved in memory. If you feel unsafe, contact a trusted adult or local help.")
    st.markdown('</div>', unsafe_allow_html=True)

elif menu=="📈 7-Day Report":
    entries = [e for e in st.session_state.journal if e["user_id"]==st.session_state.user_id and e["entry_date"]>= (date.today()-timedelta(days=6)).isoformat()]
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("7-Day Wellbeing Report")
    if not entries: st.warning("No entries in last 7 days")
    else:
        st.dataframe(pd.DataFrame(entries), use_container_width=True)
        st.download_button("📥 Export My CSV", pd.DataFrame(entries).to_csv(index=False), "mindcare_export.csv")
    st.markdown('</div>', unsafe_allow_html=True)
