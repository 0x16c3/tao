import os
import discord
import json
from discord.ext import commands
from datetime import datetime, timedelta, date
import asyncio

import os.path
from os import path

from cogs.moderation import Moderation
from cogs.score import Score
from cogs.data import Data
from cogs.utils import *

# initialize
TOKEN = open("tmp/token.txt", "r").read()

cogs = [
    "cogs.score",
    "cogs.data",
    "cogs.misc",
    "cogs.moderation",
    "cogs.eval",
    "cogs.error",
]

client = commands.Bot(
    command_prefix="tao ",
    status=discord.Status.idle,
    activity=discord.Game(name="initializing"),
)
client.remove_command("help")


@client.event
async def on_ready():
    print("{0.user}".format(client))
    guild_count = len(list(client.guilds))
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(list(client.guilds))} guilds",
        ),
    )

    if not path.exists(data_guild):
        f = open(data_guild, "w")
        f.write("{" + "}")
        f.close()
    if not path.exists(data_users):
        f = open(data_users, "w")
        f.write("{" + "}")
        f.close()


@client.event
async def on_guild_join(guild):
    # update file
    guilds = json_load(data_guild)

    await Data.update_data(Data, guilds, guild)

    json_save(guilds, data_guild)

    guild_count = len(list(client.guilds))
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(list(client.guilds))} guilds",
        ),
        fetch_offline_members=True,
    )


@client.event
async def on_member_join(member):
    # update file
    guilds = json_load(data_guild)

    alias = guilds[str(member.guild.id)]
    data_ch = alias["chnl_notify"]
    data_state = alias["scre_enable"]
    data_state_late = alias["late_enable"]

    json_save(guilds, data_guild)

    channel = client.get_channel(data_ch)

    if data_state == True:
        await Score.sort_user_auto(Score, channel, member, False, False)


@client.event
async def on_message(message):
    # embed meta
    embed = discord.Embed(color=0xF5F5F5)

    source = "https://github.com/0x16c3/tao"
    avatar = client.user.avatar_url

    if message.content == "tao":
        embed.set_author(name="Tao", url=source, icon_url=avatar)
        embed.set_thumbnail(url=avatar)

        embed.add_field(name="source", value=source, inline=False)
        embed.set_footer(text="道")

        await message.channel.send(embed=embed)
    else:
        if not message.author.bot and isinstance(
            message.channel, discord.channel.TextChannel
        ):
            # update file
            members = json_load(data_users)

            await Data.update_data_user(Data, members, message.author)
            checked = members[str(message.author.id)]["checked"]

            json_save(members, data_users)

            # update file
            guilds = json_load(data_guild)

            await Data.update_data(Data, guilds, message.guild)
            late = await Data.get_state_config(
                Data, guilds, message.guild, "late_enable"
            )
            channel = guilds[str(message.guild.id)]["chnl_notify"]
            verbose = guilds[str(message.guild.id)]["verbose_enable"]
            setup_complete = guilds[str(message.guild.id)]["setup_complete"]

            # get existing channel
            channel_notify = discord.utils.get(
                client.get_all_channels(), guild__name=message.guild.name, id=channel,
            )

            json_save(guilds, data_guild)

            if not setup_complete and message.content != "tao init":
                try:
                    await Data.setup_notify(Data, message.channel)
                except:
                    pass

            if message.content == "tao init":
                # update file
                guilds = json_load(data_guild)

                guilds[str(message.guild.id)]["notified"] = True

                json_save(guilds, data_guild)

            if late and not checked:

                await Score.sort_user_auto(Score, channel_notify, message.author, True)

                # update file
                members = json_load(data_users)

                await Data.update_data_user(Data, members, message.author)
                await Data.update_state_user(
                    Data, members, message.author, "checked", True
                )

                json_save(members, data_users)

    await client.process_commands(message)


if __name__ == "__main__":
    for extension in cogs:
        try:
            client.load_extension(extension)
        except Exception as error:
            print(f"{extension} could not be activated. [{error}]")
    try:
        client.load_extension("cogs.topgg")
    except:
        pass


async def timer_secd():

    await client.wait_until_ready()

    while client.is_ready():
        await asyncio.sleep(1)

        guilds = json_load(data_guild)

        for guild_i in guilds:
            guild = client.get_guild(int(guild_i))

            if guild:

                await Data.update_data(Data, guilds, guild)
                json_save(guilds, data_guild)

                guilds = json_load(data_guild)

                member_list = guilds[guild_i]["banned_members"]

                for member_i in member_list:
                    member = await client.fetch_user(int(member_i))

                    await Data.update_ban_timer(Data, guilds, guild, member)
                    curtime = await Data.get_ban_timer(Data, guilds, guild, member)

                    json_save(guilds, data_guild)

                    if curtime <= 0:
                        guilds = json_load(data_guild)

                        try:
                            await guild.unban(member)

                            embed = discord.Embed(
                                title="Info", description="", color=color_errr
                            )
                            embed.add_field(
                                name="You have been unbanned!",
                                value="Your ban from `"
                                + ctx.guild.name
                                + "` has expired!",
                                inline=False,
                            )
                            try:
                                await member.send(embed=embed)
                            except:
                                pass
                        except:
                            pass
                        await Data.delete_banned_member(Data, guilds, guild, member)

                        json_save(guilds, data_guild)


async def timer_hour(hours: int):

    await client.wait_until_ready()

    while client.is_ready():

        users = json_load(data_users)

        for member_i in users:

            member = await client.fetch_user(int(member_i))

            await Data.update_data_user(Data, users, member)

            json_save(users, data_users)

            users = json_load(data_users)

            # get current days
            approve_days = users[member_i]["approval"]["days"]
            approve_dval = users[member_i]["approval"]["start_date"]
            if approve_dval != 0:
                approve_date = datetime.strptime(
                    str(approve_dval), "%Y-%m-%dT%H:%M:%S.%f"
                )

            # check for users with approval days
            if approve_days > 0:

                status = member.status

                # check if they are online
                if status == discord.Status.online or status == discord.Status.dnd:
                    users = json_load(data_users)

                    # update the score
                    await Data.update_state_user_approval(
                        Data,
                        users,
                        member,
                        "score",
                        users[member_i]["approval"]["score"] + 1,
                    )
                    await Data.update_state_user_approval(
                        Data,
                        users,
                        member,
                        "checks",
                        users[member_i]["approval"]["checks"] - 1,
                    )

                    json_save(users, data_users)

                today = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
                # if its been a day since start_date
                if (today - approve_date).days >= 1:
                    users = json_load(data_users)

                    # set date as today and subtract days
                    await Data.update_state_user_approval(
                        Data, users, member, "start_date", today
                    )
                    await Data.update_state_user_approval(
                        Data,
                        users,
                        member,
                        "days",
                        users[member_i]["approval"]["days"] - 1,
                    )

                    json_save(users, data_users)

            elif approve_days == 0 and users[member_i]["approval"]["static"] != 0:
                users = json_load(data_users)

                # magical score calculation
                static = users[member_i]["approval"]["static"]
                days = static / 8

                final_score = users[member_i]["approval"]["score"] / static

                await Data.update_state_user_approval(
                    Data, users, member, "score", final_score
                )

                await Data.update_state_user(Data, users, target, "flag_approve", False)
                await Data.update_state_user_approval(
                    Data, users, target, "checks", 0
                )  # 8 checks per day
                await Data.update_state_user_approval(
                    Data, users, target, "static", 0
                )  # store check count for calculation
                await Data.update_state_user_approval(
                    Data, users, target, "start_date", 0
                )

                json_save(members, data_users)

        await asyncio.sleep(3600 * hours)


try:
    client.loop.create_task(timer_secd())
    client.loop.create_task(timer_hour(3))
    client.run(TOKEN)
except KeyboardInterrupt:
    print("exit")

