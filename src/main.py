import discord
from discord import app_commands
from gpt import GPT

from dotenv import load_dotenv
import os
import yaml
from typing import TextIO


class DiscordClient(discord.Client):

    def __init__(self, data_file: str):

        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents=intents)

        self.guild_list: dict[str, GPT] = dict()

        data: TextIO = open(data_file, "r")
        self.load(data)
        self.close

        self.data_file: TextIO = open(data_file, "a")

        self.command_tree = app_commands.CommandTree(self)

    def load(self, data: TextIO):

        api_keys: dict[str, list[str]] = yaml.safe_load(data)

        if api_keys != None:
            for guild in api_keys.keys():
                self.guild_list[guild] = GPT(api_keys[guild][0], api_keys[guild][1])

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        await self.commands()
        await self.command_tree.sync()

    async def on_message(self, message: discord.Message):

        # Messages from the bot aren't processed
        if message.author == self.user:
            return

        if message.content == "sync":
            await self.command_tree.sync(guild=message.guild)

        if message.channel.name == "chatgpt":
            if message.guild.id in self.guild_list:
                await self.send_message(
                    message.channel,
                    await self.guild_list[message.guild.id].add_message(
                        message.content
                    ),
                )
            else:
                await self.send_message("ChatGPT API not Connected")

    async def send_message(self, channel: discord.TextChannel, message: str):
        message_list = [message[i : i + 2000] for i in range(0, len(message), 2000)]

        for partial_message in message_list:
            await channel.send(partial_message)

    async def commands(self):
        @self.command_tree.command(description="Connects the ChatGPT API")
        async def gptapi(
            interaction: discord.Interaction, api_key: str, assistant_id: str
        ):
            if not interaction.guild_id in self.guild_list.keys():
                self.guild_list[interaction.guild_id] = GPT(api_key, assistant_id)
                self.data_file.write(
                    f"{interaction.guild_id}: [ {api_key}, {assistant_id} ]"
                )
                self.data_file.flush()
                await interaction.response.send_message("API Setup")
            else:
                await interaction.response.send_message("API is already connected")

        @self.command_tree.command(description="Clears the text in current channel")
        async def clear(interaction: discord.Interaction):
            await interaction.response.send_message("Clearing Channel")
            await interaction.channel.purge()

            if interaction.channel.name == "chatgpt":
                self.guild_list[interaction.guild_id].clear()


load_dotenv()

client = DiscordClient("data/guild_list.yaml")
client.run(os.getenv("discord_token"))
