import discord
import json

# guild data json
data_guild = "cogs/_guild.json"
# user data json
data_users = "cogs/_user.json"

# variables
guild_count = 0

# colors
color_main = discord.Color(0xF5F5F5)
color_done = discord.Color(0x00FFFF)
color_warn = discord.Color(0xFFFF00)
color_errr = discord.Color(0xFF0000)


def json_load(filename):
    with open(filename, "r") as f:
        return json.load(f)


def json_save(data, filename):
    try:
        with open(filename, "w") as outfile:
            json.dump(data, outfile)
    except:
        if os.path.exists(filename):
            os.unlink(filename)
        raise


def mention_to_id(mention: str):
    result = mention.replace("<", "")
    result = result.replace(">", "")
    result = result.replace("@", "")
    result = result.replace("!", "")
    return result


async def fetch_member(clientobj, id):
    for guild in clientobj.guilds:
        try:
            member = await guild.fetch_member(id)
            if member == None or member == 0:
                continue
            else:
                return await guild.fetch_member(id)
        except:
            pass


async def get_member(string, guild, channel):

    var_type = ""

    if "<" in string and ">" in string and "@" in string:
        var_type = "mention"
        try:
            return await guild.fetch_member(int(mention_to_id(string)))
        except:
            return f"{mention_to_id(string)}:FAIL_NOTFOUND"
    elif string.isdecimal():
        var_type = "id"
        try:
            return await guild.fetch_member(int(string))
        except:
            return f"{int(string)}:FAIL_NOTFOUND"
    else:
        var_type = "name"
        if guild.get_member_named(string):
            return guild.get_member_named(string)
        else:
            if channel != None and type(channel) is discord.TextChannel:
                embed_errr = discord.Embed(
                    title="{}".format("Something went wrong"),
                    description="",
                    color=0xF5F5F5,
                )

                embed_errr.add_field(
                    name="Error", value="Can't find user", inline=False
                )

                embed_errr.add_field(
                    name="Try to enter:", value=f"`member.id`", inline=False,
                )

                await channel.send(embed=embed_errr)

    if channel != None and type(channel) is discord.TextChannel:
        embed_errr = discord.Embed(
            title="{}".format("Something went wrong"), description="", color=0xF5F5F5,
        )

        embed_errr.add_field(name="Error", value="Invalid type", inline=False)

        embed_errr.add_field(
            name="Details", value=f"`Bad argument`", inline=False,
        )

        await channel.send(embed=embed_errr)

    return None
