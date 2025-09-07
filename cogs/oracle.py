from openai import OpenAI
import discord
from discord.ext import commands
import asyncio
import os

# If ai_secret.py exists, import it and use the AI_SECRET and BASE_URL variables
if os.path.exists('ai_secret.py'):
    from ai_secret import AI_SECRET, BASE_URL, MODEL
else:
    AI_SECRET = os.getenv('AI_SECRET')
    BASE_URL = os.getenv('BASE_URL')
    MODEL = os.getenv('MODEL')

    # If any of the variables are not set, raise an error
    if not AI_SECRET or not BASE_URL or not MODEL:
        raise ValueError("AI_SECRET, BASE_URL, and MODEL must be set")

system_prompt = """
You are the Oracle. You are an ancient, all-knowing being who speaks in riddles and cryptic truths.
You are able to answer any question. Your responses are short and to the point.
Your answers are ominous, foreboding, and metaphorical.
Use Discord formatting (Markdown) to make your prophecies feel dramatic.
For example: _italics_ for whispers, **bold** for warnings, > blockquotes for pronouncements, and `inline code` for cryptic single words.
Never break character or explain yourself.
"""

# Function to get the oracle's response
async def get_oracle_response(question):
    print(f"Getting oracle response for {question}")
    client = OpenAI(api_key=AI_SECRET, base_url=BASE_URL)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": question}]
    )
    print(f"Oracle response: {response.choices[0].message.content}")
    return response.choices[0].message.content

# Modal to ask the oracle a question
class QuestionModal(discord.ui.Modal, title="Question"):
    question = discord.ui.TextInput(
        label="Question", 
        placeholder="Ask the oracle a question", 
        style=discord.TextStyle.long, 
        required=True)
    async def on_submit(self, interaction: discord.Interaction):
        # Thinking indicator
        await interaction.response.defer(thinking=True)
        response = await get_oracle_response(self.question.value)
        await interaction.followup.send(f"{interaction.user.mention} has approached the oracle and asked: \n**{self.question.value}**\n...\n{response}")

    # View for a button to send the question to the oracle
class SendQuestionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = 60)
        self.answered = False # Has the oracle begun answering a question?
    
    @discord.ui.button(label="Ask the oracle", style=discord.ButtonStyle.danger, emoji="🔮")
    async def send_question_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Turn the button gray
        button.style = discord.ButtonStyle.gray
        button.disabled = True
        if not self.answered:
            self.answered = True
            await interaction.response.send_modal(QuestionModal())
            await interaction.followup.edit_message(interaction.message.id, view=self)
        else:
            await interaction.response.send_message("The oracle has already begun listening to another...", ephemeral=True)

    async def on_timeout(self) -> None:
        
        return await super().on_timeout()

# The oracle is a cog that allows the user to ask the oracle a question and get a silly ai response
class Oracle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Summon the oracle. You can summon the oracle, and it will reply to the first person who replies to the message.
    #@allowed_contexts(guilds=True, dms=True, private_channels=True)
    @commands.hybrid_command(name="summon", description="Summon the oracle")
    async def summon(self, ctx: commands.Context):
        initial_message = await ctx.send("The oracle has been summoned! You may now ask the almighty oracle a question. Only one of you reserves the right to this opportunity...", view=SendQuestionView())
        
async def setup(bot):
    await bot.add_cog(Oracle(bot))
