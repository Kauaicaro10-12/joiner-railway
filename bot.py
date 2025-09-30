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

def send_jobs(jobs_list):
    """
    Envia uma lista de jobs para o backend em sequência.
    """
    for job in jobs_list:
        payload = {
            "petName": job["petName"],
            "moneyPerSec": job["moneyPerSec"],
            "jobIdMobile": job["jobIdMobile"]
        }
        try:
            resp = requests.post(BACKEND_URL, json=payload)
            logging.info(f"Enviado para backend: {payload} | Resposta: {resp.text}")
        except Exception as e:
            logging.error(f"Erro ao enviar payload: {e}")

def extract_infos(text):
    """
    Extrai múltiplos pets/moneys/jobids de um texto. Espera blocos tipo:
      🏷 Nome: ...
      💰 Money: ...
      🔢 Job ID: ...
    """
    jobs = []
    # Encontrar todos os blocos usando regex multi-linha
    pattern = re.compile(
        r"Nome:\s*([^\n]+)\n.*?Money:\s*([^\n]+)\n.*?Job ID:\s*([A-Za-z0-9_\-]+)", re.MULTILINE
    )
    for match in pattern.finditer(text):
        pet_name = match.group(1).strip()
        money_per_sec = match.group(2).strip()
        job_id = match.group(3).strip()
        jobs.append({
            "petName": pet_name,
            "moneyPerSec": money_per_sec,
            "jobIdMobile": job_id
        })
    return jobs

def extract_infos_from_embed(embed):
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
    jobs = []
    for text in search_locations:
        jobs.extend(extract_infos(text))
    return jobs

@client.event
async def on_ready():
    logging.info(f"Bot conectado como {client.user}")

@client.event
async def on_message(message):
    if message.channel.id != CHANNEL_ID:
        return
    jobs = []
    if message.embeds:
        for embed in message.embeds:
            jobs.extend(extract_infos_from_embed(embed))
    else:
        jobs.extend(extract_infos(message.content))
    if jobs:
        send_jobs(jobs)

client.run(TOKEN)
