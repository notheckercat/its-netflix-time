import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
import random

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

CONFIG_FILE = "config.json"
CONFIG_ADMIN_ID = 1345769207588978708

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

@bot.command(name="config")
async def config(ctx, role: discord.Role):
    if ctx.author.id != CONFIG_ADMIN_ID:
        await ctx.message.delete()
        return

    config_data = load_config()
    config_data[str(ctx.guild.id)] = role.id
    save_config(config_data)

    await ctx.send(f"✅ {role.name} role can now use !addnews")

@bot.command(name="addnews")
async def addnews(ctx, tweet_url: str):
    config_data = load_config()
    guild_id = str(ctx.guild.id)
    allowed_role_id = config_data.get(guild_id)

    if allowed_role_id:
        role = ctx.guild.get_role(allowed_role_id)
        if role not in ctx.author.roles:
            await ctx.message.delete()
            return
    else:
        await ctx.message.delete()
        return

    await ctx.message.delete()

    try:
        username = tweet_url.split("/")[3]
    except:
        username = "Twitter"

    embed = discord.Embed(
        title=f"NEW {username} POST!",
        description="Check HERE!",
        color=0xe50914
    )

    button = Button(label="Open Tweet", url=tweet_url)
    view = View()
    view.add_item(button)

    await ctx.send(embed=embed, view=view)

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"!pong 🏓 | {round(bot.latency * 1000)}ms")

@bot.command(name="strange")
async def strange(ctx):
    await ctx.send("https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDI3MWQ2N2sxdzNiNXltbm1rNGN4eHFjNm95ZzBkZ2k1M2hxbGVrbSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/T9JPznkGDAxYC8m7yC/giphy.gif")

@bot.command(name="netflixtime")
async def netflixtime(ctx):
    recommendations = [
        "Stranger Things (Sci-Fi / Thriller)",
        "The Witcher (Fantasy / Action)",
        "Black Mirror (Sci-Fi / Dark)",
        "The Crown (Drama)",
        "Money Heist (Crime / Action)",
        "Squid Game (Survival / Thriller)",
        "Wednesday (Mystery / Comedy)",
        "Peaky Blinders (Crime / Drama)",
        "Lucifer (Fantasy / Crime)",
        "Breaking Bad (Drama / Crime)"
    ]

    choice = random.choice(recommendations)
    await ctx.author.send(f"🎬 Netflix Recommendation: **{choice}**")

@bot.command(name="fact")
async def fact(ctx):
    facts = [
        "Netflix was originally a DVD rental service.",
        "Stranger Things was rejected over 15 times before being accepted.",
        "Octopuses have three hearts.",
        "Honey never expires.",
        "Bananas are berries, but strawberries are not.",
        "Sharks existed before trees.",
        "The Eiffel Tower grows about 15 cm in summer.",
        "Humans blink about 20,000 times per day.",
        "Your brain uses about 20% of your body's oxygen.",
        "There are more stars in space than grains of sand on Earth.",
        "Wombat poop is cube-shaped.",
        "Coca-Cola would be green without coloring.",
        "Netflix produces more content than any TV network.",
        "The human body glows slightly, but cameras can’t detect it.",
        "Butterflies remember being caterpillars.",
        "A day on Venus is longer than a year on Venus.",
        "Tardigrades can survive in space.",
        "Scotland has 421 words for snow.",
        "There are more possible chess games than atoms in the universe.",
        "Hot water freezes faster than cold water sometimes."
    ]

    await ctx.send(f"🧠 Did you know?\n**{random.choice(facts)}**")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

TOKEN = os.environ.get("DISCORD_TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("DISCORD_TOKEN not found")
