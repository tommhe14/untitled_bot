import discord
from discord import app_commands, SelectOption, Interaction
from discord.ext import commands, tasks
from discord.ui import Button, View, Select
import traceback
import asyncio
import random

from config import load_config

config = load_config()

# ROLE IDS which the bot will not work unless the reacting has any of these.
allowable_roles = config["allowable_roles"] 

# action A and B keys needs to have the emoji ID(s) to gain these you send into the discord chat <\:emojiname:>
allowable_emojis = {config["emoji_a"] : "ACTION_A", config["emoji_b"]: "ACTION_B"}  

target_channel = config["target_channel"]

class ReactionCheck(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def handle_action_a(self, channel, message, member):
        select = Select(
            placeholder="Select a channel...",
            options=[SelectOption(label=ch.name, value=str(ch.id)) for ch in channel.guild.text_channels]
        )
        submit_button = Button(label="Submit", style=discord.ButtonStyle.green)
        
        async def select_callback(interaction: Interaction):
            await interaction.response.defer()
            selected_channel_id = int(select.values[0])
            self.selected_channel = self.client.get_channel(selected_channel_id)
            del_msg = await interaction.followup.send("Channel selected.",ephemeral=True)

            await asyncio.sleep(1)
            await del_msg.delete()
    

        async def submit_callback(interaction: Interaction):
            if hasattr(self, 'selected_channel'):
                embed = discord.Embed(colour=random.randint(0, 0xFFFFFF))
                embed.set_author(name = interaction.guild.name, icon_url=interaction.guild.icon)
                embed.description = f":fire: Trending in {message.channel.mention} [Message Link]({message.jump_url})" + f"\n\n{message.content}"
                image_url = next((attachment.url for attachment in message.attachments if attachment.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))), None)

                if image_url:
                    embed.set_image(url=image_url)

                await self.selected_channel.send(embed=embed)

            else:
                await interaction.response.defer()
                m = await interaction.followup.send("Please select a channel first.", ephemeral=True)

                await asyncio.sleep(1)
                await m.delete()

            await interaction.response.defer()
            m = await interaction.followup.send(f"message sent to {self.selected_channel.mention}", ephemeral=True)

            await asyncio.sleep(1)
            await m.delete()
            await dele_msg.delete()

        select.callback = select_callback
        submit_button.callback = submit_callback
        view = View()
        view.add_item(select)
        view.add_item(submit_button)

        embed = discord.Embed(colour=random.randint(0, 0xFFFFFF))
        embed.set_author(name = message.guild.name, icon_url=message.guild.icon)
        embed.description = f":fire: Trending in {message.channel.mention} [Message Link]({message.jump_url})" + f"\n\n{message.content}"
        image_url = next((attachment.url for attachment in message.attachments if attachment.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))), None)

        if image_url:
            embed.set_image(url=image_url)

        target_ = self.client.get_channel(target_channel)
        dele_msg = await target_.send(content = f"{member.mention} Please select a channel and submit:",embed = embed, view=view)

    async def handle_action_b(self, payload, message = None):
        guild = self.client.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        channel = self.client.get_channel(payload.channel_id)
        
        channel_select_view = View()

        pre_msg = f":fire: Trending in {message.channel.mention} [Message Link]({message.jump_url})" + f"\n\n{message.content}"

        embed = discord.Embed(colour=random.randint(0, 0xFFFFFF))
        embed.set_author(name = message.guild.name, icon_url=message.guild.icon)
        embed.description = f":fire: Trending in {message.channel.mention} [Message Link]({message.jump_url})" + f"\n\n{message.content}"
        image_url = next((attachment.url for attachment in message.attachments if attachment.filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))), None)

        if image_url:
            embed.set_image(url=image_url)
        
        select_channel = Select(
            placeholder="Select a channel...",
            options=[
                SelectOption(label=channel.name, value=str(channel.id))
                for channel in guild.text_channels
            ],
        )
        
        async def select_callback(interaction: Interaction):
            await interaction.response.defer()
            selected_channel_id = int(select_channel.values[0])
            selected_channel = self.client.get_channel(selected_channel_id)
            m1_del = await interaction.followup.send("Channel selected. You can now edit the message.", ephemeral=True)

            await asyncio.sleep(1)
            await m1_del.delete()
            
            edit_button_view = View()
            
            edit_button = Button(label="Edit Message", style=discord.ButtonStyle.primary)
            async def edit_callback(interaction: Interaction):
                class FeedbackModal(discord.ui.Modal, title="Edit Your Message"):
                    def __init__(self, client, prefilled_message):
                        super().__init__()
                        self.client = client
                        self.message = discord.ui.TextInput(
                            label="Edit Message",
                            style=discord.TextStyle.long,
                            default=pre_msg,  
                            required=True
                        )
                        self.add_item(self.message)  

                    async def on_submit(self, interaction: Interaction):
                        await interaction.response.defer()
                        embed.description = self.message.value
                        await selected_channel.send(embed=embed)
                        m2_del = await interaction.followup.send("Message sent to the selected channel!", ephemeral=True)

                        await asyncio.sleep(1)
                        await m2_del.delete()
                        await main_msg.delete()
                        await m3_del.delete()

                modal = FeedbackModal(self.client, prefilled_message="This is the default pre-filled message.")
                await interaction.response.send_modal(modal)

            edit_button.callback = edit_callback
            edit_button_view.add_item(edit_button)
            m3_del = await interaction.followup.send("Edit Message:", view=edit_button_view, ephemeral=True)

        select_channel.callback = select_callback
        channel_select_view.add_item(select_channel)
        
        target_ = self.client.get_channel(target_channel)
        main_msg = await target_.send(f"{member.mention} Please select a channel from the dropdown below:", view=channel_select_view)


    @commands.Cog.listener("on_raw_reaction_add")
    async def reaction_check(self, payload):
        try:
            if not payload.emoji.id in allowable_emojis.keys():
                return
            
            guild = self.client.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            if not any(role.id in allowable_roles for role in member.roles):
                return  

            emoji_id = payload.emoji.id
            if emoji_id not in allowable_emojis: 
                return

            channel = self.client.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)

            await message.remove_reaction(payload.emoji, member)

            if allowable_emojis[emoji_id] == "ACTION_A":
                await self.handle_action_a(channel, message, member)
            elif allowable_emojis[emoji_id] == "ACTION_B":
                await self.handle_action_b(payload, message)
        except Exception:
            print(traceback.format_exc())



async def setup(client):
    await client.add_cog(ReactionCheck(client))