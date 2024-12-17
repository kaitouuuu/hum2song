import os
import yt_dlp

def download_youtube_audio(url, output_folder="downloads"):
    """Download audio from YouTube using yt-dlp and convert it to MP3."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'noprogress': False
        }
        print("Starting download with yt-dlp...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')
            print(f"Audio downloaded and converted successfully: {file_path}")
            return file_path
    except Exception as e:
        print(f"Error downloading or converting YouTube audio: {e}")
        return None

if __name__ == "__main__":
    youtube_link = input("Enter the YouTube URL: ")
    mp3_file_path = download_youtube_audio(youtube_link)
