import discord
from discord.ext import commands
import os
import json

with open('config.json') as f:
    config = json.load(f)

BOT_TOKEN = config['token']
allowed_channels = config['allowed_channels']
ACCOUNTS_FOLDER = config['accounts_folder']

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

GIF_URL = 'https://cdn.discordapp.com/attachments/1231183727929851957/1231257859891658813/ezgif.com-video-to-gif-converter.gif?ex=6633aa3d&is=663258bd&hm=9e3b5b86cc9fd76aa54cddc46467b274ebe595c4b57288de676dcf467b758e24&'

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(title="Help", description="List of available commands", color=discord.Color.blue())
    embed.add_field(name="$gen [file]", value="Generate an account from the specified file. Sent via DM.", inline=False)
    embed.add_field(name="$stock", value="List available accounts and their line counts.", inline=False)
    embed.set_footer(text="Use $help [command] for more info on a specific command.")
    embed.set_image(url=GIF_URL)
    await ctx.send(embed=embed)

@bot.command()
async def gen(ctx, file: str):
    if ctx.channel.id not in allowed_channels:
        await ctx.send("You are not allowed to use this command in this channel.")
        return
    file_path = os.path.join(ACCOUNTS_FOLDER, f'{file}.txt')
    if not os.path.exists(file_path):
        await ctx.send('File not found.')
        return
    with open(file_path, 'r') as f:
        first_line = f.readline().strip()
    with open(file_path, 'r') as f:
        lines = f.readlines()
    with open(file_path, 'w') as f:
        f.writelines(lines[1:])
    try:
        email_user, password = first_line.split(':', 1)
    except ValueError:
        await ctx.send("Invalid format in the first line of the file.")
        return
    embed = discord.Embed(title=f"Generated {file}", color=discord.Color.purple())
    embed.add_field(name="Email/User:", value=email_user.strip(), inline=False)
    embed.add_field(name="Password:", value=password.strip(), inline=False)
    embed.set_image(url=GIF_URL)
    try:
        await ctx.author.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("Unable to send DM. The user may have DMs disabled.")
        return
    await ctx.send("Sent to your DMs. If you don't see it, open them.")

@bot.command()
async def stock(ctx):
    if ctx.channel.id not in allowed_channels:
        await ctx.send("You are not allowed to use this command in this channel.")
        return
    files = os.listdir(ACCOUNTS_FOLDER)
    txt_files = [file for file in files if file.endswith('.txt')]
    stock_embed = discord.Embed(title="Available accounts", color=discord.Color.blue())
    for file in txt_files:
        file_path = os.path.join(ACCOUNTS_FOLDER, file)
        with open(file_path, 'r') as f:
            lines = f.readlines()
        account_name = file.replace('.txt', '')
        stock_embed.add_field(name="", value=f"``{account_name}: {len(lines)}``", inline=True)
    stock_embed.set_image(url=GIF_URL)
    await ctx.send(embed=stock_embed)

@bot.event
async def on_command_error(ctx, error):
    embed = discord.Embed(title="Error", color=discord.Color.red())
    embed.add_field(name="Command", value=ctx.command.name, inline=False)
    embed.add_field(name="Error", value=str(error), inline=False)
    await ctx.send(embed=embed)

bot.run(BOT_TOKEN)
