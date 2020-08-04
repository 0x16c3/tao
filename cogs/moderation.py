import os
import discord
import json
from discord.ext import commands
from datetime import datetime, timedelta

from .data import Data
from .utils import *

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client


    @commands.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.User, args_first: str = "", args_second: str = ""):
        if args_first == "" or not args_first.startswith('-'): #permanent
            member_obj = await ctx.guild.fetch_member(member.id)
            await member_obj.ban(reason=args_first)
            # create embed
            embed = discord.Embed(title="Info", description="", color=color_done)
            embed.add_field(
                name="Member banned",
                value=target.name + "#" + target.discriminator + " has been banned `permanently`",
                inline=False,
            )
            await ctx.send(embed=embed)
        else:
            time_str = args_first[1:]
            duration = 0
            duration_str = ""

            if args_first[-1] == "m" or args_first[-1] == "minute":
                duration = int(time_str[:-1]) * 60
                if int(time_str[:-1]) == 1:
                    duration_str = "`a minute`"
                else:
                    duration_str = "`" + time_str[:-1] + " minutes`"
            if args_first[-1] == "h" or args_first[-1] == "hour":
                duration = int(time_str[:-1]) * 60 * 60
                if int(time_str[:-1]) == 1:
                    duration_str = "`an hour`"
                else:
                    duration_str = "`" + time_str[:-1] + " hours`"
            if args_first[-1] == "d" or args_first[-1] == "day":
                duration = int(time_str[:-1]) * 60 * 60 * 24
                if int(time_str[:-1]) == 1:
                    duration_str = "`a day`"
                else:
                    duration_str = "`" + time_str[:-1] + " days`"
            if args_first[-1] == "w" or args_first[-1] == "week":
                duration = int(time_str[:-1]) * 60 * 60 * 24 * 7
                if int(time_str[:-1]) == 1:
                    duration_str = "`a week`"
                else:
                    duration_str = "`" + time_str[:-1] + " weeks`"
            elif not args_first[-1] == "w" or args_first[-1] == "week" and args_first[-1] == "d" or args_first[-1] == "day" and args_first[-1] == "h" or args_first[-1] == "hour" and args_first[-1] == "m" or args_first[-1] == "minute":
                embed_errr = discord.Embed(title="Error", description="", color=color_errr)
                embed_errr.add_field(
                    name="Invalid argument",
                    value="Available arguments: `m:minute`, `h:hour`, `d:day`, `w:week`",
                    inline=False,
                )
                await ctx.send(embed=embed_errr)

            with open("cogs/_guild.json", "r") as f:
                guilds = json.load(f)

            await Data.update_banned_member(Data, guilds, ctx.guild, member, duration)

            with open("cogs/_guild.json", "w") as f:
                json.dump(guilds, f)

            # update file
            with open("cogs/_user.json", "r") as f:
                members = json.load(f)

            embed = discord.Embed(
                title="You have been banned!", description="", color=color_errr
            )
            embed.add_field(
                name="You have been banned from `" + ctx.guild.name + "`",
                value="You have been banned for " + duration_str,
                inline=False,
            )
            if args_second != "":
                embed.add_field(
                    name="Reason",
                    value="`" + args_second + "`",
                    inline=False,
                )
            try:
                await member.send(embed=embed)
            except:
                pass

            member_obj = await ctx.guild.fetch_member(member.id)
            await member_obj.ban(reason=args_second)
            # create embed
            embed = discord.Embed(title="Info", description="", color=color_done)
            embed.add_field(
                name="Member banned",
                value=member.name + "#" + member.discriminator + " has been banned for " + duration_str,
                inline=False,
            )
            await ctx.send(embed=embed)

        with open("cogs/_user.json", "w") as f:
            json.dump(members, f)

def setup(client):
    client.add_cog(Moderation(client))
