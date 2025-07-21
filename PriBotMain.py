import discord
import os
from dotenv import load_dotenv

# Load the TOKEN from .env
load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # For member join events

client = discord.Client(intents=intents)

# Replace with your server's welcome channel ID
WELCOME_CHANNEL_ID = 1396564206890909776  # <--- CHANGE THIS

@client.event
async def on_ready():
    print(f'✅ PriBotMain is online as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send(f'Hello {message.author.mention}!')

    elif message.content.startswith('$help'):
        help_text = (
            "**PriBotMain Commands:**\n"
            "`$hello` — Receive a greeting from the bot.\n"
            "`$help` — Display this help message.\n"
            "`$privacy` — View our privacy disclaimer.\n"
        )
        await message.channel.send(help_text)

    elif message.content.startswith('$privacy'):
        privacy_text = (
            "**Privacy Disclaimer**\n"
            "PriBotMain is a private bot for the Shadow Monarch Server.\n"
            "- We do not collect, store, or share any personal data.\n"
            "- The bot processes message content only when commands are used.\n"
            "- All data is temporary and used for feature delivery.\n"
            "Contact: ShadowMonarch#1234"
        )
        await message.channel.send(privacy_text)

@client.event
async def on_member_join(member):
    channel = client.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(f'🎉 Welcome to the server, {member.mention}! Make yourself at home!')

client.run(TOKEN)