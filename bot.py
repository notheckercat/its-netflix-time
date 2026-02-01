import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
import random

# === SETARE INTENTS ===
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# === COMANDA PING ===
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"!pong 🏓 | {round(bot.latency*1000)}ms")

# === COMANDA STRANGE ===
@bot.command(name="strange")
async def strange(ctx):
    gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdDI3MWQ2N2sxdzNiNXltbm1rNGN4eHFjNm95ZzBkZ2k1M2hxbGVrbSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/T9JPznkGDAxYC8m7yC/giphy.gif"
    await ctx.send(gif_url)

# === COMANDA ADDNEWS ===
@bot.command(name="addnews")
async def addnews(ctx, tweet_url: str):
    """
    Preia text + imagine dintr-un tweet public și postează în canal.
    Notă: funcționează pentru tweet-uri simple vizibile în HTML (nu API)
    """
    try:
        r = requests.get(tweet_url)
        soup = BeautifulSoup(r.text, "html.parser")

        # Extrage textul
        tweet_text = soup.find("meta", {"property": "og:description"})
        tweet_text = tweet_text["content"] if tweet_text else "No text found."

        # Extrage imaginea
        tweet_img = soup.find("meta", {"property": "og:image"})
        tweet_img = tweet_img["content"] if tweet_img else None

        # Construiește embed
        embed = discord.Embed(description=tweet_text, color=0xe50914)
        if tweet_img:
            embed.set_image(url=tweet_img)
        embed.set_footer(text=f"Tweet: {tweet_url}")

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Could not fetch tweet: {e}")

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

# === RUN BOT ===
bot.run("YOUR_DISCORD_TOKEN")
