import streamlit as st
import re
import time
import os
from pathlib import Path

# -----------------------
# Page Configuration
# -----------------------
st.set_page_config(
    page_title="Google Drive Slideshow",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------
# Custom CSS
# -----------------------
st.markdown("""
<style>
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --background-dark: #0f172a;
        --background-light: #1e293b;
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --accent: #f59e0b;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }
    
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
    
    .slideshow-container {
        position: relative;
        max-width: 100%;
        height: 85vh;
        margin: 0 auto;
        background: rgba(30, 41, 59, 0.6);
        border-radius: 1.5rem;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(99, 102, 241, 0.2);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .image-frame {
        position: relative;
        width: 100%;
        height: 100%;
        background: #000;
        border-radius: 1rem;
        overflow: hidden;
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.7);
        border: 8px solid rgba(99, 102, 241, 0.3);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .image-frame img {
        max-width: 100%;
        max-height: 100%;
        width: auto;
        height: auto;
        object-fit: contain;
    }
    
    .image-caption {
        text-align: center;
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-top: 1.5rem;
        padding: 1rem 2rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.15));
        border-radius: 0.75rem;
        border: 1px solid rgba(99, 102, 241, 0.3);
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
        margin-right: 1rem;
    }
    
    .progress-container {
        width: 100%;
        height: 8px;
        background: rgba(255,255,255,0.1);
        border-radius: 4px;
        overflow: hidden;
        margin: 1rem 0;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, var(--primary-color), var(--accent));
        border-radius: 4px;
        transition: width 0.3s ease;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.6);
    }
    
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

FOLDER_ID = "1LfSwuD7WxbS0ZdDeGo0hpiviUx6vMhqs"
FOLDER_URL = f"https://drive.google.com/drive/folders/{FOLDER_ID}?usp=sharing"

if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'autoplay' not in st.session_state:
    st.session_state.autoplay = True  # Start with autoplay on
if 'slideshow_speed' not in st.session_state:
    st.session_state.slideshow_speed = 3
if 'file_ids' not in st.session_state:
    st.session_state.file_ids = []

# -----------------------
# Header
# -----------------------
st.markdown("""
<div class="main-header">
    <h1>🎬 Google Drive Slideshow</h1>
    <p>One-by-one fullscreen image viewer with 3-second auto-rotation</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🎨 Configuration")
    
    st.info(f"📁 **Folder:** [Open in Drive]({FOLDER_URL})")
    
    file_ids_input = st.text_area(
        "📎 Paste File IDs (one per line)",
        height=200,
        help="Get file IDs from your Google Drive files. Right-click on each image → Get link → Copy the ID",
        placeholder="1ABC123xyz...\n2DEF456uvw...\n3GHI789rst..."
    )
    
    st.markdown("---")
    
    st.markdown("## ⚙️ Settings")
    
    slideshow_speed = st.slider(
        "⏱️ Slide Duration (seconds)",
        min_value=1,
        max_value=15,
        value=st.session_state.slideshow_speed
    )
    st.session_state.slideshow_speed = slideshow_speed
    
    if st.button("🚀 Load Slideshow", type="primary", use_container_width=True):
        if file_ids_input.strip():
            lines = file_ids_input.strip().split('\n')
            file_ids = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Extract file ID from URL or use as-is
                match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', line)
                if match:
                    file_ids.append(match.group(1))
                elif re.match(r'^[a-zA-Z0-9_-]+$', line):
                    file_ids.append(line)
            
            if file_ids:
                st.session_state.file_ids = file_ids
                st.session_state.current_index = 0
                st.session_state.autoplay = True
                st.success(f"✅ Loaded {len(file_ids)} images!")
                st.rerun()
            else:
                st.error("❌ No valid file IDs found")
        else:
            st.warning("⚠️ Please paste file IDs first")

if st.session_state.file_ids:
    file_ids = st.session_state.file_ids
    total = len(file_ids)
    idx = st.session_state.current_index
    current_file_id = file_ids[idx]
    
    # Progress indicator
    progress_percentage = ((idx + 1) / total) * 100
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress_percentage}%"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Full-screen image display
    st.markdown('<div class="slideshow-container">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="image-frame">
        <img src="https://drive.google.com/uc?export=view&id={current_file_id}" alt="Slide {idx + 1}" />
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Caption with counter
    st.markdown(f"""
    <div class="image-caption">
        <span class="slide-counter">{idx + 1} / {total}</span>
        <span>Image from Google Drive</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Controls
    st.markdown("### 🎮 Controls")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("⏮️ First", use_container_width=True):
            st.session_state.current_index = 0
            st.rerun()
    
    with col2:
        if st.button("⬅️ Prev", use_container_width=True):
            st.session_state.current_index = (idx - 1) % total
            st.rerun()
    
    with col3:
        if st.button("⏸️ Pause" if st.session_state.autoplay else "▶️ Play", use_container_width=True, type="primary"):
            st.session_state.autoplay = not st.session_state.autoplay
            st.rerun()
    
    with col4:
        if st.button("➡️ Next", use_container_width=True):
            st.session_state.current_index = (idx + 1) % total
            st.rerun()
    
    with col5:
        if st.button("⏭️ Last", use_container_width=True):
            st.session_state.current_index = total - 1
            st.rerun()
    
    # Auto-advance with configured speed
    if st.session_state.autoplay:
        time.sleep(st.session_state.slideshow_speed)
        st.session_state.current_index = (idx + 1) % total
        st.rerun()

else:
    st.markdown("""
    <div style="max-width: 800px; margin: 2rem auto; background: rgba(30, 41, 59, 0.6); padding: 2rem; border-radius: 1rem; border: 1px solid rgba(99, 102, 241, 0.2);">
        <h3 style="color: var(--primary-color);">👋 Welcome!</h3>
        <p style="color: var(--text-primary);">This slideshow displays images one-by-one from your Google Drive folder.</p>
        
        <h4 style="color: var(--primary-color); margin-top: 1.5rem;">📋 How to Get Started:</h4>
        <ol style="color: var(--text-primary);">
            <li>Open your <a href="https://drive.google.com/drive/folders/1LfSwuD7WxbS0ZdDeGo0hpiviUx6vMhqs?usp=sharing" target="_blank">Google Drive folder</a></li>
            <li>For each image you want in the slideshow:
                <ul>
                    <li>Right-click the file → Share → Copy link</li>
                    <li>Extract the file ID from the URL (the part after /d/ and before /view)</li>
                    <li>Example: https://drive.google.com/file/d/<strong>1ABC123xyz</strong>/view</li>
                </ul>
            </li>
            <li>Paste all file IDs in the sidebar (one per line)</li>
            <li>Click "Load Slideshow" to start!</li>
        </ol>
        
        <h4 style="color: var(--primary-color); margin-top: 1.5rem;">✨ Features:</h4>
        <ul style="color: var(--text-primary);">
            <li>🖼️ Full-screen one-by-one display</li>
            <li>⏯️ Auto-play with 3-second rotation (customizable 1-15 seconds)</li>
            <li>🔓 No authentication required</li>
            <li>📊 Progress tracking</li>
            <li>🎮 Manual navigation controls</li>
        </ul>
        
        <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(99, 102, 241, 0.1); border-radius: 0.5rem; border-left: 4px solid var(--primary-color);">
            <strong style="color: var(--primary-color);">💡 Tip:</strong>
            <span style="color: var(--text-primary);"> Make sure your Google Drive files have "Anyone with the link can view" permission enabled.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
