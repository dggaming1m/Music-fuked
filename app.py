# main.py (Single File Bot Setup)
import os
import asyncio
import subprocess
import random
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped, InputStream
from yt_dlp import YoutubeDL

# === CONFIGURATION ===
API_ID = 20678144  # Replace with your API ID
API_HASH = "53a508a38171fc32fd4bfa835966266e"  # Replace with your API HASH
BOT_TOKEN = "7979668317:AAFsV507I33ZWu4H2TPTEUtoBXoLqN0SuOg"  # Replace with your BOT TOKEN
MONGO_URI = "mongodb+srv://dggaming:dggaming@cluster0.qnfxnzm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Optional (only if using database)
OWNER_ID = 5670174770  # Replace with your Telegram user ID
CHANNEL_LINK = "https://t.me/dg_gaming_1m0"  # Replace with your channel

# === SETUP CLIENT ===
app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
pytgcalls = PyTgCalls(app)
downloads_dir = "downloads"
os.makedirs(downloads_dir, exist_ok=True)

# === MUSIC: /play ===
@app.on_message(filters.command("play"))
async def play(_, message):
    if len(message.command) < 2:
        return await message.reply("Please enter a song name.")
    query = message.text.split(maxsplit=1)[1]
    msg = await message.reply(f"Searching for: `{query}`")
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': f'{downloads_dir}/%(title)s.%(ext)s',
    }
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
            title = info['title']
            file_path = ydl.prepare_filename(info)
        except Exception as e:
            return await msg.edit(f"Error: {e}")
    await pytgcalls.join_group_call(
        message.chat.id,
        InputStream(AudioPiped(file_path)),
        stream_type="local",
    )
    await msg.edit(f"Now playing: **{title}**")

# === STOP MUSIC: /stop ===
@app.on_message(filters.command("stop"))
async def stop(_, message):
    await pytgcalls.leave_group_call(message.chat.id)
    await message.reply("Stopped playback.")

# === PROMOTIONS ===
@app.on_message(filters.command("promote") & filters.user(OWNER_ID))
async def promote(_, message):
    await message.reply(f"Check out our channel: {CHANNEL_LINK}")

@app.on_message(filters.command("autopromo"))
async def auto_promo(_, msg):
    if "join" in msg.text.lower():
        await msg.reply(f"Welcome! Subscribe to our channel: {CHANNEL_LINK}")

# === KIDNAP ===
@app.on_message(filters.command("kidnap"))
async def kidnap(_, message):
    if not message.reply_to_message:
        return await message.reply("Reply to someone to kidnap.")
    user = message.reply_to_message.from_user
    delay = random.randint(2, 10)
    await message.reply(f"Kidnapping {user.mention} in {delay} seconds...")

# === VIDEO DOWNLOAD (OBS Needed): /vplay ===
@app.on_message(filters.command("vplay"))
async def video_play(_, message):
    if len(message.command) < 2:
        return await message.reply("Please provide video name.")
    query = message.text.split(maxsplit=1)[1]
    msg = await message.reply(f"Searching for video: `{query}`")
    try:
        with YoutubeDL({'format': 'bestvideo[ext=mp4]+bestaudio/best', 'outtmpl': 'video_temp.%(ext)s'}) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
            filename = ydl.prepare_filename(info)
    except Exception as e:
        return await msg.edit(f"Failed: {e}")
    await msg.edit(f"Streaming video: **{info['title']}**\n\nNow open Telegram Desktop, join video chat, and select **OBS Virtual Camera**.")
    subprocess.Popen([
        "ffmpeg", "-re", "-i", filename, "-f", "dshow", "-vcodec", "rawvideo",
        "-pix_fmt", "yuv420p", "-video_size", "1280x720", "-framerate", "30",
        "-i", "video=OBS-Camera", "-map", "0:v", "-map", "0:a", "-f", "dshow", "video=OBS-Camera"
    ])

# === START COMMAND ===
@app.on_message(filters.command("start"))
async def start(_, msg):
    await msg.reply("Bot is online and ready for 2025!")

# === START APP ===
app.start()
pytgcalls.start()
print("Bot is running...")
app.idle()
