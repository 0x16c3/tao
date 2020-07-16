import os
import discord
import json
from discord.ext import commands
from datetime import datetime, timedelta

from .data import Data
from .utils import *


class Score(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def get_age_account(self, target: discord.Member = None):
        # return account age
        get_today = datetime.now()
        get_created = target.created_at

        return (get_today - get_created).days

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def get_age_guild(self, target: discord.Member = None):
        # return server age
        get_today = datetime.now()
        get_joined = target.joined_at

        return (get_today - get_joined).days

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def get_date_diff(self, target: discord.Member = None):
        get_create_days = await self.get_age_account(self, target)
        get_joined_days = await self.get_age_guild(self, target)

        diff = get_create_days - get_joined_days

        return diff

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def get_avatar(self, target: discord.Member = None):

        avatar_url = target.avatar_url
        default_url = "https://cdn.discordapp.com/embed/avatars"

        # check if custom avatar is set
        if str(avatar_url).find(default_url) != -1:
            return False
        else:
            return True

    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def get_score(self, target: discord.Member = None):
        score = 0

        #  1:
        # if the user has an avatar
        avatar = await self.get_avatar(self, target)
        if avatar:
            score += 1.0
        else:
            score += 0.0

        # 2:
        # account created - server joined
        diff = await self.get_date_diff(self, target)
        diff_clamped = max(min(diff, 100), 0)
        score += diff_clamped / 100

        # 3:
        # account age
        age = await self.get_age_account(self, target)
        age_clamped = max(min(age, 100), 0)
        score += age_clamped / 100

        # normalize total score
        score = score / 3

        # don't flag bots
        if target.bot:
            score = 1.0

        return score

    async def flag_member(
        self,
        flag_type: int,
        score_val: int,
        channel: discord.channel.TextChannel,
        target: discord.Member = None,
    ):
        guild = channel.guild

        # update file
        with open(data_file, "r") as f:
            guilds = json.load(f)

        approve_id = guilds[str(guild.id)]["role_approve"]
        member_id = guilds[str(guild.id)]["role_member"]

        with open(data_file, "w") as f:
            json.dump(guilds, f)

        everyone_role = guild.default_role
        approve_role = discord.utils.get(guild.roles, id=approve_id)
        member_role = discord.utils.get(guild.roles, id=member_id)

        string = ""
        color = color_main

        if not flag_type:
            flag_type = 0
        if flag_type == -1:
            await target.add_roles(member_role, "tao: Approved account")
        if flag_type == 0:
            string = "Suspicious user"
            color = color_done
        elif flag_type == 1:
            string = "Sent to manual approval"
            color = color_warn
            await target.add_roles(approve_role, "tao: Suspicious account")

            if member_role != everyone_role:
                await target.remove_roles(member_role, "tao: Suspicious account")

            embed = discord.Embed(
                title="You have been flagged", description="", color=color
            )
            embed.add_field(
                name="You have been flagged as a suspicious user",
                value="Please cooperate with the admins while the approve you",
                inline=False,
            )
            embed.add_field(name="User score", value=str(score_val), inline=False)
            try:
                await target.send(embed=embed)
            except:
                pass
        elif flag_type == 2:
            string = "Banned user"
            color = color_errr

            embed = discord.Embed(
                title="You have been banned", description="", color=color
            )
            embed.add_field(
                name="You have been detected as an alt account",
                value="If wrong, contact a staff member",
                inline=False,
            )
            embed.add_field(name="User score", value=str(score_val), inline=False)
            try:
                await target.send(embed=embed)
            except:
                pass

            await target.ban(reason="tao: Alt account")

        embed = discord.Embed(title="User flagged", description="", color=color)
        embed.add_field(
            name=string,
            value=target.mention + " | id: " + str(target.id),
            inline=False,
        )
        embed.add_field(name="User score", value=str(score_val), inline=False)
        await channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sort_user_auto(
        self, channel: discord.channel.TextChannel, target: discord.Member = None
    ):
        score_val = await self.get_score(self, target)

        if score_val >= 0.5:
            # flag user
            await self.flag_member(-1, score_val, channel, target)
        elif score_val < 0.5 and score_val >= 0.2:
            # flag user
            await self.flag_member(0, score_val, channel, target)
        elif score_val < 0.2 and score_val >= 0.1:
            # add to the manual check queue
            await self.flag_member(1, score_val, channel, target)
        elif score_val < 0.1 and score_val >= 0.0:
            # ban user
            await self.flag_member(self, 2, score_val, channel, target)


def setup(client):
    client.add_cog(Score(client))