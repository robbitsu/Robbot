# This file is for development tools. All messages should be ephemeral.

import discord
import os
import sys
import aiohttp
from discord.ext import commands

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="serverroles", description="List all roles in the server with their IDs")
    async def server_roles(self, ctx: commands.Context):
        """List all roles in the server with their IDs."""
        roles = ctx.guild.roles
        
        # Sort roles from highest to lowest in hierarchy
        roles = sorted(roles, key=lambda x: x.position, reverse=True)
        
        # Create a formatted string of roles
        role_list = "\n".join([f"{role.name}: {role.id}" for role in roles])
        
        # Create a text file with the role list
        with open('server_roles.txt', 'w', encoding='utf-8') as f:
            f.write(role_list)
        
        # Send the text file
        await ctx.send(file=discord.File('server_roles.txt'), ephemeral=True)
        
        # Delete the file after sending
        import os
        os.remove('server_roles.txt')

    @commands.hybrid_command(name="userroles", description="List roles for a specific user")
    async def user_roles(self, ctx: commands.Context, user: discord.Member = None):
        """List roles for a specific user or the command invoker."""
        # If no user specified, use the command invoker
        user = user or ctx.author
        
        # Get user's roles and sort them from highest to lowest in hierarchy
        roles = sorted(user.roles[1:], key=lambda x: x.position, reverse=True)
        
        # Create a formatted string of roles
        if roles:
            role_list = "\n".join([f"{role.name}: {role.id}" for role in roles])
            
            # Create a text file with the role list
            with open('user_roles.txt', 'w', encoding='utf-8') as f:
                f.write(role_list)
            
            # Send the text file
            await ctx.send(file=discord.File('user_roles.txt'), ephemeral=True)
            
            # Delete the file after sending
            import os
            os.remove('user_roles.txt')
        else:
            await ctx.send(f"{user.display_name} has no roles.", ephemeral=True)

    # Purge the emojis from the emoji server
    @commands.hybrid_command(name="purge_emojis", description="Purge the emojis from the emoji server")
    async def purge_emojis(self, ctx: commands.Context):
        """Purge the emojis from the emoji server."""
        guild = self.bot.get_guild(1404156657910550528)
        if guild is None:
            await ctx.send("Could not find the emoji server.", ephemeral=True)
            return
        
        # Purge the emojis
        for emoji in guild.emojis:
            await emoji.delete()
        
        await ctx.send("Emojis purged.", ephemeral=True)

    @commands.hybrid_command(name="myip", description="Show the bot's public IPv4 address")
    async def my_ip(self, ctx: commands.Context):
        """Fetches and displays the bot's public IPv4 address using an external API. The message is ephemeral."""
        
        url = "https://api.ipify.org?format=json"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.json()
                    ip = data.get("ip", "Unknown")
                    await ctx.send(f"Public IPv4 address: `{ip}`", ephemeral=True)
        except Exception as e:
            await ctx.send(f"Failed to fetch IP address: {e}", ephemeral=True)

    
        

async def setup(bot):
    await bot.add_cog(Dev(bot))

