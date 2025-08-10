import discord
import requests
from discord.ext import commands

class Book(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="book", description="Look up a book")
    async def book(self, ctx: commands.Context, book_name: str):
        await ctx.send(f"Looking up {book_name}...")
        response = requests.get(f"https://openlibrary.org/search.json?q={book_name}")
        data = response.json()
        if data['num_found'] > 0:
            book = data['docs'][0]
            title = book.get('title', 'Unknown Title')
            author = book.get('author_name', ['Unknown Author'])[0]
            first_publish_year = book.get('first_publish_year', 'Unknown')
            
            # Try to get ISBN to fetch book summary from Google Books API
            isbn = book.get('isbn', [None])[0] if 'isbn' in book else None
            summary = "No summary available."
            
            if isbn:
                try:
                    google_books_response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}")
                    google_books_data = google_books_response.json()
                    
                    if google_books_data.get('totalItems', 0) > 0:
                        volume_info = google_books_data['items'][0]['volumeInfo']
                        summary = volume_info.get('description', summary)
                except Exception as e:
                    print(f"Error fetching book summary: {e}")
            
            embed = discord.Embed(
                title=title, 
                description=f"Author: {author}\nFirst Published: {first_publish_year}\n\nSummary: {summary}",
                color=discord.Color.blue()
            )
            
            if 'cover_i' in book:
                cover_url = f"https://covers.openlibrary.org/b/id/{book['cover_i']}-M.jpg"
                embed.set_thumbnail(url=cover_url)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No books found for '{book_name}'.")

async def setup(bot):
    await bot.add_cog(Book(bot))
