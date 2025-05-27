from flask import Flask, request, jsonify, send_file, render_template, redirect
import os
import yt_dlp
import tempfile
import uuid
import re
from flask_cors import CORS
import logging
from urllib.parse import urlparse, parse_qs
import time
import json
import hashlib
import shutil
import random
import threading
from flask_babel import Babel, gettext as _
import yaml
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Site domain constant - for production environment
SITE_DOMAIN = "ttdl.cc"
# Protocol for the site
SITE_PROTOCOL = "https"

# yt-dlp version
YT_DLP_VERSION = "2025.04.30"

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

# Configure Flask-Babel for internationalization
babel = Babel(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'languages'

# List of supported languages in international standard order, with 'en' (US) first
SUPPORTED_LANGUAGES = [
    'en',  # English (US)
    'zh', # Chinese
    'es', # Spanish
    'hi', # Hindi
    'ar', # Arabic
    'pt', # Portuguese
    'bn', # Bengali
    'ru', # Russian
    'ja', # Japanese
    'de', # German
    'id', # Indonesian
    'fr', # French
    'ms', # Malay
    'it', # Italian
    'ko', # Korean
]

# Function to get the site URL with the domain
def get_site_url(path="", lang=None):
    """
    Returns the site URL with the configured domain.
    it uses the configured domain.
    
    Args:
        path (str): Path to append to the URL (without leading slash)
        lang (str): Language code to include in the URL path
        
    Returns:
        str: Complete URL
    """
    base_url = f"{SITE_PROTOCOL}://{SITE_DOMAIN}"
    
    # Add language path if provided
    if lang and lang in SUPPORTED_LANGUAGES and lang != app.config['BABEL_DEFAULT_LOCALE']:
        base_url = f"{base_url}/{lang}"
    
    # Add path if provided
    if path:
        # Ensure path doesn't start with a slash
        if path.startswith('/'):
            path = path[1:]
        return f"{base_url}/{path}"
    
    return base_url

# Download storage directory
DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Temporary directory for downloaded files
TEMP_DIR = os.path.join(tempfile.gettempdir(), 'tiktok_downloads')
os.makedirs(TEMP_DIR, exist_ok=True)

# Function to load language translations from YAML files
def load_translations(lang_code):
    translations = {}
    try:
        lang_file = os.path.join('languages', lang_code, 'translations.yaml')
        if os.path.exists(lang_file):
            with open(lang_file, 'r', encoding='utf-8') as file:
                translations = yaml.safe_load(file)
    except Exception as e:
        logger.error(f"Error loading translations for {lang_code}: {e}")
    return translations

def get_locale():
    # First check if language is in the URL path
    path_parts = request.path.lstrip('/').split('/')
    if path_parts and path_parts[0] in SUPPORTED_LANGUAGES:
        return path_parts[0]
    
    # Try to get language from request args
    lang = request.args.get('lang')
    if lang in SUPPORTED_LANGUAGES:
        return lang
    
    # Default to English
    return app.config['BABEL_DEFAULT_LOCALE']

# Set the locale selector function
babel.select_locale_func = get_locale

# Context processor to make translations available in templates
@app.context_processor
def inject_translations():
    translations = load_translations(get_locale())
    
    # Add current year to all templates
    current_year = datetime.datetime.now().year
    current_locale = get_locale()
    
    # Function for translations
    def translate(key, default=None):
        # First try to use Flask-Babel gettext for standard translations
        try:
            translated = _(key)
            if translated != key:
                return translated
        except:
            pass
        
        # If not found, try to use our YAML translations
        keys = key.split('.')
        current = translations
        
        for k in keys:
            # Check if the key is a numeric index (for arrays)
            if current and isinstance(current, dict) and k in current:
                current = current[k]
            elif current and isinstance(current, list) and k.isdigit() and int(k) < len(current):
                # Handle numeric indices for array items
                current = current[int(k)]
            else:
                # Try to handle array access with number in key (like "questions.0.question")
                if isinstance(current, dict):
                    # Try to find a key that contains the prefix before the index
                    prefix = k.split('.')[0] if '.' in k else k
                    if prefix in current and isinstance(current[prefix], list):
                        remaining_keys = k.split('.')[1:] if '.' in k else []
                        if remaining_keys and remaining_keys[0].isdigit():
                            idx = int(remaining_keys[0])
                            if idx < len(current[prefix]):
                                new_current = current[prefix][idx]
                                for nk in remaining_keys[1:]:
                                    if isinstance(new_current, dict) and nk in new_current:
                                        new_current = new_current[nk]
                                    else:
                                        return default if default is not None else key
                                return new_current
                return default if default is not None else key
                
        return current if current is not None else (default if default is not None else key)
    
    # Helper function to generate URLs with the current language
    def page_url(path=""):
        # Always include the current language in URLs if not default
        if current_locale != app.config['BABEL_DEFAULT_LOCALE']:
            return get_site_url(path, current_locale)
        return get_site_url(path)
    
    return dict(t=translate, current_year=current_year, current_locale=current_locale, 
                site_url=get_site_url, page_url=page_url)

# List of user agents to rotate through
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

def get_random_user_agent():
    """Get a random user agent from the list"""
    return random.choice(USER_AGENTS)

def clean_temp_files():
    """Clean temporary files older than 1 hour"""
    current_time = time.time()
    one_hour_ago = current_time - 3600
    
    for filename in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, filename)
        if os.path.isfile(file_path) and os.path.getmtime(file_path) < one_hour_ago:
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Failed to remove temporary file {file_path}: {e}")

def validate_tiktok_url(url):
    """Validate if the URL is a TikTok URL"""
    parsed = urlparse(url)
    return 'tiktok.com' in parsed.netloc

def extract_video_id_from_url(url):
    """Extract the TikTok video ID from a URL"""
    patterns = [
        r'tiktok\.com\/@[\w.-]+/video/(\d+)',  # Standard URL
        r'tiktok\.com/t/([A-Za-z0-9]+)',       # Shortened URL
        r'/v/(\d+)',                           # Another format
        r'video/(\d+)',                        # Generic video ID pattern
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # Try to extract from URL parameter 'video_id'
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    if 'video_id' in query_params:
        return query_params['video_id'][0]
    
    # If all else fails, generate a hash of the URL to use as ID
    if url:
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return f"hash_{url_hash[:16]}"
    
    return None

def extract_video_info(url):
    """Extract video information using yt-dlp"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
            'Referer': 'https://www.tiktok.com/'
        },
        'cookiefile': None,
        'cachedir': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Extract relevant information
            result = {
                'title': info.get('title', 'Unknown Title'),
                'author': info.get('uploader', 'Unknown Author'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'comment_count': info.get('comment_count', 0),
                'video_formats': [],
                'audio_formats': [],
                'video_id': info.get('id') or extract_video_id_from_url(url)
            }
            
            # Extract token if available
            tt_chain_token = None
            if 'cookies' in info and info['cookies']:
                cookie_str = info.get('cookies', '')
                if 'tt_chain_token' in cookie_str:
                    match = re.search(r'tt_chain_token=\"?([^\";\s]+)\"?', cookie_str)
                    if match:
                        tt_chain_token = match.group(1)
            
            # Process formats
            formats = info.get('formats', [])
            
            # Get all video formats
            video_formats = []
            for fmt in formats:
                if fmt.get('ext') == 'mp4' and fmt.get('vcodec', 'none') != 'none':
                    filesize = fmt.get('filesize')
                    filesize_str = convert_size(filesize) if filesize else 'Unknown'
                    
                    video_formats.append({
                        'format_id': fmt.get('format_id', 'video'),
                        'ext': 'mp4',
                        'quality': 'HD' if fmt.get('height', 0) >= 720 else 'SD',
                        'resolution': f"{fmt.get('width', 0)}x{fmt.get('height', 0)}",
                        'filesize': filesize_str,
                        'filesize_bytes': filesize,
                        'url': fmt.get('url', ''),
                        'type': 'video'
                    })
            
            # Sort video formats by resolution (height), highest first
            video_formats.sort(key=lambda x: int(x['resolution'].split('x')[1]), reverse=True)
            
            # Add the best video format first, then all others
            if video_formats:
                result['video_formats'].append(video_formats[0])  # Best format
                result['video_formats'].extend(video_formats[1:])  # All other formats
            
            # Add audio format
            result['audio_formats'].append({
                'format_id': 'mp3',
                'ext': 'mp3',
                'quality': 'High Quality Audio',
                'filesize': 'Unknown',
                'url': url,
                'type': 'audio'
            })
            
            # Store the token
            if tt_chain_token:
                result['tt_chain_token'] = tt_chain_token
            
            return result
    except Exception as e:
        logger.error(f"Error in yt-dlp extraction: {e}")
        raise

def get_download_path(video_id, file_type='mp4', format_id='best'):
    """Get the storage path for a download based on its ID and format"""
    video_dir = os.path.join(DOWNLOAD_DIR, video_id)
    os.makedirs(video_dir, exist_ok=True)
    
    if file_type == 'mp3':
        return os.path.join(video_dir, f"audio.mp3")
    else:
        return os.path.join(video_dir, f"{format_id}.mp4")

def is_file_cached(video_id, file_type='mp4', format_id='best'):
    """Check if a specific format is already cached"""
    file_path = get_download_path(video_id, file_type, format_id)
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0

def get_ffmpeg_path():
    """Get FFmpeg path with platform-specific handling"""
    # First try to find ffmpeg in PATH
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        logger.info(f"Found ffmpeg in PATH at: {ffmpeg_path}")
        return os.path.dirname(ffmpeg_path)
    
    # Platform-specific fallback paths
    if os.name == 'nt':  # Windows
        common_paths = [
            'C:\\ffmpeg\\bin',
            'C:\\Program Files\\ffmpeg\\bin',
            'C:\\Program Files (x86)\\ffmpeg\\bin'
        ]
    else:  # Linux/Unix
        common_paths = ['/usr/bin', '/usr/local/bin']
    
    # Check common paths
    for path in common_paths:
        if os.path.exists(os.path.join(path, 'ffmpeg')):
            logger.info(f"Found ffmpeg at: {path}")
            return path
    
    return None

def download_file(url, output_path, format_id='best', is_audio=False):
    """Download a video or extract audio using yt-dlp"""
    user_agent = get_random_user_agent()
    
    # For MP3 downloads, remove the extension as yt-dlp will add it back
    if is_audio:
        output_dir = os.path.dirname(output_path)
        output_basename = os.path.splitext(os.path.basename(output_path))[0]
        output_template = os.path.join(output_dir, output_basename)
    else:
        output_template = output_path
    
    # Configure yt-dlp options
    ydl_opts = {
        'outtmpl': output_template,
        'quiet': False,
        'verbose': True,
        'no_warnings': False,
        'http_headers': {
            'User-Agent': user_agent,
            'Referer': 'https://www.tiktok.com/',
        },
        'socket_timeout': 15,
        'retries': 5,
        'fragment_retries': 5,
        'continuedl': True,
    }
    
    if is_audio:
        # Get FFmpeg path
        ffmpeg_path = get_ffmpeg_path()
        if ffmpeg_path:
            ydl_opts['ffmpeg_location'] = ffmpeg_path
        else:
            logger.warning("FFmpeg not found in PATH or common locations. Audio extraction may fail.")
        
        # Add audio extraction options
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',  # Best quality
            }],
            'keepvideo': False,
            'extractaudio': True,
            'prefer_ffmpeg': True,
        })
    else:
        # Use specific format for video
        ydl_opts['format'] = format_id
    
    try:
        logger.info(f"Downloading {'audio' if is_audio else 'video'} with format: {format_id}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # For MP3, check if the file exists with the right extension
        if is_audio:
            expected_path = f"{output_template}.mp3"
            if os.path.exists(expected_path) and os.path.getsize(expected_path) > 0:
                logger.info(f"Found MP3 at {expected_path}, copying to {output_path}")
                # Copy file to expected location if they're different
                if expected_path != output_path:
                    shutil.copy(expected_path, output_path)
                return True
            else:
                # Look for any mp3 file in the directory
                output_dir = os.path.dirname(output_path)
                for file in os.listdir(output_dir):
                    if file.endswith('.mp3'):
                        found_path = os.path.join(output_dir, file)
                        logger.info(f"Found alternative MP3 at {found_path}, copying to {output_path}")
                        shutil.copy(found_path, output_path)
                        return True
                logger.error(f"No MP3 file found after download. Expected at {expected_path}")
                return False
        else:
            # Check if video file exists and has content
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                logger.info(f"Successfully downloaded to {output_path}")
                return True
            else:
                logger.error("Download completed but file is empty or does not exist")
                if os.path.exists(output_path):
                    os.remove(output_path)
                return False
    except Exception as e:
        logger.error(f"Error downloading: {e}")
        if os.path.exists(output_path):
            os.remove(output_path)
        return False

def convert_size(size_bytes):
    """Convert file size in bytes to human-readable format"""
    if size_bytes is None:
        return "Unknown"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    size = float(size_bytes)
    unit_index = 0
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    return f"{size:.2f} {units[unit_index]}"

# Helper function to get language URLs
def get_language_urls(current_path=""):
    """
    Generate URLs for all supported languages for the current path
    
    Args:
        current_path (str): The current page path without language prefix
        
    Returns:
        dict: Dictionary of language codes and their corresponding URLs
    """
    urls = {}
    for lang in SUPPORTED_LANGUAGES:
        if lang == app.config['BABEL_DEFAULT_LOCALE']:
            # Default language uses the original URL without language prefix
            urls[lang] = get_site_url(current_path)
        else:
            # Other languages use the language prefix
            urls[lang] = get_site_url(current_path, lang)
    return urls

# Add language URLs to all templates
@app.context_processor
def inject_language_urls():
    # Get the current path without language prefix
    path = request.path.lstrip('/')
    current_locale = get_locale()
    
    # If path starts with a language code, remove it to get the base path
    if path and path.split('/')[0] in SUPPORTED_LANGUAGES:
        path_parts = path.split('/')
        path = '/'.join(path_parts[1:])
    
    # Generate URLs for all languages
    language_urls = get_language_urls(path)
    
    # Language names for the dropdown
    language_names = {
        'en': 'English',
        'zh': '中文',
        'es': 'Español',
        'hi': 'हिन्दी',
        'ar': 'العربية',
        'pt': 'Português',
        'bn': 'বাংলা',
        'ru': 'Русский',
        'ja': '日本語',
        'de': 'Deutsch',
        'id': 'Bahasa Indonesia',
        'fr': 'Français',
        'ms': 'Bahasa Melayu',
        'it': 'Italiano',
        'ko': '한국어',
    }
    
    return {
        'language_urls': language_urls,
        'language_names': language_names,
        'is_default_language': current_locale == app.config['BABEL_DEFAULT_LOCALE']
    }

# Original routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mp3')
def mp3():
    return render_template('mp3.html')

@app.route('/how-to-save')
def how_to_save():
    return render_template('how-to-save.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy-policy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/dmca')
def dmca():
    return render_template('dmca.html')

@app.route('/submit-contact', methods=['POST'])
def submit_contact():
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')
    
    # Here you would typically send an email or store the contact data
    # For demonstration, we'll just log it and return success
    logger.info(f"Contact form submission: Name={name}, Email={email}, Subject={subject}")
    
    # Return success response
    return jsonify({"success": True, "message": "Your message has been received"}), 200

@app.route('/api/extract', methods=['POST'])
def extract():
    data = request.json
    url = data.get('url')
    is_mp3_page = data.get('is_mp3_page', False)
    
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    
    if not validate_tiktok_url(url):
        return jsonify({'error': 'Not a valid TikTok URL. Please provide a URL from tiktok.com'}), 400
    
    try:
        video_info = extract_video_info(url)
        
        if (not video_info or 
            (not video_info.get('video_formats') and not video_info.get('audio_formats'))):
            return jsonify({'error': 'Failed to extract video information. The video might be private or removed.'}), 500
        
        # Add URL used for extraction to response
        video_info['source_url'] = url
        
        # Add timestamp
        video_info['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')

        # Extract video ID for caching reference
        video_id = video_info.get('video_id')
        
        # Get formats based on the page
        if is_mp3_page:
            # For MP3 page, only return the audio format
            formats = video_info.get('audio_formats', [])
            video_info['formats'] = formats
            # Remove video formats to simplify response
            if 'video_formats' in video_info:
                del video_info['video_formats']
        else:
            # For video page, only return video formats
            formats = video_info.get('video_formats', [])
            video_info['formats'] = formats
            # Remove audio formats to simplify response
            if 'audio_formats' in video_info:
                del video_info['audio_formats']
        
        # Add download URLs and cached status
        for fmt in video_info.get('formats', []):
            fmt_id = fmt.get('format_id', 'best')
            fmt_ext = 'mp3' if fmt.get('type') == 'audio' else 'mp4'
            fmt['is_cached'] = is_file_cached(video_id, fmt_ext, fmt_id)
            
            # Create download URL
            download_url = f"/api/download?video_id={video_id}&format_id={fmt_id}&type={fmt_ext}&url={url}"
            fmt['download_url'] = download_url
        
        return jsonify(video_info)
    except Exception as e:
        logger.error(f"Error extracting video info: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['GET'])
def download():
    """Download the media file, cache it on server, then serve it to user"""
    url = request.args.get('url')
    file_type = request.args.get('type', 'mp4').lower()  # Normalize to lowercase
    video_id = request.args.get('video_id')
    format_id = request.args.get('format_id', 'best')
    
    # Validate required parameters
    if not url:
        return jsonify({
            'error': 'URL is required',
            'status': 'error',
            'code': 'MISSING_URL'
        }), 400
    
    # Validate file type
    if file_type not in ['mp4', 'mp3']:
        return jsonify({
            'error': f'Invalid file type: {file_type}. Must be either mp4 or mp3',
            'status': 'error',
            'code': 'INVALID_FILE_TYPE'
        }), 400
    
    # Try to extract video ID from URL if not provided
    if not video_id:
        video_id = extract_video_id_from_url(url)
        if not video_id:
            return jsonify({
                'error': 'Could not determine video ID',
                'status': 'error',
                'code': 'INVALID_VIDEO_ID'
            }), 400
    
    logger.info(f"Processing download for video ID: {video_id}, format: {format_id}, type: {file_type}")
    
    try:
        # Get the output path for this file
        output_path = get_download_path(video_id, file_type, format_id)
        
        # Check if the file is already cached
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            logger.info(f"Using cached file: {output_path}")
        else:
            # File doesn't exist or is empty, download it
            is_audio = file_type == 'mp3'
            
            # For video downloads, validate format_id
            if not is_audio and format_id != 'best':
                # Try to get available formats first
                try:
                    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                        info = ydl.extract_info(url, download=False)
                        available_formats = [f['format_id'] for f in info.get('formats', [])]
                        if format_id not in available_formats:
                            return jsonify({
                                'error': f'Requested format {format_id} is not available',
                                'available_formats': available_formats,
                                'status': 'error',
                                'code': 'FORMAT_NOT_AVAILABLE'
                            }), 400
                except Exception as e:
                    logger.error(f"Error validating format: {e}")
                    # Continue with download attempt even if format validation fails
            
            success = download_file(url, output_path, format_id, is_audio)
            
            if not success:
                return jsonify({
                    'error': f'Failed to download {file_type} from TikTok servers',
                    'video_id': video_id,
                    'format_id': format_id,
                    'status': 'error',
                    'code': 'DOWNLOAD_FAILED'
                }), 500
        
        # Determine clean filename for download
        if file_type == 'mp3':
            clean_filename = f"tiktok_audio_{video_id}.mp3"
        else:
            clean_filename = f"tiktok_{video_id}.mp4"
        
        # Determine correct MIME type
        mimetype = "audio/mpeg" if file_type == 'mp3' else "video/mp4"
        
        # Send the file
        return send_file(
            output_path,
            as_attachment=True,
            download_name=clean_filename,
            mimetype=mimetype
        )
        
    except Exception as e:
        logger.error(f"Error in download endpoint: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error',
            'code': 'INTERNAL_ERROR'
        }), 500

def clean_old_files():
    """Clean files older than 7 days from storage"""
    logger.info("Cleaning old files from downloads directory")
    current_time = time.time()
    one_week_ago = current_time - (7 * 24 * 60 * 60)  # 7 days in seconds
    
    try:
        for video_id in os.listdir(DOWNLOAD_DIR):
            video_dir = os.path.join(DOWNLOAD_DIR, video_id)
            if os.path.isdir(video_dir):
                # Check the modification time of the directory
                if os.path.getmtime(video_dir) < one_week_ago:
                    logger.info(f"Removing old download directory: {video_id}")
                    shutil.rmtree(video_dir, ignore_errors=True)
    except Exception as e:
        logger.error(f"Error cleaning old downloads: {e}")

# Set up a background thread to clean files periodically
def background_cleanup():
    """Run cleanup tasks periodically"""
    while True:
        try:
            clean_temp_files()
            clean_old_files()
        except Exception as e:
            logger.error(f"Error in background cleanup: {e}")
        
        # Sleep for 6 hours before next cleanup
        time.sleep(6 * 60 * 60)

# Start the cleanup thread when the app starts
cleanup_thread = threading.Thread(target=background_cleanup, daemon=True)
cleanup_thread.start()

# Language-specific routes
@app.route('/<lang>/')
@app.route('/<lang>')
def index_with_lang(lang):
    if lang not in SUPPORTED_LANGUAGES:
        return render_template('404.html'), 404
    return render_template('index.html')

@app.route('/<lang>/mp3')
def mp3_with_lang(lang):
    if lang not in SUPPORTED_LANGUAGES:
        return render_template('404.html'), 404
    return render_template('mp3.html')

@app.route('/<lang>/how-to-save')
def how_to_save_with_lang(lang):
    if lang not in SUPPORTED_LANGUAGES:
        return render_template('404.html'), 404
    return render_template('how-to-save.html')

@app.route('/<lang>/contact')
def contact_with_lang(lang):
    if lang not in SUPPORTED_LANGUAGES:
        return render_template('404.html'), 404
    return render_template('contact.html')

@app.route('/<lang>/privacy-policy')
def privacy_policy_with_lang(lang):
    if lang not in SUPPORTED_LANGUAGES:
        return render_template('404.html'), 404
    return render_template('privacy-policy.html')

@app.route('/<lang>/terms')
def terms_with_lang(lang):
    if lang not in SUPPORTED_LANGUAGES:
        return render_template('404.html'), 404
    return render_template('terms.html')

@app.route('/<lang>/dmca')
def dmca_with_lang(lang):
    if lang not in SUPPORTED_LANGUAGES:
        return render_template('404.html'), 404
    return render_template('dmca.html')

# Language-specific submit-contact route
@app.route('/<lang>/submit-contact', methods=['POST'])
def submit_contact_with_lang(lang):
    if lang not in SUPPORTED_LANGUAGES:
        return render_template('404.html'), 404
    return submit_contact()

# Custom middleware for language handling
@app.before_request
def handle_language_url():
    # Skip for static files and API requests
    if request.path.startswith('/static/') or request.path.startswith('/api/'):
        return None
    
    # Extract language from URL path if present
    path_parts = request.path.lstrip('/').split('/')
    path_lang = path_parts[0] if path_parts and path_parts[0] in SUPPORTED_LANGUAGES else None
    
    # Get language from query parameter if present
    query_lang = request.args.get('lang')
    
    # If URL has ?lang=xx parameter but no language in path, redirect to language path URL
    if query_lang in SUPPORTED_LANGUAGES and not path_lang:
        # Build the new URL with language in path
        new_path = f"/{query_lang}{request.path}"
        
        # Remove lang parameter from query string
        args = request.args.copy()
        args.pop('lang')
        query_string = '&'.join([f"{k}={v}" for k, v in args.items()]) if args else ""
        
        if query_string:
            new_url = f"{new_path}?{query_string}"
        else:
            new_url = new_path
            
        return redirect(new_url)
    
    return None

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 