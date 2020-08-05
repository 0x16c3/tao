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
    "cogs.error"
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

    if not path.exists("cogs/_guild.json"):
        f = open("cogs/_guild.json", "w")
        f.write("{" + "}")
        f.close()
    if not path.exists("cogs/_user.json"):
        f = open("cogs/_user.json", "w")
        f.write("{" + "}")
        f.close()


@client.event
async def on_guild_join(guild):
    # update file
    with open("cogs/_guild.json", "r") as f:
        guilds = json.load(f)

    await Data.update_data(Data, guilds, guild)

    with open("cogs/_guild.json", "w") as f:
        json.dump(guilds, f)

    guild_count = len(list(client.guilds))
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(list(client.guilds))} guilds",
        ),
        fetch_offline_members=True
    )


@client.event
async def on_member_join(member):
    # update file
    with open("cogs/_guild.json", "r") as f:
        guilds = json.load(f)

    data_guild = guilds[str(member.guild.id)]
    data_ch = data_guild["chnl_notify"]
    data_state = data_guild["scre_enable"]
    data_state_late = data_guild["late_enable"]

    with open("cogs/_guild.json", "w") as f:
        json.dump(guilds, f)

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
        if not message.author.bot and isinstance(message.channel, discord.channel.TextChannel):
            # update file
            with open("cogs/_user.json", "r") as f:
                members = json.load(f)

            await Data.update_data_user(Data, members, message.author)
            checked = members[str(message.author.id)]["checked"]

            with open("cogs/_user.json", "w") as f:
                json.dump(members, f)

            # update file
            with open("cogs/_guild.json", "r") as f:
                guilds = json.load(f)

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

            with open("cogs/_guild.json", "w") as f:
                json.dump(guilds, f)

            if not setup_complete and message.content != "tao init":
                await Data.setup_notify(Data, message.channel)

            if message.content == "tao init":
                # update file
                with open("cogs/_guild.json", "r") as f:
                    guilds = json.load(f)

                guilds[str(message.guild.id)]["notified"] = True

                with open("cogs/_guild.json", "w") as f:
                    json.dump(guilds, f)

            if late and not checked:

                await Score.sort_user_auto(Score, channel_notify, message.author, True)

                # update file
                with open("cogs/_user.json", "r") as f:
                    members = json.load(f)

                await Data.update_data_user(Data, members, message.author)
                await Data.update_state_user(Data, members, message.author, "checked", True)

                with open("cogs/_user.json", "w") as f:
                    json.dump(members, f)

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

        with open("cogs/_guild.json", "r") as f:
            guilds = json.load(f)

        for guild_i in guilds:
            guild = client.get_guild(int(guild_i))

            await Data.update_data(Data, guilds, guild)
            with open("cogs/_guild.json", "w") as f:
                json.dump(guilds, f)

            with open("cogs/_guild.json", "r") as f:
                guilds = json.load(f)

            member_list = guilds[guild_i]["banned_members"]

            for member_i in member_list:
                member = await client.fetch_user(int(member_i))

                await Data.update_ban_timer(Data, guilds, guild, member)
                curtime = await Data.get_ban_timer(Data, guilds, guild, member)

                with open("cogs/_guild.json", "w") as f:
                    json.dump(guilds, f)


                if curtime <= 0:
                    with open("cogs/_guild.json", "r") as f:
                        guilds = json.load(f)

                    try:
                        await guild.unban(member)

                        embed = discord.Embed(
                            title="Info", description="", color=color_errr
                        )
                        embed.add_field(
                            name="You have been unbanned!",
                            value="Your ban from `" + ctx.guild.name + "` has expired!",
                            inline=False,
                        )
                        try:
                            await member.send(embed=embed)
                        except:
                            pass
                    except:
                        pass
                    await Data.delete_banned_member(Data, guilds, guild, member)

                    with open("cogs/_guild.json", "w") as f:
                        json.dump(guilds, f)


async def timer_hour(hours: int):

    await client.wait_until_ready()

    while client.is_ready():

        with open("cogs/_user.json", "r") as f:
            users = json.load(f)

        for member_i in users:

            member = await client.fetch_user(int(member_i))

            with open("cogs/_user.json", "r") as f:
                users = json.load(f)

            await Data.update_data_user(Data, users, member)

            with open("cogs/_user.json", "w") as f:
                json.dump(users, f)

            # get current days
            approve_days = users[member_i]["approval"]["days"]
            approve_date = users[member_i]["approval"]["start_date"]


            # check for users with approval days
            if approve_days > 0:

                status = member.status

                # check if they are online
                if status == discord.Status.online or status == discord.Status.dnd:
                    # update the score
                    await Data.update_state_user_approval(Data, users, member, "score", users[member_i]["approval"]["score"] + 1)
                    await Data.update_state_user_approval(Data, users, member, "checks", users[member_i]["approval"]["checks"] - 1)

                today = date.today()
                # if its been a day since start_date
                if (today - approve_date).days >= 1:
                    # set date as today and subtract days
                    await Data.update_state_user_approval(Data, users, member, "start_date", today)
                    await Data.update_state_user_approval(Data, users, member, "days", users[member_i]["approval"]["days"] - 1)

            elif approve_days == 0 and users[member_i]["approval"]["static"] != 0:

                # magical score calculation
                static = users[member_i]["approval"]["static"]
                days   = static / 8

                final_score = users[member_i]["approval"]["score"] / static

                await Data.update_state_user_approval(Data, users, member, "score", final_score)

            with open("cogs/_user.json", "w") as f:
                json.dump(users, f)

            await asyncio.sleep(3600 * hours)



client.loop.create_task(timer_secd(   ))
client.loop.create_task(timer_hour( 3 ))
client.run(TOKEN)
