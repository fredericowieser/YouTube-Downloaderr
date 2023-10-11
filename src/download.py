import os
import sys
import time
import zipfile
import shutil
from streamlit.runtime.scriptrunner.script_run_context import SCRIPT_RUN_CONTEXT_ATTR_NAME
import streamlit as st
from threading import current_thread
from contextlib import contextmanager
from pathlib import Path
from io import StringIO


V_TYPES = (
    'Normal Vid',
    'Song',
    'Album (Playlist)',
    'Album (1 Video)',
    'Lecture Series (Playlist)',
    'Single Lecture',
    'Podcast (No Video)',
    'DJ Set (Video)',
    'Mix (No Video)',
    'Short Film',
    'Playlist'
)


@contextmanager
def st_redirect(src, dst):
    placeholder = st.empty()
    output_func = getattr(placeholder, dst)

    with StringIO() as buffer:
        old_write = src.write

        def new_write(b):
            if getattr(current_thread(), SCRIPT_RUN_CONTEXT_ATTR_NAME, None):
                buffer.write(b)
                output_func(buffer.getvalue())
            else:
                old_write(b)

        try:
            src.write = new_write
            yield
        finally:
            src.write = old_write


@contextmanager
def st_stdout(dst):
    with st_redirect(sys.stdout, dst):
        yield


@contextmanager
def set_directory(path: Path):
    """Sets the cwd within the context

    Args:
        path (Path): The path to the cwd

    Yields:
        None
    """

    origin = Path().absolute()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


def download(url, vtype):
    # Verify URL
    if url.find('youtube') == -1: return 1 

    # Clean URL
    video_id = url.split('watch?v=')[1][:11]
    
    # Create Payload
    # yt-dl: https://github.com/yt-dlp/yt-dlp
    ytdl = 'yt-dlp'
    cmd = f"{ytdl} --geo-bypass --no-check-certificate --write-description --write-link --ffmpeg-location='/opt/homebrew/bin/ffmpeg'"
    if vtype == V_TYPES[0]:
        # Normal Video
        flags = '--all-subs --embed-thumbnail --no-playlist'
    elif vtype == V_TYPES[1]:
        # Song
        flags = '--extract-audio --metadata-from-title --no-playlist'
    elif vtype == V_TYPES[2]:
        # Album (Playlist)
        flags = '--extract-audio --metadata-from-title --yes-playlist'
    elif vtype == V_TYPES[3]:
        # Album (1 Video)
        flags = '--extract-audio --metadata-from-title --no-playlist --write-comments --split-chapters'
    elif vtype == V_TYPES[4]:
        # Lecture Series
        flags = '--embed-subs --embed-thumbnail --yes-playlist '
    elif vtype == V_TYPES[5]:
        # Single Lecture
        flags = '--embed-subs --write-auto-subs --embed-thumbnail --no-playlist'
    elif vtype == V_TYPES[6]:
        # Podcast
        flags = '--extract-audio --metadata-from-title --no-playlist'
    elif vtype == V_TYPES[7]:
        # DJ Set
        flags = '--metadata-from-title --no-playlist --write-comments --split-chapters'
    elif vtype == V_TYPES[8]:
        # Mix
        flags = '--extract-audio --metadata-from-title --no-playlist --write-comments --split-chapters'
    elif vtype == V_TYPES[9]:
        # Short Film
        flags = '--all-subs --embed-thumbnail --no-playlist'
    elif vtype == V_TYPES[10]:
        # Playlist
        flags = '--all-subs --embed-thumbnail --yes-playlist'
    
    
    payload = f'{cmd}{flags} {url}'
        
    # Execute Command to Download File(s) to TMP directory
    # Make folder name = tmp_timestamp (unix time)
    current_dir = os.getcwd()
    new_dir = f'tmp_{int(time.time())}'
    final_dir = os.path.join(current_dir, new_dir)
    if not os.path.exists(final_dir):
        os.makedirs(final_dir)
    
    with set_directory(final_dir):
        with st_stdout("code"):
            os.system(payload)
            
    # Create Zip File
    zip_name = f"{[path for path in Path(final_dir).iterdir()][0].name.split('].')}]"
    with zipfile.ZipFile(f"{zip_name}.zip", mode="w") as archive:
        for file_path in Path(final_dir).iterdir():
            archive.write(file_path, arcname=file_path.name)
    
    # Create Button To Download Zip File
    with open(f"{zip_name}.zip", "rb") as file:
        btn = st.download_button(
            label="Download Compression",
            data=file,
            file_name=f"{zip_name}.zip",
          )
    
    # Delete TMP directory
    shutil.rmtree(final_dir)
    os.remove(f"{zip_name}.zip")
    