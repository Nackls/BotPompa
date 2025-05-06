# 1. Standard library
import asyncio
import os

# 2. Third-party libraries
import discord
from discord.ext import commands
from dotenv import load_dotenv

# 3. Local application/library imports
from logging_config import setup_logging

setup_logging()

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Load all the cogs
async def load_cogs():
    # Assuming all your cogs are in a 'cogs/' folder
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and filename != "__init__.py":
            extension = f"cogs.{filename[:-3]}"  # Remove .py
            await bot.load_extension(extension)
            print(f"✅ Loaded {extension}")

@bot.event
async def on_ready():
    print(f'✅Logged in as {bot.user}!')

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())