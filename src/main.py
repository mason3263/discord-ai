import discord
from gpt import GPT

from dotenv import load_dotenv
import os

class DiscordClient(discord.Client):

    def __init__(self, gpt_api_key, assistant_id):

        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(intents=intents)

        self.gpt = GPT(gpt_api_key, assistant_id)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    async def on_message(self, message: discord.Message):

        if message.author == self.user:
            return

        if message.channel.name == "ai" and message.content != "clear":
            await self.send_message(message.channel, await self.gpt.add_message(message.content))

        if message.content == "clear":
            await message.channel.purge()

    async def send_message(self, channel: discord.TextChannel, message: str):
        message_list = [message[i:i+2000] for i in range(0, len(message), 2000)]

        for partial_message in message_list:
            await channel.send(partial_message)

load_dotenv()

client = DiscordClient(os.getenv("gpt_api_key"), os.getenv("gpt_assistant_id"))
client.run(os.getenv("discord_token"))