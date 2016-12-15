import discord
from discord.ext import commands
import random

#It is also perfectly fine to replace "token" below with your actual token
#, in qoutation marks
import credentials
from credentials import token

import SREUinterface
from SREUinterface import getPlayerInfo

description = '''The EU Grandmaster Melee bot
Handles various utility functions'''
bot = commands.Bot(command_prefix='?', description=description)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(description='Print the basic smashranking.eu info about a player')
async def SR(*nameargs : str):
    name='-'.join(nameargs)
    result = getPlayerInfo(name.lower())
    if (result[0] == -1):
        await bot.say('Lookup failed, check that smashranking is up and that you typed the username correctly')
    else:
        await bot.say('{0[tag]}: EU rank is {0[eurank]}, country is {0[country]}, country rank is {0[country_rank]}, main is {0[main]}'.format(result[1]))

def obtainRoleFromName(name,server):
    toReturn=[role for role in server.roles if role.name == name]
    if (len(toReturn) != 1):
        print("Role selection error. 0 or more than 1 role found with name "+name)
        return None
    return toReturn[0]

@bot.command(description='Adds you to the notification group',pass_context=True)
async def notify(ctx):
	notifyRole=obtainRoleFromName('Notify',ctx.message.server)
	await bot.add_roles(ctx.message.author,notifyRole)
	await bot.reply('You will now be notified when the "Notify" tag is used')
	
@bot.command(description='Adds you to the notification group',pass_context=True)
async def mute(ctx):
	notifyRole=obtainRoleFromName('Notify',ctx.message.server)
	await bot.remove_roles(ctx.message.author,notifyRole)
	await bot.reply('You will no longer be notified when the "Notify" tag is used')
	
async def setRoles(member,jsonresponse,server):
    mainrole=obtainRoleFromName(jsonresponse['main'],server)
    nationalityrole=obtainRoleFromName(jsonresponse['country'],server)
    if (mainrole == None or nationalityrole == None):
        return False
    else:
        try:
            await bot.add_roles(member,mainrole,nationalityrole)
        except Exception:
            print("Error when setting roles:")
            print(sys.exc_info())
            return False
    print("Set roles from SR for "+member.name)
    return True

@bot.command(description='Sets your roles based on smashranking.eu',pass_context=True)
async def obtainroles(ctx):
    result = getPlayerInfo(ctx.message.author.name.replace(' ','-').lower())
    if (result[0] == -1):
        await bot.reply('Lookup failed, check that smashranking is up and that your username checks is the same as on smashranking')
        await bot.reply('Contact an admin if the problem persists')
    else:
        if (await setRoles(ctx.message.author,result[1],ctx.message.server)):
            await bot.reply('Your roles have been correctly setup from smashranking')
        else:
            await bot.reply('Failed to set your roles despite your username being correct, contact an admin')

@bot.event
async def on_member_join(member : discord.Member):
    await bot.send_message(member,'Welcome to the EU Grandmaster Melee server! The bot will now attempt to automatically obtain your country and main from smashranking.eu')
    result = getPlayerInfo(member.name.replace(' ','-').lower())
    if (result[0] == -1):
        await bot.send_message(member,'Failed to set your country and/or main. Contact an admin for assistance')
    else:
        if (await setRoles(member,result[1],member.server)):
            await bot.send_message(member,'Your country and main are now set! Contact an admin if the bot got it wrong')
        else:
            await bot.reply('Failed to set your roles despite your username being correct, contact an admin')

# @bot.group(pass_context=True)
# async def cool(ctx):
#     """Says if a user is cool.
#     In reality this just checks if a subcommand is being invoked.
#     """
#     if ctx.invoked_subcommand is None:
#         await bot.say('No, {0.subcommand_passed} is not cool'.format(ctx))

# @cool.command(name='bot')
# async def _bot():
#     """Is the bot cool?"""
#     await bot.say('Yes, the bot is cool.')

bot.run(token)

