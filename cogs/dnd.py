import discord
from discord.ext import commands
import numpy as np
import random

def generate_beauty_score():
    return max(1, min(100, int(np.random.normal(50, 20))))

def beauty_descriptor(score):
    """
    Return a descriptor string based on the beauty score.
    """
    descriptors = [
    (90, ["stunningly beautiful", "radiant", "divine", "breathtaking", "ethereal"]),
    (75, ["very attractive", "charming", "alluring", "striking", "handsome/beautiful"]),
    (60, ["attractive", "pleasant-looking", "good-looking", "appealing", "comely"]),
    (45, ["average", "ordinary", "common-looking", "unremarkable", "plain but tidy"]),
    (30, ["plain", "nondescript", "dull-looking", "homely", "forgettable"]),
    (15, ["unattractive", "rough-looking", "unpleasant", "awkward", "misshapen"]),
    (1, ["hideous", "repulsive", "ghastly", "grotesque", "monstrous"]),
    ]
    for threshold, desc in descriptors:
        if score >= threshold:
            return random.choice(desc)
    return "indescribable"

class DnD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="npc", description="Generate a beauty score and descriptor for an NPC")
    async def npc(self, ctx: commands.Context, name: str):
        score = generate_beauty_score()
        descriptor = beauty_descriptor(score)
        await ctx.send(f"{name} is {descriptor} with a beauty score of {score}.")

async def setup(bot):
    await bot.add_cog(DnD(bot))

# Test the beauty score generation
if __name__ == "__main__":
    from collections import Counter

    scores = [generate_beauty_score() for _ in range(100)]
    freq = Counter(scores)

    print("Beauty Score Frequencies (score: count):")
    for score, count in sorted(freq.items()):
        print(f"{score}: {count}")