import streamlit as st
import pandas as pd
from datetime import datetime
import random, os

# --------------------
# CONFIGURATION
# --------------------
ADMIN_PASSWORD = "sgs2025"
REG_FILE = "registrations.csv"
NOTICE_FILE = "notices.csv"
ALLOWED_FILE = "allowed_users.csv"   # must be in same folder as app.py

st.set_page_config(page_title="SGS Annual Function", layout="wide")

# --------------------
# LOAD CSV (REGISTRATION & NOTICES)
# --------------------
def load_csv(file, columns):
    try:
        return pd.read_csv(file)
    except:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file, index=False)
        return df

reg_df = load_csv(REG_FILE, ["Timestamp","Name","Class","Section","Item","Contact","Address","Bus","Status"])
notice_df = load_csv(NOTICE_FILE, ["Timestamp","Title","Message","PostedBy"])

# --------------------
# LOAD allowed_users.csv USING ABSOLUTE PATH
# --------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))    
ALLOWED_FILE_PATH = os.path.join(BASE_DIR, ALLOWED_FILE)

allowed_df = pd.read_csv(ALLOWED_FILE_PATH)

# ✅ Normalize phone numbers in CSV
allowed_df["mobile_number"] = (
    allowed_df["mobile_number"]
    .astype(str)
    .str.replace(" ", "")
    .str.replace("+91", "")
    .str.strip()
    .str[-10:]
)

# 🔍 Debug: show allowed users (remove later if you want)
st.info("✅ Allowed Users Loaded (from file):")
st.write(ALLOWED_FILE_PATH)
st.dataframe(allowed_df)

# --------------------
# SESSION INITIALIZATION
# --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --------------------
# LOGIN FUNCTION (OTP TEST MODE)
# --------------------
def login():
    st.sidebar.title("Login")
    mobile = st.sidebar.text_input("Enter 10-digit Mobile").strip()

    # Ensure only last 10 digits
    if len(mobile) > 10:
        mobile = mobile[-10:]

    if st.sidebar.button("Send OTP"):
        if mobile in allowed_df["mobile_number"].values:
            otp = str(random.randint(100000, 999999))
            st.session_state.otp = otp
            st.session_state.mobile = mobile
            # ✅ Hide OTP - do not display
            st.sidebar.success("OTP sent to your mobile")
        else:
            st.sidebar.error("❌ This number is not registered")

    if "otp" in st.session_state:
        code = st.sidebar.text_input("Enter OTP")
        if st.sidebar.button("Verify"):
            if code == st.session_state.otp:
                st.session_state.logged_in = True
                st.sidebar.success("✅ Login successful")
            else:
                st.sidebar.error("❌ Wrong OTP")

# --------------------
# RUN LOGIN
# --------------------
login()
if not st.session_state.logged_in:
    st.stop()

# --------------------
# MAIN TABS
# --------------------
tabs = st.tabs(["Home", "Registration", "List", "Notices", "Admin"])

# ✅ HOME TAB — mascot appears here
with tabs[0]:
    if os.path.exists(os.path.join(BASE_DIR, "mascot.png")):
        st.image("mascot.png", width=200)
    elif os.path.exists(os.path.join(BASE_DIR, "logo.png")):
        st.image("logo.png", width=200)

    st.title("St. Gregorios H.S. School")
    st.subheader("Annual Function App")

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

        if st.form_submit_button("Submit"):
            df = pd.read_csv(REG_FILE)
            df.loc[len(df)] = [datetime.now(), name, clas, sec, item, contact, address, bus, "Pending"]
            df.to_csv(REG_FILE, index=False)
            st.success("✅ Registered Successfully")

# LIST TAB
with tabs[2]:
    st.header("Registered Students")
    st.dataframe(pd.read_csv(REG_FILE))

# NOTICES TAB
with tabs[3]:
    st.header("Notices")
    df = pd.read_csv(NOTICE_FILE)
    if df.empty:
        st.warning("No notices yet")
    else:
        for _, r in df.iterrows():
            st.write(f"""
### {r['Title']}
{r['Message']}
*Posted by {r['PostedBy']}*
""")

# ADMIN TAB
with tabs[4]:
    st.header("Admin Section")
    pw = st.text_input("Admin Password", type="password")
    if st.button("Login as Admin"):
        if pw == ADMIN_PASSWORD:
            st.success("✅ Admin Logged In")
            title = st.text_input("Notice Title")
            msg = st.text_area("Message")
            by = st.text_input("Posted By", value="Admin")

            if st.button("Post Notice"):
                df = pd.read_csv(NOTICE_FILE)
                df.loc[len(df)] = [datetime.now(), title, msg, by]
                df.to_csv(NOTICE_FILE, index=False)
                st.success("✅ Notice Posted")
        else:
            st.error("❌ Incorrect password")
