import discord
from discord.ext import commands


class ModCog(commands.Cog, name="Moderation"):
    """Moderation commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="Mutes a specified user.")
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name='Muted')

        if not muted_role:
            name = 'Muted'
            perms = discord.Permissions(
                read_messages=True,
                create_instant_invite=True,
                stream=True,
                speak=True,
                connect=True,
                use_voice_activation=True,
                view_channel=True,
                read_message_history=True
            )
            muted_role = await ctx.guild.create_role(name=name, permissions=perms)

        if muted_role in member.roles:
            embed = discord.Embed(title="Failed to mute:", color=0xFF0000)
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="User:", value=member.mention)
            embed.add_field(name="Reason:", value=f"{member.display_name} is already muted.")
            await ctx.send(embed=embed)
            return

        await member.add_roles(muted_role)
        embed = discord.Embed(title="Mute:", color=0xFF0000)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="User Muted:", value=member.mention)
        await ctx.send(embed=embed)

    @commands.command(brief="Unmutes a specified muted user.")
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name='Muted')
        await member.remove_roles(muted_role)
        embed = discord.Embed(title="Unmute:", color=0x00FF00)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="User:", value=member.mention)
        await ctx.send(embed=embed)

    @commands.command(brief="Bans a specified user.")
    @commands.has_permissions(manage_channels=True)
    async def ban(self, ctx, member: discord.Member):
        await member.ban(reason=None)
        embed = discord.Embed(title="Ban:", color=0xFF0000)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name="User:", value=member.mention)
        await ctx.send(embed=embed)

    @commands.command(brief="Deletes multiple messages.")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)

    @commands.command(brief="Starts a poll in the polls channel.")
    @commands.has_permissions(manage_channels=True)
    async def poll(self, ctx, *, content: str):
        await ctx.message.delete()
        channel = self.bot.get_channel(819030044441051146)
        embed = discord.Embed(title=f"Poll: (by {ctx.author.display_name})", color=0x9b59b6)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.add_field(name="Question:", value=content, inline=True)

        role = discord.utils.get(ctx.guild.roles, name="Poll Pings")

        msg = await channel.send(role.mention, embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

    @commands.command(brief="Set channels for system messages.")
    async def set_system(self, ctx, channel_id: int, type: str):
        types = ['join', 'leave', 'level', 'verify']

        if type not in types:
            embed = discord.Embed(title="System Channel Set Error:", color=0xFF0000)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.add_field(name="Description:", value=f'Invalid type! Valid types include {types}.')
            await ctx.send(embed=embed)
        else:
            # Handle the channel setting logic here
            pass

    @set_system.error
    async def set_system_error_handler(self, ctx, error):
        member = ctx.author

        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title="System Channel Set Error:", color=0xFF0000)
            embed.set_thumbnail(url=member.avatar_url)
            embed.add_field(name="Description:", value='Missing arguments! Arguments required: (channel_id, type)')
            await ctx.send(embed=embed, delete_after=5)
        else:
            raise error


def setup(bot):
    bot.add_cog(ModCog(bot))
    print("Moderation is loaded...")
