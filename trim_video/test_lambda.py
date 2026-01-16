from trim_video import lambda_handler


try:
    responose = lambda_handler({
    "body": {
        "video_url": "https://www.youtube.com/watch?v=zdCDiCID5l0&list=RDTWfzLpR3Q_E&index=3",
        "start": 1000,
        "end": 3000,
        "is_youtube_url": "true"
    }
    },{})
    print(responose)
except Exception as e:
    print(e)



"""
{
    "video_url": "https://video-file-pro-123.s3.eu-north-1.amazonaws.com/1741620044565-fileexampleMP4192018MG.mp4?response-content-disposition=inline&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEGwaCmV1LW5vcnRoLTEiRzBFAiBC29J7hTrmxTUQFVbCOJnhi7vx%2BxowZBWWakzHcO4UvQIhALOALgwRdwuA%2Bn%2F0V3U6Mvbon60hPSYwZ%2FbUZCd38MOTKs4DCDYQABoMMjAzOTE4ODQ1NjQ3IgyxzIwj8GKVqg2xENkqqwPLZjE73VnIXVH0GFOEB4gm%2BwYOPVZp69KMLR%2BBeMNTCrAcPdqF4ClS5Vrnp5hkGprkUc0spsoAqJpexrmFKYFAG2dgmOF5CPOYEASFcbnoVFz4JYJjtZ7AC2bbE%2BOoIHvF38%2FanBJh5PBQIYEEuj92pSit4PrTHvUUmoXI8aniwRIpHV%2FE%2Bswz0uqa8AiwID1GU87NTjnmpXzUixSYJ6v%2B9kD9YaaaqybTZYJU71ziItCslTneRESkZX4JN38eRI6DPu8HottlIm2%2F35aY%2Bz%2F218jYu%2FZdS5X6rtALxD6d3xGJCgh1G%2FpuCp4T0KddbO821z4Xv5eU7l2UWleFSiKDByVEKdzXF7b27M6LR6eN9zo82BzRdgAXoGF1ArYgtJhHgUeg9FvIJ0xfLYyc21FgP8TMvK1ekzT2uzdQEgKVax5pCS%2Bwcml7fcGQrjFe%2FBlxJG26Oznci1fqDU991%2FIQZ3xQoJHIA3Y9BVt0qbaPjhJkJLqQRFsNOcOSmlGC9mWxaRPgvX0PQjAwDa%2FpoUlFV7Kg3fiQhwh70OImO3n%2BcdTCyRxD9UJNVC6kMMW%2Fo8sGOt4CP9Ubc2TBmWLXEAhW12CeqfUOKjUZnN7N%2FvbwB3JdbZ%2BANA%2FMBkB4nQ60IZ1c5pPnX61JmMp7lpRDxjB5wr5KIkb%2BAcjkZZEdMxuhoIG5jVC1VNrnklr9DGx8AnqAURy1oTXa2qU895XSMm44TBB8%2BOC%2BEObsgqIkPApaRqxr2mHWiVNHXgDRvXSKi4caMm5gp3aj5ZA76JxFpNogsa6EjjkFuiqL5w4yPgOHUEwjh5xYd3MX%2Ff3FSbngp1zvnClnfOeaJ43c54Jvg9X8i6AFYMJvdc5BAEsS7nDSqbAqoFI%2BIt59sjQ%2FDjFAqFka1YpAt%2Bvi4rMMmGQjg3cnDJ0Go%2FaPRpaZqJ9Ih9E1QrNksbgzvWIhqCmEUF1ZhGe1da18sADOE24gOQi%2F3Z5THCNIglr7TB1zMA%2BUBrqQY0QaUMgIPgjO2Z96sCqb0iOSIJOAIZGBfOFBandMsbDvtv0%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=ASIAS66UCU3HVV7BAVJD%2F20260115%2Feu-north-1%2Fs3%2Faws4_request&X-Amz-Date=20260115T123901Z&X-Amz-Expires=43200&X-Amz-SignedHeaders=host&X-Amz-Signature=c8fd269be06a39b784f4f3ff2ddc7db6e525dcf89f15e923b231a82e287f1662",
    "start": 1000,
    "end": 3000
}
"""