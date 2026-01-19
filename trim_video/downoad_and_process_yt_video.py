import json
import subprocess
import os
import uuid
import boto3
import urllib.request
from botocore.exceptions import ClientError
from botocore.config import Config

s3_client = boto3.client(
    "s3",
    region_name="eu-north-1",
    config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
)

S3_BUCKET = "trim-videos"
PRESIGNED_URL_EXPIRATION = int(os.environ.get("PRESIGNED_URL_EXPIRATION", 3600))
YTDLP_BINARY = os.path.join(os.getcwd(), "yt-dlp")

TRIM_LAMBDA_URL = (
    "https://jm2xswncovc53txwrhkkfgmiye0kepvp.lambda-url.eu-north-1.on.aws/"
)


def download_youtube_video(youtube_url, output_path):
    cmd = [
        YTDLP_BINARY,
        "-f",
        "best[ext=mp4]/best",
        "--no-playlist",
        "-o",
        output_path,
        youtube_url,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def invoke_trim_lambda(presigned_url, start_s, end_s):
    payload = {"video_url": presigned_url, "start": start_s, "end": end_s}

    req = urllib.request.Request(
        TRIM_LAMBDA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def handler(event, context):
    downloaded_file = None

    try:
        body = (
            json.loads(event["body"])
            if isinstance(event.get("body"), str)
            else event.get("body", event)
        )
        video_url = body.get("video_url")
        start_s = body.get("start")
        end_s = body.get("end")

        if not video_url:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required parameter: video_url"}),
            }

        unique_id = str(uuid.uuid4())
        downloaded_file = f"/tmp/video_{unique_id}.mp4"
        s3_key = f"youtube-videos/{unique_id}.mp4"

        # Download from YouTube
        download_youtube_video(video_url, downloaded_file)

        file_size = os.path.getsize(downloaded_file)

        # Upload to S3
        s3_client.upload_file(
            downloaded_file,
            S3_BUCKET,
            s3_key,
            ExtraArgs={
                "ContentType": "video/mp4",
                "Metadata": {"original_url": video_url},
            },
        )

        presigned_url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET, "Key": s3_key},
            ExpiresIn=PRESIGNED_URL_EXPIRATION,
        )

        # 🔥 Call trim Lambda with presigned URL
        trim_response = invoke_trim_lambda(
            presigned_url=presigned_url, start_s=start_s, end_s=end_s
        )

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "message": "Video downloaded, uploaded, and trim requested",
                    "presigned_url": presigned_url,
                    "s3_key": s3_key,
                    "file_size_bytes": file_size,
                    "trim_lambda_response": trim_response,
                }
            ),
        }

    except subprocess.CalledProcessError as e:
        return {
            "statusCode": 500,
            "body": json.dumps(
                {
                    "error": "YouTube download failed",
                    "details": e.stderr.decode() if e.stderr else str(e),
                }
            ),
        }

    except ClientError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "S3 operation failed", "details": str(e)}),
        }

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


try:
    responose = handler({
    "body": {
        "video_url": "https://www.youtube.com/watch?v=I1DreZNIo-E",
        "start": 1,
        "end": 3,
        "is_youtube_url": "true"
    }
    },{})
    print(responose)
except Exception as e:
    print(e)