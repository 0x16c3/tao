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
        with open(filename, 'w') as outfile:
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


async def get_member(string, guild, channel):

    var_type = ""

    if "<" in string and ">" in string and "@" in string:
        var_type = "mention"
        return await guild.fetch_member(int(mention_to_id(string)))
    elif string.isdecimal():
        var_type = "id"
        return await guild.fetch_member(int(string))
    else:
        var_type = "name"
        return guild.get_member_named(string)

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
