import datetime
import discord
import importlib
import json
import os

from enum import StrEnum, auto
from dotenv import load_dotenv
from pathlib import Path
from discord.ext import tasks, commands

DEBUG_MODE = False

class Game(StrEnum):
    BALATRO = auto()

# Discord Data
load_dotenv()

debug_channel_id = 1279823725495062589
default_channel_id = 890271922301071451

channel = None  # assigned at on_ready

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Serialized data
save_file = os.path.join(os.path.dirname(__file__), "data\\main.json")

game = ""
week = 0
time = datetime.datetime.now().timestamp()
scores = {}


def save_data():
    with open(save_file, "w") as f:
        data = { 
            "game": game,
            "week": week,
            "time": time,
            "scores": scores,
        }
        f.write(json.dumps(data))

    if game:
        module = importlib.import_module(game)
        module.save_data()


def load_data():
    if not Path(save_file):
        print(f"Invalid file path: {save_file}")
        return
        
    with open(save_file) as f:
        f_data = f.read()
        if f_data == "": return
        data = json.loads(f_data)

    global game, week, time, scores
    game = data["game"]
    week = data["week"]
    time = data["time"]
    scores = {int(k):v for k,v in data["scores"].items()}

    if game:
        module = importlib.import_module(game)
        module.load_data()


def get_member(id: int) -> discord.Member:
    return channel.guild.get_member(int(id))


def get_scores(ctx) -> discord.Embed:
    embed = discord.Embed(
        title=f"{game.capitalize()}: Golden Goblet",
        description=f"Week {week}\n\u200B",
        color=discord.Color.blue()
    )

    names = []
    points = []
    for id, pts in scores.items():
        names.append(get_member(id).display_name)
        points.append(str(pts))

    embed.add_field(name="Players", value="\n".join(names))
    embed.add_field(name="Scores", value="\n".join(points))

    return embed


async def send_message(message: str, embed: discord.Embed = None):
    if not channel:
        print("Unknown channel ID!")
        
    await channel.send(message, embed=embed)


@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    
    global channel
    channel_id = debug_channel_id if DEBUG_MODE else default_channel_id
    channel = bot.get_channel(channel_id)

    if DEBUG_MODE:
        await send_message("Logged in!")
    
    load_data()
    await check_time.start()


@bot.check
async def check_for_channel(ctx) -> bool:
    if ctx.channel == channel:
        return True
    return False


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        return


@bot.command()
async def test(ctx):
    await send_message("Test successful!")


@bot.command(name="post")
async def debug_post(ctx):
    await new_goblet_day()


@bot.command(name="end")
async def end(ctx):
    global game, week, time, scores
    
    if not game:
        await send_message("No event currently running!")
        return
    
    if scores:
        wid = max(scores, key=scores.get)
        winner = get_member(wid).mention
        await send_message(f"Well done to everyone who participated!\n\nThe winner of the Golden Goblet is...{winner}!", get_scores(ctx))
    else:
        await send_message("Golden Goblet has concluded.")

    game = ""
    week = 0
    time = datetime.datetime.now().timestamp()
    scores = {}

    save_data()


@bot.command(name="new")
async def new_goblet(ctx, game_name: str):
    if not hasattr(Game, game_name.upper()):
        await send_message("Invalid game name!")

    global game, week, scores
    game = getattr(Game, game_name.upper())
    week = 0
    scores = {}
    
    await new_goblet_day()


@bot.command(name="win")
async def add_to_score(ctx, user: discord.Member):
    if user.id not in scores:
        scores[user.id] = 0

    scores[user.id] += 1

    await send_message(f"Congratulations {user.mention}! You've earned a point!")
    save_data()


@bot.command(aliases=["scores", "score"])
async def show_scores(ctx):
    if not game:
        await send_message("No event currently running!")
        return
    await send_message("", get_scores(ctx))


@tasks.loop(minutes=15)
async def check_time():
    if game and datetime.datetime.now().timestamp() > time:
        await new_goblet_day()


async def new_goblet_day():
    global game, week, time
    if not game:
        await send_message("No event currently running!")
    
    week += 1
    module = importlib.import_module(game)
    
    string, embed = module.get_new_challenge(week)
    await send_message(string, embed)
    
    time = (datetime.datetime.now() + datetime.timedelta(days=7)).timestamp()
    save_data()


if __name__ == "__main__":
    bot.run(os.getenv("DISCORD_TOKEN"))