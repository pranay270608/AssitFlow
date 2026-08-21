import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import bcrypt
from datetime import datetime
from pymongo import MongoClient, errors

# ==========================================
# PAGE CONFIGURATION & SYSTEM SETTINGS
# ==========================================
st.set_page_config(
    page_title="AssistFlow | Enterprise AI Support Portal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# RELIABLE SVG ASSETS (REMOVED 'A' SYMBOL)
# ==========================================
# Updated logo: Standalone 'A' symbol replaced with a sleek lightning bolt icon
ASSISTFLOW_SVG_LOGO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 65" width="200" height="55"><defs><linearGradient id="afGrad" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#0284C7"/><stop offset="100%" stop-color="#0369A1"/></linearGradient></defs><rect width="240" height="65" rx="16" fill="url(#afGrad)"/><path d="M30 16 L20 34 H30 L26 48 L40 30 H28 L32 16 Z" fill="#FFFFFF"/><text x="142" y="34" dominant-baseline="middle" text-anchor="middle" fill="#FFFFFF" font-family="'Plus Jakarta Sans', sans-serif" font-weight="900" font-size="21" letter-spacing="1.2">AssistFlow</text><text x="142" y="48" dominant-baseline="middle" text-anchor="middle" fill="#E0F2FE" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="7" letter-spacing="1.8">ENTERPRISE SUPPORT PORTAL</text></svg>"""

AVATAR_AI = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%230284C7'><path d='M12 2a2 2 0 0 1 2 2v1a8 8 0 0 1 8 8v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h1v-1a6 6 0 1 0-12 0v1h1a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-7a8 8 0 0 1 8-8V4a2 2 0 0 1 2-2z'/></svg>"
AVATAR_USER = "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%230369A1'><path d='M12 2a5 5 0 1 0 5 5 5 5 0 0 0-5-5zm0 12c-5.33 0-8 2.67-8 5v1h16v-1c0-2.33-2.67-5-8-5z'/></svg>"

# ==========================================
# NOSQL DATABASE INTEGRATION (OPTIMIZED & CACHED)
# ==========================================
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "assistflow_support_db"

@st.cache_resource
def init_database():
    """Establishes MongoDB connection and initializes schema and seed data."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        db_obj = client[DB_NAME]
        client.admin.command('ping')
        
        # Ensure Indexes for fast database lookups
        db_obj.users.create_index("username", unique=True)
        db_obj.tickets.create_index("ticket_id", unique=True)
        db_obj.bug_reports.create_index("bug_id", unique=True)
        
        if db_obj.users.count_documents({}) == 0:
            salt = bcrypt.gensalt()
            default_users = [
                {
                    "username": "admin1",
                    "password_hash": bcrypt.hashpw("admin123".encode('utf-8'), salt).decode('utf-8'),
                    "role": "Admin",
                    "department": "IT Operations",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                },
                {
                    "username": "tech1",
                    "password_hash": bcrypt.hashpw("tech123".encode('utf-8'), salt).decode('utf-8'),
                    "role": "Technician",
                    "department": "Hardware & Systems",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                },
                {
                    "username": "employee1",
                    "password_hash": bcrypt.hashpw("user123".encode('utf-8'), salt).decode('utf-8'),
                    "role": "Employee",
                    "department": "Finance",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
            ]
            db_obj.users.insert_many(default_users)
            
        if db_obj.tickets.count_documents({}) == 0:
            db_obj.tickets.insert_many([
                {
                    "ticket_id": "TCK-1001",
                    "author": "employee1",
                    "department": "Finance",
                    "category": "Hardware",
                    "priority": "Medium",
                    "title": "Dual monitor flickering on HDMI connection",
                    "description": "Secondary monitor displays flickering horizontal lines during high load.",
                    "status": "Solved",
                    "assigned_tech": "tech1",
                    "ai_response": "1. Verify HDMI connection.\n2. Update display drivers.\n3. Reset screen refresh rate to 60Hz.",
                    "tech_notes": "Resolved via display driver update by tech1.",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                },
                {
                    "ticket_id": "TCK-1002",
                    "author": "employee1",
                    "department": "Finance",
                    "category": "Network & Internet",
                    "priority": "High",
                    "title": "GlobalProtect VPN drops connection every 15 min",
                    "description": "VPN disconnects constantly on corporate Wi-Fi network.",
                    "status": "Under Processing",
                    "assigned_tech": "tech1",
                    "ai_response": "1. Toggle connection from UDP to TCP.\n2. Flush local DNS cache via ipconfig /flushdns.",
                    "tech_notes": "Assigned to tech1 for investigation.",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
            ])

        return db_obj, None
    except errors.ServerSelectionTimeoutError:
        return None, "⚠️ Could not connect to MongoDB. Ensure local MongoDB service is running on port 27017."
    except Exception as e:
        return None, f"Database Error: {str(e)}"

db, db_error = init_database()

# Fast Caching DB Queries to prevent Streamlit UI lag
@st.cache_data(ttl=2)
def get_cached_tickets():
    if db is None: return []
    return list(db.tickets.find({}, {"_id": 0}))

@st.cache_data(ttl=2)
def get_cached_bugs():
    if db is None: return []
    return list(db.bug_reports.find({}, {"_id": 0}))

@st.cache_data(ttl=2)
def get_cached_users():
    if db is None: return []
    return list(db.users.find({}, {"_id": 0, "password_hash": 0}))

def clear_db_caches():
    get_cached_tickets.clear()
    get_cached_bugs.clear()
    get_cached_users.clear()

# ==========================================
# AUTHENTICATION ENGINE
# ==========================================
def authenticate_user(username, password, role):
    if db is None: return None
    user = db.users.find_one({"username": username.strip()})
    if user and user.get("role") == role and bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
        return user
    return None

def register_user(username, password, role, department):
    if db is None: return False, "Database disconnected."
    if db.users.find_one({"username": username.strip()}):
        return False, "Username already exists."
    
    salt = bcrypt.gensalt()
    pw_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    db.users.insert_one({
        "username": username.strip(),
        "password_hash": pw_hash,
        "role": role,
        "department": department,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    clear_db_caches()
    return True, "Account created successfully!"

# ==========================================
# MODERN CSS THEME & ENHANCED UI STYLING
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }

    #MainMenu, footer { visibility: hidden !important; height: 0px !important; }
    header[data-testid="stHeader"] { background-color: transparent !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 96% !important; }

    /* Glass Cards & Modern UI Containers */
    .glass-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.04), 0 8px 10px -6px rgba(0, 0, 0, 0.02);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 16px 30px -10px rgba(2, 132, 199, 0.12);
        border-color: #38BDF8;
    }

    /* Hero Banner Styling */
    .hero-banner {
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%);
        border-radius: 24px;
        padding: 26px 36px;
        color: #FFFFFF;
        margin-bottom: 20px;
        box-shadow: 0 12px 28px rgba(2, 132, 199, 0.2);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .hero-title-main { font-size: 2.1rem; font-weight: 900; letter-spacing: 1px; color: #FFFFFF; margin: 0; }
    .hero-title-sub { font-size: 0.95rem; font-weight: 600; color: #E0F2FE; margin-top: 4px; }

    /* Status Badges */
    .status-pill {
        display: inline-flex;
        align-items: center;
        padding: 5px 12px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 0.75rem;
        letter-spacing: 0.03em;
    }
    .status-solved { background: #DCFCE7; color: #15803D; border: 1px solid #86EFAC; }
    .status-processing { background: #FEF3C7; color: #B45309; border: 1px solid #FDE68A; }
    .status-unsolved { background: #FEE2E2; color: #B91C1C; border: 1px solid #FCA5A5; }

    /* MODERN PROFILE UI CUSTOM STYLES */
    .profile-cover {
        background: linear-gradient(135deg, #0284C7 0%, #1E1B4B 100%);
        height: 140px;
        border-top-left-radius: 24px;
        border-top-right-radius: 24px;
        position: relative;
    }

    .profile-avatar-wrapper {
        position: relative;
        margin-top: -60px;
        margin-left: 32px;
        display: inline-block;
    }

    .profile-avatar-img {
        width: 110px;
        height: 110px;
        border-radius: 50%;
        border: 4px solid #FFFFFF;
        background: #FFFFFF;
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        object-fit: cover;
    }

    .profile-badge-pill {
        background: #F1F5F9;
        border: 1px solid #CBD5E1;
        color: #334155;
        padding: 6px 14px;
        border-radius: 12px;
        font-size: 0.82rem;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    /* SMOOTHER SIDEBAR NAVIGATION */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }

    div[data-testid="stRadio"] > label { display: none !important; }
    div[data-testid="stRadio"] div[role="radiogroup"] { gap: 8px; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 12px 18px;
        font-weight: 600;
        color: #334155;
        transition: all 0.15s ease-in-out;
        cursor: pointer;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background: #F1F5F9;
        color: #0284C7;
        transform: translateX(4px);
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
        color: #FFFFFF !important;
        border-color: #0284C7 !important;
        box-shadow: 0 6px 16px rgba(2, 132, 199, 0.25);
        transform: translateX(4px);
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p {
        color: #FFFFFF !important;
        font-weight: 700;
    }

    .stButton>button {
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%) !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 20px !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 18px rgba(2, 132, 199, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_role" not in st.session_state:
    st.session_state.user_role = ""
if "user_department" not in st.session_state:
    st.session_state.user_department = ""
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "avatar": AVATAR_AI, "content": "🤖 Hello! I am your AssistFlow Assistant. How can I help resolve your technical issue today?"}
    ]

# ==========================================
# OLLAMA AI INFERENCE ENGINE
# ==========================================
def call_ollama(prompt: str, model: str = "llama3", system_prompt: str = "") -> str:
    """Executes local LLM inference with increased timeout prevention."""
    url = "http://localhost:11434/api/generate"
    full_prompt = f"{system_prompt}\n\nUser Prompt:\n{prompt}" if system_prompt else prompt
    payload = {"model": model, "prompt": full_prompt, "stream": False}
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json().get("response", "No response received.")
        return f"⚠️ Ollama Error ({response.status_code}): Ensure model '{model}' is running in Ollama."
    except requests.exceptions.Timeout:
        return (
            "⚠️ **Localhost Timeout Handled**\n\n"
            "**Diagnostic Recommendation:**\n"
            "1. Verify system display drivers & corporate VPN config.\n"
            "2. Flush local DNS cache via `ipconfig /flushdns` in terminal.\n"
            "3. Restart target application service."
        )
    except requests.exceptions.ConnectionError:
        return (
            "⚠️ **Ollama Engine Offline (Fallback Active)**\n\n"
            "**Recommended System Steps:**\n"
            "1. Toggle network protocol setting from UDP to TCP.\n"
            "2. Flush local DNS cache using `ipconfig /flushdns`.\n"
            "3. Re-authenticate through SSO Gateway."
        )
    except Exception as e:
        return f"⚠️ System Error: {str(e)}"

# ==========================================
# LOGIN & REGISTRATION PAGE
# ==========================================
def render_login():
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.3, 1])
    
    with c2:
        st.markdown(
            f"""<div style="text-align: center; background: #FFFFFF; border: 1px solid #E2E8F0; padding: 36px; border-radius: 28px; box-shadow: 0 15px 35px rgba(0,0,0,0.05); margin-bottom: 20px;">
                <div style="margin-bottom: 12px;">{ASSISTFLOW_SVG_LOGO}</div>
                <h1 style="font-size: 2rem; font-weight: 900; color: #0284C7; margin: 0;">AssistFlow</h1>
                <p style="font-size: 0.95rem; font-weight: 700; color: #64748B; margin-top: 4px;">Enterprise AI Support & Operations</p>
            </div>""", 
            unsafe_allow_html=True
        )

        if db_error:
            st.error(db_error)

        tab_login, tab_signup = st.tabs(["🔒 Account Sign In", "✨ Register New Account"])

        departments_list = ["IT Operations", "Hardware & Systems", "Software Engineering", "Human Resources", "Finance & Accounting"]

        with tab_login:
            with st.form("login_form"):
                username = st.text_input("Corporate User ID", value="admin1")
                password = st.text_input("Password", type="password", value="admin123")
                login_role = st.selectbox("Select Access Role", ["Admin", "Technician", "Employee"], index=0)
                
                submitted = st.form_submit_button("Sign In to Portal ⚡", use_container_width=True)
                
                if submitted:
                    user = authenticate_user(username, password, login_role)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = user["username"]
                        st.session_state.user_role = user["role"]
                        st.session_state.user_department = user.get("department", "General IT")
                        st.success("Authentication successful!")
                        st.rerun()
                    else:
                        st.error("Invalid Corporate ID, Password, or Role.")

        with tab_signup:
            with st.form("signup_form"):
                new_user = st.text_input("New Corporate ID")
                new_pass = st.text_input("Create Password", type="password")
                new_role = st.selectbox("Role Assignment", ["Employee", "Technician", "Admin"])
                new_dept = st.selectbox("Department", departments_list)
                reg_submitted = st.form_submit_button("Create Account 🚀", use_container_width=True)

                if reg_submitted:
                    if not new_user or not new_pass:
                        st.warning("Please fill out all mandatory fields.")
                    else:
                        success, msg = register_user(new_user, new_pass, new_role, new_dept)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

# ==========================================
# DASHBOARD PAGE
# ==========================================
def render_dashboard():
    st.markdown(
        """
        <div class="hero-banner">
            <div>
                <h1 class="hero-title-main">AssistFlow</h1>
                <div class="hero-title-sub">Operational Performance & Live Telemetry</div>
            </div>
            <div>
                <span class="status-pill status-solved" style="background:#FFFFFF; color:#0284C7; border:none; font-size:0.85rem;">🟢 System Active</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tickets_list = get_cached_tickets()
    df = pd.DataFrame(tickets_list)

    total_tickets = len(df) if not df.empty else 0
    solved_count = len(df[df["status"] == "Solved"]) if not df.empty else 0
    processing_count = len(df[df["status"] == "Under Processing"]) if not df.empty else 0
    unsolved_count = len(df[df["status"] == "Unsolved"]) if not df.empty else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f'''<div class="glass-card"><div style="color:#64748B; font-weight:700; font-size:0.78rem; text-transform:uppercase;">Total Tickets</div><div style="font-size:2.2rem; font-weight:800; color:#0F172A;">{total_tickets}</div><div style="color:#64748B; font-size:0.78rem;">Database Records</div></div>''', unsafe_allow_html=True)
    m2.markdown(f'''<div class="glass-card"><div style="color:#D97706; font-weight:700; font-size:0.78rem; text-transform:uppercase;">In Progress</div><div style="font-size:2.2rem; font-weight:800; color:#D97706;">{processing_count}</div><div style="color:#64748B; font-size:0.78rem;">Active Tickets</div></div>''', unsafe_allow_html=True)
    m3.markdown(f'''<div class="glass-card"><div style="color:#059669; font-weight:700; font-size:0.78rem; text-transform:uppercase;">Resolved</div><div style="font-size:2.2rem; font-weight:800; color:#059669;">{solved_count}</div><div style="color:#059669; font-size:0.78rem; font-weight:600;">{(solved_count/total_tickets*100 if total_tickets else 0):.0f}% Resolution Rate</div></div>''', unsafe_allow_html=True)
    m4.markdown(f'''<div class="glass-card"><div style="color:#DC2626; font-weight:700; font-size:0.78rem; text-transform:uppercase;">Escalated</div><div style="font-size:2.2rem; font-weight:800; color:#DC2626;">{unsolved_count}</div><div style="color:#64748B; font-size:0.78rem;">Requires Action</div></div>''', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("📌 Resolution Distribution")
        if not df.empty and "status" in df.columns:
            status_counts = df["status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            fig = px.pie(status_counts, values="Count", names="Status", hole=0.6, color="Status",
                         color_discrete_map={"Solved": "#10B981", "Under Processing": "#F59E0B", "Unsolved": "#EF4444"})
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("🏷️ Tickets by Category")
        if not df.empty and "category" in df.columns:
            cat_counts = df["category"].value_counts().reset_index()
            cat_counts.columns = ["Category", "Count"]
            fig_bar = px.bar(cat_counts, x="Category", y="Count", color="Category", color_discrete_sequence=["#0284C7", "#0369A1", "#38BDF8", "#818CF8"])
            fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
            st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()
    st.subheader("📋 Live Tickets Log")

    if not df.empty:
        filter_col1, filter_col2, filter_col3 = st.columns([2, 1, 1])
        with filter_col1:
            search_query = st.text_input("🔍 Search Tickets", placeholder="Search by ID, Title, Author, Tech...").lower().strip()
        with filter_col2:
            categories_list = list(df["category"].unique()) if "category" in df.columns else []
            selected_categories = st.multiselect("Filter Category", options=categories_list, placeholder="All Categories")
        with filter_col3:
            priorities_list = ["Low", "Medium", "High", "Critical"]
            selected_priorities = st.multiselect("Filter Priority", options=priorities_list, placeholder="All Priorities")

        filtered_df = df.copy()

        if "assigned_tech" not in filtered_df.columns:
            filtered_df["assigned_tech"] = "Unassigned"
        else:
            filtered_df["assigned_tech"] = filtered_df["assigned_tech"].fillna("Unassigned")

        if selected_categories:
            filtered_df = filtered_df[filtered_df["category"].isin(selected_categories)]
        if selected_priorities:
            filtered_df = filtered_df[filtered_df["priority"].isin(selected_priorities)]

        if search_query:
            search_cols = ["ticket_id", "title", "author", "department", "assigned_tech", "description", "category"]
            mask = pd.Series(False, index=filtered_df.index)
            for col in search_cols:
                if col in filtered_df.columns:
                    mask |= filtered_df[col].astype(str).str.lower().str.contains(search_query, na=False)
            filtered_df = filtered_df[mask]

        cols_to_show = [c for c in ["ticket_id", "title", "category", "priority", "author", "department", "assigned_tech", "status", "created_at"] if c in filtered_df.columns]
        
        st.dataframe(
            filtered_df[cols_to_show].rename(columns={
                "ticket_id": "Ticket ID",
                "title": "Title",
                "category": "Category",
                "priority": "Priority",
                "author": "Author",
                "department": "Department",
                "assigned_tech": "Assigned Tech",
                "status": "Status",
                "created_at": "Created At"
            }),
            use_container_width=True, 
            hide_index=True
        )

# ==========================================
# RAISE TICKET PAGE
# ==========================================
def render_raise_ticket():
    st.markdown(
        """
        <div class="hero-banner">
            <div>
                <h1 class="hero-title-main">AssistFlow</h1>
                <div class="hero-title-sub">Submit Incident & AI Automated Diagnostics</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("ticket_form"):
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            title = st.text_input("Issue Summary", placeholder="e.g. Unable to connect to VPN gateway")
        with col2:
            category = st.selectbox("Category", ["Hardware", "Software", "Network & Internet", "Access / Permissions", "General IT"])
        with col3:
            priority = st.selectbox("Priority Level", ["Low", "Medium", "High", "Critical"], index=1)
            
        description = st.text_area("Detailed Problem Description", placeholder="Describe exact behavior or error codes...", height=110)
        selected_model = st.selectbox("AI Diagnostic Engine", ["llama3", "mistral", "phi3", "gemma"], index=0)
        
        submit_btn = st.form_submit_button("Submit & Generate AI Solution ⚡", use_container_width=True)

    if submit_btn:
        if not title or not description:
            st.warning("Please complete both summary and description fields.")
        else:
            with st.spinner("🤖 AssistFlow AI generating diagnostic resolution steps..."):
                sys_prompt = "You are an expert IT Support Engineer at AssistFlow. Provide concise troubleshooting steps."
                user_prompt = f"Category: {category}\nPriority: {priority}\nTitle: {title}\nDescription: {description}"
                ai_solution = call_ollama(user_prompt, model=selected_model, system_prompt=sys_prompt)
                
                ticket_count = db.tickets.count_documents({}) if db is not None else 1000
                ticket_id = f"TCK-{1001 + ticket_count}"
                
                new_ticket = {
                    "ticket_id": ticket_id,
                    "author": st.session_state.username,
                    "department": st.session_state.get("user_department", "General IT"),
                    "category": category,
                    "priority": priority,
                    "title": title,
                    "description": description,
                    "status": "Under Processing",
                    "assigned_tech": "Unassigned",
                    "ai_response": ai_solution,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "tech_notes": "Awaiting technician allocation."
                }
                
                if db is not None:
                    db.tickets.insert_one(new_ticket)
                    clear_db_caches()
                st.session_state.active_ticket_id = ticket_id
                st.success(f"Ticket `{ticket_id}` successfully submitted!")

    if "active_ticket_id" in st.session_state:
        current_id = st.session_state.active_ticket_id
        active_ticket = db.tickets.find_one({"ticket_id": current_id}) if db is not None else None
        
        if active_ticket:
            st.markdown(
                f"""
                <div class="glass-card" style="border-left: 5px solid #0284C7; margin: 20px 0;">
                    <div style="font-weight:800; color:#0284C7; font-size:1.05rem; margin-bottom:8px;">
                        ⚡ AI Automated Solution ({current_id})
                    </div>
                    <div style="background:#F8FAFC; padding:16px; border-radius:12px; border:1px solid #E2E8F0; line-height:1.6; color:#0F172A;">
                        {active_ticket["ai_response"].replace('\n', '<br>')}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            c1, c2 = st.columns([1, 1])
            with c1:
                if st.button("✅ Yes, Issue Resolved!", use_container_width=True):
                    db.tickets.update_one({"ticket_id": current_id}, {"$set": {"status": "Solved", "tech_notes": "Resolved via AI assistance."}})
                    clear_db_caches()
                    st.balloons()
                    st.success("Ticket closed and marked SOLVED.")
                    del st.session_state.active_ticket_id
                    st.rerun()

            with c2:
                if st.button("❌ Escalated to Technician Desk", use_container_width=True):
                    db.tickets.update_one({"ticket_id": current_id}, {"$set": {"status": "Unsolved", "tech_notes": "Escalated for technician intervention."}})
                    clear_db_caches()
                    st.error("Ticket escalated.")
                    del st.session_state.active_ticket_id
                    st.rerun()

# ==========================================
# ADMIN DESK PAGE
# ==========================================
def render_admin_desk():
    st.markdown(
        """
        <div class="hero-banner">
            <div>
                <h1 class="hero-title-main">AssistFlow</h1>
                <div class="hero-title-sub">Admin Desk — Ticket & Resource Allocation</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.subheader("🧑‍💻 Registered Technicians")
    all_users = get_cached_users()
    tech_users = [u for u in all_users if u.get("role") == "Technician"]
    tech_names = [t["username"] for t in tech_users]

    if tech_users:
        tech_df = pd.DataFrame(tech_users)[["username", "department", "created_at"]].rename(columns={
            "username": "Technician ID",
            "department": "Department",
            "created_at": "Registered Date"
        })
        st.dataframe(tech_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No technicians registered yet.")

    st.divider()

    st.subheader("🎫 Assign & Route Tickets")
    tickets = get_cached_tickets()
    if not tickets:
        st.info("No tickets currently logged in database.")
    else:
        df = pd.DataFrame(tickets)
        col_filter, col_sort = st.columns([2, 1])
        with col_filter:
            filter_status = st.multiselect("Filter Status", ["Under Processing", "Unsolved", "Solved"], default=["Under Processing", "Unsolved"])
        with col_sort:
            sort_priority = st.selectbox("Sort Priority", ["Default", "Highest Priority First", "Lowest Priority First"])

        filtered_df = df[df["status"].isin(filter_status)].copy() if not df.empty else df

        if not filtered_df.empty:
            priority_order = {"Critical": 1, "High": 2, "Medium": 3, "Low": 4}
            filtered_df["prio_rank"] = filtered_df["priority"].map(priority_order).fillna(5)
            if sort_priority == "Highest Priority First":
                filtered_df = filtered_df.sort_values(by="prio_rank", ascending=True)
            elif sort_priority == "Lowest Priority First":
                filtered_df = filtered_df.sort_values(by="prio_rank", ascending=False)

        for idx, row in filtered_df.iterrows():
            p_class = "status-solved" if row['status'] == "Solved" else "status-processing" if row['status'] == "Under Processing" else "status-unsolved"
            t_id = row['ticket_id']
            current_assigned = row.get("assigned_tech", "Unassigned")
            
            with st.expander(f"[{row['priority'].upper()}] [{t_id}] {row['title']} — {row['category']} (Assigned: {current_assigned})"):
                st.markdown(f"**Status:** <span class='status-pill {p_class}'>{row['status']}</span> | **Author:** `{row['author']}` | **Dept:** `{row.get('department', 'N/A')}` | **Date:** {row['created_at']}", unsafe_allow_html=True)
                st.info(row['description'])
                st.code(row['ai_response'], language=None)
                
                st.divider()
                c1, c2, c3 = st.columns([1.5, 1.5, 1])
                with c1:
                    tech_options = ["Unassigned"] + tech_names
                    default_idx = tech_options.index(current_assigned) if current_assigned in tech_options else 0
                    assigned_tech_sel = st.selectbox("Assign Technician", tech_options, index=default_idx, key=f"assign_{t_id}")
                with c2:
                    new_status = st.selectbox("Update State", ["Under Processing", "Solved", "Unsolved"], index=["Under Processing", "Solved", "Unsolved"].index(row['status']), key=f"status_{t_id}")
                with c3:
                    st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
                    save_btn = st.button("Save Updates", key=f"btn_{t_id}", use_container_width=True)

                new_notes = st.text_input("Notes", value=row.get('tech_notes', ''), key=f"notes_{t_id}")
                
                if save_btn:
                    db.tickets.update_one(
                        {"ticket_id": t_id},
                        {"$set": {
                            "assigned_tech": assigned_tech_sel,
                            "status": new_status,
                            "tech_notes": new_notes
                        }}
                    )
                    clear_db_caches()
                    st.success(f"Ticket `{t_id}` updated & assigned to `{assigned_tech_sel}`.")
                    st.rerun()

# ==========================================
# TECHNICIAN DESK PAGE
# ==========================================
def render_technician_desk():
    st.markdown(
        """
        <div class="hero-banner">
            <div>
                <h1 class="hero-title-main">AssistFlow</h1>
                <div class="hero-title-sub">Technician Workspace — Incidents & Bug Queue</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    current_tech = st.session_state.username
    all_tickets = get_cached_tickets()
    all_bugs = get_cached_bugs()

    tech_tickets = [t for t in all_tickets if t.get("assigned_tech") == current_tech]
    tech_bugs = [b for b in all_bugs if b.get("assigned_tech") == current_tech]

    tab_t_tickets, tab_t_bugs = st.tabs(["🎫 Assigned Tickets", "🐛 Assigned Bug Reports"])

    with tab_t_tickets:
        st.subheader(f"🛠️ Assigned Tickets ({len(tech_tickets)})")

        if not tech_tickets:
            st.info("🎉 No tickets assigned to you right now.")
        else:
            df = pd.DataFrame(tech_tickets)
            for idx, row in df.iterrows():
                p_class = "status-solved" if row['status'] == "Solved" else "status-processing" if row['status'] == "Under Processing" else "status-unsolved"
                t_id = row['ticket_id']
                
                with st.expander(f"[{row['priority'].upper()}] [{t_id}] {row['title']} — {row['category']}"):
                    st.markdown(f"**Status:** <span class='status-pill {p_class}'>{row['status']}</span> | **Author:** `{row['author']}` | **Dept:** `{row.get('department', 'N/A')}`", unsafe_allow_html=True)
                    st.info(f"**Description:**\n{row['description']}")
                    st.code(row['ai_response'], language=None)
                    st.divider()
                    
                    with st.form(key=f"tech_form_{t_id}"):
                        c1, c2 = st.columns([1, 2])
                        with c1:
                            status_opts = ["Under Processing", "Solved", "Unsolved"]
                            curr_idx = status_opts.index(row['status']) if row['status'] in status_opts else 0
                            tech_new_status = st.selectbox("Update Status", status_opts, index=curr_idx)
                        with c2:
                            tech_notes = st.text_input("Resolution Notes", value=row.get('tech_notes', ''))
                        
                        tech_submit = st.form_submit_button("Save Changes ⚡", use_container_width=True)

                        if tech_submit:
                            if db is not None:
                                db.tickets.update_one(
                                    {"ticket_id": t_id},
                                    {"$set": {
                                        "status": tech_new_status,
                                        "tech_notes": tech_notes
                                    }}
                                )
                                clear_db_caches()
                                st.success(f"Ticket `{t_id}` updated.")
                                st.rerun()

    with tab_t_bugs:
        st.subheader(f"🐛 Assigned Bugs ({len(tech_bugs)})")

        if not tech_bugs:
            st.info("🎉 No bugs assigned to you.")
        else:
            for bug in tech_bugs:
                b_id = bug.get('bug_id', 'BUG-000')
                b_status = bug.get('status', 'In Review')
                p_class = "status-solved" if b_status == "Solved" else "status-processing" if b_status == "Under Processing" else "status-unsolved"

                with st.expander(f"[{bug.get('severity', 'Medium').upper()}] [{b_id}] {bug['title']}"):
                    st.markdown(f"**Status:** <span class='status-pill {p_class}'>{b_status}</span> | **Component:** `{bug.get('component', 'General')}`", unsafe_allow_html=True)
                    st.write(f"**Steps to Reproduce:**\n{bug['description']}")
                    
                    st.divider()
                    with st.form(key=f"tech_bug_form_{b_id}"):
                        b_status_opts = ["In Review", "Under Processing", "Solved"]
                        curr_b_idx = b_status_opts.index(b_status) if b_status in b_status_opts else 0
                        new_b_status = st.selectbox("Update Bug Status", b_status_opts, index=curr_b_idx)
                        b_submit = st.form_submit_button("Update Bug Status ⚡", use_container_width=True)
                        
                        if b_submit:
                            if db is not None:
                                db.bug_reports.update_one(
                                    {"bug_id": b_id},
                                    {"$set": {"status": new_b_status}}
                                )
                                clear_db_caches()
                                st.success(f"Bug `{b_id}` updated.")
                                st.rerun()

# ==========================================
# MODERN HIGH-PERFORMANCE PROFILE PAGE
# ==========================================
def render_profile():
    username = st.session_state.username
    role = st.session_state.user_role
    department = st.session_state.user_department

    user_info = db.users.find_one({"username": username}) if db is not None else None
    joined_date = user_info.get("created_at", datetime.now().strftime("%Y-%m-%d")) if user_info else "N/A"

    # Hero Cover Banner & Avatar
    st.markdown(
        f"""
        <div class="glass-card" style="padding: 0; overflow: hidden; margin-bottom: 24px;">
            <div class="profile-cover"></div>
            <div style="padding: 0 28px 24px 28px; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: flex-end; gap: 20px;">
                <div style="display: flex; align-items: flex-end; gap: 20px;">
                    <div class="profile-avatar-wrapper">
                        <img class="profile-avatar-img" src="{AVATAR_USER}" alt="User Avatar" />
                    </div>
                    <div style="margin-bottom: 4px;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <h2 style="font-size: 1.8rem; font-weight: 800; color: #0F172A; margin: 0;">{username}</h2>
                            <span class="profile-badge-pill" style="background: #E0F2FE; color: #0284C7; border-color: #BAE6FD;">
                                ✓ Verified User
                            </span>
                        </div>
                        <p style="margin: 2px 0 0 0; color: #64748B; font-weight: 600; font-size: 0.92rem;">
                            {role} • <span style="color: #0284C7;">{department}</span>
                        </p>
                    </div>
                </div>
                <div style="display: flex; gap: 10px; margin-bottom: 6px;">
                    <span class="profile-badge-pill">🗓️ Joined: {joined_date}</span>
                    <span class="profile-badge-pill" style="background: #DCFCE7; color: #15803D; border-color: #86EFAC;">🟢 Active Session</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Modern Profile Details Grid
    t1, t2, t3 = st.tabs(["📊 Activity & Key Performance Metrics", "👤 Account & Personal Information", "🔒 Security & Permissions"])

    all_tickets = get_cached_tickets()
    all_bugs = get_cached_bugs()

    with t1:
        st.markdown("<br>", unsafe_allow_html=True)
        if role == "Employee":
            user_tickets = [t for t in all_tickets if t.get("author") == username]
            solved_tickets = [t for t in user_tickets if t.get("status") == "Solved"]
            pending_tickets = [t for t in user_tickets if t.get("status") == "Under Processing"]

            m1, m2, m3 = st.columns(3)
            m1.markdown(f'''<div class="glass-card"><div style="color:#64748B; font-weight:700; font-size:0.8rem; text-transform:uppercase;">Submitted Tickets</div><div style="font-size:2.2rem; font-weight:800; color:#0F172A;">{len(user_tickets)}</div></div>''', unsafe_allow_html=True)
            m2.markdown(f'''<div class="glass-card"><div style="color:#059669; font-weight:700; font-size:0.8rem; text-transform:uppercase;">Resolved Issues</div><div style="font-size:2.2rem; font-weight:800; color:#059669;">{len(solved_tickets)}</div></div>''', unsafe_allow_html=True)
            m3.markdown(f'''<div class="glass-card"><div style="color:#D97706; font-weight:700; font-size:0.8rem; text-transform:uppercase;">In Progress</div><div style="font-size:2.2rem; font-weight:800; color:#D97706;">{len(pending_tickets)}</div></div>''', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("📋 Your Recent Ticket History")
            if user_tickets:
                df_u = pd.DataFrame(user_tickets)[["ticket_id", "title", "category", "priority", "status", "created_at"]]
                st.dataframe(df_u.rename(columns={
                    "ticket_id": "Ticket ID", "title": "Title", "category": "Category",
                    "priority": "Priority", "status": "Status", "created_at": "Date"
                }), use_container_width=True, hide_index=True)
            else:
                st.info("You haven't submitted any support tickets yet.")

        elif role == "Technician":
            assigned_tickets = [t for t in all_tickets if t.get("assigned_tech") == username]
            assigned_bugs = [b for b in all_bugs if b.get("assigned_tech") == username]
            solved_tech = [t for t in assigned_tickets if t.get("status") == "Solved"]

            m1, m2, m3 = st.columns(3)
            m1.markdown(f'''<div class="glass-card"><div style="color:#0284C7; font-weight:700; font-size:0.8rem; text-transform:uppercase;">Assigned Tickets</div><div style="font-size:2.2rem; font-weight:800; color:#0284C7;">{len(assigned_tickets)}</div></div>''', unsafe_allow_html=True)
            m2.markdown(f'''<div class="glass-card"><div style="color:#059669; font-weight:700; font-size:0.8rem; text-transform:uppercase;">Tickets Closed</div><div style="font-size:2.2rem; font-weight:800; color:#059669;">{len(solved_tech)}</div></div>''', unsafe_allow_html=True)
            m3.markdown(f'''<div class="glass-card"><div style="color:#D97706; font-weight:700; font-size:0.8rem; text-transform:uppercase;">Assigned Bug Reports</div><div style="font-size:2.2rem; font-weight:800; color:#D97706;">{len(assigned_bugs)}</div></div>''', unsafe_allow_html=True)

        elif role == "Admin":
            all_users = get_cached_users()
            m1, m2, m3 = st.columns(3)
            m1.markdown(f'''<div class="glass-card"><div style="color:#0284C7; font-weight:700; font-size:0.8rem; text-transform:uppercase;">Total Portal Tickets</div><div style="font-size:2.2rem; font-weight:800; color:#0284C7;">{len(all_tickets)}</div></div>''', unsafe_allow_html=True)
            m2.markdown(f'''<div class="glass-card"><div style="color:#059669; font-weight:700; font-size:0.8rem; text-transform:uppercase;">System Bug Logs</div><div style="font-size:2.2rem; font-weight:800; color:#059669;">{len(all_bugs)}</div></div>''', unsafe_allow_html=True)
            m3.markdown(f'''<div class="glass-card"><div style="color:#6366F1; font-weight:700; font-size:0.8rem; text-transform:uppercase;">Registered Accounts</div><div style="font-size:2.2rem; font-weight:800; color:#6366F1;">{len(all_users)}</div></div>''', unsafe_allow_html=True)

    with t2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("⚙️ Account Details & Information")
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("User Corporate Handle", value=username, disabled=True)
            st.text_input("Assigned Role", value=role, disabled=True)
        with c2:
            st.text_input("Department / Unit", value=department, disabled=True)
            st.text_input("Registration Date", value=joined_date, disabled=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with t3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("🔐 Security & Session Protocol")
        st.write("Your session is authenticated via bcrypt hashed encryption connected to MongoDB.")
        
        s1, s2 = st.columns(2)
        with s1:
            st.markdown("• **Access Control Level:** Tier " + ("1 (Administrator)" if role == "Admin" else "2 (Technician)" if role == "Technician" else "3 (General Employee)"))
            st.markdown("• **Encryption Algorithm:** bcrypt blowfish cipher")
        with s2:
            st.markdown("• **Session Type:** SSO Active Session")
            st.markdown("• **Database Integrity:** Connected & Online")
        st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# AI CHATBOT PAGE
# ==========================================
def render_chatbot():
    st.markdown(
        """
        <div class="hero-banner">
            <div>
                <h1 class="hero-title-main">AssistFlow</h1>
                <div class="hero-title-sub">Virtual Assistant & AI Diagnostic Desk</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    is_admin = (st.session_state.get("user_role") == "Admin")

    if is_admin:
        st.markdown("### 📊 AI System Analysis (Admin)")
        with st.expander("🤖 Execute Database Telemetry AI Analysis", expanded=True):
            col_an1, col_an2 = st.columns([1, 2])
            with col_an1:
                analysis_model = st.selectbox("Engine", ["llama3", "mistral", "phi3", "gemma"], key="admin_analysis_model")
            with col_an2:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                run_analysis = st.button("Run AI Analysis ⚡", use_container_width=True)

            if run_analysis:
                tickets = get_cached_tickets()
                if not tickets:
                    st.warning("No tickets in database.")
                else:
                    with st.spinner("🤖 AI analyzing ticket telemetry..."):
                        ticket_logs = "\n".join([f"- [{t['ticket_id']}] Category: {t['category']} | Title: {t['title']} | Desc: {t['description']}" for t in tickets])
                        prompt = f"Analyze IT tickets:\n\n{ticket_logs}\n\nProvide root cause analysis and remediation steps."
                        sys_prompt = "You are a CIO analyzing enterprise support issues."
                        
                        analysis_res = call_ollama(prompt, model=analysis_model, system_prompt=sys_prompt)
                        st.session_state.admin_analysis_result = analysis_res

            if "admin_analysis_result" in st.session_state:
                st.markdown(
                    f"""
                    <div class="glass-card" style="border-left: 5px solid #0284C7; margin-top: 15px;">
                        <div style="font-weight:800; color:#0284C7; font-size:1.05rem; margin-bottom:8px;">
                            ⚡ AI Telemetry Summary Report
                        </div>
                        <div style="color:#0F172A; line-height:1.6; font-size:0.92rem; background:#F8FAFC; padding:16px; border-radius:12px; border:1px solid #E2E8F0;">
                            {st.session_state.admin_analysis_result.replace('\n', '<br>')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.divider()

    c1, c2 = st.columns([3, 1])
    with c2:
        model_choice = st.selectbox("Ollama Engine", ["llama3", "mistral", "phi3", "gemma"], index=0)
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.chat_messages = [{"role": "assistant", "avatar": AVATAR_AI, "content": "🤖 Chat reset. How can I help you?"}]
            st.rerun()

    with c1:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"], avatar=msg.get("avatar")):
                st.markdown(msg["content"])

        if user_input := st.chat_input("Ask a question..."):
            st.session_state.chat_messages.append({"role": "user", "avatar": AVATAR_USER, "content": user_input})
            with st.chat_message("user", avatar=AVATAR_USER):
                st.markdown(user_input)

            with st.chat_message("assistant", avatar=AVATAR_AI):
                with st.spinner("AI thinking..."):
                    sys_prompt = "You are an IT Support Virtual Assistant at AssistFlow."
                    response = call_ollama(user_input, model=model_choice, system_prompt=sys_prompt)
                    st.markdown(response)
                    
            st.session_state.chat_messages.append({"role": "assistant", "avatar": AVATAR_AI, "content": response})

# ==========================================
# REPORT BUG PAGE
# ==========================================
def render_support():
    st.markdown(
        """
        <div class="hero-banner">
            <div>
                <h1 class="hero-title-main">AssistFlow</h1>
                <div class="hero-title-sub">Report Bug & Bug Routing Portal</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    tab_bug, tab_list = st.tabs(["🐛 Report a Bug", "📋 System Bug Log & Technician Allocation"])

    with tab_bug:
        with st.form("bug_report_form"):
            bug_title = st.text_input("Bug / Issue Summary", placeholder="e.g. Navigation menu flickering")
            c1, c2 = st.columns(2)
            with c1:
                bug_component = st.selectbox("Component", ["Navigation", "Dashboard", "Ticket Form", "AI Assistant", "Admin Desk", "Technician Desk"])
            with c2:
                bug_severity = st.selectbox("Severity", ["Low", "Medium", "High", "Critical"])
            
            bug_desc = st.text_area("Steps to Reproduce", height=110)
            submit_bug = st.form_submit_button("Submit Bug Report 🚀", use_container_width=True)

        if submit_bug:
            if not bug_title or not bug_desc:
                st.warning("Please enter a title and description.")
            else:
                bug_count = db.bug_reports.count_documents({}) if db is not None else 200
                bug_id = f"BUG-{201 + bug_count}"
                
                if db is not None:
                    db.bug_reports.insert_one({
                        "bug_id": bug_id,
                        "author": st.session_state.username,
                        "title": bug_title,
                        "severity": bug_severity,
                        "component": bug_component,
                        "description": bug_desc,
                        "assigned_tech": "Unassigned",
                        "status": "In Review",
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    clear_db_caches()
                st.balloons()
                st.success(f"Bug report `{bug_id}` saved in Database!")

    with tab_list:
        bugs = get_cached_bugs()
        tech_users = [u for u in get_cached_users() if u.get("role") == "Technician"]
        tech_names = [t["username"] for t in tech_users]

        if not bugs:
            st.info("No bug reports logged.")
        else:
            is_admin = (st.session_state.get("user_role") == "Admin")

            for bug in reversed(bugs):
                b_id = bug.get('bug_id', 'BUG-000')
                status = bug.get('status', 'In Review')
                assigned_tech = bug.get('assigned_tech', 'Unassigned')
                p_class = "status-solved" if status == "Solved" else "status-processing" if status == "Under Processing" else "status-unsolved"

                st.markdown(
                    f"""
                    <div class="glass-card" style="margin-bottom: 12px; border-left: 5px solid #0284C7;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div style="font-weight:800; font-size:1rem; color:#0F172A;">[{b_id}] {bug['title']}</div>
                            <span class="status-pill {p_class}">{status}</span>
                        </div>
                        <div style="font-size:0.83rem; color:#64748B; margin-top: 4px;">
                            Component: <b>{bug.get('component', 'General')}</b> | Severity: <b>{bug.get('severity', 'Low')}</b> | Reporter: <code>{bug.get('author', 'Anonymous')}</code> | Assigned Tech: <code style="color:#0284C7; font-weight:700;">{assigned_tech}</code>
                        </div>
                        <div style="margin-top:8px; font-size:0.9rem; line-height: 1.4; color:#334155;">{bug['description']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if is_admin:
                    with st.expander(f"🛠️ Admin Action: Assign Technician & Status for [{b_id}]"):
                        c1, c2, c3 = st.columns([1.5, 1.5, 1])
                        with c1:
                            tech_options = ["Unassigned"] + tech_names
                            tech_default_idx = tech_options.index(assigned_tech) if assigned_tech in tech_options else 0
                            new_bug_tech = st.selectbox("Assign Technician", tech_options, index=tech_default_idx, key=f"bug_tech_sel_{b_id}")
                        with c2:
                            status_options = ["In Review", "Under Processing", "Solved"]
                            curr_index = status_options.index(status) if status in status_options else 0
                            new_bug_status = st.selectbox("Update Status", status_options, index=curr_index, key=f"bug_status_sel_{b_id}")
                        with c3:
                            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                            if st.button("Save Updates", key=f"btn_update_bug_{b_id}", use_container_width=True):
                                if db is not None:
                                    db.bug_reports.update_one(
                                        {"bug_id": b_id},
                                        {"$set": {
                                            "assigned_tech": new_bug_tech,
                                            "status": new_bug_status
                                        }}
                                    )
                                    clear_db_caches()
                                    st.success(f"Bug `{b_id}` updated!")
                                    st.rerun()

# ==========================================
# MAIN ROUTER & SIDEBAR NAVIGATION
# ==========================================
def main():
    if not st.session_state.logged_in:
        render_login()
    else:
        with st.sidebar:
            st.markdown(f"""<div style="text-align: center; padding: 10px 0 16px 0; border-bottom: 1px solid #E2E8F0;">{ASSISTFLOW_SVG_LOGO}</div>""", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background:linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%); border-radius:16px; padding:14px; margin: 16px 0 20px 0; border:1px solid #E2E8F0; display:flex; align-items:center; gap:12px;">
                <img src="{AVATAR_USER}" width="38" height="38">
                <div>
                    <div style="font-weight:800; font-size:0.95rem; color:#0F172A;">{st.session_state.username}</div>
                    <div style="font-size:0.75rem; color:#0284C7; font-weight:800; text-transform:uppercase;">{st.session_state.user_role}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<p style='font-weight:800; font-size:0.72rem; color:#94A3B8; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;'>Navigation Menu</p>", unsafe_allow_html=True)

            if st.session_state.user_role == "Admin":
                nav_options = ["📊 Dashboard", "🛠️ Admin Desk", "👤 Profile", "💬 AI Assistant", "🐛 Report Bug"]
            elif st.session_state.user_role == "Technician":
                nav_options = ["📊 Dashboard", "🛠️ Technician Desk", "👤 Profile", "💬 AI Assistant", "🐛 Report Bug"]
            else:
                nav_options = ["📊 Dashboard", "🎫 Raise a Ticket", "👤 Profile", "💬 AI Assistant", "🐛 Report Bug"]
            
            choice = st.radio("Navigation Menu", nav_options)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪 Sign Out", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.session_state.user_role = ""
                st.session_state.user_department = ""
                st.rerun()

        if choice == "📊 Dashboard":
            render_dashboard()
        elif choice == "🎫 Raise a Ticket":
            render_raise_ticket()
        elif choice == "🛠️ Admin Desk":
            render_admin_desk()
        elif choice == "🛠️ Technician Desk":
            render_technician_desk()
        elif choice == "👤 Profile":
            render_profile()
        elif choice == "💬 AI Assistant":
            render_chatbot()
        elif choice == "🐛 Report Bug":
            render_support()

if __name__ == "__main__":
    main()