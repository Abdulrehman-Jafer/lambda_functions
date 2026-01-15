import json
import subprocess
import os
import uuid
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import yt_dlp

s3_client = boto3.client(
    's3',
    region_name='eu-north-1',
    config=Config(
        signature_version='s3v4',
        s3={'addressing_style': 'virtual'}
    )
)

S3_BUCKET = 'trim-videos'
PRESIGNED_URL_EXPIRATION = int(os.environ.get('PRESIGNED_URL_EXPIRATION', 3600))

def download_youtube_video(youtube_url, output_path):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        return output_path
    except Exception as e:
        raise Exception(f"Failed to download YouTube video: {str(e)}")

def lambda_handler(event, context):
    downloaded_file = None
    
    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)
        
        video_url = body.get('video_url')
        start_ms = body.get('start')
        end_ms = body.get('end')
        is_youtube_url = body.get('is_youtube_url') == "true"
        
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
        output_file = f'/tmp/output_{unique_id}.mp4'
        s3_key = f'trimmed-videos/{unique_id}.mp4'

        if is_youtube_url:
            downloaded_file = f'/tmp/downloaded_{unique_id}.mp4'
            download_youtube_video(video_url, downloaded_file)
            video_url = downloaded_file
        
        ffmpeg_command = [
            'ffmpeg',
            '-i', video_url,
            '-ss', str(start_sec),
            '-t', str(duration),
            '-c', 'copy',
            '-y',
            output_file
        ]
        
        subprocess.run(ffmpeg_command, check=True, capture_output=True)
        
        file_size = os.path.getsize(output_file)
        
        s3_client.upload_file(
            output_file,
            S3_BUCKET,
            s3_key,
            ExtraArgs={
                'ContentType': 'video/mp4',
                'Metadata': {
                    'original_url': body.get('video_url'),  # Use original URL for metadata
                    'start_ms': str(start_ms),
                    'end_ms': str(end_ms),
                    'duration_seconds': str(duration)
                }
            }
        )
        
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKET,
                'Key': s3_key
            },
            ExpiresIn=PRESIGNED_URL_EXPIRATION
        )
        
        files_to_cleanup = [output_file]
        if downloaded_file:
            files_to_cleanup.append(downloaded_file)
        cleanup_files(files_to_cleanup)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'message': 'Video trimmed successfully',
                'presigned_url': presigned_url,
                's3_key': s3_key,
                'duration_seconds': duration,
                'file_size_bytes': file_size,
                'url_expires_in_seconds': PRESIGNED_URL_EXPIRATION
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
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'S3 operation failed',
                'details': str(e)
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }