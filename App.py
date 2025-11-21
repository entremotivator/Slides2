import streamlit as st
import re
import json
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build

# -----------------------
# Page Configuration
# -----------------------
st.set_page_config(
    page_title="Drive Slideshow Gallery",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------
# Custom CSS Theme
# -----------------------
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --background-dark: #0f172a;
        --background-light: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --accent: #f59e0b;
    }
    
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
    /* Header styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        border-radius: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 40px rgba(99, 102, 241, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 3rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    
    /* Slideshow container */
    .slideshow-container {
        position: relative;
        max-width: 100%;
        margin: 2rem auto;
        background: var(--background-light);
        border-radius: 1rem;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
    }
    
    /* Image styling */
    .slideshow-image {
        border-radius: 0.75rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        transition: transform 0.3s ease;
    }
    
    .slideshow-image:hover {
        transform: scale(1.02);
    }
    
    /* Caption styling */
    .image-caption {
        text-align: center;
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-top: 1.5rem;
        padding: 1rem;
        background: rgba(99, 102, 241, 0.1);
        border-radius: 0.5rem;
        border-left: 4px solid var(--primary-color);
    }
    
    /* Progress bar */
    .progress-container {
        width: 100%;
        height: 6px;
        background: rgba(255,255,255,0.1);
        border-radius: 3px;
        overflow: hidden;
        margin: 1.5rem 0;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, var(--primary-color), var(--accent));
        border-radius: 3px;
        transition: width 0.3s ease;
    }
    
    /* Controls styling */
    .controls {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin: 2rem 0;
        padding: 1.5rem;
        background: var(--background-light);
        border-radius: 1rem;
        box-shadow: 0 5px 20px rgba(0,0,0,0.3);
    }
    
    /* Info cards */
    .info-card {
        background: var(--background-light);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 4px solid var(--primary-color);
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    
    .info-card h3 {
        color: var(--primary-color);
        margin-top: 0;
    }
    
    /* Thumbnail grid */
    .thumbnail-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
        gap: 1rem;
        margin-top: 2rem;
    }
    
    .thumbnail {
        border-radius: 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 3px solid transparent;
    }
    
    .thumbnail:hover {
        transform: scale(1.05);
        border-color: var(--primary-color);
    }
    
    .thumbnail.active {
        border-color: var(--accent);
        box-shadow: 0 0 20px var(--accent);
    }
    
    /* Stats */
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .stat-box {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        padding: 1.5rem 2rem;
        border-radius: 1rem;
        text-align: center;
        box-shadow: 0 5px 20px rgba(99, 102, 241, 0.3);
        flex: 1;
        min-width: 150px;
    }
    
    .stat-box h2 {
        color: white;
        font-size: 2.5rem;
        margin: 0;
        font-weight: 800;
    }
    
    .stat-box p {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }
</style>
""", unsafe_allow_html=True)

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
# Get Images (Enhanced)
# -----------------------
def get_images(folder_url, credentials_json):
    folder_id = extract_folder_id(folder_url)
    service = get_drive(credentials_json)

    images = []
    token = None

    while True:
        res = service.files().list(
            q=f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false",
            fields="nextPageToken, files(id, name, thumbnailLink, webContentLink, createdTime, modifiedTime, size)",
            pageSize=1000,
            pageToken=token
        ).execute()

        for f in res.get("files", []):
            file_id = f["id"]
            
            # Multi-fallback URL logic
            url = None
            if f.get("thumbnailLink"):
                url = f["thumbnailLink"].replace("=s220", "=s1600")  # Higher quality
            if not url and f.get("webContentLink"):
                url = f["webContentLink"]
            if not url:
                url = f"https://drive.google.com/uc?export=view&id={file_id}"

            images.append({
                "name": f["name"],
                "url": url,
                "id": file_id,
                "created": f.get("createdTime", "Unknown"),
                "size": f.get("size", "0")
            })

        token = res.get("nextPageToken")
        if not token:
            break

    return images

# -----------------------
# Initialize Session State
# -----------------------
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'autoplay' not in st.session_state:
    st.session_state.autoplay = False
if 'images' not in st.session_state:
    st.session_state.images = []
if 'slideshow_speed' not in st.session_state:
    st.session_state.slideshow_speed = 3

# -----------------------
# Header
# -----------------------
st.markdown("""
<div class="main-header">
    <h1>🎬 Drive Slideshow Gallery</h1>
    <p>Transform your Google Drive images into a stunning slideshow experience</p>
</div>
""", unsafe_allow_html=True)

# -----------------------
# Sidebar Configuration
# -----------------------
with st.sidebar:
    st.markdown("## 🎨 Configuration")
    
    folder_url = st.text_input(
        "📁 Google Drive Folder URL",
        placeholder="Paste your folder link here...",
        help="Enter the URL of your Google Drive folder containing images"
    )
    
    creds_file = st.file_uploader(
        "🔑 Service Account JSON",
        type=["json"],
        help="Upload your Google Cloud service account credentials"
    )
    
    st.markdown("---")
    
    st.markdown("## ⚙️ Slideshow Settings")
    
    slideshow_speed = st.slider(
        "⏱️ Slide Duration (seconds)",
        min_value=1,
        max_value=15,
        value=st.session_state.slideshow_speed,
        help="How long each image is displayed"
    )
    st.session_state.slideshow_speed = slideshow_speed
    
    transition_effect = st.selectbox(
        "✨ Transition Effect",
        ["Fade", "Slide", "Zoom", "None"],
        help="Visual effect between slides"
    )
    
    show_thumbnails = st.checkbox("🖼️ Show Thumbnail Grid", value=True)
    show_info = st.checkbox("ℹ️ Show Image Details", value=True)
    
    st.markdown("---")
    
    if st.session_state.images:
        st.markdown("## 📊 Gallery Stats")
        total_images = len(st.session_state.images)
        current_pos = st.session_state.current_index + 1
        
        st.metric("Total Images", total_images)
        st.metric("Current Position", f"{current_pos} of {total_images}")
        st.progress(current_pos / total_images)

# -----------------------
# Load Images
# -----------------------
if creds_file and folder_url:
    try:
        creds_json = creds_file.read().decode("utf-8")
        
        # Load button
        if st.button("🚀 Load Gallery", type="primary", use_container_width=True):
            with st.spinner("🔄 Loading images from Google Drive..."):
                imgs = get_images(folder_url, creds_json)
                st.session_state.images = imgs
                st.session_state.current_index = 0
                st.success(f"✅ Successfully loaded {len(imgs)} images!")
                st.balloons()

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("💡 Make sure your service account has access to the folder")

# -----------------------
# Slideshow Display
# -----------------------
if st.session_state.images:
    imgs = st.session_state.images
    total = len(imgs)
    idx = st.session_state.current_index
    
    # Stats display
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-box">
            <h2>{total}</h2>
            <p>Total Images</p>
        </div>
        <div class="stat-box">
            <h2>{idx + 1}</h2>
            <p>Current Image</p>
        </div>
        <div class="stat-box">
            <h2>{round((idx + 1) / total * 100)}%</h2>
            <p>Progress</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    progress_percentage = ((idx + 1) / total) * 100
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress_percentage}%"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Main slideshow container
    st.markdown('<div class="slideshow-container">', unsafe_allow_html=True)
    
    # Display current image
    current_img = imgs[idx]
    st.image(
        current_img["url"],
        use_container_width=True,
        output_format="auto"
    )
    
    # Image caption
    st.markdown(f"""
    <div class="image-caption">
        📷 {current_img["name"]}
    </div>
    """, unsafe_allow_html=True)
    
    # Image info
    if show_info:
        st.markdown(f"""
        <div class="info-card">
            <h3>Image Details</h3>
            <p><strong>File Name:</strong> {current_img["name"]}</p>
            <p><strong>Position:</strong> {idx + 1} of {total}</p>
            <p><strong>Image ID:</strong> {current_img["id"]}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Controls
    col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 1, 1, 1, 1])
    
    with col1:
        if st.button("⏮️ First", use_container_width=True):
            st.session_state.current_index = 0
            st.rerun()
    
    with col2:
        if st.button("⬅️ Previous", use_container_width=True):
            st.session_state.current_index = max(0, idx - 1)
            st.rerun()
    
    with col3:
        if st.button("⏸️ Pause" if st.session_state.autoplay else "▶️ Play", use_container_width=True):
            st.session_state.autoplay = not st.session_state.autoplay
            st.rerun()
    
    with col4:
        if st.button("⏹️ Stop", use_container_width=True):
            st.session_state.autoplay = False
            st.session_state.current_index = 0
            st.rerun()
    
    with col5:
        if st.button("➡️ Next", use_container_width=True):
            st.session_state.current_index = min(total - 1, idx + 1)
            st.rerun()
    
    with col6:
        if st.button("⏭️ Last", use_container_width=True):
            st.session_state.current_index = total - 1
            st.rerun()
    
    with col7:
        if st.button("🔄 Shuffle", use_container_width=True):
            import random
            st.session_state.current_index = random.randint(0, total - 1)
            st.rerun()
    
    # Thumbnail grid
    if show_thumbnails:
        st.markdown("---")
        st.markdown("### 🖼️ Thumbnail Gallery")
        
        cols_per_row = 6
        for i in range(0, total, cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                img_idx = i + j
                if img_idx < total:
                    with col:
                        if st.button(
                            f"🖼️ {img_idx + 1}",
                            key=f"thumb_{img_idx}",
                            use_container_width=True,
                            type="primary" if img_idx == idx else "secondary"
                        ):
                            st.session_state.current_index = img_idx
                            st.rerun()
    
    # Auto-advance logic
    if st.session_state.autoplay:
        time.sleep(slideshow_speed)
        st.session_state.current_index = (idx + 1) % total
        st.rerun()

else:
    # Welcome screen
    st.markdown("""
    <div class="info-card">
        <h3>👋 Welcome to Drive Slideshow Gallery!</h3>
        <p>Get started by following these steps:</p>
        <ol>
            <li>📁 Enter your Google Drive folder URL in the sidebar</li>
            <li>🔑 Upload your service account JSON credentials</li>
            <li>🚀 Click "Load Gallery" to start</li>
            <li>▶️ Use the controls to navigate or enable autoplay</li>
        </ol>
        <p><strong>Features:</strong></p>
        <ul>
            <li>✨ Smooth transitions and animations</li>
            <li>⏯️ Auto-play with customizable timing</li>
            <li>🖼️ Thumbnail grid for quick navigation</li>
            <li>📊 Real-time progress tracking</li>
            <li>🎨 Beautiful dark theme with gradients</li>
            <li>🔀 Shuffle mode for random viewing</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo stats (placeholder)
    st.markdown("""
    <div class="stats-container">
        <div class="stat-box">
            <h2>🎬</h2>
            <p>Ready to Start</p>
        </div>
        <div class="stat-box">
            <h2>∞</h2>
            <p>Unlimited Images</p>
        </div>
        <div class="stat-box">
            <h2>⚡</h2>
            <p>Fast Loading</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
