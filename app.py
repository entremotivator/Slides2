import streamlit as st
import re
import time
import os
from pathlib import Path
import requests

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
# Extract Folder ID
# -----------------------
def extract_folder_id(url: str):
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

# -----------------------
# Get Local Images
# -----------------------
def get_local_images(folder_path="public"):
    """Get image metadata from local public folder"""
    images = []
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return images
    
    extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.svg', '.ico', '.heic', '.avif')
    
    for file_path in Path(folder_path).rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in extensions:
            images.append({
                "name": file_path.name,
                "path": str(file_path),
                "source": "local"
            })
    
    return images

# -----------------------
# Get Google Drive Images (Enhanced)
# -----------------------
def get_gdrive_image_urls(folder_id: str):
    """
    Extract individual image URLs from a public Google Drive folder.
    Uses comprehensive multi-strategy scraping to fetch ALL images with aggressive extraction.
    """
    images = []
    
    try:
        st.info("🔍 Performing deep scan of Google Drive folder...")
        
        folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        # Make request with longer timeout
        response = requests.get(folder_url, headers=headers, timeout=45)
        
        if response.status_code == 200:
            html_content = response.text
            
            st.info(f"📄 Retrieved {len(html_content)} bytes of data from Drive")
            
            file_ids_found = set()
            file_metadata = {}
            
            # ============================================================
            # STRATEGY 1: Extract from JavaScript data structures
            # ============================================================
            st.info("🔎 Strategy 1: Extracting from embedded JavaScript data...")
            
            # Look for key:value file ID patterns in various JS formats
            js_patterns = [
                r'\["([a-zA-Z0-9_-]{25,})"[,\]]',  # Array format
                r'"([a-zA-Z0-9_-]{33})"',  # Standard Drive ID length
                r'\\x22([a-zA-Z0-9_-]{25,44})\\x22',  # Escaped quotes
                r'id["\']?\s*:\s*["\']([a-zA-Z0-9_-]{25,})["\']',  # Object notation
            ]
            
            for pattern in js_patterns:
                matches = re.findall(pattern, html_content)
                file_ids_found.update([m for m in matches if len(m) >= 25])
            
            # ============================================================
            # STRATEGY 2: Deep dive into _DRIVE_ivd and other data blobs
            # ============================================================
            st.info("🔎 Strategy 2: Mining Drive internal data structures...")
            
            data_patterns = [
                r'window\[\'_DRIVE_ivd\'\]\s*=\s*\'(.+?)\';',
                r'AF_initDataCallback\({[^}]*data:function\(\){return\s+(\[.+?\])',
                r'data:(\[\[.+?\]\])',
            ]
            
            for pattern in data_patterns:
                matches = re.finditer(pattern, html_content, re.DOTALL)
                for match in matches:
                    data_str = match.group(1)
                    # Extract all potential file IDs from the data blob
                    ids_in_blob = re.findall(r'["\']([a-zA-Z0-9_-]{25,44})["\']', data_str)
                    file_ids_found.update([fid for fid in ids_in_blob if len(fid) >= 25])
            
            # ============================================================
            # STRATEGY 3: Look for file metadata with MIME types
            # ============================================================
            st.info("🔎 Strategy 3: Searching for image MIME type markers...")
            
            # Find sections that mention image MIME types
            image_mime_patterns = [
                r'image/(?:jpeg|jpg|png|gif|webp|bmp|svg|tiff|heic|avif)["\'\s,\]].{0,200}?([a-zA-Z0-9_-]{25,44})',
                r'([a-zA-Z0-9_-]{25,44}).{0,200}?image/(?:jpeg|jpg|png|gif|webp|bmp)',
            ]
            
            for pattern in image_mime_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        file_ids_found.update([m for m in match if len(m) >= 25])
                    elif len(match) >= 25:
                        file_ids_found.add(match)
            
            # ============================================================
            # STRATEGY 4: Extract from thumbnail URLs
            # ============================================================
            st.info("🔎 Strategy 4: Finding thumbnail references...")
            
            thumbnail_patterns = [
                r'https?://lh3\.googleusercontent\.com/[^"\']*=s\d+',
                r'https?://drive\.google\.com/thumbnail\?id=([a-zA-Z0-9_-]{25,})',
                r'/d/([a-zA-Z0-9_-]{25,44})[/=]',
            ]
            
            for pattern in thumbnail_patterns:
                matches = re.findall(pattern, html_content)
                for match in matches:
                    if len(match) >= 25:
                        file_ids_found.add(match)
            
            # ============================================================
            # STRATEGY 5: Comprehensive regex scan (most aggressive)
            # ============================================================
            st.info("🔎 Strategy 5: Performing comprehensive ID extraction...")
            
            # Ultra-aggressive: find ALL strings that match Drive ID format
            all_potential_ids = re.findall(r'\b([a-zA-Z0-9_-]{28,44})\b', html_content)
            
            # Filter out common false positives
            false_positive_patterns = [
                r'^[A-Z]{20,}$',  # All uppercase (likely not a file ID)
                r'^[0-9]{20,}$',  # All numbers
                r'^[a-z]{20,}$',  # All lowercase
            ]
            
            for potential_id in all_potential_ids:
                if len(potential_id) >= 28 and potential_id != folder_id:
                    # Check it's not a false positive
                    is_false_positive = any(re.match(fp, potential_id) for fp in false_positive_patterns)
                    if not is_false_positive:
                        file_ids_found.add(potential_id)
            
            # Remove the folder ID itself
            file_ids_found.discard(folder_id)
            
            st.success(f"🎯 Discovered {len(file_ids_found)} potential file IDs")
            
            # ============================================================
            # VALIDATION PHASE: Verify which IDs are actually images
            # ============================================================
            st.info("✅ Validating discovered files...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_ids = len(file_ids_found)
            valid_count = 0
            skipped_count = 0
            
            # Convert to list for indexed iteration
            file_ids_list = list(file_ids_found)
            
            for idx, file_id in enumerate(file_ids_list):
                progress_bar.progress((idx + 1) / total_ids)
                status_text.text(f"🔍 Validating {idx + 1}/{total_ids} | ✅ Found: {valid_count} | ⏭️ Skipped: {skipped_count}")
                
                # Try to verify if this is an image
                try:
                    test_url = f"https://drive.google.com/uc?export=view&id={file_id}"
                    
                    # Use HEAD request for faster validation
                    head_response = requests.head(
                        test_url, 
                        timeout=8, 
                        allow_redirects=True,
                        headers={'User-Agent': headers['User-Agent']}
                    )
                    
                    content_type = head_response.headers.get('Content-Type', '').lower()
                    content_length = head_response.headers.get('Content-Length', '0')
                    
                    # Check if it's an image
                    if 'image' in content_type:
                        # Extract image format from content type
                        img_format = content_type.split('/')[-1].split(';')[0].upper()
                        size_kb = int(content_length) / 1024 if content_length.isdigit() else 0
                        
                        images.append({
                            "name": f"{img_format}_{valid_count + 1:03d}_{file_id[:12]}.{img_format.lower()}",
                            "url": test_url,
                            "source": "gdrive",
                            "file_id": file_id,
                            "content_type": content_type,
                            "size_kb": round(size_kb, 2),
                            "format": img_format
                        })
                        valid_count += 1
                    # If HEAD doesn't give content-type, try a small GET request
                    elif not content_type or 'html' not in content_type:
                        try:
                            # Try getting just first few bytes
                            get_response = requests.get(
                                test_url, 
                                timeout=8, 
                                stream=True,
                                headers={'User-Agent': headers['User-Agent']}
                            )
                            
                            # Read just first 1KB to check magic bytes
                            chunk = next(get_response.iter_content(1024), b'')
                            
                            # Check for image magic bytes
                            is_image = False
                            img_format = "UNKNOWN"
                            
                            if chunk.startswith(b'\xff\xd8\xff'):
                                is_image, img_format = True, "JPEG"
                            elif chunk.startswith(b'\x89PNG'):
                                is_image, img_format = True, "PNG"
                            elif chunk.startswith(b'GIF8'):
                                is_image, img_format = True, "GIF"
                            elif chunk.startswith(b'RIFF') and b'WEBP' in chunk[:20]:
                                is_image, img_format = True, "WEBP"
                            elif chunk.startswith(b'BM'):
                                is_image, img_format = True, "BMP"
                            elif chunk.startswith(b'<svg') or b'<SVG' in chunk[:100]:
                                is_image, img_format = True, "SVG"
                            
                            if is_image:
                                images.append({
                                    "name": f"{img_format}_{valid_count + 1:03d}_{file_id[:12]}.{img_format.lower()}",
                                    "url": test_url,
                                    "source": "gdrive",
                                    "file_id": file_id,
                                    "format": img_format,
                                    "verified": "magic_bytes"
                                })
                                valid_count += 1
                            else:
                                skipped_count += 1
                        except:
                            skipped_count += 1
                    else:
                        skipped_count += 1
                        
                except requests.Timeout:
                    # On timeout, add it anyway (we'll handle errors during display)
                    images.append({
                        "name": f"IMG_{valid_count + 1:03d}_{file_id[:12]}.jpg",
                        "url": f"https://drive.google.com/uc?export=view&id={file_id}",
                        "source": "gdrive",
                        "file_id": file_id,
                        "verified": "timeout_assumed"
                    })
                    valid_count += 1
                except Exception as e:
                    # Silent skip for validation errors
                    skipped_count += 1
                    continue
            
            progress_bar.empty()
            status_text.empty()
            
            if images:
                st.success(f"✅ Successfully loaded {len(images)} images from Google Drive!")
                st.info(f"📊 Scan Summary: {len(file_ids_found)} files discovered → {valid_count} images confirmed → {skipped_count} non-images skipped")
                
                # Show format breakdown
                formats = {}
                for img in images:
                    fmt = img.get('format', 'UNKNOWN')
                    formats[fmt] = formats.get(fmt, 0) + 1
                
                if formats:
                    format_str = " | ".join([f"{fmt}: {count}" for fmt, count in sorted(formats.items())])
                    st.info(f"🎨 Image Formats: {format_str}")
            else:
                st.warning("⚠️ No images found. Please ensure:")
                st.markdown("""
                - ✓ Folder has "Anyone with the link can view" permission
                - ✓ Folder contains image files (JPG, PNG, GIF, WEBP, etc.)
                - ✓ The folder ID is correct
                - ✓ Images are not in nested subfolders (only root level supported)
                """)
        else:
            st.error(f"❌ Could not access folder (HTTP {response.status_code})")
            st.info("💡 Make sure the folder is publicly accessible with link sharing enabled")
        
        return images
        
    except requests.Timeout:
        st.error("❌ Request timed out. The folder might be too large or network is slow.")
        st.info("💡 Try again in a moment or use a smaller folder")
        return []
    except Exception as e:
        st.error(f"❌ Error loading from Google Drive: {str(e)}")
        st.info("💡 Troubleshooting: Use just the folder ID, ensure public sharing is enabled")
        return []

# -----------------------
# Get Public Drive Images
# -----------------------
def get_public_drive_images(folder_id: str):
    """
    Get publicly accessible images from Google Drive folder.
    Works with folders that have 'Anyone with the link can view' permission.
    """
    return get_gdrive_image_urls(folder_id)

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
if 'loop_mode' not in st.session_state:
    st.session_state.loop_mode = True

# -----------------------
# Header
# -----------------------
st.markdown("""
<div class="main-header">
    <h1>🎬 Drive Slideshow Gallery</h1>
    <p>View images from local public folder and Google Drive (no auth required)</p>
</div>
""", unsafe_allow_html=True)

# -----------------------
# Sidebar Configuration
# -----------------------
with st.sidebar:
    st.markdown("## 🎨 Configuration")
    
    # Source selection
    source = st.radio(
        "📁 Image Source",
        ["Local (public folder)", "Google Drive (public folder)", "Both"],
        help="Choose where to load images from"
    )
    
    # Google Drive folder URL (if needed)
    folder_url = None
    if source in ["Google Drive (public folder)", "Both"]:
        folder_url = st.text_input(
            "🔗 Google Drive Folder URL/ID",
            value="https://drive.google.com/drive/folders/1LfSwuD7WxbS0ZdDeGo0hpiviUx6vMhqs?usp=share_link",
            placeholder="Paste your public folder link here...",
            help="Folder must have 'Anyone with the link can view' permission"
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
    
    loop_mode = st.checkbox(
        "🔁 Loop Slideshow", 
        value=st.session_state.loop_mode,
        help="Automatically restart from beginning after last slide"
    )
    st.session_state.loop_mode = loop_mode
    
    show_info = st.checkbox("ℹ️ Show Image Details", value=True)
    
    st.markdown("---")
    
    if st.session_state.images:
        st.markdown("## 📊 Gallery Stats")
        total_images = len(st.session_state.images)
        current_pos = st.session_state.current_index + 1
        
        st.metric("Total Items", total_images)
        st.metric("Current Position", f"{current_pos} of {total_images}")
        st.progress(current_pos / total_images)
        
        if st.session_state.loop_mode:
            st.success("🔁 Loop Mode: ON")
        else:
            st.info("🔁 Loop Mode: OFF")

# -----------------------
# Load Images
# -----------------------
if st.button("🚀 Load Gallery", type="primary", use_container_width=True):
    with st.spinner("🔄 Loading images..."):
        all_images = []
        
        # Load local images
        if source in ["Local (public folder)", "Both"]:
            local_imgs = get_local_images("public")
            all_images.extend(local_imgs)
            st.success(f"✅ Loaded {len(local_imgs)} images from local folder")
        
        # Load Google Drive images
        if source in ["Google Drive (public folder)", "Both"] and folder_url:
            try:
                folder_id = extract_folder_id(folder_url)
                gdrive_imgs = get_public_drive_images(folder_id)
                all_images.extend(gdrive_imgs)
            except Exception as e:
                st.error(f"❌ Error loading Google Drive: {str(e)}")
        
        st.session_state.images = all_images
        st.session_state.current_index = 0
        
        if all_images:
            st.balloons()

# -----------------------
# Slideshow Display
# -----------------------
if st.session_state.images and st.session_state.current_index < len(st.session_state.images):
    imgs = st.session_state.images
    total = len(imgs)
    idx = st.session_state.current_index
    
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-box">
            <h2>{idx + 1}/{total}</h2>
            <p>Current Slide</p>
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
    
    st.markdown('<div class="slideshow-container">', unsafe_allow_html=True)
    
    current_item = imgs[idx]
    
    st.markdown('<div class="image-frame">', unsafe_allow_html=True)
    
    if current_item["source"] == "gdrive" and "url" in current_item:
        file_id = current_item.get("file_id", "")
        
        # Try multiple Google Drive URL formats in priority order
        urls_to_try = [
            f"https://lh3.googleusercontent.com/d/{file_id}=w2000",  # Best quality
            f"https://drive.google.com/uc?export=view&id={file_id}",  # Standard view
            f"https://drive.google.com/thumbnail?id={file_id}&sz=w2000",  # Thumbnail API
            f"https://lh3.googleusercontent.com/d/{file_id}",  # CDN without size
            f"https://drive.google.com/uc?export=download&id={file_id}",  # Direct download
            f"https://drive.google.com/file/d/{file_id}/preview",  # Preview mode
        ]
        
        image_loaded = False
        last_error = None
        
        for attempt, url in enumerate(urls_to_try, 1):
            try:
                response = requests.get(url, timeout=15, allow_redirects=True, stream=True)
                content_type = response.headers.get('Content-Type', '')
                
                if response.status_code == 200 and ('image' in content_type or attempt == len(urls_to_try)):
                    from PIL import Image
                    from io import BytesIO
                    
                    img = Image.open(BytesIO(response.content))
                    
                    # Display image with format conversion for better compatibility
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Convert transparent images to RGB
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    
                    st.image(img, use_container_width=True)
                    image_loaded = True
                    break
            except Exception as e:
                last_error = str(e)
                continue
        
        if not image_loaded:
            st.error(f"❌ Unable to load image: {current_item['name']}")
            if last_error:
                st.caption(f"Error: {last_error}")
            st.info(f"💡 File ID: {file_id}")
            st.markdown(f"[📂 Open in Google Drive](https://drive.google.com/file/d/{file_id}/view)")
    else:
        # Load single local image
        try:
            st.image(
                current_item["path"],
                use_container_width=True
            )
        except Exception as e:
            st.error(f"❌ Error loading image: {current_item['name']}")

    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="image-caption">
        <span class="slide-counter">{idx + 1} / {total}</span>
        <span>{'☁️' if current_item['source'] == 'gdrive' else '📷'} {current_item["name"]}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 🎮 Slideshow Controls")
    col1, col2, col3, col4, col5 = st.columns([1.5, 1, 1, 1, 1.5])
    
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
        jump_to = st.selectbox(
            "Jump to slide:",
            range(1, total + 1),
            index=idx,
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
                st.metric("Source", current_item["source"].upper())
            with col3:
                st.metric("Position", f"{idx + 1} of {total}")
            
            # Show additional metadata for Drive images
            if current_item["source"] == "gdrive":
                col1, col2, col3 = st.columns(3)
                with col1:
                    if "format" in current_item:
                        st.metric("Format", current_item["format"])
                with col2:
                    if "size_kb" in current_item and current_item["size_kb"] > 0:
                        st.metric("Size", f"{current_item['size_kb']} KB")
                with col3:
                    st.metric("File ID", current_item.get("file_id", "N/A")[:15] + "...")
    
    # Autoplay logic
    if st.session_state.autoplay:
        time.sleep(slideshow_speed)
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
    # Welcome screen
    st.markdown("""
    <div class="info-card">
        <h3>👋 Welcome to Drive Slideshow Gallery!</h3>
        <p>Get started by following these steps:</p>
        <ol>
            <li>📁 Select your image source (local folder, Google Drive, or both)</li>
            <li>🔗 If using Google Drive, paste your public folder URL</li>
            <li>🚀 Click "Load Gallery" to start</li>
            <li>▶️ Use the controls to navigate or enable autoplay</li>
        </ol>
        <p><strong>Features:</strong></p>
        <ul>
            <li>✨ No authentication required</li>
            <li>📁 Support for local public folder</li>
            <li>☁️ Support for public Google Drive folders</li>
            <li>🔍 Advanced 5-strategy image extraction</li>
            <li>✅ Magic byte validation for accurate detection</li>
            <li>⏯️ Auto-play with customizable timing</li>
            <li>📊 Real-time progress tracking</li>
            <li>🎨 Beautiful dark theme with gradients</li>
            <li>🔀 Shuffle mode for random viewing</li>
            <li>🔁 Loop mode for continuous slideshow</li>
            <li>📈 Comprehensive format breakdown (JPEG, PNG, GIF, etc.)</li>
        </ul>
        <p><strong>Setup Instructions:</strong></p>
        <ul>
            <li>📂 Place images in the "public" folder for local viewing</li>
            <li>🔓 For Google Drive, ensure folder has "Anyone with the link can view" permission</li>
            <li>🖼️ Supports: JPG, PNG, GIF, WEBP, BMP, SVG, TIFF, HEIC, AVIF</li>
        </ul>
        <p><strong>Google Drive Extraction Strategies:</strong></p>
        <ul>
            <li>🔎 Strategy 1: JavaScript data structure mining</li>
            <li>🔎 Strategy 2: Drive internal data blob extraction</li>
            <li>🔎 Strategy 3: MIME type marker detection</li>
            <li>🔎 Strategy 4: Thumbnail URL parsing</li>
            <li>🔎 Strategy 5: Comprehensive regex pattern matching</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo stats
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
        <div class="stat-box">
            <h2>🔍</h2>
            <p>5-Strategy Scan</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------
# Footer
# -----------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-secondary); padding: 1rem;">
    <p>🎬 Drive Slideshow Gallery v2.0 | Enhanced Image Extraction</p>
    <p>Supports Local & Google Drive Sources | No Authentication Required</p>
</div>
""", unsafe_allow_html=True)
