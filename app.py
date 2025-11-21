import streamlit as st
import re
import json
from typing import List
from google.oauth2 import service_account
from googleapiclient.discovery import build

# -----------------------
# Extract Folder ID
# -----------------------
def extract_folder_id(url: str) -> str:
    patterns = [
        r'/folders/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)',
        r'^([a-zA-Z0-9_-]+)$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError("Invalid folder URL")

# -----------------------
# Drive Service
# -----------------------
def get_drive_service(credentials_json):
    credentials_dict = json.loads(credentials_json)
    credentials = service_account.Credentials.from_service_account_info(
        credentials_dict,
        scopes=['https://www.googleapis.com/auth/drive.readonly']
    )
    return build('drive', 'v3', credentials=credentials)

# -----------------------
# Fetch All Images
# -----------------------
def get_all_images_from_folder(folder_url: str, credentials_json: str) -> List[dict]:
    folder_id = extract_folder_id(folder_url)
    service = get_drive_service(credentials_json)

    images = []
    page_token = None

    while True:
        results = service.files().list(
            q=f"'{folder_id}' in parents and mimeType contains 'image/' and trashed=false",
            fields="nextPageToken, files(id, name)",
            pageSize=1000,
            pageToken=page_token
        ).execute()

        for file in results.get("files", []):
            images.append({
                "name": file["name"],
                "url": f"https://drive.google.com/uc?export=view&id={file['id']}"
            })

        page_token = results.get("nextPageToken")
        if not page_token:
            break

    return images

# -----------------------
# Streamlit UI
# -----------------------
st.set_page_config(page_title="Drive Image Loader", layout="wide")

st.title("📁 Google Drive Image Loader")

folder_url = st.text_input("Google Drive Folder URL")
uploaded_file = st.file_uploader("Upload Google Service Account JSON", type=["json"])

if uploaded_file and folder_url:
    try:
        creds_json = uploaded_file.read().decode("utf-8")

        with st.spinner("Loading images..."):
            images = get_all_images_from_folder(folder_url, creds_json)

        st.success(f"Loaded {len(images)} images!")

        for img in images:
            st.image(img["url"], caption=img["name"], use_column_width=True)
            st.markdown("---")

    except Exception as e:
        st.error(str(e))
else:
    st.info("Enter folder URL and upload credentials JSON to continue.")
