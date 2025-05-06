# 1. Standard library
import asyncio
import logging
import re

# 2. Third-party libraries
import discord
from discord.ext import commands
import yt_dlp

# 3. Local application/library imports

# Create a logger for this module
logger = logging.getLogger(__name__)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = asyncio.Queue()

    @commands.command()
    async def play(self, ctx, *, url):
        if not Music._is_valid_youtube_url(url):
            await ctx.send("❗ Please provide a valid YouTube URL.")
            return
    
        vc = await self._ensure_correct_channel(ctx)
        if not vc:
            return
        
        await self.song_queue.put((ctx, url))
        await ctx.send("Added song to queu: {url}.")
        logger.info(f"Added song to queu: {url}")
    
        if not vc.is_playing():
            await self._play_songs(vc)
    
    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("👋 Disconnected.")
            logger.info("Bot disconnected from voice channel.")

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Skipped.")
            logger.info("Song skipped.")

    # --- PRIVATE METHODS BELOW ---


    # Play songs from the queue
    async def _play_songs(self, vc):
        while not self.song_queue.empty():
            ctx, url = await self.song_queue.get()
            info = await self._fetch_youtube_info(url)
            if info is None:
                await ctx.send("❌ Error fetching song. Skipping.")
                logger.warning(f"Failed to fetch seng info for: {url}")
                continue

            FFMPEG_OPTIONS = {
                'options': '-vn'
            }

            try:
                source = discord.FFmpegPCMAudio(info['url'], **FFMPEG_OPTIONS)

                def after_play(err):
                    if err:
                        logger.error(f"Error: {err}")
                    asyncio.run_coroutine_threadsafe(self._play_songs(vc), self.bot.loop)
                vc.play(source, after = after_play)

                await ctx.send(f"🎶 Now playing: **{info['title']}**")
                logger.info(f"Now playing: {info['title']}")

            except Exception as e:
                logger.exception(f"Error during playback: {e}")

    # Ensure bot is in correct voice channel or handle switching
    async def _ensure_correct_channel(self, ctx):
        """Ensure bot is in correct voice channel or handle switching."""
        user_vc = ctx.author.voice.channel if ctx.author.voice else None
        voice_client = ctx.voice_client

        # The user is not in a voice channel
        if not user_vc:
            await ctx.send("You need to be in a voice channel.")
            logger.warning("User is not in a voice channel.")
            return None

        # Bot is already in a voice channel
        if voice_client:
            # Bot and user are in different voice channels
            if voice_client.channel != user_vc:
                # The bot is idle
                if not voice_client.is_playing():
                    await voice_client.move(user_vc)
                    await ctx.send(f"🔄 Moved to {user_vc.name} to play your song.")
                    logger.info(f"Moved to channel: {user_vc.name}")
                # The bot is already playing
                else:
                    await ctx.send(f"I'm already playing music in **{voice_client.channel.name}**. Please join me there or wait until I'm free.")
                    logger.info("Playback already in progress in another channel.")
                    return None
        # Bot is not in a voice channel
        else:
            await user_vc.connect()
            logger.info(f"Connected to voice channel: {user_vc.name}")

        return ctx.voice_client
    
    # Function to check if the URL is a YouTube playlist or live stream
    async def _is_valid_video(self, info):
        # Check if it's a playlist
        if 'entries' in info:
            return False
        
        # Check if it's a live stream
        if info.get('is_live', False):
            return False
        
        return True

    # Fetch YouTube video info safely
    async def _fetch_youtube_info(self, url):
        """Fetch YouTube video info safely."""

        YDL_OPTIONS = {
            'format': 'bestaudio[ext!=m3u8]/bestaudio/best',
            'noplaylist': True,
            'quiet': True,
            'extract_flat': False,
            'no_warnings': True
        }
        
        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                
                info = ydl.extract_info(url, download=False)
                
                if not await self._is_valid_video(info):
                    return None
                
                logger.debug(f"Fetched info for URL: {url}")
                return {
                    'title': info.get('title'),
                    'url': info.get('url')
                }
        except Exception as e:
            logger.exception(f"Unhandled error while fetching YouTube info: {e}")
            return None
        
    # Checks with a regex the validity of a an url - Youtube
    @staticmethod
    def _is_valid_youtube_url(url):
        """Checks with a regex the validity of a an url - Youtube."""
        pattern = r"(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+"
        return re.match(pattern, url) is not None

async def setup(bot):
    await bot.add_cog(Music(bot))