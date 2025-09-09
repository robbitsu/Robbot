import discord
import googletrans
import random
from discord.ext import commands

# View for a button that sends an image (which is passed as an argument) to the channel
class SendImageView(discord.ui.View):
    def __init__(self, image_url: str):
        super().__init__()
        self.image_url = image_url
    
    @discord.ui.button(label="Surprise!", style=discord.ButtonStyle.primary, emoji="🎁")
    async def send_image_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.style = discord.ButtonStyle.gray
        button.disabled = True
        await interaction.response.send_message(file=discord.File(self.image_url))
        await interaction.followup.edit_message(interaction.message.id, view=self)

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

    @commands.hybrid_command(name="surprise", description="Surprise someone with an image")
    async def surprise(self, ctx: commands.Context, image_url: str):
        await ctx.send(f"There's a surprise for you!", view=SendImageView(image_url))


async def setup(bot):
    await bot.add_cog(Tricks(bot))
