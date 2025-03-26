import discord
from discord.ext import commands
import random
import os
import csv
import re
import logging

from config import load_config

config = load_config()

logging.basicConfig(level=logging.ERROR)


class extra_cmds(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def help(self, ctx):
        """Displays help information for available commands."""
        await ctx.message.delete()

        if not ctx.author.id == 212790728802172928:
            return
        
        embed = discord.Embed(
            title="Help Menu",
            description="Here are the available commands:",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="`!search_user <username>`",
            value="Search for users in the server whose name contains the given query.\n"
                  "**Example:** `!search_user John` (Finds all users with 'John' in their name)",
            inline=False
        )

        embed.add_field(
            name="`!search_wildcard <pattern>`",
            value="Search for users using wildcard patterns.\n"
                  "- `*` matches any number of characters\n"
                  "- `?` matches a single character\n"
                  "**Example:** `!search_wildcard J*` (Finds all users starting with 'J')",
            inline=False
        )

        embed.add_field(
            name="`!export_users`",
            value="Exports a list of all server users into a `.csv` file",
            inline=False
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def search_user(self, ctx, query: str):
        """Search for users whose name contains the query."""
        await ctx.message.delete()

        try:
            guild = ctx.guild
            members = guild.members
            found_users = [member.name for member in members if query.lower() in member.name.lower()]

            if found_users:
                response = "Users Found:\n" + "\n".join(found_users)
            else:
                response = f"No users found matching '{query}'"

            await ctx.reply(response)
        except Exception as e:
            logging.error(f"Error in search_user: {e}", exc_info=True)
            await ctx.reply("An error occurred while searching. Please try again later.")

    @commands.command()
    async def search_wildcard(self, ctx, query: str):
        """
        Search for users using wildcard patterns (* for any characters, ? for a single character).

        Find all users whose name starts with "John"
        !search_wildcard John*

        Find all users whose name ends with "Smith"
        !search_wildcard *Smith
        
        Find all users whose name contains "bot"
        !search_wildcard *bot*

        Find all users whose name is exactly 5 characters long and starts with "A"
        !search_wildcard A????
        """
        await ctx.message.delete()

        try:
            pattern_regex = re.escape(query).replace("\\*", ".*").replace("\\?", ".")
            regex = re.compile(pattern_regex, re.IGNORECASE)

            guild = ctx.guild
            members = guild.members
            found_users = [member.name for member in members if regex.match(member.name)]

            if found_users:
                response = "Users Found:\n" + "\n".join(found_users)
            else:
                response = f"No users found matching '{query}'"

            await ctx.reply(response)
        except Exception as e:
            logging.error(f"Error in search_wildcard: {e}", exc_info=True)
            await ctx.reply("An error occurred while searching. Please try again later.")

    @commands.command()
    async def export_users(self, ctx):
        """Export all users in the server to a CSV file."""
        await ctx.message.delete()
        try:
            guild = ctx.guild
            members = guild.members
            filename = f"discord_users_{random.randint(0, 0xFFFFFF)}.csv"

            with open(filename, "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["User ID", "Username"])
                for member in members:
                    writer.writerow([member.id, member.name])

            try:
                await ctx.reply(
                    f"Extracted {len(members)} users. Here is the file:",
                    file=discord.File(filename)
                )
            finally:
                os.remove(filename)  

        except Exception as e:
            logging.error(f"Error in export_users: {e}", exc_info=True)
            await ctx.reply("An error occurred while exporting users. Please try again later.")


async def setup(client):
    await client.add_cog(extra_cmds(client))
