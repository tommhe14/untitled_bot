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

        await ctx.reply(embed=embed)

    async def send_results(self, ctx, response: str, filename: str):
        """Handles sending the response as a message or a text file if it's too long."""
        try:
            if len(response) <= 2000:  
                await ctx.reply(response)
            else:
                with open(filename, "w", encoding="utf-8") as file:
                    file.write(response)
                await ctx.reply(
                    "The results were too long to send in a message. Here is a text file instead:",
                    file=discord.File(filename)
                )
                os.remove(filename)  
        except Exception as e:
            logging.error(f"Error sending message: {e}", exc_info=True)
            await ctx.reply("An error occurred while sending the results. Please try again later.")

    @commands.command()
    async def search_user(self, ctx, query: str):
        """Search for users whose name contains the query."""
        try:
            guild = ctx.guild
            members = guild.members
            found_users = [member.name for member in members if query.lower() in member.name.lower()]

            response = (
                "Users Found:\n" + "\n".join(found_users) if found_users 
                else f"No users found matching '{query}'"
            )

            await self.send_results(ctx, response, "user_search_results.txt")
        except Exception as e:
            logging.error(f"Error in search_user: {e}", exc_info=True)
            await ctx.reply("An error occurred while searching. Please try again later.")

    @commands.command()
    async def search_wildcard(self, ctx, query: str):
        """
        Search for users using wildcard patterns (* for any characters, ? for a single character).

        Examples:
        - Find all users whose name starts with "John": `!search_wildcard John*`
        - Find all users whose name ends with "Smith": `!search_wildcard *Smith`
        - Find all users whose name contains "bot": `!search_wildcard *bot*`
        - Find all users whose name is exactly 5 characters long and starts with "A": `!search_wildcard A????`
        """

        try:
            pattern_regex = re.escape(query).replace("\\*", ".*").replace("\\?", ".")
            regex = re.compile(pattern_regex, re.IGNORECASE)

            guild = ctx.guild
            members = guild.members
            found_users = [member.name for member in members if regex.match(member.name)]

            response = (
                "Users Found:\n" + "\n".join(found_users) if found_users 
                else f"No users found matching '{query}'"
            )

            await self.send_results(ctx, response, "wildcard_search_results.txt")
        except Exception as e:
            logging.error(f"Error in search_wildcard: {e}", exc_info=True)
            await ctx.reply("An error occurred while searching. Please try again later.")

    @commands.command()
    async def export_users(self, ctx):
        """Export all users in the server to a CSV file."""
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
