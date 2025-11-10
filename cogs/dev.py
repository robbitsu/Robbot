# This file is for development tools. All messages should be ephemeral.

import discord
import os
import sys
import aiohttp
import boto3
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

    @commands.hybrid_command(name="update_dns", description="Update Route 53 record to current public IPv4 address using only environment variables.")
    async def update_dns(self, ctx: commands.Context):
        """
        Update the Route 53 A record to the current public IPv4 address.
        Requires env vars: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, ROUTE53_HOSTED_ZONE_ID, ROUTE53_RECORD_NAME
        """
        # Get current public IP
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.ipify.org?format=json") as resp:
                    data = await resp.json()
                    ip = data.get("ip")
                    if not ip:
                        await ctx.send("Could not get public IP.", ephemeral=True)
                        return
        except Exception as e:
            await ctx.send(f"Failed to get public IP: {e}", ephemeral=True)
            return

        # Gather AWS creds and Route 53 vars from environment
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_region = os.getenv("AWS_REGION", "us-east-1")
        record_name = os.getenv("ROUTE53_RECORD_NAME")
        hosted_zone_id = os.getenv("ROUTE53_HOSTED_ZONE_ID")
        if not (aws_access_key and aws_secret_key and record_name and hosted_zone_id):
            await ctx.send("AWS credentials or Route 53 config (ROUTE53_RECORD_NAME, ROUTE53_HOSTED_ZONE_ID) not set in env vars.", ephemeral=True)
            return

        # Update Route 53
        try:
            client = boto3.client(
                "route53",
                region_name=aws_region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
            )
            response = client.change_resource_record_sets(
                HostedZoneId=hosted_zone_id,
                ChangeBatch={
                    "Changes": [
                        {
                            "Action": "UPSERT",
                            "ResourceRecordSet": {
                                "Name": record_name,
                                "Type": "A",
                                "TTL": 300,
                                "ResourceRecords": [{"Value": ip}],
                            },
                        }
                    ]
                },
            )
            await ctx.send(f"Updated {record_name} to {ip}. Change status: {response['ChangeInfo']['Status']}", ephemeral=True)
        except Exception as e:
            await ctx.send(f"Failed to update DNS: {e}", ephemeral=True)

    
        

async def setup(bot):
    await bot.add_cog(Dev(bot))

