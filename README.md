# Hum to Song: Song Search from Melody 🎤

Welcome to the **Hum to Song** project! This system allows users to find songs by simply humming or singing a melody. It leverages signal processing and machine learning techniques to match your vocal input against a database of songs, making music discovery intuitive and accessible, even when you don't know the lyrics or artist.

## Features

*   **Query by Humming/Singing:** Input a melody by humming or singing into your microphone.
*   **Robust Melody Matching:** Utilizes Dynamic Time Warping (DTW) and its variants (FastDTW, Matrix DTW) to accurately compare melodies, accounting for variations in tempo, pitch, and rhythm.
*   **Audio-to-MIDI Conversion:** Converts raw audio (both database songs and user input) into MIDI format, focusing on the core melodic information. This uses a state-of-the-art model based on ICASSP 2022 Vocal Transcription.
*   **YouTube Data Sourcing:** Scripts to crawl and process audio data from YouTube Music to build the song database.
*   **Database Management:** Users can add new songs to the database, expanding its capabilities.
*   **User-Friendly Interface:** A GUI for easy interaction – humming, searching, and viewing results.

## 🛠️ How It Works (Pipeline)

The system follows a multi-step pipeline:

1.  **Data Acquisition & Preparation (for Database Songs):**
    *   **YouTube Crawler:** Uses `yt-dlp` to download audio from specified YouTube URLs (songs/playlists).
    *   **MP3 Conversion:** Converts downloaded audio to MP3 format.
    *   **Audio-to-MIDI:** The core audio processing step. MP3 files are converted to MIDI format, extracting the primary melody using a machine learning model (inspired by [ICASSP 2022 Vocal Transcription, Kum et al.](https://github.com/keums/icassp2022-vocal-transcription) - *if this is the exact one, link it*). This creates our song database.

2.  **Query Processing (User Input):**
    *   **Hum Recording:** The user hums or sings a melody, which is recorded.
    *   **Audio-to-MIDI:** The recorded hum is also converted into a MIDI representation using the same melody extraction process.

3.  **Melody Matching:**
    *   **Dynamic Time Warping (DTW):** The MIDI sequence from the user's hum (query) is compared against MIDI sequences in the song database.
    *   **Subsequence Matching:** DTW is applied to find the best matching *segment* within the database songs, as a hum usually represents only a part of a song.
    *   **Optimized DTW:** Variants like Matrix DTW and FastDTW are employed to improve efficiency for searching through potentially large databases.

4.  **Results Display:**
    *   The system presents a list of probable song matches through the GUI, along with metadata like song title, artist, and album (if available).

## 💻 Technologies Used
*   **Python:** Main programming language.
*   **yt-dlp:** For downloading audio from YouTube.
*   **Librosa / Essentia / similar:** For audio signal processing features. (Specify if you used particular ones)
*   **PrettyMIDI / Mido:** For MIDI file manipulation and processing. (Specify if you used particular ones)
*   **NumPy / SciPy:** For numerical operations.
*   **FastDTW / custom DTW implementation:** For Dynamic Time Warping.
*   **TensorFlow / PyTorch:** For the Audio-to-MIDI machine learning model. (Specify if applicable)
*   **Tkinter / PyQt / Kivy:** For the Graphical User Interface. (Specify which one you used)
*   **[ICASSP 2022 Vocal Transcription Model](https://github.com/keums/icassp2022-vocal-transcription):** (Or similar) For melody extraction.

## 🚀 Getting Started

### Prerequisites
*   Python 3.x
*   Pip (Python package installer)
*   FFmpeg (often required by `yt-dlp` and audio libraries for format conversion)
   
### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/kaitouuuu/hum2song.git
    cd hum2song
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

1.  **Start the application:**
    ```bash
    python main.py
    ```
2.  Use the GUI to record your hum, search for songs, or add new songs to the database.

## 🧑‍🤝‍🧑 Our Team
This project was developed by:
*   [**Le Nguyen Minh Hieu** ](https://github.com/kaitouuuu)
*   [**To Ngoc Hung**](https://github.com/Kas1902)
*   [**Le Phan Minh Khoa**](https://github.com/khoalephanminh)
*   [**Nguyen Xuan Minh**](https://github.com/SpringMinh)
*   [**Pham Trung Nghia**](https://github.com/Nghia260104)

## 🙏 Acknowledgements

*   This project builds upon concepts and methods presented in various MIR (Music Information Retrieval) research.
*   Special thanks to the authors of the [ICASSP 2022 Vocal Transcription paper (Kum et al.)](https://ieeexplore.ieee.org/document/9747903) for their work on melody extraction, which inspired parts of our audio-to-MIDI pipeline.
*   Libraries used: `yt-dlp`, `fastdtw`, etc.
