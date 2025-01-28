# data in data.json is community generated and unmoderated
from io import BytesIO
import json
import os
import textwrap
import random
from pathlib import Path

# display_image()
import re
import numpy as np

# for LCD
import serial

# For insurance reminder
import asyncio
import time

# For Oneshot price check
from itertools import cycle
from steam_web_api import Steam

import discord
from PIL import Image, ImageFont, ImageDraw, ImageSequence
from discord.ext import commands, tasks

from BotTokens import BotToken, SteamAPIToken
from word import word

# Root directory for this script, used for referencing files in same
ROOT_DIR = Path(__file__).parent
FAV_DATA_PATH = ROOT_DIR / 'data.json'

intents = discord.Intents.all()
intents.message_content = True
client = commands.Bot(command_prefix='baidbot', intents=intents)
FoldenID = 274705127380615179
baidID = 116734104300421122  # testing purposes
MeiMeiID = 1001538703296057455
serveroffriendsID = 987848902315245598
baidbotdevserverID = 1072108038577725551
# maximum response file size without compression
maxFileSize = 25000000
# ID of voice channels in baidcology discord for text chat migration
muteChat = None
voice_channel_list=[]
hardly_know_chance = 0.005

steam = Steam(SteamAPIToken)
oneshot_id = 420530
notified = False

# cycle activity status
bot_status = cycle(
    ["Now with 100% less online-hosting"])


@tasks.loop(seconds=3600)
async def change_status():
    global notified

    # oh my gah
    oneshot_price_overview = steam.apps.get_app_details(app_id=oneshot_id, filters="price_overview"
                                                        ).get(str(oneshot_id)).get("data").get("price_overview")

    if oneshot_price_overview.get("final") < oneshot_price_overview.get("initial") and not notified:
        notified = True
        await client.get_user(baidID).send("Oneshot is on sale for " + oneshot_price_overview.get("final_formatted"))
    elif oneshot_price_overview.get("final") == oneshot_price_overview.get("initial") and notified:
        notified = False
        await client.get_user(baidID).send("Oneshot is no longer on sale")


@client.event
async def on_ready():
    await client.tree.sync()
    await client.tree.sync(guild=discord.Object(id=baidbotdevserverID))
    global muteChat, voice_channel_list

    muteChat = client.get_channel(987848902642384945)
    #get all voice channels
    for channel in client.get_all_channels(): 
        if channel.guild.id == serveroffriendsID:
            if str(channel.type) == 'voice':
                voice_channel_list.append(channel.id)

    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="your webcam"))

    print(f"Ready to use as {client.user}.")
    change_status.start()


#add new voice channels
@client.event
async def on_guild_channel_create(channel):
    if channel.guild.id == serveroffriendsID and str(channel.type) == 'voice':
        voice_channel_list.append(channel.id)


#remove deleted voice channels
@client.event
async def on_guild_channel_delete(channel):
    for guild in client.guilds:
        if guild.id == serveroffriendsID and str(channel.type) == 'voice': 
            voice_channel_list.remove(channel.id)


# Ping command
@client.tree.command(name="ping", description="return bot latency")
async def ping(interaction: discord.Interaction):
    bot_latency = round(client.latency * 1000)
    await interaction.response.send_message(f"Response time: {bot_latency}ms.")


# Favorites lookup
@client.tree.command(name="findfav", description="Finds folden's favorite everything")
async def findfav(interaction: discord.Interaction, item: str):
    data = {}
    with open(FAV_DATA_PATH, "r") as f:
        data = json.load(f)
    await interaction.response.send_message(
        f"Folden's favorite {item} is {data.get(item, 'not found. Consider using /addfav to query Foldenpaper')}.")


# Add favorites
@client.tree.command(name="addfav", description="Add a new thing to favorites list")
async def addfav(interaction: discord.Interaction, item: str):
    data = {}
    with open(FAV_DATA_PATH, "r") as fr:
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
                lines.append(f"\n    \"{item}\": \"{item2}\"\n}}")
                with open("data.json", "w") as fw:
                    fw.writelines(lines)
            await interaction.response.send_message(
                f"New thing added <@274705127380615179> Use /updatefav to add your favorite {item}!")
        else:
            await interaction.response.send_message(f"Favorite {item} already exists (**{data.get(item)}**)")


# Update favorite
@client.tree.command(name="updatefav", description="Updates favorite thing (Can only be executed by Foldenpaper)")
async def updatefav(interaction: discord.Interaction, thing: str, favorite: str):
    if (interaction.user.id == FoldenID or interaction.user.id == baidID):
        data = {}
        thing = thing.lower()
        # if favorite is NOT a URL or exception greek letter, convert to lowercase.
        if not favorite.startswith("http") and thing != "greek letter":
            favorite = favorite.lower()
        with open(FAV_DATA_PATH, "r+") as f:
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
                with open(FAV_DATA_PATH, 'w') as f:
                    json.dump(data, f, indent=4)
                await interaction.response.send_message(f"Updated favorite {thing} to {favorite} from {prev_fav}")
    else:
        await interaction.response.send_message("You must be Foldenpaper to run this command!")


# Delete favorite
@client.tree.command(name="deletefav",
                     description="Deletes favorite thing category from data (Can only be executed by Foldenpaper)")
async def deletefav(interaction: discord.Interaction, thing: str):
    if (interaction.user.id == FoldenID or interaction.user.id == baidID):
        # open data.json in read mode and open temp.json in write mode
        with open(FAV_DATA_PATH, 'r') as data:
            with open((ROOT_DIR / 'temp.json'), 'w') as temp:
                datafile_lines = data.readlines()

                for i in range(0, len(datafile_lines)):
                    # if this line is not the target deletion line, and its before the second to last entry
                    if not datafile_lines[i].startswith(f"    \"{thing}\":") and i < len(datafile_lines) - 3:
                        temp.write(datafile_lines[i])
                        continue
                    # if this line is the target line and its not the last or penultimate line, exclude it
                    # and copy rest of file as is
                    if datafile_lines[i].startswith(f"    \"{thing}\":") and i < len(datafile_lines) - 3:
                        for j in range(i + 1, len(datafile_lines)):
                            temp.write(datafile_lines[j])
                        break
                    # if line is the literal last line of file ( just a closing curly brace), copy that over
                    if i == len(datafile_lines) - 1:
                        temp.write("}")
                    # if this line is target line and is also penultimate line, write the last line instead
                    # and add a curly brace line at the end
                    if datafile_lines[i].startswith(f"    \"{thing}\":") and i == len(datafile_lines) - 3:
                        temp.write(datafile_lines[i + 1])
                        temp.write("}")
                        break
                    # if this line is target line and is also last line, write the penultimate line instead
                    # without the comma and newline char and add a curly brace line at the end
                    if datafile_lines[i].startswith(f"    \"{thing}\":") and i == len(datafile_lines) - 2:
                        temp.write(datafile_lines[i - 1][:-2] + '\n')
                        temp.write("}")
                        break

        # open data.json in write mode and temp.json in read mode
        with open(FAV_DATA_PATH, 'w') as data:
            with open((ROOT_DIR / 'temp.json'), 'r') as temp:
                # read through temp.json and copy every line back to data.json
                for line in temp:
                    print("writing line: " + line + " to data")
                    data.write(line)
        await interaction.response.send_message(f"Deleted favorite {thing} from data.")
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

    with open(FAV_DATA_PATH, 'r') as f:
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


@client.tree.command(name="meme", description="Add text to an image")
async def meme(interaction: discord.Interaction, image: discord.Attachment, toptext: str = " ",
               bottext: str = " "):
    # check if file is an image content type
    if 'image' in image.content_type:
        # defer allows discord to wait for a response longer than 3 seconds
        await interaction.response.defer()
        # download the attached image
        await image.save(ROOT_DIR / "tempImage.png")
        template = Image.open(ROOT_DIR / "tempImage.png")

        # font size scales with image width
        font_size = int(template.width / 12)
        font = ImageFont.truetype("impact.ttf", font_size)
        stroke_color = (0, 0, 0)  # black
        stroke_width = int(font_size / 15)
        text_color = (255, 255, 255)  # white
        # text margin scales with image height
        text_margin = int((template.height / 100) * 2)

        # Top Text -------------------------------------------
        # split string into multiple strings based on character length 'width'
        lines = textwrap.wrap(toptext.upper(), width=20)
        # text width and height
        tleft, ttop, tright, tbottom = font.getbbox(toptext)
        tw = tright - tleft
        th = tbottom - ttop
        # top left text box coordinate with respect to image pixels. Top left of image is 0,0
        cx, cy = int(template.width / 2), text_margin
        # y_text offset
        y_text = (cy - th / 2)

        for line in lines:
            tleft, ttop, tright, tbottom = font.getbbox(line)
            tw = tright - tleft
            th = tbottom - ttop
            draw = ImageDraw.Draw(template)
            draw.text((cx - tw / 2, cy), line, text_color, font=font, stroke_width=stroke_width,
                      stroke_fill=stroke_color)
            template.save(ROOT_DIR / "meme-generated.png")
            cy += th

        # Bottom Text -------------------------------------------
        lines = textwrap.wrap(bottext.upper(), width=20)
        tleft, ttop, tright, tbottom = font.getbbox(bottext)
        tw = tright - tleft
        th = tbottom - ttop
        cx, cy = (template.width / 2, template.height - text_margin)
        y_text = (cy - th * len(lines))

        for line in lines:
            tleft, ttop, tright, tbottom = font.getbbox(line)
            tw = tright - tleft
            th = tbottom - ttop
            draw = ImageDraw.Draw(template)
            draw.text((cx - tw / 2, y_text), line, text_color, font=font, stroke_width=stroke_width,
                      stroke_fill=stroke_color)
            template.save(ROOT_DIR / "meme-generated.png")
            y_text += th

        # Check if image is under 25Mb to be able to upload back, decrease quality of image by 5% on each pass
        if os.path.getsize((ROOT_DIR / "meme-generated.png")) >= maxFileSize:
            img_quality = 100
            template.save(ROOT_DIR / "meme-generated.jpeg", "jpeg", optimize=True, quality=img_quality)
            while os.path.getsize(ROOT_DIR / "meme-generated.jpg") >= maxFileSize:
                print(f"File is too large! Compressing image to {img_quality}% as JPEG")
                template.save(ROOT_DIR / "meme-generated.jpeg", "jpeg", optimize=True, quality=img_quality)
                img_quality -= 5
                # if (somehow) image quality is at 0 and the file is still too large, return a message
                if img_quality == 0 and os.path.getsize(ROOT_DIR / "meme-generated.jpeg") >= maxFileSize:
                    await interaction.followup.send("File is too large!")
                    return
            await interaction.followup.send(file=discord.File(ROOT_DIR / "meme-generated.jpeg"))
            return
        await interaction.followup.send(file=discord.File(ROOT_DIR / "meme-generated.png"))
    else:
        await interaction.response.send_message("File must be an image!")


@client.tree.command(name="gifmeme", description="Caption a GIF")
async def memegif(interaction: discord.Interaction, gif_file: discord.Attachment, caption: str):
    if 'gif' in gif_file.content_type:
        # defer allows discord to wait for a response longer than 3 seconds
        await interaction.response.defer()

        # download the attached GIF
        await gif_file.save(ROOT_DIR / "input.gif")
        giftemplate = Image.open(ROOT_DIR / "input.gif")
        gif_loop = giftemplate.info['loop']
        font_size = int(giftemplate.width / 10)
        font = ImageFont.truetype("Futura Condensed Extra Bold Regular.ttf", font_size)
        text_color = (0, 0, 0)  # black

        lines = textwrap.wrap(caption, width=17)
        # text width and height
        tleft, ttop, tright, tbottom = font.getbbox(caption)
        tw = tright - tleft
        th = tbottom - ttop

        # height of white box to add at top
        padding_height = int((th * len(lines)) + th / 2)
        # top left text box coordinate with respect to image pixels. Top left of image is 0,0
        cx, cy = int(giftemplate.width / 2), int((padding_height / 2))
        # y_text offset
        y_text = (cy - (th / 2) * len(lines))

        base_width, base_height = giftemplate.size
        new_height = base_height + padding_height

        # create empty white frame with extra height for text
        result_template = Image.new("RGBA", size=(base_width, new_height), color=(255, 255, 255))

        # draw text lines in the extra height
        for line in lines:
            tleft, ttop, tright, tbottom = font.getbbox(line)
            tw = tright - tleft
            th = tbottom - ttop
            draw = ImageDraw.Draw(result_template)
            draw.text((cx - tw / 2, y_text), line, text_color, font=font)
            y_text += th

        # total duration of gif
        total_duration = 0
        frames = []
        for frame in ImageSequence.Iterator(giftemplate):
            # add duration of current frame to total duration
            total_duration += frame.info['duration']
            # paste each frame of gif under extra height
            temp = result_template
            temp.paste(frame, (0, padding_height))
            b = BytesIO()
            temp.save(b, format="GIF")
            temp = Image.open(b)
            frames.append(temp)
        frames[0].save(ROOT_DIR / 'meme_out.gif', save_all=True, append_images=frames[1:], loop=gif_loop,
                       duration=total_duration / len(frames))
        await interaction.followup.send(file=discord.File(ROOT_DIR / "meme_out.gif"))
    else:
        await interaction.response.send_message("File must be a GIF!")


@client.tree.command(name="speechbubble", description="Add a speech bubble to top of an image")
async def speechbubble(interaction: discord.Interaction, image: discord.Attachment):
    await interaction.response.defer()
    if "image" in image.content_type and 'gif' not in image.content_type:
        await image.save(ROOT_DIR / "speechmemetemp.png")
        speech_template = Image.open(ROOT_DIR / "speechmemetemp.png")
        speech_bubble = Image.open(ROOT_DIR / "SBOverlay.png")
        speech_bubble = speech_bubble.resize((speech_template.width, int(speech_template.height / 3)))
        # Check if original image has transparency, use alpha_composite() if so
        if speech_template.mode != "RBGA":
            speech_template.paste(speech_bubble, (0, 0), speech_bubble)
        else:
            speech_template.alpha_composite(speech_bubble, (0, 0))
        speech_template.save(ROOT_DIR / "SBresult.png")

        # Check if image is under 25Mb to be able to upload back, decrease quality of image by 5% on each pass
        if os.path.getsize((ROOT_DIR / "SBresult.png")) >= maxFileSize:
            img_quality = 100
            speech_template.save(ROOT_DIR / "SBresult.jpeg", "jpeg", optimize=True, quality=img_quality)
            while os.path.getsize(ROOT_DIR / "SBresult.jpg") >= maxFileSize:
                print(f"File is too large! Compressing image to {img_quality}% as JPEG")
                speech_template.save(ROOT_DIR / "SBresult.jpeg", "jpeg", optimize=True, quality=img_quality)
                img_quality -= 5
                # if (somehow) image quality is at 0 and the file is still too large, return a message
                if img_quality == 0 and os.path.getsize(ROOT_DIR / "SBresult.jpeg") >= maxFileSize:
                    await interaction.followup.send("File is too large!")
                    return
            await interaction.followup.send(file=discord.File(ROOT_DIR / "SBresult.jpeg"))
            return
        await interaction.followup.send(file=discord.File(ROOT_DIR / "SBresult.png"))
    else:
        await interaction.response.send_message("File must be an image!")


@client.tree.command(name="insurance", description="Remind yourself to collect Tarkov insurance tomorrow")
async def insuranceremind(interaction: discord.Interaction):
    one_day = 86400
    one_hour = 3600
    epoch_time = int(time.time())
    await interaction.response.send_message(
        f"I will remind you at <t:{epoch_time + one_day + (one_hour * 5)}:t> tomorrow to collect your insurance",
        ephemeral=True)
    await asyncio.sleep(one_day + (one_hour * 5))
    await interaction.user.send(f"Collect your Tarkov insurance from yesterday's session at <t:{epoch_time}:t>!")


@client.tree.command(name="help", description="How to use commands")
async def help(interaction: discord.Interaction):
    # embed message
    embed_message = discord.Embed(title="Command Help", color=discord.Color.orange())
    embed_message.set_author(name=f"Requested from {interaction.user.name}", icon_url=interaction.user.avatar)
    embed_message.set_thumbnail(url=client.user.avatar)
    embed_message.add_field(name="**Folden favorites**",
                            value="`/findfav` \n- Find folden's favorite everything"
                                  "\n`/addfav` \n- Add a new category to favorites (Folden will need to use /updatefav)"
                                  "\n`/updatefav` \n- Update a category's favorite item (Can only be executed by Foldenpaper)"
                                  "\n`/deletefav` \n- Delete a favorite category (Can only be executed by Foldenpaper)"
                                  "\n`/findemptyfavs` \n- List all favorites categories which are empty (Folden will need to update with /updatefav)"
                            , inline=False)
    embed_message.add_field(name="**Meme**",
                            value="`/meme` \n- Add top text and/or bottom text to an image in the classic style"
                                  "\n`/gifmeme` \n- Add text above a gif in a margin in the classic meme gif style"
                                  "\n`/speechbubble` \n- Add a speech bubble to the top of your image for meme responses"
                            , inline=False)
    embed_message.add_field(name="**Misc**",
                            value="`/insurance` \n- Used for Tarkov players to get notified when their insurance is ready to claim (from Prapor)"
                                  "\n`/ping` \n- Returns bot latency"
                                  "\n`/help` \n- List command help"
                                  "\n`/display_image` \n- Sends an attached image to display on baid's microwave PC display"
                            , inline=False)
    await interaction.response.send_message(embed=embed_message, ephemeral=True)

@client.tree.command(name="jar", description=f"{word} leaderboard")
async def jar(interaction: discord.Interaction):
    data = {}
    with open(ROOT_DIR / "ccounter.json", 'r') as f:
        data = json.load(f)
    author = interaction.user.id
    author_place = -1
    author_count = data.get(str(author), "zero")
    sortedlist = sorted(data.items(), key=lambda x: x[1], reverse=True)

    for i in range(0, len(sortedlist)):
        if str(author) == sortedlist[i][0]:
            author_place = i + 1


    embed_message = discord.Embed(title=f"The Jar", color=discord.Color.from_rgb(255, 255, 255))
    embed_message.set_author(name=f"Requested from {interaction.user.name}", icon_url=interaction.user.avatar)
    embed_message.set_thumbnail(url="https://cdn3.emoji.gg/default/twitter/glass-of-milk.png")
    embed_message.add_field(name=f"Top Contributors",
                            value=f"\N{First Place Medal}<@{sortedlist[0][0]}> has busted a record {sortedlist[0][1]} times!\n"
                                  f"\N{Second Place Medal}<@{sortedlist[1][0]}> has busted {sortedlist[1][1]} times\n"
                                  f"\N{Third Place Medal}<@{sortedlist[2][0]}> has busted {sortedlist[2][1]} times\n"
                                  f"...\n**{author_place})** You (<@{author}>) have busted {author_count} times"
                            , inline=False)

    await interaction.response.send_message(embed=embed_message)

@client.tree.command(name="display_image",
                     description="Send an image to display on baid's PC display, may take between 5-40 seconds depending on image size")
async def display_image(interaction: discord.Interaction, image: discord.Attachment):
    # defer allows discord to wait for a response longer than 3 seconds
    await interaction.response.defer(ephemeral=True)
    if 'image' in image.content_type and 'gif' not in image.content_type:

        max_image_size = 102400  # max image size in bytes to send over socket connection, should be large enough for most images

        try:
            # opens attached image, rotates it 270deg, expands image size to accomodate rotation if needed, then resizes down
            # to a maximum of 320x160px
            await image.save(ROOT_DIR / "tempImage.jpg")

            with Image.open(ROOT_DIR / "tempImage.jpg") as msg_image:
                msg_image.thumbnail((320, 160))  # resizes image with a max of (width x height)
                msg_image.save(ROOT_DIR / "tempImage.png", optimize=True)
        except:
            await interaction.followup.send(
                "Error resizing or saving image")

        out_str = ""

        #  convert image to byte array
        img_data = np.fromfile(ROOT_DIR / "tempImage.png", dtype='uint8')
        img_data = bytearray(img_data)

        array_content = ""
        image_size = 0

        #  byte array formatting, separate values with ','
        for b in img_data:
            format(b, '#04x')
            array_content += str(b) + ","
            image_size = image_size + 1

        array_content = array_content[:-1]  # remove last comma
        #  if image is too large to send, return error message
        if image_size > max_image_size:
            await interaction.followup.send(
                f"Converted image is too large! ({image_size} bytes > {max_image_size} maximum bytes)")
        else:
            #  send image data
            if __name__ == '__main__':
                try:
                    link = serial.Serial(
                        port="/dev/ttyUSB0",  # Replace with the appropriate port
                        baudrate=115200,  # Set the baud rate
                        parity=serial.PARITY_EVEN,  # Set parity (None, Even, Odd, Mark, Space)
                        stopbits=serial.STOPBITS_ONE,  # Set number of stop bits (1, 1.5, 2)
                        bytesize=serial.EIGHTBITS,  # Set data byte size (5, 6, 7, 8)
                        timeout=5,  # Set timeout value in seconds
                        xonxoff=False,  # Enable/disable software flow control (XON/XOFF)
                        rtscts=False  # Enable/disable hardware (RTS/CTS) flow control
                    )
                    link.setRTS(False)
                    link.setDTR(False)
                except:
                    await interaction.followup.send(
                        "USB Serial Connection Error to ESP32, baid probably has it unplugged")
                out_pkg = "<"  # start of data flag
                out_pkg += str(image_size)

                out_pkg += ","

                count = 0
                for i in array_content:
                    out_pkg += str(i)
                    count += 1

                    if count % 1024 == 0:
                        print(out_pkg)
                        link.write(out_pkg.encode())  # send out_pkg as bytes
                        out_pkg = ""

                out_pkg += ">"  # end of data flag

                link.write(out_pkg.encode())  # send out_pkg as bytes
                link.close()
                await interaction.followup.send("Image sent successfully")
    else:
        await interaction.followup.send("File must be an image!")

    # On message...


@client.event
async def on_message(message):
    # if message is from baidbot, ignore all other if statements
    if message.author == client.user:
        return

    # Forward all text messages in voice channels to a single text channel
    if message.channel.id in voice_channel_list and not message.author.bot:
        # embed message
        embed_message = discord.Embed(color=message.author.accent_color, timestamp=message.created_at)
        embed_message.set_author(name=f"{message.author.display_name} - {message.channel.name}", url=message.jump_url,
                                 icon_url=message.author.avatar)
        # If message has any attachments, attach the first one to embed
        if message.attachments:
            embed_message.set_image(url=message.attachments[0])
        # If has content, send content
        if message.content:
            embed_message.add_field(name="", value=message.content, inline=False)
        await muteChat.send(embed=embed_message)

    # convert message to all lowercase
    message.content = message.content.lower()
    ccount = 0
    ccount += len(re.findall(r'\b' + word + r'\b', message.content))
    ccount += len(re.findall(r'\b' + word + "ming" + r'\b', message.content))
    ccount += len(re.findall(r'\b' + word + "my" + r'\b', message.content))

    if ccount > 0:
        data = {}
        user = str(message.author.id)
        with open(ROOT_DIR / "ccounter.json", 'r+') as f:
            data = json.load(f)
        if data.get(user, "failed") == "failed":
            data[user] = ccount
        else:
            data[user] += ccount
        f.close()
        with open(ROOT_DIR / "ccounter.json", 'w') as f:
            json.dump(data, f, indent=4)


    # hello
    if message.content.startswith('hello baidbot') or message.content.startswith('hi baidbot'):
        await message.channel.send(f"Hi <@{message.author.id}>! :heart:")
    
    # :(
    if message.content.startswith('fuck you baidbot'):
        await message.channel.send(f":cry:")

    # who asked
    if message.content.lower() == "who asked" or message.content.lower() == "didnt ask" or message.content.lower() == "didn't ask":
        await message.channel.send(
            "https://tenor.com/view/i-asked-halo-halo-infinite-master-chief-chimp-zone-gif-24941497")

    if word in message.content:
        emoji = '\N{Face with One Eyebrow Raised}'
        await message.add_reaction(emoji)

    # small chance for unfunny joke :)
    try:
        last_word = message.content.split()[-1]
        rand = random.random()
        if last_word.endswith("er") and rand <= hardly_know_chance:
            await message.channel.send(f"{last_word}!? I hardly know her!")
    except Exception as e:
        print("Exception at funni words: " + message.content)
        

    # twitter
    # if message.content.startswith("https://x.com/"):
    #    await message.channel.send(f"https://vxtwitter.com/" + message.content[14:])

client.run(BotToken)
