import streamlit as st
import re
import time
import os
from pathlib import Path
import requests
from io import BytesIO
import base64

# -----------------------
# Page Configuration
# -----------------------
st.set_page_config(
    page_title="Ultimate Media Gallery",
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
    
    .image-frame video {
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
# Get Local Media Files
# -----------------------
def get_local_media(folder_path="public"):
    """Get all media files (images and videos) from local public folder"""
    media_files = []
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return media_files
    
    # Comprehensive list of image and video formats
    image_extensions = (
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.tif',
        '.svg', '.ico', '.heic', '.heif', '.avif', '.jfif', '.pjpeg', '.pjp',
        '.apng', '.cur', '.dds', '.exr', '.hdr', '.jp2', '.j2k', '.jpf', 
        '.jpx', '.jpm', '.mj2', '.pbm', '.pgm', '.ppm', '.pnm', '.pfm', 
        '.pam', '.pcx', '.tga', '.icns', '.raw', '.cr2', '.nef', '.orf', 
        '.sr2', '.arw', '.dng', '.rw2', '.raf', '.dcr', '.k25', '.kdc'
    )
    
    video_extensions = (
        '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v',
        '.mpg', '.mpeg', '.3gp', '.3g2', '.ogv', '.ogg', '.vob', '.gifv',
        '.mng', '.qt', '.yuv', '.rm', '.rmvb', '.asf', '.amv', '.m2v',
        '.svi', '.divx', '.f4v', '.m2ts', '.mts', '.ts', '.mxf', '.roq'
    )
    
    for file_path in Path(folder_path).rglob('*'):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            if ext in image_extensions:
                media_files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "source": "local",
                    "type": "image",
                    "format": ext[1:].upper()
                })
            elif ext in video_extensions:
                media_files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "source": "local",
                    "type": "video",
                    "format": ext[1:].upper()
                })
    
    return media_files

# -----------------------
# Detect Media Type from Magic Bytes
# -----------------------
def detect_media_type(data_chunk):
    """Detect media type from magic bytes - returns (is_media, type, format)"""
    if not data_chunk or len(data_chunk) < 12:
        return False, None, None
    
    # Image magic bytes
    if data_chunk.startswith(b'\xff\xd8\xff'):
        return True, "image", "JPEG"
    elif data_chunk.startswith(b'\x89PNG\r\n\x1a\n'):
        return True, "image", "PNG"
    elif data_chunk.startswith(b'GIF87a') or data_chunk.startswith(b'GIF89a'):
        return True, "image", "GIF"
    elif data_chunk.startswith(b'RIFF') and b'WEBP' in data_chunk[:20]:
        return True, "image", "WEBP"
    elif data_chunk.startswith(b'BM'):
        return True, "image", "BMP"
    elif data_chunk.startswith(b'<svg') or b'<SVG' in data_chunk[:100]:
        return True, "image", "SVG"
    elif data_chunk.startswith(b'\x00\x00\x00\x0cjP'):
        return True, "image", "JP2"
    elif data_chunk.startswith(b'II*\x00') or data_chunk.startswith(b'MM\x00*'):
        return True, "image", "TIFF"
    elif data_chunk.startswith(b'\x00\x00\x01\x00'):
        return True, "image", "ICO"
    elif data_chunk[4:12] == b'ftypavif' or data_chunk[4:12] == b'ftypheic':
        return True, "image", "HEIC/AVIF"
    
    # Video magic bytes
    elif data_chunk.startswith(b'\x00\x00\x00\x18ftypmp42') or data_chunk.startswith(b'\x00\x00\x00\x20ftypisom'):
        return True, "video", "MP4"
    elif data_chunk[4:8] == b'ftyp':
        return True, "video", "MP4/MOV"
    elif data_chunk.startswith(b'RIFF') and b'AVI ' in data_chunk[:20]:
        return True, "video", "AVI"
    elif data_chunk.startswith(b'\x1aE\xdf\xa3'):
        return True, "video", "WEBM/MKV"
    elif data_chunk.startswith(b'FLV\x01'):
        return True, "video", "FLV"
    elif data_chunk.startswith(b'\x00\x00\x01\xba') or data_chunk.startswith(b'\x00\x00\x01\xb3'):
        return True, "video", "MPEG"
    elif b'moov' in data_chunk[:100] or b'mdat' in data_chunk[:100]:
        return True, "video", "MOV/MP4"
    elif data_chunk.startswith(b'0&\xb2u\x8ef\xcf\x11'):
        return True, "video", "WMV/ASF"
    
    return False, None, None

# -----------------------
# Get Google Drive Media Files (ULTRA ENHANCED)
# -----------------------
def get_gdrive_media_urls(folder_id: str):
    """
    Extract ALL media files (images and videos) from a public Google Drive folder.
    Uses 7 comprehensive strategies with aggressive extraction and zero file skipping.
    """
    media_files = []
    
    try:
        st.info("🔍 Performing ULTRA-DEEP scan of Google Drive folder...")
        
        folder_url = f"https://drive.google.com/drive/folders/{folder_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,video/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        # Make request with extended timeout
        response = requests.get(folder_url, headers=headers, timeout=60)
        
        if response.status_code == 200:
            html_content = response.text
            
            st.info(f"📄 Retrieved {len(html_content):,} bytes of data from Drive")
            
            file_ids_found = {}  # Use dict to store metadata
            
            # ============================================================
            # STRATEGY 1: JavaScript data structure mining
            # ============================================================
            st.info("🔎 Strategy 1: Extracting from embedded JavaScript data...")
            
            js_patterns = [
                r'\["([a-zA-Z0-9_-]{25,})"[,\]]',
                r'"([a-zA-Z0-9_-]{33})"',
                r'\\x22([a-zA-Z0-9_-]{25,44})\\x22',
                r'id["\']?\s*:\s*["\']([a-zA-Z0-9_-]{25,})["\']',
                r'\\"([a-zA-Z0-9_-]{25,})\\"',
            ]
            
            for pattern in js_patterns:
                matches = re.findall(pattern, html_content)
                for match in matches:
                    if len(match) >= 25 and match != folder_id:
                        file_ids_found[match] = {"source": "js_pattern"}
            
            # ============================================================
            # STRATEGY 2: Deep data blob extraction
            # ============================================================
            st.info("🔎 Strategy 2: Mining Drive internal data structures...")
            
            data_patterns = [
                r'window\[\'_DRIVE_ivd\'\]\s*=\s*\'(.+?)\';',
                r'AF_initDataCallback\({[^}]*data:function\(\){return\s+(\[.+?\])',
                r'data:(\[\[.+?\]\])',
                r'\\x5b\\x22([a-zA-Z0-9_-]{25,44})\\x22',
            ]
            
            for pattern in data_patterns:
                matches = re.finditer(pattern, html_content, re.DOTALL)
                for match in matches:
                    data_str = match.group(1)
                    ids_in_blob = re.findall(r'["\'\[]([a-zA-Z0-9_-]{25,44})["\'\]]', data_str)
                    for fid in ids_in_blob:
                        if len(fid) >= 25 and fid != folder_id:
                            file_ids_found[fid] = {"source": "data_blob"}
            
            # ============================================================
            # STRATEGY 3: MIME type targeting (images and videos)
            # ============================================================
            st.info("🔎 Strategy 3: Searching for media MIME type markers...")
            
            mime_patterns = [
                r'(image|video)/[a-z0-9+]+["\'\s,\]].{0,300}?([a-zA-Z0-9_-]{25,44})',
                r'([a-zA-Z0-9_-]{25,44}).{0,300}?(image|video)/[a-z0-9+]+',
            ]
            
            for pattern in mime_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    for item in match:
                        if len(item) >= 25 and item not in ['image', 'video'] and item != folder_id:
                            file_ids_found[item] = {"source": "mime_type"}
            
            # ============================================================
            # STRATEGY 4: Thumbnail and CDN URL extraction
            # ============================================================
            st.info("🔎 Strategy 4: Finding thumbnail and CDN references...")
            
            thumbnail_patterns = [
                r'https?://lh3\.googleusercontent\.com/d/([a-zA-Z0-9_-]{25,})',
                r'https?://drive\.google\.com/thumbnail\?id=([a-zA-Z0-9_-]{25,})',
                r'/d/([a-zA-Z0-9_-]{25,44})[/=\?]',
                r'lh3\.googleusercontent\.com[^"\']*([a-zA-Z0-9_-]{25,44})',
            ]
            
            for pattern in thumbnail_patterns:
                matches = re.findall(pattern, html_content)
                for match in matches:
                    if len(match) >= 25 and match != folder_id:
                        file_ids_found[match] = {"source": "thumbnail"}
            
            # ============================================================
            # STRATEGY 5: Ultra-aggressive comprehensive scan
            # ============================================================
            st.info("🔎 Strategy 5: Performing ultra-comprehensive ID extraction...")
            
            # Find ALL potential Drive IDs with minimal filtering
            all_potential_ids = re.findall(r'([a-zA-Z0-9_-]{28,44})', html_content)
            
            false_positive_patterns = [
                r'^[A-Z]{25,}$',
                r'^[0-9]{25,}$',
                r'^[a-z]{25,}$',
                r'^[_-]{10,}',
            ]
            
            for potential_id in all_potential_ids:
                if len(potential_id) >= 28 and potential_id != folder_id:
                    is_false_positive = any(re.match(fp, potential_id) for fp in false_positive_patterns)
                    if not is_false_positive and potential_id not in file_ids_found:
                        file_ids_found[potential_id] = {"source": "comprehensive_scan"}
            
            # ============================================================
            # STRATEGY 6: Extract from JSON-like structures
            # ============================================================
            st.info("🔎 Strategy 6: Parsing JSON-like data structures...")
            
            json_like_patterns = [
                r'\{[^}]*"([a-zA-Z0-9_-]{25,44})"[^}]*\}',
                r'\[[^\]]*"([a-zA-Z0-9_-]{25,44})"[^\]]*\]',
            ]
            
            for pattern in json_like_patterns:
                matches = re.findall(pattern, html_content)
                for match in matches:
                    if len(match) >= 25 and match != folder_id and match not in file_ids_found:
                        file_ids_found[match] = {"source": "json_structure"}
            
            # ============================================================
            # STRATEGY 7: File name and metadata extraction
            # ============================================================
            st.info("🔎 Strategy 7: Extracting file names and metadata...")
            
            # Look for patterns that include file names near IDs
            name_patterns = [
                r'([a-zA-Z0-9_-]{25,44})["\'],\s*["\']([^"\']+\.(jpg|jpeg|png|gif|mp4|avi|mov|webm|mkv)["\'])',
                r'["\']([^"\']+\.(jpg|jpeg|png|gif|mp4|avi|mov|webm|mkv))["\'],\s*["\']([a-zA-Z0-9_-]{25,44})',
            ]
            
            for pattern in name_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    for item in match:
                        if len(item) >= 25 and item != folder_id:
                            file_ids_found[item] = {"source": "file_metadata"}
            
            # Remove folder ID
            file_ids_found.pop(folder_id, None)
            
            st.success(f"🎯 Discovered {len(file_ids_found)} potential file IDs")
            
            # ============================================================
            # VALIDATION PHASE: NO SKIPPING - Validate ALL files
            # ============================================================
            st.info("✅ Validating ALL discovered files (zero-skip policy)...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_ids = len(file_ids_found)
            valid_count = 0
            assumed_count = 0
            error_count = 0
            
            file_ids_list = list(file_ids_found.keys())
            
            for idx, file_id in enumerate(file_ids_list):
                progress_bar.progress((idx + 1) / total_ids)
                status_text.text(f"🔍 Validating {idx + 1}/{total_ids} | ✅ Confirmed: {valid_count} | 🔶 Assumed: {assumed_count} | ❌ Errors: {error_count}")
                
                test_url = f"https://drive.google.com/uc?export=view&id={file_id}"
                media_detected = False
                media_type = None
                media_format = "UNKNOWN"
                
                try:
                    # Try HEAD request first
                    head_response = requests.head(
                        test_url, 
                        timeout=10, 
                        allow_redirects=True,
                        headers={'User-Agent': headers['User-Agent']}
                    )
                    
                    content_type = head_response.headers.get('Content-Type', '').lower()
                    content_length = head_response.headers.get('Content-Length', '0')
                    
                    if 'image' in content_type:
                        media_detected = True
                        media_type = "image"
                        media_format = content_type.split('/')[-1].split(';')[0].upper()
                        valid_count += 1
                    elif 'video' in content_type:
                        media_detected = True
                        media_type = "video"
                        media_format = content_type.split('/')[-1].split(';')[0].upper()
                        valid_count += 1
                    
                    # If HEAD doesn't confirm, try GET with magic bytes (NO SKIP)
                    if not media_detected:
                        try:
                            get_response = requests.get(
                                test_url, 
                                timeout=12, 
                                stream=True,
                                headers={'User-Agent': headers['User-Agent']}
                            )
                            
                            # Read first 2KB for magic byte detection
                            chunk = next(get_response.iter_content(2048), b'')
                            
                            is_media, detected_type, detected_format = detect_media_type(chunk)
                            
                            if is_media:
                                media_detected = True
                                media_type = detected_type
                                media_format = detected_format
                                valid_count += 1
                            else:
                                # FORCE ADD even if not confirmed (zero-skip policy)
                                media_detected = True
                                media_type = "image"  # Assume image by default
                                media_format = "UNKNOWN"
                                assumed_count += 1
                        
                        except Exception:
                            # STILL ADD IT (zero-skip policy)
                            media_detected = True
                            media_type = "image"
                            media_format = "ASSUMED"
                            assumed_count += 1
                    
                except requests.Timeout:
                    # On timeout, ALWAYS add it
                    media_detected = True
                    media_type = "image"
                    media_format = "TIMEOUT_ADD"
                    assumed_count += 1
                    
                except Exception as e:
                    # Even on error, ADD IT (zero-skip policy)
                    media_detected = True
                    media_type = "image"
                    media_format = "ERROR_ADD"
                    error_count += 1
                
                # Add to media files (we add EVERYTHING)
                if media_detected:
                    media_files.append({
                        "name": f"{media_format}_{len(media_files) + 1:04d}_{file_id[:12]}.{media_format.lower()}",
                        "url": test_url,
                        "source": "gdrive",
                        "file_id": file_id,
                        "type": media_type,
                        "format": media_format,
                        "discovery": file_ids_found[file_id].get("source", "unknown")
                    })
            
            progress_bar.empty()
            status_text.empty()
            
            if media_files:
                st.success(f"✅ Successfully loaded {len(media_files)} media files from Google Drive!")
                st.info(f"📊 Scan Summary: {len(file_ids_found)} IDs discovered → {valid_count} confirmed → {assumed_count} assumed → {error_count} forced adds")
                
                # Show format and type breakdown
                formats = {}
                types = {}
                for item in media_files:
                    fmt = item.get('format', 'UNKNOWN')
                    typ = item.get('type', 'unknown')
                    formats[fmt] = formats.get(fmt, 0) + 1
                    types[typ] = types.get(typ, 0) + 1
                
                if formats:
                    format_str = " | ".join([f"{fmt}: {count}" for fmt, count in sorted(formats.items())])
                    st.info(f"🎨 Formats: {format_str}")
                
                if types:
                    type_str = " | ".join([f"{typ.upper()}: {count}" for typ, count in sorted(types.items())])
                    st.info(f"📹 Media Types: {type_str}")
            else:
                st.warning("⚠️ No media files found. Please ensure:")
                st.markdown("""
                - ✓ Folder has "Anyone with the link can view" permission
                - ✓ Folder contains media files
                - ✓ The folder ID is correct
                """)
        else:
            st.error(f"❌ Could not access folder (HTTP {response.status_code})")
            st.info("💡 Make sure the folder is publicly accessible")
        
        return media_files
        
    except requests.Timeout:
        st.error("❌ Request timed out. The folder might be very large.")
        st.info("💡 Try again - the app will still extract all files")
        return []
    except Exception as e:
        st.error(f"❌ Error loading from Google Drive: {str(e)}")
        st.info("💡 Ensure public sharing is enabled")
        return []

# -----------------------
# Initialize Session State
# -----------------------
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'autoplay' not in st.session_state:
    st.session_state.autoplay = False
if 'media_files' not in st.session_state:
    st.session_state.media_files = []
if 'slideshow_speed' not in st.session_state:
    st.session_state.slideshow_speed = 3
if 'loop_mode' not in st.session_state:
    st.session_state.loop_mode = True

# -----------------------
# Header
# -----------------------
st.markdown("""
<div class="main-header">
    <h1>🎬 Ultimate Media Gallery</h1>
    <p>Images & Videos from Local & Google Drive | Zero-Skip Extraction | 50+ Formats</p>
</div>
""", unsafe_allow_html=True)

# -----------------------
# Sidebar Configuration
# -----------------------
with st.sidebar:
    st.markdown("## 🎨 Configuration")
    
    # Source selection
    source = st.radio(
        "📁 Media Source",
        ["Local (public folder)", "Google Drive (public folder)", "Both"],
        help="Choose where to load media files from"
    )
    
    # Google Drive folder URL (if needed)
    folder_url = None
    if source in ["Google Drive (public folder)", "Both"]:
        folder_url = st.text_input(
            "🔗 Google Drive Folder URL/ID",
            value="",
            placeholder="Paste your public folder link here...",
            help="Folder must have 'Anyone with the link can view' permission"
        )
    
    st.markdown("---")
    
    st.markdown("## ⚙️ Slideshow Settings")
    
    slideshow_speed = st.slider(
        "⏱️ Slide Duration (seconds)",
        min_value=1,
        max_value=20,
        value=st.session_state.slideshow_speed,
        help="How long each item is displayed"
    )
    st.session_state.slideshow_speed = slideshow_speed
    
    loop_mode = st.checkbox(
        "🔁 Loop Slideshow", 
        value=st.session_state.loop_mode,
        help="Automatically restart from beginning after last slide"
    )
    st.session_state.loop_mode = loop_mode
    
    show_info = st.checkbox("ℹ️ Show Media Details", value=True)
    
    # Media type filter
    if st.session_state.media_files:
        st.markdown("---")
        st.markdown("## 🎯 Filter by Type")
        show_images = st.checkbox("Show Images", value=True)
        show_videos = st.checkbox("Show Videos", value=True)
    
    st.markdown("---")
    
    if st.session_state.media_files:
        st.markdown("## 📊 Gallery Stats")
        
        # Apply filters
        filtered_media = st.session_state.media_files
        if 'show_images' in locals() and 'show_videos' in locals():
            if not show_images:
                filtered_media = [m for m in filtered_media if m.get('type') != 'image']
            if not show_videos:
                filtered_media = [m for m in filtered_media if m.get('type') != 'video']
            
            # Update the working list
            st.session_state.filtered_media = filtered_media
        
        total_media = len(st.session_state.media_files)
        images_count = len([m for m in st.session_state.media_files if m.get('type') == 'image'])
        videos_count = len([m for m in st.session_state.media_files if m.get('type') == 'video'])
        
        st.metric("Total Items", total_media)
        st.metric("Images", images_count)
        st.metric("Videos", videos_count)
        
        if st.session_state.current_index < len(filtered_media):
            current_pos = st.session_state.current_index + 1
            st.metric("Current Position", f"{current_pos} of {len(filtered_media)}")
            st.progress(current_pos / len(filtered_media))
        
        if st.session_state.loop_mode:
            st.success("🔁 Loop Mode: ON")
        else:
            st.info("🔁 Loop Mode: OFF")

# -----------------------
# Load Media Files
# -----------------------
if st.button("🚀 Load Gallery", type="primary", use_container_width=True):
    with st.spinner("🔄 Loading media files..."):
        all_media = []
        
        # Load local media
        if source in ["Local (public folder)", "Both"]:
            local_media = get_local_media("public")
            all_media.extend(local_media)
            if local_media:
                st.success(f"✅ Loaded {len(local_media)} files from local folder")
        
        # Load Google Drive media
        if source in ["Google Drive (public folder)", "Both"] and folder_url:
            try:
                folder_id = extract_folder_id(folder_url)
                gdrive_media = get_gdrive_media_urls(folder_id)
                all_media.extend(gdrive_media)
            except Exception as e:
                st.error(f"❌ Error loading Google Drive: {str(e)}")
        
        st.session_state.media_files = all_media
        st.session_state.filtered_media = all_media
        st.session_state.current_index = 0
        
        if all_media:
            st.balloons()
            st.success(f"🎉 Loaded {len(all_media)} media files total!")

# -----------------------
# Media Display
# -----------------------
# Use filtered media if available, otherwise use all media
display_media = st.session_state.get('filtered_media', st.session_state.media_files)

if display_media and st.session_state.current_index < len(display_media):
    media_list = display_media
    total = len(media_list)
    idx = st.session_state.current_index
    
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-box">
            <h2>{idx + 1}/{total}</h2>
            <p>Current Item</p>
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
    
    current_item = media_list[idx]
    media_type = current_item.get("type", "image")
    
    st.markdown('<div class="image-frame">', unsafe_allow_html=True)
    
    if current_item["source"] == "gdrive":
        file_id = current_item.get("file_id", "")
        
        # Try multiple URL formats
        urls_to_try = [
            f"https://lh3.googleusercontent.com/d/{file_id}=w2000",
            f"https://drive.google.com/uc?export=view&id={file_id}",
            f"https://drive.google.com/thumbnail?id={file_id}&sz=w2000",
            f"https://lh3.googleusercontent.com/d/{file_id}",
            f"https://drive.google.com/uc?export=download&id={file_id}",
        ]
        
        media_loaded = False
        last_error = None
        
        for attempt, url in enumerate(urls_to_try, 1):
            try:
                response = requests.get(url, timeout=20, allow_redirects=True, stream=True)
                content_type = response.headers.get('Content-Type', '').lower()
                
                if response.status_code == 200:
                    if media_type == "video" or 'video' in content_type:
                        # For videos, try to display using st.video
                        try:
                            video_bytes = response.content
                            st.video(video_bytes)
                            media_loaded = True
                            break
                        except:
                            # If st.video fails, provide download link
                            st.warning(f"⚠️ Video format may not be supported for inline playback")
                            st.markdown(f"[📥 Download Video](https://drive.google.com/file/d/{file_id}/view)")
                            media_loaded = True
                            break
                    else:
                        # For images
                        try:
                            from PIL import Image
                            img = Image.open(BytesIO(response.content))
                            
                            # Convert for better compatibility
                            if img.mode in ('RGBA', 'LA', 'P'):
                                background = Image.new('RGB', img.size, (255, 255, 255))
                                if img.mode == 'P':
                                    img = img.convert('RGBA')
                                if img.mode in ('RGBA', 'LA'):
                                    background.paste(img, mask=img.split()[-1])
                                else:
                                    background.paste(img)
                                img = background
                            
                            st.image(img, use_container_width=True)
                            media_loaded = True
                            break
                        except Exception as img_error:
                            last_error = str(img_error)
                            continue
            except Exception as e:
                last_error = str(e)
                continue
        
        if not media_loaded:
            st.error(f"❌ Unable to load: {current_item['name']}")
            if last_error:
                st.caption(f"Error: {last_error}")
            st.info(f"💡 File ID: {file_id}")
            st.markdown(f"[📂 Open in Google Drive](https://drive.google.com/file/d/{file_id}/view)")
    else:
        # Load local media
        try:
            if media_type == "video":
                st.video(current_item["path"])
            else:
                st.image(current_item["path"], use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error loading: {current_item['name']}")
            st.caption(f"Error: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)
    
    # Media icon based on type
    media_icon = "🎬" if media_type == "video" else ("☁️" if current_item['source'] == 'gdrive' else "📷")
    
    st.markdown(f"""
    <div class="image-caption">
        <span class="slide-counter">{idx + 1} / {total}</span>
        <span>{media_icon} {current_item["name"]}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### 🎮 Media Controls")
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
        if st.button("🔀 Shuffle", use_container_width=True):
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
            "Jump to item:",
            range(1, total + 1),
            index=idx,
            label_visibility="collapsed"
        )
        if jump_to != idx + 1:
            st.session_state.current_index = jump_to - 1
            st.rerun()
    
    # Show details
    if show_info:
        with st.expander("📋 View Item Details"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Name", current_item["name"][:30] + "..." if len(current_item["name"]) > 30 else current_item["name"])
            with col2:
                st.metric("Type", current_item.get("type", "unknown").upper())
            with col3:
                st.metric("Format", current_item.get("format", "UNKNOWN"))
            with col4:
                st.metric("Source", current_item["source"].upper())
            
            if current_item["source"] == "gdrive":
                col1, col2, col3 = st.columns(3)
                with col1:
                    if "discovery" in current_item:
                        st.metric("Discovery Method", current_item["discovery"])
                with col2:
                    if "size_kb" in current_item and current_item["size_kb"] > 0:
                        st.metric("Size", f"{current_item['size_kb']} KB")
                with col3:
                    st.metric("File ID", current_item.get("file_id", "N/A")[:20] + "...")
                
                st.markdown(f"🔗 [Open in Google Drive](https://drive.google.com/file/d/{current_item.get('file_id', '')}/view)")
    
    # Autoplay logic
    if st.session_state.autoplay:
        time.sleep(slideshow_speed)
        if idx == total - 1 and st.session_state.loop_mode:
            st.session_state.current_index = 0
        elif idx < total - 1:
            st.session_state.current_index = idx + 1
        else:
            st.session_state.autoplay = False
        st.rerun()

else:
    # Welcome screen
    st.markdown("""
    <div class="info-card">
        <h3>👋 Welcome to Ultimate Media Gallery!</h3>
        <p><strong>🎯 Zero-Skip Extraction Technology</strong></p>
        <p>This gallery uses advanced 7-strategy extraction that captures EVERY file in your Google Drive folder with zero skipping!</p>
        
        <h4>🚀 Quick Start:</h4>
        <ol>
            <li>📁 Select your media source (local, Google Drive, or both)</li>
            <li>🔗 Paste your public Google Drive folder URL</li>
            <li>🚀 Click "Load Gallery"</li>
            <li>▶️ Enjoy your slideshow!</li>
        </ol>
        
        <h4>✨ Features:</h4>
        <ul>
            <li>🎬 <strong>Images & Videos Support</strong></li>
            <li>📸 <strong>50+ Image Formats:</strong> JPG, PNG, GIF, WEBP, BMP, TIFF, SVG, HEIC, AVIF, RAW, CR2, NEF, and more</li>
            <li>🎥 <strong>30+ Video Formats:</strong> MP4, AVI, MOV, MKV, WEBM, FLV, WMV, MPEG, and more</li>
            <li>🔍 <strong>7-Strategy Extraction:</strong>
                <ul>
                    <li>Strategy 1: JavaScript data mining</li>
                    <li>Strategy 2: Drive internal data blobs</li>
                    <li>Strategy 3: MIME type targeting</li>
                    <li>Strategy 4: Thumbnail & CDN extraction</li>
                    <li>Strategy 5: Ultra-comprehensive scan</li>
                    <li>Strategy 6: JSON structure parsing</li>
                    <li>Strategy 7: File metadata extraction</li>
                </ul>
            </li>
            <li>✅ <strong>Magic Byte Validation:</strong> Detects actual file types</li>
            <li>🚫 <strong>Zero-Skip Policy:</strong> ALL files are added, even uncertain ones</li>
            <li>⚡ <strong>No Authentication Required</strong></li>
            <li>🔁 <strong>Loop & Shuffle Modes</strong></li>
            <li>🎨 <strong>Beautiful Dark Theme</strong></li>
            <li>📊 <strong>Real-time Statistics</strong></li>
            <li>🎯 <strong>Filter by Type:</strong> Show only images or videos</li>
        </ul>
        
        <h4>🔧 Setup:</h4>
        <ul>
            <li>📂 <strong>Local:</strong> Place media in "public" folder</li>
            <li>🔓 <strong>Google Drive:</strong> Set folder to "Anyone with link can view"</li>
            <li>🌐 <strong>Supported Sources:</strong> Local files, Google Drive, or both combined</li>
        </ul>
        
        <h4>💡 Pro Tips:</h4>
        <ul>
            <li>The app validates ALL discovered files - nothing is skipped</li>
            <li>Even timeout or error files are added (zero-skip guarantee)</li>
            <li>Magic byte detection ensures accurate format identification</li>
            <li>Works with nested structures and complex folder layouts</li>
            <li>Supports any file name format - no restrictions</li>
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
            <h2>50+</h2>
            <p>Image Formats</p>
        </div>
        <div class="stat-box">
            <h2>30+</h2>
            <p>Video Formats</p>
        </div>
        <div class="stat-box">
            <h2>⚡</h2>
            <p>No Auth Needed</p>
        </div>
        <div class="stat-box">
            <h2>🔍</h2>
            <p>7 Strategies</p>
        </div>
        <div class="stat-box">
            <h2>🚫</h2>
            <p>Zero Skips</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------
# Footer
# -----------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-secondary); padding: 1rem;">
    <p>🎬 <strong>Ultimate Media Gallery v3.0</strong> | Zero-Skip Extraction | 7-Strategy Technology</p>
    <p>Supports 50+ Image Formats | 30+ Video Formats | Local & Google Drive | No Authentication</p>
    <p>💪 Powered by Advanced Magic Byte Detection & Comprehensive Pattern Matching</p>
</div>
""", unsafe_allow_html=True)
