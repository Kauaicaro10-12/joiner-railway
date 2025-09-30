import discord
import requests
import re
import os
import logging

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ["DISCORD_TOKEN"]

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print("Bot online!")

client.run(TOKEN)

CHANNEL_ID = 1420108999075958888  # Substitua se necessário
BACKEND_URL = "https://aj-production.up.railway.app/job"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def send_job(job_id):
    try:
        resp = requests.post(BACKEND_URL, json={"jobIdMobile": job_id})
        logging.info(f"Enviado para backend: {job_id} | Resposta: {resp.text}")
    except Exception as e:
        logging.error(f"Erro ao enviar jobId: {e}")

def extract_job_id(text):
    """
    Aceita tanto Job ID em formato UUID quanto criptografado (LENNRANDA_...).
    """
    match = re.search(
        r"Job ID:\s*['\"]?((?:[a-fA-F0-9\-]{36})|(?:LENNRANDA_[A-Za-z0-9]+))['\"]?",
        text
    )
    if match:
        return match.group(1).strip()
    return None

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
        job_id = extract_job_id(text)
        if job_id:
            return job_id
    return None

@client.event
async def on_ready():
    logging.info(f"Bot conectado como {client.user}")

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
                logging.warning("--- Embed sem Job ID ---")
                try:
                    logging.warning(embed.to_dict())
                except Exception:
                    pass
    else:
        job_id = extract_job_id(message.content)
        if job_id:
            send_job(job_id)

client.run(TOKEN)
