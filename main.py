import streamlit as st
import time
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Hangar Havoc: Dirty Dozen",
    page_icon="✈️",
    layout="centered"
)

# --- CSS STYLING ---
st.markdown("""
    <style>
    .stButton button {
        width: 100%;
        font-weight: bold;
    }
    .big-font {
        font-size: 20px !important;
    }
    .success {
        color: #28a745;
        font-weight: bold;
    }
    .danger {
        color: #dc3545;
        font-weight: bold;
    }
    .warning {
        color: #ffc107;
        font-weight: bold;
        background-color: #333;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GAME CONSTANTS ---
MAX_TIME = 60
FATIGUE_LIMIT = 100
BOLTS_NEEDED = 6

# --- STATE MANAGEMENT ---
def init_game():
    if 'game_state' not in st.session_state:
        st.session_state.game_state = "SPLASH" # SPLASH, PLAYING, WON, LOST
    
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    
    if 'fatigue' not in st.session_state:
        st.session_state.fatigue = 0
        
    if 'bolts' not in st.session_state:
        # Each bolt has: current_tightness (0-100), is_mystery (True/False), is_heavy (True/False)
        st.session_state.bolts = []
        for i in range(BOLTS_NEEDED):
            st.session_state.bolts.append({
                "id": i,
                "progress": 0,
                "is_mystery": random.choice([True] + [False]*4),
                "is_heavy": random.choice([True] + [False]*4),
                "status": "Loose"
            })
            
    if 'status_effects' not in st.session_state:
        st.session_state.status_effects = {
            "tool_broken": False,
            "distraction": False,
            "boss_pressure": False,
            "tunnel_vision": False
        }
    
    if 'log' not in st.session_state:
        st.session_state.log = ["Welcome to the Hangar. Check the bolts!"]

def add_log(msg):
    st.session_state.log.insert(0, f"• {msg}")
    if len(st.session_state.log) > 5:
        st.session_state.log.pop()

# --- GAME LOGIC FUNCTIONS ---

def check_game_over():
    # 1. Check Time
    elapsed = time.time() - st.session_state.start_time
    if elapsed > MAX_TIME:
        st.session_state.game_state = "LOST"
        st.session_state.end_reason = "TIME OUT! (Pressure)"
        return True

    # 2. Check Fatigue
    if st.session_state.fatigue >= FATIGUE_LIMIT:
        st.session_state.game_state = "LOST"
        st.session_state.end_reason = "PASSED OUT! (Fatigue)"
        return True

    # 3. Check Win (All bolts 100%)
    if all(b['progress'] >= 100 for b in st.session_state.bolts):
        st.session_state.game_state = "WON"
        st.session_state.end_reason = "AIRCRAFT RELEASED TO SERVICE."
        return True
    
    return False

def trigger_random_event():
    # Only trigger events if game is playing
    if st.session_state.game_state != "PLAYING": return

    roll = random.randint(1, 100)
    
    # 1. Distraction (10% chance)
    if roll < 10 and not st.session_state.status_effects['distraction']:
        st.session_state.status_effects['distraction'] = True
        add_log("PHONE RINGING! (Distraction)")
        
    # 2. Tool Break (5% chance)
    elif roll < 15 and not st.session_state.status_effects['tool_broken']:
        st.session_state.status_effects['tool_broken'] = True
        add_log("WRENCH SNAPPED! (Lack of Resources)")

    # 3. Boss Pressure (5% chance)
    elif roll < 20 and not st.session_state.status_effects['boss_pressure']:
        st.session_state.status_effects['boss_pressure'] = True
        add_log("BOSS: 'SIGN IT OFF NOW!' (Assertiveness)")

    # 4. Fatigue Creep (Always happens)
    st.session_state.fatigue += random.randint(2, 5)

# --- ACTIONS (CALLBACKS) ---

def start_game():
    st.session_state.game_state = "PLAYING"
    st.session_state.start_time = time.time()
    st.session_state.fatigue = 0
    st.session_state.log = ["Shift started. Good luck."]
    # Reset bolts
    st.session_state.bolts = []
    for i in range(BOLTS_NEEDED):
        st.session_state.bolts.append({
            "id": i,
            "progress": 0,
            "is_mystery": random.choice([True] + [False]*4),
            "is_heavy": random.choice([True] + [False]*4),
            "status": "Loose"
        })
    st.session_state.status_effects = {k: False for k in st.session_state.status_effects}

def action_tighten(bolt_idx):
    trigger_random_event()
    
    # Check Blocks
    if st.session_state.status_effects['distraction']:
        add_log("CAN'T WORK: ANSWER PHONE FIRST!")
        return
    if st.session_state.status_effects['tool_broken']:
        add_log("CAN'T WORK: TOOL BROKEN!")
        return
        
    bolt = st.session_state.bolts[bolt_idx]
    
    # Check Specific Bolt Issues
    if bolt['is_mystery']:
        add_log("UNKNOWN PART! Check Manual first.")
        return
    
    # Progress Logic
    increment = 25
    if bolt['is_heavy']:
        increment = 10 # Heavy bolts are harder
        add_log("Heavy bolt... turning slowly.")
        
    bolt['progress'] += increment
    
    if bolt['progress'] >= 100:
        bolt['progress'] = 100
        bolt['status'] = "SECURE"
        add_log(f"Bolt {bolt_idx+1} Secured.")

def action_manual(bolt_idx):
    st.session_state.bolts[bolt_idx]['is_mystery'] = False
    add_log(f"Bolt {bolt_idx+1} Identified.")
    trigger_random_event()

def action_rest():
    st.session_state.fatigue = max(0, st.session_state.fatigue - 30)
    add_log("Drank Coffee. Alertness restored.")
    trigger_random_event()

def action_fix_tool():
    st.session_state.status_effects['tool_broken'] = False
    add_log("Tool Replaced.")
    trigger_random_event()

def action_dismiss_distraction():
    st.session_state.status_effects['distraction'] = False
    add_log("Phone silenced.")
    trigger_random_event()

def action_refuse_boss():
    st.session_state.status_effects['boss_pressure'] = False
    add_log("Refused to sign off unsafe work.")
    trigger_random_event()

# --- UI RENDERING ---

def render_splash():
    st.title("✈️ Hangar Havoc: The Dirty Dozen")
    st.warning("⚠️ DISCLAIMER: This is a demo game for educational purposes only.")
    
    st.markdown("### The Mission")
    st.write("You are an aircraft mechanic. You have **60 seconds** to secure all **6 bolts**.")
    st.write("But the **Dirty Dozen** (Human Factors) will try to stop you.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**Game Mechanics:**")
        st.markdown("""
        - **Fatigue:** Increases every action. Click 'Rest' to lower it.
        - **Bolts:** Click 'Tighten' multiple times to fix.
        - **Mystery Bolts (❓):** You must click 'Check Manual' first.
        - **Heavy Bolts (⚖️):** Take more clicks to tighten.
        """)
    with col2:
        st.error("**The Threats:**")
        st.markdown("""
        - **Distractions:** Phone rings? Dismiss it immediately.
        - **Broken Tools:** Visit the Toolbox to fix.
        - **Pressure:** Watch the timer!
        """)
        
    st.button("START SHIFT", on_click=start_game, type="primary")

def render_game():
    # 1. Check Game Over status BEFORE rendering
    if check_game_over():
        st.experimental_rerun()

    # 2. Header / HUD
    elapsed = int(time.time() - st.session_state.start_time)
    time_left = MAX_TIME - elapsed
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Pressure (Time)", f"{time_left}s")
    c2.metric("Fatigue", f"{st.session_state.fatigue}%", delta_color="inverse")
    c3.metric("Bolts Fixed", f"{len([b for b in st.session_state.bolts if b['progress'] >= 100])}/6")

    # Fatigue Warning
    if st.session_state.fatigue > 70:
        st.error("⚠️ FATIGUE CRITICAL! REST NOW!")
        
    st.progress(min(100, st.session_state.fatigue))

    st.markdown("---")

    # 3. Active Threats (The Dirty Dozen)
    if st.session_state.status_effects['distraction']:
        st.warning("📱 PHONE RINGING! 'Hey, want to go to the pub?'")
        st.button("IGNORE (Dismiss)", on_click=action_dismiss_distraction, type="primary")
        st.markdown("---")
        
    if st.session_state.status_effects['boss_pressure']:
        st.error("👔 BOSS: 'Stop wasting time and sign it off!'")
        col_boss1, col_boss2 = st.columns(2)
        col_boss1.button("REFUSE (Safety First)", on_click=action_refuse_boss)
        col_boss2.button("SIGN (Unsafe)", on_click=lambda: st.write("GAME OVER: You signed off unsafe work.")) # Instant fail trap
        st.markdown("---")

    if st.session_state.status_effects['tool_broken']:
        st.error("🛠️ WRENCH BROKEN!")
        st.button("GO TO STORES (Fix Tool)", on_click=action_fix_tool)
        st.markdown("---")

    # 4. The Work Area (Bolts)
    st.subheader("🔧 Maintenance Panel")
    
    # Create a grid of bolts
    cols = st.columns(3)
    for i, bolt in enumerate(st.session_state.bolts):
        with cols[i % 3]:
            # Determine Icon and Status
            icon = "🔩"
            if bolt['progress'] >= 100:
                icon = "✅"
            elif bolt['is_mystery']:
                icon = "❓"
            elif bolt['is_heavy']:
                icon = "⚖️"
                
            st.write(f"**Bolt {i+1}** {icon}")
            
            # Progress Bar for this bolt
            st.progress(bolt['progress'])
            
            # Action Buttons
            if bolt['progress'] < 100:
                if bolt['is_mystery']:
                    st.button(f"Manual #{i+1}", on_click=action_manual, args=(i,), key=f"man_{i}")
                else:
                    st.button(f"Tighten #{i+1}", on_click=action_tighten, args=(i,), key=f"btn_{i}")
            else:
                st.write("*Secure*")
    
    st.markdown("---")
    
    # 5. Global Actions
    st.subheader("🧠 Human Factor Counter-Measures")
    c_rest, c_scan = st.columns(2)
    c_rest.button("☕ DRINK COFFEE (Reduce Fatigue)", on_click=action_rest)
    c_scan.button("👀 SCAN AREA (Check Awareness)") # Flavor button mostly

    # 6. Log
    st.markdown("---")
    st.text("Shift Log:")
    for msg in st.session_state.log:
        st.caption(msg)

def render_gameover():
    st.title("SHIFT ENDED")
    if st.session_state.game_state == "WON":
        st.success("🎉 MISSION ACCOMPLISHED!")
        st.balloons()
        st.write("You successfully navigated the Dirty Dozen and secured the aircraft.")
    else:
        st.error("❌ INCIDENT REPORT FILED")
        st.write(f"**Cause:** {st.session_state.end_reason}")
    
    st.write("---")
    st.write("### Human Factors Debrief")
    st.info("In aviation, the 'Dirty Dozen' are the 12 most common causes of human error. In this game, you faced Distraction, Fatigue, Pressure, Lack of Resources, and Lack of Knowledge.")
    
    st.button("START NEW SHIFT", on_click=lambda: st.session_state.update(game_state="SPLASH"))

# --- MAIN RUNNER ---
init_game()

if st.session_state.game_state == "SPLASH":
    render_splash()
elif st.session_state.game_state == "PLAYING":
    render_game()
else:
    render_gameover()
