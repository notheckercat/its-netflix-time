import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
import random  # <--- asta trebuie pentru !netflixtime

# === INTENTS ===
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

CONFIG_FILE = "config.json"
CONFIG_ADMIN_ID = 1345769207588978708  # Doar acest user poate folosi !config

# === Helper pentru roluri permise ===
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

# === COMANDA CONFIG ===
@bot.command(name="config")
async def config(ctx, role: discord.Role):
    if ctx.author.id != CONFIG_ADMIN_ID:
        await ctx.message.delete()
        return
    config = load_config()
    config[str(ctx.guild.id)] = role.id
    save_config(config)
    await ctx.send(f"✅ {role.name} role can now use !addnews.")

# === COMANDA ADDNEWS ===
@bot.command(name="addnews")
async def addnews(ctx, tweet_url: str):
    config = load_config()
    guild_id = str(ctx.guild.id)
    allowed_role_id = config.get(guild_id)

    if allowed_role_id:
        allowed_role = ctx.guild.get_role(allowed_role_id)
        if allowed_role not in ctx.author.roles:
            await ctx.message.delete()
            return
    else:
        await ctx.message.delete()
        return

    await ctx.message.delete()

    try:
        username = tweet_url.split("/")[3]
    except IndexError:
        username = "Unknown"

    embed = discord.Embed(
        title=f"NEW {username} POST!",
        description="Check it here!",
        color=0xe50914
    )

    button = Button(label="Go to Tweet", url=tweet_url)
    view = View()
    view.add_item(button)

    await ctx.send(embed=embed, view=view)

# === COMANDA PING ===
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"!pong 🏓 | {round(bot.latency*1000)}ms")

# === COMANDA STRANGE ===
@bot.command(name="strange")
async def strange(ctx):
    gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDI3MWQ2N2sxdzNiNXltbm1rNGN4eHFjNm95ZzBkZ2k1M2hxbGVrbSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/T9JPznkGDAxYC8m7yC/giphy.gif"
    await ctx.send(gif_url)

# === COMANDA NETFLIXTIME ===
@bot.command(name="netflixtime")
async def netflixtime(ctx):
    recommendations = [
        "Stranger Things (Sci-Fi / Thriller)",
        "The Crown (Drama / Historical)",
        "Black Mirror (Sci-Fi / Anthology)",
        "The Witcher (Fantasy / Action)",
        "Bridgerton (Romance / Drama)",
        "Squid Game (Thriller / Survival)",
        "BoJack Horseman (Animation / Comedy / Drama)"
    ]
    choice = random.choice(recommendations)
    await ctx.author.send(f"🎬 Netflix Recommendation for you: **{choice}**")

# === ON READY ===
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# === RUN BOT cu variabilă de mediu ===
TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    print("❌ Error: DISCORD_TOKEN environment variable not set.")
else:
    bot.run(TOKEN)
