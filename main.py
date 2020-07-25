import os
import discord
import json
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio

import os.path
from os import path

from cogs.moderation import Moderation
from cogs.score import Score
from cogs.data import Data

# initialize
TOKEN = open("tmp/token.txt", "r").read()

cogs = ["cogs.score", "cogs.data", "cogs.misc", "cogs.moderation", "cogs.error"]  #

client = commands.Bot(
    command_prefix="tao ",
    status=discord.Status.idle,
    activity=discord.Game(name="initializing"),
)


@client.event
async def on_ready():
    print("{0.user}".format(client))
    await client.change_presence(
        status=discord.Status.online, activity=discord.Game(name=f"tao")
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
        await Score.sort_user_auto(Score, channel, member, data_state_late)


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
        if not message.author.bot:
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
            late = await Data.get_state_config(Data, guilds, message.guild, "late_enable")
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

            if late and not checked:

                await Score.sort_user_auto(Score, channel_notify, message.author, True)
                if verbose:
                    await Score.send_score_info(Score, channel_notify, message.author, False, True)

                # update file
                with open("cogs/_user.json", "r") as f:
                    members = json.load(f)

                await Data.update_data_user(Data, members, message.author)
                await Data.update_state_user(Data, members, message.author, True)

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

async def timer():

    await client.wait_until_ready()

    while client.is_ready():
        await asyncio.sleep(1)

        with open("cogs/_guild.json", "r") as f:
            guilds = json.load(f)

        for guild_i in guilds:

            member_list = guilds[guild_i]["banned_members"]
            guild = client.get_guild(int(guild_i))

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


client.loop.create_task(timer())
client.run(TOKEN)
