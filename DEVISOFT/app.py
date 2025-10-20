import streamlit as st
import pandas as pd
from datetime import datetime
import random

# --------------------
# CONFIGURATION
# --------------------
ADMIN_PASSWORD = "sgs2025"
REG_FILE = "registrations.csv"
NOTICE_FILE = "notices.csv"
ALLOWED_FILE = "allowed_users.csv"

st.set_page_config(page_title="SGS Annual Function", layout="wide")

# --------------------
# FUNCTION TO LOAD CSV
# --------------------
def load_csv(file, columns):
    try:
        return pd.read_csv(file)
    except:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file, index=False)
        return df

# Load data files
reg_df = load_csv(REG_FILE, ["Timestamp","Name","Class","Section","Item","Contact","Address","Bus","Status"])
notice_df = load_csv(NOTICE_FILE, ["Timestamp","Title","Message","PostedBy"])
allowed_df = load_csv(ALLOWED_FILE, ["mobile_number","student_name"])

# ✅ Clean / normalize allowed mobile numbers
allowed_df["mobile_number"] = (
    allowed_df["mobile_number"]
    .astype(str)
    .str.replace(" ", "")
    .str.replace("+91", "")
    .str.strip()
    .str[-10:]    # Always keep last 10 digits
)

# (TEMPORARY) Display contents for checking — remove later
st.info("📂 Allowed Users Loaded Successfully:")
st.dataframe(allowed_df)

# --------------------
# SESSION INITIALIZATION
# --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --------------------
# LOGIN FUNCTION
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
            st.sidebar.success("OTP (Test Mode): " + otp)
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
# MAIN APP TABS
# --------------------
tabs = st.tabs(["Home", "Registration", "List", "Notices", "Admin"])

with tabs[0]:
    st.title("St. Gregorios H.S. School")
    st.subheader("Annual Function App")

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

with tabs[2]:
    st.header("Registered Students")
    st.dataframe(pd.read_csv(REG_FILE))

with tabs[3]:
    st.header("Notices")
    df = pd.read_csv(NOTICE_FILE)
    if df.empty:
        st.info("No notices yet")
    else:
        for _, r in df.iterrows():
            st.write(f"""
### {r['Title']}
{r['Message']}
*Posted by {r['PostedBy']}*
""")

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
