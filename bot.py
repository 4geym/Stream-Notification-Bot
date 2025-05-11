import os
import asyncio
import aiohttp
import discord
from discord.ext import tasks, commands
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_USERNAME = os.getenv("TWITCH_USERNAME")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

class TwitchNotifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.access_token = None
        self.user_id = None
        self.was_live = False
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("Бот готов, запускаем проверку стрима...")
        self.check_stream.start()

    async def get_access_token(self):
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": TWITCH_CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as resp:
                data = await resp.json()
                return data["access_token"]

    async def get_user_id(self, access_token):
        url = f"https://api.twitch.tv/helix/users?login={TWITCH_USERNAME}"
        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {access_token}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                return data["data"][0]["id"]

    async def is_live(self, access_token, user_id):
        url = f"https://api.twitch.tv/helix/streams?user_id={user_id}"
        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {access_token}"
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                return data["data"][0] if data["data"] else None

    @tasks.loop(seconds=60)
    async def check_stream(self):
        if not self.access_token:
            self.access_token = await self.get_access_token()
        if not self.user_id:
            self.user_id = await self.get_user_id(self.access_token)

        stream_data = await self.is_live(self.access_token, self.user_id)
        channel = self.bot.get_channel(DISCORD_CHANNEL_ID)

        if stream_data and not self.was_live:
            self.was_live = True
            title = stream_data['title']
            game = stream_data.get('game_name', 'Unknown Game')
            url = f"https://www.twitch.tv/{TWITCH_USERNAME}"
            await channel.send(f"🔴 **{TWITCH_USERNAME}** начал(а) стрим!\n**{title}**\n🎮 {game}\n{url}")
        elif not stream_data and self.was_live:  # Если стрим только что закончился
            self.was_live = False
            await channel.send(f"⚪ **{TWITCH_USERNAME}** закончил(а) стрим.")

    @check_stream.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

async def main():
    async with bot:
        await bot.add_cog(TwitchNotifier(bot))
        await bot.start(DISCORD_TOKEN)

asyncio.run(main())
