from urllib.parse import urlparse, parse_qs



def extract_video_id(youtube_url: str) -> str:
    parsed = urlparse(youtube_url)

    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        query = parse_qs(parsed.query)
        if "v" in query and query["v"]:
            return query["v"][0]

    if parsed.hostname == "youtu.be":
        return parsed.path.lstrip("/")

    raise ValueError("Invalid or unsupported YouTube URL")