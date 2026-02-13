import io
import json
import base64
import time
import pandas as pd
import streamlit as st
import requests
import altair as alt

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="GitHub Excel Approval System",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management System</h1>", unsafe_allow_html=True)
st.write("---")

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
if "df" not in st.session_state:
    st.session_state.df = None

if "edited_df" not in st.session_state:
    st.session_state.edited_df = None

# ---------------------------------------------------
# LOAD SECRETS
# ---------------------------------------------------
required_secrets = [
    "GITHUB_TOKEN",
    "GITHUB_REPO",
    "GITHUB_FILE_PATH",
    "FILE_ID",
    "SERVICE_ACCOUNT_JSON"
]

for key in required_secrets:
    if key not in st.secrets:
        st.error(f"Missing secret: {key}")
        st.stop()

GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO = st.secrets["GITHUB_REPO"]
GITHUB_FILE_PATH = st.secrets["GITHUB_FILE_PATH"]
FILE_ID = st.secrets["FILE_ID"]
SERVICE_ACCOUNT_JSON = st.secrets["SERVICE_ACCOUNT_JSON"]

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# ---------------------------------------------------
# GOOGLE DRIVE FUNCTIONS
# ---------------------------------------------------
def get_drive_service():
    creds = Credentials.from_service_account_info(
        json.loads(SERVICE_ACCOUNT_JSON),
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=creds)

def download_excel_from_drive():
    service = get_drive_service()
    request = service.files().get_media(fileId=FILE_ID)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    fh.seek(0)
    return pd.read_excel(fh, engine="openpyxl")

def upload_excel_to_drive(df):
    service = get_drive_service()
    out = io.BytesIO()
    df.to_excel(out, index=False, engine="openpyxl")
    out.seek(0)
    media = MediaIoBaseUpload(
        out,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        resumable=True
    )
    service.files().update(fileId=FILE_ID, media_body=media).execute()

# ---------------------------------------------------
# GITHUB FUNCTIONS
# ---------------------------------------------------
@st.cache_data(ttl=300)
def download_excel_from_github():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    r = requests.get(url, headers=HEADERS)
    r.raise_for_status()
    content = r.json()["content"]
    file_bytes = base64.b64decode(content)
    return pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")

def upload_excel_to_github(df):
    out = io.BytesIO()
    df.to_excel(out, index=False, engine="openpyxl")
    out.seek(0)
    content_b64 = base64.b64encode(out.read()).decode()
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    sha = requests.get(url, headers=HEADERS).json()["sha"]
    payload = {
        "message": "Updated via Streamlit Approval System",
        "content": content_b64,
        "sha": sha
    }
    r = requests.put(url, headers=HEADERS, data=json.dumps(payload))
    r.raise_for_status()

# ---------------------------------------------------
# INITIAL LOAD
# ---------------------------------------------------
if st.session_state.df is None:
    with st.spinner("🔄 Syncing Excel from Drive → GitHub..."):
        drive_df = download_excel_from_drive()
        upload_excel_to_github(drive_df)
        df = download_excel_from_github()

        for col in ["APPROVAL_1", "APPROVAL_2"]:
            if col not in df.columns:
                df[col] = ""

        st.session_state.df = df.reset_index(drop=True)

df = st.session_state.df.copy()

# ---------------------------------------------------
# FILTER UI
# ---------------------------------------------------
df_ui = df[
    ~(
        (df["APPROVAL_1"].astype(str).str.upper() == "REJECTED") &
        (df["APPROVAL_2"].astype(str).str.upper() == "REJECTED")
    )
].copy()

# ---------------------------------------------------
# DISPLAY COLUMNS
# ---------------------------------------------------
DISPLAY_COLUMNS = [
    "STATUS_MATCHED_ESTIMATION", "GST %", "TDS %",
    "GST (Yes/No)", "TDS (Yes/No)",
    "BENEFICIARY PAN", "BENEFICIARY GSTIN",
    "BENEFICIARY ACCOUNT NO", "FINAL AMOUNT",
    "PROJECT_NAME", "CATEGORY",
    "FIXED_AMOUNT", "BALANCE_AMOUNT",
    "ADJUSTMENT_AMOUNT", "BASIC_AMOUNT",
    "APPROVAL_1", "APPROVAL_2",
    "BENEFICIARY NAME", "NARRATION",
    "Remarks", "DATE","COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"
]

df_ui = df_ui[DISPLAY_COLUMNS]

# ---------------------------------------------------
# AUTO ADJUSTMENT
# ---------------------------------------------------
df_ui["BASIC_AMOUNT"] = pd.to_numeric(df_ui["BASIC_AMOUNT"], errors="coerce").fillna(0)
df_ui["ADJUSTMENT_AMOUNT"] = pd.to_numeric(df_ui["ADJUSTMENT_AMOUNT"], errors="coerce").fillna(0)

mask = (
    (df_ui["STATUS_MATCHED_ESTIMATION"].fillna("").str.upper() == "ESTIMATION NOT MATCHED") &
    (df_ui["BASIC_AMOUNT"] != 0) & 
    (df_ui["ADJUSTMENT_AMOUNT"] == 0)
)

df_ui.loc[mask, "ADJUSTMENT_AMOUNT"] = df_ui.loc[mask, "BASIC_AMOUNT"]

if st.session_state.edited_df is None:
    st.session_state.edited_df = df_ui.copy()

# ---------------------------------------------------
# ADD STATUS CHECKBOX COLUMNS
# ---------------------------------------------------
STATUS_COLUMNS = ["ACCEPTED", "PAID", "HOLD", "REJECTED"]

for col in STATUS_COLUMNS:
    if col not in st.session_state.edited_df.columns:
        st.session_state.edited_df[col] = False
st.session_state.edited_df[STATUS_COLUMNS] = st.session_state.edited_df[STATUS_COLUMNS].astype(bool)

# ---------------------------------------------------
# REORDER → Place checkboxes after BASIC_AMOUNT
# ---------------------------------------------------
cols = list(st.session_state.edited_df.columns)
if "BASIC_AMOUNT" in cols:
    basic_index = cols.index("BASIC_AMOUNT")
    for s in STATUS_COLUMNS:
        if s in cols:
            cols.remove(s)
    for i, s in enumerate(STATUS_COLUMNS):
        cols.insert(basic_index + 1 + i, s)
    st.session_state.edited_df = st.session_state.edited_df[cols]

# ---------------------------------------------------
# RADIO BUTTONS → Select All for Status
# ---------------------------------------------------
st.subheader("📂 Pending Approvals")
st.markdown("### 🔘 Select Overall Status for All Rows")

selected_status = st.radio(
    "Select one status for all rows:",
    options=["None"] + STATUS_COLUMNS,  # "None" keeps all as-is
    index=0,
    horizontal=True
)

if selected_status != "None":
    # Reset all status columns first
    st.session_state.edited_df[STATUS_COLUMNS] = False
    # Set the selected status column to True
    st.session_state.edited_df[selected_status] = True

# ---------------------------------------------------
# EDITOR
# ---------------------------------------------------
with st.form("approval_form"):
    edited_df = st.data_editor(
        st.session_state.edited_df,
        key="editor",
        hide_index=True,
        use_container_width=True,
        column_config={
            "ACCEPTED": st.column_config.CheckboxColumn("ACCEPTED"),
            "PAID": st.column_config.CheckboxColumn("PAID"),
            "HOLD": st.column_config.CheckboxColumn("HOLD"),
            "REJECTED": st.column_config.CheckboxColumn("REJECTED"),
            "BASIC_AMOUNT": st.column_config.NumberColumn("BASIC_AMOUNT", format="%.2f"),
        }
    )

    submit = st.form_submit_button("💾 Save")

# ---------------------------------------------------
# SAVE LOGIC
# ---------------------------------------------------
if submit:
    try:
        edited_df = edited_df.copy()
        edited_df.index = df_ui.index

        for idx, row in edited_df.iterrows():
            selected = [s for s in STATUS_COLUMNS if row[s]]
            if len(selected) > 1:
                last = selected[-1]
                for s in STATUS_COLUMNS:
                    edited_df.at[idx, s] = (s == last)
            final_status = ""
            for s in STATUS_COLUMNS:
                if edited_df.at[idx, s]:
                    final_status = s
            edited_df.at[idx, "APPROVAL_1"] = final_status
            edited_df.at[idx, "APPROVAL_2"] = final_status

        cols = ["APPROVAL_1","APPROVAL_2","BASIC_AMOUNT"] + STATUS_COLUMNS
        df.loc[df_ui.index, cols] = edited_df[cols].values

        upload_excel_to_github(df)
        time.sleep(3)
        upload_excel_to_drive(df)

        st.cache_data.clear()
        st.session_state.df = df.copy()

        st.success("✅ Saved Successfully")

    except Exception as e:
        st.error(f"❌ Save failed: {e}")

# ---------------------------------------------------
# PROJECT SUMMARY
# ---------------------------------------------------
st.write("---")
st.subheader("💼 Project-wise Highest Expense")

expense_df = df.copy()
expense_df["FINAL AMOUNT"] = pd.to_numeric(expense_df["FINAL AMOUNT"], errors="coerce").fillna(0)
expense_df["PROJECT_NAME"] = expense_df["PROJECT_NAME"].astype(str).str.upper().str.strip()

grp = expense_df.groupby(["PROJECT_NAME", "CATEGORY"])["FINAL AMOUNT"].sum().reset_index()
top_expenses = grp.sort_values("FINAL AMOUNT", ascending=False).groupby("PROJECT_NAME").head(1)

st.dataframe(top_expenses, use_container_width=True)

chart = alt.Chart(top_expenses).mark_bar().encode(
    x="PROJECT_NAME:N",
    y="FINAL AMOUNT:Q",
    color="CATEGORY:N",
    tooltip=["PROJECT_NAME", "CATEGORY", "FINAL AMOUNT"]
).properties(height=400)

st.altair_chart(chart, use_container_width=True)

st.info("ℹ GitHub is the working copy. Google Drive is the final synced file.")
