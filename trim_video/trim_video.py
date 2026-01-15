import json
import subprocess
import os
import uuid
import boto3
from botocore.exceptions import ClientError

s3_client = boto3.client('s3')

S3_BUCKET = os.environ.get('S3_BUCKET_NAME')
PRESIGNED_URL_EXPIRATION = int(os.environ.get('PRESIGNED_URL_EXPIRATION', 3600))
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
        
        if not S3_BUCKET:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'S3_BUCKET_NAME environment variable not configured'
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
                    'original_url': video_url,
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
        
        cleanup_files([output_file])
        
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

def cleanup_files(file_paths):
    for path in file_paths:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass