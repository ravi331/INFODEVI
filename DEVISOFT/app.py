import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random, os, time
from io import BytesIO

# ---------------------------------
# Page & light theme polish
# ---------------------------------
st.set_page_config(page_title="SGS Annual Function", layout="wide", page_icon="🎉")
st.markdown("""
<style>
    .main { background: #faf7ff; }
    .sgs-banner {
        background: linear-gradient(90deg, #7c3aed, #f59e0b);
        color: white; padding: 12px 18px; border-radius: 14px;
        margin-bottom: 10px; font-weight: 700; font-size: 18px;
        display: inline-block;
    }
    .chip {
        display:inline-block;background:#7c3aed10;color:#7c3aed;border:1px solid #7c3aed33;
        padding:6px 10px;border-radius:999px;font-weight:600;margin:6px 0;
    }
    .countdown {
        font-size: 18px; font-weight: 600; color:#111; margin-top:10px
    }
    .muted { color:#666; font-size: 13px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding: 10px 16px; border-radius: 10px; background:#ffffffaa; }
    .stButton>button { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# Constants & files
# ---------------------------------
ADMIN_PASSWORD = "sgs2025"
REG_FILE = "registrations.csv"
NOTICE_FILE = "notices.csv"
ALLOWED_FILE = "allowed_users.csv"   # must be in same folder as app.py

# Event date for countdown (YYYY, MM, DD, HH, MM) -> set time if you like
EVENT_DATETIME = datetime(2025, 12, 20, 0, 0, 0)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALLOWED_PATH = os.path.join(BASE_DIR, ALLOWED_FILE)

# ---------------------------------
# Helpers
# ---------------------------------
def load_csv(file, columns):
    try:
        return pd.read_csv(file)
    except Exception:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file, index=False)
        return df

def normalize_10_digits(series: pd.Series) -> pd.Series:
    return (series.astype(str)
                 .str.replace(" ", "", regex=False)
                 .str.replace("+91", "", regex=False)
                 .str.replace("-", "", regex=False)
                 .str.strip()
                 .str[-10:])

def fmt_delta(td: timedelta) -> str:
    # Avoid negatives after event
    total_secs = max(int(td.total_seconds()), 0)
    days = total_secs // 86400
    hours = (total_secs % 86400) // 3600
    minutes = (total_secs % 3600) // 60
    seconds = total_secs % 60
    return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Registrations")
    return output.getvalue()

# ---------------------------------
# Load data
# ---------------------------------
reg_df    = load_csv(REG_FILE,   ["Timestamp","Name","Class","Section","Item","Contact","Address","Bus","Status"])
notice_df = load_csv(NOTICE_FILE,["Timestamp","Title","Message","PostedBy"])

# Allowed users (silent)
allowed_df = pd.read_csv(ALLOWED_PATH)
allowed_df["mobile_number"] = normalize_10_digits(allowed_df["mobile_number"])

# ---------------------------------
# Session state
# ---------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "mobile" not in st.session_state:
    st.session_state.mobile = ""
if "otp" not in st.session_state:
    st.session_state.otp = None
if "welcomed" not in st.session_state:
    st.session_state.welcomed = False

# ---------------------------------
# Sidebar: Login/Logout
# ---------------------------------
def login_sidebar():
    st.sidebar.header("Login")
    if not st.session_state.logged_in:
        mobile = st.sidebar.text_input("Enter 10-digit Mobile").strip()
        if len(mobile) > 10:
            mobile = mobile[-10:]

        if st.sidebar.button("Send OTP"):
            if mobile in allowed_df["mobile_number"].values:
                otp = str(random.randint(100000, 999999))
                st.session_state.otp = otp
                st.session_state.mobile = mobile
                # Test mode: show OTP on screen
                st.sidebar.success(f"OTP (Test Mode): {otp}")
            else:
                st.sidebar.error("❌ This number is not registered.")

        if st.session_state.otp:
            code = st.sidebar.text_input("Enter OTP")
            if st.sidebar.button("Verify"):
                if code == st.session_state.otp:
                    st.session_state.logged_in = True
                    st.session_state.welcomed = False  # show welcome once
                    st.sidebar.success("✅ Login successful!")
                    st.session_state.otp = None
                else:
                    st.sidebar.error("❌ Wrong OTP")
    else:
        st.sidebar.success(f"Logged in: {st.session_state.mobile}")
        if st.sidebar.button("Logout"):
            for k in ["logged_in","mobile","otp","welcomed"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

login_sidebar()
if not st.session_state.logged_in:
    st.stop()

# ---------------------------------
# Header / Banner
# ---------------------------------
st.markdown('<div class="sgs-banner">SGS AnnualFunction 2025</div>', unsafe_allow_html=True)

# ---------------------------------
# One-time welcome with mascot + quick countdown
# ---------------------------------
if not st.session_state.welcomed:
    c1, c2 = st.columns([1,2], vertical_alignment="center")
    with c1:
        # Show mascot if available
        if os.path.exists(os.path.join(BASE_DIR, "mascot.png")):
            st.image("mascot.png", width=220)
        elif os.path.exists(os.path.join(BASE_DIR, "logo.png")):
            st.image("logo.png", width=220)
    with c2:
        st.subheader(f"🎉 Welcome, {st.session_state.mobile}!")
        st.write("You're now logged in. Taking you to the Home page…")
        with st.empty():
            for i in range(3, 0, -1):
                st.write(f"Redirecting in **{i}** seconds…")
                time.sleep(1)
    st.session_state.welcomed = True
    st.rerun()

# ---------------------------------
# Tabs
# ---------------------------------
tabs = st.tabs(["Home", "Registration", "List", "Notices", "Admin"])

# HOME TAB
with tabs[0]:
    # Top row: Event logo (if any) and title
    ctop1, ctop2 = st.columns([1,3])
    # Try common file names for annual day logo
    event_logo_candidates = ["annual_logo.png", "annualday.png", "annual_day.png", "logo.png"]
    event_logo = next((f for f in event_logo_candidates if os.path.exists(os.path.join(BASE_DIR, f))), None)
    if event_logo:
        with ctop1:
            st.image(event_logo, width=260)
    with ctop2:
        st.title("St. Gregorios H.S. School")
        st.subheader("45th Annual Day – Talent Meets Opportunity")

    # Mascot line (optional repeat)
    if os.path.exists(os.path.join(BASE_DIR, "mascot.png")):
        st.image("mascot.png", width=180)

    # Countdown (recomputed on every rerun)
    now = datetime.now()
    remaining = EVENT_DATETIME - now
    if remaining.total_seconds() > 0:
        st.markdown(
            f"<div class='countdown'>🎉 Annual Function ({EVENT_DATETIME.date()}) starts in "
            f"{fmt_delta(remaining)}</div>",
            unsafe_allow_html=True
        )
        # Light auto-refresh so seconds tick (every 1s)
        st.experimental_rerun  # (no call; Streamlit reruns on any interaction)
    else:
        st.success("🎊 The Annual Function day has arrived. Enjoy the event!")

    st.markdown("<p class='muted'>Logged in as " + st.session_state.mobile + "</p>", unsafe_allow_html=True)

# REGISTRATION TAB
with tabs[1]:
    st.header("Register")
    with st.form("reg"):
        name = st.text_input("Name")
        clas = st.text_input("Class")
        sec = st.text_input("Section")
        item = st.text_input("Item")
        address = st.text_area("Address")
        bus = st.radio("Using Bus?", ["Yes", "No"])
        contact = st.text_input("Contact", value=st.session_state.mobile)
        submitted = st.form_submit_button("Submit")
        if submitted:
            df = load_csv(REG_FILE, ["Timestamp","Name","Class","Section","Item","Contact","Address","Bus","Status"])
            df.loc[len(df)] = [datetime.now(), name, clas, sec, item, contact, address, bus, "Pending"]
            df.to_csv(REG_FILE, index=False)
            st.success("✅ Registered Successfully!")

# LIST TAB + Excel export
with tabs[2]:
    st.header("Registered Students")
    reg_view = load_csv(REG_FILE, ["Timestamp","Name","Class","Section","Item","Contact","Address","Bus","Status"])
    st.dataframe(reg_view, use_container_width=True)

    excel_bytes = to_excel_bytes(reg_view)
    st.download_button(
        label="⬇️ Download Registrations (Excel)",
        data=excel_bytes,
        file_name="registrations.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

# NOTICES TAB
with tabs[3]:
    st.header("Notices")
    df = load_csv(NOTICE_FILE, ["Timestamp","Title","Message","PostedBy"])
    if df.empty:
        st.info("No notices available")
    else:
        for _, r in df.iterrows():
            ts = ""
            if pd.notnull(r.get("Timestamp", "")):
                try:
                    ts = pd.to_datetime(r["Timestamp"]).strftime("%d-%b-%Y %I:%M %p")
                except Exception:
                    ts = str(r["Timestamp"])
            st.write(f"""
### {r['Title']}
{r['Message']}
*Posted by {r['PostedBy']} {('on ' + ts) if ts else ''}*
""")

# ADMIN TAB (password protected)
with tabs[4]:
    st.header("Admin Section")
    pw = st.text_input("Admin Password", type="password")
    if st.button("Login as Admin"):
        if pw == ADMIN_PASSWORD:
            st.success("✅ Admin Logged In")
            st.markdown("**Post a Notice**")
            title = st.text_input("Notice Title")
            msg = st.text_area("Message")
            by = st.text_input("Posted By", value="Admin")
            if st.button("Post Notice"):
                df = load_csv(NOTICE_FILE, ["Timestamp","Title","Message","PostedBy"])
                df.loc[len(df)] = [datetime.now(), title, msg, by]
                df.to_csv(NOTICE_FILE, index=False)
                st.success("✅ Notice Posted")
        else:
            st.error("❌ Incorrect password")
