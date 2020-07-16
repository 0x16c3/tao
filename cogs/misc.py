import discord
from discord.ext import commands
from datetime import datetime, timedelta

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

        # basic info
        embed.add_field(name="username", value=target, inline=True)
        embed.add_field(name="ID", value=target.id, inline=True)

        embed.add_field(name="—", value="—", inline=False)

        embed.add_field(name="status", value=target.status, inline=True)
        embed.add_field(name="top role", value=target.top_role, inline=True)

        embed.add_field(name="—", value="—", inline=False)

        # age
        current_date = datetime.now()

        user_created = target.created_at
        user_created_str = user_created.strftime("%B %d, %Y %I:%M %p")
        embed.add_field(
            name="created", value="{}".format(user_created_str), inline=True
        )

        user_join = target.joined_at
        user_join_str = user_join.strftime("%B %d, %Y %I:%M %p")
        embed.add_field(name="joined", value="{}".format(user_join_str), inline=True)

        embed.add_field(name="—", value="—", inline=False)

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

        # footer
        embed.set_footer(text="requested by {}".format(ctx.author))

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Misc(client))
