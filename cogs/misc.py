import discord
import json
from discord.ext import commands
from datetime import datetime, timedelta

from .data import Data
from .score import Score
from .utils import *


class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(pass_context=True)
    @commands.has_permissions(ban_members=True)
    async def info(self, ctx, target: discord.Member = None):
        # embed target information
        if not target:
            target = ctx.author

        # title
        embed = discord.Embed(
            title="{}".format(target.name), description="", color=color_main
        )

        # author
        embed.set_author(name=target, icon_url=target.avatar_url)

        # avatar thumbnail
        embed.set_thumbnail(url=target.avatar_url)

        ##########################################

        # ID
        embed.add_field(name="ID", value=target.id, inline=False)

        # username
        embed.add_field(name="username", value=target, inline=True)

        # age
        current_date = datetime.now()

        user_created = target.created_at
        user_created_str = user_created.strftime("%y/%m/%d")
        embed.add_field(
            name="created", value="{}".format(user_created_str), inline=True
        )

        user_join = target.joined_at
        user_join_str = user_join.strftime("%y/%m/%d")
        embed.add_field(name="joined", value="{}".format(user_join_str), inline=True)

        embed.add_field(name="top role", value=target.top_role, inline=True)

        # account age
        embed.add_field(
            name="account age",
            value="{}".format(await Score.get_age_account(ctx, target)),
            inline=True,
        )

        # guild age
        embed.add_field(
            name="guild age",
            value="{}".format(await Score.get_age_guild(ctx, target)),
            inline=True,
        )

        ##########################################

        # footer
        embed.set_footer(text="requested by {}".format(ctx.author))

        await ctx.send(embed=embed)

    @commands.command(pass_context=False)
    @commands.has_permissions(administrator=True)
    async def run(
        self,
        ctx,
        command: str = "",
        target: discord.Member = None,
        args_first: str = "",
    ):
        guild = ctx.guild

        # update file
        with open("cogs/_guild.json", "r") as f:
            guilds = json.load(f)

        data_guild = guilds[str(guild.id)]
        data_ch = data_guild["chnl_notify"]
        data_late = data_guild["late_enable"]

        with open("cogs/_guild.json", "w") as f:
            json.dump(guilds, f)

        channel = discord.utils.get(
            self.client.get_all_channels(), guild__name=guild.name, id=data_ch,
        )

        if command == "":
            embed_errr = discord.Embed(title="Error", description="", color=color_errr)
            embed_errr.add_field(
                name="Invalid argument",
                value="Available arguments: `-set_flag`, `-get_score`, `-sort`",
                inline=False,
            )
            await ctx.send(embed=embed_errr)
            return 0
        elif command == "-set_flag":
            if target is None:
                embed_errr = discord.Embed(
                    title="Error", description="", color=color_errr
                )
                embed_errr.add_field(
                    name="Invalid argument",
                    value="`target` cannot be `None`",
                    inline=False,
                )
                await ctx.send(embed=embed_errr)
                return 1
            if args_first == "":
                embed_errr = discord.Embed(
                    title="Error", description="", color=color_errr
                )
                embed_errr.add_field(
                    name="Invalid argument",
                    value="Available arguments: `-0`, `-1`, `-2`, `-3`",
                    inline=False,
                )
                await ctx.send(embed=embed_errr)
                return 2
            if args_first == "-0":  # notify
                await Score.flag_member(Score, 0, 0.30, channel, target)
            elif args_first == "-1":  # approval
                await Score.flag_member(Score, 1, 0.15, channel, target)
            elif args_first == "-2":  # ban
                await Score.flag_member(Score, 2, 0.05, channel, target)
            elif args_first == "-3":  # valid
                await Score.flag_member(Score, -1, 1.0, channel, target)
        elif command == "-get_score":
            await Score.send_score_info(Score, ctx.channel, target, data_late)
        elif command == "-sort":
            if target is None:
                embed_errr = discord.Embed(
                    title="Error", description="", color=color_errr
                )
                embed_errr.add_field(
                    name="Invalid argument",
                    value="`target` cannot be `None`",
                    inline=False,
                )
                await ctx.send(embed=embed_errr)
                return 1
            else:
                await Score.sort_user_auto(Score, channel, target, False, True)
                await Score.send_score_info(Score, ctx.channel, target, True)
        elif command == "-leave":
            embed_errr = discord.Embed(
                    title="Bye!", description="", color=color_errr
                )
            embed_errr.add_field(
                name="Leave",
                value="Make sure to write your issues on the github repository.",
                inline=False,
            )
            embed_errr.add_field(name="GitHub", value = "https://github.com/0x16c3/tao", inline=False)
            await ctx.send(embed=embed_errr)
            await guild.leave()
    @commands.command(pass_context=True)
    @commands.has_permissions(administrator=True)
    async def config(self, ctx, cfg: str = "", args: str = ""):
        guild = ctx.guild

        if cfg == "":
            embed_errr = discord.Embed(title="Error", description="", color=color_errr)
            embed_errr.add_field(
                name="Invalid argument",
                value="Available arguments: `-score`, `-verbose`, `-late`",
                inline=False,
            )
            await ctx.send(embed=embed_errr)
            return

        # update file
        with open(data_file, "r") as f:
            guilds = json.load(f)

        await Data.update_data(Data, guilds, guild)
        state_scre = guilds[str(guild.id)]["scre_enable"]
        state_vrbs = guilds[str(guild.id)]["verbose_enable"]
        state_late = guilds[str(guild.id)]["late_enable"]

        with open(data_file, "w") as f:
            json.dump(guilds, f)

        if cfg == "-score":
            await Data.set_config(Data, ctx, cfg, args, state_scre)
        if cfg == "-verbose":
            await Data.set_config(Data, ctx, cfg, args, state_vrbs)
        if cfg == "-late":
            await Data.set_config(Data, ctx, cfg, args, state_late)


def setup(client):
    client.add_cog(Misc(client))
