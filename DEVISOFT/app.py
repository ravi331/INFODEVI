import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random, os, time
from io import BytesIO

# -----------------------------------------
# Page & Style
# -----------------------------------------
st.set_page_config(page_title="SGS Annual Function", layout="wide", page_icon="🎉")

st.markdown("""
<style>
    .main { background: #fafbff; }
    .sgs-banner {
        background: linear-gradient(90deg, #7c3aed, #f59e0b);
        color: white; padding: 12px 18px; border-radius: 14px;
        margin-bottom: 15px; font-weight: bold; font-size: 20px;
        display: inline-block;
    }
    .countdown { font-size: 18px; font-weight: 600; color:#222; margin-top:10px }
    .notice-banner {
        background: #fff7e6; border:1px solid #ffddaa; color:#7a4c00;
        padding:10px; border-radius:10px; margin-bottom:15px;
    }
    .muted { color:#666; font-size:13px; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { padding:10px 16px; border-radius:10px; background:#ffffffaa; }
    .stButton>button { border-radius:10px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------
# Configuration
# -----------------------------------------
ADMIN_PASSWORD = "sgs2025"
REG_FILE = "registrations.csv"
NOTICE_FILE = "notices.csv"
ALLOWED_FILE = "allowed_users.csv"

EVENT_DATETIME = datetime(2025, 12, 20, 0, 0, 0)   # For countdown

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -----------------------------------------
# Helper Functions
# -----------------------------------------
def load_csv(file, columns):
    """Loads or creates a CSV file with given columns"""
    try:
        return pd.read_csv(file)
    except:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file, index=False)
        return df

def normalize_10_digits(series):
    """Converts phone numbers to 10-digit string"""
    return (series.astype(str)
                .str.replace(" ", "", regex=False)
                .str.replace("+91", "", regex=False)
                .str.replace("-", "", regex=False)
                .str.strip()
                .str[-10:])

def time_difference(event_time):
    """Formats remaining time for countdown"""
    diff = event_time - datetime.now()
    if diff.total_seconds() < 0:
        return "Today is the event! 🎉"
    days = diff.days
    hours, rem = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"

def safe_show_image(filename, width=None):
    """Safely loads and displays images without breaking"""
    path = os.path.join(BASE_DIR, filename)
    if os.path.exists(path):
        st.image(path, width=width)

def to_excel_bytes(df):
    """Exports DataFrame to Excel without extra dependencies like xlsxwriter"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Registrations")
    output.seek(0)
    return output.read()

# -----------------------------------------
# Load CSV Data
# -----------------------------------------
reg_df = load_csv(REG_FILE, ["Timestamp","Name","Class","Section","Item","Contact","Address","Bus","Status"])
notice_df = load_csv(NOTICE_FILE, ["Timestamp","Title","Message","PostedBy"])
allowed_df = load_csv(ALLOWED_FILE, ["mobile_number","name"])
allowed_df["mobile_number"] = normalize_10_digits(allowed_df["mobile_number"])

# -----------------------------------------
# Session States
# -----------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "mobile" not in st.session_state:
    st.session_state.mobile = ""
if "otp" not in st.session_state:
    st.session_state.otp = None
if "welcomed" not in st.session_state:
    st.session_state.welcomed = False

# -----------------------------------------
# Sidebar Login System
# -----------------------------------------
def login_sidebar():
    st.sidebar.header("Login")
    if not st.session_state.logged_in:
        mobile = st.sidebar.text_input("Enter 10-digit mobile").strip()
        if len(mobile) > 10:
            mobile = mobile[-10:]

        if st.sidebar.button("Send OTP"):
            if mobile in allowed_df["mobile_number"].values:
                otp = str(random.randint(100000, 999999))
                st.session_state.otp = otp
                st.session_state.mobile = mobile
                st.sidebar.success(f"OTP (Test Mode): {otp}")
            else:
                st.sidebar.error("❌ Number not registered")

        if st.session_state.otp:
            code = st.sidebar.text_input("Enter OTP")
            if st.sidebar.button("Verify"):
                if code == st.session_state.otp:
                    st.session_state.logged_in = True
                    st.session_state.welcomed = False
                    st.sidebar.success("✅ Login successful")
                else:
                    st.sidebar.error("❌ Incorrect OTP")
    else:
        st.sidebar.success(f"Logged in: {st.session_state.mobile}")
        if st.sidebar.button("Logout"):
            for key in ["logged_in","otp","mobile","welcomed"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

login_sidebar()
if not st.session_state.logged_in:
    st.stop()

# -----------------------------------------
# Welcome Banner (Only Once Per Session)
# -----------------------------------------
st.markdown('<div class="sgs-banner">SGS Annual Function 2025</div>', unsafe_allow_html=True)

if not st.session_state.welcomed:
    c1, c2 = st.columns([1,2])
    with c1:
        safe_show_image("mascot.png", width=200)
    with c2:
        st.subheader(f"🎉 Welcome, {st.session_state.mobile}!")
        st.write("Redirecting to Home...")
        for i in range(3, 0, -1):
            st.write(f"Redirecting in {i} seconds...")
            time.sleep(1)
    st.session_state.welcomed = True
    st.rerun()

# -----------------------------------------
# Main Tabs
# -----------------------------------------
tabs = st.tabs(["Home", "Registration", "List", "Notices", "Admin"])

# Home Tab
with tabs[0]:
    left, right = st.columns([1,3])
    with left:
        safe_show_image("mascot.png", width=200)
    with right:
        safe_show_image("logo.png", width=350)
        st.title("St. Gregorios H.S. School")
        st.subheader("45th Annual Day – Talent Meets Opportunity")

    # Show latest notice (optional)
    df = load_csv(NOTICE_FILE, ["Timestamp","Title","Message","PostedBy"])
    if not df.empty:
        last = df.iloc[-1]
        st.markdown(f"<div class='notice-banner'>📢 <b>{last['Title']}</b><br>{last['Message']}</div>", unsafe_allow_html=True)

    # Countdown
    st.markdown(f"<div class='countdown'>⏳ Event Countdown: {time_difference(EVENT_DATETIME)}</div>", unsafe_allow_html=True)
    st.caption(f"Logged in as: {st.session_state.mobile}")

# Registration Tab
with tabs[1]:
    st.header("Register for an Event")
    with st.form("reg_form"):
        name = st.text_input("Name")
        clas = st.text_input("Class")
        sec = st.text_input("Section")
        item = st.text_input("Event / Item")
        address = st.text_area("Address")
        bus = st.radio("Using Bus?", ["Yes","No"])
        contact = st.text_input("Contact", value=st.session_state.mobile)
        if st.form_submit_button("Submit"):
            df = load_csv(REG_FILE, ["Timestamp","Name","Class","Section","Item","Contact","Address","Bus","Status"])
            df.loc[len(df)] = [datetime.now(), name, clas, sec, item, contact, address, bus, "Pending"]
            df.to_csv(REG_FILE, index=False)
            st.success("✅ Registration Submitted!")

# List Tab with Excel Export
with tabs[2]:
    st.header("Registered Students")
    r = load_csv(REG_FILE, ["Timestamp","Name","Class","Section","Item","Contact","Address","Bus","Status"])
    st.dataframe(r, use_container_width=True)

    excel_data = to_excel_bytes(r)
    st.download_button("⬇️ Download Excel", data=excel_data, file_name="registrations.xlsx")

# Notices Tab
with tabs[3]:
    st.header("Notices & Announcements")
    n = load_csv(NOTICE_FILE, ["Timestamp","Title","Message","PostedBy"])
    if n.empty:
        st.info("No notices yet")
    else:
        for _, row in n.iterrows():
            ts = pd.to_datetime(row["Timestamp"]).strftime("%d-%b-%Y %I:%M %p") if pd.notnull(row["Timestamp"]) else ""
            st.write(f"### {row['Title']}\n{row['Message']}\n*Posted by {row['PostedBy']} on {ts}*")

# Admin Tab
with tabs[4]:
    st.header("Admin Panel")
    pw = st.text_input("Admin Password", type="password")
    if st.button("Login as Admin"):
        if pw == ADMIN_PASSWORD:
            st.success("✅ Admin Logged In")
            t = st.text_input("Notice Title")
            m = st.text_area("Notice Message")
            b = st.text_input("Posted By", value="Admin")
            if st.button("Post Notice"):
                n = load_csv(NOTICE_FILE, ["Timestamp","Title","Message","PostedBy"])
                n.loc[len(n)] = [datetime.now(), t, m, b]
                n.to_csv(NOTICE_FILE, index=False)
                st.success("✅ Notice Posted!")
        else:
            st.error("❌ Wrong Password")
