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
    async def load_error(self, ctx):
        if str(ctx.author.id) != "346941434202685442" and str(ctx.author.id) != "611635076769513507":
            return
        self.client.load_extension("cogs.error")

    @commands.command(pass_context=True)
    async def unload_error(self, ctx):
        if str(ctx.author.id) != "346941434202685442" and str(ctx.author.id) != "611635076769513507":
            return
        self.client.unload_extension("cogs.error")

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

        # auto score
        embed.add_field(
            name="auto score",
            value="{}".format(await Score.get_score(ctx, target)),
            inline=False,
        )

        # late score
        embed.add_field(
            name="late score",
            value="{}".format(await Score.get_score(ctx, target, True)),
            inline=False,
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
        args_second: str = ""
    ):
        guild = ctx.guild

        # update file
        with open("cogs/_guild.json", "r") as f:
            guilds = json.load(f)

        data_guild = guilds[str(guild.id)]
        data_ch = data_guild["chnl_notify"]
        data_late = data_guild["late_enable"]
        setup_complete = data_guild["setup_complete"]

        with open("cogs/_guild.json", "w") as f:
            json.dump(guilds, f)

        if not setup_complete:
            await Data.setup_notify(Data, message.channel)
            return

        channel = discord.utils.get(
            self.client.get_all_channels(), guild__name=guild.name, id=data_ch,
        )

        if command == "":
            embed_errr = discord.Embed(title="Error", description="", color=color_errr)
            embed_errr.add_field(
                name="Invalid argument",
                value="Available arguments: `-set_flag`, `-send_score_info`, `-sort_user`",
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
        elif command == "-send_score_info":
            await Score.send_score_info(Score, ctx.channel, target, True, False, True)
        elif command == "-sort_user":
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
                await Score.send_score_info(Score, ctx.channel, target, False, False, True)
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
        else:
            embed_errr = discord.Embed(title="Error", description="", color=color_errr)
            embed_errr.add_field(
                name="Invalid argument",
                value="Available arguments: `-set_flag`, `-send_score_info`, `-sort_user`",
                inline=False,
            )
            await ctx.send(embed=embed_errr)
            return 0


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

    @commands.command(pass_context=True)
    async def help(self, ctx, args_first: str = "", args_second: str = ""):
        if args_first == "" and args_second == "":
            embed_info = discord.Embed(
                title="Info", description="", color=color_done
            )
            embed_info.add_field(
                name="Available commands",
                value="Available arguments: `info`, `init`, `config`, `run`, `ban`",
                inline=False,
            )
            embed_info.add_field(
                name="To learn more about a command",
                value="Type in: `tao help -[command]`",
                inline=False,
            )
            await ctx.send(embed=embed_info)
        if args_first == "-info":
            embed_info = discord.Embed(
                title="tao info `<user>`", description="", color=color_done
            )
            embed_info.add_field(
                name="Description",
                value="Returns info about a specific user",
                inline=False,
            )
            embed_info.add_field(
                name="Arguments",
                value="<user>:`User`",
                inline=False,
            )
            await ctx.send(embed=embed_info)
        if args_first == "-init":
            if args_second == "":
                embed_info = discord.Embed(
                    title="tao init `[-reset]`", description="", color=color_done
                )
                embed_info.add_field(
                    name="Description",
                    value="Initializes permissions, roles and the database for the guild",
                    inline=False,
                )
                embed_info.add_field(
                    name="Arguments",
                    value="[-reset]",
                    inline=False,
                )
                embed_info.add_field(
                    name="To learn more about an argument",
                    value="Type in: `tao help -[command] -[argument]`",
                    inline=False,
                )
                await ctx.send(embed=embed_info)
            elif args_second == "-reset":
                embed_info = discord.Embed(
                    title="tao init -reset", description="", color=color_done
                )
                embed_info.add_field(
                    name="Description",
                    value="Resets current configuration and re-initializes Tao.",
                    inline=False,
                )
                await ctx.send(embed=embed_info)
            else:
                embed_errr = discord.Embed(
                    title="Error", description="", color=color_errr
                )
                embed_errr.add_field(
                    name="Invalid argument",
                    value="Available arguments: `reset`",
                    inline=False,
                )
                await ctx.send(embed=embed_errr)
        if args_first == "-config":
            if args_second == "":
                embed_info = discord.Embed(
                    title="tao config `<-config>` `<-enable/-disable>`", description="", color=color_done
                )
                embed_info.add_field(
                    name="Description",
                    value="Allows to edit Tao configuration",
                    inline=False,
                )
                embed_info.add_field(
                    name="Arguments",
                    value="`<-score> | <-verbose> | <-late>`, `<-enable> | <-disable>`",
                    inline=False,
                )
                embed_info.add_field(
                    name="To learn more about an argument",
                    value="Type in: `tao help -[command] -[argument]`",
                    inline=False,
                )
                await ctx.send(embed=embed_info)
            elif args_second == "-score":
                embed_info = discord.Embed(
                    title="tao init -score `<-enable/-disable>`", description="", color=color_done
                )
                embed_info.add_field(
                    name="Description",
                    value="Allows to enable or disable the score system",
                    inline=False,
                )
                embed_info.add_field(
                    name="Arguments",
                    value="`<-enable> | <-disable>`",
                    inline=False,
                )
                await ctx.send(embed=embed_info)
            elif args_second == "-verbose":
                embed_info = discord.Embed(
                    title="tao init -verbose `<-enable/-disable>`", description="", color=color_done
                )
                embed_info.add_field(
                    name="Description",
                    value="Sends debug or detailed information in notifications",
                    inline=False,
                )
                embed_info.add_field(
                    name="Arguments",
                    value="`<-enable> | <-disable>`",
                    inline=False,
                )
                await ctx.send(embed=embed_info)
            elif args_second == "-late":
                embed_info = discord.Embed(
                    title="tao init -late `<-enable/-disable>`", description="", color=color_done
                )
                embed_info.add_field(
                    name="Description",
                    value="Allows to enable or disable whether the users will get sorted after they've joined the server",
                    inline=False,
                )
                embed_info.add_field(
                    name="Arguments",
                    value="`<-enable> | <-disable>`",
                    inline=False,
                )
                await ctx.send(embed=embed_info)
            else:
                embed_errr = discord.Embed(
                    title="Error", description="", color=color_errr
                )
                embed_errr.add_field(
                    name="Invalid argument",
                    value="Available arguments: `score`, `verbose`, `late`",
                    inline=False,
                )
                await ctx.send(embed=embed_errr)
        if args_first == "-run":
            if args_second == "":
                embed_info = discord.Embed(
                    title="tao run `<-action>` `<argument>`", description="", color=color_done
                )
                embed_info.add_field(
                    name="Description",
                    value="Runs an internal function",
                    inline=False,
                )
                embed_info.add_field(
                    name="Arguments",
                    value="`<-sort_user> | <-send_score_info> | <-set_flag>`, `<custom>`",
                    inline=False,
                )
                embed_info.add_field(
                    name="To learn more about an argument",
                    value="Type in: `tao help -[command] -[argument]`",
                    inline=False,
                )
                await ctx.send(embed=embed_info)
            elif args_second == "-sort_user":
                embed_info = discord.Embed(
                    title="tao run -sort_user `<user>`", description="", color=color_done
                )
                embed_info.add_field(
                    name="Description",
                    value="Simulates the sorting function that runs when a user joins",
                    inline=False,
                )
                embed_info.add_field(
                    name="Arguments",
                    value="<user>:`User`",
                    inline=False,
                )
                await ctx.send(embed=embed_info)
            elif args_second == "-send_score_info":
                embed_info = discord.Embed(
                    title="tao run -send_score_info `<user>`", description="", color=color_done
                )
                embed_info.add_field(
                    name="Description",
                    value="Sends score of a user",
                    inline=False,
                )
                embed_info.add_field(
                    name="Arguments",
                    value="<user>:`User`",
                    inline=False,
                )
                await ctx.send(embed=embed_info)
            elif args_second == "-set_flag":
                embed_info = discord.Embed(
                    title="tao run -set_flag `<custom>`", description="", color=color_done
                )
                embed_info.add_field(
                    name="Description",
                    value="Simulates flagging action on a user",
                    inline=False,
                )
                embed_info.add_field(
                    name="Arguments",
                    value="`<0> | <1> | <2> | <3>`",
                    inline=False,
                )
                embed_info.add_field(
                    name="Flag enum `0`",
                    value="Send warning notification",
                    inline=False,
                )
                embed_info.add_field(
                    name="Flag enum `1`",
                    value="Send user to manual approval",
                    inline=True,
                )
                embed_info.add_field(
                    name="Flag enum `2`",
                    value="Ban user",
                    inline=False,
                )
                embed_info.add_field(
                    name="Flag enum `3`",
                    value="Flag user as a valid account (clear other flags)",
                    inline=True,
                )
                await ctx.send(embed=embed_info)
            else:
                embed_errr = discord.Embed(
                    title="Error", description="", color=color_errr
                )
                embed_errr.add_field(
                    name="Invalid argument",
                    value="Available arguments: `sort_user`, `send_score_info`, `set_flag`",
                    inline=False,
                )
                await ctx.send(embed=embed_errr)
        if args_first == "-ban":
            if args_second == "":
                embed_info = discord.Embed(
                    title="tao ban `<user>` `[duration]` `[reason]`", description="", color=color_done
                )
                embed_info.add_field(
                    name="Description",
                    value="Bans a user (permanently if no duration specified)",
                    inline=False,
                )
                embed_info.add_field(
                    name="Arguments",
                    value="<user>:`User`, [duration]:`Time`, [reason]:`str`",
                    inline=False,
                )
                embed_info.add_field(
                    name="To learn more about an argument",
                    value="Type in: `tao help -[command] -[argument]`",
                    inline=False,
                )
                await ctx.send(embed=embed_info)
            elif args_second == "-duration":
                embed_info = discord.Embed(
                    title="tao ban `<user>` -duration", description="", color=color_done
                )
                embed_info.add_field(
                    name="Description",
                    value="Specifies ban duration",
                    inline=False,
                )
                embed_info.add_field(
                    name="Ban time `m / minute` | -Xm / -Xminute",
                    value="Time in minutes",
                    inline=False,
                )
                embed_info.add_field(
                    name="Ban time `h / hour` | -Xh / -Xhour",
                    value="Time in hours",
                    inline=False,
                )
                embed_info.add_field(
                    name="Ban time `d / day` | -Xd / -Xday",
                    value="Time in days",
                    inline=False,
                )
                embed_info.add_field(
                    name="Ban time `w / week` | -Xw / -Xweek",
                    value="Time in weeks",
                    inline=False,
                )
                await ctx.send(embed=embed_info)
            elif args_second == "-reason":
                embed_info = discord.Embed(
                    title="tao ban `<user>` `[duration]` 'reason'", description="", color=color_done
                )
                embed_info.add_field(
                    name="Description",
                    value="Ban reason (takes place of duration if duration is not specified)",
                    inline=False,
                )
                await ctx.send(embed=embed_info)
            else:
                embed_errr = discord.Embed(
                    title="Error", description="", color=color_errr
                )
                embed_errr.add_field(
                    name="Invalid argument",
                    value="Available arguments: `reset`",
                    inline=False,
                )
                await ctx.send(embed=embed_errr)


def setup(client):
    client.add_cog(Misc(client))
