import re
import json
import requests
from urllib.parse import urlparse, parse_qs
import time
import random
import hashlib
import logging

class TiktokCustomDownloader:
    def __init__(self):
        """Initialize the custom TikTok downloader"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.tiktok.com/',
            'Origin': 'https://www.tiktok.com',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        self.logger = logging.getLogger('TiktokDownloader')
    
    def extract_video_id(self, url):
        """Extract the video ID from a TikTok URL"""
        # Clean URL first
        url = url.strip()
        
        # Handle mobile share URLs (vm.tiktok.com, vt.tiktok.com)
        if 'vm.tiktok.com' in url or 'vt.tiktok.com' in url:
            try:
                # Follow redirect to get the full URL
                r = self.session.head(url, allow_redirects=True)
                url = r.url
                self.logger.info(f"Redirected to: {url}")
            except Exception as e:
                self.logger.error(f"Failed to follow redirect: {e}")
        
        # Regular TikTok URL patterns
        patterns = [
            r'tiktok\.com\/@[\w.-]+/video/(\d+)',  # Standard URL
            r'tiktok\.com/t/([A-Za-z0-9]+)',       # Shortened URL
            r'/v/(\d+)',                           # Another format
            r'video/(\d+)'                         # Generic video ID pattern
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Try to extract from query parameters (some URLs use this)
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
        if 'item_id' in query_params:
            return query_params['item_id'][0]
        
        self.logger.error(f"Could not extract video ID from URL: {url}")
        return None
    
    def extract_username(self, url):
        """Extract the username from a TikTok URL"""
        match = re.search(r'tiktok\.com\/@([\w.-]+)', url)
        if match:
            return match.group(1)
        return None
    
    def get_video_info(self, url):
        """Get video information using custom methods"""
        video_id = self.extract_video_id(url)
        
        if not video_id:
            self.logger.error("Could not extract video ID from URL")
            return None
        
        self.logger.info(f"Extracted video ID: {video_id}")
        
        # Try TikTok website scraping method first
        try:
            result = self._try_website_scraping(url, video_id)
            if result:
                return result
        except Exception as e:
            self.logger.warning(f"Website scraping method failed: {e}")
        
        # Then try the TikTok web API
        try:
            result = self._get_video_info_web_api(url, video_id)
            if result:
                return result
        except Exception as e:
            self.logger.warning(f"Web API method failed: {e}")
        
        # Finally try the mobile API
        try:
            result = self._get_video_info_mobile_api(url, video_id)
            if result:
                return result
        except Exception as e:
            self.logger.warning(f"Mobile API method failed: {e}")
        
        # If all methods fail, try the TikTok embed approach
        try:
            result = self._try_embed_api(url, video_id)
            if result:
                return result
        except Exception as e:
            self.logger.warning(f"Embed API method failed: {e}")
        
        # If all methods fail
        self.logger.error("All methods failed to extract video info")
        return None
    
    def _try_website_scraping(self, url, video_id):
        """Try to get video info by direct scraping of the TikTok website"""
        # Directly access the TikTok URL with proper user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        # Use a clean URL
        clean_url = f"https://www.tiktok.com/video/{video_id}"
        
        try:
            response = requests.get(clean_url, headers=headers)
            html_content = response.text
            
            # Try to find JSON data in the HTML
            # Look for the SIGI_STATE
            sigi_match = re.search(r'<script id="SIGI_STATE" type="application/json">(.*?)</script>', html_content)
            if sigi_match:
                json_data = json.loads(sigi_match.group(1))
                
                # Extract key information
                item_module = json_data.get('ItemModule', {})
                if not item_module:
                    return None
                
                # Get the video data
                video_data = item_module.get(video_id, None)
                if not video_data:
                    video_keys = list(item_module.keys())
                    if video_keys:
                        video_data = item_module[video_keys[0]]
                    else:
                        return None
                
                # Extract basic info
                author = video_data.get('author', '')
                title = video_data.get('desc', '')
                
                # Get video and audio URLs
                video_url = None
                audio_url = None
                
                if 'video' in video_data:
                    video_obj = video_data['video']
                    if 'playAddr' in video_obj:
                        video_url = video_obj['playAddr']
                    elif 'downloadAddr' in video_obj:
                        video_url = video_obj['downloadAddr']
                
                # Get thumbnail
                thumbnail = None
                if 'cover' in video_data:
                    thumbnail = video_data['cover']
                
                # Extract stats
                stats = video_data.get('stats', {})
                play_count = stats.get('playCount', 0)
                digg_count = stats.get('diggCount', 0)
                comment_count = stats.get('commentCount', 0)
                
                # Extract audio URL if available
                if 'music' in video_data:
                    music_obj = video_data['music']
                    if 'playUrl' in music_obj:
                        audio_url = music_obj['playUrl']
                
                # Calculate file sizes
                video_filesize = self._get_filesize(video_url) if video_url else None
                audio_filesize = self._get_filesize(audio_url) if audio_url else None
                
                # Create format objects
                formats = []
                all_formats = []
                
                if video_url:
                    video_format = {
                        'format_id': 'mp4',
                        'ext': 'mp4',
                        'quality': 'HD',
                        'resolution': 'Unknown',
                        'filesize': self._format_size(video_filesize),
                        'filesize_bytes': video_filesize,
                        'url': video_url,
                        'type': 'video'
                    }
                    formats.append(video_format)
                    all_formats.append(video_format)
                
                if audio_url:
                    audio_format = {
                        'format_id': 'mp3',
                        'ext': 'mp3',
                        'quality': 'Audio',
                        'filesize': self._format_size(audio_filesize),
                        'filesize_bytes': audio_filesize,
                        'url': audio_url,
                        'type': 'audio'
                    }
                    formats.append(audio_format)
                    all_formats.append(audio_format)
                
                return {
                    'title': title,
                    'author': author,
                    'thumbnail': thumbnail,
                    'view_count': play_count,
                    'like_count': digg_count,
                    'comment_count': comment_count,
                    'formats': formats,
                    'all_formats': all_formats
                }
        
        except Exception as e:
            self.logger.error(f"Error in website scraping method: {e}")
            return None
    
    def _try_embed_api(self, url, video_id):
        """Try to get video info from TikTok embed API"""
        embed_url = f"https://www.tiktok.com/embed/v2/{video_id}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.tiktok.com/'
        }
        
        try:
            response = requests.get(embed_url, headers=headers)
            html_content = response.text
            
            # Extract video player data
            player_data_match = re.search(r'<script id="__NEXT_DATA__" type="application\/json">(.*?)<\/script>', html_content)
            if player_data_match:
                player_data = json.loads(player_data_match.group(1))
                
                # Navigate to get the video data
                props = player_data.get('props', {})
                page_props = props.get('pageProps', {})
                video_data = page_props.get('videoData', {})
                
                if not video_data:
                    return None
                
                # Extract basic info
                author = video_data.get('authorInfo', {}).get('uniqueId', '')
                title = video_data.get('title', '')
                thumbnail = video_data.get('thumbnailUrl', '')
                
                # Get video and audio URLs
                video_url = video_data.get('videoUrl', '')
                audio_url = video_data.get('musicUrl', '')
                
                # Extract stats
                stats = video_data.get('stats', {})
                play_count = stats.get('playCount', 0)
                digg_count = stats.get('diggCount', 0)
                comment_count = stats.get('commentCount', 0)
                
                # Calculate file sizes
                video_filesize = self._get_filesize(video_url) if video_url else None
                audio_filesize = self._get_filesize(audio_url) if audio_url else None
                
                # Create format objects
                formats = []
                all_formats = []
                
                if video_url:
                    video_format = {
                        'format_id': 'mp4',
                        'ext': 'mp4',
                        'quality': 'HD',
                        'resolution': f"{video_data.get('width', 0)}x{video_data.get('height', 0)}",
                        'filesize': self._format_size(video_filesize),
                        'filesize_bytes': video_filesize,
                        'url': video_url,
                        'type': 'video'
                    }
                    formats.append(video_format)
                    all_formats.append(video_format)
                
                if audio_url:
                    audio_format = {
                        'format_id': 'mp3',
                        'ext': 'mp3',
                        'quality': 'Audio',
                        'filesize': self._format_size(audio_filesize),
                        'filesize_bytes': audio_filesize,
                        'url': audio_url,
                        'type': 'audio'
                    }
                    formats.append(audio_format)
                    all_formats.append(audio_format)
                
                return {
                    'title': title,
                    'author': author,
                    'thumbnail': thumbnail,
                    'view_count': play_count,
                    'like_count': digg_count,
                    'comment_count': comment_count,
                    'formats': formats,
                    'all_formats': all_formats
                }
        except Exception as e:
            self.logger.error(f"Error in embed API method: {e}")
            return None
    
    def _get_video_info_web_api(self, original_url, video_id):
        """Try to get video info using the TikTok web API"""
        # First, get any redirect from the original URL
        try:
            res = self.session.head(original_url, allow_redirects=True)
            url = res.url
        except:
            url = original_url
        
        # Try to extract data from the webpage
        try:
            res = self.session.get(url)
            match = re.search(r'<script id="SIGI_STATE" type="application/json">(.*?)</script>', res.text)
            if match:
                data = json.loads(match.group(1))
                
                # Extract video details
                item_module = data.get('ItemModule', {})
                video_data = None
                
                for key, value in item_module.items():
                    if key == video_id or value.get('id') == video_id:
                        video_data = value
                        break
                
                if not video_data:
                    return None
                
                author = video_data.get('author', '')
                title = video_data.get('desc', '')
                
                # Extract video URL
                video_url = None
                music_url = None
                
                # Try to find the video URL in the JSON data
                if 'video' in video_data:
                    video_obj = video_data['video']
                    if 'playAddr' in video_obj:
                        video_url = video_obj['playAddr']
                    elif 'downloadAddr' in video_obj:
                        video_url = video_obj['downloadAddr']
                
                # Extract thumbnail
                thumbnail = None
                if 'cover' in video_data:
                    thumbnail = video_data['cover']
                
                # Try to find music URL
                if 'music' in video_data:
                    music_obj = video_data['music']
                    if 'playUrl' in music_obj:
                        music_url = music_obj['playUrl']
                
                # Extract stats if available
                stats = video_data.get('stats', {})
                digg_count = stats.get('diggCount', 0)
                share_count = stats.get('shareCount', 0)
                comment_count = stats.get('commentCount', 0)
                play_count = stats.get('playCount', 0)
                
                # Get file sizes if possible by making HEAD requests
                video_filesize = None
                music_filesize = None
                
                if video_url:
                    video_filesize = self._get_filesize(video_url)
                
                if music_url:
                    music_filesize = self._get_filesize(music_url)
                
                # Prepare all available formats - for web API we only have two formats
                all_formats = []
                
                if video_url:
                    all_formats.append({
                        'format_id': 'mp4',
                        'ext': 'mp4',
                        'url': video_url,
                        'vcodec': 'h264',
                        'acodec': 'aac',
                        'filesize': self._format_size(video_filesize),
                        'filesize_bytes': video_filesize,
                        'format_note': 'HD',
                        'type': 'video'
                    })
                
                if music_url:
                    all_formats.append({
                        'format_id': 'mp3',
                        'ext': 'mp3',
                        'url': music_url,
                        'vcodec': 'none',
                        'acodec': 'mp3',
                        'filesize': self._format_size(music_filesize),
                        'filesize_bytes': music_filesize,
                        'format_note': 'Audio',
                        'type': 'audio'
                    })
                
                return {
                    'title': title,
                    'author': author,
                    'thumbnail': thumbnail,
                    'view_count': play_count,
                    'like_count': digg_count,
                    'comment_count': comment_count,
                    'share_count': share_count,
                    'formats': [
                        {
                            'format_id': 'mp4',
                            'ext': 'mp4',
                            'quality': 'HD',
                            'resolution': 'Unknown',
                            'filesize': self._format_size(video_filesize),
                            'filesize_bytes': video_filesize,
                            'url': video_url,
                            'type': 'video'
                        } if video_url else None,
                        {
                            'format_id': 'mp3',
                            'ext': 'mp3',
                            'quality': 'Audio',
                            'filesize': self._format_size(music_filesize),
                            'filesize_bytes': music_filesize,
                            'url': music_url,
                            'type': 'audio'
                        } if music_url else None
                    ],
                    'all_formats': all_formats
                }
        except Exception as e:
            self.logger.error(f"Error in web API method: {e}")
            return None
    
    def _get_video_info_mobile_api(self, url, video_id):
        """Try to get video info using the TikTok mobile API"""
        api_url = f"https://api.tiktokv.com/aweme/v1/aweme/detail/?aweme_id={video_id}"
        
        headers = {
            'User-Agent': 'TikTok 26.2.0 rv:262018 (iPhone; iOS 14.4.2; en_US) Cronet',
            'Accept': 'application/json',
        }
        
        try:
            response = requests.get(api_url, headers=headers)
            response.raise_for_status()  # Will raise an exception for 4XX/5XX responses
            data = response.json()
            
            if 'aweme_detail' not in data:
                return None
            
            detail = data['aweme_detail']
            
            # Basic info
            title = detail.get('desc', '')
            author = detail.get('author', {}).get('nickname', '')
            
            # Thumbnail
            thumbnail = None
            if 'cover' in detail and 'url_list' in detail['cover']:
                thumbnail = detail['cover']['url_list'][0]
            
            # Video URL (without watermark if possible)
            video_url = None
            if 'video' in detail:
                video = detail['video']
                if 'play_addr' in video and 'url_list' in video['play_addr']:
                    video_url = video['play_addr']['url_list'][0]
                elif 'download_addr' in video and 'url_list' in video['download_addr']:
                    video_url = video['download_addr']['url_list'][0]
            
            # Music URL
            music_url = None
            if 'music' in detail and 'play_url' in detail['music'] and 'url_list' in detail['music']['play_url']:
                music_url = detail['music']['play_url']['url_list'][0]
            
            # Extract stats
            statistics = detail.get('statistics', {})
            duration = detail.get('duration', 0) / 1000 if 'duration' in detail else 0  # Convert ms to seconds
            digg_count = statistics.get('digg_count', 0)
            comment_count = statistics.get('comment_count', 0)
            play_count = statistics.get('play_count', 0)
            share_count = statistics.get('share_count', 0)
            
            # Get video resolution if available
            resolution = 'Unknown'
            width = height = 0
            if 'video' in detail and 'width' in detail['video'] and 'height' in detail['video']:
                width = detail['video']['width']
                height = detail['video']['height']
                resolution = f"{width}x{height}"
            
            # Get file sizes
            video_filesize = self._get_filesize(video_url) if video_url else None
            music_filesize = self._get_filesize(music_url) if music_url else None
            
            # Prepare all available formats
            all_formats = []
            
            if video_url:
                all_formats.append({
                    'format_id': 'mp4',
                    'ext': 'mp4',
                    'url': video_url,
                    'resolution': resolution,
                    'width': width,
                    'height': height,
                    'vcodec': 'h264',
                    'acodec': 'aac',
                    'filesize': self._format_size(video_filesize),
                    'filesize_bytes': video_filesize,
                    'format_note': 'HD',
                    'type': 'video'
                })
            
            if music_url:
                all_formats.append({
                    'format_id': 'mp3',
                    'ext': 'mp3',
                    'url': music_url,
                    'vcodec': 'none',
                    'acodec': 'mp3',
                    'filesize': self._format_size(music_filesize),
                    'filesize_bytes': music_filesize,
                    'format_note': 'Audio',
                    'type': 'audio'
                })
            
            return {
                'title': title,
                'author': author,
                'thumbnail': thumbnail,
                'duration': duration,
                'view_count': play_count,
                'like_count': digg_count,
                'comment_count': comment_count,
                'share_count': share_count,
                'formats': [
                    {
                        'format_id': 'mp4',
                        'ext': 'mp4',
                        'quality': 'HD',
                        'resolution': resolution,
                        'filesize': self._format_size(video_filesize),
                        'filesize_bytes': video_filesize,
                        'url': video_url,
                        'type': 'video'
                    } if video_url else None,
                    {
                        'format_id': 'mp3',
                        'ext': 'mp3',
                        'quality': 'Audio',
                        'filesize': self._format_size(music_filesize),
                        'filesize_bytes': music_filesize,
                        'url': music_url,
                        'type': 'audio'
                    } if music_url else None
                ],
                'all_formats': all_formats
            }
        
        except Exception as e:
            self.logger.error(f"Error in mobile API method: {e}")
            return None
    
    def _get_filesize(self, url):
        """Get the file size in bytes for a given URL using a HEAD request"""
        if not url:
            return None
        
        try:
            response = requests.head(url, timeout=5)
            if response.status_code == 200 and 'content-length' in response.headers:
                return int(response.headers['content-length'])
        except Exception as e:
            self.logger.warning(f"Failed to get file size: {e}")
        
        return None
    
    def _format_size(self, size_bytes):
        """Convert file size in bytes to human-readable format"""
        if size_bytes is None:
            return "Unknown"
        
        # Define units and their respective sizes in bytes
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        size = float(size_bytes)
        unit_index = 0
        
        # Convert to appropriate unit
        while size >= 1024 and unit_index < len(units) - 1:
            size /= 1024
            unit_index += 1
        
        # Format to 2 decimal places if not B
        if unit_index == 0:
            return f"{int(size)} {units[unit_index]}"
        return f"{size:.2f} {units[unit_index]}"
    
    def remove_watermark(self, video_url):
        """Attempts to remove watermark from video URL"""
        # This implementation is for demonstration
        # A real implementation would process the video to remove watermarks
        # For now, we just return the video URL as-is
        return video_url 