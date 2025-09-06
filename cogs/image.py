import os
from io import BytesIO
import re

import aiohttp
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageSequence, ImageFont

# --- Image manipulation functions ---
def create_supremacy_image(name, base_path="base.png", font_path="impact.ttf", output_path="supremacy.png"):
    image = Image.open(base_path)
    name = name.upper()
    draw = ImageDraw.Draw(image)
    max_width = image.width - 40
    max_height = image.height // 4
    font_size = 100
    while font_size > 10:
        font = ImageFont.truetype(font_path, font_size)
        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        if text_width <= max_width and text_height <= max_height:
            break
        font_size -= 2
    x = image.width - text_width - 20
    y = 95
    draw.text((x, y), name, fill="black", font=font)
    font_size = 100
    text_content = "WE LOVE \n YOU " + name
    max_left_width = int(image.width * 0.4) - 40
    max_left_height = image.height // 4
    while font_size > 10:
        font = ImageFont.truetype(font_path, font_size)
        text_bbox = draw.textbbox((0, 0), text_content, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        if text_width <= max_left_width and text_height <= max_left_height:
            break
        font_size -= 2
    x = 20
    y = image.height - text_height - 100
    draw.text((x, y), text_content, fill="black", font=font)
    image.save(output_path)
    return output_path

def make_mini_emoji_image(avatar_bytes, output_path="mini_emoji.png"):
    with Image.open(BytesIO(avatar_bytes)).convert("RGBA") as im:
        im = im.resize((128, 128), Image.LANCZOS)
        im.save(output_path, format="PNG")
    with open(output_path, "rb") as f:
        emoji_bytes = f.read()
    return emoji_bytes

def generate_petpet_webp(image_bytes, petpet_gif_path, output_filename="petpet.webp"):
    """
    Generates a 'petpet' style animated webp using any generic image (not just avatars).
    The input image will be resized and animated with the petpet hand gif.

    Args:
        image_bytes (bytes): The bytes of the input image (any format supported by PIL).
        petpet_gif_path (str): Path to the petpet hand gif.
        output_filename (str): Output filename (not used, output is returned as BytesIO).

    Returns:
        BytesIO: The resulting animated webp image.
    """
    from io import BytesIO
    import math

    with Image.open(BytesIO(image_bytes)).convert("RGBA") as input_im:
        # Resize input image to fit in 112x112 box, preserving aspect ratio and centering
        base_size = (112, 112)
        input_im.thumbnail(base_size, Image.LANCZOS)
        avatar_im = Image.new("RGBA", base_size, (0, 0, 0, 0))
        paste_x = (base_size[0] - input_im.width) // 2
        paste_y = (base_size[1] - input_im.height) // 2
        avatar_im.paste(input_im, (paste_x, paste_y), input_im)

        with Image.open(petpet_gif_path) as petpet_gif:
            frames = []
            durations = []
            n_frames = petpet_gif.n_frames if hasattr(petpet_gif, "n_frames") else sum(1 for _ in ImageSequence.Iterator(petpet_gif))
            for i, frame in enumerate(ImageSequence.Iterator(petpet_gif)):
                frame = frame.convert("RGBA")
                t = i / (n_frames - 1) if n_frames > 1 else 0
                squish = math.sin(math.pi * t)
                min_scale = 0.7
                scale_y = 1 - (1 - min_scale) * squish
                scale_x = 1 + (1 - scale_y)
                squished_img = avatar_im.resize((int(112 * scale_x), int(112 * scale_y)), Image.LANCZOS)
                img_layer = Image.new("RGBA", (112, 112), (0, 0, 0, 0))
                paste_x = (112 - squished_img.width) // 2
                paste_y = 112 - squished_img.height
                img_layer.paste(squished_img, (paste_x, paste_y), squished_img)
                base = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
                base.paste(img_layer, (8, 16), img_layer)
                base.alpha_composite(frame)
                frames.append(base)
                durations.append(frame.info.get("duration", petpet_gif.info.get("duration", 20)))
            output = BytesIO()
            frames[0].save(
                output,
                format="WEBP",
                save_all=True,
                append_images=frames[1:],
                duration=durations,
                loop=0,
                lossless=True,
                method=6,
                quality=100,
                transparency=0,
                disposal=2,
            )
            output.seek(0)
    return output


class ImageCog(commands.Cog):
    """Cog for image editing commands."""
    def __init__(self, bot):
        self.bot = bot


    @commands.hybrid_command(name="supremacy", description="Generate a supremacy image with the given name")
    async def supremacy(self, ctx: commands.Context, name: str):
        output_path = create_supremacy_image(name)
        await ctx.send(file=discord.File(output_path))
        os.remove(output_path)

    @commands.hybrid_command(
        name="mini",
        description="Add a user's profile picture as a custom emoji called :mini: to a specific server"
    )
    async def mini(
        self,
        ctx: commands.Context,
        user: discord.Member,
        use_user_avatar: bool = False
    ):
        """
        Add a user's profile picture as a custom emoji called :mini: to a specific server.
        By default, uses the server avatar if available. Set use_user_avatar=True to use the global avatar.
        """
        # Get the target guild by ID
        guild_id = 1404156657910550528
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            await ctx.send("Could not find the target server.", ephemeral=True)
            return

        # Validate if emoji capacity is reached
        if len(guild.emojis) >= 50:
            await ctx.send("The server has reached the emoji capacity limit.", ephemeral=True)
            return

        # Check bot permissions
        me = guild.me if hasattr(guild, "me") else guild.get_member(self.bot.user.id)
        if not me.guild_permissions.manage_emojis_and_stickers:
            await ctx.send("I don't have permission to manage emojis in the target server.", ephemeral=True)
            return

        # Determine which avatar to use
        if use_user_avatar:
            avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
        else:
            avatar_url = (
                user.guild_avatar.url
                if hasattr(user, "guild_avatar") and user.guild_avatar
                else (user.avatar.url if user.avatar else user.default_avatar.url)
            )

        # Download the avatar image
        async with ctx.typing(ephemeral=True):
            async with self.bot.http._HTTPClient__session.get(avatar_url) as resp:
                if resp.status != 200:
                    await ctx.send("Failed to download the user's avatar.", ephemeral=True)
                    return
                avatar_bytes = await resp.read()
            emoji_bytes = make_mini_emoji_image(avatar_bytes)

            # Create the emoji
            emoji_name = f"{user.name}"
            # If the emoji name is too long, truncate it
            if len(emoji_name) > 30:
                emoji_name = emoji_name[:30]
            # If the emoji contains non-alphanumeric characters, remove them
            emoji_name = re.sub(r'[^a-zA-Z0-9]', '', emoji_name)
            emoji_name = f"mini_{emoji_name}"

            # Remove existing emoji with the same name
            existing = discord.utils.get(guild.emojis, name=emoji_name)
            if existing:
                try:
                    await existing.delete()
                except Exception:
                    pass  # Ignore if can't delete
            
            try:
                emoji = await guild.create_custom_emoji(
                    name=emoji_name,
                    image=emoji_bytes,
                    reason=f"Created by {ctx.author} via mini command"
                )
            except discord.HTTPException as e:
                await ctx.send(f"Failed to create emoji: {e}", ephemeral=True)
                try:
                    os.remove("mini_emoji.png")
                except Exception:
                    pass
                return

            # Delete the created image file
            try:
                os.remove("mini_emoji.png")
            except Exception:
                pass

        await ctx.send(f"Emoji :mini_{user.name}: added to the server! {str(emoji)}", ephemeral=True)

    # Take a user's profile picture or image URL and make it a gif with petpet-transparent.gif overlaid on top of it
    @commands.hybrid_command(
        name="petpet",
        description="Overlay the petpet hand gif on a user's avatar or image URL to make a petpet webp"
    )
    async def petpet(self, ctx: commands.Context, target: str = None):
        """
        Overlay the petpet hand gif on a user's avatar or image URL to make a petpet animated webp.
        The image will squish once across the entire loop.
        
        Args:
            target: Either a user mention/ID or an image URL. If not provided, uses your avatar.
        """

        image_url = None
        
        # If no target provided, use author's avatar
        if target is None:
            image_url = ctx.author.display_avatar.replace(format="png", size=128).url
        else:
            # Check if target is a URL
            if target.startswith(('http://', 'https://')):
                image_url = target
            else:
                # Try to convert to a user
                try:
                    # Try to get user by mention or ID
                    user = await commands.MemberConverter().convert(ctx, target)
                    image_url = user.display_avatar.replace(format="png", size=128).url
                except commands.BadArgument:
                    await ctx.send("Invalid user or URL provided.", ephemeral=True)
                    return

        # Download the image as bytes
        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status != 200:
                        await ctx.send("Failed to download image.", ephemeral=True)
                        return
                    image_bytes = await resp.read()

            petpet_path = os.path.join(os.path.dirname(__file__), "petpet-transparent.gif")
            if not os.path.exists(petpet_path):
                await ctx.send("petpet-transparent.gif not found in cog directory.", ephemeral=True)
                return
            output = generate_petpet_webp(image_bytes, petpet_path)
            file = discord.File(fp=output, filename="petpet.webp")
            await ctx.send(file=file)

async def setup(bot):
    await bot.add_cog(ImageCog(bot)) 

# Test the image generation if this file is run directly
if __name__ == "__main__":
    create_supremacy_image("bob")