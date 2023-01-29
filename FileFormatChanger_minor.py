from moviepy.video.fx.speedx import speedx
import streamlit as st
from moviepy.editor import *
from proglog import ProgressBarLogger
from pytube import YouTube
from pytube import Playlist
from guesslang import Guess
import zipfile
from PIL import Image
import shutil
import requests
import pytesseract
import os

class MyBarLogger(ProgressBarLogger):
    def callback(self, **changes):
        # Every time the logger message is updated, this function is called with
        # the `changes` dictionary of the form `parameter: new value`.
        for (parameter, value) in changes.items():
            print('Parameter %s is now %s' % (parameter, value))

    def bars_callback(self, bar, attr, value, old_value=None):
        # Every time the logger progress is updated, this function is called
        percentage = (value / self.bars[bar]['total']) * 100
        status.progress(int(percentage))

st.set_page_config(page_title='File Converter App',layout="wide",page_icon="https://cdn.movavi.io/pages/0012/67/f97f4053080a1d1ecc3e23c4095de7e73522ea17.png")
logger = MyBarLogger()
hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                header {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
set_background = """
                <style>
                .stApp {
                     background-image: url("https://i.pinimg.com/originals/13/83/07/138307c749c670d6d5ebffcbf15fe025.jpg");
                     background-size: cover;
                }
                </style>
                """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
#st.markdown(set_background, unsafe_allow_html=True)

def Youtube_casts(url):
    Download = YouTube(url)
    resolutions = ["--select--"]
    for resolution in Download.streams.filter(progressive=True):
        resolutions.append(resolution.resolution)
    res = st.selectbox("Choose your quality: ", (resolutions))
    if (res != "--select--"):
        st.success("You choose: " + res)
        st.write("Here is your file => " + "[View/Download](" +
                 Download.streams.filter(resolution=res, progressive=True)[0].url + ")")
        st.info("Not happy with the resolutions available! You can download upto 1080p with our desktop app try now")
        items = os.getcwd() + "/Robin2bin-Video2audio-Desktop.zip"
        with open(items, "rb") as file:
            btn = st.download_button(
                label='Download desktop application here' + " (" + f'{round(os.stat(items).st_size / (1024 * 1024), 1)}' + " MB)",
                data=file,
                file_name='Robin2bin-Video2audio-Desktop.zip',
                mime="application/octet-stream"
            )

def video2audio(video):
    output = "audio_file.wav"
    video = VideoFileClip(video)
    audio = video.audio
    audio.write_audiofile(output, logger=logger)
    st.success("Successful Conversion!")
    st.audio(output)
    audio.close()
    video.close()
    os.remove(output)

def mix_vid(video,audio):
    Video = VideoFileClip(video)
    Audio = AudioFileClip(audio)
    vid_duration = Video.duration
    audio_duration = Audio.duration
    output = 'final_video.mp4'
    if (vid_duration < audio_duration or vid_duration > audio_duration):
        Audio = AudioFileClip(audio)
        Video = VideoFileClip(video).fx(speedx, vid_duration / audio_duration)
        final_clip = Video.set_audio(Audio)
    else:
        Video = VideoFileClip(video)
        Audio = AudioFileClip(audio)
        final_clip = Video.set_audio(Audio)
    final_clip.write_videofile(output, logger=logger)
    st.success("Successfull conversion")
    st.video(output)  # shows the video
    os.remove(output)
    Video.close()
    Audio.close()

with st.container():
    st.title("Format Changer App")
    st.header("Hi I am your app to change the format of your files: ")
    st.write("---")
    st.sidebar.header("Admin Portal")
    id = st.sidebar.text_input("Enter Login Id: ")
    password = hash(st.sidebar.text_input("Enter Password",type="password"))
    true_password = hash("PassFile@2023#")
    if(id and password):
        if(password == true_password):
            st.sidebar.success("Successfully loggged in as admin")
            with st.expander("ADMIN PORTAL"):
                size = 0
                for items in os.listdir():
                    file_size = os.stat(items).st_size / (1024 * 1024)
                    size += file_size
                if(800 - size < 200):
                    st.error(str(round(800 - size,2)) + " MB/800 MB")
                elif (800 - size > 200 and 800 - size < 600):
                    st.warning(str(round(800 - size,2)) + " MB/800 MB")
                elif (800 - size > 600):
                    st.success(str(round(800 - size,2)) + " MB/800 MB")
                file_uploads = st.file_uploader("Upload your file",accept_multiple_files=True)
                if file_uploads:
                    for upload in file_uploads:
                        with open(upload.name, "wb") as f:
                            f.write(upload.read())
                    st.success("uploaded successfully!")
                files = ["--select--"]
                show_files = ["--select--"]
                for items in os.listdir(os.getcwd()):
                    if (".idea" in items):
                        pass
                    elif ("requirements.txt" in items):
                        pass
                    elif (".py" in items):
                        pass
                    elif (".git" in items):
                        pass
                    elif (".streamlit" in items):
                        pass
                    else:
                        files.append(items)
                        show_files.append(items + " " + str(round(os.stat(items).st_size / (1024*1024),2)) + " MB")
                sec = st.selectbox("Choose the file you want to delete: ",show_files)
                if(sec != "--select--"):
                    os.remove(files[show_files.index(sec)])
                    st.success("Successfully deleted " + sec)
        else:
            st.sidebar.error("Incorrect id/password")


with st.container():
    st.subheader("Choose the service: ")
    left,right = st.columns(2)
    with left:
        st.subheader("Convert video files to audio files: ")
        video_file = st.file_uploader("Choose a video file", type=['mp4', 'avi'])
        st.subheader("OR")
        online_File = st.text_input("Enter Youtube URL: ")
        if(video_file):
            video = video_file.name
            with open(video,"wb") as f:
                f.write(video_file.read())
            status = st.progress(0)
            video2audio(video)
            os.remove(video_file.name)
        elif(online_File):
            Download = YouTube(online_File)
            try:
                st.write("Here is your audio file => " + "[View/Download](" +
                         Download.streams.filter(type="audio",mime_type="audio/mp4")[0].url + ")")
            except Exception as e:
                st.error("This video has no audio")

    with right:
        st.subheader("Combine audio and video files: ")
        video = None
        audio = None
        video_file = st.file_uploader("Choose your video file: ",type=['mp4','avi'])
        st.write("OR")
        online_video_File = st.text_input("Enter video youtube link: ")
        audio_file = st.file_uploader("Choose your audio file: ",type=['mp3','wav'])
        st.write("OR")
        online_audio_File = st.text_input("Enter audio youtube link: ")
        if(video == None):
            if(online_video_File):
                st.warning("Getting your video file....")
                video = "video.mp4"
                Download = YouTube(online_video_File)
                file_size = int(Download.streams.filter(only_video=True, file_extension='mp4')[0].filesize)
                st.warning("Getting your video file...." + str(round(file_size / 1048576, 2)) + " MB")
                r = requests.get(Download.streams.filter(only_video=True, file_extension='mp4')[0].url)
                st.warning("Downloading your video file...." + str(round(file_size / 1048576, 2)) + " MB")
                status = st.progress(0)
                with open(video, 'wb') as f:
                    downloaded = 0
                    for data in r.iter_content(chunk_size=1024):
                        f.write(data)
                        downloaded += len(data)
                        progress = (downloaded / file_size) * 100
                        status.progress(int(progress))
            if (video_file):
                video = video_file.name
                with open(video, "wb") as f:
                    f.write(video_file.read())
        if(audio == None):
            if(online_audio_File):
                st.warning("Getting your audio file...")
                audio = "audio.wav"
                Download = YouTube(online_audio_File)
                r = requests.get(Download.streams.filter(type="audio",mime_type="audio/mp4")[0].url)
                file_size = int(Download.streams.filter(type="audio",mime_type="audio/mp4")[0].filesize)
                st.warning("Downloading your audio file...." + str(round(file_size / 1048576,2)) + " MB")
                status = st.progress(0)
                with open(audio, 'wb') as f:
                    downloaded = 0
                    for data in r.iter_content(chunk_size=1024):
                        f.write(data)
                        downloaded += len(data)
                        progress = (downloaded / file_size) * 100
                        status.progress(int(progress))
            if (audio_file):
                audio = audio_file.name
                with open(audio, "wb") as f:
                    f.write(audio_file.read())

        if(video and audio):
            st.success("Successfully got the files now processing for results...")
            status = st.progress(0)
            mix_vid(video,audio)
            os.remove(video)
            os.remove(audio)

with st.container():
    st.header("Convert Image to text")
    file = st.file_uploader("Upload your image file here")
    if(file):
        with open(file.name, 'wb') as s:
            s.write(file.read())
        #with zipfile.ZipFile(os.getcwd() + "/Tesseract-OCR.zip", "r") as T:
             #T.extractall(path=os.getcwd() + "/tesseract")
        #pytesseract.pytesseract.tesseract_cmd = "tesseract/tesseract.exe"
        image = Image.open(file.name)
        txt = pytesseract.image_to_string(image, lang='eng')
        guess = Guess()
        prog_lang = guess.language_name(txt)
        if(prog_lang == "Python" or prog_lang == "python"):
            prog_lang = "py"
        st.success("Conversion successfull")
        st.code(txt,language=prog_lang.lower())
        shutil.rmtree(os.getcwd() + "/tesseract")
        os.remove(file.name)


with st.container():
    st.header("Youtube video downloader: ")
    url = st.text_input(label="Enter youtube URL: ")
    if(url):
        if("playlist" not in url):
            Youtube_casts(url)
        else:
            Player = Playlist(url)
            videos = ["--Select--"]
            urls = ["--select--"]
            for i in Player.video_urls:
                name = YouTube(i)
                videos.append(name.title)
                urls.append(i)
            sec_vid = st.selectbox("Choose the video: ",videos)
            if(sec_vid != "--Select--"):
                st.success("You choose = " + sec_vid)
                Youtube_casts(urls[videos.index(sec_vid)])



with st.container():
    st.write("---")
    left,middle,right_middle,right = st.columns(4)
    with left:
        st.subheader("Developer Contact: ")
        st.write("Contact us: cosmosbeta99@gmail.com")
    with middle:
        st.subheader("Explore our channel")
        st.write("[Check out here>](https://www.youtube.com/c/robin2bin)")
    with right_middle:
        st.subheader("Want to get more feature?")
        st.write("Try our desktop app version: ")
        items = os.getcwd() + "/Robin2bin-Video2audio-Desktop.zip"
        with open(items, "rb") as file:
            btn = st.download_button(
                label= 'Robin2bin-Video2audio-Desktop.zip' + " (" + f'{round(os.stat(items).st_size / (1024 * 1024),1)}' + " MB)",
                data=file,
                file_name='Robin2bin-Video2audio-Desktop.zip',
                mime="application/octet-stream"
            )
    with right:
        st.image("https://yt3.ggpht.com/ytc/AMLnZu-iZi_tq1cWBc90QKMCe3WSRXDn7L_ny9i57CSj=s900-c-k-c0x00ffffff-no-rj",width=200)
