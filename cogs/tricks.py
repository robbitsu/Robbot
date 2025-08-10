import discord
import googletrans
import random
from discord.ext import commands

class Tricks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Command to show the full size version of a per-server profile picture
    @commands.hybrid_command(name="profile", description="Show the full size version of a per-server profile picture")
    async def profile(self, ctx: commands.Context, user: discord.Member = None):
        user = user or ctx.author
        # Try to get the per-server (guild) avatar, fallback to global avatar if not set
        if hasattr(user, "guild_avatar") and user.guild_avatar is not None:
            avatar_url = user.guild_avatar.url
            await ctx.send(f"Full size **server profile** picture for {user.mention}: {avatar_url}")
        else:
            avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
            await ctx.send(f"{user.mention} does not have a server profile picture. Showing global avatar: {avatar_url}")

    # Command to welcome someone because I'm too lazy to do it myself
    @commands.hybrid_command(name="welcome", description="Welcome someone to the server")
    async def welcome(self, ctx: commands.Context, user: discord.Member):
        await ctx.send(f"Welcome {user.mention}! I'm too lazy to type this out myself, so I made a bot command that tells you to grab roles and maybe make an introduction.")

    # Command to translate an English message through a specific number of random languages and back to English to make it sound like a babble
    @commands.hybrid_command(name="babble", description="Translate an English message through random languages to make it sound like a babble")
    async def babble(self, ctx: commands.Context, message: str, languages: int = 4, show_steps: bool = False):
        if languages < 1 or languages > 10:
            await ctx.send("Please choose between 1 and 10 languages for maximum babble!")
            return
        async with ctx.typing():
            translator = googletrans.Translator()
            available_langs = list(googletrans.LANGUAGES.keys())
            available_langs.remove('en')
            chosen_langs = random.sample(available_langs, k=languages)
            current_text = message
            chain = ["en"] + chosen_langs + ["en"]
            steps = []
            for i in range(1, len(chain)):
                dest = chain[i]
                translated = await translator.translate(current_text, dest=dest)
                steps.append(f"{googletrans.LANGUAGES[dest]}: {translated.text}")
                current_text = translated.text
            babble_result = current_text
            if show_steps:
                steps_display = '\n'.join(steps)
                await ctx.send(f"{babble_result}\n\n**Translation steps:**\n{steps_display}")
            else:
                await ctx.send(f"{babble_result}")

    # Command to imitate a specific user with a specified message by copying their profile picture and name
    @commands.hybrid_command(
        name="imitate",
        description="Imitate a user by sending a message as them (bot will copy their name and avatar)"
    )
    async def imitate(self, ctx: commands.Context, user: discord.Member, *, message: str):
        # Only allow the command in guilds
        if not ctx.guild:
            await ctx.send("This command can only be used in a server.")
            return

        # Check bot permissions
        if not ctx.channel.permissions_for(ctx.guild.me).send_messages:
            await ctx.send("I don't have permission to send messages in this channel.")
            return
        if not ctx.channel.permissions_for(ctx.guild.me).manage_webhooks:
            await ctx.send("I need the 'Manage Webhooks' permission to imitate users.")
            return

        # Find or create a webhook for this channel
        webhooks = await ctx.channel.webhooks()
        webhook = None
        for wh in webhooks:
            if wh.user == ctx.guild.me:
                webhook = wh
                break
        if webhook is None:
            webhook = await ctx.channel.create_webhook(name="Imitator")

        # Use the user's display name and avatar (prefer server avatar)
        avatar_url = user.guild_avatar.url if hasattr(user, "guild_avatar") and user.guild_avatar else (user.avatar.url if user.avatar else user.default_avatar.url)
        display_name = user.display_name

        # Send the message as the user
        await webhook.send(
            content=message,
            username=display_name,
            avatar_url=avatar_url,
            wait=True
        )

        # Optionally, delete the command invocation for stealth
        try:
            await ctx.message.delete()
        except Exception:
            pass  # Ignore if can't delete


async def setup(bot):
    await bot.add_cog(Tricks(bot))
