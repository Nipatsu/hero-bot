from discord.ext import commands
import os
import datetime
import psutil
import json
import random
import discord
import typing

from keep_alive import keep_alive

keep_alive()

token = BOT TOKEN
cooldowns = {}

start_time = datetime.datetime.now()

intents = discord.Intents.all()
intents.members = True
intents.messages = True
client = commands.Bot(command_prefix='!', intents=intents)



def load_data():
    try:
        with open('economy_data.json', 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return data



# Save data to file
def save_data(data):
    with open('economy_data.json', 'w') as file:
        json.dump(data, file)


@client.event
async def on_ready():
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="HERO'S LOUNGE"
    )
    await client.change_presence(activity=activity)
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@client.command()
async def ping(ctx):
    uptime = datetime.datetime.now() - start_time
    uptime_str = str(uptime).split('.')[0]

    server_count = len(client.guilds)

    memory_usage = psutil.Process().memory_full_info().rss / 1024 ** 2

    embed = discord.Embed(title='Bot Status', color=discord.Color.green())
    embed.add_field(name='Uptime', value=uptime_str)
    embed.add_field(name='Servers', value=str(server_count))
    embed.add_field(name='Memory Usage', value=f'{memory_usage:.2f} MB')
    await ctx.send(embed=embed)


@client.command()
@commands.cooldown(1, 180, commands.BucketType.user)
async def work(ctx):
    user_id = str(ctx.author.id)
    data = load_data()

    if user_id in data:
        job = data[user_id]['job']
        earnings = random.randint(100, 500)
        data[user_id]['pocket'] += earnings
        save_data(data)

        embed = discord.Embed(
            title='Work',
            description=f'You worked as {job} and earned {earnings} Hero money<:HeroCoin:1125125643437342801>!',
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title='Work',
            description='You need to choose a job first with the `choose` command.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

@work.error
async def work_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        cooldown = round(error.retry_after)
        embed = discord.Embed(
            title='Work',
            description=f'You are on cooldown. Please try again in {cooldown} seconds.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title='Work',
            description='An error occurred while executing the command.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)




@client.command()
async def choose(ctx, *, job: str = None):
    available_jobs = ['Pit Crew', 'Moderator', 'Heros Chef']
    user_id = str(ctx.author.id)
    data = load_data()

    if user_id not in data:
        if job and job in available_jobs:
            data[user_id] = {'pocket': 0, 'bank': 0, 'job': job}
            save_data(data)

            embed = discord.Embed(title='Job Selection', description=f'You have chosen the job: {job}', color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title='Job Selection', description='Invalid job. Choose from available jobs which are: `Pit Crew` `Moderator` `Heros Chef`.', color=discord.Color.red())
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title='Job Selection', description='You have already chosen a job.', color=discord.Color.red())
        await ctx.send(embed=embed)




@client.command()
async def deposit(ctx, amount: typing.Union[int, str]):
    user_id = str(ctx.author.id)
    data = load_data()

    if user_id in data:
        pocket_balance = data[user_id]['pocket']

        if isinstance(amount, str) and amount.lower() == 'all':
            amount = pocket_balance

        if isinstance(amount, int) and amount > 0 and amount <= pocket_balance:
            bank_balance = data[user_id].get('bank', 0)
            bank_balance += amount
            data[user_id]['bank'] = bank_balance
            data[user_id]['pocket'] -= amount
            save_data(data)

            embed = discord.Embed(
                title='Deposit',
                description=f'You have deposited {amount} into your bank account.',
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title='Deposit',
                description='Invalid amount. Please enter a valid positive amount or "all" to deposit all your money.',
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    else:
        embed = discord.Embed(
            title='Deposit',
            description='You need to choose a job first with the `choose` command.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)




@client.command()
async def balance(ctx):
    user_id = str(ctx.author.id)
    data = load_data()

    if user_id in data:
        pocket_balance = data[user_id]['pocket']
        bank_balance = data[user_id].get('bank', 0)

        embed = discord.Embed(title='Balance', color=discord.Color.blue())
        embed.add_field(name='<:HeroCoin:1125125643437342801> Pocket Balance', value=f'{pocket_balance} money')
        embed.add_field(name='<:HeroCoin:1125125643437342801> Bank Balance', value=f'{bank_balance} money')
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title='Balance', description='You need to choose a job first with the `choose` command.', color=discord.Color.red())
        await ctx.send(embed=embed)


client.run(token)
