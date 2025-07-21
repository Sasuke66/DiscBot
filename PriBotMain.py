import discord
from discord.ext import commands
from discord import FFmpegPCMAudio, app_commands
import yt_dlp
import os
from dotenv import load_dotenv
from keep_alive import keep_alive

keep_alive()

# Load token from .env
load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="$", intents=intents)

WELCOME_CHANNEL_ID = 1396564206890909776  # Replace with your welcome channel ID


@bot.event
async def on_ready():
    print(f"✅ PriBotMain is online as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(f'🎉 Welcome to the server, {member.mention}! Make yourself at home!')


@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.mention}!')


@bot.command()
async def helpme(ctx):
    help_text = (
        "**PriBotMain Commands:**\n"
        "`$hello` — Receive a greeting.\n"
        "`$helpme` — Display this help message.\n"
        "`$privacy` — View the privacy disclaimer.\n"
        "`$join` — Join your voice channel.\n"
        "`$play <YouTube URL>` — Play music.\n"
        "`$stop` — Stop music.\n"
        "`$leave` — Leave voice channel.\n"
        "`$addrole <@user> <@role>` — Add a role to a user.\n"
        "`$removerole <@user> <@role>` — Remove a role.\n"
        "`$makemod <@user>` — Make a user a moderator.\n"
        "`/music <song name>` — Play music using slash command.\n"
        "`/stopmusic` — Stop music and disconnect."
    )
    await ctx.send(help_text)


@bot.command()
async def privacy(ctx):
    await ctx.send(
        "**Privacy Disclaimer**\n"
        "PriBotMain is a private-use bot.\n"
        "- We do not store or share any data.\n"
        "- Commands process data only when used.\n"
        "Contact: ShadowMonarch#1234"
    )


# Role Management
@bot.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"✅ Added {role.name} to {member.mention}")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f"✅ Removed {role.name} from {member.mention}")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def makemod(ctx, member: discord.Member):
    mod_role = discord.utils.get(ctx.guild.roles, name="Moderator")
    if not mod_role:
        mod_role = await ctx.guild.create_role(name="Moderator", permissions=discord.Permissions(manage_messages=True))
        await ctx.send("✅ Created 'Moderator' role.")
    await member.add_roles(mod_role)
    await ctx.send(f"✅ {member.mention} is now a Moderator!")


# Voice Control Commands
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send(f"✅ Joined {ctx.author.voice.channel.name}")
    else:
        await ctx.send("❌ You are not in a voice channel!")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("✅ Left the voice channel.")
    else:
        await ctx.send("❌ I'm not in a voice channel!")


@bot.command()
async def play(ctx, url):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("❌ You are not in a voice channel!")
            return

    ydl_opts = {'format': 'bestaudio', 'quiet': True}
    ffmpeg_opts = {'options': '-vn'}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        source = FFmpegPCMAudio(url2, **ffmpeg_opts)
        ctx.voice_client.play(source)
        await ctx.send(f"🎶 Now playing: **{info['title']}**")


@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("🛑 Music stopped.")
    else:
        await ctx.send("❌ I'm not playing anything.")

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"❌ Error: {str(error)}")


@bot.tree.command(name="music", description="Play a song from YouTube search.")
@app_commands.describe(song="Name of the song to play")
async def music(interaction: discord.Interaction, song: str):
    if not interaction.user.voice:
        await interaction.response.send_message("❌ You must be in a voice channel.", ephemeral=True)
        return

    await interaction.response.defer()

    if not interaction.guild.voice_client:
        await interaction.user.voice.channel.connect()

    vc = interaction.guild.voice_client

    ydl_opts = {'format': 'bestaudio', 'quiet': True, 'default_search': 'ytsearch'}
    ffmpeg_opts = {'options': '-vn'}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song, download=False)['entries'][0]
            url2 = info['url']
            source = FFmpegPCMAudio(url2, **ffmpeg_opts)
            vc.play(source)
            await interaction.followup.send(f"🎶 Now playing: **{info['title']}**")
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}")


@bot.tree.command(name="stopmusic", description="Stop music and leave the voice channel.")
async def stopmusic(interaction: discord.Interaction):
    vc = interaction.guild.voice_client
    if vc and vc.is_connected():
        await vc.disconnect()
        await interaction.response.send_message("🛑 Music stopped and disconnected.")
    else:
        await interaction.response.send_message("❌ I'm not in a voice channel.")


bot.run(TOKEN)