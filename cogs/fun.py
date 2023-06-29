import discord
from discord.ext import commands


class FunCog(commands.Cog, name="Fun"):
    """Fun commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Displays a specified user's profile picture.")
    async def pfp(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        embed = discord.Embed(title=f"{member.display_name}'s Profile Picture:", color=member.color)
        embed.set_image(url=member.avatar_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(FunCog(bot))
    print("Fun is loaded...")
