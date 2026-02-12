
#==================================new rerun latest ===================================================================

# import io
# import json
# import pandas as pd
# import streamlit as st
# from google.oauth2.service_account import Credentials
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
# import gspread
# import altair as alt

# # --------------------------
# # PAGE CONFIG
# # --------------------------
# st.set_page_config(
#     page_title="Drive Excel Sync",
#     page_icon="📝",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # --------------------------
# # SCROLL RESTORATION
# # --------------------------
# st.markdown(
#     """
#     <script>
#     document.addEventListener("DOMContentLoaded", function() {
#         let pos = sessionStorage.getItem("scroll_pos");
#         if(pos) window.scrollTo(0, parseInt(pos));
#     });
#     window.addEventListener("scroll", function() {
#         sessionStorage.setItem("scroll_pos", window.scrollY);
#     });
#     </script>
#     """, unsafe_allow_html=True
# )



# st.markdown("<h1 style='text-align:center;'>📊 Excel Data Management Panel</h1>", unsafe_allow_html=True)
# st.write("---")

# # --------------------------
# # LOAD SERVICE ACCOUNT
# # --------------------------
# if "SERVICE_ACCOUNT_JSON" not in st.secrets or "FILE_ID" not in st.secrets or "SHEET_FILE_ID" not in st.secrets:
#     st.error("Add SERVICE_ACCOUNT_JSON, FILE_ID, SHEET_FILE_ID to Streamlit secrets!")
#     st.stop()

# json_key = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])
# FILE_ID = st.secrets["FILE_ID"].strip()
# SHEET_FILE_ID = st.secrets["SHEET_FILE_ID"].strip()
# FOLDER_ID = "1PnU8vSLG6w30kCfCb9Ho4lNqoCYwrShH"

# SCOPES = ["https://www.googleapis.com/auth/drive",
#           "https://www.googleapis.com/auth/spreadsheets"]

# creds = Credentials.from_service_account_info(json_key, scopes=SCOPES)
# drive_service = build("drive", "v3", credentials=creds)
# gspread_client = gspread.authorize(creds)

# # --------------------------
# # CACHED EXCEL DOWNLOAD
# # --------------------------
# @st.cache_data(ttl=60)
# def download_excel_as_df(file_id: str) -> pd.DataFrame:
#     request = drive_service.files().get_media(fileId=file_id)
#     fh = io.BytesIO()
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while not done:
#         _, done = downloader.next_chunk()
#     fh.seek(0)
#     df = pd.read_excel(fh, engine="openpyxl")
#     return df

# # --------------------------
# # EXCEL UPLOAD
# # --------------------------
# def upload_excel_from_df(file_id: str, df: pd.DataFrame):
#     out = io.BytesIO()
#     df.to_excel(out, index=False, engine="openpyxl")
#     out.seek(0)
#     media = MediaIoBaseUpload(out, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", resumable=True)
#     drive_service.files().update(fileId=file_id, media_body=media, supportsAllDrives=True).execute()

# # --------------------------
# # INITIALIZE SESSION STATE
# # --------------------------
# if "df" not in st.session_state:
#     with st.spinner("Downloading Excel from Google Drive..."):
#         st.session_state.df = download_excel_as_df(FILE_ID)
#         # Ensure approval columns exist
#         for col in ["APPROVAL_1", "APPROVAL_2"]:
#             st.session_state.df[col] = st.session_state.df.get(col, "").astype(str).fillna("")

# if "search" not in st.session_state:
#     st.session_state.search = ""

# df = st.session_state.df

# # --------------------------
# # REMOVE REJECTED ROWS
# # --------------------------
# # df = df[
# #     ~(
# #         (df["APPROVAL_1"].str.upper() == "REJECTED") |
# #         (df["APPROVAL_2"].str.upper() == "REJECTED")
# #     )
# # ].reset_index(drop=True)

# df = df[
#     ~(
#         (df["APPROVAL_1"].str.upper() == "REJECTED") &
#         (df["APPROVAL_2"].str.upper() == "REJECTED")
#     )
# ].reset_index(drop=True)


# # --------------------------
# # DISPLAY TABLE
# # --------------------------
# status_options = ["ACCEPTED", "REJECTED", ""]

# # DISPLAY_COLUMN_ORDER = [
# #     "DATE", "COMPANY ACCOUNT NO", "COMPANY IFSC", "COMPANY PAN", "COMPANY GSTIN",
# #     "CORPORATE ID", "TRANSACTION TYPE", "GST %", "TDS %", "GST (Yes/No)",
# #     "TDS (Yes/No)", "FROM_MAIL", , "BENEFICIARY PAN",
# #     "BENEFICIARY GSTIN", "BENEFICIARY ACCOUNT NO", "FINAL AMOUNT", "PROJECT_NAME",
# #     "CATEGORY", "FIXED_AMOUNT", "BALANCE_AMOUNT", "ADJUSTMENT_AMOUNT", "BASIC_AMOUNT",
# #     "APPROVAL_1", "APPROVAL_2", "BENEFICIARY NAME", "NARRATION", "Remarks"
# # ]

# DISPLAY_COLUMN_ORDER = [
#     "STATUS_MATCHED_ESTIMATION", "GST %", "TDS %", "GST (Yes/No)",
#     "TDS (Yes/No)", "BENEFICIARY PAN",
#     "BENEFICIARY GSTIN", "BENEFICIARY ACCOUNT NO", "FINAL AMOUNT", "PROJECT_NAME",
#     "CATEGORY", "FIXED_AMOUNT", "BALANCE_AMOUNT", "ADJUSTMENT_AMOUNT", "BASIC_AMOUNT",
#     "APPROVAL_1", "APPROVAL_2", "BENEFICIARY NAME", "NARRATION", "Remarks","DATE"
# ]


# df_display = df[DISPLAY_COLUMN_ORDER].copy()
# df_display["BASIC_AMOUNT"] = pd.to_numeric(df_display.get("BASIC_AMOUNT", 0), errors="coerce").fillna(0)
# df_display["ADJUSTMENT_AMOUNT"] = pd.to_numeric(df_display.get("ADJUSTMENT_AMOUNT", 0), errors="coerce").fillna(0)

# # Auto-fill adjustment amount
# mask = (
#     df_display.get("STATUS_MATCHED_ESTIMATION", "").astype(str).str.upper() == "ESTIMATION NOT MATCHED"
# ) & (df_display["BASIC_AMOUNT"] != 0) & (df_display["ADJUSTMENT_AMOUNT"] == 0)
# df_display.loc[mask, "ADJUSTMENT_AMOUNT"] = df_display.loc[mask, "BASIC_AMOUNT"]

# # --------------------------
# # FORM FOR EDITING
# # --------------------------
# with st.form("edit_table_form"):
#     edited_df = st.data_editor(
#         df_display,
#         use_container_width=True,
#         hide_index=True,
#         num_rows="dynamic",
#         column_config={
#             "APPROVAL_1": st.column_config.SelectboxColumn("APPROVAL_1", options=status_options),
#             "APPROVAL_2": st.column_config.SelectboxColumn("APPROVAL_2", options=status_options),
#         }
#     )
#     submit = st.form_submit_button("💾 Save Changes to Drive")

# if submit:
#     try:
#         # Merge edited columns back
#         for col in DISPLAY_COLUMN_ORDER:
#             df[col] = edited_df[col]
#         st.session_state.df = df
#         upload_excel_from_df(FILE_ID, df)
#         # Refresh folder
#         drive_service.files().update(fileId=FOLDER_ID, body={}, supportsAllDrives=True).execute()
#         st.success("✅ Excel and folder updated!")
#     except Exception as e:
#         st.error(f"Failed to upload: {e}")

# # --------------------------
# # SEARCH FILTER
# # --------------------------
# st.session_state.search = st.text_input("Search (filters visible rows)", st.session_state.search)
# filtered = edited_df if st.session_state.search == "" else edited_df[
#     edited_df.apply(lambda row: row.astype(str).str.contains(st.session_state.search, case=False).any(), axis=1)
# ]
# st.dataframe(filtered, use_container_width=True)

# # --------------------------
# # PROJECT-WISE EXPENSE
# # --------------------------
# st.write("---")
# st.subheader("💼 Project-wise Highest Expense Categories")
# try:
#     sh = gspread_client.open_by_key(SHEET_FILE_ID)
#     ws = sh.sheet1
#     expense_df = pd.DataFrame(ws.get_all_records())
# except Exception as e:
#     st.error(f"Error loading Google Sheet: {e}")
#     st.stop()

# required_cols = ["PROJECT_NAME", "CATEGORY", "FINAL AMOUNT"]
# missing = [c for c in required_cols if c not in expense_df.columns]
# if missing:
#     st.error(f"Missing columns: {missing}")
#     st.stop()

# expense_df["PROJECT_NAME"] = expense_df["PROJECT_NAME"].astype(str).str.upper().str.strip()
# expense_df["FINAL AMOUNT"] = pd.to_numeric(expense_df["FINAL AMOUNT"], errors="coerce").fillna(0)

# # Filter current month
# expense_df["DATE"] = pd.to_datetime(expense_df["DATE"], errors="coerce")
# now = pd.Timestamp.now()
# expense_df = expense_df[
#     (expense_df["DATE"].dt.month == now.month) &
#     (expense_df["DATE"].dt.year == now.year)
# ]

# grp = expense_df.groupby(["PROJECT_NAME", "CATEGORY"])["FINAL AMOUNT"].sum().reset_index()
# top_expenses = grp.sort_values("FINAL AMOUNT", ascending=False).groupby("PROJECT_NAME").head(1).reset_index(drop=True)

# st.dataframe(top_expenses, use_container_width=True)

# # Altair chart
# chart = alt.Chart(top_expenses).mark_bar().encode(
#     x=alt.X("PROJECT_NAME:N", title="Project"),
#     y=alt.Y("FINAL AMOUNT:Q", title="Total Expense"),
#     color="CATEGORY:N",
#     tooltip=["PROJECT_NAME", "CATEGORY", "FINAL AMOUNT"]
# ).properties(height=400)
# st.altair_chart(chart, use_container_width=True)

# st.info("Note: This app overwrites the file in Drive. Consider creating backups if multiple users edit.")



# #GITHUB ---------======================================================================================================================
# import io
# import json
# import base64
# import pandas as pd
# import streamlit as st
# import requests
# import altair as alt
# import time

# # ---------------------------------------------------
# # PAGE CONFIG
# # ---------------------------------------------------
# st.set_page_config(
#     page_title="GitHub Excel Approval System",
#     page_icon="📝",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management system</h1>", unsafe_allow_html=True)
# st.write("---")

# # ---------------------------------------------------
# # SESSION FLAGS
# # ---------------------------------------------------
# if "df" not in st.session_state:
#     st.session_state.df = None

# if "edited_df" not in st.session_state:
#     st.session_state.edited_df = None

# if "save_in_progress" not in st.session_state:
#     st.session_state.save_in_progress = False

# # ---------------------------------------------------
# # LOAD SECRETS
# # ---------------------------------------------------
# required_secrets = ["GITHUB_TOKEN", "GITHUB_REPO", "GITHUB_FILE_PATH"]
# for key in required_secrets:
#     if key not in st.secrets:
#         st.error(f"{key} missing in Streamlit secrets")
#         st.stop()

# GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
# GITHUB_REPO = st.secrets["GITHUB_REPO"]          # e.g., "username/repo"
# GITHUB_FILE_PATH = st.secrets["GITHUB_FILE_PATH"]  # e.g., "data/approval.xlsx"

# HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# # ---------------------------------------------------
# # UTIL FUNCTIONS
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
#     # Convert df to Excel bytes
#     out = io.BytesIO()
#     df.to_excel(out, index=False, engine="openpyxl")
#     out.seek(0)
#     content_b64 = base64.b64encode(out.read()).decode()

#     # Get current file SHA
#     url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
#     r = requests.get(url, headers=HEADERS)
#     r.raise_for_status()
#     sha = r.json()["sha"]

#     # Push update
#     payload = {
#         "message": "Update approvals via Streamlit",
#         "content": content_b64,
#         "sha": sha
#     }
#     r = requests.put(url, headers=HEADERS, data=json.dumps(payload))
#     r.raise_for_status()
#     return r.json()

# # ---------------------------------------------------
# # LOAD DATA
# # ---------------------------------------------------
# if st.session_state.df is None:
#     with st.spinner("📥 Downloading Excel from GitHub..."):
#         df = download_excel_from_github()

#         for col in ["APPROVAL_1", "APPROVAL_2"]:
#             if col not in df.columns:
#                 df[col] = ""

#         st.session_state.df = df.reset_index(drop=True)

# df = st.session_state.df.copy()

# # ---------------------------------------------------
# # FILTER (UI ONLY)
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
#     "STATUS_MATCHED_ESTIMATION", "GST %", "TDS %", "GST (Yes/No)",
#     "TDS (Yes/No)", "BENEFICIARY PAN",
#     "BENEFICIARY GSTIN", "BENEFICIARY ACCOUNT NO", "FINAL AMOUNT", "PROJECT_NAME",
#     "CATEGORY", "FIXED_AMOUNT", "BALANCE_AMOUNT", "ADJUSTMENT_AMOUNT", "BASIC_AMOUNT",
#     "APPROVAL_1", "APPROVAL_2", "BENEFICIARY NAME",
#     "NARRATION", "Remarks", "DATE"
# ]

# df_ui = df_ui[DISPLAY_COLUMNS]

# # ---------------------------------------------------
# # AUTO ADJUSTMENT LOGIC
# # ---------------------------------------------------
# df_ui["BASIC_AMOUNT"] = pd.to_numeric(df_ui["BASIC_AMOUNT"], errors="coerce").fillna(0)
# df_ui["ADJUSTMENT_AMOUNT"] = pd.to_numeric(df_ui["ADJUSTMENT_AMOUNT"], errors="coerce").fillna(0)

# mask = (
#     df_ui["STATUS_MATCHED_ESTIMATION"].fillna("").str.upper() == "ESTIMATION NOT MATCHED"
# ) & (
#     df_ui["BASIC_AMOUNT"] != 0
# ) & (
#     df_ui["ADJUSTMENT_AMOUNT"] == 0
# )

# df_ui.loc[mask, "ADJUSTMENT_AMOUNT"] = df_ui.loc[mask, "BASIC_AMOUNT"]

# # ---------------------------------------------------
# # PRESERVE EDITOR STATE
# # ---------------------------------------------------
# if st.session_state.edited_df is None:
#     st.session_state.edited_df = df_ui.copy()

# # ---------------------------------------------------
# # EDIT FORM
# # # ---------------------------------------------------

# status_options = ["ACCEPTED", "REJECTED", "PAID", ""]

# st.subheader("📂 Pending Approvals")

# with st.form("approval_form"):
#     edited_df = st.data_editor(
#         st.session_state.edited_df,
#         key="approval_editor",
#         hide_index=True,
#         use_container_width=True,
#         disabled=[c for c in df_ui.columns if c not in ["APPROVAL_1", "APPROVAL_2"]],
#         column_config={
#             "APPROVAL_1": st.column_config.SelectboxColumn("APPROVAL_1", options=status_options),
#             "APPROVAL_2": st.column_config.SelectboxColumn("APPROVAL_2", options=status_options),
#         }
#     )



#     submit = st.form_submit_button("💾 Save Bulk Approval")



# # ---------------------------------------------------
# # SAVE LOGIC (GITHUB)
# # ---------------------------------------------------
# if submit:
#     try:
#         st.session_state.save_in_progress = True

#         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2"]] = \
#             edited_df[["APPROVAL_1", "APPROVAL_2"]].values

#         st.session_state.df = df.copy()
#         st.session_state.edited_df = edited_df.copy()

#         upload_excel_to_github(df)

#         time.sleep(5)

#         st.cache_data.clear()
#         st.success("✅ Changes saved to GitHub successfully!")

#     except Exception as e:
#         st.error(f"❌ Save failed: {e}")

#     finally:
#         st.session_state.save_in_progress = False

# # ---------------------------------------------------
# # SEARCH
# # ---------------------------------------------------
# st.write("---")
# search = st.text_input("🔍 Search")

# if search:
#     mask = st.session_state.edited_df.apply(
#         lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1
#     )
#     st.dataframe(st.session_state.edited_df[mask], use_container_width=True)
# else:
#     st.dataframe(st.session_state.edited_df, use_container_width=True)

# # ---------------------------------------------------
# # PROJECT-WISE EXPENSE SUMMARY
# # ---------------------------------------------------
# st.write("---")
# st.subheader("💼 Project-wise Highest Expense")

# # Using the same Excel data for summary
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

# st.info("⚠ This app overwrites the Excel file in GitHub. Enable backups if multiple users edit simultaneously.")


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

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management System</h1>", unsafe_allow_html=True)
# st.write("---")

# # ---------------------------------------------------
# # SESSION FLAGS
# # ---------------------------------------------------
# if "df" not in st.session_state:
#     st.session_state.df = None

# if "edited_df" not in st.session_state:
#     st.session_state.edited_df = None

# if "save_in_progress" not in st.session_state:
#     st.session_state.save_in_progress = False

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
#         st.error(f"{key} missing in Streamlit secrets")
#         st.stop()

# GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
# GITHUB_REPO = st.secrets["GITHUB_REPO"]
# GITHUB_FILE_PATH = st.secrets["GITHUB_FILE_PATH"]

# HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# # ---------------------------------------------------
# # GOOGLE DRIVE FUNCTIONS
# # ---------------------------------------------------
# def get_drive_service():
#     creds = Credentials.from_service_account_info(
#         st.secrets["SERVICE_ACCOUNT_JSON"],
#         scopes=["https://www.googleapis.com/auth/drive"]
#     )
#     return build("drive", "v3", credentials=creds)


# def download_excel_from_drive():
#     service = get_drive_service()
#     request = service.files().get_media(fileId=st.secrets["FILE_ID"])
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

#     service.files().update(
#         fileId=st.secrets["GDRIVE_FILE_ID"],
#         media_body=media
#     ).execute()

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
#     r = requests.get(url, headers=HEADERS)
#     r.raise_for_status()
#     sha = r.json()["sha"]

#     payload = {
#         "message": "Update approvals via Streamlit",
#         "content": content_b64,
#         "sha": sha
#     }

#     r = requests.put(url, headers=HEADERS, data=json.dumps(payload))
#     r.raise_for_status()

# # ---------------------------------------------------
# # INITIAL LOAD (DRIVE → GITHUB → APP)
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
# # FILTER (UI ONLY)
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
#     "STATUS_MATCHED_ESTIMATION", "GST %", "TDS %", "GST (Yes/No)",
#     "TDS (Yes/No)", "BENEFICIARY PAN", "BENEFICIARY GSTIN",
#     "BENEFICIARY ACCOUNT NO", "FINAL AMOUNT", "PROJECT_NAME",
#     "CATEGORY", "FIXED_AMOUNT", "BALANCE_AMOUNT", "ADJUSTMENT_AMOUNT",
#     "BASIC_AMOUNT", "APPROVAL_1", "APPROVAL_2", "BENEFICIARY NAME",
#     "NARRATION", "Remarks", "DATE"
# ]

# df_ui = df_ui[DISPLAY_COLUMNS]

# # ---------------------------------------------------
# # AUTO ADJUSTMENT LOGIC
# # ---------------------------------------------------
# df_ui["BASIC_AMOUNT"] = pd.to_numeric(df_ui["BASIC_AMOUNT"], errors="coerce").fillna(0)
# df_ui["ADJUSTMENT_AMOUNT"] = pd.to_numeric(df_ui["ADJUSTMENT_AMOUNT"], errors="coerce").fillna(0)

# mask = (
#     (df_ui["STATUS_MATCHED_ESTIMATION"].fillna("").str.upper() == "ESTIMATION NOT MATCHED") &
#     (df_ui["BASIC_AMOUNT"] != 0) &
#     (df_ui["ADJUSTMENT_AMOUNT"] == 0)
# )

# df_ui.loc[mask, "ADJUSTMENT_AMOUNT"] = df_ui.loc[mask, "BASIC_AMOUNT"]

# # ---------------------------------------------------
# # PRESERVE EDIT STATE
# # ---------------------------------------------------
# if st.session_state.edited_df is None:
#     st.session_state.edited_df = df_ui.copy()

# # ---------------------------------------------------
# # EDIT FORM
# # ---------------------------------------------------
# status_options = ["ACCEPTED", "REJECTED", "PAID", ""]

# st.subheader("📂 Pending Approvals")

# with st.form("approval_form"):
#     edited_df = st.data_editor(
#         st.session_state.edited_df,
#         key="approval_editor",
#         hide_index=True,
#         use_container_width=True,
#         disabled=[c for c in df_ui.columns if c not in ["APPROVAL_1", "APPROVAL_2"]],
#         column_config={
#             "APPROVAL_1": st.column_config.SelectboxColumn("APPROVAL_1", options=status_options),
#             "APPROVAL_2": st.column_config.SelectboxColumn("APPROVAL_2", options=status_options),
#         }
#     )

#     submit = st.form_submit_button("💾 Save Bulk Approval")

# # ---------------------------------------------------
# # SAVE LOGIC (GITHUB → 5s → DRIVE)
# # ---------------------------------------------------
# if submit:
#     try:
#         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2"]] = \
#             edited_df[["APPROVAL_1", "APPROVAL_2"]].values

#         st.session_state.df = df.copy()
#         st.session_state.edited_df = edited_df.copy()

#         upload_excel_to_github(df)

#         time.sleep(5)

#         upload_excel_to_drive(df)

#         st.cache_data.clear()
#         st.success("✅ Saved to GitHub and synced back to Drive!")

#     except Exception as e:
#         st.error(f"❌ Save failed: {e}")

# # ---------------------------------------------------
# # SEARCH
# # ---------------------------------------------------
# st.write("---")
# search = st.text_input("🔍 Search")

# if search:
#     mask = st.session_state.edited_df.apply(
#         lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1
#     )
#     st.dataframe(st.session_state.edited_df[mask], use_container_width=True)
# else:
#     st.dataframe(st.session_state.edited_df, use_container_width=True)

# # ---------------------------------------------------
# # PROJECT-WISE EXPENSE SUMMARY
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

# st.info("⚠️ GitHub is the working copy. Google Drive is auto-synced after save.")

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

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management System</h1>", unsafe_allow_html=True)
# st.write("---")

# # ---------------------------------------------------
# # SESSION STATE
# # ---------------------------------------------------
# if "df" not in st.session_state:
#     st.session_state.df = None

# if "edited_df" not in st.session_state:
#     st.session_state.edited_df = None

# # ---------------------------------------------------
# # LOAD SECRETS (USING YOUR EXACT NAMES)
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
# FILE_ID = st.secrets["FILE_ID"]  # 🔥 Google Drive Excel
# SERVICE_ACCOUNT_JSON = st.secrets["SERVICE_ACCOUNT_JSON"]

# HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# # ---------------------------------------------------
# # GOOGLE DRIVE FUNCTIONS (EXCEL FILE)
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

#     service.files().update(
#         fileId=FILE_ID,
#         media_body=media
#     ).execute()

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
# # INITIAL LOAD (DRIVE → GITHUB → APP)
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
# # FILTER (UI ONLY)
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
#     "APPROVAL_1", "APPROVAL_2",
#     "BENEFICIARY NAME", "NARRATION",
#     "Remarks", "DATE"
# ]

# df_ui = df_ui[DISPLAY_COLUMNS]

# # ---------------------------------------------------
# # AUTO ADJUSTMENT LOGIC
# # ---------------------------------------------------
# df_ui["BASIC_AMOUNT"] = pd.to_numeric(df_ui["BASIC_AMOUNT"], errors="coerce").fillna(0)
# df_ui["ADJUSTMENT_AMOUNT"] = pd.to_numeric(df_ui["ADJUSTMENT_AMOUNT"], errors="coerce").fillna(0)

# mask = (
#     (df_ui["STATUS_MATCHED_ESTIMATION"].fillna("").str.upper() == "ESTIMATION NOT MATCHED") &
#     (df_ui["BASIC_AMOUNT"] != 0) &
#     (df_ui["ADJUSTMENT_AMOUNT"] == 0)
# )

# df_ui.loc[mask, "ADJUSTMENT_AMOUNT"] = df_ui.loc[mask, "BASIC_AMOUNT"]

# if st.session_state.edited_df is None:
#     st.session_state.edited_df = df_ui.copy()

# # ---------------------------------------------------
# # EDITOR
# # ---------------------------------------------------
# # st.subheader("📂 Pending Approvals")

# # with st.form("approval_form"):
# #     edited_df = st.data_editor(
# #         st.session_state.edited_df,
# #         hide_index=True,
# #         use_container_width=True,
# #         disabled=[c for c in df_ui.columns if c not in ["APPROVAL_1", "APPROVAL_2"]],
# #         column_config={
# #             "APPROVAL_1": st.column_config.SelectboxColumn("APPROVAL_1", ["", "ACCEPTED", "REJECTED"]),
# #             "APPROVAL_2": st.column_config.SelectboxColumn("APPROVAL_2", ["", "ACCEPTED", "REJECTED"])
# #         }
# #     )

# #     submit = st.form_submit_button("💾 Save Bulk Approval")

# st.subheader("📂 Pending Approvals")

# with st.form("approval_form"):
#     edited_df = st.data_editor(
#         st.session_state.edited_df,
#         hide_index=True,
#         use_container_width=True,
#         disabled=[c for c in df_ui.columns if c not in ["APPROVAL_1", "APPROVAL_2"]],
#         column_config={
#             "APPROVAL_1": st.column_config.SelectboxColumn(
#                 "APPROVAL_1",
#                 options=["","ACCEPTED", "REJECTED","PAID","HOLD"]
#             ),
#             "APPROVAL_2": st.column_config.SelectboxColumn(
#                 "APPROVAL_2",
#                 options=["", "ACCEPTED", "REJECTED","PAID","HOLD"]
#             )
#         }
#     )

#     submit = st.form_submit_button("💾 Save Bulk Approval")


# # ---------------------------------------------------
# # SAVE (GITHUB → 5s → DRIVE)
# # ---------------------------------------------------
# if submit:
#     try:
#         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2"]] = \
#             edited_df[["APPROVAL_1", "APPROVAL_2"]].values

#         df.loc[df_ui.index, "ADJUSTMENT_AMOUNT"] = df_ui["ADJUSTMENT_AMOUNT"].values

#         upload_excel_to_github(df)
#         time.sleep(5)
#         upload_excel_to_drive(df)

#         st.cache_data.clear()
#         st.success("✅ Saved to GitHub and synced back to Google Drive")

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
# ================================================
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

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management System,</h1>", unsafe_allow_html=True)
# st.write("---")

# # ---------------------------------------------------
# # SESSION STATE
# # # ---------------------------------------------------
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

#     service.files().update(
#         fileId=FILE_ID,
#         media_body=media
#     ).execute()

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
# # # ---------------------------------------------------
# # if st.session_state.df is None:
# #     with st.spinner("🔄 Syncing Excel from Drive → GitHub..."):
# #         drive_df = download_excel_from_drive()
# #         upload_excel_to_github(drive_df)
# #         df = download_excel_from_github()

# #         for col in ["APPROVAL_1", "APPROVAL_2"]:
# #             if col not in df.columns:
# #                 df[col] = ""

# #         st.session_state.df = df.reset_index(drop=True)

# if "df" not in st.session_state or st.session_state.df is None:
#     with st.spinner("🔄 Syncing Excel from Drive → GitHub..."):
#         drive_df = download_excel_from_drive()
#         upload_excel_to_github(drive_df)
#         df = download_excel_from_github()

#         for col in ["APPROVAL_1", "APPROVAL_2"]:
#             if col not in df.columns:
#                 df[col] = ""

#         st.session_state.df = df.reset_index(drop=True)
#         st.session_state.edited_df = st.session_state.df.copy()
# else:
#     df = st.session_state.df.copy()


# df = st.session_state.df.copy()

# # ---------------------------------------------------
# # FILTER UI
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
#     "APPROVAL_1", "APPROVAL_2",
#     "BENEFICIARY NAME", "NARRATION",
#     "Remarks", "DATE","COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY" 
# ]

# df_ui = df_ui[DISPLAY_COLUMNS]

# # ---- FORCE TEXT COLUMNS AS STRING (CRITICAL FIX) ----
# TEXT_COLS = ["COST_CENTER", "LEDGER_NAME", "LEDGER_UNDER", "TO", "BY"]

# for col in TEXT_COLS:
#     df_ui[col] = df_ui[col].astype(str).replace("nan", "").replace("0", "").replace("0.0","").replace("0.00","")


# # ---------------------------------------------------
# # AUTO ADJUSTMENT LOGIC
# # ---------------------------------------------------
# df_ui["BASIC_AMOUNT"] = pd.to_numeric(df_ui["BASIC_AMOUNT"], errors="coerce").fillna(0)
# df_ui["ADJUSTMENT_AMOUNT"] = pd.to_numeric(df_ui["ADJUSTMENT_AMOUNT"], errors="coerce").fillna(0)

# mask = (
#     (df_ui["STATUS_MATCHED_ESTIMATION"].fillna("").str.upper() == "ESTIMATION NOT MATCHED") &
#     (df_ui["BASIC_AMOUNT"] != 0) &
#     (df_ui["ADJUSTMENT_AMOUNT"] == 0)
# )

# df_ui.loc[mask, "ADJUSTMENT_AMOUNT"] = df_ui.loc[mask, "BASIC_AMOUNT"]



# # if st.session_state.edited_df is None:
# #     st.session_state.edited_df = df_ui.copy()

# if "edited_df" not in st.session_state or st.session_state.edited_df is None:
#     st.session_state.edited_df = df_ui.copy()



# # ---------------------------------------------------
# # EDITOR
# # ---------------------------------------------------
# st.subheader("📂 Pending Approvals")

# # with st.form("approval_form"):
# #     edited_df = st.data_editor(
# #         st.session_state.edited_df,
# #         hide_index=True,
# #         use_container_width=True,
# #         disabled=[
# #             c for c in df_ui.columns
# #             if c not in ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT"]
# #         ],
# #         column_config={
# #             "APPROVAL_1": st.column_config.SelectboxColumn(
# #                 "APPROVAL_1",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "APPROVAL_2": st.column_config.SelectboxColumn(
# #                 "APPROVAL_2",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "BASIC_AMOUNT": st.column_config.NumberColumn(
# #                 "BASIC_AMOUNT",
# #                 min_value=0,
# #                 step=1,
# #                 format="%.2f"
# #             )
# #         }
# #     )

# #     submit = st.form_submit_button("💾 Save Bulk Approval")

# # with st.form("approval_form"):
# #     edited_df = st.data_editor(
# #         st.session_state.edited_df,
# #         hide_index=True,
# #         use_container_width=True,
# #         disabled=[
# #             c for c in df_ui.columns
# #             if c not in ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT", "COST_CENTER", "PARTICULAR", "LEDGER_UNDER", "TO", "BY"]
# #         ],
# #         column_config={
# #             "APPROVAL_1": st.column_config.SelectboxColumn(
# #                 "APPROVAL_1",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "APPROVAL_2": st.column_config.SelectboxColumn(
# #                 "APPROVAL_2",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "BASIC_AMOUNT": st.column_config.NumberColumn(
# #                 "BASIC_AMOUNT",
# #                 min_value=0,
# #                 step=1,
# #                 format="%.2f"
# #             ),
# #             # Make these text columns editable
# #             "COST_CENTER": st.column_config.TextColumn("COST_CENTER"),
# #             "PARTICULAR": st.column_config.TextColumn("PARTICULAR"),
# #             "LEDGER_UNDER": st.column_config.TextColumn("LEDGER_UNDER"),
# #             "TO": st.column_config.TextColumn("TO"),
# #             "BY": st.column_config.TextColumn("BY")
# #         }
# #     )

# #     submit = st.form_submit_button("💾 Save Bulk Approval")


# with st.form("approval_form"):
#     edited_df = st.data_editor(
#         st.session_state.edited_df.assign(
#             COST_CENTER=st.session_state.edited_df["COST_CENTER"].astype(str).replace("0", "").replace("0.0","").replace("0.00",""),
#             LEDGER_NAME=st.session_state.edited_df["LEDGER_NAME"].astype(str).replace("0", "").replace("0.0","").replace("0.00",""),
#             LEDGER_UNDER=st.session_state.edited_df["LEDGER_UNDER"].astype(str).replace("0", "").replace("0.0","").replace("0.00",""),
#             TO=st.session_state.edited_df["TO"].astype(str).replace("0", "").replace("0.0","").replace("0.00",""),
#             BY=st.session_state.edited_df["BY"].astype(str).replace("0", "").replace("0.0","").replace("0.00","")
#         ),
#         hide_index=True,
#         use_container_width=True,
#         disabled=[
#             c for c in df_ui.columns
#             if c not in ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
#                          "COST_CENTER", "LEDGER_NAME", "LEDGER_UNDER", "TO", "BY"]
#         ],
#         column_config={
#             "APPROVAL_1": st.column_config.SelectboxColumn(
#                 "APPROVAL_1",
#                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
#             ),
#             "APPROVAL_2": st.column_config.SelectboxColumn(
#                 "APPROVAL_2",
#                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
#             ),
#             "BASIC_AMOUNT": st.column_config.NumberColumn(
#                 "BASIC_AMOUNT",
#                 min_value=0,
#                 step=1,
#                 format="%.2f"
#             ),
#             "COST_CENTER": st.column_config.TextColumn("COST_CENTER"),
#             "LEDGER_NAME": st.column_config.TextColumn("LEDGER_NAME"),
#             "LEDGER_UNDER": st.column_config.TextColumn("LEDGER_UNDER"),
#             "TO": st.column_config.TextColumn("TO"),
#             "BY": st.column_config.TextColumn("BY")
#         }
#     )
#     st.session_state.edited_df = edited_df.copy()


#     submit = st.form_submit_button("💾 Save Bulk Approval")


# # ---------------------------------------------------
# # SAVE
# # ---------------------------------------------------
# # if submit:
# #     try:
# #         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT"]] = \
# #             edited_df[["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT"]].values

# #         recalc_mask = (
# #             (df["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
# #             (df["ADJUSTMENT_AMOUNT"].fillna(0) == 0)
# #         )

# #         df.loc[recalc_mask, "ADJUSTMENT_AMOUNT"] = df.loc[recalc_mask, "BASIC_AMOUNT"]

# #         upload_excel_to_github(df)
# #         time.sleep(5)
# #         upload_excel_to_drive(df)

# #         st.cache_data.clear()
# #         st.success("✅ Saved to GitHub and synced back to Google Drive")

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")

# # if submit:
# #     try:
# #         # Fill empty/null text columns with "0" before saving
# #         for col in ["COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]:
# #             edited_df[col] = edited_df[col].fillna("0").replace("", "0")

# #         # Ensure BASIC_AMOUNT is numeric
# #         edited_df["BASIC_AMOUNT"] = pd.to_numeric(edited_df["BASIC_AMOUNT"], errors="coerce").fillna(0)

# #         # Update df with edited values
# #         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
# #                              "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]] = \
# #             edited_df[["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
# #                        "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]].values

# #         # Recalculate ADJUSTMENT_AMOUNT if ESTIMATION NOT MATCHED
# #         recalc_mask = (
# #             (df["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
# #             (df["ADJUSTMENT_AMOUNT"].fillna(0) == 0)
# #         )
# #         df.loc[recalc_mask, "ADJUSTMENT_AMOUNT"] = df.loc[recalc_mask, "BASIC_AMOUNT"]

# #         # Upload to GitHub and Drive
# #         upload_excel_to_github(df)
# #         time.sleep(5)  # Give GitHub time to process
# #         upload_excel_to_drive(df)

# #         st.cache_data.clear()
# #         st.success("✅ Saved to GitHub and synced back to Google Drive")

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")

# # if submit:
# #     try:
# #         edited_df = st.session_state.edited_df.copy()

# #         # Clean text columns
# #         for col in ["COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]:
# #             edited_df[col] = edited_df[col].astype(str).fillna("0").replace("", "0")

# #         edited_df["BASIC_AMOUNT"] = pd.to_numeric(
# #             edited_df["BASIC_AMOUNT"], errors="coerce"
# #         ).fillna(0)

# #         # 🔧 CRITICAL FIX
# #         df["APPROVAL_1"] = df["APPROVAL_1"].astype(str).replace("nan","")
# #         df["APPROVAL_2"] = df["APPROVAL_2"].astype(str).replace("nan","")

# #         # Push edited values
# #         df.loc[
# #             df_ui.index,
# #             ["APPROVAL_1","APPROVAL_2","BASIC_AMOUNT",
# #              "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]
# #         ] = edited_df[
# #             ["APPROVAL_1","APPROVAL_2","BASIC_AMOUNT",
# #              "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]
# #         ].values

# #         recalc_mask = (
# #             (df["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
# #             (df["ADJUSTMENT_AMOUNT"].fillna(0) == 0)
# #         )
# #         df.loc[recalc_mask, "ADJUSTMENT_AMOUNT"] = df.loc[recalc_mask, "BASIC_AMOUNT"]

# #         upload_excel_to_github(df)
# #         time.sleep(5)
# #         upload_excel_to_drive(df)

# #         st.cache_data.clear()
# #         st.success("✅ Changes saved successfully")

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")


# if submit:
#     try:
#         # Copy current edited data
#         edited_df = st.session_state.edited_df.copy()

#         # Clean text columns
#         for col in TEXT_COLS:
#             edited_df[col] = edited_df[col].astype(str).fillna("0").replace("", "0")

#         edited_df["BASIC_AMOUNT"] = pd.to_numeric(edited_df["BASIC_AMOUNT"], errors="coerce").fillna(0)

#         # Clean approval columns
#         df["APPROVAL_1"] = df["APPROVAL_1"].astype(str).replace("nan","")
#         df["APPROVAL_2"] = df["APPROVAL_2"].astype(str).replace("nan","")

#         # Update main df with edited_df values
#         df.loc[
#             df_ui.index,
#             ["APPROVAL_1","APPROVAL_2","BASIC_AMOUNT"] + TEXT_COLS
#         ] = edited_df[["APPROVAL_1","APPROVAL_2","BASIC_AMOUNT"] + TEXT_COLS].values

#         # Recalculate ADJUSTMENT_AMOUNT
#         recalc_mask = (
#             (df["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
#             (df["ADJUSTMENT_AMOUNT"].fillna(0) == 0)
#         )
#         df.loc[recalc_mask, "ADJUSTMENT_AMOUNT"] = df.loc[recalc_mask, "BASIC_AMOUNT"]

#         # Upload to GitHub & Drive
#         upload_excel_to_github(df)
#         time.sleep(5)
#         upload_excel_to_drive(df)

#         # Update session state so the editor shows saved values
#         st.session_state.df = df.copy()
#         st.session_state.edited_df = edited_df.copy()

#         st.cache_data.clear()
#         st.success("✅ Changes saved successfully")

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

#     service.files().update(
#         fileId=FILE_ID,
#         media_body=media
#     ).execute()

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
# # if st.session_state.df is None:
# #     with st.spinner("🔄 Syncing Excel from Drive → GitHub..."):
# #         drive_df = download_excel_from_drive()
# #         upload_excel_to_github(drive_df)
# #         df = download_excel_from_github()

# #         for col in ["APPROVAL_1", "APPROVAL_2"]:
# #             if col not in df.columns:
# #                 df[col] = ""

# #         st.session_state.df = df.reset_index(drop=True)

# # df = st.session_state.df.copy()

# # # ---------------------------------------------------
# # # FILTER UI
# # # ---------------------------------------------------
# # df_ui = df[
# #     ~(
# #         (df["APPROVAL_1"].astype(str).str.upper() == "REJECTED") &
# #         (df["APPROVAL_2"].astype(str).str.upper() == "REJECTED")
# #     )
# # ].copy()

# # INITIAL LOAD
# if st.session_state.get("df") is None:
#     with st.spinner("🔄 Syncing Excel from Drive → GitHub..."):
#         drive_df = download_excel_from_drive()
#         upload_excel_to_github(drive_df)
#         df = download_excel_from_github()

#         # Add missing approval columns if not exist
#         for col in ["APPROVAL_1", "APPROVAL_2"]:
#             if col not in df.columns:
#                 df[col] = ""

#         st.session_state.df = df.reset_index(drop=True)

# # Always work with session_state.df
# df = st.session_state.df

# # -------------------------------
# # Filter for UI (pending approvals)
# # -------------------------------


# # -------------------------------
# # Prepare UI DataFrame (Pending Approvals)
# # -------------------------------
# if st.session_state.get("edited_df") is None:
#     # Filter out fully rejected rows
#     df_ui = df[
#         ~(
#             (df["APPROVAL_1"].astype(str).str.upper() == "REJECTED") &
#             (df["APPROVAL_2"].astype(str).str.upper() == "REJECTED")
#         )
#     ].copy()

#     # Keep only display columns
#     DISPLAY_COLUMNS = [
#         "STATUS_MATCHED_ESTIMATION", "GST %", "TDS %",
#         "GST (Yes/No)", "TDS (Yes/No)",
#         "BENEFICIARY PAN", "BENEFICIARY GSTIN",
#         "BENEFICIARY ACCOUNT NO", "FINAL AMOUNT",
#         "PROJECT_NAME", "CATEGORY",
#         "FIXED_AMOUNT", "BALANCE_AMOUNT",
#         "ADJUSTMENT_AMOUNT", "BASIC_AMOUNT",
#         "APPROVAL_1", "APPROVAL_2",
#         "BENEFICIARY NAME", "NARRATION",
#         "Remarks", "DATE","COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY" 
#     ]
#     df_ui = df_ui[DISPLAY_COLUMNS]

#     # Force text columns to strings
#     TEXT_COLS = ["COST_CENTER", "LEDGER_NAME", "LEDGER_UNDER", "TO", "BY"]
#     for col in TEXT_COLS:
#         df_ui[col] = df_ui[col].astype(str).replace("nan", "").replace("0", "").replace("0.0","").replace("0.00","")

#     # Set session state
#     st.session_state.edited_df = df_ui.copy()

# # Use the existing edited_df for UI
# df_ui = st.session_state.edited_df



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
#     "APPROVAL_1", "APPROVAL_2",
#     "BENEFICIARY NAME", "NARRATION",
#     "Remarks", "DATE","COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY" 
# ]

# df_ui = df_ui[DISPLAY_COLUMNS]

# # ---- FORCE TEXT COLUMNS AS STRING (CRITICAL FIX) ----
# TEXT_COLS = ["COST_CENTER", "LEDGER_NAME", "LEDGER_UNDER", "TO", "BY"]

# for col in TEXT_COLS:
#     df_ui[col] = df_ui[col].astype(str).replace("nan", "").replace("0", "").replace("0.0","").replace("0.00","")


# # ---------------------------------------------------
# # AUTO ADJUSTMENT LOGIC
# # ---------------------------------------------------
# df_ui["BASIC_AMOUNT"] = pd.to_numeric(df_ui["BASIC_AMOUNT"], errors="coerce").fillna(0)
# df_ui["ADJUSTMENT_AMOUNT"] = pd.to_numeric(df_ui["ADJUSTMENT_AMOUNT"], errors="coerce").fillna(0)

# mask = (
#     (df_ui["STATUS_MATCHED_ESTIMATION"].fillna("").str.upper() == "ESTIMATION NOT MATCHED") &
#     (df_ui["BASIC_AMOUNT"] != 0) &
#     (df_ui["ADJUSTMENT_AMOUNT"] == 0)
# )

# df_ui.loc[mask, "ADJUSTMENT_AMOUNT"] = df_ui.loc[mask, "BASIC_AMOUNT"]



# # if st.session_state.edited_df is None:
# #     st.session_state.edited_df = df_ui.copy()

# if "edited_df" not in st.session_state or st.session_state.edited_df is None:
#     st.session_state.edited_df = df_ui.copy()



# # ---------------------------------------------------
# # EDITOR
# # ---------------------------------------------------
# st.subheader("📂 Pending Approvals")

# # with st.form("approval_form"):
# #     edited_df = st.data_editor(
# #         st.session_state.edited_df,
# #         hide_index=True,
# #         use_container_width=True,
# #         disabled=[
# #             c for c in df_ui.columns
# #             if c not in ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT"]
# #         ],
# #         column_config={
# #             "APPROVAL_1": st.column_config.SelectboxColumn(
# #                 "APPROVAL_1",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "APPROVAL_2": st.column_config.SelectboxColumn(
# #                 "APPROVAL_2",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "BASIC_AMOUNT": st.column_config.NumberColumn(
# #                 "BASIC_AMOUNT",
# #                 min_value=0,
# #                 step=1,
# #                 format="%.2f"
# #             )
# #         }
# #     )

# #     submit = st.form_submit_button("💾 Save Bulk Approval")

# # with st.form("approval_form"):
# #     edited_df = st.data_editor(
# #         st.session_state.edited_df,
# #         hide_index=True,
# #         use_container_width=True,
# #         disabled=[
# #             c for c in df_ui.columns
# #             if c not in ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT", "COST_CENTER", "PARTICULAR", "LEDGER_UNDER", "TO", "BY"]
# #         ],
# #         column_config={
# #             "APPROVAL_1": st.column_config.SelectboxColumn(
# #                 "APPROVAL_1",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "APPROVAL_2": st.column_config.SelectboxColumn(
# #                 "APPROVAL_2",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "BASIC_AMOUNT": st.column_config.NumberColumn(
# #                 "BASIC_AMOUNT",
# #                 min_value=0,
# #                 step=1,
# #                 format="%.2f"
# #             ),
# #             # Make these text columns editable
# #             "COST_CENTER": st.column_config.TextColumn("COST_CENTER"),
# #             "PARTICULAR": st.column_config.TextColumn("PARTICULAR"),
# #             "LEDGER_UNDER": st.column_config.TextColumn("LEDGER_UNDER"),
# #             "TO": st.column_config.TextColumn("TO"),
# #             "BY": st.column_config.TextColumn("BY")
# #         }
# #     )

# #     submit = st.form_submit_button("💾 Save Bulk Approval")


# # with st.form("approval_form"):
# #     edited_df = st.data_editor(
# #         st.session_state.edited_df.assign(
# #             COST_CENTER=st.session_state.edited_df["COST_CENTER"].astype(str).replace("0", "").replace("0.0","").replace("0.00",""),
# #             LEDGER_NAME=st.session_state.edited_df["LEDGER_NAME"].astype(str).replace("0", "").replace("0.0","").replace("0.00",""),
# #             LEDGER_UNDER=st.session_state.edited_df["LEDGER_UNDER"].astype(str).replace("0", "").replace("0.0","").replace("0.00",""),
# #             TO=st.session_state.edited_df["TO"].astype(str).replace("0", "").replace("0.0","").replace("0.00",""),
# #             BY=st.session_state.edited_df["BY"].astype(str).replace("0", "").replace("0.0","").replace("0.00","")
# #         ),
# #         hide_index=True,
# #         use_container_width=True,
# #         disabled=[
# #             c for c in df_ui.columns
# #             if c not in ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
# #                          "COST_CENTER", "LEDGER_NAME", "LEDGER_UNDER", "TO", "BY"]
# #         ],
# #         column_config={
# #             "APPROVAL_1": st.column_config.SelectboxColumn(
# #                 "APPROVAL_1",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "APPROVAL_2": st.column_config.SelectboxColumn(
# #                 "APPROVAL_2",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "BASIC_AMOUNT": st.column_config.NumberColumn(
# #                 "BASIC_AMOUNT",
# #                 min_value=0,
# #                 step=1,
# #                 format="%.2f"
# #             ),
# #             "COST_CENTER": st.column_config.TextColumn("COST_CENTER"),
# #             "LEDGER_NAME": st.column_config.TextColumn("LEDGER_NAME"),
# #             "LEDGER_UNDER": st.column_config.TextColumn("LEDGER_UNDER"),
# #             "TO": st.column_config.TextColumn("TO"),
# #             "BY": st.column_config.TextColumn("BY")
# #         }
# #     )
# #     st.session_state.edited_df = edited_df.copy()


# #     submit = st.form_submit_button("💾 Save Bulk Approval")


# with st.form("approval_form"):
#     # Use session_state.edited_df directly
#     edited_df = st.data_editor(
#         st.session_state.edited_df,
#         key="approval_editor",
#         hide_index=True,
#         use_container_width=True,
#         disabled=[
#             c for c in df_ui.columns
#             if c not in ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
#                          "COST_CENTER", "LEDGER_NAME", "LEDGER_UNDER", "TO", "BY"]
#         ],
#         column_config={
#             "APPROVAL_1": st.column_config.SelectboxColumn(
#                 "APPROVAL_1",
#                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
#             ),
#             "APPROVAL_2": st.column_config.SelectboxColumn(
#                 "APPROVAL_2",
#                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
#             ),
#             "BASIC_AMOUNT": st.column_config.NumberColumn(
#                 "BASIC_AMOUNT",
#                 min_value=0,
#                 step=1,
#                 format="%.2f"
#             ),
#             "COST_CENTER": st.column_config.TextColumn("COST_CENTER"),
#             "LEDGER_NAME": st.column_config.TextColumn("LEDGER_NAME"),
#             "LEDGER_UNDER": st.column_config.TextColumn("LEDGER_UNDER"),
#             "TO": st.column_config.TextColumn("TO"),
#             "BY": st.column_config.TextColumn("BY")
#         }
#     )

#     submit = st.form_submit_button("💾 Save Bulk Approval")


# # ---------------------------------------------------
# # SAVE
# # ---------------------------------------------------
# # if submit:
# #     try:
# #         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT"]] = \
# #             edited_df[["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT"]].values

# #         recalc_mask = (
# #             (df["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
# #             (df["ADJUSTMENT_AMOUNT"].fillna(0) == 0)
# #         )

# #         df.loc[recalc_mask, "ADJUSTMENT_AMOUNT"] = df.loc[recalc_mask, "BASIC_AMOUNT"]

# #         upload_excel_to_github(df)
# #         time.sleep(5)
# #         upload_excel_to_drive(df)

# #         st.cache_data.clear()
# #         st.success("✅ Saved to GitHub and synced back to Google Drive")

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")

# # if submit:
# #     try:
# #         # Fill empty/null text columns with "0" before saving
# #         for col in ["COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]:
# #             edited_df[col] = edited_df[col].fillna("0").replace("", "0")

# #         # Ensure BASIC_AMOUNT is numeric
# #         edited_df["BASIC_AMOUNT"] = pd.to_numeric(edited_df["BASIC_AMOUNT"], errors="coerce").fillna(0)

# #         # Update df with edited values
# #         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
# #                              "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]] = \
# #             edited_df[["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
# #                        "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]].values

# #         # Recalculate ADJUSTMENT_AMOUNT if ESTIMATION NOT MATCHED
# #         recalc_mask = (
# #             (df["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
# #             (df["ADJUSTMENT_AMOUNT"].fillna(0) == 0)
# #         )
# #         df.loc[recalc_mask, "ADJUSTMENT_AMOUNT"] = df.loc[recalc_mask, "BASIC_AMOUNT"]

# #         # Upload to GitHub and Drive
# #         upload_excel_to_github(df)
# #         time.sleep(5)  # Give GitHub time to process
# #         upload_excel_to_drive(df)

# #         st.cache_data.clear()
# #         st.success("✅ Saved to GitHub and synced back to Google Drive")

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")

# # if submit:
# #     try:
# #         edited_df = st.session_state.edited_df.copy()

# #         # Clean text columns
# #         for col in ["COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]:
# #             edited_df[col] = edited_df[col].astype(str).fillna("0").replace("", "0")

# #         edited_df["BASIC_AMOUNT"] = pd.to_numeric(
# #             edited_df["BASIC_AMOUNT"], errors="coerce"
# #         ).fillna(0)

# #         # 🔧 CRITICAL FIX
# #         df["APPROVAL_1"] = df["APPROVAL_1"].astype(str).replace("nan","")
# #         df["APPROVAL_2"] = df["APPROVAL_2"].astype(str).replace("nan","")

# #         # Push edited values
# #         df.loc[
# #             df_ui.index,
# #             ["APPROVAL_1","APPROVAL_2","BASIC_AMOUNT",
# #              "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]
# #         ] = edited_df[
# #             ["APPROVAL_1","APPROVAL_2","BASIC_AMOUNT",
# #              "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]
# #         ].values

# #         recalc_mask = (
# #             (df["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
# #             (df["ADJUSTMENT_AMOUNT"].fillna(0) == 0)
# #         )
# #         df.loc[recalc_mask, "ADJUSTMENT_AMOUNT"] = df.loc[recalc_mask, "BASIC_AMOUNT"]

# #         upload_excel_to_github(df)
# #         time.sleep(5)
# #         upload_excel_to_drive(df)

# #         st.cache_data.clear()
# #         st.success("✅ Changes saved successfully")

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")



# # if submit:
# #     try:
# #         edited_df = st.session_state.edited_df.copy()

# #         # Clean text columns
# #         for col in ["COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]:
# #             edited_df[col] = edited_df[col].astype(str).fillna("0").replace("", "0")

# #         edited_df["BASIC_AMOUNT"] = pd.to_numeric(
# #             edited_df["BASIC_AMOUNT"], errors="coerce"
# #         ).fillna(0)

# #         # Clean df approval columns
# #         df["APPROVAL_1"] = df["APPROVAL_1"].astype(str).replace("nan","")
# #         df["APPROVAL_2"] = df["APPROVAL_2"].astype(str).replace("nan","")

# #         # Update df with edited values
# #         df.loc[
# #             df_ui.index,
# #             ["APPROVAL_1","APPROVAL_2","BASIC_AMOUNT",
# #              "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]
# #         ] = edited_df[
# #             ["APPROVAL_1","APPROVAL_2","BASIC_AMOUNT",
# #              "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]
# #         ].values

# #         # Recalculate ADJUSTMENT_AMOUNT if needed
# #         recalc_mask = (
# #             (df["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
# #             (df["ADJUSTMENT_AMOUNT"].fillna(0) == 0)
# #         )
# #         df.loc[recalc_mask, "ADJUSTMENT_AMOUNT"] = df.loc[recalc_mask, "BASIC_AMOUNT"]

# #         # Upload changes
# #         upload_excel_to_github(df)
# #         time.sleep(5)
# #         upload_excel_to_drive(df)

# #         # ✅ Update session_state so rerun preserves edits
# #         st.session_state.df = df.copy()
# #         st.session_state.edited_df = edited_df.copy()

# #         st.cache_data.clear()
# #         st.success("✅ Changes saved successfully")

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")


# if submit:
#     try:
#         # Save edited_df to session_state first (prevents losing edits)
#         st.session_state.edited_df = edited_df.copy()

#         # Clean numeric/text columns
#         for col in ["COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]:
#             st.session_state.edited_df[col] = st.session_state.edited_df[col].astype(str).fillna("0").replace("", "0")

#         st.session_state.edited_df["BASIC_AMOUNT"] = pd.to_numeric(
#             st.session_state.edited_df["BASIC_AMOUNT"], errors="coerce"
#         ).fillna(0)

#         # Update main df
#         df.loc[df_ui.index, ["APPROVAL_1","APPROVAL_2","BASIC_AMOUNT",
#                              "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]] = \
#             st.session_state.edited_df[
#                 ["APPROVAL_1","APPROVAL_2","BASIC_AMOUNT",
#                  "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]
#             ].values

#         # Recalculate adjustment if needed
#         recalc_mask = (
#             (df["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
#             (df["ADJUSTMENT_AMOUNT"].fillna(0) == 0)
#         )
#         df.loc[recalc_mask, "ADJUSTMENT_AMOUNT"] = df.loc[recalc_mask, "BASIC_AMOUNT"]

#         # Upload
#         upload_excel_to_github(df)
#         time.sleep(5)
#         upload_excel_to_drive(df)

#         # ✅ Update session_state
#         st.session_state.df = df.copy()

#         st.cache_data.clear()
#         st.success("✅ Changes saved successfully (No rerun reset!)")

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

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management System,</h1>", unsafe_allow_html=True)
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

#     service.files().update(
#         fileId=FILE_ID,
#         media_body=media
#     ).execute()

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
# # FILTER UI
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
#     "APPROVAL_1", "APPROVAL_2",
#     "BENEFICIARY NAME", "NARRATION",
#     "Remarks", "DATE","COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY" 
# ]

# df_ui = df_ui[DISPLAY_COLUMNS]

# # ---- FORCE TEXT COLUMNS AS STRING (CRITICAL FIX) ----
# TEXT_COLS = ["COST_CENTER", "LEDGER_NAME", "LEDGER_UNDER", "TO", "BY"]

# for col in TEXT_COLS:
#     df_ui[col] = df_ui[col].astype(str).replace("nan", "").replace("0", "").replace("0.0","").replace("0.00","")


# # ---------------------------------------------------
# # AUTO ADJUSTMENT LOGIC
# # ---------------------------------------------------
# df_ui["BASIC_AMOUNT"] = pd.to_numeric(df_ui["BASIC_AMOUNT"], errors="coerce").fillna(0)
# df_ui["ADJUSTMENT_AMOUNT"] = pd.to_numeric(df_ui["ADJUSTMENT_AMOUNT"], errors="coerce").fillna(0)

# mask = (
#     (df_ui["STATUS_MATCHED_ESTIMATION"].fillna("").str.upper() == "ESTIMATION NOT MATCHED") &
#     (df_ui["BASIC_AMOUNT"] != 0) &
#     (df_ui["ADJUSTMENT_AMOUNT"] == 0)
# )

# df_ui.loc[mask, "ADJUSTMENT_AMOUNT"] = df_ui.loc[mask, "BASIC_AMOUNT"]



# if st.session_state.edited_df is None:
#     st.session_state.edited_df = df_ui.copy()




# # ---------------------------------------------------
# # EDITOR
# # ---------------------------------------------------
# st.subheader("📂 Pending Approvals")

# # with st.form("approval_form"):
# #     edited_df = st.data_editor(
# #         st.session_state.edited_df,
# #         hide_index=True,
# #         use_container_width=True,
# #         disabled=[
# #             c for c in df_ui.columns
# #             if c not in ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT"]
# #         ],
# #         column_config={
# #             "APPROVAL_1": st.column_config.SelectboxColumn(
# #                 "APPROVAL_1",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "APPROVAL_2": st.column_config.SelectboxColumn(
# #                 "APPROVAL_2",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "BASIC_AMOUNT": st.column_config.NumberColumn(
# #                 "BASIC_AMOUNT",
# #                 min_value=0,
# #                 step=1,
# #                 format="%.2f"
# #             )
# #         }
# #     )

# #     submit = st.form_submit_button("💾 Save Bulk Approval")

# # with st.form("approval_form"):
# #     edited_df = st.data_editor(
# #         st.session_state.edited_df,
# #         hide_index=True,
# #         use_container_width=True,
# #         disabled=[
# #             c for c in df_ui.columns
# #             if c not in ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT", "COST_CENTER", "PARTICULAR", "LEDGER_UNDER", "TO", "BY"]
# #         ],
# #         column_config={
# #             "APPROVAL_1": st.column_config.SelectboxColumn(
# #                 "APPROVAL_1",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "APPROVAL_2": st.column_config.SelectboxColumn(
# #                 "APPROVAL_2",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "BASIC_AMOUNT": st.column_config.NumberColumn(
# #                 "BASIC_AMOUNT",
# #                 min_value=0,
# #                 step=1,
# #                 format="%.2f"
# #             ),
# #             # Make these text columns editable
# #             "COST_CENTER": st.column_config.TextColumn("COST_CENTER"),
# #             "PARTICULAR": st.column_config.TextColumn("PARTICULAR"),
# #             "LEDGER_UNDER": st.column_config.TextColumn("LEDGER_UNDER"),
# #             "TO": st.column_config.TextColumn("TO"),
# #             "BY": st.column_config.TextColumn("BY")
# #         }
# #     )

# #     submit = st.form_submit_button("💾 Save Bulk Approval")


# with st.form("approval_form"):
#     edited_df = st.data_editor(
#         st.session_state.edited_df.assign(
#             COST_CENTER=st.session_state.edited_df["COST_CENTER"].astype(str).replace("0", "").replace("0.0","").replace("0.00",""),
#             LEDGER_NAME=st.session_state.edited_df["LEDGER_NAME"].astype(str).replace("0", "").replace("0.0","").replace("0.00",""),
#             LEDGER_UNDER=st.session_state.edited_df["LEDGER_UNDER"].astype(str).replace("0", "").replace("0.0","").replace("0.00",""),
#             TO=st.session_state.edited_df["TO"].astype(str).replace("0", "").replace("0.0","").replace("0.00",""),
#             BY=st.session_state.edited_df["BY"].astype(str).replace("0", "").replace("0.0","").replace("0.00","")
#         ),
#         hide_index=True,
#         use_container_width=True,
#         disabled=[
#             c for c in df_ui.columns
#             if c not in ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
#                          "COST_CENTER", "LEDGER_NAME", "LEDGER_UNDER", "TO", "BY"]
#         ],
#         column_config={
#             "APPROVAL_1": st.column_config.SelectboxColumn(
#                 "APPROVAL_1",
#                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
#             ),
#             "APPROVAL_2": st.column_config.SelectboxColumn(
#                 "APPROVAL_2",
#                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
#             ),
#             "BASIC_AMOUNT": st.column_config.NumberColumn(
#                 "BASIC_AMOUNT",
#                 min_value=0,
#                 step=1,
#                 format="%.2f"
#             ),
#             "COST_CENTER": st.column_config.TextColumn("COST_CENTER"),
#             "LEDGER_NAME": st.column_config.TextColumn("LEDGER_NAME"),
#             "LEDGER_UNDER": st.column_config.TextColumn("LEDGER_UNDER"),
#             "TO": st.column_config.TextColumn("TO"),
#             "BY": st.column_config.TextColumn("BY")
#         }
#     )

#     submit = st.form_submit_button("💾 Save Bulk Approval")



# # ---------------------------------------------------
# # SAVE
# # ---------------------------------------------------
# # if submit:
# #     try:
# #         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT"]] = \
# #             edited_df[["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT"]].values

# #         recalc_mask = (
# #             (df["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
# #             (df["ADJUSTMENT_AMOUNT"].fillna(0) == 0)
# #         )

# #         df.loc[recalc_mask, "ADJUSTMENT_AMOUNT"] = df.loc[recalc_mask, "BASIC_AMOUNT"]

# #         upload_excel_to_github(df)
# #         time.sleep(5)
# #         upload_excel_to_drive(df)

# #         st.cache_data.clear()
# #         st.success("✅ Saved to GitHub and synced back to Google Drive")

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")

# if submit:
#     try:
#         # Fill empty/null text columns with "0" before saving
#         for col in ["COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]:
#             edited_df[col] = edited_df[col].fillna("0").replace("", "0")

#         # Ensure BASIC_AMOUNT is numeric
#         edited_df["BASIC_AMOUNT"] = pd.to_numeric(edited_df["BASIC_AMOUNT"], errors="coerce").fillna(0)

#         # Update df with edited values
#         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
#                              "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]] = \
#             edited_df[["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
#                        "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]].values

#         # Recalculate ADJUSTMENT_AMOUNT if ESTIMATION NOT MATCHED
#         recalc_mask = (
#             (df["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
#             (df["ADJUSTMENT_AMOUNT"].fillna(0) == 0)
#         )
#         df.loc[recalc_mask, "ADJUSTMENT_AMOUNT"] = df.loc[recalc_mask, "BASIC_AMOUNT"]

#         # Upload to GitHub and Drive
#         upload_excel_to_github(df)
#         time.sleep(5)  # Give GitHub time to process
#         upload_excel_to_drive(df)

#         st.cache_data.clear()
#         st.success("✅ Saved to GitHub and synced back to Google Drive")

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

#============================================02-12-2026====================================================================
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

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management System,</h1>", unsafe_allow_html=True)
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

#     service.files().update(
#         fileId=FILE_ID,
#         media_body=media
#     ).execute()

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
# # FILTER UI
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
#     "APPROVAL_1", "APPROVAL_2",
#     "BENEFICIARY NAME", "NARRATION",
#     "Remarks", "DATE","COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY" 
# ]

# df_ui = df_ui[DISPLAY_COLUMNS]

# # ---- FORCE TEXT COLUMNS AS STRING (CRITICAL FIX) ----
# TEXT_COLS = ["COST_CENTER", "LEDGER_NAME", "LEDGER_UNDER", "TO", "BY"]

# for col in TEXT_COLS:
#     df_ui[col] = df_ui[col].astype(str).replace("nan", "").replace("0", "").replace("0.0","").replace("0.00","")


# # ---------------------------------------------------
# # AUTO ADJUSTMENT LOGIC
# # ---------------------------------------------------
# df_ui["BASIC_AMOUNT"] = pd.to_numeric(df_ui["BASIC_AMOUNT"], errors="coerce").fillna(0)
# df_ui["ADJUSTMENT_AMOUNT"] = pd.to_numeric(df_ui["ADJUSTMENT_AMOUNT"], errors="coerce").fillna(0)

# mask = (
#     (df_ui["STATUS_MATCHED_ESTIMATION"].fillna("").str.upper() == "ESTIMATION NOT MATCHED") &
#     (df_ui["BASIC_AMOUNT"] != 0) &
#     (df_ui["ADJUSTMENT_AMOUNT"] == 0)
# )

# df_ui.loc[mask, "ADJUSTMENT_AMOUNT"] = df_ui.loc[mask, "BASIC_AMOUNT"]



# if st.session_state.edited_df is None:
#     st.session_state.edited_df = df_ui.copy()




# # ---------------------------------------------------
# # EDITOR
# # ---------------------------------------------------
# st.subheader("📂 Pending Approvals")

# # with st.form("approval_form"):
# #     edited_df = st.data_editor(
# #         st.session_state.edited_df,
# #         hide_index=True,
# #         use_container_width=True,
# #         disabled=[
# #             c for c in df_ui.columns
# #             if c not in ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT"]
# #         ],
# #         column_config={
# #             "APPROVAL_1": st.column_config.SelectboxColumn(
# #                 "APPROVAL_1",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "APPROVAL_2": st.column_config.SelectboxColumn(
# #                 "APPROVAL_2",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "BASIC_AMOUNT": st.column_config.NumberColumn(
# #                 "BASIC_AMOUNT",
# #                 min_value=0,
# #                 step=1,
# #                 format="%.2f"
# #             )
# #         }
# #     )

# #     submit = st.form_submit_button("💾 Save Bulk Approval")

# # with st.form("approval_form"):
# #     edited_df = st.data_editor(
# #         st.session_state.edited_df,
# #         hide_index=True,
# #         use_container_width=True,
# #         disabled=[
# #             c for c in df_ui.columns
# #             if c not in ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT", "COST_CENTER", "PARTICULAR", "LEDGER_UNDER", "TO", "BY"]
# #         ],
# #         column_config={
# #             "APPROVAL_1": st.column_config.SelectboxColumn(
# #                 "APPROVAL_1",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "APPROVAL_2": st.column_config.SelectboxColumn(
# #                 "APPROVAL_2",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "BASIC_AMOUNT": st.column_config.NumberColumn(
# #                 "BASIC_AMOUNT",
# #                 min_value=0,
# #                 step=1,
# #                 format="%.2f"
# #             ),
# #             # Make these text columns editable
# #             "COST_CENTER": st.column_config.TextColumn("COST_CENTER"),
# #             "PARTICULAR": st.column_config.TextColumn("PARTICULAR"),
# #             "LEDGER_UNDER": st.column_config.TextColumn("LEDGER_UNDER"),
# #             "TO": st.column_config.TextColumn("TO"),
# #             "BY": st.column_config.TextColumn("BY")
# #         }
# #     )

# #     submit = st.form_submit_button("💾 Save Bulk Approval")

# # ---- CLEAN TEXT COLUMNS BEFORE EDITOR ----
# for col in ["COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]:
#     st.session_state.edited_df[col] = (
#         st.session_state.edited_df[col]
#         .astype(str)
#         .replace(["0","0.0","0.00","nan"], "")
#     )


# # with st.form("approval_form"):
# #     edited_df = st.data_editor(
# #         st.session_state.edited_df.assign(
# #             COST_CENTER=st.session_state.edited_df["COST_CENTER"].astype(str).replace("0", "").replace("0.0","").replace("0.00",""),
# #             LEDGER_NAME=st.session_state.edited_df["LEDGER_NAME"].astype(str).replace("0", "").replace("0.0","").replace("0.00",""),
# #             LEDGER_UNDER=st.session_state.edited_df["LEDGER_UNDER"].astype(str).replace("0", "").replace("0.0","").replace("0.00",""),
# #             TO=st.session_state.edited_df["TO"].astype(str).replace("0", "").replace("0.0","").replace("0.00",""),
# #             BY=st.session_state.edited_df["BY"].astype(str).replace("0", "").replace("0.0","").replace("0.00","")
# #         ),
# #         hide_index=True,
# #         use_container_width=True,
# #         disabled=[
# #             c for c in df_ui.columns
# #             if c not in ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
# #                          "COST_CENTER", "LEDGER_NAME", "LEDGER_UNDER", "TO", "BY"]
# #         ],
# #         column_config={
# #             "APPROVAL_1": st.column_config.SelectboxColumn(
# #                 "APPROVAL_1",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "APPROVAL_2": st.column_config.SelectboxColumn(
# #                 "APPROVAL_2",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "BASIC_AMOUNT": st.column_config.NumberColumn(
# #                 "BASIC_AMOUNT",
# #                 min_value=0,
# #                 step=1,
# #                 format="%.2f"
# #             ),
# #             "COST_CENTER": st.column_config.TextColumn("COST_CENTER"),
# #             "LEDGER_NAME": st.column_config.TextColumn("LEDGER_NAME"),
# #             "LEDGER_UNDER": st.column_config.TextColumn("LEDGER_UNDER"),
# #             "TO": st.column_config.TextColumn("TO"),
# #             "BY": st.column_config.TextColumn("BY")
# #         }
# #     )

# #     submit = st.form_submit_button("💾 Save Bulk Approval")

# # --- Never modify dropdown columns ---
# for col in ["APPROVAL_1", "APPROVAL_2"]:
#     if col not in st.session_state.edited_df.columns:
#         st.session_state.edited_df[col] = ""
#     else:
#         st.session_state.edited_df[col] = st.session_state.edited_df[col].astype(str).replace("nan","")


# # with st.form("approval_form"):
# #     edited_df = st.data_editor(
# #         st.session_state.edited_df,
# #         hide_index=True,
# #         use_container_width=True,
# #         disabled=[
# #             c for c in df_ui.columns
# #             if c not in ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
# #                          "COST_CENTER", "LEDGER_NAME", "LEDGER_UNDER", "TO", "BY"]
# #         ],
# #         column_config={
# #             "APPROVAL_1": st.column_config.SelectboxColumn(
# #                 "APPROVAL_1",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "APPROVAL_2": st.column_config.SelectboxColumn(
# #                 "APPROVAL_2",
# #                 options=["", "ACCEPTED", "REJECTED", "PAID", "HOLD"]
# #             ),
# #             "BASIC_AMOUNT": st.column_config.NumberColumn(
# #                 "BASIC_AMOUNT",
# #                 min_value=0,
# #                 step=1,
# #                 format="%.2f"
# #             ),
# #             "COST_CENTER": st.column_config.TextColumn("COST_CENTER"),
# #             "LEDGER_NAME": st.column_config.TextColumn("LEDGER_NAME"),
# #             "LEDGER_UNDER": st.column_config.TextColumn("LEDGER_UNDER"),
# #             "TO": st.column_config.TextColumn("TO"),
# #             "BY": st.column_config.TextColumn("BY")
# #         }
# #     )

# #     submit = st.form_submit_button("💾 Save Bulk Approval")

# with st.form("approval_form"):
#     edited_df = st.data_editor(
#         st.session_state.edited_df,
#         key="editor",   # bind widget state
#         hide_index=True,
#         use_container_width=True,
#         disabled=[
#             c for c in df_ui.columns
#             if c not in ["APPROVAL_1","APPROVAL_2","BASIC_AMOUNT",
#                          "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]
#         ],
#         column_config={
#             "APPROVAL_1": st.column_config.SelectboxColumn(
#                 "APPROVAL_1", options=["","ACCEPTED","REJECTED","PAID","HOLD"]
#             ),
#             "APPROVAL_2": st.column_config.SelectboxColumn(
#                 "APPROVAL_2", options=["","ACCEPTED","REJECTED","PAID","HOLD"]
#             ),
#             "BASIC_AMOUNT": st.column_config.NumberColumn(
#                 "BASIC_AMOUNT", min_value=0, step=1, format="%.2f"
#             ),
#             "COST_CENTER": st.column_config.TextColumn("COST_CENTER"),
#             "LEDGER_NAME": st.column_config.TextColumn("LEDGER_NAME"),
#             "LEDGER_UNDER": st.column_config.TextColumn("LEDGER_UNDER"),
#             "TO": st.column_config.TextColumn("TO"),
#             "BY": st.column_config.TextColumn("BY"),
#         }
#     )
#     submit = st.form_submit_button("💾 Save")


# # ---------------------------------------------------
# # SAVE
# # ---------------------------------------------------
# # if submit:
# #     try:
# #         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT"]] = \
# #             edited_df[["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT"]].values

# #         recalc_mask = (
# #             (df["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
# #             (df["ADJUSTMENT_AMOUNT"].fillna(0) == 0)
# #         )

# #         df.loc[recalc_mask, "ADJUSTMENT_AMOUNT"] = df.loc[recalc_mask, "BASIC_AMOUNT"]

# #         upload_excel_to_github(df)
# #         time.sleep(5)
# #         upload_excel_to_drive(df)

# #         st.cache_data.clear()
# #         st.success("✅ Saved to GitHub and synced back to Google Drive")

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")

# # if submit:
# #     try:
# #         # Fill empty/null text columns with "0" before saving
# #         for col in ["COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]:
# #             edited_df[col] = edited_df[col].fillna("0").replace("", "0")

# #         # Ensure BASIC_AMOUNT is numeric
# #         edited_df["BASIC_AMOUNT"] = pd.to_numeric(edited_df["BASIC_AMOUNT"], errors="coerce").fillna(0)

# #         # Update df with edited values
# #         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
# #                              "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]] = \
# #             edited_df[["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
# #                        "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]].values

# #         # Recalculate ADJUSTMENT_AMOUNT if ESTIMATION NOT MATCHED
# #         recalc_mask = (
# #             (df["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
# #             (df["ADJUSTMENT_AMOUNT"].fillna(0) == 0)
# #         )
# #         df.loc[recalc_mask, "ADJUSTMENT_AMOUNT"] = df.loc[recalc_mask, "BASIC_AMOUNT"]

# #         # Upload to GitHub and Drive
# #         upload_excel_to_github(df)
# #         time.sleep(5)  # Give GitHub time to process
# #         upload_excel_to_drive(df)

# #         st.cache_data.clear()
# #         st.success("✅ Saved to GitHub and synced back to Google Drive")

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")


# # if submit:
# #     try:
# #         for col in ["COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]:
# #             edited_df[col] = edited_df[col].fillna("0").replace("", "0")

# #         edited_df["BASIC_AMOUNT"] = pd.to_numeric(
# #             edited_df["BASIC_AMOUNT"], errors="coerce"
# #         ).fillna(0)

# #         # Get original row positions of df_ui
# #         target_positions = list(df_ui.index)

# #         # Assign by POSITION not label
# #         df.iloc[target_positions, df.columns.get_indexer([
# #             "APPROVAL_1","APPROVAL_2","BASIC_AMOUNT",
# #             "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"
# #         ])] = edited_df[[
# #             "APPROVAL_1","APPROVAL_2","BASIC_AMOUNT",
# #             "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"
# #         ]].values

# #         # Recalculate ADJUSTMENT_AMOUNT
# #         recalc_mask = (
# #             (df["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
# #             (df["ADJUSTMENT_AMOUNT"].fillna(0) == 0)
# #         )
# #         df.loc[recalc_mask, "ADJUSTMENT_AMOUNT"] = df.loc[recalc_mask, "BASIC_AMOUNT"]

# #         upload_excel_to_github(df)
# #         time.sleep(5)
# #         upload_excel_to_drive(df)

# #         st.cache_data.clear()
# #         st.success("✅ Dropdown now saves without ROW_ID")

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")


# # if submit:
# #     try:
# #         for col in ["COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]:
# #             edited_df[col] = edited_df[col].fillna("0").replace("", "0")

# #         edited_df["BASIC_AMOUNT"] = pd.to_numeric(edited_df["BASIC_AMOUNT"], errors="coerce").fillna(0)

# #         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
# #                              "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]] = \
# #             edited_df[["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
# #                        "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]].values

# #         recalc_mask = (
# #             (df["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
# #             (df["ADJUSTMENT_AMOUNT"].fillna(0) == 0)
# #         )
# #         df.loc[recalc_mask, "ADJUSTMENT_AMOUNT"] = df.loc[recalc_mask, "BASIC_AMOUNT"]

# #         upload_excel_to_github(df)
# #         time.sleep(5)
# #         upload_excel_to_drive(df)

# #         st.cache_data.clear()
# #         st.success("✅ Saved to GitHub and synced back to Google Drive")

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")


# # if submit:
# #     try:
# #         # Ensure BASIC_AMOUNT is numeric
# #         edited_df["BASIC_AMOUNT"] = pd.to_numeric(
# #             edited_df["BASIC_AMOUNT"], errors="coerce"
# #         ).fillna(0)

# #         # Update df with edited values FIRST (dropdown columns untouched before this)
# #         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
# #                              "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]] = \
# #             edited_df[["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
# #                        "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]].values

# #         # Now clean only non-dropdown text columns in df
# #         for col in ["COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]:
# #             df[col] = df[col].fillna("0").replace("", "0")

# #         # Recalculate ADJUSTMENT_AMOUNT if ESTIMATION NOT MATCHED
# #         recalc_mask = (
# #             (df["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
# #             (df["ADJUSTMENT_AMOUNT"].fillna(0) == 0)
# #         )
# #         df.loc[recalc_mask, "ADJUSTMENT_AMOUNT"] = df.loc[recalc_mask, "BASIC_AMOUNT"]

# #         # Upload to GitHub and Drive
# #         upload_excel_to_github(df)
# #         time.sleep(5)
# #         upload_excel_to_drive(df)

# #         st.cache_data.clear()
# #         st.success("✅ Saved to GitHub and synced back to Google Drive")

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")

# # if submit:
# #     try:
# #         # Align edited_df to df_ui index
# #         edited_df = edited_df.copy()
# #         edited_df.index = df_ui.index

# #         # Ensure BASIC_AMOUNT is numeric
# #         edited_df["BASIC_AMOUNT"] = pd.to_numeric(
# #             edited_df["BASIC_AMOUNT"], errors="coerce"
# #         ).fillna(0)

# #         # Write back to main df
# #         cols = ["APPROVAL_1", "APPROVAL_2", "BASIC_AMOUNT",
# #                 "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]

# #         df.loc[df_ui.index, cols] = edited_df[cols].values

# #         # Clean only non-dropdown text columns in df
# #         for col in ["COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]:
# #             df[col] = df[col].fillna("0").replace("", "0")

# #         # Recalculate ADJUSTMENT_AMOUNT
# #         recalc_mask = (
# #             (df["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
# #             (df["ADJUSTMENT_AMOUNT"].fillna(0) == 0)
# #         )
# #         df.loc[recalc_mask, "ADJUSTMENT_AMOUNT"] = df.loc[recalc_mask, "BASIC_AMOUNT"]

# #         upload_excel_to_github(df)
# #         time.sleep(5)
# #         upload_excel_to_drive(df)

# #         st.cache_data.clear()
# #         # ---- Refresh session state after save so dropdowns don't revert ----
# #         st.session_state.df = df.copy()

# #         df_ui_new = df[
# #          ~(
# #         (df["APPROVAL_1"].astype(str).str.upper() == "REJECTED") &
# #         (df["APPROVAL_2"].astype(str).str.upper() == "REJECTED")
# #          )
# #         ].copy()

# #         df_ui_new = df_ui_new[DISPLAY_COLUMNS]

# #         st.session_state.edited_df = df_ui_new.copy()

# #         st.success("✅ Saved to GitHub and synced back to Google Drive")

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")

# # if submit:
# #     try:
# #         edited_df = edited_df.copy()
# #         edited_df.index = df_ui.index

# #         # numeric only
# #         edited_df["BASIC_AMOUNT"] = pd.to_numeric(
# #             edited_df["BASIC_AMOUNT"], errors="coerce"
# #         ).fillna(0)

# #         cols = ["APPROVAL_1","APPROVAL_2","BASIC_AMOUNT",
# #                 "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]

# #         df.loc[df_ui.index, cols] = edited_df[cols].values

# #         # clean only non-dropdown columns
# #         for col in ["COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]:
# #             df[col] = df[col].fillna("0").replace("", "0")

# #         upload_excel_to_github(df)
# #         time.sleep(5)
# #         upload_excel_to_drive(df)

# #         st.cache_data.clear()
# #         st.session_state.df = df.copy()
# #         st.session_state.edited_df = df_ui.copy()

# #         st.success("✅ Dropdown now saves correctly")

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")

# # if submit:
# #     try:
# #         # freeze editor state immediately
# #         st.session_state.edited_df = edited_df.copy()

# #         edited_df = edited_df.copy()
# #         edited_df.index = df_ui.index

# #         edited_df["BASIC_AMOUNT"] = pd.to_numeric(
# #             edited_df["BASIC_AMOUNT"], errors="coerce"
# #         ).fillna(0)

# #         cols = ["APPROVAL_1","APPROVAL_2","BASIC_AMOUNT",
# #                 "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]

# #         df.loc[df_ui.index, cols] = edited_df[cols].values

# #         # clean only non-dropdown columns
# #         for col in ["COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]:
# #             df[col] = df[col].fillna("0").replace("", "0")

# #         upload_excel_to_github(df)
# #         time.sleep(5)
# #         upload_excel_to_drive(df)

# #         st.cache_data.clear()

# #         # refresh UI data
# #         st.session_state.df = df.copy()
# #         st.session_state.edited_df = df_ui.copy()

# #         st.success("✅ No more data loss on rerun")

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")

# if submit:
#     try:
#         # freeze editor values
#         edited_df = edited_df.copy()
#         edited_df.index = df_ui.index

#         edited_df["BASIC_AMOUNT"] = pd.to_numeric(
#             edited_df["BASIC_AMOUNT"], errors="coerce"
#         ).fillna(0)

#         cols = ["APPROVAL_1","APPROVAL_2","BASIC_AMOUNT",
#                 "COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]

#         df.loc[df_ui.index, cols] = edited_df[cols].values

#         # clean only text cols
#         for col in ["COST_CENTER","LEDGER_NAME","LEDGER_UNDER","TO","BY"]:
#             df[col] = df[col].fillna("0").replace("", "0")

#         upload_excel_to_github(df)
#         time.sleep(5)
#         upload_excel_to_drive(df)

#         st.cache_data.clear()

#         # update main df only
#         st.session_state.df = df.copy()

#         # DO NOT overwrite edited_df here

#         st.success("✅ Saved without rerun data loss")
        

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



#=========================================checkbox ========================================================

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
#     layout="wide"
# )

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management System</h1>", unsafe_allow_html=True)
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
# # GOOGLE DRIVE
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

#     service.files().update(
#         fileId=FILE_ID,
#         media_body=media
#     ).execute()

# # ---------------------------------------------------
# # GITHUB
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
#     with st.spinner("🔄 Syncing Excel..."):
#         drive_df = download_excel_from_drive()
#         upload_excel_to_github(drive_df)
#         df = download_excel_from_github()

#         for col in ["APPROVAL_1", "APPROVAL_2"]:
#             if col not in df.columns:
#                 df[col] = ""

#         st.session_state.df = df.reset_index(drop=True)

# df = st.session_state.df.copy()

# # ---------------------------------------------------
# # STATUS CHECKBOX COLUMNS
# # ---------------------------------------------------
# status_cols = ["ACCEPTED", "PAID", "HOLD", "REJECTED"]

# for col in status_cols:
#     if col not in df.columns:
#         df[col] = False

# # Sync checkboxes from APPROVAL_1
# for idx in df.index:
#     val = str(df.at[idx, "APPROVAL_1"]).strip().upper()
#     for col in status_cols:
#         df.at[idx, col] = (val == col)

# # ---------------------------------------------------
# # SELECT / UNSELECT ALL (COLUMN LEVEL)
# # ---------------------------------------------------
# st.subheader("Select / Unselect All")

# c1, c2, c3, c4 = st.columns(4)

# select_all = {}

# with c1:
#     select_all["ACCEPTED"] = st.checkbox("All ACCEPTED")

# with c2:
#     select_all["PAID"] = st.checkbox("All PAID")

# with c3:
#     select_all["HOLD"] = st.checkbox("All HOLD")

# with c4:
#     select_all["REJECTED"] = st.checkbox("All REJECTED")

# for status in status_cols:
#     if select_all[status]:
#         for col in status_cols:
#             df[col] = False
#         df[status] = True
#         break

# # ---------------------------------------------------
# # DATA EDITOR
# # ---------------------------------------------------
# st.write("---")
# st.subheader("📂 Approvals")

# with st.form("approval_form"):

#     edited_df = st.data_editor(
#         df,
#         hide_index=True,
#         use_container_width=True,
#         column_config={
#             "ACCEPTED": st.column_config.CheckboxColumn("ACCEPTED"),
#             "PAID": st.column_config.CheckboxColumn("PAID"),
#             "HOLD": st.column_config.CheckboxColumn("HOLD"),
#             "REJECTED": st.column_config.CheckboxColumn("REJECTED"),
#         }
#     )

#     submit = st.form_submit_button("💾 Save")

# # ---------------------------------------------------
# # SAVE LOGIC
# # ---------------------------------------------------
# # ---------------------------------------------------
# # SAVE LOGIC
# # ---------------------------------------------------
# if submit:
#     try:
#         for idx, row in edited_df.iterrows():

#             selected = [col for col in status_cols if row[col]]

#             if len(selected) > 1:
#                 st.error(f"❌ Only ONE status allowed per row (Row {idx+1})")
#                 st.stop()

#             if len(selected) == 1:
#                 status = selected[0]
#                 df.at[idx, "APPROVAL_1"] = status
#                 df.at[idx, "APPROVAL_2"] = status
#             else:
#                 df.at[idx, "APPROVAL_1"] = ""
#                 df.at[idx, "APPROVAL_2"] = ""

#         # 🔥 REMOVE UI CHECKBOX COLUMNS BEFORE SAVING
#         df_to_save = df.drop(columns=status_cols, errors="ignore")

#         upload_excel_to_github(df_to_save)
#         time.sleep(3)
#         upload_excel_to_drive(df_to_save)

#         st.cache_data.clear()
#         st.session_state.df = df_to_save.copy()

#         st.success("✅ Saved Successfully (No extra columns in Excel)")

#     except Exception as e:
#         st.error(f"❌ Save failed: {e}")
# # ---------------------------------------------------
# # SUMMARY CHART
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

# st.info("ℹ GitHub is working copy. Google Drive is final synced file.")

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
    layout="wide"
)

st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management System</h1>", unsafe_allow_html=True)
st.write("---")

# ---------------------------------------------------
# SESSION STATE
# ---------------------------------------------------
if "df" not in st.session_state:
    st.session_state.df = None

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
# GOOGLE DRIVE
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

    service.files().update(
        fileId=FILE_ID,
        media_body=media
    ).execute()

# ---------------------------------------------------
# GITHUB
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
    with st.spinner("🔄 Syncing Excel..."):
        drive_df = download_excel_from_drive()
        upload_excel_to_github(drive_df)
        df = download_excel_from_github()

        for col in ["APPROVAL_1", "APPROVAL_2"]:
            if col not in df.columns:
                df[col] = ""

        st.session_state.df = df.reset_index(drop=True)

df = st.session_state.df.copy()

# ---------------------------------------------------
# STATUS CHECKBOX COLUMNS
# ---------------------------------------------------
status_cols = ["ACCEPTED", "PAID", "HOLD", "REJECTED"]

for col in status_cols:
    if col not in df.columns:
        df[col] = False

# Sync checkboxes from APPROVAL_1
for idx in df.index:
    val = str(df.at[idx, "APPROVAL_1"]).strip().upper()
    for col in status_cols:
        df.at[idx, col] = (val == col)

# ---------------------------------------------------
# SELECT / UNSELECT ALL (COLUMN LEVEL)
# ---------------------------------------------------
st.subheader("Select / Unselect All")

c1, c2, c3, c4 = st.columns(4)

select_all = {}

with c1:
    select_all["ACCEPTED"] = st.checkbox("All ACCEPTED")

with c2:
    select_all["PAID"] = st.checkbox("All PAID")

with c3:
    select_all["HOLD"] = st.checkbox("All HOLD")

with c4:
    select_all["REJECTED"] = st.checkbox("All REJECTED")

for status in status_cols:
    if select_all[status]:
        for col in status_cols:
            df[col] = False
        df[status] = True
        break

# ---------------------------------------------------
# DATA EDITOR
# ---------------------------------------------------
st.write("---")
st.subheader("📂 Approvals")

with st.form("approval_form"):

    edited_df = st.data_editor(
        df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "ACCEPTED": st.column_config.CheckboxColumn("ACCEPTED"),
            "PAID": st.column_config.CheckboxColumn("PAID"),
            "HOLD": st.column_config.CheckboxColumn("HOLD"),
            "REJECTED": st.column_config.CheckboxColumn("REJECTED"),
        }
    )

    submit = st.form_submit_button("💾 Save")

# ---------------------------------------------------
# SAVE LOGIC
# ---------------------------------------------------
if submit:
    try:
        for idx, row in edited_df.iterrows():

            selected = [col for col in status_cols if row[col]]

            if len(selected) > 1:
                st.error(f"❌ Only ONE status allowed per row (Row {idx+1})")
                st.stop()

            if len(selected) == 1:
                status = selected[0]
                df.at[idx, "APPROVAL_1"] = status
                df.at[idx, "APPROVAL_2"] = status
            else:
                df.at[idx, "APPROVAL_1"] = ""
                df.at[idx, "APPROVAL_2"] = ""

        upload_excel_to_github(df)
        time.sleep(3)
        upload_excel_to_drive(df)

        st.cache_data.clear()
        st.session_state.df = df.copy()

        st.success("✅ Saved Successfully (Both approvals updated)")

    except Exception as e:
        st.error(f"❌ Save failed: {e}")

# ---------------------------------------------------
# SUMMARY CHART
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

st.info("ℹ GitHub is working copy. Google Drive is final synced file.")
