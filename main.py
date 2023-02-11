# data in data.json is community generated and unmoderated

import discord
import json
from discord.ext import commands, tasks
from itertools import cycle
from PIL import Image, ImageFont, ImageDraw
from token import BotToken
import textwrap
import os

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='baidbot', intents=intents)
FoldenID = 274705127380615179
baidID = 116734104300421122  # testing purposes
MeiMeiID = 1001538703296057455
baidcologyID = 987848902315245598

# cycle activity status
bot_status = cycle(
    ["with fire", "+ having fun + don't care", "with portals", "try \"hello baidbot!\"", "Half-Life 3",
     "Now with 30% less sugar!"])


@tasks.loop(seconds=300)
async def change_status():
    await client.change_presence(activity=discord.Game(next(bot_status)))


@client.event
async def on_ready():
    await client.tree.sync()
    print(f"Ready to use as {client.user}.")
    change_status.start()


# Ping command
@client.tree.command(name="ping", description="return bot latency")
async def ping(interaction: discord.Interaction):
    bot_latency = round(client.latency * 1000)
    await interaction.response.send_message(f"Response time: {bot_latency}ms.")


# Favorites lookup
@client.tree.command(name="findfav", description="Finds folden's favorite everything")
async def findfav(interaction: discord.Interaction, item: str):
    data = {}
    with open("data.json", "r") as f:
        data = json.load(f)
    await interaction.response.send_message(
        f"Folden's favorite {item} is {data.get(item, 'not found. Consider using /addfav to query Foldenpaper')}.")


# Add favorites
@client.tree.command(name="addfav", description="Add a new thing to favorites list")
async def addfav(interaction: discord.Interaction, item: str):
    data = {}
    with open("data.json", "r") as fr:
        data = json.load(fr)
        fr.close()
        item = item.lower()
        # if item is not in dictionary, copy entire dictionary except the last line
        # add a comma to end of second to last line and add a new line with the added item
        # and corresponding value "None", then write it back to data.json
        if data.get(item, "failed") == "failed":
            with open("data.json", "r") as fr:
                lines = fr.readlines()[:-1]
                lines[-1] = lines[-1][:-1] + ','
                fr.close()

                item2 = None
                lines.append(f"\n  \"{item}\": \"{item2}\"\n}}")
                with open("data.json", "w") as fw:
                    fw.writelines(lines)
            await interaction.response.send_message(
                f"New thing added <@274705127380615179> Use /updatefav to add your favorite {item}!")
        else:
            await interaction.response.send_message(f"Favorite {item} already exists (**{data.get(item)}**)")


# Update favorite
@client.tree.command(name="updatefav", description="Updates favorite thing (Can only be executed by Foldenpaper)")
async def updatefav(interaction: discord.Interaction, thing: str, favorite: str):
    if (interaction.user.id == FoldenID):
        data = {}
        thing = thing.lower()
        # if favorite is NOT a URL, convert to lowercase.
        if not favorite.startswith("http"):
            favorite = favorite.lower()
        with open("data.json", "r+") as f:
            data = json.load(f)
            # Check if thing exists, if not, send fail message
            if data.get(thing, "failed") == "failed":
                await interaction.response.send_message(
                    f"Update failed! {thing} does not exist in list! Try using /addfav to create it first.")
                return
            else:
                prev_fav = data.get(thing)
                data[thing] = favorite
                f.close()
                with open("data.json", 'w') as f:
                    json.dump(data, f, indent=4)
                await interaction.response.send_message(f"Updated favorite {thing} to {favorite} from {prev_fav}")
    else:
        await interaction.response.send_message("You must be Foldenpaper to run this command!")


# Find empty favorites
@client.tree.command(name="findemptyfavs", description="Finds and lists favorites with no entry")
async def emptyfavs(interaction: discord.Interaction):
    data = {}
    emptyItems = ""
    # embed message format setup
    embed_message = discord.Embed(title="Empty Favorites", description="Foldenpaper must set these with /updatefav",
                                  color=discord.Color.orange())
    embed_message.set_author(name=f"Requested from {interaction.user.name}", icon_url=interaction.user.avatar)
    embed_message.set_thumbnail(url=interaction.guild.icon)

    with open("data.json", 'r') as f:
        data = json.load(f)
    # iterate through entire dictionary, if the favorite is listed as "None"
    # add the corresponding 'thing' to 'emptyItems' string array
    for thing, favorite in data.items():
        if favorite == "None":
            # if emptyItems is empty, dont start with a new line
            if emptyItems == "":
                emptyItems += thing
            else:
                emptyItems += ('\n' + thing)
    embed_message.add_field(name="Empty favorites for the following things:", value=emptyItems, inline=False)
    await interaction.response.send_message(embed=embed_message)


# @client.tree.command(name="listfavs", description="List available things to query")
# async def listfavs(interaction: discord.Interaction):
#    data = {}
#    favlist = ""
#    # embed message
#    embed_message = discord.Embed(title="Available things", description="All available things to use with /findfav",
#                                  color=discord.Color.orange())
#    embed_message.set_author(name=f"Requested from {interaction.user.name}", icon_url=interaction.user.avatar)
#    embed_message.set_thumbnail(url=interaction.guild.icon)
#   with open("data.json", 'r') as f:
#        data = json.load(f)
#   for thing, favorite in data.items():
#       if favlist == "":
#           favlist += thing
#       else:
#           favlist += (', ' + thing)
#   embed_message.add_field(name="Things:", value=favlist, inline=False)
#   await interaction.response.send_message(embed=embed_message)

@client.tree.command(name="meme", description="Add text to an image")
async def emptyfavs(interaction: discord.Interaction, image: discord.Attachment, toptext: str = " ",
                    bottext: str = " "):
    # check if file is an image content type
    if 'image' in image.content_type:
        # defer allows discord to wait for a response longer than 3 seconds
        await interaction.response.defer()
        # download the attached image
        await image.save("tempImage.jpg")
        template = Image.open("tempImage.jpg")
        # Convert to JPG
        template = template.convert("RGB")
        # font size scales with image width
        font_size = int(template.width / 10)
        font = ImageFont.truetype("impact.ttf", font_size)
        stroke_color = (0, 0, 0)  # black
        stroke_width = int(font_size / 10)
        text_color = (255, 255, 255)  # white
        # text margin scales with image height
        text_margin = int((template.height / 100) * 2)

        # Top Text -------------------------------------------
        # split string into multiple strings based on character length 'width'
        lines = textwrap.wrap(toptext.upper(), width=20)
        # text width and height
        tw, th = font.getsize(toptext)
        # top left text box coordinate with respect to image pixels. Top left of image is 0,0
        cx, cy = int(template.width / 2), text_margin
        # y_text offset
        y_text = (cy - th / 2)

        for line in lines:
            tw, th = font.getsize(line)
            draw = ImageDraw.Draw(template)
            draw.text((cx - tw / 2, cy), line, text_color, font=font, stroke_width=stroke_width,
                      stroke_fill=stroke_color)
            template.save("meme-generated.jpg", "JPG")
            y_text += th

        # Bottom Text -------------------------------------------
        lines = textwrap.wrap(bottext.upper(), width=20)
        tw, th = font.getsize(bottext)
        cx, cy = (template.width / 2, template.height - text_margin)
        y_text = (cy - th * len(lines))

        for line in lines:
            tw, th = font.getsize(line)
            draw = ImageDraw.Draw(template)
            draw.text((cx - tw / 2, y_text), line, text_color, font=font, stroke_width=stroke_width,
                      stroke_fill=stroke_color)
            template.save("meme-generated.png", "jpg")
            y_text += th

        # Check if image is under 8Mb to be able to upload back, decrease quality of image by 5% on each pass
        img_quality = 100
        while os.path.getsize("meme-generated.jpg") >= 8000000:
            img_quality -= 5
            template.save("meme-generated.png", "jpg", optimize=True, quality=img_quality)
            # if (somehow) image quality is at 0 and the file is still too large, return a message
            if img_quality == 0 and os.path.getsize("meme-generated.jpg") >= 8000000:
                await interaction.followup.send("File is too large!")
                return

        await interaction.followup.send(file=discord.File("meme-generated.jpg"))
    else:
        interaction.response.send_message("File must be an image!")


# On message...
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    message.content = message.content.lower()
    if message.content.startswith('hello baidbot') or message.content.startswith('hi baidbot'):
        await message.channel.send("Heyo! :wave:")

    if ((message.content.endswith('er')
         or message.content.endswith('er.')
         or message.content.endswith('er?')
         or message.content.endswith('er*')
         or message.content.endswith('er:')
         or message.content.endswith('er!'))
            and message.author.id != MeiMeiID  # MeiMei is not to be trusted...
            and message.author.id != baidID
            and message.guild.id == baidcologyID):
        await message.channel.send(f"{message.content}? I hardly know her")

    if message.content.lower() == "who asked":
        await message.channel.send(
            "https://tenor.com/view/i-asked-halo-halo-infinite-master-chief-chimp-zone-gif-24941497")



client.run(BotToken)
