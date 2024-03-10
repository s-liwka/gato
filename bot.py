import discord
from discord.ext import commands
import time
import random
import json
import os
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import aiohttp
import shutil
import platform
import tempfile
import g4f
import asyncio
from cryptography.fernet import Fernet

import modules.captions
import modules.speechbubble
import modules.attachments
import modules.token_tools
import modules.nitro_sniper

from queue import Queue


import modules.paths

# welcome to shitcode

# yippie globals
global config
global log

def load_config():
    global config
    global log
    config_file, config_dir = modules.paths.get_config_file_dir()

    # sounds for play
    if not os.path.exists(os.path.join(config_dir, 'sounds')):
        os.makedirs(os.path.join(config_dir, 'sounds'), exist_ok=True)

    default_config = {
        "logger": False,
        "sniper": False,
        "profanity": False,
        "prompt_destructive": True,
        "delete_after_time": 5.0,
        "prefix": ";",
        "token": ""
    }

    # config
    if not os.path.exists(config_file):
        os.makedirs(config_dir, exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(default_config, f)

    else:
        # add keys if new options are added
        with open(config_file, 'r') as f:
            config = json.load(f)

        for key, value in default_config.items():
            if key not in config:
                config[key] = value

        with open(config_file, 'w') as f:
            json.dump(config, f)

    with open(config_file, 'r') as f:
        config = json.load(f)

    # log
    log = os.path.join(config_dir, 'log.json')

    if not os.path.exists(log):
        with open(log, 'w') as f:
            messages = {}
            json.dump(messages, f)

    # token key
    if not os.path.exists(os.path.join(config_dir, 'token_encryption_key')):
        with open(os.path.join(config_dir, 'token_encryption_key'), 'wb') as f:
            key = Fernet.generate_key()
            f.write(key)

    return config, log

class Gato(commands.Bot):

    global config
    global log

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = kwargs.get('queue', Queue())


    async def on_ready(self):
        print(f'haii!! {self.user} is weady!!! :3 meow')
        self.queue.put(f'[SUCCESS] Logged in as {self.user}')


    async def on_message_delete(self, message):
        if config.get("logger", False):

            if message.author == self.user:
                return

            try:
                test = message.guild.name
                dm = False
            except AttributeError:
                dm = True

            data = {
                'server': message.guild.name if not dm else "DM",
                'channel': message.channel.name if not dm else "N/A",
                'channel_id': message.channel.id,
                'author': message.author.name.replace('#0', ''),
                'author_id': message.author.id,
                'content': message.content,
                'attachments': [attachment.url for attachment in message.attachments],
            }

            with open(log, 'r') as f:
                messages = json.load(f)

            messages[len(messages) + 1] = data

            with open(log, 'w') as f:
                json.dump(messages, f)

            self.queue.put(f"[INFO] Logged message -> {message.author.name.replace('#0', '')}: {message.content}")

    async def on_message(self, message):
        await self.process_commands(message)


        if config.get('profanity', True):
            pass


        if config.get('sniper', True):
            if 'discord.gift' in message.content:
                response = await modules.nitro_sniper.redeem_nitro(config['token'], message.content.split('discord.gift/')[1], str(message.channel.id))
            elif 'discord.com/gifts/' in message.content:
                response = await modules.nitro_sniper.redeem_nitro(config['token'], message.content.split('discord.com/gifts/')[1], str(message.channel.id))
            else:
                response = None

            if response is not None:
                if response['code'] == 10038:
                    self.queue.put("[INFO] Nitro Sniper: Unknown gift code")
                else:
                    self.queue.put("[INFO] Nitro Sniper: NOT an unknown gift code. Maybe expired or success idk what codes there are")

# config gets created here
config, log = load_config()
bot = Gato(command_prefix=config['prefix'], self_bot=True, queue=None)


async def confirm_destructive_action(ctx):
    try:
        prompt_message = await ctx.reply('**! DESTRUCTIVE ACTION !**\n\nReply with **"y"** to confirm. **"n"** to cancel.')
        reply = await bot.wait_for('message', timeout=15, check=lambda m: m.author == ctx.author)
        
        if reply.content.lower() == 'y':
            await prompt_message.delete()
            await ctx.reply('Confirmed.', delete_after=config['delete_after_time'])
            return True
        elif reply.content.lower() == 'n':
            await prompt_message.delete()
            await ctx.reply('Cancelled.', delete_after=config['delete_after_time'])
            return False
        else:
            await prompt_message.delete()
            await ctx.reply('Invalid selection. Cancelled.', delete_after=config['delete_after_time'])
            return False

    except asyncio.TimeoutError:
        await prompt_message.delete()
        await ctx.reply("You didn't reply in time.", delete_after=config['delete_after_time'])
        return False

async def split_message(ctx, message):
    bot.queue.put("[DEBUG] Message is too long! Splitting into chunks...")

    if ctx.message.author.premium:
        max_length = 4000
    else:
        max_length = 2000

    chunks = [message[i:i + max_length] for i in range(0, len(message), max_length)]
    return chunks


@bot.command()
async def h(ctx):
    msg = ""
    msg += f"{config['prefix']}ping -> Checks your latency\n"
    msg += f"{config['prefix']}mock -> mOcKs SoMeOnE. Reply to the message you wanna mock with the command\n"
    msg += f"{config['prefix']}ddg -> Makes a duckduckgo query on the message you will respond to with this command\n"
    msg += f"{config['prefix']}s -> Get the last deleted message from this channel\n"
    msg += f"{config['prefix']}calc <equation> -> Do simple arithmetic\n"
    msg += f"{config['prefix']}caption <caption> -> Caption a gif/image esmbot style. Reply to the image which you wish to caption\n"
    msg += f"{config['prefix']}speechbubble -> Add a speech bubble to a gif/image. Reply to the image you wish to add the speech bubble to\n"
    msg += f"{config['prefix']}togif -> Converts an image to a gif. Reply to the image you wish to convert\n"
    msg += f"{config['prefix']}masscreate <name> <times> -> Creates a channel with the name <name> <times> times\n"
    msg += f"{config['prefix']}massdelete <name> -> Deletes all channels with the provided name\n"
    msg += f"{config['prefix']}roles <give/take> <member> <role name/id> -> Manage user's roles\n"
    msg += f"{config['prefix']}gpt [--provider] [--ctx] -> Talk with a chatbot. --provider <provider> to select the bot and --ctx <num> to let the bot have the previous messages\n"
    msg += f"{config['prefix']}convert <num> <unit from> <unit to> -> Convert lenght and weight units\n"
    msg += f"{config['prefix']}clear <num> -> Deletes <num> messages from the channel\n"
    msg += f"{config['prefix']}clean <num> -> Deletes <num> messages sent by you from the channel\n"
    msg += f"{config['prefix']}nuke -> Nukes a channel\n"

    if len(msg)>2000:
        await ctx.message.delete()
        chunks = await split_message(ctx, msg)

        for chunk in chunks:
            await ctx.send(chunk)

    else:
        await ctx.message.edit(msg)

@bot.command(category='Utils')
async def ping(ctx):
    """If you found this using the help command then run the h command instead"""
    try:
        latency = bot.latency * 1000
        await ctx.reply(f'Pong! **{latency:.0f}ms**', delete_after=None)
        bot.queue.put(f'[INFO] Latency: {latency:.0f}ms')
    
    except Exception as e:
        await ctx.reply(f"[ERR]: {e}")
        bot.queue.put(f"[ERR] Ping command raised an exception: {e}")

@bot.command()
async def mock(ctx):
    """mOcKs SoMeOnE. Reply to the message you wanna mock with the command"""
    bot.queue.put("[INFO] Command mock called")
    try:
        i = 0
        message = ''
        for char in ctx.message.reference.resolved.content:
            i += 1
            if i%2 == 0:
                message += char.lower()
            else:
                message += char.upper()

        await ctx.message.edit(message)
        bot.queue.put("[INFO] Command mock successful")


    except Exception as e:
        await ctx.reply(f"[ERR]: {e}")
        bot.queue.put(f"[ERR] Mock command raised an exception: {e}")



@bot.command()
async def ddg(ctx, query: str=None):
    """Makes a duckduckgo query on the message you will respond to with this command"""
    bot.queue.put(f"[INFO] Command DDG called. Query: {query}")
    try:
        if ctx.message.reference is not None:
            await ctx.message.edit(f'https://duckduckgo.com/?q={ctx.message.reference.resolved.content.replace(" ", "%20")}')

        else:
            if query is not None:
                await ctx.message.edit(f'https://duckduckgo.com/?q={query.replace(" ", "%20")}')
            else:
                await ctx.reply('Invalid syntax. ddg [query] or respond to a message with ddg', delete_after=config['delete_after_time'])
                await ctx.message.remove()
                bot.queue.put("[ERR] Command DDG: Invalid syntax: No query/reference message")

        bot.queue.put("[INFO] Command DDG successful")

    except Exception as e:
        await ctx.reply(f"[ERR]: {e}")
        bot.queue.put(f"[ERR] DDG command raised an exception: {e}")


@bot.command()
async def s(ctx):
    """Get the last deleted message from this channel"""
    global log
    bot.queue.put("[INFO] Command s (snipe) called")
    try:
        with open(log, 'r') as f:
            data = json.load(f)
        
        for section in reversed(data.values()):
            if section["channel_id"] == ctx.channel.id:
                if len(section["attachments"]) != 0:
                    if section['content'] != "":
                        await ctx.message.edit(f'**{section["author"]}** said **"{section["content"]}"** with but deleted it. Linked attachments:')
                        for url in section['attachments']:
                            await ctx.channel.send(url)
                    else:
                        await ctx.message.edit(f'**{section["author"]}** sent a message with some attachments but deleted it:')
                        for url in section['attachments']:
                            await ctx.channel.send(url)  
                else:
                    await ctx.message.edit(f'**{section["author"]}** said **"{section["content"]}"** but deleted it')
                return
        
        try:
            await ctx.message.edit(f"No logged messages in this channel ({ctx.message.channel.name}) found.")
        except:
            await ctx.message.edit(f"No logged messages in this channel found.")

        bot.queue.put("[INFO] Command s (snipe) successful")


    except Exception as e:
        await ctx.reply(f"[ERR]: {e}")
        bot.queue.put(f"[ERR] Snipe command raised an exception: {e}")


@bot.command()
async def calc(ctx, equation: str):
    """Do simple arithmetic. Usage: calc <equation>"""
    bot.queue.put("[INFO] Command calc called")
    try:
        if len(equation) > 15:
            await ctx.reply('Equation too long', delete_after=config['delete_after_time'])
            return
        await ctx.message.edit(f"{ctx.message.content.replace('.calc ', '')} = {eval(equation)}")
        bot.queue.put("[INFO] Command calc successful")


    except Exception as e:
        await ctx.reply(f"[ERR]: {e}")
        bot.queue.put(f"[ERR] Calc command raised an exception: {e}")


@bot.command()
async def caption(ctx, *captions):
    """Caption a gif/image esmbot style. Usage: caption <caption> -- Reply to the image which you wish to caption."""
    try:
        captions = ' '.join(captions)
        tmp = tempfile.gettempdir()
        bot.queue.put(f'[INFO] Command caption called. Captions: {captions}')

        if ctx.message.reference.resolved.content and 'tenor.com' in ctx.message.reference.resolved.content:
            bot.queue.put("[DEBUG] Command caption: Tenor detected")
            url = await modules.attachments.get_gif_url_tenor(ctx.message.reference.resolved.content)
            if url is not None:
                path = await modules.attachments.download_attachment(url, bot.queue)

        else:
            path = await modules.attachments.download_attachment(ctx.message, bot.queue)

        caption_path = modules.captions.generate_caption_image(captions, Image.open(path), bot.queue)

        output_path = os.path.join(tmp, 'captioned.gif')

        if modules.attachments.is_animated(path):
            bot.queue.put('[DEBUG] Command caption: Creating animated image...')
            modules.captions.process_animated_gif(path, caption_path, output_path, bot.queue)
        else:
            bot.queue.put('[DEBUG] Command caption: Creating static image...')
            modules.captions.process_image(path, caption_path, output_path, bot.queue)

        await ctx.channel.send(file=discord.File(output_path))
        os.remove(output_path)
        await ctx.message.delete()

        bot.queue.put('[INFO] Command caption successful')


    except Exception as e:
        await ctx.reply(f"[ERR]: {e}")
        bot.queue.put(f"[ERR] Caption command raised an exception: {e}")


@bot.command()
async def speechbubble(ctx):
    """Add a speech bubble to a gif/image. Reply to the image you wish to add the speech bubble to"""
    bot.queue.put("[INFO] Command speechbubble called")
    try:
        tmp = tempfile.gettempdir()
        if ctx.message.reference.resolved.content and 'tenor.com' in ctx.message.reference.resolved.content:
            bot.queue.put("[DEBUG] Command speechbubble: Tenor detected")
            url = await modules.attachments.get_gif_url_tenor(ctx.message.reference.resolved.content)
            if url is not None:
                path = await modules.attachments.download_attachment(url, bot.queue)

        else:
            path = await modules.attachments.download_attachment(ctx.message, bot.queue)
    

        output_path = os.path.join(tmp, 'speechbubble.gif')
        
        if modules.attachments.is_animated(path):
            bot.queue.put('[DEBUG] Command speechbubble: Creating animated image...')
            modules.speechbubble.process_animated_gif(path, output_path, bot.queue)
        else:
            bot.queue.put('[DEBUG] Command speechbubble: Creating static image...')
            modules.speechbubble.process_image(path, output_path, bot.queue)

        await ctx.channel.send(file=discord.File(output_path))
        os.remove(output_path)
        await ctx.message.delete()
        bot.queue.put("[INFO] Command speechbubble successful")



    except Exception as e:
        await ctx.reply(f"[ERR]: {e}")
        bot.queue.put(f"[ERR] Speechbubble command raised an exception: {e}")

@bot.command()
async def togif(ctx):
    """Convert an image to a gif. Reply to the image you wanna convert with this command"""
    bot.queue.put("[INFO] Command togif called")
    try:
        tmp = tempfile.gettempdir()
        path = await modules.attachments.download_attachment(ctx.message, bot.queue) 

        image = Image.open(path)
        image.save(os.path.join(tmp, 'togif.gif'), 'GIF')

        await ctx.message.delete()
        await ctx.channel.send(file=discord.File(os.path.join(tmp, 'togif.gif')))
        os.remove(os.path.join(tmp, 'togif.gif'))

        bot.queue.put("[INFO] Command togif successful")


    except Exception as e:
        await ctx.reply(f'[ERR]: {e}', delete_after=config['delete_after_time'])
        bot.queue.put(f'[ERR] Command togif raised an exception: {e}')


# mass create
@bot.command()
async def masscreate(ctx, name, times):
    """Create some channels with some name. Usage: masscreate <name> <times>"""
    bot.queue.put(f"[INFO] Command masscreate called. Name: {name}, {times} times")
    try:

        try:
            times = int(times)
        except:
            bot.queue.put("[ERR] Command masscreate: Invalid syntax: times is not int")
            await ctx.send("Invalid syntax. Usage: `masscreate <name> <times>`", delete_after=config['delete_after_time'])
            return
        
        if ctx.message.guild is None:
            bot.queue.put("[ERR] Command masscreate: Not a guild")
            await ctx.send("This is a DM channel, but the command can only run on guilds.", delete_after=config['delete_after_time'])
            return

        
        if not ctx.message.author.guild_permissions.manage_channels:
            await ctx.send("You have insufficient permissions for this action. Required permission: Manage channels")
            return

        for i in range (0, times):
            await ctx.guild.create_text_channel(name)
        
        await ctx.message.delete()

        bot.queue.put("[INFO] Command masscreate successful")

    except Exception as e:
        await ctx.channel.delete()
        await ctx.send(f'[ERR]: {e}')
        bot.queue.put(f'[ERR] Command masscreate raised an exception: {e}')

@masscreate.error
async def masscreate_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Invalid syntax. Usage: `masscreate <name> <times>`", delete_after=config['delete_after_time'])
        

# massdelete
@bot.command(cog='Server Utils', enabled=False)
async def massdelete(ctx, name):
    bot.queue.put("[INFO] Command massdelete called")
    await ctx.message.delete()

    if ctx.message.guild is None:
        bot.queue.put("[ERR] Command massdelete: Failure: Not a guild")
        await ctx.send("This is a DM channel, but the command can only run on guilds.", delete_after=config['delete_after_time'])
        return
    

    if not ctx.message.author.guild_permissions.manage_channels:
        await ctx.send("You have insufficient permissions for this action. Required permission: Manage channels", delete_after=config['delete_after_time'])
        return

    for channel in ctx.guild.channels:
        if channel.name == name:
            await channel.delete()

    bot.queue.put("[INFO] Command massdelete successful")



@massdelete.error
async def massdelete_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Invalid syntax. Usage: `massdelete <name>`", delete_after=config['delete_after_time'])


#niuk
@bot.command()
async def nuke(ctx):
    try:

        if ctx.message.guild is None:
            await ctx.message.delete()
            await ctx.send("This is a DM channel, but the command can only run on guilds.", delete_after=config['delete_after_time'])
            return

        if not ctx.message.author.guild_permissions.manage_channels:
            await ctx.message.delete()
            await ctx.send("You have insufficient permissions for this action. Required permission: Manage channels", delete_after=config['delete_after_time'])
            return

        if config.get('prompt_for_destructive', True):
            if not await confirm_destructive_action(ctx):
                await ctx.message.delete()
                return

        info = {
            'name': ctx.channel.name,
            'topic': ctx.channel.topic,
            'category': ctx.channel.category,
            'nsfw': ctx.channel.nsfw,
            'slowmode_delay': ctx.channel.slowmode_delay,
            'position': ctx.channel.position
        }
        
        await ctx.channel.delete()
        await ctx.guild.create_text_channel(name=info['name'], category=info['category'], topic=info['topic'], nsfw=info['nsfw'], position=info['position'], slowmode_delay=info['slowmode_delay'])

    except Exception as e:
        await ctx.channel.delete()
        await ctx.send(f'[ERR]: {e}')
        bot.queue.put(f'[ERR] Command nuke raised an exception: {e}')
        



#konwerszyn
@bot.command()
async def convert(ctx, number, unit_from, unit_to):

    lenght_conversion_factors = {
        "mm": {"mm": 1, "cm": 0.1, "m": 0.001, "km": 1e-6, "ft": 0.003281, "in": 0.03937},
        "cm": {"mm": 10, "cm": 1, "m": 0.01, "km": 1e-5, "ft": 0.032808, "in": 0.393701},
        "m": {"mm": 1000, "cm": 100, "m": 1, "km": 0.001, "ft": 3.281, "in": 39.37},
        "km": {"mm": 1e6, "cm": 1e5, "m": 1000, "km": 1, "ft": 3281, "in": 39370},
        "ft": {"mm": 304.8, "cm": 30.48, "m": 0.3048, "km": 0.0003048, "ft": 1, "in": 12},
        "in": {"mm": 25.4, "cm": 2.54, "m": 0.0254, "km": 0.0000254, "ft": 0.0833333, "in": 1}
    }

    weight_conversion_factors = {
        "mg": {"mg": 1, "g": 0.001, "kg": 1e-6, "lb": 2.20462e-6, "oz": 3.5274e-5},
        "g": {"mg": 1000, "g": 1, "kg": 0.001, "lb": 0.00220462, "oz": 0.035274},
        "kg": {"mg": 1e6, "g": 1000, "kg": 1, "lb": 2.20462, "oz": 35.274},
        "lb": {"mg": 453592, "g": 453.592, "kg": 0.453592, "lb": 1, "oz": 16},
        "oz": {"mg": 28349.5, "g": 28.3495, "kg": 0.0283495, "lb": 0.0625, "oz": 1}
    }

    if unit_from in lenght_conversion_factors and unit_to in lenght_conversion_factors[unit_from]:
        result = round(float(number) * float(lenght_conversion_factors[unit_from][unit_to]), 4)
        result = str(result).rstrip('0').rstrip('.') if '.' in str(result) else str(result)
        await ctx.message.edit(f'{number}{unit_from} is {result}{unit_to}')

    elif unit_from in weight_conversion_factors and unit_to in weight_conversion_factors[unit_from]:
        result = round(float(number) * float(weight_conversion_factors[unit_from][unit_to]), 4)
        result = str(result).rstrip('0').rstrip('.') if '.' in str(result) else str(result)
        await ctx.message.edit(f'{number}{unit_from} is {result}{unit_to}')



# clean
@bot.command()
async def clean(ctx, count: int):
    try:
        await ctx.message.delete()
        messages_deleted = 0
        async for message in ctx.channel.history(limit=None):
            if message.author == ctx.message.author:
                await message.delete()
                messages_deleted += 1
                if messages_deleted == count:
                    break

        await ctx.send(f'Deleted {count} messages sent by myself.')
        bot.queue.put('[INFO] Command clean successful')

    except Exception as e:
        await ctx.send(f'[ERR]: {e}')
        bot.queue.put(f'[ERR] Command clean raised an exception: {e}')
        

@clean.error
async def clean_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Invalid syntax. Usage: `clean <amount>`", delete_after=config['delete_after_time'])


# server utils

# clear
@bot.command()
async def clear(ctx, count: int):
    bot.queue.put('[INFO] Command clear called')
    try:

        if ctx.message.guild is None:
            await ctx.message.delete()
            await ctx.send("This is a DM channel, but the command can only run on guilds.", delete_after=config['delete_after_time'])
            return

        if not ctx.message.author.guild_permissions.manage_messages:
            await ctx.message.delete()
            await ctx.send("You have insufficient permissions for this action. Required permission: Manage messages", delete_after=config['delete_after_time'])
            return


        await ctx.message.delete()
        messages_deleted = 0
        async for message in ctx.channel.history(limit=None):
            await message.delete()
            messages_deleted += 1
            if messages_deleted == count:
                break
        
        await ctx.send(f'Deleted {count} messages.')
        bot.queue.put('[INFO] Command clear successful')

    except Exception as e:
        await ctx.send(f'[ERR]: {e}')
        bot.queue.put(f'[ERR] Command clear raised an exception: {e}')
        

@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Invalid syntax. Usage: `clean <amount>`", delete_after=config['delete_after_time'])


# roles

@bot.command()
async def roles(ctx, action, member, role):
    bot.queue.put(f'[INFO] Command roles called. Arguments: Action: {action} | Member: {member} | Role: {role}')
    try:

        if ctx.message.guild is None:
            await ctx.message.delete()
            await ctx.send("This is a DM channel, but the command can only run on guilds.", delete_after=config['delete_after_time'])
            return

        if not ctx.message.author.guild_permissions.manage_roles:
            await ctx.message.delete()
            await ctx.send("You have insufficient permissions for this action. Required permission: Manage roles", delete_after=config['delete_after_time'])
            return

        if role.isdigit():
            role = ctx.guild.get_role(int(role))
        else:
            role = discord.utils.get(ctx.guild.roles, name=role)

        if action == 'give':
            if member == '@everyone':
                if config.get('prompt_for_destructive', True):
                    if not await confirm_destructive_action(ctx):
                        await ctx.message.delete()
                        return

                for m in ctx.guild.members:
                    await m.add_roles(role)
                await ctx.send(f"Gave everyone the role **{role.name}**", delete_after=config['delete_after_time'])

            elif member is not None:
                member = await commands.MemberConverter().convert(ctx, member)
                await member.add_roles(role)
                await ctx.send(f"Gave {member} the role **{role.name}**", delete_after=config['delete_after_time'])
            else:
                await ctx.reply(f"Invalid member {member}")

        elif action == 'take':
            if member == '@everyone':
                if config.get('prompt_for_destructive', True):
                    if not await confirm_destructive_action(ctx):
                        await ctx.message.delete()
                        return

                for m in ctx.guild.members:
                    await m.remove_roles(role)

                await ctx.send(f"Removed the role **{role.name}** from everyone", delete_after=config['delete_after_time'])
            elif member is not None:
                member = await commands.MemberConverter().convert(ctx, member)
                await member.remove_roles(role)
                await ctx.send(f"Removed the role {role.name} from {member}", delete_after=config['delete_after_time'])
            else:
                await ctx.reply(f"Invalid member {member}")
            
        await ctx.message.delete()

    except Exception as e:
        bot.queue.put(f'[ERR] Command roles raised an exception: {e}')

# gpt 
@bot.command()
async def gpt(ctx, *prompt):
    bot.queue.put("[INFO] Command GPT called")
    try:
        prompt = list(prompt)
        if '--provider' in prompt:
            provider = prompt[prompt.index('--provider') + 1]
            prompt.pop(prompt.index('--provider') + 1)
            prompt.remove('--provider')
        else:
            provider = None
        if '--ctx' in prompt:
            context_window = prompt[prompt.index('--ctx') + 1]
            prompt.pop(prompt.index('--ctx') + 1)
            prompt.remove('--ctx')
        else:
            context_window = None

        bot.queue.put(f'[DEBUG] Command GPT: {"Detected provider argument "+provider+". " if provider is not None else "No provider argument detected. Using the default. "}{"Detected context window "+str(context_window)+"." if context_window is not None else "No context window detected."}')
        
        prompt = ' '.join(prompt)

        if context_window is not None:
            try:
                context_window = int(context_window)
                try:
                    recent_messages = []
                    async for message in ctx.message.channel.history(limit=context_window+1):
                        if message != ctx.message:
                            recent_messages.append(message)

                    og_prompt = prompt
                    prompt = "Previous messages sent for context:\n"
                    for msg in recent_messages:
                        prompt += f"{msg.author}: {msg.content}\n"
                    prompt += f"Prompt: {og_prompt}"


                except Exception as e:
                    bot.queue.put(f'[ERR] Command GPT: Fetching history: {e}')
                    return       

            except:
                await ctx.reply('Invalid syntax. Context window must be a number.', delete_after=config['delete_after_time'])
                await ctx.message.delete()
                bot.queue.put(f'[ERR] Command GPT: Invalid syntax. Context window must be a number.')
                return

        bot.queue.put(f'[DEBUG] Command GPT: Prompt is "{prompt}"')

        if provider is None:
            provider = g4f.Provider.You
            found = True
        else:
            found = False
            for prov in g4f.Provider.__providers__:
                if prov.working:
                    if prov.__name__ == provider.capitalize():
                        provider = prov
                        found = True
                        break
        
        if not found:
            await ctx.reply(f'[ERR] Provider "{provider}" either doesnt exist or isnt working', delete_after=config['delete_after_time'])
            await ctx.message.delete()
            bot.queue.put(f'[ERR] Command GPT: Provider "{provider}" either doesnt exist or isnt working')
            return

        await ctx.message.edit("Please wait, generating response...")

        try:
            response = await g4f.ChatCompletion.create_async(
                model=g4f.models.default,
                messages=[{"role": "user", "content": prompt}],
                provider=provider,
            )

            if len(response)>2000:
                await ctx.message.delete()
                chunks = await split_message(ctx, response)

                for chunk in chunks:
                    await ctx.send(chunk)
            else:
                await ctx.message.edit(response)
            bot.queue.put(f"[INFO] Command GPT successful")

        except Exception as e:
            await ctx.reply(f'[ERR] Exception while generating an response: {e}', delete_after=config['delete_after_time'])
            await ctx.message.delete()
            bot.queue.put(f'[ERR] Command GPT: Generating response: {e}')
            
    except Exception as e:
        await ctx.reply(f'[ERR]: {e}', delete_after=config['delete_after_time'])
        await ctx.message.delete()
        bot.queue.put(f'[ERR] Command GPT: {e}')


# soundboard free nitro real


@bot.command()
async def play(ctx, filename):
    bot.queue.put('[INFO] Play command called')

    print(ctx.voice_client)
    try:
        config_file, config_dir = modules.paths.get_config_file_dir()

        if not '/' in filename:
            bot.queue.put('[DEBUG] Play command: Using the sounds directory')
            found = False
            for file in os.listdir(os.path.join(config_dir, 'sounds')):
                if filename in file:
                    path = os.path.join(config_dir, 'sounds', file)
                    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(path))
                    found = True
                    break
            
            if not found:
                await ctx.reply(f'[ERR] File **"{filename}"** doesnt exist')
                bot.queue.put(f'[ERR] Play command: File "{filename}" doesnt exist')
                await ctx.message.delete()
                return               

        else:
            bot.queue.put('[DEBUG] Play command: Using path to file')
        
            if not os.path.exists(filename):
                await ctx.reply(f'[ERR] File **"{filename}"** doesnt exist')
                bot.queue.put(f'[ERR] Play command: File "{filename}" doesnt exist')
                await ctx.message.delete()
                return

            else:
                path = filename
                source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(path))
            
        bot.queue.put(f'[DEBUG] Play command: Playing sound {path}')


        ctx.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)

    except Exception as e:
        await ctx.reply(f'[ERR]: {e}')
        bot.queue.put(f'[ERR] Play command raised an exception: {e}')
        await ctx.message.delete()



def main(token, queue):
    global bot
    queue.put('[INFO] Logging in...')
    config, log = load_config()
    bot.queue = queue
    bot.command_prefix = config['prefix']
    bot.run(token)