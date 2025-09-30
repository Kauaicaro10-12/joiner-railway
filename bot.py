import discord
import requests
import re

import os
import discord

TOKEN = os.environ["DISCORD_TOKEN"]

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print("Bot online!")

client.run(TOKEN)
CHANNEL_ID = 1418832448229212301  # Coloque o ID do canal

BACKEND_URL = "https://aj-production.up.railway.app/job"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def send_job(job_id):
    try:
        resp = requests.post(BACKEND_URL, json={"jobIdMobile": job_id})
        print(f"Enviado para backend: {job_id} | Resposta: {resp.text}")
    except Exception as e:
        print(f"Erro ao enviar jobId: {e}")

def extract_job_id_from_embed(embed):
    search_locations = []

    if embed.title:
        search_locations.append(embed.title)
    if embed.description:
        search_locations.append(embed.description)
    if embed.fields:
        for field in embed.fields:
            if hasattr(field, "value"):
                search_locations.append(field.value)
    if embed.footer and hasattr(embed.footer, "text"):
        search_locations.append(embed.footer.text)

    for text in search_locations:
        # Regex pega Job ID entre crase, aspas simples/duplas ou sem nada
        match = re.search(r"Job ID:\s*['\"]?([a-fA-F0-9\-]{36})['\"]?", text)
        if match:
            return match.group(1).strip()
    return None

@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")

@client.event
async def on_message(message):
    if message.channel.id != CHANNEL_ID:
        return

    job_id = None
    if message.embeds:
        for embed in message.embeds:
            job_id = extract_job_id_from_embed(embed)
            if job_id:
                send_job(job_id)
            else:
                print("--- Embed sem Job ID ---")
                print(embed.to_dict())
    else:
        match = re.search(r"Job ID:\s*['\"]?([a-fA-F0-9\-]{36})['\"]?", message.content)
        if match:
            job_id = match.group(1).strip()
            send_job(job_id)

client.run(TOKEN)
