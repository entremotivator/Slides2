import streamlit as st
import re

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
    
    # Display options
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
        # Grid/thumbnail view
        embed_url = f"https://drive.google.com/embeddedfolderview?id={folder_id}#grid"
    else:
        # List view
        embed_url = f"https://drive.google.com/embeddedfolderview?id={folder_id}#list"
    
    # Display the embedded Google Drive folder
    st.markdown('<div class="iframe-container">', unsafe_allow_html=True)
    
    st.components.v1.iframe(
        src=embed_url,
        height=iframe_height,
        scrolling=True
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Additional info
    st.markdown("---")
    st.markdown("""
    ### 💡 Features
    - **No Authentication Required** - View public folders directly
    - **Live Updates** - See changes to the folder in real-time
    - **Multiple Views** - Switch between grid and list modes
    - **Interactive** - Click to preview images and files
    - **Responsive** - Adjust viewer height to your preference
    """)
    
    # Direct link
    st.markdown(f"""
    ### 🔗 Direct Links
    - [Open in Google Drive]({folder_url})
    - [Grid View Embed]({embed_url})
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
