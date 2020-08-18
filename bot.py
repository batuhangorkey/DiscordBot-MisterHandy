import os
import random
import discord
import pymysql

from minigame import Minigame
from youtube_bot import Music
# from kaiser import Kaiser
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
HOST = os.getenv('HOST')
USER_ID = os.getenv('USER_ID')
PASSWORD = os.getenv('PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')

client = discord.Client()
bot = commands.Bot(command_prefix='!')

adj = {
    8: 'Efsane',
    7: 'İnanılmaz',
    6: 'Şahane',
    5: 'Muhteşem',
    4: 'Harika',
    3: 'Baya iyi',
    2: 'İyi',
    1: 'Eh',
    0: 'Düz',
    -1: 'Dandik',
    -2: 'Kötü',
    -3: 'Rezalet',
    -4: 'Felaket'
}


def fetch_user_tables():
    user_table = {}
    kaiser_points = {}

    conn = pymysql.connect(str(HOST),
                           str(USER_ID),
                           str(PASSWORD),
                           str(DATABASE_NAME))
    with conn.cursor() as cursor:
        cursor.execute('SELECT VERSION()')
        data = cursor.fetchone()
        print(f'Database version: {data[0]}')
        cursor.execute("SELECT * FROM main")
        data = cursor.fetchall()
    conn.close()

    for _, b, k in data:
        user_table[int(_)] = int(b)
        # kaiser_points[int(_)] = int(k)
    return user_table, kaiser_points


@bot.event
async def on_ready():
    print('{0.name} with id: {0.id} has connected to Discord!'.format(bot.user))
    async for guild in bot.fetch_guilds():
        print('Operating on {} with id: {}'.format(guild.name, guild.id))

    channel = bot.get_channel(710179799792091227)
    await channel.send('Buradayım')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,
                                                        name='wasteland with sensors offline'))
    bot.add_cog(Minigame(bot, user_table=fetch_user_tables()[0]))
    # bot.add_cog(Kaiser(bot, kaiser_points=fetch_user_tables()[1]))
    bot.add_cog(Music(bot))


@bot.command(help='Roll dice.')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))


@bot.command(help='FATE zarı atar')
async def zar(ctx, modifier: int = 0):
    dice = [
        random.choice([-1, -1, 0, 0, 1, 1])
        for _ in range(4)
    ]
    _sum = sum(dice) + modifier
    await ctx.send(', '.join(map(str, dice)) + ' + {} = {}   **{}**'.format(modifier, _sum, adj[_sum]))


@bot.command(help='Tries to purge max 50 messages by the bot.')
async def del_bot(ctx):
    def is_me(m):
        return m.author == bot.user

    deleted = await ctx.channel.purge(limit=50, check=is_me, bulk=False)
    await ctx.send(f'Deleted {len(deleted)} message(s).')


@bot.command(help='Tries to purge messages. Max limit 50')
async def delete(ctx, limit: int = None):
    if limit is None:
        limit = 50
    if limit > 50:
        limit = 50
    deleted = await ctx.channel.purge(limit=limit)
    await ctx.send(f'Deleted {len(deleted)} message(s).')


@bot.command(help='Refreshes music cog.')
async def refresh(ctx):
    async with ctx.typing():
        bot.remove_cog('Music')
        bot.add_cog(Music(bot))
        await ctx.send('Oynatıcı baştan yüklendi.')

bot.run(TOKEN)
