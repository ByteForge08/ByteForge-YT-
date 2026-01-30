import json
import urllib.parse
import yt_dlp
import tempfile
import os
import re

def handler(event, context):
    try:
        # Parse request
        query = event.get('queryStringParameters', {}) or {}
        url = query.get('url', '')
        download_type = query.get('type', 'video')
        
        if not url:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'URL não fornecida'})
            }
        
        # Configure yt-dlp
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'outtmpl': '%(title)s.%(ext)s',
            'socket_timeout': 30,
        }
        
        if download_type == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            ydl_opts.update({
                'format': 'best[ext=mp4]/best',
                'merge_output_format': 'mp4',
            })
        
        with tempfile.TemporaryDirectory() as tmpdir:
            ydl_opts['outtmpl'] = os.path.join(tmpdir, '%(title)s.%(ext)s')
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Get video info
                info = ydl.extract_info(url, download=False)
                
                # Download
                ydl.download([url])
                
                # Find downloaded file
                base_filename = ydl.prepare_filename(info)
                
                if download_type == 'audio':
                    # Look for MP3 file
                    mp3_file = base_filename.rsplit('.', 1)[0] + '.mp3'
                    if os.path.exists(mp3_file):
                        file_path = mp3_file
                        content_type = 'audio/mpeg'
                        file_ext = 'mp3'
                    else:
                        # Search for any MP3
                        import glob
                        mp3_files = glob.glob(os.path.join(tmpdir, '*.mp3'))
                        if mp3_files:
                            file_path = mp3_files[0]
                            content_type = 'audio/mpeg'
                            file_ext = 'mp3'
                        else:
                            raise Exception("MP3 file not found after conversion")
                else:
                    # Look for video file
                    if os.path.exists(base_filename):
                        file_path = base_filename
                    else:
                        # Search for any video file
                        import glob
                        video_files = glob.glob(os.path.join(tmpdir, '*.*'))
                        video_exts = ['.mp4', '.webm', '.mkv']
                        for f in video_files:
                            if any(f.endswith(ext) for ext in video_exts):
                                file_path = f
                                break
                        else:
                            raise Exception("Video file not found")
                    
                    content_type = 'video/mp4'
                    file_ext = 'mp4'
                
                # Read file
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                # Create safe filename
                title = info.get('title', 'download')
                safe_title = re.sub(r'[^\w\s-]', '', title)[:50]
                filename = f"{safe_title}.{file_ext}"
                
                # Return file
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': content_type,
                        'Content-Disposition': f'attachment; filename="{filename}"',
                        'Cache-Control': 'no-cache, no-store, must-revalidate'
                    },
                    'body': file_content.hex(),
                    'isBase64Encoded': False
                }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': str(e)})
        }