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

    async def get_age_account(self, target: discord.Member = None):
        # return account age
        get_today = datetime.now()
        get_created = target.created_at

        return (get_today - get_created).days

    async def get_age_guild(self, target: discord.Member = None):
        # return server age
        get_today = datetime.now()
        get_joined = target.joined_at

        return (get_today - get_joined).days

    async def get_date_diff(self, target: discord.Member = None):
        get_create_days = await self.get_age_account(self, target)
        get_joined_days = await self.get_age_guild(self, target)

        diff = get_create_days - get_joined_days

        return diff

    async def get_avatar(self, target: discord.Member = None):

        avatar_url = target.avatar_url
        default_url = "https://cdn.discordapp.com/embed/avatars"

        # check if custom avatar is set
        if str(avatar_url).find(default_url) != -1:
            return False
        else:
            return True

    async def get_is_on_mobile(self, target: discord.Member = None):
        return target.is_on_mobile()

    async def get_premium(self, target: discord.Member = None):
        # bot accounts cannot use the profile function
        # so look for popular discriminators and animated avatars
        discriminator = target.discriminator
        animated = target.is_avatar_animated()

        discrim_list = [
            "0001",
            "0002",
            "0003",
            "0004",
            "0005",
            "0006",
            "0007",
            "0008",
            "0009",
            "1337",
            "1234",
            "4321",
            "0666",
            "6660",
            "1000",
            "2000",
            "3000",
            "4000",
            "5000",
            "6000",
            "7000",
        ]

        if any(discriminator in s for s in discrim_list):
            return True
        if animated:
            return True
        else:
            return False

    """
    async def get_hypesquad(self, target: discord.Member = None):
        flags = target.public_flags.all()
        bravery = flags.hypesquad_bravery
        brilliance = flags.hypesquad_brilliance
        balance = flags.hypesquad_balance

        if bravery or brilliance or balance:
            return True
        else: return False
    """

    async def get_score(self, target: discord.Member = None, late: bool = False):
        score = 0

        # 1:
        # if the user has an avatar
        avatar = await self.get_avatar(self, target)
        if avatar:
            score += 0.250
        else:
            score += 0.000

        # 2:
        # account created - server joined
        if late:
            diff = await self.get_date_diff(self, target)
            diff_clamped = max(min(diff, 100), 0)
            score += diff_clamped / 100

        # 3:
        # account age
        age = await self.get_age_account(self, target)
        age_clamped = max(min(age, 100), 0)
        score += age_clamped / 100

        # 4:
        # is the user on mobile
        mobile = await self.get_is_on_mobile(self, target)
        if mobile:
            score += 0.250
        else:
            score += 0.000

        # 5:
        # does the user have nitro
        premium = await self.get_premium(self, target)
        if premium:
            score += 1.0
        else:
            score += 0.0

        # 6:
        # is the user member of hypesquad
        # hypesquad = await self.get_hypesquad(self, target)
        # if hypesquad:
        #    score += 0.5
        # else:
        #    score += 0.0

        # normalize total score
        if late:
            score = max(min(score / 2.5, 1), 0)
        else:
            score = max(min(score / 1.5, 1), 0)

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
        manual: bool = False
    ):
        guild = channel.guild

        # update file
        with open(data_file, "r") as f:
            guilds = json.load(f)

        approve_id = guilds[str(guild.id)]["role_approve"]
        member_id = guilds[str(guild.id)]["role_member"]
        verbose = guilds[str(guild.id)]["verbose_enable"]
        late = guilds[str(guild.id)]["late_enable"]

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
            if member_role is not everyone_role:
                await target.add_roles(member_role)
        if flag_type == 0:
            string = "Potential suspicious user"
            color = color_done
        elif flag_type == 1:
            string = "Sent to manual approval"
            color = color_warn
            await target.add_roles(approve_role)

            if member_role != everyone_role:
                await target.remove_roles(member_role)

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

            embed1 = discord.Embed(
                title="You have been banned", description="", color=color
            )
            embed1.add_field(
                name="You have been detected as an alt account",
                value="If wrong, contact a staff member",
                inline=False,
            )
            embed1.add_field(name="User score", value=str(score_val), inline=False)
            try:
                await target.send(embed=embed1)
            except:
                pass

            await target.ban(reason="tao: Alt account")

        if flag_type != -1:
            embed = discord.Embed(title="User flagged", description="", color=color)
            embed.add_field(
                name=string,
                value=target.name
                + "#"
                + target.discriminator
                + " | id: "
                + str(target.id),
                inline=False,
            )
            embed.add_field(name="User score", value=str(score_val), inline=False)
            await channel.send(embed=embed)
            if verbose and not late:
                await self.send_score_info(self, channel, target, manual)

    async def sort_user_auto(
        self, channel: discord.channel.TextChannel, target: discord.Member = None, late = False, manual: bool = False
    ):
        score_val = await self.get_score(self, target, late)

        if score_val >= 0.5:
            # flag user
            await self.flag_member(self, -1, score_val, channel, target, manual)
        elif score_val < 0.5 and score_val >= 0.3:
            # flag user
            await self.flag_member(self, 0, score_val, channel, target, manual)
        elif score_val < 0.3 and score_val >= 0.1:
            # add to the manual check queue
            await self.flag_member(self, 1, score_val, channel, target, manual)
        elif score_val < 0.1 and score_val >= 0.0:
            # ban user
            await self.flag_member(self, 2, score_val, channel, target, manual)

    async def send_score_info(self, channel: discord.TextChannel, target, manual=False, late=False, run=False):
        scr_val = await self.get_score(self, target, late)
        acc_val = await self.get_age_account(self, target)
        gld_val = await self.get_age_guild(self, target)
        avt_val = await self.get_avatar(self, target)
        mbl_val = await self.get_is_on_mobile(self, target)
        # hsq_val = await self.get_hypesquad(self, target)
        ntr_val = await self.get_premium(self, target)
        if scr_val < 0.5 and not run:
            embed_info = discord.Embed(
                title="Info | " + target.name + "#" + target.discriminator,
                description="",
                color=color_done,
            )
            embed_info.add_field(
                name="User score:", value=str(scr_val), inline=True,
            )
            age = await self.get_age_account(self, target)
            age_clamped = max(min(age, 100), 0)
            embed_info.add_field(
                name="Account age:",
                value=str(acc_val) + " : +" + str(age_clamped / 100),
                inline=True,
            )
            if late:
                diff = await self.get_date_diff(self, target)
                diff_clamped = max(min(diff, 100), 0)
                embed_info.add_field(
                    name="Join age:",
                    value=str(gld_val) + " : +" + str(diff_clamped / 100),
                    inline=True,
                )
            avt = 0
            if avt_val:
                avt = 0.250
            else:
                avt = 0
            embed_info.add_field(
                name="Custom avatar:", value=str(avt_val) + " : +" + str(avt), inline=True,
            )
            mbl = 0
            if mbl_val:
                mbl = 0.250
            else:
                mbl = 0
            embed_info.add_field(
                name="On mobile:", value=str(mbl_val) + " : +" + str(mbl), inline=True,
            )
            ntr = 0
            if ntr_val:
                ntr = 0.5
            else:
                ntr = 0
            embed_info.add_field(
                name="Nitro:", value=str(ntr_val) + " : +" + str(ntr), inline=True,
            )
            if manual:
                embed_info.add_field(
                    name="Manual sorting", value="User manually sorted", inline=True,
                )
            elif late:
                embed_info.add_field(
                    name="Late sorting", value="User manually sorted", inline=True,
                )
            else:
                embed_info.add_field(
                    name="Auto sorting", value="User automatically sorted", inline=True,
                )
            await channel.send(embed=embed_info)
        elif run:
            embed_info = discord.Embed(
                title="Info | " + target.name + "#" + target.discriminator,
                description="",
                color=color_done,
            )
            embed_info.add_field(
                name="User score:", value=str(scr_val), inline=True,
            )
            age = await self.get_age_account(self, target)
            age_clamped = max(min(age, 100), 0)
            embed_info.add_field(
                name="Account age:",
                value=str(acc_val) + " : +" + str(age_clamped / 100),
                inline=True,
            )
            if late:
                diff = await self.get_date_diff(self, target)
                diff_clamped = max(min(diff, 100), 0)
                embed_info.add_field(
                    name="Join age:",
                    value=str(gld_val) + " : +" + str(diff_clamped / 100),
                    inline=True,
                )
            avt = 0
            if avt_val:
                avt = 0.250
            else:
                avt = 0
            embed_info.add_field(
                name="Custom avatar:", value=str(avt_val) + " : +" + str(avt), inline=True,
            )
            mbl = 0
            if mbl_val:
                mbl = 0.250
            else:
                mbl = 0
            embed_info.add_field(
                name="On mobile:", value=str(mbl_val) + " : +" + str(mbl), inline=True,
            )
            ntr = 0
            if ntr_val:
                ntr = 0.5
            else:
                ntr = 0
            embed_info.add_field(
                name="Nitro:", value=str(ntr_val) + " : +" + str(ntr), inline=True,
            )
            if manual:
                embed_info.add_field(
                    name="Manual sorting", value="User manually sorted", inline=True,
                )
            elif late:
                embed_info.add_field(
                    name="Late sorting", value="User manually sorted", inline=True,
                )
            else:
                embed_info.add_field(
                    name="Auto sorting", value="User automatically sorted", inline=True,
                )
            await channel.send(embed=embed_info)


def setup(client):
    client.add_cog(Score(client))
