import os
import sqlite3
import random
import discord
from discord.ext import commands
from pretty_help import PrettyHelp

intents = discord.Intents.default()
intents.members = True

db = sqlite3.connect('database.db')
bot = commands.Bot(command_prefix='-!', help_command=PrettyHelp(), intents=intents)
token = "token"

member_count_channel = 0
member_leave_channel = 0
member_join_channel = 0
level_up_channel = 0
verify_channel = 0

@bot.event
async def on_ready():
    print('Bot is ready!')
    guild = bot.get_guild(member_count_channel)
    channel1 = bot.get_channel(member_count_channel)
    await channel1.edit(name=f"Members: {guild.member_count - 3}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    ctx = await bot.get_context(message)
    channel = message.channel.id

    cursor = db.cursor()
    cursor.execute("SELECT prefix FROM prefix WHERE user_id = ?", (ctx.message.author.id,))
    current_prefix = cursor.fetchone()
    if current_prefix is None:
        current_prefix = "-!"
    else:
        current_prefix = current_prefix[0]

    bot.command_prefix = current_prefix

    exp_gained = random.randint(1, 4)

    cursor.execute("SELECT exp FROM exp WHERE user_id = ? AND guild_id = ?", (message.author.id, ctx.guild.id))
    current_exp = cursor.fetchone()
    if current_exp is None:
        db.execute("INSERT INTO exp(guild_id, user_id, exp, lvl_req, lvl) VALUES(?, ?, ?, ?, ?)",
                   (ctx.guild.id, message.author.id, exp_gained, 100, 1))
        db.commit()
    else:
        new_exp = current_exp[0] + exp_gained
        db.execute("UPDATE exp SET exp = ? WHERE user_id = ? AND guild_id = ?",
                   (new_exp, message.author.id, ctx.guild.id))
        db.commit()
        cursor.execute("SELECT lvl_req FROM exp WHERE user_id = ? AND guild_id = ?", (message.author.id, ctx.guild.id))
        lvl_req = cursor.fetchone()[0]
        if new_exp >= lvl_req:
            db.execute("UPDATE exp SET lvl = lvl + 1, exp = 0, lvl_req = ? WHERE user_id = ? AND guild_id = ?",
                       (int(lvl_req * 1.25), message.author.id, ctx.guild.id))
            db.commit()
            cursor.execute("SELECT lvl FROM exp WHERE user_id = ? AND guild_id = ?", (message.author.id, ctx.guild.id))
            current_lvl = cursor.fetchone()[0]
            embed = discord.Embed(title="Level Up:", color=message.author.color)
            embed.set_thumbnail(url=f'{message.author.avatar_url}')
            embed.add_field(
                name=f"{message.author.display_name} leveled up from level {current_lvl - 1} to {current_lvl}!",
                value=f"Required exp to level up is now {round(lvl_req * 1.25)}.")

            channel1 = bot.get_channel(level_up_channel)
            await channel1.send(message.author.mention, embed=embed)

    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(member_join_channel)
    embed = discord.Embed(title="Arrival:", color=0x00FF00)
    embed.add_field(name="User:", value=f"Welcome <@!{member.id}>!")
    embed.set_thumbnail(url=member.avatar_url)
    await channel.send(embed=embed)
    channel1 = bot.get_channel(member_count_channel)
    guild = bot.get_guild(member_count_channel)
    await channel1.edit(name=f"Members: {guild.member_count - 3}")


@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(member_leave_channel)
    embed = discord.Embed(title="Departure:", color=0xFF0000)
    embed.add_field(name="User:", value=f"Bye-bye <@!{member.id}>!")
    embed.set_thumbnail(url=member.avatar_url)
    await channel.send(embed=embed)
    channel1 = bot.get_channel(member_count_channel)
    guild = bot.get_guild(member_count_channel)
    await channel1.edit(name=f"Members: {guild.member_count - 3}")


@bot.command(brief="Verify your account in the server.")
async def verify(ctx):
    if ctx.channel.id == verify_channel:
        verified_role = discord.utils.get(ctx.guild.roles, name='Pedestrian')
        await ctx.author.add_roles(verified_role)
    await ctx.message.delete()


@bot.command(brief="Change your prefix.")
async def prefix(ctx, *, pfx: str):
    cursor = db.cursor()
    cursor.execute("SELECT prefix FROM prefix WHERE user_id = ? AND guild_id = ?", (ctx.message.author.id, ctx.guild.id))
    current_prefix = cursor.fetchone()
    if current_prefix is None:
        db.execute("INSERT INTO prefix(guild_id, user_id, prefix) VALUES(?, ?, ?)",
                   (ctx.guild.id, ctx.message.author.id, pfx))
        db.commit()
    else:
        db.execute("UPDATE prefix SET prefix = ? WHERE user_id = ? AND guild_id = ?",
                   (pfx, ctx.message.author.id, ctx.guild.id))
        db.commit()

    await ctx.send("Prefix changed!")


for filename in os.listdir("./cogs"):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(token)
