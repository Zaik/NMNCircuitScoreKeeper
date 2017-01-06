import discord
from discord.ext import commands
import random
import sys
import json

#It is also perfectly fine to replace "token" below with your actual token
#, in qoutation marks
import credentials
from credentials import token

import SREUinterface
from SREUinterface import getPlayerInfo
from SREUinterface import getPlayerHighestSlug

description = '''The EU Grandmaster Melee bot
Handles various utility functions'''
LARGE_NUMBER=9999999
bot = commands.Bot(command_prefix='?', description=description)

#Binding from tag to list, in date order, of post-IDs
taggedPosts = {}

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
        #Try to find other slugs
        secondslug=getPlayerHighestSlug(name)
        if (secondslug[0] == 0):
            result = getPlayerInfo(secondslug[1])
            name=secondslug[1]
    if (result[0] == 0):
        await bot.say('{0[tag]}: EU rank is {0[eurank]}, country is {0[country]}, country rank is {0[country_rank]}, main is {0[main]}\nData consolidated from http://smashranking.eu/smashers/{1}'.format(result[1],name))
    else:
        await bot.say('Lookup failed, check that smashranking is up and that you typed the username correctly')

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
	await bot.send_message(ctx.message.author,'You will now be notified when the "Notify" tag is used')

@bot.command(description='Adds you to the notification group',pass_context=True)
async def Notify(ctx):
	notifyRole=obtainRoleFromName('Notify',ctx.message.server)
	await bot.add_roles(ctx.message.author,notifyRole)
	await bot.send_message(ctx.message.author,'You will now be notified when the "Notify" tag is used')
	
@bot.command(description='Adds you to the notification group',pass_context=True)
async def mute(ctx):
	notifyRole=obtainRoleFromName('Notify',ctx.message.server)
	await bot.remove_roles(ctx.message.author,notifyRole)
	await bot.send_message(ctx.message.author,'You will no longer be notified when the "Notify" tag is used')
	
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
        await bot.reply('Lookup failed, check that smashranking is up and that your username is the same as on smashranking')
        await bot.reply('Contact an admin if the problem persists')
    else:
        if (await setRoles(ctx.message.author,result[1],ctx.message.server)):
            await bot.reply('Your roles have been correctly setup from smashranking')
        else:
            await bot.reply('Failed to set your roles despite your username being correct, contact an admin')
			
@bot.command(description='Format: ?obtainroles <MENTION> <ID>\nSets someones roles based on a particular smashranking.eu ID. MOD ONLY',pass_context=True)
async def setroles(ctx, membertoset : discord.Member, IDtoUse : str):
    #check privileges of author
    if (not ctx.message.author.server_permissions.manage_roles):
        await bot.reply('You cannot use this command.')
        return
    result = getPlayerInfo(IDtoUse.lower())
    if (result[0] == -1):
        await bot.reply('Lookup failed, check that smashranking is up and that the ID used exists on smashranking (you can try "id-<nationality abbreviation>"')
        await bot.reply('Contact an admin if the problem persists')
    else:
        if (await setRoles(membertoset,result[1],ctx.message.server)):
            await bot.reply(membertoset.mention + ' roles have been correctly setup from smashranking')
        else:
            await bot.reply('Failed to set roles despite the ID existing')

@bot.command(description='Format: ?setroles <ID>\nSets your roles based on a particular smashranking.eu ID. Useful if your discord nickname is not the same as your smashranking.eu identifier.',pass_context=True)
async def obtainroles_id(ctx, IDtoUse : str):
    result = getPlayerInfo(IDtoUse.lower())
    if (result[0] == -1):
        await bot.reply('Lookup failed, check that smashranking is up and that the ID used exists on smashranking (you can try "id-<nationality abbreviation>"')
        await bot.reply('Contact an admin if the problem persists')
    else:
        if (await setRoles(ctx.message.author,result[1],ctx.message.server)):
            await bot.reply('Your roles have been correctly setup from smashranking')
        else:
            await bot.reply('Failed to set your roles despite the ID existing, contact an admin')
			
			
@bot.event
async def on_member_join(member : discord.Member):
    await bot.send_message(member,'Welcome to the EU Grandmaster Melee server! The bot will now attempt to automatically obtain your country and main from smashranking.eu')
    name=member.name.replace(' ','-').lower()
    result = getPlayerInfo(name)
    if (result[0] == -1):
        #Try to find other slugs
        secondslug=getPlayerHighestSlug(name)
        if (secondslug[0] == 0):
            result = getPlayerInfo(secondslug[1])
            name=secondslug[1]
    if (result[0] == -1):
        await bot.send_message(member,'Failed to set your country and/or main automatically. Contact an admin for assistance')
    else:
        if (await setRoles(member,result[1],member.server)):
            await bot.send_message(member,'Your country and main are now set! Contact an admin if the bot got it wrong')
        else:
            await bot.reply('Failed to set your roles despite your username being correct, contact an admin')

@bot.command(description="Format: ?tag <POST-ID> tag1 tag2 ...\nAdds the selected tags to the selected post-ID. Obtain post-IDs by right clicking options on a post")
async def tag(post_id : str, *tags : str):
	print(str(post_id) + ", " + str(tags))
	if (len(tags) < 1):
		bot.reply('Requires atleast one tag to tag')
		return
	for tag in tags:
		proptag=tag.lower()
		if (proptag in taggedPosts):
			taggedPosts[proptag].add(post_id)
		else:
			taggedPosts[proptag]=set([post_id])
	await bot.reply("Tagging successful!")
	print("Received new tagged post, saving new tag-ID map")
	try:
		toDump={}
		for key in taggedPosts:
			toDump[key]=list(taggedPosts[key])
		json.dump(toDump,open('tagidbindings.json','w'))
	except Exception:
		print("WARNING: Failed to write tag-ID map:")
		print(sys.exc_info())
		print("Printing JSON dump for backup purposes")
		print(json.dumps(taggedPosts))

async def obtainPostsFromIDS(IDS,channel):
	matchingPosts=[]
	async for post in bot.logs_from(channel,LARGE_NUMBER):
		matchingPosts.append(post)
	matchingPosts = [post for post in matchingPosts if post.id in IDS]
	return matchingPosts
		
@bot.command(pass_context=True,description="Format: ?search tag1 tag2 ...\nPrints all posts, in order of posting, that have ALL the selected tags")
async def search(ctx,*tags : str):
	if (len(tags) < 1):
		bot.reply('Requires atleast one tag to search, blanket printing all posts is not allowed')
		return
	for tag in tags:
		if not tag in taggedPosts:
			await bot.reply("There are no posts tagged with '"+tag+"'")
			return
	potentialposts=taggedPosts[tags[0]]
	for tag in tags[1:]:
		potentialposts=[post for post in  potentialposts if post in taggedPosts[tag] ]
	actualposts=await obtainPostsFromIDS(potentialposts,ctx.message.channel)
	actualposts.sort(key=lambda x: x.timestamp)
	if (len(actualposts) == 0):
		await bot.reply("Sorry, there were no posts tagged with: " + " ".join(tags))
		return
	await bot.say("Printing posts tagged with: " + " ".join(tags)) 
	for post in actualposts:
		await bot.say(post.author.name + "@" + str(post.timestamp) +" (" + post.id + "):\n" + post.content)

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

print("Reading local tag-ID bindings...")
try:
	taggedPostsLists=json.load(open('tagidbindings.json','r'))
	for key in taggedPostsLists:
		taggedPosts[key]=set(taggedPostsLists[key])
except Exception:
	print("Failed to open local tag-ID bindings")
	print("If this is because you don't have the file created, you're fine.")
	print(sys.exc_info())

bot.run(token)

