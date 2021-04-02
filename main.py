from discord.ext import commands
import os
import sqlite3
from pretty_help import PrettyHelp
import discord
import random

intents = discord.Intents.default()
intents.members = True
db = sqlite3.connect('database.db')
bot = commands.Bot(command_prefix='-!', help_command=PrettyHelp(), intents=intents)
blacklist = [" niger ", " nigger ", " nigga ", " nig ", " fag ", " faggot ", " tranny ", " dyke ", " chink ", " gooky ",
             " porch monkey ", " raghead ", " redskin ", " sliteye ", " slanteye ", " towel head ", " shemale ",
             " shylock ", " kike "]


@bot.event
async def on_ready():
    print('Bot is ready!')
    channel1 = bot.get_channel(819035422437015572)
    guild = bot.get_guild(818677928358576148)
    await channel1.edit(name=f"Members: {guild.member_count - 3}")
    await bot.change_presence(activity=discord.Activity(name="deez nuts", type=5))


@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)
    channel = message.channel.id

    cursor = db.cursor()
    cursor.execute(f"SELECT prefix FROM prefix WHERE user_id = {ctx.message.author.id}")
    current_prefix = cursor.fetchone()
    if current_prefix is None:
        current_prefix = "-!"
    else:
        current_prefix = current_prefix[0]

    bot.command_prefix = current_prefix

    if channel == 819039790715633704:
        await message.add_reaction("✅")
        await message.add_reaction("❌")

    content = message.content.lower()
    content = content.replace("*", "")
    content = content.replace("|", "")
    content = content.replace("-", "")
    content = content.replace("_", "")
    content = content.replace("~", "")
    content = content.replace("`", "")
    content = content.replace("\\", "")
    content = " " + content + " "

    for i in blacklist:
        if i in content:
            await message.delete()
            muted_role = discord.utils.get(ctx.guild.roles, name='Muted')
            await message.author.add_roles(muted_role)

    if message.author.id != 775893655356702762:
        exp_gained = random.randint(1, 4)

        cursor = db.cursor()
        cursor.execute(f"SELECT exp FROM exp WHERE user_id = {message.author.id} AND guild_id = {ctx.guild.id}")
        current_exp = cursor.fetchone()
        if current_exp is None:
            db.execute("INSERT into exp(guild_id, user_id, exp, lvl_req, lvl) VALUES(?, ?, ?, ?, ?)",
                       (ctx.guild.id, message.author.id, exp_gained, 100, 1))
            db.commit()
        else:
            db.execute(
                f"UPDATE exp SET exp = exp + {exp_gained} WHERE user_id = {message.author.id} AND guild_id = {ctx.guild.id}")
            db.commit()
            cursor = db.cursor()
            cursor.execute(f"SELECT lvl_req FROM exp WHERE user_id = {message.author.id} AND guild_id = {ctx.guild.id}")
            lvl_req = cursor.fetchone()[0]
            if current_exp[0] + exp_gained >= lvl_req:
                db.execute(
                    f"UPDATE exp SET lvl = lvl + {1} WHERE user_id = {message.author.id} AND guild_id = {ctx.guild.id}")
                db.commit()
                db.execute(
                    f"UPDATE exp SET exp = {0} WHERE user_id = {message.author.id} AND guild_id = {ctx.guild.id}")
                db.commit()
                db.execute(
                    f"UPDATE exp SET lvl_req = {int(lvl_req * 1.25)} WHERE user_id = {message.author.id} AND guild_id = {ctx.guild.id}")
                db.commit()
                cursor = db.cursor()
                cursor.execute(f"SELECT lvl FROM exp WHERE user_id = {message.author.id} AND guild_id = {ctx.guild.id}")
                current_lvl = cursor.fetchone()[0]
                embed = discord.Embed(title="Level Up:", color=message.author.color)
                embed.set_thumbnail(url=f'{message.author.avatar_url}')
                embed.add_field(
                    name=f"{message.author.display_name} leveled up from level {current_lvl - 1} to {current_lvl}!",
                    value=f"Required exp to level up is now {round(lvl_req * 1.25)}.")

                channel1 = bot.get_channel(819039449379635231)

                await channel1.send(f"{message.author.mention}", embed=embed)

    await bot.process_commands(message)


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(818958012257009674)
    embed = discord.Embed(title="Arrival:", color=0x00FF00)
    embed.add_field(name="User:", value=f"Welcome <@!{member.id}>!")
    embed.set_thumbnail(url=f"{member.avatar_url}")
    await channel.send(embed=embed)
    channel1 = bot.get_channel(819035422437015572)
    guild = bot.get_guild(818677928358576148)
    await channel1.edit(name=f"Members: {guild.member_count - 3}")


@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(818958012257009674)
    embed = discord.Embed(title="Departure:", color=0xFF0000)
    embed.add_field(name="User:", value=f"Bye-bye <@!{member.id}>!")
    embed.set_thumbnail(url=f"{member.avatar_url}")
    await channel.send(embed=embed)
    channel1 = bot.get_channel(819035422437015572)
    guild = bot.get_guild(818677928358576148)
    await channel1.edit(name=f"Members: {guild.member_count - 3}")


@bot.command(brief="Verify your account in the server.")
async def verify(ctx):
    message = ctx.message
    if message.channel.id == 818680118427123763:
        verified_role = discord.utils.get(ctx.guild.roles, name='Pedestrian')
        await message.author.add_roles(verified_role)

    await message.delete()


@bot.command(brief="Get certain roles.")
async def role(ctx, role_id: int):
    if ctx.channel.id == 819008725695201280:
        await ctx.message.delete()
        assigned_role = discord.utils.get(ctx.guild.roles, id=role_id)
        if assigned_role.position > 3:
            embed = discord.Embed(title="Role Error:", color=0xFF0000)
            embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
            embed.add_field(name="Missing Permissions:", value='Please enter a valid role ID.')
            await ctx.send(embed=embed, delete_after=5)
            return
        else:
            await ctx.message.author.add_roles(assigned_role)
            embed = discord.Embed(title="Role:", color=0x00FF00)
            embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
            embed.add_field(name="Role Given:", value=f'You received the {assigned_role.name} role.')
            await ctx.send(embed=embed, delete_after=5)
            return
    else:
        embed = discord.Embed(title="Role Error:", color=0xFF0000)
        embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
        embed.add_field(name="Description:", value=f'Command was run in the wrong channel.')

        await ctx.send(embed=embed, delete_after=5)
        return


@role.error
async def role_handler(ctx, error):
    member = ctx.message.author
    if isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="Role Error:", color=0xFF0000)
        embed.set_thumbnail(url=f"{member.avatar_url}")
        embed.add_field(name="Missing ID:", value='Please enter a role ID.')
        await ctx.send(embed=embed, delete_after=5)
    else:
        raise error


@bot.command(brief="Change your prefix.")
async def prefix(ctx, *, pfx: str):
    cursor = db.cursor()
    cursor.execute(f"SELECT prefix FROM prefix WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
    current_prefix = cursor.fetchone()
    if current_prefix is None:
        db.execute("INSERT into prefix(guild_id, user_id, prefix) VALUES(?, ?, ?)",
                   (ctx.guild.id, ctx.message.author.id, pfx))
        db.commit()
    else:
        db.execute(f"UPDATE prefix SET prefix = ? WHERE user_id = ? AND guild_id = ?",
                   (pfx, ctx.message.author.id, ctx.guild.id))
        db.commit()

    await ctx.send("Prefix changed!")


for filename in os.listdir("./cogs"):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[0:-3]}')

bot.run('Nzc1ODkzNjU1MzU2NzAyNzYy.X6s9Rg.bq8o3Y5iMByv7kfC-yDKZ67vJrU')
