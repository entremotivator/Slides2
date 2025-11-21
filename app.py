import streamlit as st
import re
import time

# -----------------------
# Page Configuration
# -----------------------
st.set_page_config(
    page_title="Google Drive Gallery",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# -----------------------
# Custom CSS
# -----------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main-header {
        text-align: center;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 1rem;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .iframe-container {
        background: white;
        border-radius: 1rem;
        padding: 1rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    /* Added slideshow fullscreen styles */
    .slideshow-container {
        background: black;
        border-radius: 1rem;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 600px;
    }
    
    .slideshow-image {
        max-width: 100%;
        max-height: 80vh;
        object-fit: contain;
        border-radius: 0.5rem;
    }
    
    .slide-counter {
        color: white;
        text-align: center;
        font-size: 1.2rem;
        margin-top: 1rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------
# Extract Folder ID
# -----------------------
def extract_folder_id(url: str):
    """Extract folder ID from various Google Drive URL formats"""
    patterns = [
        r'/folders/([a-zA-Z0-9_-]+)',
        r'id=([a-zA-Z0-9_-]+)',
        r'^([a-zA-Z0-9_-]+)$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_files_from_folder(folder_id: str):
    """
    Extract file IDs from a public Google Drive folder
    Note: This uses web scraping as a fallback for public folders without auth
    """
    try:
        # Use the embedded folder view URL
        url = f"https://drive.google.com/embeddedfolderview?id={folder_id}"
        
        # For demo purposes, return the file IDs you need to manually input
        # Since we can't scrape without auth, we'll let user paste file IDs
        return []
    except:
        return []

# -----------------------
# Initialize Session State
# -----------------------
if 'current_slide' not in st.session_state:
    st.session_state.current_slide = 0
if 'slideshow_active' not in st.session_state:
    st.session_state.slideshow_active = False
if 'file_ids' not in st.session_state:
    st.session_state.file_ids = []

# -----------------------
# Header
# -----------------------
st.markdown("""
<div class="main-header">
    <h1>📁 Google Drive Live Gallery</h1>
    <p style="color: rgba(255,255,255,0.9); margin-top: 0.5rem;">View your public Google Drive folder in real-time</p>
</div>
""", unsafe_allow_html=True)

# -----------------------
# Default Folder URL
# -----------------------
default_folder_url = "https://drive.google.com/drive/folders/1LfSwuD7WxbS0ZdDeGo0hpiviUx6vMhqs?usp=sharing"

# Input for folder URL (optional - user can change it)
folder_url = st.text_input(
    "Google Drive Folder URL (public)",
    value=default_folder_url,
    help="Paste a public Google Drive folder link here"
)

# Extract folder ID
folder_id = extract_folder_id(folder_url)

if folder_id:
    st.success(f"✅ Folder ID detected: `{folder_id}`")
    
    mode = st.radio(
        "Mode",
        ["Browse Folder", "Slideshow"],
        horizontal=True,
        help="Browse to explore files, or Slideshow for auto-rotating presentation"
    )
    
    if mode == "Browse Folder":
        # Original browse mode
        col1, col2 = st.columns(2)
        with col1:
            view_mode = st.selectbox(
                "View Mode",
                ["Grid View", "List View"],
                index=0
            )
        
        with col2:
            iframe_height = st.slider(
                "Viewer Height",
                min_value=400,
                max_value=1200,
                value=800,
                step=50,
                help="Adjust the height of the Drive viewer"
            )
        
        st.markdown("---")
        
        # Create embedded URL based on view mode
        if view_mode == "Grid View":
            embed_url = f"https://drive.google.com/embeddedfolderview?id={folder_id}#grid"
        else:
            embed_url = f"https://drive.google.com/embeddedfolderview?id={folder_id}#list"
        
        # Display the embedded Google Drive folder
        st.markdown('<div class="iframe-container">', unsafe_allow_html=True)
        
        st.components.v1.iframe(
            src=embed_url,
            height=iframe_height,
            scrolling=True
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        st.markdown("### 🎬 Slideshow Mode")
        
        # File IDs input
        file_ids_input = st.text_area(
            "Enter Google Drive File IDs (one per line)",
            height=150,
            help="Get file IDs from 'Share > Copy link' for each image. Paste the full URL or just the ID.",
            placeholder="https://drive.google.com/file/d/1ABC123.../view\nhttps://drive.google.com/file/d/1XYZ789.../view\nor just:\n1ABC123...\n1XYZ789..."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            rotation_speed = st.slider(
                "Rotation Speed (seconds)",
                min_value=1,
                max_value=10,
                value=3,
                help="How long each slide displays"
            )
        
        with col2:
            auto_start = st.checkbox("Auto-start slideshow", value=True)
        
        if file_ids_input:
            # Parse file IDs from input
            lines = file_ids_input.strip().split('\n')
            parsed_ids = []
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # Try to extract file ID from URL or use as-is
                match = re.search(r'/file/d/([a-zA-Z0-9_-]+)', line)
                if match:
                    parsed_ids.append(match.group(1))
                elif re.match(r'^[a-zA-Z0-9_-]+$', line):
                    parsed_ids.append(line)
            
            st.session_state.file_ids = parsed_ids
            
            if parsed_ids:
                st.success(f"✅ Found {len(parsed_ids)} files")
                
                st.markdown("---")
                
                # Slideshow controls
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    if st.button("⏮️ Previous"):
                        st.session_state.current_slide = (st.session_state.current_slide - 1) % len(parsed_ids)
                        st.rerun()
                
                with col2:
                    if st.button("⏯️ Play/Pause"):
                        st.session_state.slideshow_active = not st.session_state.slideshow_active
                        st.rerun()
                
                with col3:
                    if st.button("⏭️ Next"):
                        st.session_state.current_slide = (st.session_state.current_slide + 1) % len(parsed_ids)
                        st.rerun()
                
                with col4:
                    if st.button("🔄 Reset"):
                        st.session_state.current_slide = 0
                        st.session_state.slideshow_active = False
                        st.rerun()
                
                # Auto-start if enabled
                if auto_start and not st.session_state.slideshow_active:
                    st.session_state.slideshow_active = True
                
                # Display current slide
                current_file_id = parsed_ids[st.session_state.current_slide]
                
                st.markdown('<div class="slideshow-container">', unsafe_allow_html=True)
                
                # Use Google Drive thumbnail/preview URL for images
                image_url = f"https://drive.google.com/uc?export=view&id={current_file_id}"
                
                st.markdown(f"""
                    <div style="text-align: center;">
                        <img src="{image_url}" class="slideshow-image" />
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Slide counter
                st.markdown(f"""
                    <div class="slide-counter">
                        Slide {st.session_state.current_slide + 1} of {len(parsed_ids)}
                    </div>
                """, unsafe_allow_html=True)
                
                # Auto-advance if slideshow is active
                if st.session_state.slideshow_active:
                    time.sleep(rotation_speed)
                    st.session_state.current_slide = (st.session_state.current_slide + 1) % len(parsed_ids)
                    st.rerun()
            else:
                st.warning("⚠️ No valid file IDs found. Please enter valid Google Drive file URLs or IDs.")
        else:
            st.info("""
            **How to create a slideshow:**
            1. Open your Google Drive folder
            2. For each image, right-click and select "Get link"
            3. Make sure the file is set to "Anyone with the link can view"
            4. Copy the link and paste it in the text area above (one per line)
            5. The slideshow will automatically start with 3-second rotation
            """)
    
    # Additional info
    st.markdown("---")
    st.markdown("""
    ### 💡 Features
    - **No Authentication Required** - View public folders directly
    - **Browse Mode** - Explore your folder with grid or list view
    - **Slideshow Mode** - Full PowerPoint-style presentation with 3-second auto-rotation
    - **Live Updates** - See changes to the folder in real-time
    - **Interactive Controls** - Play, pause, navigate slides manually
    """)
    
    # Direct link
    st.markdown(f"""
    ### 🔗 Direct Links
    - [Open in Google Drive]({folder_url})
    """)
    
else:
    st.error("❌ Invalid Google Drive folder URL. Please enter a valid public folder link.")
    st.info("""
    **How to get a public folder link:**
    1. Open your Google Drive folder
    2. Right-click and select "Share"
    3. Click "Change to anyone with the link"
    4. Set permission to "Viewer"
    5. Copy the link and paste it above
    """)
