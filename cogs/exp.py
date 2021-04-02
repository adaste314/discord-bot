import discord
from discord.ext import commands
import sqlite3

db = sqlite3.connect("database.db")


class ExpCog(commands.Cog, name="Exp"):
    """Experience commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Displays the top ten most active users.", aliases=["elb"])
    async def exp_leaderboard(self, ctx):
        message = ctx.message
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id, lvl from exp ORDER BY lvl DESC LIMIT 10")
        result = cursor.fetchall()
        embed = discord.Embed(title="Leaderboard:", color=message.author.color)
        embed.set_thumbnail(url=f"{message.author.avatar_url}")
        for i, x in enumerate(result, 1):
            embed.add_field(name=f"#{i}", value=f"<@!{str(x[0])}> is level {str(x[1])}.", inline=False)
        await ctx.send(embed=embed)

    @commands.command(brief='Displays level and exp progress.', alieses=["r"])
    async def rank(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.message.author
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id FROM exp WHERE user_id = {member.id}")
        user_id = cursor.fetchone()
        if user_id is None:
            current_exp, current_lvl, current_lvl_req = 0, 1, 100
        else:
            cursor = db.cursor()
            cursor.execute(f"SELECT exp FROM exp WHERE user_id = {member.id}")
            current_exp = cursor.fetchone()[0]
            cursor = db.cursor()
            cursor.execute(f"SELECT lvl FROM exp WHERE user_id = {member.id}")
            current_lvl = cursor.fetchone()[0]
            cursor = db.cursor()
            cursor.execute(f"SELECT lvl_req FROM exp WHERE user_id = {member.id}")
            current_lvl_req = cursor.fetchone()[0]

        bar = ["━", "━", "━", "━", "━", "━", "━", "━", "━", "━", "━", "━", "━", "━", "━"]
        percentage = current_exp / current_lvl_req
        bar_percentage = round(percentage * 15)
        if bar_percentage > len(bar) - 1:
            bar_percentage = len(bar) - 1
        for i in range(bar_percentage):
            bar[i] = "─"

        bar[bar_percentage] = "●"
        bar1 = ""
        for i in bar:
            bar1 = bar1 + i

        embed = discord.Embed(title="Rank: ", color=member.color)
        embed.set_thumbnail(url=f'{member.avatar_url}')
        embed.add_field(name=f"{member.display_name} is level {current_lvl}.", value=f"Progress: {bar1} {round(percentage * 100, 2)}%", inline=True)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ExpCog(bot))
    print("Exp is loaded...")
