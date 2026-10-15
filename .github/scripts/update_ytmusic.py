import os
import re
import sys
from ytmusicapi import YTMusic

README_PATH = "README.md"
AUTH_FILE = "headers_auth.json"

def get_ytmusic_block():
    auth_header = os.environ.get("YTMUSIC_AUTH")
    if not auth_header:
        print("Warning: YTMUSIC_AUTH secret not set or empty. Skipping update.")
        return None

    # Write auth file temporarily
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        f.write(auth_header)

    try:
        yt = YTMusic(AUTH_FILE)
        history = yt.get_history()
    except Exception as e:
        print(f"Error fetching history from YouTube Music: {e}", file=sys.stderr)
        return None
    finally:
        if os.path.exists(AUTH_FILE):
            os.remove(AUTH_FILE)

    if not history:
        print("No playback history found on YouTube Music.")
        return None

    # First item is the latest / currently playing track
    current = history[0]
    current_title = current.get("title", "Unknown Track")
    artists_list = [a["name"] for a in current.get("artists", [])]
    current_artist = ", ".join(artists_list) if artists_list else "Unknown Artist"

    # Next 5 items are recently played history
    recent_tracks = history[1:6]
    recent_lines = []
    for idx, track in enumerate(recent_tracks, 1):
        t_title = track.get("title", "Unknown Track")
        t_artists = ", ".join([a["name"] for a in track.get("artists", [])]) or "Unknown Artist"
        recent_lines.append(f"{idx}. 🎵 {t_title} — {t_artists}")

    if not recent_lines:
        recent_lines.append("1. 🎵 No additional recent tracks found.")

    rendered = f"""```text
▶  NOW PLAYING ON YOUTUBE MUSIC:
[■■■■■■■■■■■■■■■■□□□□]
🎵 Track  : {current_title}
👤 Artist : {current_artist}
💿 Source : YouTube Music (Live)

📜 LAST 5 PLAYED TRACKS:
""" + "\n".join(recent_lines) + "\n```"

    return rendered

def update_readme():
    block = get_ytmusic_block()
    if not block:
        print("No content generated; leaving README unchanged.")
        return

    if not os.path.exists(README_PATH):
        print(f"Error: {README_PATH} not found.", file=sys.stderr)
        return

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = r"<!-- YOUTUBE-MUSIC:START -->.*?<!-- YOUTUBE-MUSIC:END -->"
    replacement = f"<!-- YOUTUBE-MUSIC:START -->\n{block}\n<!-- YOUTUBE-MUSIC:END -->"

    if not re.search(pattern, content, flags=re.DOTALL):
        print("Warning: Target marker tags <!-- YOUTUBE-MUSIC:START/END --> not found in README.")
        return

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("Successfully updated README.md with latest YouTube Music playback!")

if __name__ == "__main__":
    update_readme()
