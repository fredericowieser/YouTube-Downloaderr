import streamlit as st
import numpy as np
import pandas as pd

from streamlit_option_menu import option_menu

from src.download import download

def make_gui():
    st.set_page_config(layout="wide")
    
    # Side Bar
    with st.sidebar: mode = make_sidebar()
    
    # Pages
    if mode == "Home": home_page()
    
    
def make_sidebar():
    choose = option_menu(
        "YT-DWNLDRR", 
        [
            "Home",
        ],
        icons=[
            'house',
        ],
        menu_icon="app-indicator",
        default_index=0,
        )
    return choose


def home_page():
    st.title('YouTube Downloaderr')
    
    st.session_state.visibility = "visible"
    st.session_state.disabled = False
    
    url = st.text_input(
        "Enter the URL 👇",
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        placeholder="URL",
    )
    
    vtype = st.selectbox(
        "What kind of URL is this?",
        ('Normal Vid', 'Song', 'Album', 'Lecture Series', 'Single Lecture',
         'Podcast', 'DJ Set', 'Mix')
    )
    
    dwnld = st.button("Start Download", type="primary")
    if dwnld:
        download(url, vtype)
        
    
    
