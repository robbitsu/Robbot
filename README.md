# Robbot Discord Bot

Robbot is a modular, feature-rich Discord bot built with [discord.py](https://discordpy.readthedocs.io/). It provides a variety of fun, utility, and moderation commands, organized into separate cogs for easy maintenance and extension.

## Features

- **Anime & Manga Lookup**: Search for anime and manga details using the Jikan API.
- **Book Lookup**: Find book information and summaries using OpenLibrary and Google Books APIs.
- **Image Manipulation**: Generate supremacy images, create custom emojis, and make animated 'petpet' images.
- **D&D NPC Generator**: Generate random beauty scores and descriptors for NPCs (great for tabletop games).
- **Fun Tricks**:
  - Show full-size profile pictures
  - Babble (translate a message through random languages)
- **Development Tools**: List server/user roles, purge emojis, and more (owner-only commands).
- **Modular Cog System**: Easily add or remove features by editing the `cogs/` directory.

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Robbot
   ```

2. **Install dependencies**
   Ensure you have Python 3.8+ and pip installed. Then run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your bot token**
   - Create a `secret.py` file in the project root with the following content:
     ```python
     TOKEN = "your-discord-bot-token"
     ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

## Usage

- Use `!help` or `/help` in your Discord server to see available commands.
- Most commands are available as both prefix (`!command`) and slash (`/command`) commands.
- Some commands (like `reload`, `sync`, and dev tools) are restricted to the bot owner.

## Example Commands

- `!anime <name>` — Look up an anime
- `!manga <name>` — Look up a manga
- `!book <title>` — Look up a book
- `!supremacy <name>` — Generate a supremacy image
- `!mini <user>` — Create a mini emoji from a user's avatar
- `!petpet <user>` — Make a petpet animated image
- `!npc <name>` — Generate a D&D NPC beauty score
- `!babble <message>` — Translate a message through random languages
- `!imitate <user> <message>` — Imitate a user (requires Manage Webhooks permission)

## Adding/Removing Features

- To add or remove features, edit the Python files in the `cogs/` directory. Each file represents a separate module (cog).
- Use the `!reload` or `/reload` command (owner only) to reload all cogs without restarting the bot.

## Dependencies

See `requirements.txt` for a full list. Major dependencies include:
- discord.py
- requests
- aiohttp
- Pillow
- numpy
- googletrans
- opencv-python

## License

MIT License. See [LICENSE](LICENSE) for details.

---

*Robbot is designed for fun and utility. Contributions and suggestions are welcome!*