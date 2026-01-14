import json
import subprocess
import os
import base64
import uuid

def lambda_handler(event, context):
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)
        
        video_url = body.get('video_url')
        start_ms = body.get('start')
        end_ms = body.get('end')
        
        if not all([video_url, start_ms is not None, end_ms is not None]):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameters: video_url, start, end'
                })
            }
        
        start_sec = start_ms / 1000
        end_sec = end_ms / 1000
        duration = end_sec - start_sec
        
        if duration <= 0:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'End time must be greater than start time'
                })
            }
        
        unique_id = str(uuid.uuid4())
        input_file = f'/tmp/input_{unique_id}.mp4'
        output_file = f'/tmp/output_{unique_id}.mp4'
        
        download_video(video_url, input_file)
        
        ffmpeg_command = [
            'ffmpeg',
            '-i', input_file,
            '-ss', str(start_sec),
            '-t', str(duration),
            '-c', 'copy',
            '-y',
            output_file
        ]
        
        subprocess.run(ffmpeg_command, check=True, capture_output=True)
        
        with open(output_file, 'rb') as f:
            video_data = f.read()
            video_base64 = base64.b64encode(video_data).decode('utf-8')
        
        file_size = os.path.getsize(output_file)
        
        cleanup_files([input_file, output_file])
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Video trimmed successfully',
                'video_base64': video_base64,
                'duration_seconds': duration,
                'file_size_bytes': file_size
            })
        }
        
    except subprocess.CalledProcessError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'FFmpeg processing failed',
                'details': e.stderr.decode() if e.stderr else str(e)
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }

def download_video(url, output_path):
    import urllib.request
    urllib.request.urlretrieve(url, output_path)

def cleanup_files(file_paths):
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass