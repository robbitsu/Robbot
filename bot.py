import discord
from discord.ext import commands
from discord.app_commands import AppCommandContext
from secret import TOKEN
import os
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a logger specifically for the bot
logger = logging.getLogger('discord_bot')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents, slash_commands=True, allowed_contexts=AppCommandContext(guild=True, dm_channel=True, private_channel=True))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.tree.sync()
    
async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.find('secret') != -1:
            continue
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f"Loaded {filename[:-3]}")
    

@bot.hybrid_command(name='reload')
@commands.is_owner()  # Restrict to bot owner for security
async def reload_cogs(ctx):
    try:
        # Unload all extensions
        for filename in os.listdir('./cogs'):
            if filename.find('secret') != -1:
                continue
            if filename.endswith('.py'):
                await bot.unload_extension(f'cogs.{filename[:-3]}')
        
        # Reload extensions
        await load_extensions()
        
        await ctx.send("Successfully reloaded all cogs!", ephemeral=True)
    except Exception as e:
        await ctx.send(f"An error occurred while reloading: {e}", ephemeral=True)

@bot.hybrid_command(name='sync')
@commands.is_owner()
async def sync_commands(ctx):
    await bot.tree.sync()
    await ctx.send("Successfully synced commands!", ephemeral=True)

# Add a global command logging decorator
@bot.event
async def on_command(ctx):
    logger.info(
        f"Command used: {ctx.command.name} "
        f"by {ctx.author} ({ctx.author.id}) "
        f"in {ctx.channel} ({ctx.channel.id})"
    )

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

asyncio.run(main())
