import discord
from discord.ext import commands
from discord.ui import Button, View
from openai import OpenAI
import json
import os
import random
import time

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

ai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

CONFIG_FILE = "config.json"
CONFIG_ADMIN_ID = 1345769207588978708

fact_usage = {}

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

    data = load_config()
    data[str(ctx.guild.id)] = role.id
    save_config(data)

    await ctx.send(f"✅ {role.name} role can now use !addnews")

@bot.command(name="addnews")
async def addnews(ctx, tweet_url: str):
    data = load_config()
    guild_id = str(ctx.guild.id)
    allowed_role_id = data.get(guild_id)

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
    shows = [
        "Stranger Things (Sci-Fi / Thriller)",
        "The Witcher (Fantasy / Action)",
        "Black Mirror (Sci-Fi)",
        "The Crown (Drama)",
        "Money Heist (Crime)",
        "Squid Game (Thriller)",
        "Wednesday (Mystery)",
        "Peaky Blinders (Crime)",
        "Lucifer (Fantasy)",
        "Breaking Bad (Drama)"
    ]

    pick = random.choice(shows)
    await ctx.author.send(f"🎬 Netflix Recommendation: **{pick}**")

@bot.command(name="fact")
async def fact(ctx, *, question: str = None):
    user_id = ctx.author.id
    now = time.time()

    if user_id not in fact_usage:
        fact_usage[user_id] = {"count": 0, "time": now}

    elapsed = now - fact_usage[user_id]["time"]

    if elapsed > 1800:
        fact_usage[user_id]["count"] = 0
        fact_usage[user_id]["time"] = now

    if fact_usage[user_id]["count"] >= 3:
        await ctx.send("I am too bored to say again a fact to you! Try again in 30 minutes.")
        return

    if not question:
        await ctx.send("Ask me something! Example: `!fact how rich is mr beast`")
        return

    fact_usage[user_id]["count"] += 1

    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a smart assistant that gives short, clear factual answers."
                },
                {
                    "role": "user",
                    "content": question
                }
            ],
            max_tokens=150,
            temperature=0.6
        )

        answer = response.choices[0].message.content
        await ctx.send(f"🧠 **AI FACT RESPONSE:**\n{answer}")

    except:
        await ctx.send("❌ AI service error. Try again later.")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

TOKEN = os.environ.get("DISCORD_TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("DISCORD_TOKEN not found")
