import discord
import requests
import re
import os
import logging

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ["DISCORD_TOKEN"]
CHANNEL_ID = 1420109016373268632  # Substitua se necessário
BACKEND_URL = "https://aj-production.up.railway.app/job"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def send_job(pet_name, money_per_sec, job_id):
    payload = {
        "petName": pet_name,
        "moneyPerSec": money_per_sec,
        "jobIdMobile": job_id
    }
    try:
        resp = requests.post(BACKEND_URL, json=payload)
        logging.info(f"Enviado para backend: {payload} | Resposta: {resp.text}")
    except Exception as e:
        logging.error(f"Erro ao enviar payload: {e}")

def extract_info(text):
    """
    Extrai pet name, money per sec e job id de um texto.
    Espera formato tipo:
      🏷 Nome: Spaghetti Tualetti
      💰 Money: $540M/s
      🔢 Job ID: LENNRANDA_...
    """
    pet_name = None
    money_per_sec = None
    job_id = None

    # Pet name
    match = re.search(r"Nome:\s*\*?([^\n*]+)", text)
    if match:
        pet_name = match.group(1).strip()
    # Money per sec
    match = re.search(r"Money:\s*\**([^\n*]+)", text)
    if match:
        money_per_sec = match.group(1).strip()
    # Job ID
    match = re.search(r"Job ID:\s*\**([A-Za-z0-9_\-]+)", text)
    if match:
        job_id = match.group(1).strip()
    return pet_name, money_per_sec, job_id

def extract_info_from_embed(embed):
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
        pet_name, money_per_sec, job_id = extract_info(text)
        if pet_name and money_per_sec and job_id:
            return pet_name, money_per_sec, job_id
    return None, None, None

@client.event
async def on_ready():
    logging.info(f"Bot conectado como {client.user}")

@client.event
async def on_message(message):
    if message.channel.id != CHANNEL_ID:
        return
    if message.embeds:
        for embed in message.embeds:
            pet_name, money_per_sec, job_id = extract_info_from_embed(embed)
            if pet_name and money_per_sec and job_id:
                send_job(pet_name, money_per_sec, job_id)
            else:
                logging.warning("--- Embed sem todos os dados ---")
                try:
                    logging.warning(embed.to_dict())
                except Exception:
                    pass
    else:
        pet_name, money_per_sec, job_id = extract_info(message.content)
        if pet_name and money_per_sec and job_id:
            send_job(pet_name, money_per_sec, job_id)

client.run(TOKEN)
