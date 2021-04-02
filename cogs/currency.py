import discord
from discord.ext import commands
import sqlite3
import random
import time

db = sqlite3.connect("database.db")


class CurrencyCog(commands.Cog, name="Currency"):
    """Currency commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief="The command to earn coins in the server.")
    async def work(self, ctx):
        cursor = db.cursor()
        cursor.execute(f"SELECT time, length FROM cooldown WHERE user_id = ? AND guild_id = ? AND command = ?",
                       (ctx.message.author.id, ctx.guild.id, "work"))
        time_length = cursor.fetchall()
        if time_length:
            time1 = time_length[0][0]
            length = time_length[0][1]
            difference = time.time() - time1
            if difference >= length:
                db.execute("DELETE FROM cooldown WHERE user_id = ? AND guild_id = ? AND command = ?",
                           (ctx.message.author.id, ctx.guild.id, "work"))
                db.commit()
            else:
                embed = discord.Embed(title="Cooldown:", color=0xFF0000)
                embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                time_left = length - difference
                hours = time_left // 3600
                mins = (time_left // 60) - (hours * 60)
                secs = time_left % 60
                embed.add_field(name="Time Left:",
                                value='This command is on cooldown, please try again in {:.0f}h {:.0f}m {:.0f}s'.format(
                                    hours, mins, secs))
                await ctx.send(embed=embed)
                return

        member = ctx.message.author
        cursor = db.cursor()
        amount_earned = random.randint(450, 550)
        cursor.execute(f'SELECT coins FROM currency WHERE user_id = {member.id}')
        current_coins = cursor.fetchone()
        if current_coins is None:
            db.execute("INSERT into currency(guild_id, user_id, coins, multiplier, daily, company_count) VALUES(?, ?, ?, ?, ?, ?)",
                       (ctx.guild.id, member.id, amount_earned, 1, 0, 0))
            db.commit()
            return
        else:
            cursor = db.cursor()
            cursor.execute(f"SELECT multiplier FROM currency WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")
            multiplier = cursor.fetchone()
            if multiplier is None:
                multiplier = 1
            else:
                multiplier = multiplier[0]
            amount_earned = round(amount_earned * multiplier)
            cursor.execute(f"SELECT coins FROM currency WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")
            current_bal = cursor.fetchone()[0]
            if current_bal < 0:
                db.execute(f"UPDATE currency SET coins = {0} WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")
                db.commit()
            db.execute(f"UPDATE currency SET coins = coins + {amount_earned} WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")
            db.commit()

        cursor = db.cursor()
        cursor.execute(f"SELECT multiplier FROM currency WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")
        multiplier = cursor.fetchone()[0]
        embed = discord.Embed(title="Work:", color=member.color)
        embed.set_thumbnail(url=f'{member.avatar_url}')
        embed.add_field(name="Amount Earned:",
                        value=f"You earned {amount_earned} coins with a {multiplier}x multiplier!")

        await ctx.send(embed=embed)

        cursor = db.cursor()
        cursor.execute(f"SELECT user_id FROM cooldown WHERE user_id = ? AND guild_id = ? AND command = ?",
                       (ctx.message.author.id, ctx.guild.id, "work"))
        if cursor.fetchone() is None:
            db.execute("INSERT into cooldown(guild_id, user_id, command, length, time) VALUES(?, ?, ?, ?, ?)",
                       (ctx.guild.id, ctx.message.author.id, "work", 600, int(time.time())))
            db.commit()
        else:
            return

    @commands.command(brief="Displays a specified user's current balance.", aliases=["bal"])
    async def balance(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.message.author
        cursor = db.cursor()
        cursor.execute(f"SELECT coins FROM currency WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")
        current_coins = cursor.fetchone()
        if current_coins is None:
            embed = discord.Embed(title="Current Balance:", color=member.color)
            embed.set_thumbnail(url=f"{member.avatar_url}")
            embed.add_field(name="Coins:", value=f"<@!{member.id}> has 0 coins!")
        else:
            embed = discord.Embed(title="Current Balance:", color=member.color)
            embed.set_thumbnail(url=f"{member.avatar_url}")
            embed.add_field(name="Coins:", value=f"<@!{member.id}> has {current_coins[0]} coins!")

        await ctx.send(embed=embed)

    @commands.command(brief="Displays the top ten richest users.", aliases=["lb"])
    async def leaderboard(self, ctx):
        message = ctx.message
        cursor = db.cursor()
        cursor.execute(f"SELECT user_id, coins from currency ORDER BY coins DESC LIMIT 10")
        result = cursor.fetchall()
        embed = discord.Embed(title="Leaderboard:", color=message.author.color)
        embed.set_thumbnail(url=f"{message.author.avatar_url}")
        for i, x in enumerate(result, 1):
            embed.add_field(name=f"#{i}", value=f"<@!{str(x[0])}> has {str(x[1])} coins.", inline=False)
        await ctx.send(embed=embed)

    @commands.command(brief="Allows the user to gamble for coins.")
    async def gamble(self, ctx, bid):
        cursor = db.cursor()
        cursor.execute(f"SELECT time, length FROM cooldown WHERE user_id = ? AND guild_id = ? AND command = ?",
                       (ctx.message.author.id, ctx.guild.id, "gamble"))
        time_length = cursor.fetchall()
        if time_length:
            time1 = time_length[0][0]
            length = time_length[0][1]
            difference = time.time() - time1
            if difference >= length:
                db.execute("DELETE FROM cooldown WHERE user_id = ? AND guild_id = ? AND command = ?",
                           (ctx.message.author.id, ctx.guild.id, "gamble"))
                db.commit()
            else:
                embed = discord.Embed(title="Cooldown:", color=0xFF0000)
                embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                time_left = length - difference
                hours = time_left // 3600
                mins = (time_left // 60) - (hours * 60)
                secs = time_left % 60
                embed.add_field(name="Time Left:",
                                value='This command is on cooldown, please try again in {:.0f}h {:.0f}m {:.0f}s'.format(
                                    hours, mins, secs))
                await ctx.send(embed=embed)
                return

        bid = int(bid)
        cursor = db.cursor()
        cursor.execute(
            f"SELECT coins FROM currency WHERE user_id = {int(ctx.message.author.id)} AND guild_id = {ctx.guild.id}")
        current_coins = cursor.fetchone()
        if current_coins is None:
            embed = discord.Embed(title="Gamble Error:", color=0xFF0000)
            embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
            embed.add_field(name="Description:", value="You have no coins!")
            await ctx.send(embed=embed)
            return
        else:
            if bid > int(current_coins[0]):
                embed = discord.Embed(title="Gamble Error:", color=0xFF0000)
                embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                embed.add_field(name="Description:", value="You don't have enough coins!")
                await ctx.send(embed=embed)
                return
            elif bid <= 0:
                embed = discord.Embed(title="Gamble Error:", color=0xFF0000)
                embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                embed.add_field(name="Description:", value="You have no coins!")
                await ctx.send(embed=embed)
                return
            else:
                db.execute(
                    f"UPDATE currency SET coins = coins - {bid} WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
                db.commit()
                odds = random.randint(2, 10)
                embed = discord.Embed(title="Gamble:", color=ctx.message.author.color)
                embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                embed.add_field(name="User:", value=f"<@!{ctx.message.author.id}>")
                embed.add_field(name="Bet:", value=f"{bid}")
                embed.add_field(name="Odds / Reward:", value=f"1/{odds} for a {odds}x payout.")
                msg = await ctx.send(embed=embed)
                cursor = db.cursor()
                cursor.execute(f"SELECT user_id FROM cooldown WHERE user_id = ? AND guild_id = ? AND command = ?",
                               (ctx.message.author.id, ctx.guild.id, "gamble"))
                if cursor.fetchone() is None:
                    db.execute("INSERT into cooldown(guild_id, user_id, command, length, time) VALUES(?, ?, ?, ?, ?)",
                               (ctx.guild.id, ctx.message.author.id, "gamble", 1800, int(time.time())))
                    db.commit()
                else:
                    return
                await msg.add_reaction("✅")
                await msg.add_reaction("❌")
                reaction1, user1 = await self.bot.wait_for("reaction_add",
                                                           check=lambda reaction, user: user == ctx.author)
                if str(reaction1.emoji) == "✅":
                    if random.randint(1, odds) == 1:
                        winnings = bid * (odds + 1)
                        db.execute(
                            f"UPDATE currency SET coins = coins + {winnings} WHERE user_id = {ctx.message.author.id}")
                        db.commit()
                        embed = discord.Embed(title="Gamble:", color=0x00FF00)
                        embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                        embed.add_field(name="Results:", value=f"You won {winnings} coins!")
                        await msg.edit(embed=embed)
                        return
                    else:
                        embed = discord.Embed(title="Gamble:", color=0xFF0000)
                        embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                        embed.add_field(name="Results:", value=f"You lost {bid} coins!")
                        await msg.edit(embed=embed)
                        return
                else:
                    db.execute(
                        f"UPDATE currency SET coins = coins + {bid} WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
                    db.commit()
                    await msg.edit(embed=embed, delete_after=5)

    @gamble.error
    async def gamble_handler(self, ctx, error):
        member = ctx.message.author
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title="Gamble Error:", color=0xFF0000)
            embed.set_thumbnail(url=f"{member.avatar_url}")
            embed.add_field(name="Missing Bid:", value='Please enter an amount to bid.')
            await ctx.send(embed=embed)
        else:
            raise error

    @commands.command(brief="A shop command where a user can buy upgrades.")
    async def shop(self, ctx):
        cursor = db.cursor()
        cursor.execute(
            f"SELECT coins FROM currency WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
        current_coins = cursor.fetchone()
        cursor = db.cursor()
        cursor.execute(
            f"SELECT multiplier FROM currency WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
        current_multiplier = cursor.fetchone()
        if current_multiplier is None:
            current_multiplier = 1
        else:
            current_multiplier = current_multiplier[0]

        if current_coins is None:
            current_coins = 0
        else:
            current_coins = current_coins[0]

        embed = discord.Embed(title="Shop:", color=ctx.message.author.color)
        embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
        embed.add_field(name="#1: Raise (1.5x)", value="75000 coins", inline=False)
        embed.add_field(name="#2: Promotion (2x)", value="355000 coins", inline=False)
        embed.add_field(name="#3: Assistant (2.5x)", value="895000 coins", inline=False)
        embed.add_field(name="#4: Company (3.5x)", value="4.5m coins", inline=False)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction(str('1️⃣'))
        await msg.add_reaction(str('2️⃣'))
        await msg.add_reaction(str('3️⃣'))
        await msg.add_reaction(str('4️⃣'))
        reaction1, user1 = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author)
        if str(reaction1.emoji) == str('1️⃣'):
            if current_coins < 75000:
                embed = discord.Embed(title="Shop Error:", color=0xFF0000)
                embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                embed.add_field(name="Description:", value="You don't have enough coins!")
                await msg.edit(embed=embed, delete_after=5)
            else:
                db.execute(
                    f"UPDATE currency SET coins = coins - {75000} WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
                db.execute(
                    f"UPDATE currency SET multiplier = {1.5} WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
                db.commit()

                embed = discord.Embed(title="Shop:", color=0x00FF00)
                embed.set_thumbnail(url=f'{ctx.message.author.avatar_url}')
                embed.add_field(name='Purchase:', value="Thank you for purchasing a raise!")
                await msg.edit(embed=embed, delete_after=5)

        elif str(reaction1.emoji) == str('2️⃣'):
            if current_multiplier == 1.5:
                if current_coins < 355000:
                    embed = discord.Embed(title="Shop Error:", color=0xFF0000)
                    embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                    embed.add_field(name="Description:", value="You don't have enough coins!")
                    await msg.edit(embed=embed, delete_after=5)
                else:
                    db.execute(
                        f"UPDATE currency SET coins = coins - {355000} WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
                    db.execute(
                        f"UPDATE currency SET multiplier = {2} WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
                    db.commit()

                    embed = discord.Embed(title="Shop:", color=0x00FF00)
                    embed.set_thumbnail(url=f'{ctx.message.author.avatar_url}')
                    embed.add_field(name='Purchase:', value="Thank you for purchasing a promotion!")
                    await msg.edit(embed=embed, delete_after=5)
            elif current_multiplier >= 2:
                embed = discord.Embed(title="Shop Error:", color=0xFF0000)
                embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                embed.add_field(name="Description:", value="You already have this upgrade!")
                await msg.edit(embed=embed, delete_after=5)
            else:
                embed = discord.Embed(title="Shop Error:", color=0xFF0000)
                embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                embed.add_field(name="Description:", value="You need to buy the previous upgrade!")
                await msg.edit(embed=embed, delete_after=5)

        elif str(reaction1.emoji) == str('3️⃣'):
            if current_multiplier == 2:
                if current_coins < 895000:
                    embed = discord.Embed(title="Shop Error:", color=0xFF0000)
                    embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                    embed.add_field(name="Description:", value="You don't have enough coins!")
                    await msg.edit(embed=embed, delete_after=5)
                else:
                    db.execute(
                        f"UPDATE currency SET coins = coins - {895000} WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
                    db.execute(
                        f"UPDATE currency SET multiplier = {2.5} WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
                    db.commit()

                    embed = discord.Embed(title="Shop:", color=0x00FF00)
                    embed.set_thumbnail(url=f'{ctx.message.author.avatar_url}')
                    embed.add_field(name='Purchase:', value="Thank you for purchasing an assistant!")
                    await msg.edit(embed=embed, delete_after=5)
            elif current_multiplier >= 2.5:
                embed = discord.Embed(title="Shop Error:", color=0xFF0000)
                embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                embed.add_field(name="Description:", value="You already have this upgrade!")
                await msg.edit(embed=embed, delete_after=5)
            else:
                embed = discord.Embed(title="Shop Error:", color=0xFF0000)
                embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                embed.add_field(name="Description:", value="You need to buy the previous upgrade!")
                await msg.edit(embed=embed, delete_after=5)

        else:
            if current_multiplier == 2.5:
                if current_coins < 4500000:
                    embed = discord.Embed(title="Shop Error:", color=0xFF0000)
                    embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                    embed.add_field(name="Description:", value="You don't have enough coins!")
                    await msg.edit(embed=embed, delete_after=5)
                else:
                    cursor = db.cursor()
                    cursor.execute("SELECT company_count FROM currency WHERE user_id = ? AND guild_id = ?", (ctx.message.author.id, ctx.guild.id))
                    company_count = cursor.fetchone()
                    if company_count is None:
                        company_count = 0
                    else:
                        company_count = company_count[0]

                    if company_count >= 5:
                        embed = discord.Embed(title="Shop Error:", color=0xFF0000)
                        embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                        embed.add_field(name="Description:", value="You have reached the maximum amount of companies per user.")
                        await msg.edit(embed=embed, delete_after=5)
                    else:
                        db.execute(f"UPDATE currency SET coins = coins - {4500000} WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
                        db.execute(f"UPDATE currency SET multiplier = {3.5} WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
                        db.execute(f"UPDATE currency SET company_count = {company_count + 1} WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
                        db.commit()

                        embed = discord.Embed(title="Shop:", color=0x00FF00)
                        embed.set_thumbnail(url=f'{ctx.message.author.avatar_url}')
                        embed.add_field(name='Purchase:', value="Thank you for purchasing a Company!")
                        await msg.edit(embed=embed, delete_after=5)

                        db.execute("INSERT INTO company(guild_id, user_id, name, stocks, price) VALUES(?, ?, ?, ?, ?)",
                                   (ctx.guild.id, ctx.message.author.id, "Default Company", 100, 1))
                        db.commit()

            elif current_multiplier >= 3.5:
                embed = discord.Embed(title="Shop Error:", color=0xFF0000)
                embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                embed.add_field(name="Description:", value="You already have this upgrade!")
                await msg.edit(embed=embed, delete_after=5)
            else:
                embed = discord.Embed(title="Shop Error:", color=0xFF0000)
                embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                embed.add_field(name="Description:", value="You need to buy the previous upgrade!")
                await msg.edit(embed=embed, delete_after=5)

    @commands.command(brief="Daily reward for currency.", aliases=["d"])
    async def daily(self, ctx):
        cursor = db.cursor()
        cursor.execute(f"SELECT time, length FROM cooldown WHERE user_id = ? AND guild_id = ? AND command = ?",
                       (ctx.message.author.id, ctx.guild.id, "daily"))
        time_length = cursor.fetchall()
        if time_length:
            time1 = time_length[0][0]
            length = time_length[0][1]
            difference = time.time() - time1
            if difference >= length:
                db.execute("DELETE FROM cooldown WHERE user_id = ? AND guild_id = ? AND command = ?",
                           (ctx.message.author.id, ctx.guild.id, "daily"))
                db.commit()
            else:
                embed = discord.Embed(title="Cooldown:", color=0xFF0000)
                embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                time_left = length - difference
                hours = time_left // 3600
                mins = (time_left // 60) - (hours * 60)
                secs = time_left % 60
                embed.add_field(name="Time Left:",
                                value='This command is on cooldown, please try again in {:.0f}h {:.0f}m {:.0f}s'.format(
                                    hours, mins, secs))
                await ctx.send(embed=embed)
                return

        cursor = db.cursor()
        cursor.execute(f"SELECT daily FROM currency WHERE user_id = {ctx.message.author.id}")
        current_daily = cursor.fetchone()

        if current_daily is None:
            current_daily = 0
        else:
            current_daily = current_daily[0]

        reward = ((int(current_daily) + 1) * 50000) % 45000
        db.execute(
            f"UPDATE currency SET coins = coins + {reward} WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
        db.commit()
        db.execute(
            f"UPDATE currency SET daily = {current_daily + 0.2} WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
        db.commit()
        days_left = ((int(current_daily) + 1) - current_daily) / 0.2
        embed = discord.Embed(title="Daily Reward:", color=ctx.message.author.color)
        embed.set_thumbnail(url=f'{ctx.message.author.avatar_url}')
        embed.add_field(name=f"You received {reward} coins!", value=f"{int(days_left) - 1} days until upgrade.",
                        inline=False)

        await ctx.send(embed=embed)

        cursor = db.cursor()
        cursor.execute(f"SELECT user_id FROM cooldown WHERE user_id = ? AND guild_id = ? AND command = ?",
                       (ctx.message.author.id, ctx.guild.id, "daily"))
        if cursor.fetchone() is None:
            db.execute("INSERT into cooldown(guild_id, user_id, command, length, time) VALUES(?, ?, ?, ?, ?)",
                       (ctx.guild.id, ctx.message.author.id, "daily", 86400, int(time.time())))
            db.commit()
        else:
            return

    @commands.command(brief="Pays a user of your choice coins taken from your balance.", aliases=["g"])
    async def give(self, ctx, member: discord.Member, amount: int):
        cursor = db.cursor()
        cursor.execute(
            f"SELECT coins FROM currency WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
        bal = cursor.fetchone()
        if bal is None:
            bal = 0
        else:
            bal = bal[0]

        if amount < 0:
            embed = discord.Embed(title="Give Error:", color=0xFF0000)
            embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
            embed.add_field(name=f"Invalid amount!", value=f"You cannot input negative values.")
            await ctx.send(embed=embed, delete_after=5)
            return
        if amount > bal:
            missing = amount - bal
            embed = discord.Embed(title="Give Error:", color=0xFF0000)
            embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
            embed.add_field(name=f"You don't have enough coins!", value=f"Missing {missing} coins.")

            await ctx.send(embed=embed, delete_after=5)
            return

        embed = discord.Embed(title="Confirmation:", color=ctx.message.author.color)
        embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
        embed.add_field(name=f"Are you sure you want to give the coins to {member.display_name}?",
                        value=f"Coins: {amount}")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        reaction1, user1 = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author)
        if str(reaction1.emoji) == "✅":
            cursor = db.cursor()
            cursor.execute(f"SELECT coins FROM currency WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")
            bal1 = cursor.fetchone()
            if bal1 is None:
                embed = discord.Embed(title="Give Error:", color=0xFF0000)
                embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                embed.add_field(name="Receiver has no coins!",
                                value=f"{member.display_name} needs to work at least once.")
            else:
                db.execute(
                    f"UPDATE currency SET coins = coins + {amount} WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")
                db.commit()
                db.execute(
                    f"UPDATE currency SET coins = coins - {amount} WHERE user_id = {ctx.message.author.id} AND guild_id = {ctx.guild.id}")
                db.commit()
                embed = discord.Embed(title="Coins Given:", color=0x00FF00)
                embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                embed.add_field(name=f"User {member.display_name} received coins.", value=f"Coins: {amount}")

                await msg.edit(embed=embed, delete_after=5)
        else:
            embed = discord.Embed(title="Cancelled:", color=0xFF0000)
            embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
            embed.add_field(name=f"User {member.display_name} did not receive coins.", value=f"Command cancelled.")

            await msg.edit(embed=embed, delete_after=5)

    @give.error
    async def give_handler(self, ctx, error):
        member = ctx.message.author
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title="Give Error:", color=0xFF0000)
            embed.set_thumbnail(url=f"{member.avatar_url}")
            embed.add_field(name="Missing Bid:", value='Please enter all required arguments (user, amount).')
            await ctx.send(embed=embed)
        else:
            raise error

    @commands.command(brief="Rob another player of a fraction of their coins.")
    async def rob(self, ctx, member: discord.Member):
        cursor = db.cursor()
        cursor.execute(f"SELECT time, length FROM cooldown WHERE user_id = ? AND guild_id = ? AND command = ?",
                       (ctx.message.author.id, ctx.guild.id, "rob"))
        time_length = cursor.fetchall()
        if time_length:
            time1 = time_length[0][0]
            length = time_length[0][1]
            difference = time.time() - time1
            if difference >= length:
                db.execute("DELETE FROM cooldown WHERE user_id = ? AND guild_id = ? AND command = ?",
                           (ctx.message.author.id, ctx.guild.id, "rob"))
                db.commit()
            else:
                embed = discord.Embed(title="Cooldown:", color=0xFF0000)
                embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                time_left = length - difference
                hours = time_left // 3600
                mins = (time_left // 60) - (hours * 60)
                secs = time_left % 60
                embed.add_field(name="Time Left:",
                                value='This command is on cooldown, please try again in {:.0f}h {:.0f}m {:.0f}s'.format(
                                    hours, mins, secs))
                await ctx.send(embed=embed)
                return

        cursor = db.cursor()
        cursor.execute("SELECT coins FROM currency WHERE guild_id = ? AND user_id = ?",
                       (ctx.guild.id, ctx.message.author.id))
        current_coins = cursor.fetchone()
        if current_coins is None:
            return
        else:
            current_coins = current_coins[0]

        cursor = db.cursor()
        cursor.execute("SELECT coins FROM currency WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, member.id))
        member_coins = cursor.fetchone()
        if current_coins is None:
            member_coins = 0
        else:
            member_coins = member_coins[0]

        if (member_coins + 1) / (current_coins + 1) >= 5:
            embed = discord.Embed(title="Rob:", color=0xFF0000)
            embed.set_thumbnail(url=f'{member.avatar_url}')
            embed.add_field(name="Robbing Failure:", value=f"{member.display_name} is too rich for you to rob!")
            await ctx.send(embed=embed)
        else:
            robbed = int(member_coins * 0.05)
            cooldown = int((robbed / 10000) * 150)
            x = robbed / int(current_coins * 0.05)

            fail_chance = (x / .5) * 2

            random1 = random.randint(1, 100)
            if random1 >= fail_chance:
                db.execute("UPDATE currency SET coins = coins + ? WHERE user_id = ? AND guild_id = ?",
                           (robbed, ctx.message.author.id, ctx.guild.id))
                db.commit()
                db.execute("UPDATE currency SET coins = coins - ? WHERE user_id = ? AND guild_id = ?",
                           (robbed, member.id, ctx.guild.id))
                db.commit()
                embed = discord.Embed(title="Rob:", color=0x00FF00)
                embed.set_thumbnail(url=f'{member.avatar_url}')
                embed.add_field(name="Amount Robbed:", value=f"You stole {robbed} coins from {member.display_name}!")
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="Rob:", color=0xFF0000)
                embed.set_thumbnail(url=f'{member.avatar_url}')
                embed.add_field(name="Robbing Failure:",
                                value=f"You failed to steal {robbed} coins from {member.display_name}!")
                await ctx.send(embed=embed)
                cooldown = cooldown * 3

            cursor = db.cursor()
            cursor.execute(f"SELECT user_id FROM cooldown WHERE user_id = ? AND guild_id = ? AND command = ?",
                           (ctx.message.author.id, ctx.guild.id, "rob"))
            if cursor.fetchone() is None:
                db.execute("INSERT into cooldown(guild_id, user_id, command, length, time) VALUES(?, ?, ?, ?, ?)",
                           (ctx.guild.id, ctx.message.author.id, "rob", cooldown, int(time.time())))
                db.commit()
            else:
                return

    @rob.error
    async def rob_handler(self, ctx, error):
        member = ctx.message.author
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title="Rob Error:", color=0xFF0000)
            embed.set_thumbnail(url=f"{member.avatar_url}")
            embed.add_field(name="Missing Argument:", value='Please enter a member to rob.')
            await ctx.send(embed=embed)
        else:
            raise error

    @commands.command(brief="Set a name for your company.")
    async def name_company(self, ctx, *, name: str):
        cursor = db.cursor()
        cursor.execute("SELECT name FROM company WHERE user_id = ? AND guild_id = ?",
                       (ctx.message.author.id, ctx.guild.id))
        current_name = cursor.fetchone()
        if current_name is None:
            embed = discord.Embed(title="Company:", color=0xFF0000)
            embed.set_thumbnail(url=f'{ctx.author.avatar_url}')
            embed.add_field(name="Name Change Failure:", value=f"You need to buy the CEO upgrade to have a company!")
            await ctx.send(embed=embed)
        else:
            db.execute("UPDATE company SET name = ? WHERE user_id = ? AND guild_id = ?",
                       (name, ctx.message.author.id, ctx.guild.id))
            db.commit()
            await ctx.send("Company name changed!")

    @commands.command(brief="View information on a company.")
    async def company(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.message.author

        cursor = db.cursor()
        cursor.execute("SELECT name, stocks, price FROM company WHERE user_id = ? AND guild_id = ?",
                       (member.id, ctx.guild.id))
        info = cursor.fetchall()
        if info:
            name = info[0][0]
            stocks = info[0][1]
            price = info[0][2]
        else:
            embed = discord.Embed(title="Company Error:", color=0xFF0000)
            embed.set_thumbnail(url=f'{ctx.author.avatar_url}')
            embed.add_field(name="Description:", value=f"This user does not own a company!")
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="Company:", color=member.color)
        embed.set_thumbnail(url=f'{ctx.author.avatar_url}')
        embed.add_field(name="Name:", value=f"{name}", inline=False)
        embed.add_field(name="Shares:", value=f"{stocks}", inline=False)
        embed.add_field(name="Price per Stock:", value=f"{price} coin(s)", inline=False)
        await ctx.send(embed=embed)

    @commands.command(brief="Sell a company you own.")
    async def sell_company(self, ctx):
        cursor = db.cursor()
        cursor.execute("SELECT name, stocks, price FROM company WHERE user_id = ? AND guild_id = ?", (ctx.message.author.id, ctx.guild.id))
        info = cursor.fetchall()
        if info:
            name = info[0][0]
            stocks = info[0][1]
            price = info[0][2]
        else:
            embed = discord.Embed(title="Company Error:", color=0xFF0000)
            embed.set_thumbnail(url=f'{ctx.author.avatar_url}')
            embed.add_field(name="Description:", value=f"You do not own a company to sell!")
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="Company:", color=ctx.author.color)
        embed.set_thumbnail(url=f'{ctx.author.avatar_url}')
        embed.add_field(name="Name:", value=f"{name}", inline=False)
        embed.add_field(name="Shares:", value=f"{stocks}", inline=False)
        embed.add_field(name="Price per Stock:", value=f"{price} coin(s)", inline=False)
        embed.add_field(name="Confirmation:", value=f"Are you sure you want to sell this company for {stocks * price * 1000}? (There is a maximum of five companies per user.)", inline=True)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        reaction1, user1 = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author)
        if str(reaction1.emoji) == "✅":
            db.execute("DELETE FROM company WHERE user_id = ? AND guild_id = ?", (ctx.message.author.id, ctx.guild.id))
            db.execute("UPDATE currency SET multiplier = ? WHERE user_id = ? AND guild_id = ?", (2.5, ctx.message.author.id, ctx.guild.id))
            db.commit()
            cursor = db.cursor()
            cursor.execute("SELECT company_count FROM currency WHERE user_id = ? AND guild_id = ?", (ctx.message.author.id, ctx.guild.id))
            company_count = cursor.fetchone()
            if company_count is None:
                company_count = 0
            else:
                company_count = company_count[0]

            embed = discord.Embed(title="Company:", color=0x00FF00)
            embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
            embed.add_field(name=f"You sold your company.", value=f"{5 - company_count} companies left.")

            await msg.edit(embed=embed, delete_after=5)

        else:
            embed = discord.Embed(title="Cancelled:", color=0xFF0000)
            embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
            embed.add_field(name=f"You did not sell your company.", value=f"Command cancelled.")

            await msg.edit(embed=embed, delete_after=5)

    @commands.command(brief="Increase the amount of shares in your company.")
    async def company_stock(self, ctx):
        member = ctx.message.author

        cursor = db.cursor()
        cursor.execute("SELECT stocks, price FROM company WHERE user_id = ? AND guild_id = ?", (member.id, ctx.guild.id))
        info = cursor.fetchall()
        if info:
            stocks = info[0][0]
            price = info[0][1]
        else:
            embed = discord.Embed(title="Company Error:", color=0xFF0000)
            embed.set_thumbnail(url=f'{ctx.author.avatar_url}')
            embed.add_field(name="Description:", value=f"This user does not own a company!")
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(title="Company value:", color=member.color)
        embed.set_thumbnail(url=f'{ctx.author.avatar_url}')
        embed.add_field(name="Shares:", value=f"{stocks}", inline=False)
        embed.add_field(name="Price per Stock:", value=f"{price} coin(s)", inline=False)
        embed.add_field(name="Amount added:", value="How many shares would you like to add? ", inline=True)
        await ctx.send(embed=embed)

        msg = await self.bot.wait_for('message')
        total_price = 0
        if msg.author.id == member.id:
            if msg.content.isdigit():
                amount = int(msg.content)

                if amount + stocks > 5000:
                    embed = discord.Embed(title="Company Error:", color=0xFF0000)
                    embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                    embed.add_field(name=f"Invalid amount!", value=f"You cannot have more than 5000 shares.")
                    await ctx.send(embed=embed, delete_after=5)
                    return
                if amount < 0:
                    embed = discord.Embed(title="Company Error:", color=0xFF0000)
                    embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                    embed.add_field(name=f"Invalid amount!", value=f"You cannot input negative values.")
                    await ctx.send(embed=embed, delete_after=5)
                    return
                for i in range(amount):
                    price = price - (price / stocks)
                    total_price = total_price + (price * 10)
                    stocks = stocks + 1

                price = round(price, 2)

                cursor = db.cursor()
                cursor.execute(f"SELECT coins FROM currency WHERE user_id = {member.id} AND guild_id = {ctx.guild.id}")
                current_coins = cursor.fetchone()[0]
                if total_price > current_coins:
                    missing = total_price - current_coins
                    embed = discord.Embed(title="Company Error:", color=0xFF0000)
                    embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                    embed.add_field(name="You don't have enough coins to add that amount of shares:", value=f"Missing {missing} coins.")
                    await msg.edit(embed=embed, delete_after=5)
                    return

                embed = discord.Embed(title="Confirmation:", color=ctx.message.author.color)
                embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                embed.add_field(name=f"Are you sure you want to add {amount} shares?", value=f"New Price: {price} \n New Share Amount: {stocks}")
                msg = await ctx.send(embed=embed)
                await msg.add_reaction("✅")
                await msg.add_reaction("❌")
                reaction1, user1 = await self.bot.wait_for("reaction_add", check=lambda reaction, user: user == ctx.author)
                if str(reaction1.emoji) == "✅":
                    db.execute(f"UPDATE company SET stocks = {stocks} WHERE user_id = ? AND guild_id = ?", (member.id, ctx.guild.id))
                    db.execute(f"UPDATE company SET price = {price} WHERE user_id = ? AND guild_id = ?", (member.id, ctx.guild.id))
                    db.execute(f"UPDATE currency SET coins = coins - {total_price} WHERE user_id = ? AND guild_id = ?", (member.id, ctx.guild.id))
                    db.commit()
                    embed = discord.Embed(title="Shares Added: ", color=member.color)
                    embed.set_thumbnail(url=f'{ctx.author.avatar_url}')
                    embed.add_field(name="Amount: ", value=f"You added {amount} shares", inline=False)
                    embed.add_field(name="Price:", value=f"{price} coin(s)", inline=False)
                    embed.add_field(name="Shares:", value=f"{stocks}", inline=False)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="Cancelled:", color=0xFF0000)
                    embed.set_thumbnail(url=f"{ctx.message.author.avatar_url}")
                    embed.add_field(name=f"No shares added: ", value=f"Command cancelled.")

                    await msg.edit(embed=embed, delete_after=5)


def setup(bot):
    bot.add_cog(CurrencyCog(bot))
    print("Currency is loaded...")
