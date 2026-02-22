import discord
from discord.ext import commands

class MyButton(discord.ui.Button):
    def __init__(self, label):
        super().__init__(label=label)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'You clicked {self.label}!')

class MyView(discord.ui.View):
    def __init__(self):
        super().__init__()
        button = MyButton(label='Click Me!')
        self.add_item(button)

bot = commands.Bot(command_prefix='!')

@bot.command()
async def button_example(ctx):
    await ctx.send('Here is a button!', view=MyView())

bot.run('YOUR_BOT_TOKEN')