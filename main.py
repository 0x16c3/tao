import os
import discord
import json
from discord.ext import commands
from datetime import datetime, timedelta

import os.path
from os import path

from cogs.score import Score
from cogs.data import Data

# initialize
TOKEN = open("tmp/token.txt", "r").read()

cogs = ["cogs.score", "cogs.data", "cogs.misc"]  # , "cogs.error"

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


@client.event
async def on_member_join(member):
    # update file
    with open("cogs/_guild.json", "r") as f:
        guilds = json.load(f)

    data_guild = guilds[str(member.guild.id)]
    data_ch = data_guild["chnl_notify"]
    data_state = data_guild["scre_enable"]

    with open("cogs/_guild.json", "w") as f:
        json.dump(guilds, f)

    channel = client.get_channel(data_ch)

    if data_state == True:
        await Score.sort_user_auto(Score, channel, member)


@client.event
async def on_message(message):
    # embed meta
    embed = discord.Embed(color=0xF5F5F5)

    source = "https://github.com/iinfin/tao"
    avatar = client.user.avatar_url

    if message.content == "tao":
        embed.set_author(name="Tao", url=source, icon_url=avatar)
        embed.set_thumbnail(url=avatar)

        embed.add_field(name="source", value=source, inline=False)
        embed.set_footer(text="道")

        await message.channel.send(embed=embed)

    await client.process_commands(message)


if __name__ == "__main__":
    for extension in cogs:
        try:
            client.load_extension(extension)
        except Exception as error:
            print(f"{extension} could not be activated. [{error}]")


client.run(TOKEN)
