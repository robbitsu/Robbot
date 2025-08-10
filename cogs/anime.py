import discord
import requests
from discord.ext import commands

class Anime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="anime", description="Look up an anime")
    async def anime(self, ctx: commands.Context, anime_name: str):
        await ctx.send(f"Looking up {anime_name}...")
        try:
            # Search for anime using Jikan API
            response = requests.get(f"https://api.jikan.moe/v4/anime", params={"q": anime_name, "limit": 1})
            response.raise_for_status()
            data = response.json()
            
            if data['data']:
                anime = data['data'][0]
                
                # Extract relevant information
                english_title = anime.get('title_english', anime['title'])
                japanese_title = anime.get('title_japanese', 'N/A')
                summary = anime.get('synopsis', 'No summary available.')
                
                # Get studio information
                studios = [studio['name'] for studio in anime.get('studios', [])]
                studio_names = ', '.join(studios) if studios else 'N/A'
                
                # Try to get director (might require additional API call)
                director = 'N/A'
                staff_response = requests.get(f"https://api.jikan.moe/v4/anime/{anime['mal_id']}/staff")
                if staff_response.status_code == 200:
                    staff_data = staff_response.json()
                    directors = [person['person']['name'] for person in staff_data.get('data', []) 
                                 if 'Director' in person.get('positions', [])]
                    director = directors[0] if directors else 'N/A'
                
                # Create embed with anime information
                embed = discord.Embed(
                    title=english_title,
                    description=summary,
                    color=discord.Color.blue()
                )
                embed.add_field(name="Japanese Title", value=japanese_title, inline=False)
                embed.add_field(name="Studio", value=studio_names, inline=False)
                embed.add_field(name="Director", value=director, inline=False)
                
                # Add image if available
                if anime.get('images', {}).get('jpg', {}).get('image_url'):
                    embed.set_image(url=anime['images']['jpg']['image_url'])
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"No anime found for '{anime_name}'.")
        
        except requests.RequestException as e:
            await ctx.send(f"Error fetching anime information: {e}")

    @commands.hybrid_command(name="manga", description="Look up a manga")
    async def manga(self, ctx: commands.Context, manga_name: str):
        await ctx.send(f"Looking up {manga_name}...")
        try:
            # Search for manga using Jikan API
            response = requests.get(f"https://api.jikan.moe/v4/manga", params={"q": manga_name, "limit": 1})
            response.raise_for_status()
            data = response.json()
            
            if data['data']:
                manga = data['data'][0]
                
                # Extract relevant information
                english_title = manga.get('title_english', manga['title'])
                japanese_title = manga.get('title_japanese', 'N/A')
                author = manga.get('authors', [{}])[0].get('name', 'N/A')
                summary = manga.get('synopsis', 'No summary available.')
                
                # Create embed with manga information
                embed = discord.Embed(
                    title=english_title,
                    color=discord.Color.blue()
                )
                embed.add_field(name="Japanese Title", value=japanese_title, inline=False)
                embed.add_field(name="Author", value=author, inline=False)
                embed.add_field(name="Summary", value=summary, inline=False)

                # Add image if available
                if manga.get('images', {}).get('jpg', {}).get('image_url'):
                    embed.set_image(url=manga['images']['jpg']['image_url'])
                
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"No manga found for '{manga_name}'.")
        
        except requests.RequestException as e:
            await ctx.send(f"Error fetching manga information: {e}")
        

async def setup(bot):
    await bot.add_cog(Anime(bot))
