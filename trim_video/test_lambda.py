from trim_video import lambda_handler


try:
    responose = lambda_handler({
    "body": {
        "video_url": "https://www.youtube.com/watch?v=I1DreZNIo-E",
        "start": 1000,
        "end": 3000,
        "is_youtube_url": "true"
    }
    },{})
    print(responose)
except Exception as e:
    print(e)

