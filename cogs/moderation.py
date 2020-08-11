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
    async def ban(self, ctx, member: str, args_first: str = "", *args_second):

        var_type = "None"
        member_array = member.split(";")

        for member_i in member_array:

            member_obj = await get_member(member_i, ctx.guild, ctx.channel)

            if type(member_obj) == str:
                if "FAIL_NOTFOUND" in member_obj:
                    member_obj = await self.client.fetch_user(int(member_obj[:-14]))        
            if member_obj is None:
                return           

            if args_first == "" or not args_first.startswith("-"):  # permanent

                await ctx.guild.ban(member_obj, reason=" ".join(map(str, args_second)))

                # create embed
                embed = discord.Embed(title="Info", description="", color=color_done)
                embed.add_field(
                    name="Member banned",
                    value=member_obj.name
                    + "#"
                    + member_obj.discriminator
                    + " has been banned `permanently`",
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
                if (
                    not (time_str[-1] == "w" or time_str[-1] == "week")
                    and not (time_str[-1] == "d" or time_str[-1] == "day")
                    and not (time_str[-1] == "h" or time_str[-1] == "hour")
                    and not (time_str[-1] == "m" or time_str[-1] == "minute")
                ):
                    embed_errr = discord.Embed(
                        title="Error", description="", color=color_errr
                    )
                    embed_errr.add_field(
                        name="Invalid argument",
                        value="Available arguments: `m:minute`, `h:hour`, `d:day`, `w:week`",
                        inline=False,
                    )
                    await ctx.send(embed=embed_errr)
                    return

                guilds = json_load(data_guild)

                await Data.update_banned_member(
                    Data, guilds, ctx.guild, member_obj, duration
                )

                json_save(guilds, data_guild)

                # update file
                members = json_load(data_users)

                embed = discord.Embed(
                    title="You have been banned!", description="", color=color_errr
                )
                embed.add_field(
                    name="You have been banned from `" + ctx.guild.name + "`",
                    value="You have been banned for " + duration_str,
                    inline=False,
                )
                if args_second != None:
                    embed.add_field(
                        name="Reason",
                        value="`" + " ".join(map(str, args_second)) + "`",
                        inline=False,
                    )
                try:
                    await member_obj.send(embed=embed)
                except:
                    pass

                await ctx.guild.ban(member_obj, reason=" ".join(map(str, args_second)))
                # create embed
                embed = discord.Embed(title="Info", description="", color=color_done)
                embed.add_field(
                    name="Member banned",
                    value=member_obj.name
                    + "#"
                    + member_obj.discriminator
                    + " has been banned for "
                    + duration_str,
                    inline=False,
                )
                await ctx.send(embed=embed)

                json_save(members, data_users)


def setup(client):
    client.add_cog(Moderation(client))
