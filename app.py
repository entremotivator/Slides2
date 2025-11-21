import streamlit as st
import re

# Page configuration for ultimate immersive experience
st.set_page_config(
    page_title="Google Drive Public Slideshow",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful modern dark theme
st.markdown("""
<style>
    :root {
        --primary: #6366f1;
        --secondary: #8b5cf6;
        --bg-dark: #0f172a;
        --bg-light: #1e293b;
        --text-main: #f1f5f9;
        --text-alt: #94a3b8;
        --accent: #f59e0b;
    }
    .stApp { background: linear-gradient(135deg, var(--bg-dark) 0%, var(--bg-light) 100%); }
    .main-header { text-align:center; background:linear-gradient(135deg,var(--primary),var(--secondary)); margin-bottom:2rem; padding:2rem 0 1rem 0; border-radius:1rem; box-shadow:0 10px 40px rgba(99,102,241,.3);}
    .main-header h1 { color:white; font-size:3rem; font-weight:900; text-shadow:2px 2px 8px rgba(0,0,0,.25);}
    .slideshow-container { max-width:1400px; margin:2rem auto; background:rgba(30,41,59,.7); border-radius:2rem; padding:3rem; box-shadow:0 20px 60px rgba(0,0,0,.4); border:1px solid rgba(99,102,241,.28);}
    .iframe-frame { border-radius:1.2rem; overflow:hidden; background:#fff; }
    .info-card { background:var(--bg-light); border-radius:1.2rem; padding:2rem; box-shadow:0 6px 18px rgba(0,0,0,.24); margin-top:1.5rem;}
    .stat-container { display:flex; justify-content:center; gap:2rem; margin:2rem 0;}
    .stat-box { background:linear-gradient(135deg,rgba(99,102,241,.18),rgba(139,92,246,.15)); border-radius:1rem; box-shadow: 0 2px 18px rgba(99,102,241,.12); min-width:130px; padding:1.4rem 2.4rem; text-align:center;}
    .stat-box h2 { color: var(--primary); font-size:2.3rem; font-weight:800; margin:0 0 .5rem 0;}
    .stat-box p { color:var(--text-alt); font-size:1rem; margin:0; font-weight:500;}
</style>
""", unsafe_allow_html=True)

# Google Drive public folder ID
drive_folder_url = "https://drive.google.com/drive/folders/1LfSwuD7WxbS0ZdDeGo0hpiviUx6vMhqs?usp=sharing"
match = re.search(r'/folders/([a-zA-Z0-9_-]+)', drive_folder_url)
folder_id = match.group(1) if match else "1LfSwuD7WxbS0ZdDeGo0hpiviUx6vMhqs"
embed_url = f"https://drive.google.com/embeddedfolderview?id={folder_id}#grid"

# Main header
st.markdown("""
<div class="main-header">
    <h1>🖼️ Public Google Drive Gallery</h1>
    <p>Browse all images directly from this shared folder—no login, upload, or configuration required!</p>
</div>
""", unsafe_allow_html=True)

# Info Card: User Instructions, Features, and Tips
st.markdown("""
<div class="info-card">
    <h3>👋 How To Use</h3>
    <ol>
        <li>🌐 View the full gallery below (images & folders are public)</li>
        <li>🔗 Click on any image thumbnail for a fullscreen preview</li>
        <li>⏯️ Use built-in Drive navigation for paging and sorting</li>
        <li>📎 <a href="https://drive.google.com/drive/folders/1LfSwuD7WxbS0ZdDeGo0hpiviUx6vMhqs?usp=sharing" target="_blank">Open folder in Google Drive for uploads or edits</a></li>
    </ol>
    <br>
    <strong>Features:</strong>
    <ul>
        <li>✨ True public access—no authentication or upload needed</li>
        <li>☁️ Unlimited images and subfolders</li>
        <li>🖼️ Native slideshow/grid via Drive interface</li>
        <li>🌙 Beautiful dark theming, responsive and secure</li>
        <li>🛠️ Easily extendable for custom thumbnail, link, or info overlays</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# Gallery Stats
st.markdown("""
<div class="stat-container">
    <div class="stat-box">
        <h2>🎬</h2><p>Google Drive Embedded</p>
    </div>
    <div class="stat-box">
        <h2>∞</h2><p>Unlimited Images</p>
    </div>
    <div class="stat-box">
        <h2>🔓</h2><p>No Login Needed</p>
    </div>
</div>
""", unsafe_allow_html=True)

# SLIDESHOW: Directly use embedded folder view for live updates and full navigation:
st.markdown(f"""
<div class="slideshow-container">
    <div class="iframe-frame">
        <iframe src="{embed_url}" width="100%" height="750" frameborder="0"></iframe>
    </div>
</div>
""", unsafe_allow_html=True)

# Extra Guidance and Troubleshooting
with st.expander("ℹ️ Folder Info & Troubleshooting"):
    st.write("This gallery loads all content from the public Drive folder.")
    st.write("To add images, open the Google Drive folder and drag/upload files; changes are instantly visible.")
    st.write("If gallery isn't loading, ensure folder permissions are set to 'Anyone with link can view'. Image thumbnails, preview, and sorting are managed natively by Google Drive for best performance.")

# Extendable Features You Can Add:
# - Show custom info or overlays for each thumbnail
# - Add sharing/copy/preview links alongside images
# - Integrate advanced drive picker (see official Streamlit components)[web:29][web:28]
# - Support search/filter by file name, type, or Drive tags
# - Add image detail/metadata via embedded panels

# This design uses ONLY the public folder, is robust, instantly updates, and requires no programming changes if new images are added—making it ideal for collaborative sharing, teaching, platform demos, or quick prototyping[web:29][web:9][web:27].
