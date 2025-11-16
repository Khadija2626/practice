# app.py
import streamlit as st
import random
import time
import datetime

# --- Page Config ---
st.set_page_config(
    page_title="Typing Speed Test — Glass UI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Data: Paragraphs and Words ---
PARAGRAPHS = [
    "The quick brown fox jumps over the lazy dog. This pangram contains every letter of the alphabet at least once. It is commonly used for testing keyboards and typing speed. Practice makes perfect, and consistent effort leads to improvement.",
    "Python is a high-level, interpreted programming language known for its simplicity and readability. It supports multiple programming paradigms, including procedural, object-oriented, and functional programming. Developers love Python for rapid prototyping and building scalable applications.",
    "Typing speed is measured in words per minute (WPM). Accuracy is equally important because mistakes reduce effective speed. Professional typists often achieve over 80 WPM with 98% accuracy. Regular practice with varied text improves both metrics.",
    "Technology evolves rapidly. Artificial intelligence, machine learning, and cloud computing are transforming industries. Staying updated with new tools and frameworks is essential for developers. Online platforms provide excellent resources for continuous learning.",
    "Good posture and finger placement are crucial for efficient typing. The home row keys (ASDF for left hand, JKL; for right) serve as the foundation. Keep wrists elevated and fingers curved. Avoid looking at the keyboard to build muscle memory."
]

WORDS = [
    "the","quick","brown","fox","jumps","over","lazy","dog","python","programming","keyboard",
    "typing","practice","speed","accuracy","challenge","test","computer","monitor","screen",
    "development","software","hardware","internet","network","server","algorithm","database",
    "function","variable","class","object","method","loop",
]

# --- Stateful defaults ---
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.test_active = False
    st.session_state.practice_mode = False
    st.session_state.mode = "words"  # "words" or "paragraphs"
    st.session_state.round = 1
    st.session_state.total_rounds = 10
    st.session_state.score = 0
    st.session_state.total_time = 0.0
    st.session_state.correct_chars = 0
    st.session_state.total_chars = 0
    st.session_state.start_time = None
    st.session_state.current_text = ""
    st.session_state.user_input = ""
    st.session_state.history = []
    st.session_state.dark_mode = False
    st.session_state.ui_id = random.randint(1000, 9999)  # unique keys
    st.session_state.test_action = None  # safe rerun control

# --- Utility functions ---
def get_random_text():
    if st.session_state.mode == "words":
        return " ".join(random.sample(WORDS, k=random.randint(8, 15)))
    return random.choice(PARAGRAPHS).strip()

def highlight_text(target, typed):
    out = []
    for i, ch in enumerate(typed):
        if i < len(target) and ch == target[i]:
            out.append(f"<span class='ok'>{ch}</span>")
        else:
            out.append(f"<span class='bad'>{ch}</span>")
    if len(typed) < len(target):
        rem = target[len(typed):]
        out.append(f"<span class='rem'>{rem}</span>")
    return "".join(out)

def calculate_wpm(correct_chars, seconds):
    if seconds <= 0:
        return 0.0
    return (correct_chars / 5) / (seconds / 60.0)

def save_result():
    if st.session_state.total_chars == 0:
        return
    wpm = calculate_wpm(st.session_state.correct_chars, st.session_state.total_time)
    accuracy = (st.session_state.correct_chars / st.session_state.total_chars) * 100
    st.session_state.history.append({
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "wpm": round(wpm, 1),
        "accuracy": round(accuracy, 1),
        "score": st.session_state.score,
        "mode": st.session_state.mode
    })

def reset_test():
    st.session_state.test_active = False
    st.session_state.practice_mode = False
    st.session_state.round = 1
    st.session_state.score = 0
    st.session_state.total_time = 0.0
    st.session_state.correct_chars = 0
    st.session_state.total_chars = 0
    st.session_state.current_text = get_random_text()
    st.session_state.user_input = ""
    st.session_state.start_time = None

# --- Styling: Glass + Neon ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
:root{
    --glass-bg: rgba(255,255,255,0.06);
    --glass-border: rgba(255,255,255,0.08);
    --accent: rgba(124,58,237,0.95);
    --accent-2: rgba(99,102,241,0.95);
    --muted: rgba(255,255,255,0.55);
}
.stApp, .css-18e3th9 { background: linear-gradient(135deg, rgba(10,10,20,1) 0%, rgba(16,10,30,1) 100%); font-family: 'Inter', sans-serif; }
.glass { background: linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02)); border:1px solid var(--glass-border); backdrop-filter: blur(8px) saturate(1.1); -webkit-backdrop-filter: blur(8px) saturate(1.1); border-radius:14px; padding:18px; box-shadow:0 6px 30px rgba(2,6,23,0.6); color:#e9eef8; }
.header { padding:18px; border-radius:12px; margin-bottom:10px; }
.app-title { font-size:1.6rem; font-weight:700; letter-spacing:-0.3px; margin:0; }
.sub-title { color: var(--muted); margin-top:4px; font-size:0.95rem; }
.text-display { font-family:'Courier New', monospace; font-size:1.15rem; line-height:1.6; padding:16px; border-radius:10px; border:1px solid rgba(255,255,255,0.04); background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); min-height:120px; white-space: pre-wrap; color:#dfe8ff; }
.input-area textarea { font-family:'Courier New', monospace !important; font-size:1.12rem !important; min-height:120px !important; background:transparent !important; color:#fff !important; border-radius:8px !important; border:1px dashed rgba(255,255,255,0.04) !important; padding:12px !important; }
.ok { color:#7df0a3; font-weight:600 }
.bad { color:#ffb3b3; background: rgba(255,80,80,0.03); border-radius:3px }
.rem { color: #9aa6c7 }
.controls .stButton>button { background: linear-gradient(90deg, rgba(124,58,237,0.95), rgba(59,130,246,0.95)); border:none; color:white; padding:10px 16px; border-radius:10px; box-shadow:0 8px 24px rgba(59,130,246,0.08), inset 0 -2px 6px rgba(0,0,0,0.15);}
.ghost { background: transparent !important; border:1px solid rgba(255,255,255,0.05) !important; color:#dfe8ff !important; }
.muted { color: var(--muted); font-size:0.95rem }
.stat-box { background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(0,0,0,0.02)); padding:12px; border-radius:10px; min-width:140px; text-align:center; border:1px solid rgba(255,255,255,0.03); }
.accent-pill { display:inline-block; padding:6px 10px; border-radius:999px; background: linear-gradient(90deg, var(--accent), var(--accent-2)); color:white; font-weight:600; font-size:0.9rem; }
.footer { color: var(--muted); font-size:0.88rem; }
@media (max-width: 720px) { .app-title { font-size: 1.2rem; } .text-display { font-size: 1rem; min-height: 100px; } }
</style>
""", unsafe_allow_html=True)

# --- Header ---
with st.container():
    header_col1, header_col2 = st.columns([3, 1], gap="large")
    with header_col1:
        st.markdown(f"""
        <div class="glass header">
            <div style="display:flex; align-items:center; gap:14px;">
                <div style="width:56px;height:56px;border-radius:12px; background:linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02)); display:flex;align-items:center;justify-content:center;border:1px solid rgba(255,255,255,0.04);">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" style="opacity:0.95">
                        <path d="M3 12h18" stroke="white" stroke-width="1.3" stroke-linecap="round"/>
                        <path d="M3 6h18" stroke="white" stroke-width="1.3" stroke-linecap="round" opacity="0.6"/>
                        <path d="M3 18h18" stroke="white" stroke-width="1.3" stroke-linecap="round" opacity="0.6"/>
                    </svg>
                </div>
                <div>
                    <div class="app-title">Typing Speed Test</div>
                    <div class="sub-title">Glass UI • Neo-modern • Improve WPM & accuracy with beautiful practice sessions</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with header_col2:
        st.markdown("""
        <div class="glass" style="text-align:center;">
            <div style="font-size:0.95rem; color: #dfe8ff; font-weight:600">Glass Mode</div>
            <div style="margin-top:8px;"><span class="accent-pill">Neo-Modern</span></div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("")

# --- Main layout ---
left, right = st.columns([3, 1.2], gap="large")

with left:
    st.markdown('<div class="glass">', unsafe_allow_html=True)

    # --- Controls ---
    ctrl1, ctrl2, ctrl3 = st.columns([1.2, 1.2, 1], gap="small")
    with ctrl1:
        if st.button("Start Test", key=f"start_test_{st.session_state.ui_id}"):
            st.session_state.test_action = "start_test"

        if st.button("Start Practice", key=f"start_pr_{st.session_state.ui_id}"):
            st.session_state.test_action = "start_practice"

    with ctrl2:
        if st.button("Random Words", key=f"mw_{st.session_state.ui_id}"):
            st.session_state.mode = "words"
            st.success("Mode set: Random Words", icon="✅")

        if st.button("Random Paragraph", key=f"mp_{st.session_state.ui_id}"):
            st.session_state.mode = "paragraphs"
            st.success("Mode set: Random Paragraphs", icon="✅")

    with ctrl3:
        rounds = st.number_input("Rounds", min_value=1, max_value=50, value=st.session_state.total_rounds, key=f"rounds_{st.session_state.ui_id}")
        st.session_state.total_rounds = int(rounds)

    # --- Execute actions after button press ---
    if st.session_state.test_action:
        action = st.session_state.pop("test_action")
        reset_test()
        st.session_state.test_active = True
        st.session_state.practice_mode = (action == "start_practice")
        st.session_state.start_time = time.time()
        st.experimental_rerun()

    st.markdown("---")

    # --- Typing Test Area ---
    if st.session_state.test_active:
        if not st.session_state.current_text:
            st.session_state.current_text = get_random_text()

        if not st.session_state.practice_mode:
            st.markdown(f"**Round {st.session_state.round}/{st.session_state.total_rounds}**  •  Mode: **{st.session_state.mode.title()}**")

        st.markdown(f'<div class="text-display">{st.session_state.current_text}</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        user_input = st.text_area(
            "Type the text above:",
            value="",
            key=f"typing_input_{st.session_state.ui_id}",
            label_visibility="collapsed",
            placeholder="Start typing here... (press Enter on a new line to submit)"
        )

        if len(user_input) > 0 and st.session_state.start_time is None:
            st.session_state.start_time = time.time()

        submitted = False
        if user_input.endswith("\n"):
            submitted = True
            user_input = user_input.rstrip("\n")
        if st.button("Submit", key=f"submit_{st.session_state.ui_id}"):
            submitted = True

        if submitted:
            end_time = time.time()
            time_taken = end_time - (st.session_state.start_time or end_time)
            correct_chars = sum(1 for a, b in zip(st.session_state.current_text, user_input) if a == b)
            total_chars = len(st.session_state.current_text)

            st.session_state.correct_chars += correct_chars
            st.session_state.total_chars += total_chars
            st.session_state.total_time += time_taken

            is_correct = user_input == st.session_state.current_text
            if is_correct:
                st.session_state.score += 10

            # --- Result Display ---
            st.markdown("---")
            st.markdown("**Result**")
            st.markdown(f"<div style='font-family:monospace; font-size:1.05rem'>{highlight_text(st.session_state.current_text, user_input)}</div>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"<div class='stat-box'><div style='font-size:0.9rem; color:var(--muted)'>Time</div><div style='font-size:1.2rem; font-weight:700'>{time_taken:.2f}s</div></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='stat-box'><div style='font-size:0.9rem; color:var(--muted)'>Accuracy (this)</div><div style='font-size:1.2rem; font-weight:700'>{(correct_chars/total_chars*100) if total_chars else 0:.1f}%</div></div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div class='stat-box'><div style='font-size:0.9rem; color:var(--muted)'>Match</div><div style='font-size:1.2rem; font-weight:700'>{'Yes' if is_correct else 'No'}</div></div>", unsafe_allow_html=True)

            # --- Next Actions ---
            if st.session_state.practice_mode:
                if st.button("Next Practice", key=f"next_pr_{st.session_state.ui_id}"):
                    st.session_state.test_action = "next_practice"
                if st.button("Stop Practice", key=f"stop_pr_{st.session_state.ui_id}"):
                    st.session_state.test_action = "stop_practice"
            else:
                if st.session_state.round < st.session_state.total_rounds:
                    if st.button("Next Round", key=f"next_round_{st.session_state.ui_id}"):
                        st.session_state.test_action = "next_round"
                else:
                    if st.button("View Results", key=f"view_res_{st.session_state.ui_id}"):
                        st.session_state.test_action = "view_results"

            # Execute actions
            if st.session_state.test_action:
                action = st.session_state.pop("test_action")
                if action == "next_practice":
                    st.session_state.current_text = get_random_text()
                    st.session_state.start_time = time.time()
                elif action == "stop_practice":
                    save_result()
                    st.session_state.test_active = False
                    st.session_state.practice_mode = False
                elif action == "next_round":
                    st.session_state.round += 1
                    st.session_state.current_text = get_random_text()
                    st.session_state.start_time = time.time()
                elif action == "view_results":
                    save_result()
                    st.session_state.test_active = False

                st.experimental_rerun()

        st.session_state.start_time = None

    else:
        # --- Latest Result if not active ---
        st.markdown('<div class="glass">', unsafe_allow_html=True)
        st.markdown("### Latest Result", unsafe_allow_html=True)
        if st.session_state.history:
            latest = st.session_state.history[-1]
            st.markdown(f"<div style='display:flex; gap:12px; align-items:center'> \
                <div class='stat-box'><div style='font-size:0.9rem; color:var(--muted)'>WPM</div><div style='font-size:1.4rem; font-weight:700'>{latest['wpm']}</div></div> \
                <div class='stat-box'><div style='font-size:0.9rem; color:var(--muted)'>Accuracy</div><div style='font-size:1.4rem; font-weight:700'>{latest['accuracy']}%</div></div> \
                <div class='stat-box'><div style='font-size:0.9rem; color:var(--muted)'>Score</div><div style='font-size:1.4rem; font-weight:700'>{latest['score']}</div></div> \
            </div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='muted'>No results yet. Start a test or practice session!</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown("### Stats & History", unsafe_allow_html=True)
    if st.session_state.history:
        for h in reversed(st.session_state.history[-5:]):
            st.markdown(f"- {h['date']} | WPM: {h['wpm']} | Acc: {h['accuracy']}% | Score: {h['score']} | Mode: {h['mode']}")
    else:
        st.markdown("<div class='muted'>No history yet.</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- Footer ---
st.markdown('<div class="footer">Made with ❤️ by YourName — Neo-modern Typing Test</div>', unsafe_allow_html=True)
