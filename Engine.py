import re
import time
import random
import threading
import concurrent.futures
from collections import Counter
from pathlib import Path

import requests
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

PYPI_SIMPLE_INDEX = "https://pypi.org/simple/"
PYPI_JSON_TEMPLATE = "https://pypi.org/pypi/{name}/json"
PYPI_PROJECT_TEMPLATE = "https://pypi.org/project/{name}/"
USER_AGENT = "Mozilla/5.0 (compatible; PyModuleGenie/1.0; +https://pypi.org)"
CACHE_DIR = Path.home() / ".pymodule_genie_cache"
CACHE_FILE = CACHE_DIR / "pypi_index.txt"
CACHE_MAX_AGE_SECONDS = 7 * 24 * 3600

MODULE_DB = [
    dict(name="streamlit", category="Web App", install="streamlit",
         tags="web app dashboard ui interface frontend interactive quick prototype data app",
         description="Turns a Python script into a shareable interactive web app in minutes.",
         example='''import streamlit as st
st.title("Hello World")
name = st.text_input("Your name")
st.write(f"Hi, {name} 👋")'''),
    dict(name="flask", category="Web App", install="flask",
         tags="web app backend api server website route microframework rest",
         description="A lightweight web framework for building websites and REST APIs.",
         example='''from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Hello World!"

app.run(debug=True)'''),
    dict(name="fastapi", category="Web App", install="fastapi uvicorn",
         tags="web app backend api server rest async fast microservice validation",
         description="A modern, high-performance web framework for building APIs with automatic docs.",
         example='''from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

# run: uvicorn main:app --reload'''),
    dict(name="django", category="Web App", install="django",
         tags="web app backend full stack website cms admin panel orm",
         description="A batteries-included full-stack web framework with an admin panel and ORM.",
         example='''# terminal
django-admin startproject mysite
cd mysite
python manage.py runserver'''),
    dict(name="pandas", category="Data", install="pandas",
         tags="data analysis csv excel dataframe table clean transform spreadsheet",
         description="The go-to library for loading, cleaning, filtering, and analyzing tabular data.",
         example='''import pandas as pd
df = pd.read_csv("data.csv")
print(df.describe())'''),
    dict(name="numpy", category="Data", install="numpy",
         tags="math array numeric matrix vector scientific computation linear algebra",
         description="Fast numerical computing with n-dimensional arrays.",
         example='''import numpy as np
arr = np.array([1, 2, 3])
print(arr.mean(), arr.std())'''),
    dict(name="matplotlib", category="Visualization", install="matplotlib",
         tags="chart plot graph visualization line bar histogram figure",
         description="The classic plotting library for static charts and graphs.",
         example='''import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
plt.savefig("plot.png")'''),
    dict(name="plotly", category="Visualization", install="plotly",
         tags="chart plot graph visualization interactive dashboard 3d web",
         description="Creates interactive, zoomable charts perfect for dashboards and web apps.",
         example='''import plotly.express as px
fig = px.bar(x=["A", "B"], y=[10, 20])
fig.show()'''),
    dict(name="scikit-learn", category="Machine Learning", install="scikit-learn",
         tags="machine learning ml model classifier regression clustering predict train",
         description="The standard toolkit for classical machine learning.",
         example='''from sklearn.linear_model import LinearRegression
model = LinearRegression().fit(X, y)
print(model.predict(X_new))'''),
    dict(name="tensorflow", category="Machine Learning", install="tensorflow",
         tags="machine learning deep learning neural network ai model train gpu",
         description="Google's deep learning framework for building and training neural networks.",
         example='''import tensorflow as tf
model = tf.keras.Sequential([tf.keras.layers.Dense(10)])
model.compile(optimizer="adam", loss="mse")'''),
    dict(name="pytorch", category="Machine Learning", install="torch",
         tags="machine learning deep learning neural network ai model train research",
         description="A flexible deep learning framework favored for research.",
         example='''import torch
x = torch.tensor([1.0, 2.0, 3.0])
print(x * 2)'''),
    dict(name="openai", category="AI / LLM", install="openai",
         tags="ai chatbot llm gpt text generation assistant conversation api",
         description="Official client for calling GPT models to build chatbots and assistants.",
         example='''from openai import OpenAI
client = OpenAI()
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}])
print(resp.choices[0].message.content)'''),
    dict(name="anthropic", category="AI / LLM", install="anthropic",
         tags="ai chatbot llm claude text generation assistant conversation api",
         description="Official client for calling Claude models to build AI-powered features.",
         example='''import anthropic
client = anthropic.Anthropic()
msg = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=200,
    messages=[{"role": "user", "content": "Hello!"}])
print(msg.content)'''),
    dict(name="langchain", category="AI / LLM", install="langchain",
         tags="ai chatbot llm agent chain rag retrieval document assistant pipeline",
         description="A framework for chaining LLM calls, tools, and documents into AI agents.",
         example='''from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini")
print(llm.invoke("Tell me a joke").content)'''),
    dict(name="spacy", category="NLP", install="spacy",
         tags="nlp text language entity extraction parsing tagging fast",
         description="Industrial-strength NLP for named entity recognition and parsing.",
         example='''import spacy
nlp = spacy.load("en_core_web_sm")
doc = nlp("Apple is looking at buying a startup.")
print([(ent.text, ent.label_) for ent in doc.ents])'''),
    dict(name="Pillow", category="Image", install="Pillow",
         tags="image photo picture resize crop edit filter thumbnail convert",
         description="The essential library for opening, editing, resizing, and saving images.",
         example='''from PIL import Image
img = Image.open("photo.jpg")
img.resize((200, 200)).save("thumb.jpg")'''),
    dict(name="opencv-python", category="Computer Vision", install="opencv-python",
         tags="image video camera face detection tracking computer vision webcam",
         description="A powerful computer-vision library for image/video processing and face detection.",
         example='''import cv2
img = cv2.imread("photo.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imwrite("gray.jpg", gray)'''),
    dict(name="pydub", category="Audio", install="pydub",
         tags="audio sound music edit convert mix mp3 wav",
         description="Simple, high-level audio editing: slicing, joining, converting formats.",
         example='''from pydub import AudioSegment
sound = AudioSegment.from_mp3("song.mp3")
sound[:5000].export("clip.mp3", format="mp3")'''),
    dict(name="SpeechRecognition", category="Speech", install="SpeechRecognition",
         tags="speech voice recognition transcribe microphone audio to text",
         description="Converts spoken audio into text using multiple recognition engines.",
         example='''import speech_recognition as sr
r = sr.Recognizer()
with sr.AudioFile("speech.wav") as source:
    audio = r.record(source)
print(r.recognize_google(audio))'''),
    dict(name="pyttsx3", category="Speech", install="pyttsx3",
         tags="speech voice text to speech tts offline audio",
         description="Offline text-to-speech: makes your program talk without internet.",
         example='''import pyttsx3
engine = pyttsx3.init()
engine.say("Hello there!")
engine.runAndWait()'''),
    dict(name="requests", category="Web Scraping", install="requests",
         tags="http request api download web fetch url scrape",
         description="The simplest way to send HTTP requests and talk to web APIs.",
         example='''import requests
r = requests.get("https://api.github.com")
print(r.json())'''),
    dict(name="beautifulsoup4", category="Web Scraping", install="beautifulsoup4",
         tags="scrape html parse web extract crawler",
         description="Parses HTML/XML to easily extract data from web pages.",
         example='''from bs4 import BeautifulSoup
soup = BeautifulSoup(html, "html.parser")
print(soup.title.text)'''),
    dict(name="selenium", category="Automation", install="selenium",
         tags="automation browser click form fill web testing scrape javascript",
         description="Automates real web browsers — clicking, filling forms, scraping JS-heavy sites.",
         example='''from selenium import webdriver
driver = webdriver.Chrome()
driver.get("https://example.com")
print(driver.title)'''),
    dict(name="pyautogui", category="Automation", install="pyautogui",
         tags="automation mouse keyboard click screenshot desktop bot",
         description="Controls the mouse and keyboard to automate desktop tasks.",
         example='''import pyautogui
pyautogui.click(100, 200)
pyautogui.write("Hello!")'''),
    dict(name="schedule", category="Automation", install="schedule",
         tags="automation cron job scheduler recurring task timer",
         description="A friendly way to run Python functions on a schedule.",
         example='''import schedule, time
schedule.every(10).seconds.do(lambda: print("tick"))
while True:
    schedule.run_pending()
    time.sleep(1)'''),
    dict(name="tkinter", category="GUI", install="(built-in)",
         tags="gui desktop app window button form interface native",
         description="Python's built-in GUI toolkit for simple desktop applications.",
         example='''import tkinter as tk
root = tk.Tk()
tk.Label(root, text="Hello!").pack()
root.mainloop()'''),
    dict(name="PyQt5", category="GUI", install="PyQt5",
         tags="gui desktop app window native professional interface",
         description="A feature-rich toolkit for building professional desktop apps.",
         example='''from PyQt5.QtWidgets import QApplication, QLabel
app = QApplication([])
label = QLabel("Hello!")
label.show()
app.exec_()'''),
    dict(name="pygame", category="Game Dev", install="pygame",
         tags="game 2d graphics sprite animation arcade sound",
         description="The classic library for building 2D games with sprites and sound.",
         example='''import pygame
pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("My Game")'''),
    dict(name="sqlite3", category="Database", install="(built-in)",
         tags="database sql store persist local file lightweight",
         description="Built-in, file-based SQL database — no server setup required.",
         example='''import sqlite3
conn = sqlite3.connect("app.db")
conn.execute("CREATE TABLE users (name TEXT)")'''),
    dict(name="sqlalchemy", category="Database", install="sqlalchemy",
         tags="database sql orm model query table relational",
         description="The most popular Python ORM, mapping tables to Python classes.",
         example='''from sqlalchemy import create_engine
engine = create_engine("sqlite:///app.db")
engine.connect()'''),
    dict(name="PyPDF2", category="PDF", install="PyPDF2",
         tags="pdf read merge split extract text document",
         description="Reads, merges, splits, and extracts text from PDF files.",
         example='''from PyPDF2 import PdfReader
reader = PdfReader("file.pdf")
print(reader.pages[0].extract_text())'''),
    dict(name="reportlab", category="PDF", install="reportlab",
         tags="pdf generate create report invoice document",
         description="Generates PDF documents/reports from scratch.",
         example='''from reportlab.pdfgen import canvas
c = canvas.Canvas("out.pdf")
c.drawString(100, 750, "Hello World")
c.save()'''),
    dict(name="openpyxl", category="Excel", install="openpyxl",
         tags="excel spreadsheet xlsx read write cell formula",
         description="Reads and writes Excel .xlsx files, including formulas and formatting.",
         example='''from openpyxl import Workbook
wb = Workbook()
wb.active["A1"] = "Hello"
wb.save("out.xlsx")'''),
    dict(name="python-docx", category="Word", install="python-docx",
         tags="word document docx report generate text",
         description="Creates and edits Microsoft Word .docx documents.",
         example='''from docx import Document
doc = Document()
doc.add_paragraph("Hello World")
doc.save("out.docx")'''),
    dict(name="click", category="CLI", install="click",
         tags="cli command line tool argument terminal interface",
         description="Builds beautiful, composable command-line interfaces.",
         example='''import click

@click.command()
@click.option("--name", default="World")
def hello(name):
    click.echo(f"Hello {name}!")

hello()'''),
    dict(name="rich", category="CLI", install="rich",
         tags="cli terminal pretty print color table progress bar formatting",
         description="Makes terminal output beautiful — colors, tables, progress bars.",
         example='''from rich.console import Console
console = Console()
console.print("Hello [bold magenta]World[/bold magenta]!")'''),
    dict(name="python-telegram-bot", category="Bots", install="python-telegram-bot",
         tags="bot telegram chat message automation messenger",
         description="Builds Telegram bots that respond to messages and commands.",
         example='''from telegram.ext import ApplicationBuilder
app = ApplicationBuilder().token("TOKEN").build()
app.run_polling()'''),
    dict(name="discord.py", category="Bots", install="discord.py",
         tags="bot discord chat message automation server",
         description="Builds Discord bots to automate servers and respond to messages.",
         example='''import discord
client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

client.run("TOKEN")'''),
    dict(name="folium", category="Maps", install="folium",
         tags="map geo location visualize markers interactive leaflet",
         description="Creates interactive maps with markers, overlaid on Leaflet.js.",
         example='''import folium
m = folium.Map(location=[45.5, -122.6])
folium.Marker([45.5, -122.6]).add_to(m)
m.save("map.html")'''),
    dict(name="cryptography", category="Security", install="cryptography",
         tags="encrypt decrypt security password hash secure",
         description="Provides strong encryption and hashing primitives.",
         example='''from cryptography.fernet import Fernet
key = Fernet.generate_key()
f = Fernet(key)
token = f.encrypt(b"secret message")'''),
    dict(name="pydantic", category="Data Validation", install="pydantic",
         tags="validation data model schema type checking api",
         description="Validates and parses data using Python type hints.",
         example='''from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

u = User(name="Ada", age=30)'''),
    dict(name="pytest", category="Testing", install="pytest",
         tags="test testing unit assert quality ci",
         description="The most popular testing framework — simple syntax, powerful fixtures.",
         example='''def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5

# run: pytest'''),
    dict(name="qrcode", category="Image", install="qrcode[pil]",
         tags="qr code generate image barcode label scan",
         description="The standard library for generating QR codes from text or URLs.",
         example='''import qrcode
img = qrcode.make("https://example.com")
img.save("qr.png")'''),
    dict(name="pyzbar", category="Image", install="pyzbar",
         tags="qr barcode scan decode read image detect",
         description="Reads and decodes QR codes and barcodes from images.",
         example='''from pyzbar.pyzbar import decode
from PIL import Image
result = decode(Image.open("qr.png"))
print(result[0].data)'''),
    dict(name="gTTS", category="Speech", install="gTTS",
         tags="text to speech tts voice audio google speak translate",
         description="Converts text to natural-sounding speech using Google Translate's TTS engine.",
         example='''from gtts import gTTS
tts = gTTS("Hello there!", lang="en")
tts.save("hello.mp3")'''),
    dict(name="moviepy", category="Video", install="moviepy",
         tags="video edit clip merge trim convert audio movie",
         description="Edits video files programmatically — cutting, merging, adding audio/text.",
         example='''from moviepy.editor import VideoFileClip
clip = VideoFileClip("video.mp4").subclip(0, 10)
clip.write_videofile("clip.mp4")'''),
    dict(name="Faker", category="Data", install="Faker",
         tags="fake data generate test sample mock names addresses",
         description="Generates realistic fake data (names, emails, addresses) for testing and demos.",
         example='''from faker import Faker
fake = Faker()
print(fake.name(), fake.email())'''),
    dict(name="tqdm", category="CLI", install="tqdm",
         tags="progress bar loop loading percent status",
         description="Adds a smart, low-effort progress bar to any loop.",
         example='''from tqdm import tqdm
for i in tqdm(range(100)):
    pass'''),
    dict(name="loguru", category="Logging", install="loguru",
         tags="log logging debug error track record",
         description="A much simpler, prettier alternative to Python's built-in logging module.",
         example='''from loguru import logger
logger.info("Server started")
logger.error("Something went wrong")'''),
    dict(name="watchdog", category="Automation", install="watchdog",
         tags="file system monitor watch folder change trigger automation",
         description="Watches a folder and triggers your code whenever files change.",
         example='''from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class Handler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f"Changed: {event.src_path}")'''),
    dict(name="APScheduler", category="Automation", install="APScheduler",
         tags="schedule cron job recurring task background timer",
         description="A more powerful task scheduler than 'schedule', with cron-style triggers.",
         example='''from apscheduler.schedulers.blocking import BlockingScheduler
sched = BlockingScheduler()

@sched.scheduled_job("interval", seconds=10)
def job():
    print("tick")

sched.start()'''),
    dict(name="twilio", category="Messaging", install="twilio",
         tags="sms text message phone call notify alert",
         description="Sends SMS texts and makes phone calls programmatically via the Twilio API.",
         example='''from twilio.rest import Client
client = Client("ACCOUNT_SID", "AUTH_TOKEN")
client.messages.create(to="+1234567890", from_="+0987654321", body="Hi!")'''),
    dict(name="boto3", category="Cloud", install="boto3",
         tags="aws cloud s3 storage upload lambda deploy",
         description="The official AWS SDK — talk to S3, Lambda, DynamoDB, and other AWS services.",
         example='''import boto3
s3 = boto3.client("s3")
s3.upload_file("file.txt", "my-bucket", "file.txt")'''),
    dict(name="paramiko", category="Networking", install="paramiko",
         tags="ssh remote server connect automation transfer file",
         description="Connects to remote servers over SSH to run commands or transfer files.",
         example='''import paramiko
ssh = paramiko.SSHClient()
ssh.connect("host", username="user", password="pass")
stdin, stdout, stderr = ssh.exec_command("ls")'''),
    dict(name="wordcloud", category="Visualization", install="wordcloud",
         tags="word cloud text visualize frequency image",
         description="Generates word-cloud images from text, sizing words by frequency.",
         example='''from wordcloud import WordCloud
wc = WordCloud().generate("some long text here")
wc.to_file("cloud.png")'''),
    dict(name="networkx", category="Data", install="networkx",
         tags="graph network node edge relationship visualize algorithm",
         description="Creates, analyzes, and visualizes graphs and networks.",
         example='''import networkx as nx
G = nx.Graph()
G.add_edge("A", "B")
print(nx.shortest_path(G, "A", "B"))'''),
    dict(name="gradio", category="Web App", install="gradio",
         tags="web app ui demo machine learning model interface quick",
         description="Wraps a Python/ML function in a shareable web UI in a few lines.",
         example='''import gradio as gr

def greet(name):
    return f"Hello {name}!"

gr.Interface(fn=greet, inputs="text", outputs="text").launch()'''),
    dict(name="PyJWT", category="Security", install="PyJWT",
         tags="jwt token auth authentication login security api",
         description="Encodes and decodes JSON Web Tokens for authentication systems.",
         example='''import jwt
token = jwt.encode({"user": "ada"}, "secret", algorithm="HS256")
print(jwt.decode(token, "secret", algorithms=["HS256"]))'''),
    dict(name="pymupdf", category="PDF", install="pymupdf",
         tags="pdf read extract text image convert high performance",
         description="A very fast library for extracting text and images from PDFs.",
         example='''import fitz  # pymupdf
doc = fitz.open("file.pdf")
print(doc[0].get_text())'''),
]

STOPWORDS = set("""
a an the i want to create make build for and with of my app that is in on as
using use like need would could python script your it this be will can help
me a lot get some good simple please give know how do makes creates program
also going gonna out into from
""".split())

SHORT_TECH_WORDS = {"ai", "ml", "ui", "ux", "io", "db", "cv", "qr", "os", "gc"}


def tokenize(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return [w for w in words if w not in STOPWORDS and (len(w) > 2 or w in SHORT_TECH_WORDS)]


def simple_stem(word):
    for suffix in ("ing", "ies", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            if suffix == "ies":
                return word[:-3] + "y"
            return word[: -len(suffix)]
    return word


def score_curated(user_text, db):
    tokens = tokenize(user_text)
    if not tokens:
        return []
    token_counts = Counter(tokens)
    results = []
    for mod in db:
        tag_tokens = set(re.findall(r"[a-zA-Z]+", mod["tags"].lower()))
        desc_tokens = set(re.findall(r"[a-zA-Z]+", mod["description"].lower()))
        cat_tokens = set(re.findall(r"[a-zA-Z]+", mod["category"].lower()))
        score = 0.0
        hits = 0
        for tok, weight in token_counts.items():
            if tok in tag_tokens:
                score += weight * 3
                hits += 1
            elif tok in cat_tokens:
                score += weight * 2
                hits += 1
            elif tok in desc_tokens:
                score += weight * 1
                hits += 1
        if hits > 0:
            results.append((score, mod))
    results.sort(key=lambda x: x[0], reverse=True)
    if not results:
        return []
    top_score = results[0][0]
    threshold = max(top_score * 0.4, 2.0)
    return [(s, m) for s, m in results if s >= threshold]


_pypi_index_cache = None


def load_pypi_index():
    global _pypi_index_cache
    if _pypi_index_cache is not None:
        return _pypi_index_cache
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if CACHE_FILE.exists():
        age = time.time() - CACHE_FILE.stat().st_mtime
        if age < CACHE_MAX_AGE_SECONDS:
            try:
                _pypi_index_cache = CACHE_FILE.read_text(encoding="utf-8").splitlines()
                return _pypi_index_cache
            except Exception:
                pass
    resp = requests.get(PYPI_SIMPLE_INDEX, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    names = re.findall(r'<a href="/simple/[^"]*/">([^<]+)</a>', resp.text)
    try:
        CACHE_FILE.write_text("\n".join(names), encoding="utf-8")
    except Exception:
        pass
    _pypi_index_cache = names
    return names


def _name_token_score(low, parts, tok):
    stem_tok = simple_stem(tok)
    stem_parts = [simple_stem(p) for p in parts]
    if tok in parts or stem_tok in stem_parts:
        return 3.0
    if low.startswith(tok) or low.endswith(tok) or low.startswith(stem_tok) or low.endswith(stem_tok):
        return 1.5
    if tok in low or stem_tok in low:
        return 0.75
    return 0.0


def rank_pypi_candidates(tokens, names, limit=20):
    if not tokens:
        return []
    per_token_limit = max(4, (limit * 2) // len(tokens))
    candidate_names = set()
    for tok in tokens:
        token_matches = []
        for name in names:
            low = name.lower()
            parts = re.split(r"[-_.]", low)
            s = _name_token_score(low, parts, tok)
            if s > 0:
                token_matches.append((s - min(len(name), 40) * 0.02, name))
        token_matches.sort(key=lambda x: x[0], reverse=True)
        candidate_names.update(name for _, name in token_matches[:per_token_limit])

    scored = []
    for name in candidate_names:
        low = name.lower()
        parts = re.split(r"[-_.]", low)
        score = 0.0
        hit_tokens = 0
        for tok in tokens:
            s = _name_token_score(low, parts, tok)
            if s > 0:
                score += s
                hit_tokens += 1
        score += hit_tokens * 1.5
        score -= min(len(name), 40) * 0.02
        scored.append((score, name))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [n for _, n in scored[:limit]]


def fetch_pypi_details(name):
    try:
        r = requests.get(PYPI_JSON_TEMPLATE.format(name=name), headers={"User-Agent": USER_AGENT}, timeout=6)
        if r.status_code != 200:
            return None
        info = r.json().get("info", {})
        summary = (info.get("summary") or "").strip()
        if len(summary) < 8:
            return None
        return dict(name=info.get("name", name), summary=summary, version=info.get("version", ""), home_page=info.get("home_page") or info.get("project_url") or "", install=info.get("name", name))
    except Exception:
        return None


def live_pypi_search(user_text, candidate_pool=25, final_n=6):
    tokens = tokenize(user_text)
    if not tokens:
        return [], None
    try:
        names = load_pypi_index()
    except Exception as e:
        return [], f"Couldn't reach PyPI right now ({e}). Check your internet connection."

    top_candidates = rank_pypi_candidates(tokens, names, limit=candidate_pool)
    if not top_candidates:
        return [], None

    details = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for result in executor.map(fetch_pypi_details, top_candidates):
            if result:
                details.append(result)

    def summary_score(pkg):
        s = pkg["summary"].lower()
        return sum(1 for t in tokens if t in s or simple_stem(t) in s)

    details.sort(key=summary_score, reverse=True)
    return details[:final_n], None


def guess_import_name(pypi_name):
    return re.sub(r"[-.]", "_", pypi_name.strip()).lower()


EXAMPLES = [
    "I want to build a chatbot that reads PDFs and answers questions",
    "I want to scrape product prices from a website and save to Excel",
    "I want to make a 2D platformer game",
    "I want to build a dashboard that shows live stock charts",
    "I want to automate sending daily email reports",
    "I want an app that removes background noise from audio recordings",
]


class PyModuleGenieApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧞 PyModule Genie")
        self.root.geometry("1200x820")
        self.root.minsize(1000, 650)

        self.categories = sorted(set(m["category"] for m in MODULE_DB))

        self._build_layout()

    def _build_layout(self):
        outer = ttk.Frame(self.root, padding=10)
        outer.pack(fill="both", expand=True)

        header = ttk.Label(outer, text="🧞 PyModule Genie", font=("Segoe UI", 18, "bold"))
        header.pack(anchor="w")
        sub = ttk.Label(outer, text="Describe what you want to build — get real Python modules, install commands, and starter code, searched live across all of PyPI.", wraplength=1080, foreground="#555")
        sub.pack(anchor="w", pady=(0, 10))

        body = ttk.Frame(outer)
        body.pack(fill="both", expand=True)

        sidebar = ttk.Frame(body, width=270, padding=(0, 0, 15, 0))
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        main = ttk.Frame(body)
        main.pack(side="left", fill="both", expand=True)

        self._build_sidebar(sidebar)
        self._build_main(main)

    def _build_sidebar(self, sidebar):
        ttk.Label(sidebar, text="⚙️ Options", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 8))

        ttk.Label(sidebar, text="Curated results to show").pack(anchor="w")
        self.top_n_var = tk.IntVar(value=5)
        ttk.Scale(sidebar, from_=2, to=8, variable=self.top_n_var, orient="horizontal", command=lambda v: self.top_n_var.set(round(float(v)))).pack(fill="x")
        ttk.Label(sidebar, textvariable=self.top_n_var).pack(anchor="e")

        ttk.Label(sidebar, text="Live PyPI results to show").pack(anchor="w", pady=(10, 0))
        self.live_n_var = tk.IntVar(value=6)
        ttk.Scale(sidebar, from_=2, to=10, variable=self.live_n_var, orient="horizontal", command=lambda v: self.live_n_var.set(round(float(v)))).pack(fill="x")
        ttk.Label(sidebar, textvariable=self.live_n_var).pack(anchor="e")

        self.use_live_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(sidebar, text="🌐 Search live on PyPI (recommended)", variable=self.use_live_var).pack(anchor="w", pady=(10, 10))

        ttk.Separator(sidebar).pack(fill="x", pady=12)

        ttk.Label(sidebar, text="📚 Browse curated categories", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.category_var = tk.StringVar(value="(none)")
        cat_dropdown = ttk.Combobox(sidebar, textvariable=self.category_var, values=["(none)"] + self.categories, state="readonly")
        cat_dropdown.pack(fill="x", pady=(4, 4))
        cat_dropdown.bind("<<ComboboxSelected>>", lambda e: self.show_category(self.category_var.get()))

        ttk.Separator(sidebar).pack(fill="x", pady=12)
        ttk.Label(sidebar, text=f"Curated set: {len(MODULE_DB)} modules. Live search: all of PyPI (~900k projects).", wraplength=240, foreground="#666").pack(anchor="w")

    def _build_main(self, main):
        search_row = ttk.Frame(main)
        search_row.pack(fill="x", pady=(0, 5))

        ttk.Label(search_row, text="💡 Describe what you want to create").pack(anchor="w")
        self.idea_text = tk.Text(search_row, height=4, font=("Segoe UI", 10), wrap="word")
        self.idea_text.pack(fill="x", pady=(2, 5))

        btn_row = ttk.Frame(search_row)
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="🎲 Surprise me", command=self.surprise_me).pack(side="left")
        ttk.Button(btn_row, text="✨ Find my modules", command=self.run_search).pack(side="left", padx=(8, 0))

        ttk.Label(search_row, text="Try one of these:").pack(anchor="w", pady=(6, 2))
        ex_row = ttk.Frame(search_row)
        ex_row.pack(fill="x")
        for ex in EXAMPLES[:3]:
            ttk.Button(ex_row, text=ex[:40] + ("..." if len(ex) > 40 else ""), command=lambda e=ex: self.run_example(e)).pack(side="left", padx=(0, 6))

        self.status_var = tk.StringVar(value="")
        ttk.Label(main, textvariable=self.status_var, foreground="#0a7d32").pack(anchor="w", pady=(8, 4))

        canvas_frame = ttk.Frame(main)
        canvas_frame.pack(fill="both", expand=True, pady=(4, 0))

        self.canvas = tk.Canvas(canvas_frame, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.results_frame = ttk.Frame(self.canvas)

        self.results_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.results_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        footer = ttk.Label(main, text="Live results come straight from PyPI's official package index and JSON API — no scraping of blocked pages, no fake data.", wraplength=880, foreground="#777")
        footer.pack(anchor="w", pady=(10, 0))

    def surprise_me(self):
        self.idea_text.delete("1.0", "end")
        self.idea_text.insert("1.0", random.choice(EXAMPLES))

    def run_example(self, ex):
        self.idea_text.delete("1.0", "end")
        self.idea_text.insert("1.0", ex)
        self.run_search()

    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def add_code_block(self, parent, code_text, height=None):
        if height is None:
            height = min(max(code_text.count("\n") + 1, 1), 12)
        box = scrolledtext.ScrolledText(parent, height=height, font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4", insertbackground="white", wrap="none")
        box.insert("1.0", code_text)
        box.configure(state="disabled")
        box.pack(fill="x", pady=(2, 8))

    def add_module_card(self, badge_text, title_text, description, install_code, example_code, badge_color="#7850ff", extra_link=None):
        card = tk.Frame(self.results_frame, bd=1, relief="solid", padx=14, pady=10, bg="#f6f5fb")
        card.pack(fill="x", pady=6, padx=2)

        badge = tk.Label(card, text=badge_text, bg=badge_color, fg="white", font=("Segoe UI", 8, "bold"), padx=8, pady=2)
        badge.pack(anchor="w")

        title = tk.Label(card, text=title_text, font=("Segoe UI", 11, "bold"), bg="#f6f5fb", anchor="w", justify="left", wraplength=880)
        title.pack(anchor="w", pady=(4, 2))

        desc = tk.Label(card, text=description, wraplength=880, justify="left", bg="#f6f5fb", fg="#333")
        desc.pack(anchor="w", pady=(0, 6))

        if extra_link:
            link = tk.Label(card, text=extra_link, fg="#1a5fb4", cursor="hand2", bg="#f6f5fb")
            link.pack(anchor="w", pady=(0, 6))
            link.bind("<Button-1>", lambda e, u=extra_link: webbrowser_open(u))

        ttk.Label(card, text="Install:", background="#f6f5fb", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.add_code_block(card, install_code, height=1)

        ttk.Label(card, text="Example usage:", background="#f6f5fb", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        self.add_code_block(card, example_code)

    def add_pip_summary(self, installs):
        if not installs:
            return
        seen = list(dict.fromkeys(installs))
        card = tk.Frame(self.results_frame, bd=1, relief="solid", padx=14, pady=10, bg="#eef7ee")
        card.pack(fill="x", pady=6, padx=2)
        ttk.Label(card, text="Everything in one line:", background="#eef7ee", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.add_code_block(card, f"pip install {' '.join(seen)}", height=1)

    def run_search(self):
        idea = self.idea_text.get("1.0", "end").strip()
        if not idea:
            messagebox.showinfo("Missing idea", "Type an idea first — even a short sentence works, e.g. 'automate my Instagram posts'.")
            return

        self.clear_results()
        self.status_var.set("Searching...")
        self.root.update_idletasks()

        top_n = self.top_n_var.get()
        curated_matches = score_curated(idea, MODULE_DB)[:top_n]
        use_live = self.use_live_var.get()

        if curated_matches:
            self.status_var.set(f"Found {len(curated_matches)} curated matches for: {idea}")
            installs = [m["install"] for _, m in curated_matches if m["install"] != "(built-in)"]
            self.add_pip_summary(installs)
            header = tk.Label(self.results_frame, text="✅ Hand-picked, tested recommendations", font=("Segoe UI", 12, "bold"))
            header.pack(anchor="w", pady=(4, 4))
            for score, mod in curated_matches:
                install_code = "Built-in — no install needed" if mod["install"] == "(built-in)" else f"pip install {mod['install']}"
                self.add_module_card(mod["category"], f"📦 {mod['name']}", mod["description"], install_code, mod["example"])

        if use_live:
            live_n = self.live_n_var.get()
            threading.Thread(target=self._run_live_search, args=(idea, live_n), daemon=True).start()
        elif not curated_matches:
            self.status_var.set("No matches found. Try describing your idea with a few more concrete nouns/verbs (e.g. 'read pdf', 'scrape website', 'face detection').")

    def _run_live_search(self, idea, live_n):
        live_matches, live_error = live_pypi_search(idea, candidate_pool=25, final_n=live_n)
        self.root.after(0, lambda: self._show_live_results(live_matches, live_error))

    def _show_live_results(self, live_matches, live_error):
        header = tk.Label(self.results_frame, text="🌐 More matches, searched live on PyPI", font=("Segoe UI", 12, "bold"))
        header.pack(anchor="w", pady=(10, 2))
        sub = tk.Label(self.results_frame, text="Ranked by keyword relevance, not popularity — skim summaries before installing.", fg="#666")
        sub.pack(anchor="w", pady=(0, 4))

        if live_error:
            self.status_var.set(live_error)
            return

        if not live_matches:
            tk.Label(self.results_frame, text="No additional live matches found beyond the curated list above.", fg="#666").pack(anchor="w")
            return

        for pkg in live_matches:
            example_code = f"import {guess_import_name(pkg['name'])}"
            self.add_module_card(f"PyPI · v{pkg['version']}", f"📦 {pkg['name']}", pkg["summary"], f"pip install {pkg['install']}", example_code, badge_color="#0096ff", extra_link=PYPI_PROJECT_TEMPLATE.format(name=pkg["install"]))

        self.status_var.set(f"Live search returned {len(live_matches)} additional packages.")

    def show_category(self, category):
        if category == "(none)":
            return
        self.clear_results()
        self.status_var.set(f"📚 {category} modules")
        for mod in [m for m in MODULE_DB if m["category"] == category]:
            install_code = "Built-in — no install needed" if mod["install"] == "(built-in)" else f"pip install {mod['install']}"
            self.add_module_card(mod["category"], f"📦 {mod['name']}", mod["description"], install_code, mod["example"])


def webbrowser_open(url):
    import webbrowser
    webbrowser.open(url)


def main():
    root = tk.Tk()
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    app = PyModuleGenieApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
