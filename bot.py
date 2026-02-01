import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import json
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

# Load database
if os.path.exists("data.json"):
    with open("data.json") as f:
        db = json.load(f)
else:
    db = {}

# Slash command: add-channel
@bot.slash_command(name="add-channel", description="Add Twitter account to post in a channel")
async def add_channel(ctx, channel: discord.Option(discord.TextChannel), twitter_account: str):
    db[str(ctx.guild.id)] = {"channel": channel.id, "account": twitter_account, "last_post": None}
    with open("data.json", "w") as f:
        json.dump(db, f)
    await ctx.respond(f"Added {twitter_account} to post in {channel.mention}!")

# Task: check Twitter/X every 5 minutes
@tasks.loop(minutes=5)
async def check_twitter():
    for guild_id, info in db.items():
        url = info["account"]
        channel_id = info["channel"]
        last_post = info.get("last_post")

        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            tweet = soup.find("div", {"data-testid": "tweet"})
            if tweet:
                tweet_text = tweet.get_text().strip()
                if tweet_text != last_post:
                    channel = bot.get_channel(channel_id)
                    if channel:
                        await channel.send(f"New post from {url}:\n{tweet_text}")
                        db[guild_id]["last_post"] = tweet_text
                        with open("data.json", "w") as f:
                            json.dump(db, f)
        except Exception as e:
            print(f"Error fetching {url}: {e}")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    check_twitter.start()

# Run bot
bot.run(os.environ["DISCORD_TOKEN"])
