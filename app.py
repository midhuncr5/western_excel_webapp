#==================simple structure=======================================

# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive
# import pandas as pd
# import streamlit as st

# # --------------------------
# # AUTHENTICATION
# # --------------------------
# gauth = GoogleAuth()
# gauth.LocalWebserverAuth()
# drive = GoogleDrive(gauth)

# FILE_ID = "1jJk2__AaS7iRtRkgGYnoW040O6ROsXYQ"

# # --------------------------
# # DOWNLOAD THE FILE
# # --------------------------
# file = drive.CreateFile({'id': FILE_ID})
# file.GetContentFile("local.xlsx")

# df = pd.read_excel("local.xlsx")

# # --------------------------
# # SHOW TABLE (EDITABLE)
# # --------------------------
# st.title("🔧 Drive Excel Sync System")
# st.write("Edit the table below and click Save")

# edited_df = st.data_editor(df)

# # --------------------------
# # SAVE BACK TO DRIVE
# # --------------------------
# if st.button("Save Changes to Drive"):
#     edited_df.to_excel("local.xlsx", index=False)
#     file.SetContentFile("local.xlsx")
#     file.Upload()

#     st.success("🔥 Excel Updated Successfully in Google Drive!")




#======================modified structure=============================================

# from pydrive.auth import GoogleAuth
# from pydrive.drive import GoogleDrive
# import pandas as pd
# import streamlit as st

# # --------------------------
# # PAGE CONFIG
# # --------------------------
# st.set_page_config(
#     page_title="Drive Excel Sync",
#     page_icon="📝",
#     layout="wide"
# )

# # --------------------------
# # AUTHENTICATION
# # --------------------------
# gauth = GoogleAuth()
# gauth.LocalWebserverAuth()
# drive = GoogleDrive(gauth)

# FILE_ID = "1jJk2__AaS7iRtRkgGYnoW040O6ROsXYQ"

# # --------------------------
# # HEADER
# # --------------------------
# st.markdown("<h1 style='text-align:center;'>📊 Excel Data Management</h1>", unsafe_allow_html=True)

# # --------------------------
# # DOWNLOAD FILE
# # --------------------------
# file = drive.CreateFile({'id': FILE_ID})
# file.GetContentFile("local.xlsx")

# df = pd.read_excel("local.xlsx")

# # --------------------------
# # DROPDOWN OPTIONS
# # --------------------------
# status_options = ["ACCEPTED", "REJECTED"]

# # Apply dropdown configuration only if columns exist
# column_config = {}
# if "Status1" in df.columns:
#     column_config["Status1"] = st.column_config.SelectboxColumn(
#         label="Status1",
#         options=status_options,
#         default=None
#     )

# if "Status2" in df.columns:
#     column_config["Status2"] = st.column_config.SelectboxColumn(
#         label="Status2",
#         options=status_options,
#         default=None
#     )

# # --------------------------
# # SHOW TABLE (EDITABLE)
# # --------------------------
# st.subheader("📂 Editable Table")

# edited_df = st.data_editor(
#     df,
#     use_container_width=True,
#     hide_index=True,
#     num_rows="dynamic",
#     column_config=column_config
# )

# # --------------------------
# # SAVE TO DRIVE
# # --------------------------
# if st.button("💾 Save Changes to Drive"):
#     edited_df.to_excel("local.xlsx", index=False)
#     file.SetContentFile("local.xlsx")
#     file.Upload()
#     st.success("🔥 Updated Successfully in Google Drive!")



#=========================FINAL STRUCTURE=================================================


# app.py
# import io
# import json
# import pandas as pd
# import streamlit as st
# from google.oauth2.service_account import Credentials
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

# # --------------------------
# # PAGE CONFIG
# # --------------------------
# st.set_page_config(
#     page_title="Drive Excel Sync",
#     page_icon="📝",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# st.markdown("<h1 style='text-align:center;'>📊 Excel Data Management Panel</h1>", unsafe_allow_html=True)
# st.write("---")

# # --------------------------
# # LOAD SERVICE ACCOUNT FROM STREAMLIT SECRETS
# # --------------------------
# # You will add SERVICE_ACCOUNT_JSON and FILE_ID in Streamlit Cloud secrets
# if "SERVICE_ACCOUNT_JSON" not in st.secrets:
#     st.error("Service account credentials not found in Streamlit secrets. Add SERVICE_ACCOUNT_JSON.")
#     st.stop()

# if "FILE_ID" not in st.secrets:
#     st.error("Google Drive FILE_ID not found in Streamlit secrets. Add FILE_ID.")
#     st.stop()

# json_key = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])
# FILE_ID = st.secrets["FILE_ID"].strip()

# SCOPES = ["https://www.googleapis.com/auth/drive"]

# creds = Credentials.from_service_account_info(json_key, scopes=SCOPES)
# drive_service = build("drive", "v3", credentials=creds)

# # --------------------------
# # UTILS: download file as bytes -> pandas
# # --------------------------
# @st.cache_data(ttl=60)
# def download_excel_as_df(file_id: str) -> pd.DataFrame:
#     request = drive_service.files().get_media(fileId=file_id)
#     fh = io.BytesIO()
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while not done:
#         status, done = downloader.next_chunk()  # returns (status, done)
#     fh.seek(0)
#     try:
#         df = pd.read_excel(fh, engine="openpyxl")
#     except Exception as e:
#         st.error(f"Error reading Excel file: {e}")
#         raise
#     return df

# # --------------------------
# # UTILS: upload bytes (overwrite existing file)
# # --------------------------
# def upload_excel_from_df(file_id: str, df: pd.DataFrame) -> None:
#     out = io.BytesIO()
#     df.to_excel(out, index=False, engine="openpyxl")
#     out.seek(0)
#     media = MediaIoBaseUpload(out, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", resumable=True)
#     # Use files().update to overwrite
#     drive_service.files().update(fileId=file_id, media_body=media).execute()

# # --------------------------
# # Load dataframe
# # --------------------------
# with st.spinner("Downloading Excel from Google Drive..."):
#     df = download_excel_as_df(FILE_ID)

# st.sidebar.header("Controls")
# st.sidebar.write("Use these controls to customize view.")
# if st.sidebar.checkbox("Show DataFrame Info"):
#     st.sidebar.write(df.info())

# # If you want to pre-process columns (e.g., ensure Status columns exist), do here
# if "Status1" not in df.columns:
#     df["Status1"] = ""
# if "Status2" not in df.columns:
#     df["Status2"] = ""

# # --------------------------
# # Column configuration (dropdown for Status columns)
# # --------------------------
# status_options = ["ACCEPTED", "REJECTED", ""]  # include empty if you want blank option

# # Streamlit's st.data_editor column_config API (Streamlit >=1.24) 
# # If your Streamlit version doesn't support column_config, fallback to st.data_editor plain.
# column_config = {}
# try:
#     # Attempt to import column classes if available
#     from streamlit import column_config as _col_cfg  # may be present depending on version
#     # Use simple dict of column settings; exact class names differ across versions — keep general
# except Exception:
#     # We'll still pass the names in a simpler way below
#     column_config = None

# # Build the editable table. We'll use st.data_editor with a simple fallback.
# st.subheader("📂 Editable Table (make changes and click Save)")

# # If Streamlit supports typed column_config with SelectboxColumn use it — otherwise use data_editor and post-process
# try:
#     # Newer Streamlit versions allow column_config parameter with SelectboxColumn
#     edited_df = st.data_editor(
#         df,
#         use_container_width=True,
#         hide_index=True,
#         num_rows="dynamic",
#         column_config={
#             "Status1": st.column_config.SelectboxColumn("Status1", options=status_options),
#             "Status2": st.column_config.SelectboxColumn("Status2", options=status_options),
#         }
#     )
# except Exception:
#     # Fallback: show editable grid without typed selects
#     edited_df = st.data_editor(df, use_container_width=True, hide_index=True, num_rows="dynamic")

# # Optionally apply search filter in-app
# search = st.text_input("Search (filters visible rows)", value="")
# if search:
#     mask = edited_df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
#     filtered = edited_df[mask]
# else:
#     filtered = edited_df

# st.write("Showing", len(filtered), "rows")
# st.dataframe(filtered, use_container_width=True)

# # --------------------------
# # Save button with confirmation & simple locking (per session)
# # --------------------------
# if st.button("💾 Save Changes to Drive"):
#     try:
#         with st.spinner("Uploading updated Excel to Drive..."):
#             upload_excel_from_df(FILE_ID, edited_df)
#         st.success("✅ Excel updated successfully in Google Drive.")
#     except Exception as e:
#         st.error(f"Failed to upload: {e}")

# st.write("---")
# st.info("Note: This app overwrites the file in Drive. Consider creating backups if multiple users will edit.")



# import io
# import json
# import pandas as pd
# import streamlit as st
# from google.oauth2.service_account import Credentials
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
# import gspread
# import altair as alt
# import streamlit.components.v1 as components

# components.html(
#     """
#     <script>
#     // Restore scroll on load
#     document.addEventListener("DOMContentLoaded", function() {
#         const pos = sessionStorage.getItem("scroll_pos");
#         if (pos !== null) {
#             window.scrollTo(0, parseInt(pos));
#         }
#     });

#     // Save scroll position
#     window.addEventListener("scroll", function() {
#         sessionStorage.setItem("scroll_pos", window.scrollY);
#     });
#     </script>
#     """,
#     height=0,
# )

# # --------------------------
# # PAGE CONFIG
# # --------------------------
# st.set_page_config(
#     page_title="Drive Excel Sync",
#     page_icon="📝",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )
# # ============================






# # ------------------------------------------------------------
# # SCROLL POSITION FIX (WORKING SOLUTION)
# # ------------------------------------------------------------
# scroll_js = """
# <script>
# document.addEventListener("DOMContentLoaded", function(event) {
#     let pos = sessionStorage.getItem("scroll_pos");
#     if (pos !== null) {
#         window.scrollTo(0, parseInt(pos));
#     }
# });

# window.addEventListener("scroll", function(event) {
#     sessionStorage.setItem("scroll_pos", window.scrollY);
# });
# </script>
# """

# st.markdown(scroll_js, unsafe_allow_html=True)

# #--------------------------------------------------

# st.markdown("<h1 style='text-align:center;'>📊 Excel Data Management Panel</h1>", unsafe_allow_html=True)
# st.write("---")



# # --------------------------
# # LOAD SERVICE ACCOUNT FROM STREAMLIT SECRETS
# # --------------------------
# if "SERVICE_ACCOUNT_JSON" not in st.secrets:
#     st.error("Service account credentials not found in Streamlit secrets. Add SERVICE_ACCOUNT_JSON.")
#     st.stop()

# if "FILE_ID" not in st.secrets:
#     st.error("Google Drive FILE_ID not found in Streamlit secrets. Add FILE_ID.")
#     st.stop()

# if "SHEET_FILE_ID" not in st.secrets:
#     st.error("Google Sheet SHEET_FILE_ID not found in Streamlit secrets. Add SHEET_FILE_ID.")
#     st.stop()

# json_key = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])
# FILE_ID = st.secrets["FILE_ID"].strip()
# SHEET_FILE_ID = st.secrets["SHEET_FILE_ID"].strip()
# FOLDER_ID = "1PnU8vSLG6w30kCfCb9Ho4lNqoCYwrShH"

# SCOPES = ["https://www.googleapis.com/auth/drive",
#           "https://www.googleapis.com/auth/spreadsheets"]

# creds = Credentials.from_service_account_info(json_key, scopes=SCOPES)

# # --------------------------
# # Initialize Google Drive & Sheets clients
# # --------------------------
# drive_service = build("drive", "v3", credentials=creds)
# gspread_client = gspread.authorize(creds)  # ✅ Fixed: gspread client

# # --------------------------
# # UTILS: download Excel from Drive
# # --------------------------
# @st.cache_data(ttl=60)
# def download_excel_as_df(file_id: str) -> pd.DataFrame:
#     request = drive_service.files().get_media(fileId=file_id)
#     fh = io.BytesIO()
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while not done:
#         status, done = downloader.next_chunk()
#     fh.seek(0)
#     try:
#         df = pd.read_excel(fh, engine="openpyxl")
#     except Exception as e:
#         st.error(f"Error reading Excel file: {e}")
#         raise
#     return df

# # --------------------------
# # UTILS: upload Excel to Drive (overwrite)
# # --------------------------
# # def upload_excel_from_df(file_id: str, df: pd.DataFrame) -> None:
# #     out = io.BytesIO()
# #     df.to_excel(out, index=False, engine="openpyxl")
# #     out.seek(0)
# #     media = MediaIoBaseUpload(out,
# #                               mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
# #                               resumable=True)
# #     drive_service.files().update(fileId=file_id, media_body=media).execute()

# def upload_excel_from_df(file_id: str, df: pd.DataFrame) -> None:
#     out = io.BytesIO()
#     df.to_excel(out, index=False, engine="openpyxl")
#     out.seek(0)
#     media = MediaIoBaseUpload(
#         out,
#         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         resumable=True
#     )
#     drive_service.files().update(
#         fileId=file_id,
#         media_body=media,
#         supportsAllDrives=True
#     ).execute()


# # --------------------------
# # Load dataframe
# # --------------------------
# with st.spinner("Downloading Excel from Google Drive..."):
#     df = download_excel_as_df(FILE_ID)

# st.sidebar.header("Controls")
# st.sidebar.write("Use these controls to customize view.")
# if st.sidebar.checkbox("Show DataFrame Info"):
#     st.sidebar.write(df.info())

# # Ensure approval columns exist
# for col in ["APPROVAL_1", "APPROVAL_2"]:
#     if col not in df.columns:
#         df[col] = ""
# for col in ["APPROVAL_1", "APPROVAL_2"]:
#     if col not in df.columns:
#         df[col] = ""
#     else:
#         df[col] = df[col].astype(str).fillna("")  # Force string dtype and fill NaN

# # ---------------------------------------
# # REMOVE rows that are already REJECTED
# # ---------------------------------------
# df = df[
#     ~(
#         (df["APPROVAL_1"].str.upper() == "REJECTED") |
#         (df["APPROVAL_2"].str.upper() == "REJECTED")
#     )
# ].reset_index(drop=True)


# # --------------------------
# # Status options for dropdowns
# # --------------------------
# status_options = ["ACCEPTED", "REJECTED", ""]  # include empty

# # # --------------------------
# # # Editable table
# # # --------------------------
# # st.subheader("📂 Editable Table (make changes and click Save)")

# # try:
# #     edited_df = st.data_editor(
# #         df,
# #         use_container_width=True,
# #         hide_index=True,
# #         num_rows="dynamic",
# #         column_config={
# #             "APPROVAL_1": st.column_config.SelectboxColumn("APPROVAL_1", options=status_options),
# #             "APPROVAL_2": st.column_config.SelectboxColumn("APPROVAL_2", options=status_options),
# #         }
# #     )
# # except Exception:
# #     # Fallback: editable without selectbox
# #     edited_df = st.data_editor(df, use_container_width=True, hide_index=True, num_rows="dynamic")

# # # --------------------------
# # # Search/filter
# # # --------------------------
# # search = st.text_input("Search (filters visible rows)", value="")
# # if search:
# #     mask = edited_df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
# #     filtered = edited_df[mask]
# # else:
# #     filtered = edited_df

# # # st.write("Showing", len(filtered), "rows")
# # # st.dataframe(filtered, use_container_width=True)

# # # # --------------------------
# # # # Save button
# # # # --------------------------
# # # if st.button("💾 Save Changes to Drive"):
# # #     try:
# # #         with st.spinner("Uploading updated Excel to Drive..."):
# # #             upload_excel_from_df(FILE_ID, edited_df)
# # #         st.success("✅ Excel updated successfully in Google Drive.")
# # #     except Exception as e:
# # #         st.error(f"Failed to upload: {e}")

# # if st.button("💾 Save Changes to Drive"):
# #     try:
# #         with st.spinner("Uploading updated Excel to Drive..."):
# #             upload_excel_from_df(FILE_ID, edited_df)

# #             # 👉 SIMPLE one-line update to refresh parent folder (Pending_FOLDER)
# #             drive_service.files().update(
# #                 fileId=FOLDER_ID,
# #                 body={},   # empty body = refresh metadata, updates folder timestamp
# #                 supportsAllDrives=True
# #             ).execute()

# #         st.success("✅ Excel and folder updated!")
# #     except Exception as e:
# #         st.error(f"Failed to upload: {e}")



# # --------------------------
# # Define columns to display & order
# # --------------------------
# DISPLAY_COLUMN_ORDER = [
#     "DATE",
#     "COMPANY ACCOUNT NO",
#     "COMPANY IFSC",
#     "COMPANY PAN",
#     "COMPANY GSTIN",
#     "CORPORATE ID",
#     "TRANSACTION TYPE",
#     "GST %",
#     "TDS %",
#     "GST (Yes/No)",
#     "TDS (Yes/No)",
#     "FROM_MAIL",
#     "STATUS_MATCHED_ESTIMATION",
#     "BENEFICIARY PAN",
#     "BENEFICIARY GSTIN",
#     "BENEFICIARY ACCOUNT NO",
#     "FINAL AMOUNT",
#     "PROJECT_NAME",
#     "CATEGORY",
#     "FIXED_AMOUNT",
#     "BALANCE_AMOUNT",
#     "ADJUSTMENT_AMOUNT",
#     "BASIC_AMOUNT",
#     "APPROVAL_1",
#     "APPROVAL_2",
#     "BENEFICIARY NAME",
#     "NARRATION",
#     "Remarks",
# ]

# # Filter df to only display columns for editing
# df_display = df[DISPLAY_COLUMN_ORDER].copy()


# # ===================================================================
# # AUTO-FILL ADJUSTMENT_AMOUNT BASED ON RULES
# # ===================================================================
# for col in ["STATUS_MATCHED_ESTIMATION", "BASIC_AMOUNT", "ADJUSTMENT_AMOUNT"]:
#     if col not in df_display.columns:
#         df_display[col] = ""

# df_display["BASIC_AMOUNT"] = pd.to_numeric(df_display["BASIC_AMOUNT"], errors="coerce").fillna(0)
# df_display["ADJUSTMENT_AMOUNT"] = pd.to_numeric(df_display["ADJUSTMENT_AMOUNT"], errors="coerce").fillna(0)

# cond_status = df_display["STATUS_MATCHED_ESTIMATION"].astype(str).str.upper() == "ESTIMATION NOT MATCHED"
# cond_basic = df_display["BASIC_AMOUNT"] != 0
# cond_adj_empty = df_display["ADJUSTMENT_AMOUNT"] == 0

# mask = cond_status & cond_basic & cond_adj_empty
# df_display.loc[mask, "ADJUSTMENT_AMOUNT"] = df_display.loc[mask, "BASIC_AMOUNT"]



# # --------------------------===============================================================
# # Define row background coloring for even rows
# # --------------------------
# # --------------------------
# # Editable table
# # --------------------------
# st.subheader("📂 Editable Table (make changes and click Save)")
# edited_display_df = st.data_editor(
#     df_display,
#     use_container_width=True,
#     hide_index=True,
#     num_rows="dynamic",
#     column_config={
#         "APPROVAL_1": st.column_config.SelectboxColumn("APPROVAL_1", options=status_options),
#         "APPROVAL_2": st.column_config.SelectboxColumn("APPROVAL_2", options=status_options),
#     }
# )

# # --------------------------
# # Search/filter
# # --------------------------
# search = st.text_input("Search (filters visible rows)", value="")
# if search:
#     mask = edited_display_df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
#     filtered = edited_display_df[mask]
# else:
#     filtered = edited_display_df

# # --------------------------
# # Save button
# # --------------------------
# if st.button("💾 Save Changes to Drive"):
#     try:
#         with st.spinner("Uploading updated Excel to Drive..."):
#             # Merge edited columns back to original df
#             for col in DISPLAY_COLUMN_ORDER:
#                 df[col] = edited_display_df[col]

#             # Upload full dataframe
#             upload_excel_from_df(FILE_ID, df)

#             # Refresh parent folder timestamp
#             drive_service.files().update(
#                 fileId=FOLDER_ID,
#                 body={},
#                 supportsAllDrives=True
#             ).execute()

#         st.success("✅ Excel and folder updated!")
#     except Exception as e:
#         st.error(f"Failed to upload: {e}")


# # --------------------------
# # Project-wise Highest Expense Categories (Google Sheet)
# # --------------------------
# st.write("---")
# st.subheader("💼 Project-wise Highest Expense Categories")

# try:
#     sh = gspread_client.open_by_key(SHEET_FILE_ID)
#     ws = sh.sheet1
#     expense_df = pd.DataFrame(ws.get_all_records())
#     st.success("Google Sheet loaded successfully!")
# except Exception as e:
#     st.error(f"Error loading Google Sheet: {e}")
#     st.stop()

# # --------------------------
# # Convert DATE column and filter current month
# # --------------------------
# if "DATE" not in expense_df.columns:
#     st.error("DATE column not found in sheet!")
#     st.stop()

# expense_df["DATE"] = pd.to_datetime(expense_df["DATE"], format="%d-%m-%Y", errors="coerce")
# expense_df = expense_df.dropna(subset=["DATE"])

# current_month = pd.Timestamp.now().month
# current_year = pd.Timestamp.now().year

# expense_df = expense_df[
#     (expense_df["DATE"].dt.month == current_month) &
#     (expense_df["DATE"].dt.year == current_year)
# ]

# st.info(f"Showing expenses only for **{current_month}-{current_year}**")
# # st.dataframe(expense_df.head(), use_container_width=True)
# st.dataframe(expense_df, use_container_width=True)

# # --------------------------
# # Required columns check
# # --------------------------
# # required = ["PROJECT_NAME", "CATEGORY", "FINAL AMOUNT"]
# # missing = [c for c in required if c not in expense_df.columns]
# # if missing:
# #     st.error(f"Missing columns: {missing}")
# #     st.stop()

# # expense_df["FINAL AMOUNT"] = pd.to_numeric(expense_df["FINAL AMOUNT"], errors="coerce").fillna(0)

# # Required columns check
# required = ["PROJECT_NAME", "CATEGORY", "FINAL AMOUNT"]
# missing = [c for c in required if c not in expense_df.columns]
# if missing:
#     st.error(f"Missing columns: {missing}")
#     st.stop()

# # NORMALIZE PROJECT NAME
# expense_df["PROJECT_NAME"] = (
#     expense_df["PROJECT_NAME"]
#     .astype(str)
#     .str.upper()
#     .str.strip()
# )

# expense_df["FINAL AMOUNT"] = pd.to_numeric(expense_df["FINAL AMOUNT"], errors="coerce").fillna(0)


# # --------------------------
# # Group and get top expense per project
# # --------------------------
# grp = (
#     expense_df.groupby(["PROJECT_NAME", "CATEGORY"])["FINAL AMOUNT"]
#     .sum()
#     .reset_index()
# )

# top_expenses = (
#     grp.sort_values("FINAL AMOUNT", ascending=False)
#        .groupby("PROJECT_NAME")
#        .head(1)
#        .reset_index(drop=True)
# )

# st.write("### 🏆 Highest Expense Category Per Project")
# st.dataframe(top_expenses, use_container_width=True)

# # --------------------------
# # Altair chart
# # --------------------------
# chart = (
#     alt.Chart(top_expenses)
#     .mark_bar()
#     .encode(
#         x=alt.X("PROJECT_NAME:N", title="Project"),
#         y=alt.Y("FINAL AMOUNT:Q", title="Total Expense"),
#         color="CATEGORY:N",
#         tooltip=["PROJECT_NAME", "CATEGORY", "FINAL AMOUNT"]
#     )
#     .properties(height=400)
# )

# st.altair_chart(chart, use_container_width=True)

# st.write("---")
# st.info("Note: This app overwrites the file in Drive. Consider creating backups if multiple users will edit.")
# #======================================new avoid rerun ================================================================================
# app.py
# app.py
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

# st.markdown("<h1 style='text-align:center;'>📊 Excel Data Management Panel</h1>", unsafe_allow_html=True)
# st.write("---")

# # --------------------------
# # LOAD SERVICE ACCOUNT
# # --------------------------
# required_secrets = ["SERVICE_ACCOUNT_JSON", "FILE_ID", "SHEET_FILE_ID"]
# for key in required_secrets:
#     if key not in st.secrets:
#         st.error(f"{key} not found in Streamlit secrets.")
#         st.stop()

# json_key = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])
# FILE_ID = st.secrets["FILE_ID"].strip()
# SHEET_FILE_ID = st.secrets["SHEET_FILE_ID"].strip()
# FOLDER_ID = "1PnU8vSLG6w30kCfCb9Ho4lNqoCYwrShH"

# SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
# creds = Credentials.from_service_account_info(json_key, scopes=SCOPES)
# drive_service = build("drive", "v3", credentials=creds)
# gspread_client = gspread.authorize(creds)

# # --------------------------
# # UTILS
# # --------------------------
# @st.cache_data(ttl=300)
# def download_excel_as_df(file_id: str) -> pd.DataFrame:
#     """Download Excel from Drive as DataFrame"""
#     request = drive_service.files().get_media(fileId=file_id)
#     fh = io.BytesIO()
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while not done:
#         _, done = downloader.next_chunk()
#     fh.seek(0)
#     df = pd.read_excel(fh, engine="openpyxl")
#     return df

# def upload_excel_from_df(file_id: str, df: pd.DataFrame):
#     """Upload DataFrame to Drive (overwrite)"""
#     out = io.BytesIO()
#     df.to_excel(out, index=False, engine="openpyxl")
#     out.seek(0)
#     media = MediaIoBaseUpload(
#         out,
#         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         resumable=True
#     )
#     drive_service.files().update(fileId=file_id, media_body=media, supportsAllDrives=True).execute()

# def safe_str_col(df, col):
#     """Ensure a column is string type and fill NaN"""
#     if col not in df.columns:
#         df[col] = ""
#     else:
#         df[col] = df[col].astype(str).fillna("")
#     return df

# # --------------------------
# # SESSION STATE: Load DataFrame once
# # --------------------------
# if "df" not in st.session_state:
#     with st.spinner("Downloading Excel from Google Drive..."):
#         st.session_state.df = download_excel_as_df(FILE_ID)

# df = st.session_state.df

# # Ensure string columns for safe .str.upper()
# df = safe_str_col(df, "APPROVAL_1")
# df = safe_str_col(df, "APPROVAL_2")

# # Remove rejected rows
# df = df[
#     ~(
#         (df["APPROVAL_1"].str.upper() == "REJECTED") |
#         (df["APPROVAL_2"].str.upper() == "REJECTED")
#     )
# ].reset_index(drop=True)

# # --------------------------
# # Sidebar
# # --------------------------
# st.sidebar.header("Controls")
# if st.sidebar.checkbox("Show DataFrame Info"):
#     st.sidebar.write(df.info())

# # --------------------------
# # Search box (persisted)
# # --------------------------
# if "search" not in st.session_state:
#     st.session_state.search = ""

# st.session_state.search = st.text_input("Search (filters visible rows)", value=st.session_state.search)

# # --------------------------
# # Editable Table in Form (avoids rerun)
# # --------------------------
# st.subheader("📂 Editable Table")
# status_options = ["ACCEPTED", "REJECTED", ""]

# with st.form("edit_form"):
#     edited_df = st.data_editor(
#         df,
#         use_container_width=True,
#         hide_index=True,
#         column_config={
#             "APPROVAL_1": st.column_config.SelectboxColumn("APPROVAL_1", options=status_options),
#             "APPROVAL_2": st.column_config.SelectboxColumn("APPROVAL_2", options=status_options),
#         },
#         num_rows="dynamic"
#     )
#     submit = st.form_submit_button("💾 Save Changes")
#     if submit:
#         st.session_state.df = edited_df  # persist edits
#         upload_excel_from_df(FILE_ID, edited_df)
#         # refresh folder timestamp
#         drive_service.files().update(fileId=FOLDER_ID, body={}, supportsAllDrives=True).execute()
#         st.success("✅ Excel updated successfully!")

# # --------------------------
# # Filter table by search
# # --------------------------
# if st.session_state.search:
#     mask = st.session_state.df.apply(lambda row: row.astype(str).str.contains(st.session_state.search, case=False).any(), axis=1)
#     filtered_df = st.session_state.df[mask]
# else:
#     filtered_df = st.session_state.df

# st.write(f"Showing {len(filtered_df)} rows after filter")
# st.dataframe(filtered_df, use_container_width=True)

# # --------------------------
# # Google Sheet: Top Expenses
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

# # DATE column check
# if "DATE" not in expense_df.columns:
#     st.error("DATE column not found in Google Sheet")
#     st.stop()

# expense_df["DATE"] = pd.to_datetime(expense_df["DATE"], format="%d-%m-%Y", errors="coerce")
# expense_df = expense_df.dropna(subset=["DATE"])
# current_month, current_year = pd.Timestamp.now().month, pd.Timestamp.now().year
# expense_df = expense_df[(expense_df["DATE"].dt.month == current_month) &
#                         (expense_df["DATE"].dt.year == current_year)]

# st.info(f"Showing expenses for **{current_month}-{current_year}**")

# required_cols = ["PROJECT_NAME", "CATEGORY", "FINAL AMOUNT"]
# missing_cols = [c for c in required_cols if c not in expense_df.columns]
# if missing_cols:
#     st.error(f"Missing columns in Google Sheet: {missing_cols}")
#     st.stop()

# expense_df["PROJECT_NAME"] = expense_df["PROJECT_NAME"].astype(str).str.upper().str.strip()
# expense_df["FINAL AMOUNT"] = pd.to_numeric(expense_df["FINAL AMOUNT"], errors="coerce").fillna(0)

# grp = expense_df.groupby(["PROJECT_NAME", "CATEGORY"])["FINAL AMOUNT"].sum().reset_index()
# top_expenses = grp.sort_values("FINAL AMOUNT", ascending=False).groupby("PROJECT_NAME").head(1).reset_index(drop=True)

# st.dataframe(top_expenses, use_container_width=True)

# chart = alt.Chart(top_expenses).mark_bar().encode(
#     x=alt.X("PROJECT_NAME:N", title="Project"),
#     y=alt.Y("FINAL AMOUNT:Q", title="Total Expense"),
#     color="CATEGORY:N",
#     tooltip=["PROJECT_NAME", "CATEGORY", "FINAL AMOUNT"]
# ).properties(height=400)

# st.altair_chart(chart, use_container_width=True)

# st.write("---")
# st.info("⚠️ Editing this app overwrites the file in Drive. Consider backups if multiple users edit simultaneously.")

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

#========

# import io
# import json
# import pandas as pd
# import streamlit as st
# from google.oauth2.service_account import Credentials
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
# import gspread
# import altair as alt

# # ---------------------------------------------------
# # PAGE CONFIG
# # ---------------------------------------------------
# st.set_page_config(
#     page_title="Drive Excel Approval System",
#     page_icon="📝",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management</h1>", unsafe_allow_html=True)
# st.write("---")

# # ---------------------------------------------------
# # LOAD SECRETS
# # ---------------------------------------------------
# required_secrets = ["SERVICE_ACCOUNT_JSON", "FILE_ID", "SHEET_FILE_ID"]
# for key in required_secrets:
#     if key not in st.secrets:
#         st.error(f"{key} missing in Streamlit secrets")
#         st.stop()

# json_key = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])
# FILE_ID = st.secrets["FILE_ID"]
# SHEET_FILE_ID = st.secrets["SHEET_FILE_ID"]
# FOLDER_ID = "1PnU8vSLG6w30kCfCb9Ho4lNqoCYwrShH"

# SCOPES = [
#     "https://www.googleapis.com/auth/drive",
#     "https://www.googleapis.com/auth/spreadsheets"
# ]

# creds = Credentials.from_service_account_info(json_key, scopes=SCOPES)
# drive_service = build("drive", "v3", credentials=creds)
# gspread_client = gspread.authorize(creds)

# # ---------------------------------------------------
# # UTIL FUNCTIONS
# # ---------------------------------------------------
# @st.cache_data(ttl=300)
# def download_excel(file_id):
#     request = drive_service.files().get_media(fileId=file_id)
#     fh = io.BytesIO()
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while not done:
#         _, done = downloader.next_chunk()
#     fh.seek(0)
#     return pd.read_excel(fh, engine="openpyxl")

# def upload_excel(file_id, df):
#     out = io.BytesIO()
#     df.to_excel(out, index=False, engine="openpyxl")
#     out.seek(0)
#     media = MediaIoBaseUpload(
#         out,
#         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         resumable=True
#     )
#     drive_service.files().update(
#         fileId=file_id,
#         media_body=media,
#         supportsAllDrives=True
#     ).execute()

# # ---------------------------------------------------
# # LOAD DATA ONCE (SESSION SAFE)
# # ---------------------------------------------------
# if "df" not in st.session_state:
#     with st.spinner("Downloading Excel from Drive..."):
#         df = download_excel(FILE_ID)

#         # Ensure ROW_ID (critical)
#         if "ROW_ID" not in df.columns:
#             df.insert(0, "ROW_ID", range(1, len(df) + 1))

#         # Ensure approval columns
#         for col in ["APPROVAL_1", "APPROVAL_2"]:
#             df[col] = df.get(col, "").astype(str).fillna("")

#         st.session_state.df = df

# df = st.session_state.df.copy()

# # ---------------------------------------------------
# # DISPLAY FILTER (ONLY UI)
# # ---------------------------------------------------
# df_ui = df[
#     ~(
#         (df["APPROVAL_1"].str.upper() == "REJECTED") &
#         (df["APPROVAL_2"].str.upper() == "REJECTED")
#     )
# ].copy()

# # DISPLAY_COLUMNS = [
# #     "ROW_ID",
# #     "PROJECT_NAME",
# #     "CATEGORY",
# #     "FINAL AMOUNT",
# #     "BASIC_AMOUNT",
# #     "ADJUSTMENT_AMOUNT",
# #     "APPROVAL_1",
# #     "APPROVAL_2",
# #     "BENEFICIARY NAME",
# #     "NARRATION",
# #     "Remarks",
# #     "DATE"
# # ]

# DISPLAY_COLUMNS = [
#      "STATUS_MATCHED_ESTIMATION", "GST %", "TDS %", "GST (Yes/No)",
#      "TDS (Yes/No)", "BENEFICIARY PAN",
#      "BENEFICIARY GSTIN", "BENEFICIARY ACCOUNT NO", "FINAL AMOUNT", "PROJECT_NAME",
#      "CATEGORY", "FIXED_AMOUNT", "BALANCE_AMOUNT", "ADJUSTMENT_AMOUNT", "BASIC_AMOUNT",
#      "APPROVAL_1", "APPROVAL_2", "BENEFICIARY NAME", "NARRATION", "Remarks","DATE"
#  ]



# df_ui = df_ui[DISPLAY_COLUMNS]

# # ---------------------------------------------------
# # AUTO CALC ADJUSTMENT AMOUNT
# # ---------------------------------------------------
# df_ui["BASIC_AMOUNT"] = pd.to_numeric(df_ui["BASIC_AMOUNT"], errors="coerce").fillna(0)
# df_ui["ADJUSTMENT_AMOUNT"] = pd.to_numeric(df_ui["ADJUSTMENT_AMOUNT"], errors="coerce").fillna(0)

# # mask = (
# #     (df_ui.get("STATUS_MATCHED_ESTIMATION", "").astype(str).str.upper() == "ESTIMATION NOT MATCHED") &
# #     (df_ui["BASIC_AMOUNT"] != 0) &
# #     (df_ui["ADJUSTMENT_AMOUNT"] == 0)
# # )
# # df_ui.loc[mask, "ADJUSTMENT_AMOUNT"] = df_ui.loc[mask, "BASIC_AMOUNT"]

# # Ensure the column exists
# if "STATUS_MATCHED_ESTIMATION" not in df_ui.columns:
#     df_ui["STATUS_MATCHED_ESTIMATION"] = ""

# # Create mask safely
# mask = (
#     df_ui["STATUS_MATCHED_ESTIMATION"]
#         .fillna("")
#         .astype(str)
#         .str.upper()
#         == "ESTIMATION NOT MATCHED"
# ) & (
#     df_ui["BASIC_AMOUNT"] != 0
# ) & (
#     df_ui["ADJUSTMENT_AMOUNT"] == 0
# )

# # Update ADJUSTMENT_AMOUNT
# df_ui.loc[mask, "ADJUSTMENT_AMOUNT"] = df_ui.loc[mask, "BASIC_AMOUNT"]


# # ---------------------------------------------------
# # EDIT FORM (NO RERUN BUG)
# # ---------------------------------------------------
# status_options = ["ACCEPTED", "REJECTED", ""]

# st.subheader("📂 Pending Approvals")

# with st.form("approval_form"):
#     edited_df = st.data_editor(
#         df_ui,
#         hide_index=True,
#         use_container_width=True,
#         column_config={
#             "APPROVAL_1": st.column_config.SelectboxColumn("APPROVAL_1", options=status_options),
#             "APPROVAL_2": st.column_config.SelectboxColumn("APPROVAL_2", options=status_options),
#         }
#     )
#     submit = st.form_submit_button("💾 Save Bulk Approval")

# # ---------------------------------------------------
# # SAVE (🔥 THIS FIXES YOUR ISSUE 🔥)
# # ---------------------------------------------------
# if submit:
#     try:
#         df.set_index("ROW_ID", inplace=True)
#         edited_df.set_index("ROW_ID", inplace=True)

#         # SAFE UPDATE BY KEY
#         df.update(edited_df)

#         df.reset_index(inplace=True)
#         st.session_state.df = df

#         upload_excel(FILE_ID, df)

#         # Touch folder (optional)
#         drive_service.files().update(
#             fileId=FOLDER_ID,
#             body={},
#             supportsAllDrives=True
#         ).execute()

#         st.success("✅ Bulk approval saved successfully!")
#     except Exception as e:
#         st.error(f"Save failed: {e}")

# # ---------------------------------------------------
# # SEARCH
# # ---------------------------------------------------
# search = st.text_input("Search")
# if search:
#     mask = edited_df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
#     st.dataframe(edited_df[mask], use_container_width=True)
# else:
#     st.dataframe(edited_df, use_container_width=True)

# # ---------------------------------------------------
# # PROJECT-WISE EXPENSE SUMMARY
# # ---------------------------------------------------
# st.write("---")
# st.subheader("💼 Project-wise Highest Expense")

# sh = gspread_client.open_by_key(SHEET_FILE_ID)
# ws = sh.sheet1
# expense_df = pd.DataFrame(ws.get_all_records())

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

# st.info("⚠️ This app overwrites the Excel file. Enable backups if multiple users edit simultaneously.")


# import io
# import json
# import pandas as pd
# import streamlit as st
# from google.oauth2.service_account import Credentials
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
# import gspread
# import altair as alt

# # ---------------------------------------------------
# # PAGE CONFIG
# # ---------------------------------------------------
# st.set_page_config(
#     page_title="Drive Excel Approval System",
#     page_icon="📝",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management</h1>", unsafe_allow_html=True)
# st.write("---")

# # ---------------------------------------------------
# # LOAD SECRETS
# # ---------------------------------------------------
# required_secrets = ["SERVICE_ACCOUNT_JSON", "FILE_ID", "SHEET_FILE_ID"]
# for key in required_secrets:
#     if key not in st.secrets:
#         st.error(f"{key} missing in Streamlit secrets")
#         st.stop()

# json_key = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])
# FILE_ID = st.secrets["FILE_ID"]
# SHEET_FILE_ID = st.secrets["SHEET_FILE_ID"]

# SCOPES = [
#     "https://www.googleapis.com/auth/drive",
#     "https://www.googleapis.com/auth/spreadsheets"
# ]

# creds = Credentials.from_service_account_info(json_key, scopes=SCOPES)
# drive_service = build("drive", "v3", credentials=creds)
# gspread_client = gspread.authorize(creds)

# # ---------------------------------------------------
# # UTIL FUNCTIONS
# # ---------------------------------------------------
# @st.cache_data(ttl=300)
# def download_excel(file_id):
#     request = drive_service.files().get_media(fileId=file_id)
#     fh = io.BytesIO()
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while not done:
#         _, done = downloader.next_chunk()
#     fh.seek(0)
#     return pd.read_excel(fh, engine="openpyxl")

# def upload_excel(file_id, df):
#     out = io.BytesIO()
#     df.to_excel(out, index=False, engine="openpyxl")
#     out.seek(0)
#     media = MediaIoBaseUpload(
#         out,
#         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         resumable=True
#     )
#     drive_service.files().update(
#         fileId=file_id,
#         media_body=media,
#         supportsAllDrives=True
#     ).execute()

# # ---------------------------------------------------
# # LOAD DATA (NO ROW_ID)
# # ---------------------------------------------------
# if "df" not in st.session_state:
#     with st.spinner("Downloading Excel from Drive..."):
#         df = download_excel(FILE_ID)

#         for col in ["APPROVAL_1", "APPROVAL_2"]:
#             if col not in df.columns:
#                 df[col] = ""

#         st.session_state.df = df.reset_index(drop=True)

# df = st.session_state.df.copy()

# # ---------------------------------------------------
# # FILTER REJECTED RECORDS (UI ONLY)
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
# # EDIT FORM (EDITABLE FIX)
# # ---------------------------------------------------
# status_options = ["ACCEPTED", "REJECTED", ""]

# st.subheader("📂 Pending Approvals")

# with st.form("approval_form"):
#     edited_df = st.data_editor(
#         df_ui,
#         key="approval_editor",  # 🔥 REQUIRED
#         hide_index=True,
#         use_container_width=True,
#         disabled=[
#             c for c in df_ui.columns
#             if c not in ["APPROVAL_1", "APPROVAL_2"]
#         ],
#         column_config={
#             "APPROVAL_1": st.column_config.SelectboxColumn("APPROVAL_1", options=status_options),
#             "APPROVAL_2": st.column_config.SelectboxColumn("APPROVAL_2", options=status_options),
#         }
#     )
#     submit = st.form_submit_button("💾 Save Bulk Approval")

# # ---------------------------------------------------
# # SAVE (NO ROW_ID)
# # ---------------------------------------------------
# if submit:
#     try:
#         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2"]] = \
#             edited_df[["APPROVAL_1", "APPROVAL_2"]].values

#         st.session_state.df = df
#         upload_excel(FILE_ID, df)

#         st.success("✅ Bulk approval saved successfully!")
#     except Exception as e:
#         st.error(f"Save failed: {e}")

# # ---------------------------------------------------
# # SEARCH
# # ---------------------------------------------------
# search = st.text_input("Search")
# if search:
#     mask = edited_df.apply(
#         lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1
#     )
#     st.dataframe(edited_df[mask], use_container_width=True)
# else:
#     st.dataframe(edited_df, use_container_width=True)

# # ---------------------------------------------------
# # PROJECT-WISE EXPENSE SUMMARY
# # ---------------------------------------------------
# st.write("---")
# st.subheader("💼 Project-wise Highest Expense")

# sh = gspread_client.open_by_key(SHEET_FILE_ID)
# ws = sh.sheet1
# expense_df = pd.DataFrame(ws.get_all_records())

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

# st.info("⚠️ This app overwrites the Excel file. Enable backups if multiple users edit simultaneously.")


#cache
# import io
# import json
# import pandas as pd
# import streamlit as st
# from google.oauth2.service_account import Credentials
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
# import gspread
# import altair as alt

# # ---------------------------------------------------
# # PAGE CONFIG
# # ---------------------------------------------------
# st.set_page_config(
#     page_title="Drive Excel Approval System",
#     page_icon="📝",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management</h1>", unsafe_allow_html=True)
# st.write("---")

# # ---------------------------------------------------
# # LOAD SECRETS
# # ---------------------------------------------------
# required_secrets = ["SERVICE_ACCOUNT_JSON", "FILE_ID", "SHEET_FILE_ID"]
# for key in required_secrets:
#     if key not in st.secrets:
#         st.error(f"{key} missing in Streamlit secrets")
#         st.stop()

# json_key = json.loads(st.secrets["SERVICE_ACCOUNT_JSON"])
# FILE_ID = st.secrets["FILE_ID"]
# SHEET_FILE_ID = st.secrets["SHEET_FILE_ID"]

# SCOPES = [
#     "https://www.googleapis.com/auth/drive",
#     "https://www.googleapis.com/auth/spreadsheets"
# ]

# creds = Credentials.from_service_account_info(json_key, scopes=SCOPES)
# drive_service = build("drive", "v3", credentials=creds)
# gspread_client = gspread.authorize(creds)

# # ---------------------------------------------------
# # UTIL FUNCTIONS
# # ---------------------------------------------------
# def download_excel(file_id):
#     """Download latest Excel from Google Drive (no caching)"""
#     request = drive_service.files().get_media(fileId=file_id)
#     fh = io.BytesIO()
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while not done:
#         _, done = downloader.next_chunk()
#     fh.seek(0)
#     return pd.read_excel(fh, engine="openpyxl")

# def upload_excel(file_id, df):
#     """Upload Excel to Google Drive"""
#     out = io.BytesIO()
#     df.to_excel(out, index=False, engine="openpyxl")
#     out.seek(0)
#     media = MediaIoBaseUpload(
#         out,
#         mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
#         resumable=True
#     )
#     drive_service.files().update(
#         fileId=file_id,
#         media_body=media,
#         supportsAllDrives=True
#     ).execute()

# # ---------------------------------------------------
# # LOAD DATA
# # ---------------------------------------------------
# if "df" not in st.session_state:
#     with st.spinner("Downloading Excel from Drive..."):
#         df = download_excel(FILE_ID)

#         # Add approval columns if missing
#         for col in ["APPROVAL_1", "APPROVAL_2"]:
#             if col not in df.columns:
#                 df[col] = ""

#         st.session_state.df = df.reset_index(drop=True)

# df = st.session_state.df.copy()

# # ---------------------------------------------------
# # FILTER REJECTED RECORDS (UI ONLY)
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
# # EDIT FORM
# # ---------------------------------------------------
# status_options = ["ACCEPTED", "REJECTED", ""]

# st.subheader("📂 Pending Approvals")

# with st.form("approval_form"):
#     edited_df = st.data_editor(
#         df_ui,
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
# # SAVE CHANGES
# # ---------------------------------------------------
# if submit:
#     try:
#         # Update main df
#         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2"]] = edited_df[["APPROVAL_1", "APPROVAL_2"]].values

#         # Upload to Drive
#         upload_excel(FILE_ID, df)

#         # Re-download latest Excel to reflect changes
#         df = download_excel(FILE_ID)
#         st.session_state.df = df

#         st.success("✅ Bulk approval saved successfully!")
#     except Exception as e:
#         st.error(f"Save failed: {e}")

# # ---------------------------------------------------
# # SEARCH
# # ---------------------------------------------------
# search = st.text_input("Search")
# if search:
#     mask = edited_df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
#     st.dataframe(edited_df[mask], use_container_width=True)
# else:
#     st.dataframe(edited_df, use_container_width=True)

# # ---------------------------------------------------
# # PROJECT-WISE EXPENSE SUMMARY
# # ---------------------------------------------------
# st.write("---")
# st.subheader("💼 Project-wise Highest Expense")

# sh = gspread_client.open_by_key(SHEET_FILE_ID)
# ws = sh.sheet1
# expense_df = pd.DataFrame(ws.get_all_records())

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

# st.info("⚠️ This app overwrites the Excel file. Enable backups if multiple users edit simultaneously.")

# import io
# import json
# import base64
# import pandas as pd
# import streamlit as st
# import requests
# import altair as alt

# # ---------------------------------------------------
# # PAGE CONFIG
# # ---------------------------------------------------
# st.set_page_config(
#     page_title="GitHub Excel Approval System",
#     page_icon="📝",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management</h1>", unsafe_allow_html=True)
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
# # ---------------------------------------------------
# status_options = ["ACCEPTED", "REJECTED", ""]

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

# st.info("⚠️ This app overwrites the Excel file in GitHub. Enable backups if multiple users edit simultaneously.")

# #GITHUB ---------
# import io
# import json
# import base64
# import pandas as pd
# import streamlit as st
# import requests
# import altair as alt

# # ---------------------------------------------------
# # PAGE CONFIG
# # ---------------------------------------------------
# st.set_page_config(
#     page_title="GitHub Excel Approval System",
#     page_icon="📝",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management</h1>", unsafe_allow_html=True)
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
# # ---------------------------------------------------
# status_options = ["ACCEPTED", "REJECTED", ""]

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

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management</h1>", unsafe_allow_html=True)
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
#     "GDRIVE_FILE_ID",
#     "GDRIVE_SERVICE_ACCOUNT"
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
#         st.secrets["GDRIVE_SERVICE_ACCOUNT"],
#         scopes=["https://www.googleapis.com/auth/drive"]
#     )
#     return build("drive", "v3", credentials=creds)


# def download_excel_from_drive():
#     service = get_drive_service()
#     request = service.files().get_media(fileId=st.secrets["GDRIVE_FILE_ID"])
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
# status_options = ["ACCEPTED", "REJECTED", ""]

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

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management</h1>", unsafe_allow_html=True)
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
#                 options=["", "ACCEPTED", "REJECTED"]
#             ),
#             "APPROVAL_2": st.column_config.SelectboxColumn(
#                 "APPROVAL_2",
#                 options=["", "ACCEPTED", "REJECTED"]
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

#          df.loc[df_ui.index, "ADJUSTMENT_AMOUNT"] = df_ui["ADJUSTMENT_AMOUNT"].values

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

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management</h1>", unsafe_allow_html=True)
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

#     content = base64.b64decode(r.json()["content"])
#     return pd.read_excel(io.BytesIO(content), engine="openpyxl")

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
# # INITIAL LOAD (Drive → GitHub → App)
# # ---------------------------------------------------
# if st.session_state.df is None:
#     with st.spinner("🔄 Syncing Excel..."):
#         df = download_excel_from_drive()
#         upload_excel_to_github(df)
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
# # DATA EDITOR
# # ---------------------------------------------------
# st.subheader("📂 Pending Approvals")

# with st.form("approval_form"):
#     edited_df = st.data_editor(
#         df_ui,
#         hide_index=True,
#         use_container_width=True,
#         disabled=[c for c in df_ui.columns if c not in ["APPROVAL_1", "APPROVAL_2"]],
#         column_config={
#             "APPROVAL_1": st.column_config.SelectboxColumn(
#                 "APPROVAL_1", options=["", "ACCEPTED", "REJECTED"]
#             ),
#             "APPROVAL_2": st.column_config.SelectboxColumn(
#                 "APPROVAL_2", options=["", "ACCEPTED", "REJECTED"]
#             ),
#         }
#     )

#     submit = st.form_submit_button("💾 Save Bulk Approval")

# # ---------------------------------------------------
# # SAVE (RECALCULATE → GITHUB → DRIVE)
# # ---------------------------------------------------
# # if submit:
# #     try:
# #         # Save approvals
# #         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2"]] = \
# #             edited_df[["APPROVAL_1", "APPROVAL_2"]].values

# #         # 🔥 FORCE adjustment calculation on MAIN DF
# #         df["BASIC_AMOUNT"] = pd.to_numeric(df["BASIC_AMOUNT"], errors="coerce").fillna(0)
# #         df["ADJUSTMENT_AMOUNT"] = pd.to_numeric(df["ADJUSTMENT_AMOUNT"], errors="coerce").fillna(0)

# #         mask = (
# #             (df["STATUS_MATCHED_ESTIMATION"].fillna("").str.upper() == "ESTIMATION NOT MATCHED") &
# #             (df["BASIC_AMOUNT"] != 0)
# #         )

# #         df.loc[mask, "ADJUSTMENT_AMOUNT"] = df.loc[mask, "BASIC_AMOUNT"]

# #         upload_excel_to_github(df)
# #         time.sleep(5)
# #         upload_excel_to_drive(df)

# #         st.session_state.df = df.copy()
# #         st.session_state.edited_df = None
# #         st.cache_data.clear()

# #         st.success("✅ Saved successfully. Adjustment Amount preserved.")
# #         st.rerun()

# #     except Exception as e:
# #         st.error(f"❌ Save failed: {e}")

# if submit:
#     try:
#         # ✅ Update approvals
#         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2"]] = \
#             edited_df[["APPROVAL_1", "APPROVAL_2"]].values

#         # ✅ Ensure numeric
#         df["BASIC_AMOUNT"] = pd.to_numeric(df["BASIC_AMOUNT"], errors="coerce").fillna(0)
#         df["ADJUSTMENT_AMOUNT"] = pd.to_numeric(df["ADJUSTMENT_AMOUNT"], errors="coerce").fillna(0)

#         # ✅ Apply adjustment ONLY on edited rows
#         adj_mask = (
#             df.index.isin(df_ui.index) &
#             (df["STATUS_MATCHED_ESTIMATION"].fillna("").str.upper() == "ESTIMATION NOT MATCHED") &
#             (df["BASIC_AMOUNT"] != 0)
#         )

#         df.loc[adj_mask, "ADJUSTMENT_AMOUNT"] = df.loc[adj_mask, "BASIC_AMOUNT"]

#         # ✅ Upload sequence
#         upload_excel_to_github(df)
#         time.sleep(5)
#         upload_excel_to_drive(df)

#         # ✅ Reset state
#         st.session_state.df = df.copy()
#         st.cache_data.clear()

#         st.success("✅ Saved successfully. Adjustment Amount updated correctly.")
#         st.rerun()

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

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management</h1>", unsafe_allow_html=True)
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

#     content = base64.b64decode(r.json()["content"])
#     return pd.read_excel(io.BytesIO(content), engine="openpyxl")

# def upload_excel_to_github(df):
#     out = io.BytesIO()
#     df.to_excel(out, index=False, engine="openpyxl")
#     out.seek(0)

#     content_b64 = base64.b64encode(out.read()).decode()

#     # Refresh SHA every time
#     url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
#     r_sha = requests.get(url, headers=HEADERS)
#     r_sha.raise_for_status()
#     sha = r_sha.json()["sha"]

#     payload = {
#         "message": "Updated via Streamlit Approval System",
#         "content": content_b64,
#         "sha": sha
#     }

#     r = requests.put(url, headers=HEADERS, data=json.dumps(payload))
#     r.raise_for_status()

# # ---------------------------------------------------
# # ADJUSTMENT LOGIC
# # ---------------------------------------------------
# def apply_adjustment_logic(df):
#     def clean_amount(series):
#         return (
#             series.astype(str)
#             .str.replace(",", "", regex=False)
#             .str.replace("₹", "", regex=False)
#             .str.strip()
#             .pipe(pd.to_numeric, errors="coerce")
#             .fillna(0)
#         )

#     df["BASIC_AMOUNT"] = clean_amount(df["BASIC_AMOUNT"])
#     df["ADJUSTMENT_AMOUNT"] = clean_amount(df["ADJUSTMENT_AMOUNT"])

#     mask = (
#         (df["STATUS_MATCHED_ESTIMATION"].fillna("").str.upper().str.strip() == "ESTIMATION NOT MATCHED") &
#         (df["BASIC_AMOUNT"] != 0)
#     )

#     df.loc[mask, "ADJUSTMENT_AMOUNT"] = df.loc[mask, "BASIC_AMOUNT"]

#     # Force numeric types for Excel
#     df["ADJUSTMENT_AMOUNT"] = df["ADJUSTMENT_AMOUNT"].astype(float)
#     df["BASIC_AMOUNT"] = df["BASIC_AMOUNT"].astype(float)

#     return df

# # ---------------------------------------------------
# # INITIAL LOAD (Drive → Adjustment → GitHub → App)
# # ---------------------------------------------------
# if st.session_state.df is None:
#     with st.spinner("🔄 Syncing Excel..."):
#         df = download_excel_from_drive()
#         df = apply_adjustment_logic(df)

#         # Debug
#         st.write("Max ADJUSTMENT_AMOUNT before GitHub upload:", df["ADJUSTMENT_AMOUNT"].max())

#         upload_excel_to_github(df)
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
# # DATA EDITOR
# # ---------------------------------------------------
# st.subheader("📂 Pending Approvals")

# with st.form("approval_form"):
#     edited_df = st.data_editor(
#         df_ui,
#         hide_index=True,
#         use_container_width=True,
#         disabled=[c for c in df_ui.columns if c not in ["APPROVAL_1", "APPROVAL_2"]],
#         column_config={
#             "APPROVAL_1": st.column_config.SelectboxColumn(
#                 "APPROVAL_1", options=["", "ACCEPTED", "REJECTED"]
#             ),
#             "APPROVAL_2": st.column_config.SelectboxColumn(
#                 "APPROVAL_2", options=["", "ACCEPTED", "REJECTED"]
#             ),
#         }
#     )

#     submit = st.form_submit_button("💾 Save Bulk Approval")

# # ---------------------------------------------------
# # SAVE (Adjustment → GitHub → Drive)
# # ---------------------------------------------------
# if submit:
#     try:
#         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2"]] = \
#             edited_df[["APPROVAL_1", "APPROVAL_2"]].values

#         df = apply_adjustment_logic(df)

#         # Debug
#         st.write("Max ADJUSTMENT_AMOUNT before upload:", df["ADJUSTMENT_AMOUNT"].max())

#         upload_excel_to_github(df)
#         time.sleep(5)
#         upload_excel_to_drive(df)

#         st.session_state.df = df.copy()
#         st.cache_data.clear()

#         st.success("✅ Saved successfully. Adjustment Amount updated.")
#         st.rerun()

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

# st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management</h1>", unsafe_allow_html=True)
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

#     content = base64.b64decode(r.json()["content"])
#     return pd.read_excel(io.BytesIO(content), engine="openpyxl")

# # def upload_excel_to_github(df):
# #     out = io.BytesIO()
# #     df.to_excel(out, index=False, engine="openpyxl")
# #     out.seek(0)

# #     content_b64 = base64.b64encode(out.read()).decode()

# #     # Refresh SHA every time
# #     url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
# #     r_sha = requests.get(url, headers=HEADERS)
# #     r_sha.raise_for_status()
# #     sha = r_sha.json()["sha"]

# #     payload = {
# #         "message": "Updated via Streamlit Approval System",
# #         "content": content_b64,
# #         "sha": sha
# #     }

# #     r = requests.put(url, headers=HEADERS, data=json.dumps(payload))
# #     r.raise_for_status()

# # ---------------------------------------------------
# # GITHUB FUNCTIONS (WRITE-ONLY)
# # ---------------------------------------------------
# def upload_excel_to_github(df):
#     # FORCE numeric write
#     df["BASIC_AMOUNT"] = pd.to_numeric(df["BASIC_AMOUNT"], errors="coerce").fillna(0)
#     df["ADJUSTMENT_AMOUNT"] = pd.to_numeric(df["ADJUSTMENT_AMOUNT"], errors="coerce").fillna(0)

#     out = io.BytesIO()
#     with pd.ExcelWriter(out, engine="openpyxl") as writer:
#         df.to_excel(writer, index=False)
#     out.seek(0)

#     content_b64 = base64.b64encode(out.read()).decode()

#     url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
#     r_sha = requests.get(url, headers=HEADERS)
#     r_sha.raise_for_status()

#     payload = {
#         "message": "Auto-updated adjustment amount",
#         "content": content_b64,
#         "sha": r_sha.json()["sha"]
#     }

#     r = requests.put(url, headers=HEADERS, json=payload)
#     r.raise_for_status()


# # ---------------------------------------------------
# # ADJUSTMENT LOGIC (SAFE)
# # ---------------------------------------------------
# def apply_adjustment_logic(df):
#     def clean(series):
#         return (
#             series.astype(str)
#             .str.replace(",", "", regex=False)
#             .str.replace("₹", "", regex=False)
#             .str.strip()
#             .pipe(pd.to_numeric, errors="coerce")
#             .fillna(0)
#         )

#     df["BASIC_AMOUNT"] = clean(df.get("BASIC_AMOUNT", 0))
#     df["ADJUSTMENT_AMOUNT"] = 0.0   # 🔴 FORCE RESET

#     mask = (
#         df["STATUS_MATCHED_ESTIMATION"]
#         .fillna("")
#         .str.upper()
#         .str.strip()
#         .eq("ESTIMATION NOT MATCHED")
#         & (df["BASIC_AMOUNT"] > 0)
#     )

#     df.loc[mask, "ADJUSTMENT_AMOUNT"] = df.loc[mask, "BASIC_AMOUNT"]

#     return df


# # ---------------------------------------------------
# # INITIAL LOAD (Drive → Logic → GitHub → UI)
# # ---------------------------------------------------
# if st.session_state.df is None:
#     with st.spinner("🔄 Syncing from Drive..."):
#         df = download_excel_from_drive()
#         df = apply_adjustment_logic(df)

#         upload_excel_to_github(df)   # WRITE ONLY
#         st.session_state.df = df.copy()


# # ---------------------------------------------------
# # ADJUSTMENT LOGIC
# # ---------------------------------------------------
# def apply_adjustment_logic(df):
#     def clean_amount(series):
#         return (
#             series.astype(str)
#             .str.replace(",", "", regex=False)
#             .str.replace("₹", "", regex=False)
#             .str.strip()
#             .pipe(pd.to_numeric, errors="coerce")
#             .fillna(0)
#         )

#     df["BASIC_AMOUNT"] = clean_amount(df["BASIC_AMOUNT"])
#     df["ADJUSTMENT_AMOUNT"] = clean_amount(df["ADJUSTMENT_AMOUNT"])

#     mask = (
#         (df["STATUS_MATCHED_ESTIMATION"].fillna("").str.upper().str.strip() == "ESTIMATION NOT MATCHED") &
#         (df["BASIC_AMOUNT"] != 0)
#     )

#     df.loc[mask, "ADJUSTMENT_AMOUNT"] = df.loc[mask, "BASIC_AMOUNT"]

#     # Force numeric types for Excel
#     df["ADJUSTMENT_AMOUNT"] = df["ADJUSTMENT_AMOUNT"].astype(float)
#     df["BASIC_AMOUNT"] = df["BASIC_AMOUNT"].astype(float)

#     return df

# # ---------------------------------------------------
# # INITIAL LOAD AND AUTO SYNC
# # ---------------------------------------------------
# def load_and_sync_excel():
#     """
#     1. Download Excel from Drive
#     2. Apply adjustment logic
#     3. Upload immediately to GitHub
#     4. Return updated DataFrame
#     """
#     with st.spinner("🔄 Syncing Excel from Drive and updating GitHub..."):
#         df_drive = download_excel_from_drive()
#         df_adjusted = apply_adjustment_logic(df_drive)

#         # Debug
#         st.write("Max ADJUSTMENT_AMOUNT after adjustment:", df_adjusted["ADJUSTMENT_AMOUNT"].max())

#         # Upload automatically to GitHub
#         upload_excel_to_github(df_adjusted)

#         # Optional: reload from GitHub to confirm sync
#         df_github = download_excel_from_github()

#         # Ensure APPROVAL columns exist
#         for col in ["APPROVAL_1", "APPROVAL_2"]:
#             if col not in df_github.columns:
#                 df_github[col] = ""

#         return df_github.reset_index(drop=True)

# # Load data into session state
# if st.session_state.df is None:
#     st.session_state.df = load_and_sync_excel()

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
# # DATA EDITOR
# # ---------------------------------------------------
# st.subheader("📂 Pending Approvals")

# with st.form("approval_form"):
#     edited_df = st.data_editor(
#         df_ui,
#         hide_index=True,
#         use_container_width=True,
#         disabled=[c for c in df_ui.columns if c not in ["APPROVAL_1", "APPROVAL_2"]],
#         column_config={
#             "APPROVAL_1": st.column_config.SelectboxColumn(
#                 "APPROVAL_1", options=["", "ACCEPTED", "REJECTED"]
#             ),
#             "APPROVAL_2": st.column_config.SelectboxColumn(
#                 "APPROVAL_2", options=["", "ACCEPTED", "REJECTED"]
#             ),
#         }
#     )

#     submit = st.form_submit_button("💾 Save Bulk Approval")

# # ---------------------------------------------------
# # SAVE (Adjustment → GitHub → Drive)
# # ---------------------------------------------------
# if submit:
#     try:
#         df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2"]] = \
#             edited_df[["APPROVAL_1", "APPROVAL_2"]].values

#         df = apply_adjustment_logic(df)

#         # Debug
#         st.write("Max ADJUSTMENT_AMOUNT before upload:", df["ADJUSTMENT_AMOUNT"].max())

#         upload_excel_to_github(df)
#         time.sleep(5)
#         upload_excel_to_drive(df)

#         st.session_state.df = df.copy()
#         st.cache_data.clear()

#         st.success("✅ Saved successfully. Adjustment Amount updated.")
#         st.rerun()

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

st.markdown("<h1 style='text-align:center;'>📊 Excel Approval Management</h1>", unsafe_allow_html=True)
st.write("---")

# ---------------------------------------------------
# SECRETS
# ---------------------------------------------------
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
    fh = io.BytesIO()
    request = service.files().get_media(fileId=FILE_ID)
    MediaIoBaseDownload(fh, request).next_chunk()
    fh.seek(0)
    return pd.read_excel(fh, engine="openpyxl")

def upload_excel_to_drive(df):
    service = get_drive_service()
    out = io.BytesIO()
    df.to_excel(out, index=False, engine="openpyxl")
    out.seek(0)

    media = MediaIoBaseUpload(
        out,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    service.files().update(fileId=FILE_ID, media_body=media).execute()

# ---------------------------------------------------
# GITHUB
# ---------------------------------------------------
def upload_excel_to_github(df):
    out = io.BytesIO()
    df.to_excel(out, index=False, engine="openpyxl")
    out.seek(0)

    content_b64 = base64.b64encode(out.read()).decode()

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    sha = requests.get(url, headers=HEADERS).json()["sha"]

    payload = {
        "message": "Updated adjustment amount via Streamlit",
        "content": content_b64,
        "sha": sha
    }

    r = requests.put(url, headers=HEADERS, json=payload)
    r.raise_for_status()

# ---------------------------------------------------
# ✅ ADJUSTMENT LOGIC (SINGLE SOURCE OF TRUTH)
# ---------------------------------------------------
def apply_adjustment_logic(df):
    df = df.copy()

    df["BASIC_AMOUNT"] = pd.to_numeric(df["BASIC_AMOUNT"], errors="coerce").fillna(0)
    df["ADJUSTMENT_AMOUNT"] = pd.to_numeric(df["ADJUSTMENT_AMOUNT"], errors="coerce").fillna(0)

    mask = (
        df["STATUS_MATCHED_ESTIMATION"]
        .astype(str)
        .str.upper()
        .str.strip()
        .eq("ESTIMATION NOT MATCHED")
        & (df["BASIC_AMOUNT"] > 0)
    )

    df.loc[mask, "ADJUSTMENT_AMOUNT"] = df.loc[mask, "BASIC_AMOUNT"]

    return df

# ---------------------------------------------------
# INITIAL LOAD (RUNS ONCE)
# ---------------------------------------------------
if "df" not in st.session_state:
    with st.spinner("🔄 Loading Excel from Drive..."):
        df = download_excel_from_drive()
        df = apply_adjustment_logic(df)

        # SAVE EXACT SAME DF
        upload_excel_to_github(df)
        upload_excel_to_drive(df)

        st.session_state.df = df

df = st.session_state.df

# ---------------------------------------------------
# FILTER UI (ONLY VISUAL)
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
    "Remarks", "DATE"
]

df_ui = df_ui[DISPLAY_COLUMNS]

# ---------------------------------------------------
# DATA EDITOR
# ---------------------------------------------------
st.subheader("📂 Pending Approvals")

with st.form("approval_form"):
    edited_df = st.data_editor(
        df_ui,
        hide_index=True,
        use_container_width=True,
        disabled=[c for c in df_ui.columns if c not in ["APPROVAL_1", "APPROVAL_2"]],
        column_config={
            "APPROVAL_1": st.column_config.SelectboxColumn(
                "APPROVAL_1", options=["", "ACCEPTED", "REJECTED"]
            ),
            "APPROVAL_2": st.column_config.SelectboxColumn(
                "APPROVAL_2", options=["", "ACCEPTED", "REJECTED"]
            ),
        }
    )

    submit = st.form_submit_button("💾 Save Bulk Approval")

# ---------------------------------------------------
# SAVE (SAME DF → ADJUST → SAVE)
# ---------------------------------------------------
if submit:
    try:
        df = st.session_state.df

        df.loc[df_ui.index, ["APPROVAL_1", "APPROVAL_2"]] = \
            edited_df[["APPROVAL_1", "APPROVAL_2"]].values

        df = apply_adjustment_logic(df)

        # 🔍 Verification
        st.write("Saving max adjustment:", df["ADJUSTMENT_AMOUNT"].max())

        upload_excel_to_github(df)
        upload_excel_to_drive(df)

        st.session_state.df = df

        st.success("✅ Adjustment saved correctly to GitHub & Drive")
        st.rerun()

    except Exception as e:
        st.error(f"❌ Save failed: {e}")

# ---------------------------------------------------
# SUMMARY
# ---------------------------------------------------
st.write("---")
st.info("ℹ GitHub and Google Drive are now always in sync.")

