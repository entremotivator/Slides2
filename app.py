import streamlit as st
import re
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# -----------------------
# Extract Folder ID
# -----------------------
def extract_folder_id(url: str):
    patterns = [
        r'/folders/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)',
        r'^([a-zA-Z0-9_-]+)$'
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    raise ValueError("Invalid Google Drive folder link.")

# -----------------------
# Drive Client
# -----------------------
def get_drive(credentials_json):
    cred_dict = json.loads(credentials_json)
    creds = service_account.Credentials.from_service_account_info(
        cred_dict, scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    return build("drive", "v3", credentials=creds)

# -----------------------
# Get Images (Fail-safe)
# -----------------------
def get_images(folder_url, credentials_json):
    folder_id = extract_folder_id(folder_url)
    service = get_drive(credentials_json)

    images = []
    token = None

    while True:
        res = service.files().list(
            q=f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false",
            fields="nextPageToken, files(id, name, thumbnailLink, webContentLink)",
            pageSize=1000,
            pageToken=token
        ).execute()

        for f in res.get("files", []):
            file_id = f["id"]

            # multi fallback logic
            url = None

            # 1. thumbnail always loads (best fallback)
            if f.get("thumbnailLink"):
                url = f["thumbnailLink"]

            # 2. public link
            if not url and f.get("webContentLink"):
                url = f["webContentLink"]

            # 3. direct load link
            if not url:
                url = f"https://drive.google.com/uc?export=view&id={file_id}"

            images.append({
                "name": f["name"],
                "url": url
            })

        token = res.get("nextPageToken")
        if not token:
            break

    return images

# -----------------------
# UI
# -----------------------
st.title("📁 Google Drive Image Loader")

folder_url = st.text_input("Google Drive Folder URL")

creds_file = st.file_uploader("Upload Service Account JSON", type=["json"])

if creds_file and folder_url:
    try:
        creds_json = creds_file.read().decode("utf-8")

        with st.spinner("Loading images..."):
            imgs = get_images(folder_url, creds_json)

        st.success(f"Loaded {len(imgs)} images")

        for img in imgs:
            st.image(img["url"], caption=img["name"], use_column_width=True)
            st.write("---")

    except Exception as e:
        st.error(str(e))
