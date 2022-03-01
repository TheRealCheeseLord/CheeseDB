from asyncio.windows_events import NULL
from base64 import decode
from dis import disco
from distutils import command
from distutils.util import change_root
from doctest import debug_script
from email import message
from http import client
import os
from pickle import NONE
from posixpath import split
from pydoc import describe
from socket import timeout
from turtle import update
import typing
from xml.dom import UserDataHandler
from discord import Client, Intents, Embed
from discord.ext import commands
import discord
from dotenv import load_dotenv
import asyncio
import json
import hashlib
import binascii
from discord_slash import SlashCommand, SlashContext
import requests
from discord.abc import GuildChannel, PrivateChannel, Snowflake
import random
import string
import re
import shutil


load_dotenv(".env")
TOKEN = os.getenv("TOKEN")
bot = commands.Bot(command_prefix='.', help_command=None)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command(name='help')
async def help(ctx):
    embed = discord.Embed(title="Commands", description='**.help** - Shows this message\n**.create** - Create a CheeseDB account\n**.login** - Login to your CheeseDB account\n**.logout** - Logout from your CheesDB account\n**.transfer <old_username> <recovery_key>** - Transfer your account to a new one\n**.create_txt <txt_name> "<content>"** - Creates a .txt file\n**.ls** - List contents of current directory\n**.mkdir <name>** -create a directory\n**.cd <folder_path>** - Change directory to folder path. Do ".cd / " to switch to home directory\n**.rm <file_name>** - Removes specified file\n**.rmdir <folder_name>** - Removes specified directory\n**.cat <file_name>** - show content of text file\n**.cp <file_name> __<destination>__** - copy file to destination\n**.mv <file_name> __<destination>__** - move file to destination\n**.rename <file_name> <new_name>** - rename file to new name\n**.download <file_name>** - download file\n**.upload <file_name>** - upload file to database\n**.send <file_name> [User#1234]** - send file to user\n**.block [User#1234]** - Block a user from sending you files\n**.unblock [User#1234]** - Unblock a user\n\n<Test> - required\n__<Test>__ - not required\n[User#1234] - Username\n\nFor support visit **-** or email **support.cheesedb@gmail.com**', color=0xebca26)
    await ctx.reply(embed = embed)

@bot.command(name='create', help='Creates a CheeseDB account which directly links to your discord user')
async def create(ctx):
    if ctx.author == bot.user:
        return

    input_json = open('users.json')
    json_array = json.load(input_json)

    if not str(ctx.author) in json_array:
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')        
        recovery_code = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(256))
        hashed_code = hashlib.pbkdf2_hmac('sha512', str(recovery_code).encode('utf-8'), salt, 200000)
        hashed_code = binascii.hexlify(hashed_code)     

        decoded_hash = hashed_code.decode('ascii')
        decoded_salt = salt.decode('ascii')

        embed = discord.Embed(title="Successfully created account", description="__You have now created a CheeseDB account.__ This account is cross-linked to every server this bot is in. That means you can login in any server the bot is in. **BUT REMEMBER ALWAYS LOG OUT AFTER YOU ARE DONE!** Or else people could possibly interact with your bot. \n If you happen to lose your account or your discord tag gets changed because of Nitro you will have to use the recovery key **(SAVE KEY AND USERNAME)** to link your account to a different user, without it theres way **no** to get the account back. \n \n __Username:__ **" + str(ctx.author) + "**" + "\n \n __Recovery Code:__ **" + str(recovery_code) + "**", color=0xebca26 )
        await ctx.author.send(embed=embed)

        username = str(ctx.author)
        folder_name = re.sub('[!@,;.:?\\}=)({/&%$\"\'+*~^<>|#]', '', username)
        path = "Databases/" + str(folder_name)
        os.mkdir(path)
        os.mkdir(path + "/Mail")

        update = {str(ctx.author): {"key": str(decoded_hash), "salt": str(decoded_salt), "folder_path": str(path), "current_directory": str(path), "mail_folder": str(path) + "/Mail", "blocked_users": []}}

        json_array.update(update)

        with open("users.json", "w") as jsonFile:
            json.dump(json_array, jsonFile, sort_keys=True, indent=4)
    else: 
        embed = discord.Embed(title = "Account already exists", description="You already have a CheeseDB account", color=0xebca26)
        await ctx.author.send(embed=embed)

@bot.command(name='login', help="Logs you into your CheeseDB account")
async def login(ctx):
    if ctx.author == bot.user:
        return

    usernames_input = open('logged-usernames.json')
    usernames_array = json.load(usernames_input)    
    
    if str(ctx.author) in usernames_array:
        embed = discord.Embed(title="Already logged in", description='You are already logged into an account somewhere', color=0xebca26)
        await ctx.reply(embed=embed)
    else:
        input_json = open('users.json')
        json_array = json.load(input_json)

        if str(ctx.author) in json_array:

            # creates a role with permission to interact with textchannel
            guild = ctx.guild
            autorize_role = await guild.create_role(name=str(ctx.author))
            user = ctx.message.author        
            role = discord.utils.get(ctx.guild.roles, name=str(ctx.author))
            await user.add_roles(role)

            # creates a private text channel to interact with your database
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True),
                autorize_role: discord.PermissionOverwrite(read_messages=True)
            }
            await guild.create_text_channel(str(ctx.author), overwrites=overwrites)

            # adds your discord username and account username to "logged-usernames.json"

            logged_input = open('logged-usernames.json')
            logged_users = json.load(logged_input)

            logged_users["Users"].append(str(ctx.author))

            with open("logged-usernames.json", "w") as jsonFile:
                json.dump(logged_users, jsonFile, sort_keys=True, indent=4)

            embed = discord.Embed(title='Welcome Back', description=f'Welcome back {ctx.author}', color=0xebca26)
            await ctx.reply(embed=embed)


@bot.command(name = 'logout', help='Logout from your CheeseDB account')
async def logout(ctx):
    if ctx.author == bot.user:
        return
    
    input_file = open ('logged-usernames.json')
    json_array = json.load(input_file)

    username = str(ctx.author)
    username_lower = username.lower()
    channel_name = re.sub('[!@,;.:?\\}=)({/&%$\"\'+*~^<>|#]', '', username_lower)
    channel = discord.utils.get(ctx.guild.channels, name=str(channel_name))
    role = discord.utils.get(ctx.guild.roles, name=username)

    if (role in ctx.author.roles):
        try:
            await role.delete()
            await channel.delete()
            json_array["Users"].remove(username)

            with open("logged-usernames.json", "w") as jsonFile:
                json.dump(json_array, jsonFile, sort_keys=True, indent=4)

        except discord.Forbidden:
            embed = discord.Embed(title='Missing permissions', description='The bot is missing permissions to execute this command', color=0xebca26)
            await ctx.repy(embed=embed)
    else: 
        embed = discord.Embed(title='Currently not logged in', description='You aren\'t currently logged in', color=0xebca26)
        await ctx.reply(embed=embed)

@bot.command(name='transfer', help='Transfer your CheeseDB account to a different user using the recovery code. Syntax: .transfer *username* *recovery_key*')
async def transfer(ctx, old_username, recovery_code):
    if ctx.author == bot.user:
        return

    users_input = open('users.json')
    users_array = json.load(users_input)
    username = ctx.author
    salt = users_array[str(old_username)]["salt"]
    hash = hashlib.pbkdf2_hmac('sha512', str(recovery_code).encode('utf-8'), str(salt).encode('ascii'), 200000)
    hash = binascii.hexlify(hash).decode('ascii')
    user_hash = users_array[str(old_username)]["key"]
    user_salt = users_array[str(old_username)]["salt"]
    path = users_array[str(old_username)]["folder_path"]
    blocked_users = users_array[str(old_username)]["blocked_users"]

    if hash in users_array[str(old_username)]["key"]:

        users_input = open('users.json')
        users_array = json.load(users_input)        
        update = {str(username): {"key": user_hash, "salt": user_salt, "folder_path": str(path), "current_directory": str(path), "mail_folder": str(path) + "/Mail", "blocked_users": blocked_users}}

        users_array.update(update)
        del users_array[old_username]

        with open("users.json", "w") as jsonFile:
            json.dump(users_array, jsonFile, sort_keys=True, indent=4)

        embed = discord.Embed(title='Account successfully transfered', description=f'Account successfully transfered \n New account name: {str(ctx.author)}', color=0xebca26)
        await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(title='Matchup Error', description='Username and/or Recovery keys don\'t match up', color=0xebca26)
        await ctx.reply(embed=embed)

@bot.command(name='create_txt', help='Create a .txt file in your database')
async def create_txt(ctx, file_name, text):
    if ctx.author == bot.user:
        return
    
    usernames_input = open('logged-usernames.json')
    usernames_array = json.load(usernames_input)    
    
    users_input = open('users.json')
    users_array = json.load(users_input)

    current_directory = users_array[str(ctx.author)]["current_directory"] 

    if str(ctx.author) in usernames_array["Users"]:
        with open(str(current_directory) + "/" + str(file_name) + ".txt", 'w') as f:
            f.write(str(text))
        embed = discord.Embed(title='Created File', description='Successfully created text file', color=0xebca26)
        await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(title='Not logged in', description='You aren\'t logged in', color=0xebca26)
        await ctx.reply(embed=embed)

@bot.command(name='ls', help='List the contents of your current directory')
async def ls(ctx):
    if ctx.author == bot.user:
        return
    
    usernames_input = open('logged-usernames.json')
    usernames_array = json.load(usernames_input)

    users_file = open ('users.json')
    users_array = json.load(users_file)    

    if str(ctx.author) in usernames_array["Users"]:
        current_directory = users_array[str(ctx.author)]["current_directory"]
        listed = os.listdir(current_directory)
        list = ""
        for x in listed:
            list += x + "\n"

        embed = discord.Embed(title='List Directory', description=str(list), color=0xebca26)
        await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(title='Not logged in', description='You aren\'t logged in', color=0xebca26)
        await ctx.reply(embed=embed)

@bot.command(name='mkdir', help="Creates a directory")
async def mkdir(ctx, directory_name):
    if ctx.author == bot.user:
        return
    
    usernames_input = open('logged-usernames.json')
    usernames_array = json.load(usernames_input)

    users_file = open('users.json')
    users_array = json.load(users_file)

    if str(ctx.author) in usernames_array["Users"]:
        current_directory = users_array[str(ctx.author)]["current_directory"]
        os.mkdir(current_directory + "/" + directory_name)
        embed = discord.Embed(title='Create Directory', description='Successfully created directory named: **' + directory_name + "**", color=0xebca26)
        await ctx.reply(embed = embed)
    else:
        embed = discord.Embed(title='Not logged in', description='You aren\'t logged in', color=0xebca26)
        await ctx.reply(embed=embed)        

@bot.command(name='cd')
async def cd(ctx, directory_name):
    if ctx.author == bot.user:
        return

    usernames_input = open('logged-usernames.json')
    usernames_array = json.load(usernames_input)

    users_file = open('users.json')
    users_array = json.load(users_file)

    if str(ctx.author) in usernames_array["Users"]:
        current_directory = users_array[str(ctx.author)]["current_directory"]
        if directory_name == "/":
            key = users_array[str(ctx.author)]["key"]
            salt = users_array[str(ctx.author)]["salt"]
            folder_path = users_array[str(ctx.author)]["current_directory"]
            username = str(ctx.author)
            folder_name = re.sub('[!@,;.:?\\}=)({/&%$\"\'+*~^<>|#]', '', username)
            home_directory = "Databases/" + str(folder_name)

            update = {str(ctx.author): {"key": key, "salt": salt, "folder_path": home_directory, "current_directory": str(home_directory)}}

            users_array.update(update)

            with open("users.json", "w") as jsonFile:
                json.dump(users_array, jsonFile, sort_keys=True, indent=4)

            embed = discord.Embed(title='Changed Directory', description='Changed Directory to **home directory**', color=0xebca26)
            await ctx.reply(embed=embed)
        else:
            key = users_array[str(ctx.author)]["key"]
            salt = users_array[str(ctx.author)]["salt"]
            folder_path = users_array[str(ctx.author)]["current_directory"]
            username = str(ctx.author)
            folder_name = re.sub('[!@,;.:?\\}=)({/&%$\"\'+*~^<>|#]', '', username)

            update = {str(ctx.author): {"key": key, "salt": salt, "folder_path": folder_path, "current_directory": str(current_directory + "/" + str(directory_name))}}

            users_array.update(update)

            with open("users.json", "w") as jsonFile:
                json.dump(users_array, jsonFile, sort_keys=True, indent=4)

            embed = discord.Embed(title='Changed Directory', description='Changed Directory to **' + str(directory_name) + '** directory', color=0xebca26)
            await ctx.reply(embed=embed)            
    else:
        embed = discord.Embed(title='Not logged in', description='You aren\'t logged in', color=0xebca26)
        await ctx.reply(embed=embed)

@bot.command(name='rm')
async def rm(ctx, file_name):
    if ctx.author == bot.user:
        return
    
    users_file = open('users.json')
    users_array = json.load(users_file)

    current_directory = users_array[str(ctx.author)]["current_directory"]

    os.remove(str(current_directory) + "/" + file_name)

    embed = discord.Embed(title='Removed File', description='Successfully removed **' + str(file_name) + "**", color=0xebca26)
    await ctx.reply(embed=embed)

@bot.command(name='rmdir')
async def rm(ctx, folder_name):
    if ctx.author == bot.user:
        return

    users_file = open('users.json')
    users_array = json.load(users_file)

    current_directory = users_array[str(ctx.author)]["current_directory"]

    shutil.rmtree(str(current_directory) + "/" + folder_name)

    embed = discord.Embed(title='Removed File', description='Successfully removed **' + str(folder_name) + '** directory', color=0xebca26)
    await ctx.reply(embed = embed)

@bot.command(name='cat')
async def cat(ctx, file_name):
    if ctx.author == bot.user:
        return

    users_file = open('users.json')
    users_array = json.load(users_file)

    current_directory = users_array[str(ctx.author)]["current_directory"]

    with open(str(current_directory) + "/" + str(file_name), "r") as textFile:
        content = textFile.read()
    
    embed = discord.Embed(title='Contents', description=str(content), color=0xebca26)
    await ctx.reply(embed=embed)

@bot.command(name='cp')
async def cat(ctx, file_name, destination=None):
    if ctx.author == bot.user:
        return

    users_file = open('users.json')
    users_array = json.load(users_file)

    current_directory = users_array[str(ctx.author)]["current_directory"]
    folder_path = users_array[str(ctx.author)]["folder_path"]

    if destination != None:
        if str(destination) == "/":
            shutil.copy2(str(current_directory) + "/" + str(file_name), str(folder_path) + "/copy_" + str(file_name))
            embed = discord.Embed(title='Copied File', description='Successfully copied **' + str(file_name) + '** to **home directory**', color=0xebca26)
            await ctx.reply(embed=embed)
        elif str(destination).startswith("/"):
            shutil.copy2(str(current_directory) + "/" + str(file_name), str(folder_path) + str(destination) + "/copy_" + str(file_name))
            embed = discord.Embed(title='Copied File', description='Successfully copied **' + str(file_name) + '** to **' + str(folder_path) + str(destination) + '**', color=0xebca26)
            await ctx.reply(embed=embed)
        else:
            shutil.copy2(str(current_directory) + "/" + str(file_name), str(current_directory) + "/" + str(destination) + "/copy_" + str(file_name))
            embed = discord.Embed(title='Copied File', description='Successfully copied **' + str(file_name) + '** to **' + str(destination) + '**', color=0xebca26)
            await ctx.reply(embed=embed)
    else:
        shutil.copy2(str(current_directory) + "/" + str(file_name), str(current_directory) + "/copy_" + str(file_name))
        embed = discord.Embed(title='Copied File', description='Successfully copied **' + str(file_name) + '**', color=0xebca26)
        await ctx.reply(embed=embed)

@bot.command(name='mv')
async def mv(ctx, file_name, destination=None):
    if ctx.author == bot.user:
        return

    users_file = open('users.json')
    users_array = json.load(users_file)

    current_directory = users_array[str(ctx.author)]["current_directory"]
    folder_path = users_array[str(ctx.author)]["folder_path"]

    if destination != None:
        if str(destination) == "/":
            shutil.move(str(current_directory) + "/" + str(file_name), str(folder_path) + "/copy_" + str(file_name))
            embed = discord.Embed(title='Copied File', description='Successfully moved **' + str(file_name) + '** to **home directory**', color=0xebca26)
            await ctx.reply(embed=embed)
        elif str(destination).startswith("/"):
            shutil.move(str(current_directory) + "/" + str(file_name), str(folder_path) + str(destination) + "/copy_" + str(file_name))
            embed = discord.Embed(title='Copied File', description='Successfully moved **' + str(file_name) + '** to **' + str(folder_path) + str(destination) + '**', color=0xebca26)
            await ctx.reply(embed=embed)
        else:
            shutil.move(str(current_directory) + "/" + str(file_name), str(current_directory) + "/" + str(destination) + "/copy_" + str(file_name))
            embed = discord.Embed(title='Copied File', description='Successfully moved **' + str(file_name) + '** to **' + str(destination) + '**', color=0xebca26)
            await ctx.reply(embed=embed)
    else:
        shutil.move(str(current_directory) + "/" + str(file_name), str(current_directory) + "/copy_" + str(file_name))
        embed = discord.Embed(title='Copied File', description='Successfully moved **' + str(file_name) + '**', color=0xebca26)
        await ctx.reply(embed=embed)

@bot.command(name='rename')
async def rename(ctx, file_name, new_name):
    if ctx.author == bot.user:
        return

    users_file = open('users.json')
    users_array = json.load(users_file)

    current_directory = users_array[str(ctx.author)]["current_directory"]
    folder_path = users_array[str(ctx.author)]["folder_path"]

    if str(file_name) == "Mail" and str(current_directory) == str(folder_path):
        embed = discord.Embed(title='Can\'t rename Mail folder', description='You can\'t rename the Mail Folder', color=0xebca26)
        ctx.reply(embed=embed)
    else:
        os.rename(str(current_directory) + "/" + str(file_name), str(current_directory) + "/" + str(new_name))
        embed = discord.Embed(title='Renamed File', description='Successfully renamed file **' + str(file_name) + "** to **" + str(new_name) + "**", color=0xebca26)
        await ctx.reply(embed=embed)

@bot.command(name='download')
async def download(ctx, filename):
    if ctx.author == bot.user:
        return

    users_file = open('users.json')
    users_array = json.load(users_file)

    current_directory = users_array[str(ctx.author)]["current_directory"]
    folder_path = users_array[str(ctx.author)]["folder_path"]

    file = discord.File(str(current_directory) + "/" + str(filename))

    embed = discord.Embed(title='File Download', description= "**" + str(filename) + "**", color=0xebca26)
    await ctx.reply(embed=embed, file=file)

@bot.command(name='upload')
async def upload(ctx, file_name):
    if ctx.author == bot.user:
        return

    users_file = open('users.json')
    users_array = json.load(users_file)

    current_directory = users_array[str(ctx.author)]["current_directory"]

    attachment = ctx.message.attachments[0]

    await attachment.save(str(current_directory) + "/" + file_name)
    embed = discord.Embed(title='File Upload', description=f'Successfully uploaded **{file_name}**', color=0xebca26)
    await ctx.reply(embed = embed)

@bot.command(name='send')
async def send(ctx, file_name, user_input):
    if ctx.author == bot.user:
        return

    users_file = open('users.json')
    users_array = json.load(users_file)

    current_diretory = users_array[str(ctx.author)]["current_directory"]

    user = re.sub('[!@,;.:?\\}=)({/&%$\"\'+*~^<>|#]', '', user_input)

    pathExist = os.path.exists("Databases/" + str(user))

    if pathExist == True:
        if ctx.author in users_array[str(user_input)]["blocked_users"]:
            embed = discord.Embed(title='Blocked', description='**' + str(user_input) +'** blocked you from sending them files', color=0xebca26)
            await ctx.reply(embed=embed)
        else:
            shutil.copy2(str(current_diretory) + "/" + str(ctx.author) + "_" + str(file_name), "Databases/" + str(user) + "/Mail")
            embed = discord.Embed(title='Sent File', description='File **' + str(file_name) + '** successfully sent to **' + str(user_input) + '**', color=0xebca26)
            await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(title='User not Found', description='Users not Found, check your spelling and if User exists', color=0xebca26)
        await ctx.reply(embed=embed) 

@bot.command(name='block')
async def block(ctx, user_input):
    if ctx.author == bot.user:
        return

    users_file = open('users.json')
    users_array = json.load(users_file)

    username = str(ctx.author)

    user = re.sub('[!@,;.:?\\}=)({/&%$\"\'+*~^<>|#]', '', user_input)

    pathExist = os.path.exists("Databases/" + str(user))    

    if pathExist == True:
        users_array[username]["blocked_users"].append(user_input)

        with open("users.json", "w") as jsonFile:
            json.dump(users_array, jsonFile, sort_keys=True, indent=4)

        embed = discord.Embed(title='Blocked User', description='Successfully blocked User **' + user_input + '**', color=0xebca26)
        await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(title='User not Found', description='Users not Found, check your spelling and if User exists', color=0xebca26)
        await ctx.reply(embed=embed)

@bot.command(name='unblock')
async def unblock(ctx, user_input):
    if ctx.author == bot.user:
        return

    users_file = open('users.json')
    users_array = json.load(users_file)

    username = str(ctx.author)

    if str(user_input) in users_array[username]["blocked_users"]:
        users_array[username]["blocked_users"].remove(str(user_input))

        with open("users.json", "w") as jsonFile:
            json.dump(users_array, jsonFile, sort_keys=True, indent=4)

        embed = discord.Embed(title='Unblocked User', description='Successfully unblocked User **' + user_input + '**', color=0xebca26)
        await ctx.reply(embed=embed)        
    else:
        embed = discord.Embed(title='User not Found', description='Users not Found, check your spelling and if User exists', color=0xebca26)
        await ctx.reply(embed=embed)

bot.run(TOKEN)