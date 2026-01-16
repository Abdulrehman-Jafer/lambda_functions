import json
import subprocess
import os
import uuid
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

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

YTDLP_BINARY = os.path.join(os.getcwd(), 'yt-dlp')


def download_youtube_video(youtube_url, output_path):
    cmd = [
        YTDLP_BINARY,
        '-f', 'best[ext=mp4]/best',
        '--no-playlist',
        '-o', output_path,
        youtube_url
    ]

    subprocess.run(
        cmd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )


def lambda_handler(event, context):
    downloaded_file = None
    output_file = None

    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event.get('body', event)

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

        input_file = video_url
        output_file = f'/tmp/output_{unique_id}.mp4'
        s3_key = f'trimmed-videos/{unique_id}.mp4'

        if is_youtube_url:
            downloaded_file = f'/tmp/input_{unique_id}.mp4'
            download_youtube_video(video_url, downloaded_file)
            input_file = downloaded_file

        ffmpeg_command = [
            'ffmpeg',
            '-ss', str(start_sec),
            '-i', input_file,
            '-t', str(duration),
            '-c', 'copy',
            '-y',
            output_file
        ]

        subprocess.run(
            ffmpeg_command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

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

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
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
                'error': 'Processing failed',
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
