import discord
import aiohttp
import os
from gtts import gTTS

FASTAPI_URL = "http://localhost:8001/phq"
DISCORD_BOT_TOKEN = "MTM5ODY5NjI0NTg3ODMyNTM2MA.GLVauZ.ggyo0SCubllz39l2cOW0Tmtb8Lk-AaYlzDTp64"

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = discord.Client(intents=intents)
voice_client = None  # global tracker

@client.event
async def on_ready():
    print(f"✅ Logged in as {client.user}")

@client.event
async def on_message(message):
    global voice_client

    if message.author == client.user:
        return

    # Join voice channel
    if message.content.lower().startswith("!join"):
        if message.author.voice:
            channel = message.author.voice.channel
            voice_client = await channel.connect()
            await message.channel.send("🎙️ Joined the voice channel!")
        else:
            await message.channel.send("❌ You're not in a voice channel.")
        return

    # Leave voice channel
    if message.content.lower().startswith("!leave"):
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            await message.channel.send("👋 Left the voice channel.")
        else:
            await message.channel.send("❌ I'm not in a voice channel.")
        return

    # Chatbot response + voice
    async with aiohttp.ClientSession() as session:
        try:
            payload = {"user_response": message.content}
            async with session.post(FASTAPI_URL, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    reply = data.get("response", "🤖 No reply from bot.")
                    await message.channel.send(reply)

                    # If in voice channel, speak the reply
                    if voice_client and voice_client.is_connected():
                        tts = gTTS(reply)
                        tts.save("reply.mp3")
                        voice_client.play(discord.FFmpegPCMAudio("reply.mp3"))
                else:
                    await message.channel.send("⚠️ Bot backend error.")
        except Exception as e:
            print(f"Exception: {e}")
            await message.channel.send(f"🚨 Error: {e}")

client.run(DISCORD_BOT_TOKEN)
