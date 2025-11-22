import streamlit as st
import re
import time
import requests
from typing import List, Dict, Any
from urllib.parse import urlparse, parse_qs

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
# Custom CSS Theme (Copied from user's provided code)
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
    
    /* Enhanced slideshow container with centered frame layout */
    .slideshow-container {
        position: relative;
        max-width: 1400px;
        margin: 2rem auto;
        background: rgba(30, 41, 59, 0.6);
        border-radius: 1.5rem;
        padding: 3rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    /* Image frame with perfect centering */
    .image-frame {
        position: relative;
        width: 100%;
        max-width: 1200px;
        margin: 0 auto;
        background: #000;
        border-radius: 1rem;
        overflow: hidden;
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.7);
        border: 8px solid rgba(99, 102, 241, 0.3);
    }
    
    .image-frame img {
        display: block;
        width: 100%;
        height: auto;
        max-height: 70vh;
        object-fit: contain;
        background: #000;
    }
    
    /* Enhanced caption with slide counter */
    .image-caption {
        text-align: center;
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-top: 2rem;
        padding: 1.2rem 2rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.15));
        border-radius: 0.75rem;
        border: 1px solid rgba(99, 102, 241, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
    }
    
    .slide-counter {
        display: inline-block;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 2rem;
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    /* Progress bar */
    .progress-container {
        width: 100%;
        height: 8px;
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
        overflow: hidden;
        margin: 1.5rem 0;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, var(--primary-color), var(--accent));
        border-radius: 4px;
        transition: width 0.3s ease;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.6);
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
    
    /* Simplified stats container for cleaner look */
    .stats-container {
        display: flex;
        justify-content: center;
        margin: 2rem 0 1rem 0;
        flex-wrap: wrap;
        gap: 1.5rem;
    }
    
    .stat-box {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2));
        padding: 1.2rem 2.5rem;
        border-radius: 1rem;
        text-align: center;
        box-shadow: 0 5px 20px rgba(99, 102, 241, 0.2);
        border: 1px solid rgba(99, 102, 241, 0.3);
        backdrop-filter: blur(10px);
        min-width: 140px;
    }
    
    .stat-box h2 {
        color: var(--primary-color);
        font-size: 2.5rem;
        margin: 0;
        font-weight: 800;
        text-shadow: 0 2px 10px rgba(99, 102, 241, 0.4);
    }
    
    .stat-box p {
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin: 0.5rem 0 0 0;
        font-weight: 500;
    }
    
    /* Control buttons styling */
    .stButton > button {
        border-radius: 0.75rem;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 1px solid rgba(99, 102, 241, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(99, 102, 241, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------
# Utility Functions
# -----------------------

def extract_folder_id(url: str) -> str:
    """Extract folder ID from various Google Drive URL formats"""
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

@st.cache_data(show_spinner="Attempting to fetch all image file IDs from Google Drive...")
def get_all_gdrive_file_ids(folder_id: str) -> List[str]:
    """
    Attempts to fetch a comprehensive list of file IDs from a public Google Drive folder.
    
    NOTE: This is still a screen-scraping method, but it is cached to prevent
    repeated network calls and is the only way to proceed without the user's
    full list of URLs or a proper API key. The user's original code was limited
    by the amount of data Google Drive loads initially. This function will
    still face that limitation.
    
    The ultimate fix requires the user to provide the full list of URLs,
    or use the Google Drive API.
    """
    st.info("⚠️ **Warning:** This method relies on screen-scraping and may not retrieve all 400+ images if Google Drive's web interface limits the initial load. The most reliable solution is to use the Google Drive API or provide a direct list of all image URLs.")
    
    file_ids = set()
    try:
        folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(folder_url, headers=headers, timeout=30)
        response.raise_for_status()
        html_content = response.text
        
        # Pattern 1: 33-character file IDs (most common)
        ids_33 = re.findall(r'"([a-zA-Z0-9_-]{33})"', html_content)
        file_ids.update(ids_33)
        
        # Pattern 2: 28-character file IDs (alternative format)
        ids_28 = re.findall(r'"([a-zA-Z0-9_-]{28})"', html_content)
        file_ids.update(ids_28)
        
        # Pattern 3: Search for file IDs in JSON structures (longer IDs)
        json_pattern = r'\["([a-zA-Z0-9_-]{25,})"'
        json_ids = re.findall(json_pattern, html_content)
        file_ids.update(json_ids)
        
        # Remove the folder ID itself if it was mistakenly included
        file_ids.discard(folder_id)
        
        st.success(f"✅ Found {len(file_ids)} unique file IDs from the folder page.")
        return list(file_ids)
        
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Network Error: Could not access Google Drive folder. Check URL and permissions. Error: {e}")
        return []
    except Exception as e:
        st.error(f"❌ An unexpected error occurred during scraping: {e}")
        return []

def file_ids_to_image_data(file_ids: List[str]) -> List[Dict[str, Any]]:
    """Converts a list of file IDs to the structured image data format."""
    image_data = []
    for i, file_id in enumerate(file_ids):
        image_data.append({
            "name": f"Image {i+1}.jpg",
            "url": f"https://drive.google.com/uc?export=view&id={file_id}",
            "source": "gdrive",
            "file_id": file_id
        })
    return image_data

# -----------------------
# Initialize Session State
# -----------------------
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'autoplay' not in st.session_state:
    st.session_state.autoplay = False
if 'images' not in st.session_state:
    st.session_state.images = []
if 'folder_id' not in st.session_state:
    st.session_state.folder_id = ""
if 'loop_mode' not in st.session_state:
    st.session_state.loop_mode = True
if 'slideshow_speed' not in st.session_state:
    st.session_state.slideshow_speed = 5.0

# -----------------------
# Sidebar Controls
# -----------------------
with st.sidebar:
    st.header("Gallery Settings")
    
    # Input for Google Drive URL/ID
    folder_input = st.text_input(
        "Google Drive Folder URL or ID",
        key="folder_input",
        placeholder="e.g., 1LfSwuD7WxbS0ZdDeGo0hpiviUx6vMhqs"
    )
    
    if st.button("Load Gallery", use_container_width=True, type="primary"):
        try:
            folder_id = extract_folder_id(folder_input)
            st.session_state.folder_id = folder_id
            
            # Clear cache and re-run the fetching function
            get_all_gdrive_file_ids.clear()
            file_ids = get_all_gdrive_file_ids(folder_id)
            st.session_state.images = file_ids_to_image_data(file_ids)
            st.session_state.current_index = 0
            st.session_state.autoplay = False
            st.rerun()
            
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"An error occurred: {e}")

    st.markdown("---")
    
    # Slideshow Controls
    st.subheader("Slideshow Options")
    st.session_state.slideshow_speed = st.slider(
        "Slide Duration (seconds)",
        min_value=1.0,
        max_value=15.0,
        value=st.session_state.slideshow_speed,
        step=0.5
    )
    
    st.session_state.loop_mode = st.checkbox(
        "Loop Slideshow",
        value=st.session_state.loop_mode
    )
    
    show_info = st.checkbox("Show Item Details", value=True)

# -----------------------
# Main Application Logic
# -----------------------

st.markdown('<div class="main-header"><h1>Drive Slideshow Gallery</h1><p>Displaying images from Google Drive</p></div>', unsafe_allow_html=True)

images = st.session_state.images
total = len(images)

if total > 0:
    idx = st.session_state.current_index
    current_item = images[idx]
    
    # Progress Bar
    progress_percent = (idx + 1) / total
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress_percent * 100}%;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Image Display (Using st.image for robust loading)
    st.markdown('<div class="slideshow-container">', unsafe_allow_html=True)
    st.markdown('<div class="image-frame">', unsafe_allow_html=True)
    
    # Use st.image for better handling of external URLs
    st.image(
        current_item["url"],
        caption=current_item["name"],
        use_column_width="always"
    )
    
    st.markdown('</div>', unsafe_allow_html=True) # Close image-frame
    
    # Caption with Counter
    st.markdown(f"""
    <div class="image-caption">
        <span class="slide-counter">{idx + 1} / {total}</span>
        {current_item["name"]}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True) # Close slideshow-container
    
    # Navigation Controls
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1.5, 1, 1])
    
    with col1:
        if st.button("⏮️ First", use_container_width=True):
            st.session_state.current_index = 0
            st.rerun()
    
    with col2:
        if st.button("⬅️ Prev", use_container_width=True):
            if idx == 0 and st.session_state.loop_mode:
                st.session_state.current_index = total - 1
            else:
                st.session_state.current_index = max(0, idx - 1)
            st.rerun()
    
    with col3:
        if st.button("⏸️ Pause" if st.session_state.autoplay else "▶️ Play", use_container_width=True, type="primary"):
            st.session_state.autoplay = not st.session_state.autoplay
            st.rerun()
    
    with col4:
        if st.button("➡️ Next", use_container_width=True):
            if idx == total - 1 and st.session_state.loop_mode:
                st.session_state.current_index = 0
            else:
                st.session_state.current_index = min(total - 1, idx + 1)
            st.rerun()
    
    with col5:
        if st.button("⏭️ Last", use_container_width=True):
            st.session_state.current_index = total - 1
            st.rerun()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Shuffle", use_container_width=True):
            import random
            st.session_state.current_index = random.randint(0, total - 1)
            st.rerun()
    
    with col2:
        if st.button("⏹️ Stop & Reset", use_container_width=True):
            st.session_state.autoplay = False
            st.session_state.current_index = 0
            st.rerun()
    
    with col3:
        # Use a key to prevent the selectbox from resetting on rerun
        jump_to = st.selectbox(
            "Jump to slide:",
            range(1, total + 1),
            index=idx,
            key="jump_to_select",
            label_visibility="collapsed"
        )
        if jump_to != idx + 1:
            st.session_state.current_index = jump_to - 1
            st.rerun()
    
    # Show details in expander to keep view clean
    if show_info:
        with st.expander("📋 View Item Details"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Name", current_item["name"])
            with col2:
                st.metric("Source", "GOOGLE DRIVE")
            with col3:
                st.metric("Position", f"{idx + 1} of {total}")
    
    # Autoplay logic
    if st.session_state.autoplay:
        time.sleep(st.session_state.slideshow_speed)
        # If at last slide, loop back to start if loop mode is on
        if idx == total - 1 and st.session_state.loop_mode:
            st.session_state.current_index = 0
        elif idx < total - 1:
            st.session_state.current_index = idx + 1
        else:
            # At end and no loop - stop autoplay
            st.session_state.autoplay = False
        st.rerun()

else:
    # Welcome screen (Copied from user's provided code)
    st.markdown("""
    <div class="info-card">
        <h3>👋 Welcome to Drive Slideshow Gallery!</h3>
        <p>Get started by following these steps:</p>
        <ol>
            <li>🔗 Paste your Google Drive public folder URL or ID in the sidebar</li>
            <li>🚀 Click "Load Gallery" to start</li>
            <li>▶️ Use the controls to navigate or enable autoplay</li>
        </ol>
        <p><strong>Features:</strong></p>
        <ul>
            <li>✨ No authentication required</li>
            <li>☁️ Support for public Google Drive folders</li>
            <li>⏯️ Auto-play with customizable timing</li>
            <li>📊 Real-time progress tracking</li>
            <li>🎨 Beautiful dark theme with gradients</li>
            <li>🔀 Shuffle mode for random viewing</li>
            <li>🔁 Loop mode for continuous slideshow</li>
        </ul>
        <p><strong>Setup Instructions:</strong></p>
        <ul>
            <li>🔓 Ensure folder has "Anyone with the link can view" permission</li>
            <li>📂 Folder should contain image files (PNG, JPG, GIF, etc.)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo stats (Copied from user's provided code)
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
            <p>No Auth Needed</p>
        </div>
        <div class="stat-box">
            <h2>🔁</h2>
            <p>Loop Mode Available</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
