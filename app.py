# import io
# import json
# import base64
# import time
# import pandas as pd
# import streamlit as st
# import requests
# import altair as alt

# from google.oauth2.service_account import Credentials
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

# # ---------------------------------------------------
# # PAGE CONFIG
# # ---------------------------------------------------
# st.set_page_config(
#     page_title="GitHub Excel Approval System",
#     page_icon="📝",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management System.</h1>", unsafe_allow_html=True)
# st.write("---")

# # ---------------------------------------------------
# # SESSION STATE
# # ---------------------------------------------------
# if "df" not in st.session_state:
#     st.session_state.df = None

# if "edited_df" not in st.session_state:
#     st.session_state.edited_df = None

# # ---------------------------------------------------
# # LOAD SECRETS
# # ---------------------------------------------------
# required_secrets = [
#     "GITHUB_TOKEN",
#     "GITHUB_REPO",
#     "GITHUB_FILE_PATH",
#     "FILE_ID",
#     "SERVICE_ACCOUNT_JSON"
# ]

# for key in required_secrets:
#     if key not in st.secrets:
#         st.error(f"Missing secret: {key}")
#         st.stop()

# GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
# GITHUB_REPO = st.secrets["GITHUB_REPO"]
# GITHUB_FILE_PATH = st.secrets["GITHUB_FILE_PATH"]
# FILE_ID = st.secrets["FILE_ID"]
# SERVICE_ACCOUNT_JSON = st.secrets["SERVICE_ACCOUNT_JSON"]

# HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# # ---------------------------------------------------
# # GOOGLE DRIVE FUNCTIONS
# # ---------------------------------------------------
# def get_drive_service():
#     creds = Credentials.from_service_account_info(
#         json.loads(SERVICE_ACCOUNT_JSON),
#         scopes=["https://www.googleapis.com/auth/drive"]
#     )
#     return build("drive", "v3", credentials=creds)

# def download_excel_from_drive():
#     service = get_drive_service()
#     request = service.files().get_media(fileId=FILE_ID)
#     fh = io.BytesIO()
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while not done:
#         _, done = downloader.next_chunk()
#     fh.seek(0)
#     return pd.read_excel(fh, engine="openpyxl")

# def upload_excel_to_drive(df):
#     service = get_drive_service()
#     out = io.BytesIO()
#     df.to_excel(out, index=False, engine="openpyxl")
#     out.seek(0)
#     media = MediaIoBaseUpload(
#         out,
#         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         resumable=True
#     )
#     service.files().update(fileId=FILE_ID, media_body=media).execute()

# # ---------------------------------------------------
# # GITHUB FUNCTIONS
# # ---------------------------------------------------
# @st.cache_data(ttl=300)
# def download_excel_from_github():
#     url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
#     r = requests.get(url, headers=HEADERS)
#     r.raise_for_status()
#     content = r.json()["content"]
#     file_bytes = base64.b64decode(content)
#     return pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")

# def upload_excel_to_github(df):
#     out = io.BytesIO()
#     df.to_excel(out, index=False, engine="openpyxl")
#     out.seek(0)
#     content_b64 = base64.b64encode(out.read()).decode()
#     url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
#     sha = requests.get(url, headers=HEADERS).json()["sha"]
#     payload = {
#         "message": "Updated via Streamlit Approval System",
#         "content": content_b64,
#         "sha": sha
#     }
#     r = requests.put(url, headers=HEADERS, data=json.dumps(payload))
#     r.raise_for_status()

# # ---------------------------------------------------
# # INITIAL LOAD
# # ---------------------------------------------------
# if st.session_state.df is None:
#     with st.spinner("🔄 Syncing Excel from Drive → GitHub..."):
#         drive_df = download_excel_from_drive()
#         upload_excel_to_github(drive_df)
#         df = download_excel_from_github()

#         for col in ["APPROVAL_1", "APPROVAL_2"]:
#             if col not in df.columns:
#                 df[col] = ""

#         st.session_state.df = df.reset_index(drop=True)

# df = st.session_state.df.copy()

# # ---------------------------------------------------
# # FILTER OUT FULLY REJECTED
# # ---------------------------------------------------
# df_ui = df[
#     ~(
#         (df["APPROVAL_1"].astype(str).str.upper() == "REJECTED") &
#         (df["APPROVAL_2"].astype(str).str.upper() == "REJECTED")
#     )
# ].copy()

# # ---------------------------------------------------
# # DISPLAY COLUMNS (WITHOUT APPROVAL_1 & APPROVAL_2)
# # ---------------------------------------------------
# DISPLAY_COLUMNS = [
#     "STATUS_MATCHED_ESTIMATION", "GST %", "TDS %",
#     "GST (Yes/No)", "TDS (Yes/No)",
#     "BENEFICIARY PAN", "BENEFICIARY GSTIN",
#     "BENEFICIARY ACCOUNT NO", "FINAL AMOUNT",
#     "PROJECT_NAME", "CATEGORY",
#     "FIXED_AMOUNT", "BALANCE_AMOUNT",
#     "ADJUSTMENT_AMOUNT", "BASIC_AMOUNT",
#     "BENEFICIARY NAME", "NARRATION",
#     "Remarks", "DATE","COST_CENTER",
#     "LEDGER_NAME","LEDGER_UNDER","TO","BY"
# ]

# df_ui = df_ui[DISPLAY_COLUMNS]

# # ---------------------------------------------------
# # ADD UI STATUS CHECKBOXES (UI ONLY)
# # ---------------------------------------------------
# STATUS_COLUMNS = ["ACCEPTED", "PAID", "HOLD", "REJECTED"]

# for col in STATUS_COLUMNS:
#     df_ui[col] = False

# # Move checkboxes after BASIC_AMOUNT
# cols = list(df_ui.columns)
# basic_index = cols.index("BASIC_AMOUNT")
# for s in STATUS_COLUMNS:
#     cols.remove(s)
# for i, s in enumerate(STATUS_COLUMNS):
#     cols.insert(basic_index + 1 + i, s)

# df_ui = df_ui[cols]

# # ---------------------------------------------------
# # RADIO SELECT ALL
# # ---------------------------------------------------
# st.subheader("📂 Pending Approvals")

# selected_status = st.radio(
#     "Select one status for all rows:",
#     options=["None"] + STATUS_COLUMNS,
#     horizontal=True
# )

# if selected_status != "None":
#     df_ui[STATUS_COLUMNS] = False
#     df_ui[selected_status] = True

# # ---------------------------------------------------
# # DATA EDITOR
# # ---------------------------------------------------
# with st.form("approval_form"):
#     edited_df = st.data_editor(
#         df_ui,
#         hide_index=True,
#         use_container_width=True,
#         column_config={
#             "ACCEPTED": st.column_config.CheckboxColumn("ACCEPTED"),
#             "PAID": st.column_config.CheckboxColumn("PAID"),
#             "HOLD": st.column_config.CheckboxColumn("HOLD"),
#             "REJECTED": st.column_config.CheckboxColumn("REJECTED"),
#             "BASIC_AMOUNT": st.column_config.NumberColumn("BASIC_AMOUNT", format="%.2f"),
#         }
#     )

#     submit = st.form_submit_button("💾 Save")

# # ---------------------------------------------------
# # SAVE LOGIC (ONLY UPDATE APPROVAL_1 & APPROVAL_2)
# # ---------------------------------------------------
# # if submit:
# #     try:
# #         edited_df.index = df_ui.index

# #         for idx, row in edited_df.iterrows():
# #             selected = [s for s in STATUS_COLUMNS if row[s]]
# #             final_status = selected[-1] if selected else ""
# #             df.at[idx, "APPROVAL_1"] = final_status
# #             df.at[idx, "APPROVAL_2"] = final_status
# #             df.at[idx, "BASIC_AMOUNT"] = row["BASIC_AMOUNT"]

# #         upload_excel_to_github(df)
# #         time.sleep(2)
# #         upload_excel_to_drive(df)

# #         st.session_state.df = df.copy()
# #         st.cache_data.clear()

# #         st.success("✅ Saved Successfully")

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")

# # ---------------------------------------------------
# # SAVE LOGIC (ONLY UPDATE APPROVAL_1 & APPROVAL_2)
# # ---------------------------------------------------
# if submit:
#     try:
#         edited_df.index = df_ui.index

#         for idx, row in edited_df.iterrows():
#             selected = [s for s in STATUS_COLUMNS if row[s]]
#             final_status = selected[-1] if selected else ""

#             df.at[idx, "APPROVAL_1"] = final_status
#             df.at[idx, "APPROVAL_2"] = final_status
#             df.at[idx, "BASIC_AMOUNT"] = row["BASIC_AMOUNT"]

#         # 🔥 REMOVE UI-ONLY COLUMNS BEFORE SAVE
#         df_clean = df.drop(columns=STATUS_COLUMNS, errors="ignore")

#         upload_excel_to_github(df_clean)
#         time.sleep(2)
#         upload_excel_to_drive(df_clean)

#         st.session_state.df = df_clean.copy()
#         st.cache_data.clear()

#         st.success("✅ Saved Successfully")

#     except Exception as e:
#         st.error(f"❌ Save failed: {e}")


# # ---------------------------------------------------
# # PROJECT SUMMARY
# # ---------------------------------------------------
# st.write("---")
# st.subheader("💼 Project-wise Highest Expense")

# expense_df = df.copy()
# expense_df["FINAL AMOUNT"] = pd.to_numeric(expense_df["FINAL AMOUNT"], errors="coerce").fillna(0)
# expense_df["PROJECT_NAME"] = expense_df["PROJECT_NAME"].astype(str).str.upper().str.strip()

# grp = expense_df.groupby(["PROJECT_NAME", "CATEGORY"])["FINAL AMOUNT"].sum().reset_index()
# top_expenses = grp.sort_values("FINAL AMOUNT", ascending=False).groupby("PROJECT_NAME").head(1)

# st.dataframe(top_expenses, use_container_width=True)

# chart = alt.Chart(top_expenses).mark_bar().encode(
#     x="PROJECT_NAME:N",
#     y="FINAL AMOUNT:Q",
#     color="CATEGORY:N",
#     tooltip=["PROJECT_NAME", "CATEGORY", "FINAL AMOUNT"]
# ).properties(height=400)

# st.altair_chart(chart, use_container_width=True)

# st.info("ℹ GitHub is the working copy. Google Drive is the final synced file.")


# import io
# import json
# import base64
# import time
# import pandas as pd
# import streamlit as st
# import requests
# import altair as alt
# import calendar


# from google.oauth2.service_account import Credentials
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

# # ---------------------------------------------------
# # PAGE CONFIG
# # ---------------------------------------------------
# st.set_page_config(
#     page_title="GitHub Excel Approval System",
#     page_icon="📝",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management System.</h1>", unsafe_allow_html=True)
# st.write("---")

# # ---------------------------------------------------
# # SESSION STATE
# # ---------------------------------------------------
# if "df" not in st.session_state:
#     st.session_state.df = None

# # ---------------------------------------------------
# # LOAD SECRETS
# # ---------------------------------------------------
# required_secrets = [
#     "GITHUB_TOKEN",
#     "GITHUB_REPO",
#     "GITHUB_FILE_PATH",
#     "FILE_ID",
#     "SHEET_FILE_ID",
#     "SERVICE_ACCOUNT_JSON"
# ]

# for key in required_secrets:
#     if key not in st.secrets:
#         st.error(f"Missing secret: {key}")
#         st.stop()

# GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
# GITHUB_REPO = st.secrets["GITHUB_REPO"]
# GITHUB_FILE_PATH = st.secrets["GITHUB_FILE_PATH"]
# FILE_ID = st.secrets["FILE_ID"]
# SHEET_FILE_ID = st.secrets["SHEET_FILE_ID"]     # Monthly Summary Sheet
# SERVICE_ACCOUNT_JSON = st.secrets["SERVICE_ACCOUNT_JSON"]

# HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# # ---------------------------------------------------
# # GOOGLE DRIVE FUNCTIONS
# # ---------------------------------------------------
# def get_drive_service():
#     creds = Credentials.from_service_account_info(
#         json.loads(SERVICE_ACCOUNT_JSON),
#         scopes=["https://www.googleapis.com/auth/drive"]
#     )
#     return build("drive", "v3", credentials=creds)

# def download_excel_from_drive():
#     service = get_drive_service()
#     request = service.files().get_media(fileId=FILE_ID)
#     fh = io.BytesIO()
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while not done:
#         _, done = downloader.next_chunk()
#     fh.seek(0)
#     return pd.read_excel(fh, engine="openpyxl")

# def upload_excel_to_drive(df):
#     service = get_drive_service()
#     out = io.BytesIO()
#     df.to_excel(out, index=False, engine="openpyxl")
#     out.seek(0)
#     media = MediaIoBaseUpload(
#         out,
#         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         resumable=True
#     )
#     service.files().update(fileId=FILE_ID, media_body=media).execute()



# # ---------------------------------------------------
# # DOWNLOAD MONTHLY GOOGLE SHEET
# # ---------------------------------------------------
# def download_monthly_sheet():
#     service = get_drive_service()

#     # Export Google Sheet as Excel
#     request = service.files().export_media(
#         fileId=SHEET_FILE_ID,
#         mimeType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )

#     fh = io.BytesIO()
#     downloader = MediaIoBaseDownload(fh, request)

#     done = False
#     while not done:
#         _, done = downloader.next_chunk()

#     fh.seek(0)
#     return pd.read_excel(fh, engine="openpyxl")


# # ---------------------------------------------------
# # GITHUB FUNCTIONS
# # ---------------------------------------------------
# @st.cache_data(ttl=300)
# def download_excel_from_github():
#     url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
#     r = requests.get(url, headers=HEADERS)
#     r.raise_for_status()
#     content = r.json()["content"]
#     file_bytes = base64.b64decode(content)
#     return pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")

# def upload_excel_to_github(df):
#     out = io.BytesIO()
#     df.to_excel(out, index=False, engine="openpyxl")
#     out.seek(0)
#     content_b64 = base64.b64encode(out.read()).decode()
#     url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
#     sha = requests.get(url, headers=HEADERS).json()["sha"]
#     payload = {
#         "message": "Updated via Streamlit Approval System",
#         "content": content_b64,
#         "sha": sha
#     }
#     r = requests.put(url, headers=HEADERS, data=json.dumps(payload))
#     r.raise_for_status()

# # ---------------------------------------------------
# # INITIAL LOAD
# # ---------------------------------------------------
# if st.session_state.df is None:
#     with st.spinner("🔄 Syncing Excel from Drive → GitHub..."):
#         drive_df = download_excel_from_drive()
#         upload_excel_to_github(drive_df)
#         df = download_excel_from_github()

#         for col in ["APPROVAL_1", "APPROVAL_2"]:
#             if col not in df.columns:
#                 df[col] = ""

#         st.session_state.df = df.reset_index(drop=True)

# df = st.session_state.df.copy()

# # ---------------------------------------------------
# # FILTER OUT FULLY REJECTED
# # ---------------------------------------------------
# df_ui = df[
#     ~(
#         (df["APPROVAL_1"].astype(str).str.upper() == "REJECTED") &
#         (df["APPROVAL_2"].astype(str).str.upper() == "REJECTED")
#     )
# ].copy()

# # ---------------------------------------------------
# # DISPLAY COLUMNS
# # ---------------------------------------------------
# DISPLAY_COLUMNS = [
#     "STATUS_MATCHED_ESTIMATION", "GST %", "TDS %",
#     "GST (Yes/No)", "TDS (Yes/No)",
#     "BENEFICIARY PAN", "BENEFICIARY GSTIN",
#     "BENEFICIARY ACCOUNT NO", "FINAL AMOUNT",
#     "PROJECT_NAME", "CATEGORY",
#     "FIXED_AMOUNT", "BALANCE_AMOUNT",
#     "ADJUSTMENT_AMOUNT", "BASIC_AMOUNT",
#     "BENEFICIARY NAME", "NARRATION",
#     "Remarks", "DATE","COST_CENTER",
#     "LEDGER_NAME","LEDGER_UNDER","TO","BY"
# ]

# df_ui = df_ui[DISPLAY_COLUMNS]

# # ---------------------------------------------------
# # UI STATUS CHECKBOXES
# # ---------------------------------------------------
# STATUS_COLUMNS = ["ACCEPTED", "PAID", "HOLD", "REJECTED"]

# for col in STATUS_COLUMNS:
#     df_ui[col] = False

# cols = list(df_ui.columns)
# basic_index = cols.index("BASIC_AMOUNT")

# for s in STATUS_COLUMNS:
#     cols.remove(s)

# for i, s in enumerate(STATUS_COLUMNS):
#     cols.insert(basic_index + 1 + i, s)

# df_ui = df_ui[cols]

# # ---------------------------------------------------
# # SELECT ALL RADIO
# # ---------------------------------------------------
# st.subheader("📂 Pending Approvals")

# selected_status = st.radio(
#     "Select one status for all rows:",
#     options=["None"] + STATUS_COLUMNS,
#     horizontal=True
# )

# if selected_status != "None":
#     df_ui[STATUS_COLUMNS] = False
#     df_ui[selected_status] = True

# # ---------------------------------------------------
# # DATA EDITOR
# # ---------------------------------------------------
# with st.form("approval_form"):
#     edited_df = st.data_editor(
#         df_ui,
#         hide_index=True,
#         use_container_width=True,
#         column_config={
#             "ACCEPTED": st.column_config.CheckboxColumn("ACCEPTED"),
#             "PAID": st.column_config.CheckboxColumn("PAID"),
#             "HOLD": st.column_config.CheckboxColumn("HOLD"),
#             "REJECTED": st.column_config.CheckboxColumn("REJECTED"),
#             "BASIC_AMOUNT": st.column_config.NumberColumn("BASIC_AMOUNT", format="%.2f"),
#         }
#     )

#     submit = st.form_submit_button("💾 Save")

# # ---------------------------------------------------
# # SAVE LOGIC
# # ---------------------------------------------------
# if submit:
#     try:
#         edited_df.index = df_ui.index

#         for idx, row in edited_df.iterrows():
#             selected = [s for s in STATUS_COLUMNS if row[s]]
#             final_status = selected[-1] if selected else ""
#             df.at[idx, "APPROVAL_1"] = final_status
#             df.at[idx, "APPROVAL_2"] = final_status
#             df.at[idx, "BASIC_AMOUNT"] = row["BASIC_AMOUNT"]

#         df_clean = df.drop(columns=STATUS_COLUMNS, errors="ignore")

#         upload_excel_to_github(df_clean)
#         time.sleep(2)
#         upload_excel_to_drive(df_clean)

#         st.session_state.df = df_clean.copy()
#         st.cache_data.clear()

#         st.success("✅ Saved Successfully")

#     except Exception as e:
#         st.error(f"❌ Save failed: {e}")

# # ---------------------------------------------------
# # CURRENT MONTH EXPENSE SUMMARY
# # ---------------------------------------------------
# # st.write("---")
# # st.subheader("📅 Current Month Expense Summary")

# # try:
# #     expense_df = df.copy()

# #     expense_df["DATE"] = pd.to_datetime(
# #         expense_df["DATE"],
# #         errors="coerce",
# #         dayfirst=True
# #     )

# #     expense_df["FINAL AMOUNT"] = pd.to_numeric(
# #         expense_df["FINAL AMOUNT"],
# #         errors="coerce"
# #     ).fillna(0)

# #     today = pd.Timestamp.today()
# #     current_month = today.month
# #     current_year = today.year

# #     current_month_df = expense_df[
# #         (expense_df["DATE"].dt.month == current_month) &
# #         (expense_df["DATE"].dt.year == current_year)
# #     ].copy()

# #     if current_month_df.empty:
# #         st.warning("No expense data available for current month.")
# #     else:
# #         current_month_df["PROJECT_NAME"] = (
# #             current_month_df["PROJECT_NAME"]
# #             .astype(str)
# #             .str.upper()
# #             .str.strip()
# #         )

# #         current_summary = (
# #             current_month_df.groupby("PROJECT_NAME")["FINAL AMOUNT"]
# #             .sum()
# #             .reset_index()
# #             .sort_values("FINAL AMOUNT", ascending=False)
# #         )

# #         total_expense = current_month_df["FINAL AMOUNT"].sum()

# #         st.metric(
# #             label=f"💰 Total Expense - {today.strftime('%B %Y')}",
# #             value=f"₹ {total_expense:,.2f}"
# #         )

# #         st.dataframe(current_summary, use_container_width=True)

# #         chart = alt.Chart(current_summary).mark_bar().encode(
# #             x=alt.X("PROJECT_NAME:N", sort="-y"),
# #             y="FINAL AMOUNT:Q",
# #             tooltip=["PROJECT_NAME", "FINAL AMOUNT"]
# #         ).properties(height=400)

# #         st.altair_chart(chart, use_container_width=True)

# # except Exception as e:
# #     st.error(f"Error generating current month summary: {e}")

# # st.info("ℹ GitHub is the working copy. Google Drive is the final synced file.")

# # ---------------------------------------------------
# # CURRENT MONTH EXPENSE SUMMARY
# # ---------------------------------------------------

# # ---------------------------------------------------
# # CURRENT MONTH EXPENSE SUMMARY (FINAL FIXED)
# # ---------------------------------------------------

# st.write("---")
# st.subheader("📅 Current Month Expense Summary")

# try:
#     expense_df = download_monthly_sheet()

#     expense_df.columns = expense_df.columns.str.strip()

#     expense_df["DATE"] = pd.to_datetime(
#         expense_df["DATE"],
#         errors="coerce",
#         dayfirst=True
#     ).dt.date

#     expense_df["FINAL AMOUNT"] = (
#         expense_df["FINAL AMOUNT"]
#         .astype(str)
#         .str.replace(",", "", regex=False)
#         .str.replace("₹", "", regex=False)
#         .str.strip()
#     )

#     expense_df["FINAL AMOUNT"] = pd.to_numeric(
#         expense_df["FINAL AMOUNT"],
#         errors="coerce"
#     ).fillna(0)

#     today = pd.Timestamp.today().date()
#     start_date = today.replace(day=1)
#     last_day = calendar.monthrange(today.year, today.month)[1]
#     end_date = today.replace(day=last_day)

#     current_month_df = expense_df[
#         (expense_df["DATE"] >= start_date) &
#         (expense_df["DATE"] <= end_date)
#     ].copy()

#     if current_month_df.empty:
#         st.warning("⚠ No expense data available for current month.")
#     else:
#         current_month_df["PROJECT_NAME"] = (
#             current_month_df["PROJECT_NAME"]
#             .astype(str)
#             .str.upper()
#             .str.strip()
#         )

#         summary = (
#             current_month_df
#             .groupby("PROJECT_NAME", as_index=False)["FINAL AMOUNT"]
#             .sum()
#             .sort_values("FINAL AMOUNT", ascending=False)
#         )

#         total = current_month_df["FINAL AMOUNT"].sum()

#         st.metric(
#             label=f"💰 Total Expense - {today.strftime('%B %Y')}",
#             value=f"₹ {total:,.2f}"
#         )

#         st.dataframe(summary, use_container_width=True)

#         chart = alt.Chart(summary).mark_bar().encode(
#             x=alt.X("PROJECT_NAME:N", sort="-y"),
#             y="FINAL AMOUNT:Q",
#             tooltip=["PROJECT_NAME", "FINAL AMOUNT"]
#         ).properties(height=400)

#         st.altair_chart(chart, use_container_width=True)

# except Exception as e:
#     st.error(f"Error generating summary: {e}")


import io
import json
import base64
import time
import pandas as pd
import streamlit as st
import requests
import altair as alt
import calendar

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
)

st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management System,</h1>", unsafe_allow_html=True)
st.write("---")

# ---------------------------------------------------
# LOAD SECRETS
# ---------------------------------------------------
required_secrets = [
    "GITHUB_TOKEN",
    "GITHUB_REPO",
    "GITHUB_FILE_PATH",
    "FILE_ID",
    "SHEET_FILE_ID",
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
SHEET_FILE_ID = st.secrets["SHEET_FILE_ID"]
SERVICE_ACCOUNT_JSON = st.secrets["SERVICE_ACCOUNT_JSON"]

# ---------------------------------------------------
# GOOGLE DRIVE SERVICE
# ---------------------------------------------------
def get_drive_service():
    creds = Credentials.from_service_account_info(
        json.loads(SERVICE_ACCOUNT_JSON),
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=creds)

# ---------------------------------------------------
# DRIVE DOWNLOAD
# ---------------------------------------------------
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

# ---------------------------------------------------
# DRIVE UPLOAD
# ---------------------------------------------------
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
# GITHUB DOWNLOAD (NO CACHE)
# ---------------------------------------------------
def download_excel_from_github():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Cache-Control": "no-cache"
    }

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    content = r.json()["content"]
    file_bytes = base64.b64decode(content)

    return pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")

# ---------------------------------------------------
# GITHUB UPLOAD
# ---------------------------------------------------
def upload_excel_to_github(df):
    out = io.BytesIO()
    df.to_excel(out, index=False, engine="openpyxl")
    out.seek(0)

    content_b64 = base64.b64encode(out.read()).decode()

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Cache-Control": "no-cache"
    }

    sha = requests.get(url, headers=headers).json()["sha"]

    payload = {
        "message": "Updated via Streamlit Approval System",
        "content": content_b64,
        "sha": sha
    }

    r = requests.put(url, headers=headers, data=json.dumps(payload))
    r.raise_for_status()

# ---------------------------------------------------
# INITIAL SYNC (Drive → GitHub)
# ---------------------------------------------------
with st.spinner("🔄 Syncing latest data from Drive..."):
    drive_df = download_excel_from_drive()
    upload_excel_to_github(drive_df)
    df = download_excel_from_github()

# Ensure approval columns exist
for col in ["APPROVAL_1", "APPROVAL_2"]:
    if col not in df.columns:
        df[col] = ""

df = df.reset_index(drop=True)

# ---------------------------------------------------
# FILTER FULLY REJECTED
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
    "PROJECT_NAME",
    "BENEFICIARY NAME",
    "FINAL AMOUNT",
    "BASIC_AMOUNT",
    "DATE",
    "Remarks"
]

df_ui = df_ui[DISPLAY_COLUMNS + ["APPROVAL_1", "APPROVAL_2"]]

# ---------------------------------------------------
# STATUS CHECKBOXES
# ---------------------------------------------------
STATUS_COLUMNS = ["ACCEPTED", "PAID", "HOLD", "REJECTED"]

for col in STATUS_COLUMNS:
    df_ui[col] = False

st.subheader("📂 Pending Approvals")

selected_status = st.radio(
    "Select one status for all rows:",
    options=["None"] + STATUS_COLUMNS,
    horizontal=True
)

if selected_status != "None":
    df_ui[STATUS_COLUMNS] = False
    df_ui[selected_status] = True

# ---------------------------------------------------
# DATA EDITOR
# ---------------------------------------------------
with st.form("approval_form"):
    edited_df = st.data_editor(
        df_ui,
        hide_index=True,
        use_container_width=True
    )

    submit = st.form_submit_button("💾 Save")

# ---------------------------------------------------
# SAVE LOGIC
# ---------------------------------------------------
if submit:
    try:
        for idx, row in edited_df.iterrows():
            selected = [s for s in STATUS_COLUMNS if row[s]]
            final_status = selected[-1] if selected else ""

            df.at[idx, "APPROVAL_1"] = final_status
            df.at[idx, "APPROVAL_2"] = final_status

        upload_excel_to_github(df)
        upload_excel_to_drive(df)

        st.success("✅ Saved Successfully")
        st.rerun()

    except Exception as e:
        st.error(f"❌ Save failed: {e}")

# # ---------------------------------------------------
# # MONTHLY SUMMARY
# # ---------------------------------------------------
# st.write("---")
# st.subheader("📅 Current Month Expense Summary")

# try:
#     expense_df = download_excel_from_drive()

#     expense_df["DATE"] = pd.to_datetime(
#         expense_df["DATE"],
#         errors="coerce",
#         dayfirst=True
#     )

#     expense_df["FINAL AMOUNT"] = pd.to_numeric(
#         expense_df["FINAL AMOUNT"],
#         errors="coerce"
#     ).fillna(0)

#     today = pd.Timestamp.today()
#     current_month = today.month
#     current_year = today.year

#     current_month_df = expense_df[
#         (expense_df["DATE"].dt.month == current_month) &
#         (expense_df["DATE"].dt.year == current_year)
#     ]

#     if current_month_df.empty:
#         st.warning("⚠ No expense data for current month.")
#     else:
#         summary = (
#             current_month_df.groupby("PROJECT_NAME")["FINAL AMOUNT"]
#             .sum()
#             .reset_index()
#             .sort_values("FINAL AMOUNT", ascending=False)
#         )

#         total = current_month_df["FINAL AMOUNT"].sum()

#         st.metric(
#             label=f"💰 Total Expense - {today.strftime('%B %Y')}",
#             value=f"₹ {total:,.2f}"
#         )

#         st.dataframe(summary, use_container_width=True)

#         chart = alt.Chart(summary).mark_bar().encode(
#             x=alt.X("PROJECT_NAME:N", sort="-y"),
#             y="FINAL AMOUNT:Q",
#             tooltip=["PROJECT_NAME", "FINAL AMOUNT"]
#         ).properties(height=400)

#         st.altair_chart(chart, use_container_width=True)

# except Exception as e:
#     st.error(f"Error generating summary: {e}")

# st.info("ℹ GitHub is working copy. Google Drive is final source.")

# ---------------------------------------------------
# MONTHLY SUMMARY (FROM GOOGLE SHEET)
# ---------------------------------------------------
st.write("---")
st.subheader("📅 Current Month Expense Summary")

try:
    expense_df = download_monthly_sheet()

    expense_df.columns = expense_df.columns.str.strip()

    # Convert DATE
    expense_df["DATE"] = pd.to_datetime(
        expense_df["DATE"],
        errors="coerce",
        dayfirst=True
    )

    # Clean FINAL AMOUNT
    expense_df["FINAL AMOUNT"] = (
        expense_df["FINAL AMOUNT"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.strip()
    )

    expense_df["FINAL AMOUNT"] = pd.to_numeric(
        expense_df["FINAL AMOUNT"],
        errors="coerce"
    ).fillna(0)

    today = pd.Timestamp.today()
    current_month = today.month
    current_year = today.year

    current_month_df = expense_df[
        (expense_df["DATE"].dt.month == current_month) &
        (expense_df["DATE"].dt.year == current_year)
    ]

    if current_month_df.empty:
        st.warning("⚠ No expense data available for current month.")
    else:
        summary = (
            current_month_df
            .groupby("PROJECT_NAME", as_index=False)["FINAL AMOUNT"]
            .sum()
            .sort_values("FINAL AMOUNT", ascending=False)
        )

        total = current_month_df["FINAL AMOUNT"].sum()

        st.metric(
            label=f"💰 Total Expense - {today.strftime('%B %Y')}",
            value=f"₹ {total:,.2f}"
        )

        st.dataframe(summary, use_container_width=True)

        chart = alt.Chart(summary).mark_bar().encode(
            x=alt.X("PROJECT_NAME:N", sort="-y"),
            y="FINAL AMOUNT:Q",
            tooltip=["PROJECT_NAME", "FINAL AMOUNT"]
        ).properties(height=400)

        st.altair_chart(chart, use_container_width=True)

except Exception as e:
    st.error(f"Error generating summary: {e}")


