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
        cursor = db.cursor()
        cursor.execute("SELECT user_id, lvl FROM exp ORDER BY lvl DESC LIMIT 10")
        result = cursor.fetchall()

        embed = discord.Embed(title="Leaderboard:", color=ctx.author.color)
        embed.set_thumbnail(url=ctx.author.avatar_url)

        for i, (user_id, lvl) in enumerate(result, 1):
            user = self.bot.get_user(user_id)
            embed.add_field(name=f"#{i}", value=f"{user.mention} is level {lvl}.", inline=False)

        await ctx.send(embed=embed)

    @commands.command(brief='Displays level and exp progress.', alises=["r"])
    async def rank(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        cursor = db.cursor()
        cursor.execute("SELECT exp, lvl, lvl_req FROM exp WHERE user_id = ?", (member.id,))
        user_data = cursor.fetchone()

        current_exp, current_lvl, current_lvl_req = user_data or (0, 1, 100)

        percentage = current_exp / current_lvl_req
        bar_percentage = min(round(percentage * 15), 14)
        bar = ["─" if i < bar_percentage else "●" for i in range(15)]
        bar1 = ''.join(bar)

        embed = discord.Embed(title="Rank: ", color=member.color)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(
            name=f"{member.display_name} is level {current_lvl}.",
            value=f"Progress: {bar1} {round(percentage * 100, 2)}%",
            inline=True
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ExpCog(bot))
    print("Exp is loaded...")
