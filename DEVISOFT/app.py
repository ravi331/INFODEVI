import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random, os, time
from io import BytesIO

# -------------------------------------------------
# Streamlit Page Settings
# -------------------------------------------------
st.set_page_config(page_title="SGS Annual Function", layout="wide", page_icon="🎉")

# -------------------------------------------------
# Constants & File Names
# -------------------------------------------------
ADMIN_PASSWORD = "sgs2025"
EVENT_DATETIME = datetime(2025, 12, 20, 0, 0, 0)

# CSV Files
REG_FILE = "registrations.csv"
NOTICE_FILE = "notices.csv"
ALLOWED_FILE = "allowed_users.csv"

# Directory Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -------------------------------------------------
# Helper Functions
# -------------------------------------------------
def safe_path(filename):
    return os.path.join(BASE_DIR, filename)

def load_csv(file, columns):
    try:
        return pd.read_csv(file)
    except:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file, index=False)
        return df

def normalize_number(series):
    """Ensure numbers are only last 10 digits"""
    return (series.astype(str)
                 .str.replace(" ", "", regex=False)
                 .str.replace("+91", "", regex=False)
                 .str.strip()
                 .str[-10:])

def to_excel_bytes(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return output.read()

def safe_show_image(filename, width=None):
    path = safe_path(filename)
    if os.path.exists(path):
        st.image(path, width=width)

def time_left():
    diff = EVENT_DATETIME - datetime.now()
    if diff.total_seconds() < 0:
        return "Today is the Annual Function! 🎉"
    days = diff.days
    hours, rem = divmod(diff.seconds, 3600)
    mins, secs = divmod(rem, 60)
    return f"{days} days, {hours} hrs, {mins} mins, {secs} secs"

# -------------------------------------------------
# Load Data
# -------------------------------------------------
reg_df = load_csv(REG_FILE, ["Timestamp","Name","Class","Section","Item","Contact","Address","Bus","Status"])
notice_df = load_csv(NOTICE_FILE, ["Timestamp","Title","Message","PostedBy"])

allowed_df = load_csv(safe_path(ALLOWED_FILE), ["mobile_number","name"])
allowed_df["mobile_number"] = normalize_number(allowed_df["mobile_number"])

# -------------------------------------------------
# Session State
# -------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "mobile" not in st.session_state:
    st.session_state.mobile = ""
if "otp" not in st.session_state:
    st.session_state.otp = None
if "welcomed" not in st.session_state:
    st.session_state.welcomed = False

# -------------------------------------------------
# Sidebar Login System
# -------------------------------------------------
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
                    st.sidebar.success("✅ Login Successful")
                else:
                    st.sidebar.error("❌ Incorrect OTP")

    else:
        st.sidebar.success(f"Logged in as: {st.session_state.mobile}")
        if st.sidebar.button("Logout"):
            for key in ["logged_in", "otp", "mobile", "welcomed"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

login_sidebar()
if not st.session_state.logged_in:
    st.stop()

# -------------------------------------------------
# Welcome Screen (shown only once)
# -------------------------------------------------
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

# -------------------------------------------------
# Main Interface
# -------------------------------------------------
st.title("St. Gregorios H.S. School")
tabs = st.tabs(["Home", "Registration", "List", "Notices", "Admin"])

# -------------------------------------------------
# Home Tab
# -------------------------------------------------
with tabs[0]:
    left, right = st.columns([1,3])
    with left:
        safe_show_image("mascot.png", width=200)
    with right:
        safe_show_image("logo.png", width=350)
        st.subheader("45th Annual Day – Talent Meets Opportunity")

    # Show Latest Notice
    if not notice_df.empty:
        recent = notice_df.iloc[-1]
        st.info(f"📢 **{recent['Title']}**\n\n{recent['Message']}")

    # Countdown
    st.write("⏳ **Countdown to Annual Function (20-Dec-2025):**")
    st.success(time_left())

# -------------------------------------------------
# Registration Tab
# -------------------------------------------------
with tabs[1]:
    st.header("Register Participation")
    with st.form("reg_form"):
        name = st.text_input("Name")
        clas = st.text_input("Class")
        sec = st.text_input("Section")
        item = st.text_input("Event")
        address = st.text_area("Address")
        bus = st.radio("Using School Bus?", ["Yes","No"])
        contact = st.text_input("Contact", value=st.session_state.mobile)

        if st.form_submit_button("Submit"):
            r = load_csv(REG_FILE, ["Timestamp","Name","Class","Section","Item","Contact","Address","Bus","Status"])
            r.loc[len(r)] = [datetime.now(), name, clas, sec, item, contact, address, bus, "Pending"]
            r.to_csv(REG_FILE, index=False)
            st.success("✅ Registration Submitted")

# -------------------------------------------------
# List Tab
# -------------------------------------------------
with tabs[2]:
    st.header("Registered Students")
    df = load_csv(REG_FILE, ["Timestamp","Name","Class","Section","Item","Contact","Address","Bus","Status"])
    st.dataframe(df)

    excel_data = to_excel_bytes(df)
    st.download_button("⬇ Download as Excel", data=excel_data, file_name="registrations.xlsx")

# -------------------------------------------------
# Notices Tab
# -------------------------------------------------
with tabs[3]:
    st.header("Notices & Announcements")
    n = load_csv(NOTICE_FILE, ["Timestamp","Title","Message","PostedBy"])
    if n.empty:
        st.info("No notices yet")
    else:
        for i, row in n.iterrows():
            st.write(f"### {row['Title']}\n{row['Message']}\n*By {row['PostedBy']}*")

# -------------------------------------------------
# Admin Tab
# -------------------------------------------------
with tabs[4]:
    st.header("Admin Panel")
    admin_pw = st.text_input("Enter Admin Password", type="password")
    if st.button("Login as Admin"):
        if admin_pw == ADMIN_PASSWORD:
            st.success("✅ Admin Verified")
            title = st.text_input("Notice Title")
            msg = st.text_area("Notice Message")
            by = st.text_input("Posted By", value="Admin")

            if st.button("Post Notice"):
                n = load_csv(NOTICE_FILE, ["Timestamp","Title","Message","PostedBy"])
                n.loc[len(n)] = [datetime.now(), title, msg, by]
                n.to_csv(NOTICE_FILE, index=False)
                st.success("✅ Notice Posted")
        else:
            st.error("❌ Wrong Password")
