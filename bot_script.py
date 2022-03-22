from discord import ChannelType
from discord.ext import commands
import requests
import json

## read token
TOKEN = None
for line in open(".env"):
    if line.startswith("BOT_TOKEN"):
        TOKEN = line.strip().split("=")[1]
if TOKEN is None:
    raise RuntimeError("Could not read bot token from .env file.")

RED_CATEGORY = "RED"
BLUE_CATEGORY = "BLUE"

BASE_URL = 'http://localhost:8000/bot/'
NEW_GAME_PATH = "new_game/"
GET_ROUND_PATH = "get_round"
NEXT_TURN_PATH = "next_turn/"
GET_MESSAGES_PATH = "get_messages"
POST_MESSAGE_PATH = "send_message/"

description = '''Dispatch bot for IKS'''
bot = commands.Bot(command_prefix='!', description=description)
turn = 1

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}


def get_url(url_function, id=None, filter=None):
    """ general function get to read"""
    this_url = BASE_URL + url_function
    if id is not None:
        this_url += '/' + str(id)
    response = requests.get(this_url, params=filter, headers=headers)
    response.raise_for_status()
    return response.json()


def patch_url(url_function, id=None, data=None):
    """ general function put to update"""
    url = BASE_URL + url_function
    if id:
        url += str(id)
    if data:
        data = json.dumps(data)
    response = requests.patch(url, data=data, headers=headers)
    return response.json()


def post_url(url_function, data={}):
    """ general function post to create"""
    url = BASE_URL + url_function
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return response.json()


def getChannelByName(name):
    srv = bot.guilds[0]  # TODO make generic
    for chnl in srv.channels:
        if chnl.name == name:
            return chnl
    return None


async def deliver(message):
    dispatch_text = "Dispatch from %s:\n>>> %s" % (message["sender"], message["text"])
    channel = getChannelByName(message["channelName"])
    await channel.send(dispatch_text)


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def hello(ctx):
    """Says world"""
    await ctx.send("Hello I am the Disptach Bot")


@bot.command()
async def dispatch(ctx, message: str):
    """recieve a disptach from a player"""
    try:
        data = {
            "text": ctx.message.content.split("!dispatch", 1)[1],
            "sender": ctx.message.author.name
        }
        post_url(POST_MESSAGE_PATH, data)
        await ctx.send("Dispatch was send")
    except Exception as e:
        await ctx.send("There was an error sending your dispatch:%s" % str(e)[:1000])


@bot.command()
async def get_round(ctx):
    res = get_url("get_round")
    await ctx.send("This is round " + str(res['turn']))


@bot.command()
async def next_turn(ctx):
    """Tell the server to avance the turn by one"""
    try:
        res = patch_url(NEXT_TURN_PATH)
        print(res)
        await ctx.send("Next turn started. This is turn {}, time is {}".format(res["turn"], res["current_time"]))
    except Exception as e:
        await ctx.send("There was an error advancing the turn:%s" % str(e)[:1000])
        raise
    try:
        messages = get_url(GET_MESSAGES_PATH)
        await ctx.send("Received %i messages from the server" % len(messages))
    except Exception as e:
        await ctx.send("There was an error receiving messages:%s" % str(e)[:1000])
        raise
    try:
        for message in messages:
            await deliver(message)
    except Exception as e:
        await ctx.send("There was an error delivering messages:%s" % str(e)[:1000])
        raise


@bot.command()
async def start_game(ctx, name):
    """start a new game"""
    blue = {}
    red = {}
    for entry in ctx.guild.channels:
        if entry.type == ChannelType.category:
            if entry.name == RED_CATEGORY:
                for channel in entry.text_channels:
                    red[channel.name] = channel.id
            if entry.name == BLUE_CATEGORY:
                for channel in entry.text_channels:
                    blue[channel.name] = channel.id

    print(red)
    print(blue)
    data = {
        "name_channels": list(blue.keys()) + list(red.keys()),
        "name_game": name
    }
    try:
        res = post_url(NEW_GAME_PATH, data)
        await ctx.send("Game created\nName: %s\nTime is now %s\n%i Blue channels\n%i Red channels" % (
        res["name"], res["start_time"], len(blue), len(red)))
    except Exception as e:
        await ctx.send("There was an error creating the game:%s" % str(e)[:1000])
        raise


@bot.command()
async def dummy_start_game(ctx, game_name: str):
    data = {"name_channels": ["channel1", "channel2", "channel3"],
            "name_game": game_name}
    res = post_url("new_game/", data)
    await ctx.send("A new game " + res["name"] + " has started\n Time is now " + res['start_time'])


# @bot.event
# async def on_message(message):
#
#    print(message)
#    print(message.content)
#    await bot.process_commands(message)
#    #await message.send(message.content)

bot.run(TOKEN)
