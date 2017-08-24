import discord
import asyncio
import random
import json
import os
import re
import shlex
import math 
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

random.seed(os.urandom(64))

myself = {}

with open('settings.json') as data_file:    
    settings = json.load(data_file)
myself['prefix'] = settings['prefix']
myself['charsign'] = settings['charsign']
myself['help'] = settings['help']

with open('characters.json') as data_file:    
    characters = json.load(data_file)
myself['characters'] = characters

with open('bookdata.json') as data_file:    
    bookdata = json.load(data_file)
myself['bookdata'] = bookdata

token = settings['token']

#string concat: 'your %s is in the %s' % (object, location)

client = discord.Client()

class Fairy:
    def __init__(self):
        self.word = 'Watch Out!'
    
    def state(self):
        if self.word == 'Hey!':
            self.word = 'Listen!'
        elif self.word == 'Listen!':
            self.word = 'Watch Out!'
        else:
            self.word = 'Hey!'
        return self.word

myself['navi'] = Fairy()

myself['waiting'] = {}

def diceRoll(s):
    if s.find('d')==0:
        s = '1'+s
    p1,p2 = s.split('d')
    tab = [1 for i in range(int(p1))]
    tab = [str(random.randint(1,int(p2))) for i in range(int(p1))]
    return '('+'+'.join(tab)+')'

@client.event
async def on_ready():
    global myself
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    global myself
    if message.content.startswith(myself['prefix']):
        if message.author.id in myself['waiting']:
            if myself['waiting'][message.author.id][0]=='prefix' or myself['waiting'][message.author.id][0]=='charsign':
                thing = myself['waiting'][message.author.id][0]
                if message.content.strip() == myself['prefix']+'Yes':
                    with open('settings.json') as data_file:
                        settings = json.load(data_file)
                    settings[thing] = myself['waiting'][message.author.id][1]
                    with open('settings.json','w') as data_file:
                        json.dump(settings,data_file,indent=4)
                    myself[thing] = settings[thing]
                    await client.send_message(message.channel, thing+" changed to "+myself[thing])
                elif message.content.strip() == myself['prefix']+'No':
                    await client.send_message(message.channel, thing+" change cancelled")
                else:
                    await client.send_message(message.channel, "That was an invalid response. "+thing+" change cancelled.")
                del myself['waiting'][message.author.id]
            elif myself['waiting'][message.author.id][0]=='delete':
                if message.content.strip() == myself['prefix']+'Yes':
                    del myself['characters'][myself['waiting'][message.author.id][1]]
                    with open('characters.json','w') as data_file:
                        json.dump(myself['characters'],data_file,indent=4)
                    await client.send_message(message.channel, 'Character '+myself['waiting'][message.author.id][1]+' deleted. Goodbye, old friend! :cry:')
                elif message.content.strip() == myself['prefix']+'No':
                    await client.send_message(message.channel, "Character deletion cancelled")
                else:
                    await client.send_message(message.channel, "That was an invalid response. Character deletion cancelled.")
                del myself['waiting'][message.author.id]
        elif message.content.startswith(myself['prefix']+'help'):
            await client.send_message(message.author, "<@"+message.author.id+">:\n"+myself['help'].replace('<spec:prefix>',myself['prefix']).replace('<spec:charsign>',myself['charsign']))
        elif message.content.startswith(myself['prefix']+'roll') or message.content.startswith(myself['prefix']+'r '):
            work = message.content.replace(' +','+').replace('+ ','+')
            if message.content.find(myself['charsign']):
                try:
                    twork = message.content.split(myself['charsign'])[1::2]
                    tout = []
                    for i in twork:
                        x = i.split(':')
                        tout.append(myself['characters'][x[0]][x[1]])
                    for i in range(len(twork)):
                        work = work.replace('$'+twork[i]+'$',tout[i])
                except:
                    work = ''
            work = shlex.split(work) # 0 = prefix, 1 = roll, 2 = message
            work = [work[0],work[1],''.join(work[2:])]
            if len(work)<2 or work[1]=='' :
                await client.send_message(message.channel, '<@'+message.author.id+'>'+" tried to roll, but didn't know how the syntax works!")
            else:
                try:
                    initial = '<@'+message.author.id+'>'
                    if work[1].find('d')!=-1:
                        initial = initial + ' rolled '+work[1]
                    else:
                        initial = initial + ' calculated '+work[1]
                    if len(work)==3 and work[2]!='':
                        initial = initial + ' for ' + work[2]
                    if not(initial[len(initial)-1] in ['!','.','?']):
                        initial = initial + '!'
                    await client.send_message(message.channel, initial)
                    roll = work[1]
                    matches = re.findall('\d*d\d+', roll)
                    matches = [[i,diceRoll(i)] for i in matches]
                    for i in matches:
                        roll = roll.replace(i[0],i[1],1)
                    await client.send_message(message.channel, '<@'+message.author.id+">'s result:`"+roll+'='+str(eval(roll.replace('%','0.01')))+'`')
                except:
                    if work[1].find('d')!=-1:
                        await client.send_message(message.channel, '<@'+message.author.id+'>'+"'s roll didn't make any sense to me!")
                    else:
                        await client.send_message(message.channel, '<@'+message.author.id+'>'+" calculation didn't make any sense to me!")
        elif message.content.startswith(myself['prefix']+'newchar'):
            work = shlex.split(message.content)
            if len(work)==1:
                await client.send_message(message.channel, 'newchar usage: '+myself['prefix']+'newchar [character name] <attributes>')
            else:
                char = work[1]
                if char in myself['characters']:
                    await client.send_message(message.channel, "That character already exists; use editattr to change attributes.")
                else:
                    myself['characters'][char]={'__creator__':message.author.id,'__hidden__':False}
                    work = work[2:]
                    while len(work)>0:
                        if work[0].find('=')!=-1:
                            w = work[0].split('=')
                            if not(w[0] in ['__creator__']) and w[0].find('!')!=0:
                                myself['characters'][char][w[0]]=w[1]
                        elif work[0].find(':')!=-1:
                            w = work[0].split('=')
                            if not(w[0] in ['__creator__']) and w[0].find('!')!=0:
                                myself['characters'][char][w[0]]=w[1]
                        work = work[1:]
                    with open('characters.json','w') as data_file:
                        json.dump(myself['characters'],data_file,indent=4)
                    await client.send_message(message.channel, char + " created! Use "+myself['prefix']+"editattr to change attributes, or "+myself['prefix']+"viewchar to view.")
        elif message.content.startswith(myself['prefix']+'viewchar'):
            work = shlex.split(message.content)
            if len(work)==1:
                await client.send_message(message.channel, 'viewchar usage: '+myself['prefix']+'viewchar [character name] <attribute>')
            else:
                char = work[1]
                if char in myself['characters'] and (not(myself['characters'][char]['__hidden__']) or message.author.id == myself['characters'][char]['__creator__'] or message.author.server_permissions.administrator):
                    if len(work)==3:
                        if work[2] in myself['characters'][char]:
                            await client.send_message(message.channel, "%s's %s attribute: %s"%(char,work[2],myself['characters'][char][work[2]]))
                        else:
                            await client.send_message(message.channel, "%s doesn't have an attribute called %s."%(char,work[2]))
                    else:
                        await client.send_message(message.channel, char+" is a character created by <@"+ myself['characters'][char]['__creator__'] +"> with the following attributes:") 
                        attrs = []
                        for i,j in myself['characters'][char].items():
                            if not(i in ["__creator__",'__hidden__']):
                                attrs.append(i)
                        if attrs==[]:
                            attrs="None"
                        else:
                            attrs = ', '.join(attrs[:-1])+', and '+attrs[-1]
                        await client.send_message(message.channel, attrs)    
                else:
                    await client.send_message(message.channel, "That character does not exist, or is hidden.") 
        elif message.content.startswith(myself['prefix']+'hidechar'):
            work = shlex.split(message.content)
            if len(work)==1:
                await client.send_message(message.channel, 'hidechar usage: '+myself['prefix']+'hidechar [character name]')
            else:
                char = work[1]
                if char in myself['characters'] and (message.author.id == myself['characters'][char]['__creator__'] or message.author.server_permissions.administrator):
                    myself['characters'][char]['__hidden__'] = not(myself['characters'][char]['__hidden__'])
                    if myself['characters'][char]['__hidden__']:
                        await client.send_message(message.channel, char + " hidden.")
                    else:
                        await client.send_message(message.channel, char + " unhidden.")
                else:
                    await client.send_message(message.channel, "That character does not exist, or does not belong to you.") 
        elif message.content.startswith(myself['prefix']+'delchar'):
            work = shlex.split(message.content)
            if len(work)==1:
                await client.send_message(message.channel, 'delchar usage: '+myself['prefix']+'delchar [character name]')
            else:
                char = work[1]
                if char in myself['characters']:
                    if message.author.id == myself['characters'][char]['__creator__']:
                        await client.send_message(message.channel, 'Are you sure you want to delete your character %s? Use %sYes or %sNo'%(char,myself['prefix'],myself['prefix']))
                        myself['waiting'][message.author.id]=['delete',char]
                    elif message.author.server_permissions.administrator:
                        await client.send_message(message.channel, "Are you sure you want to delete %s's character %s? Use %sYes or %sNo"%(myself['characters'][char]['__creator__'],char,myself['prefix'],myself['prefix']))
                        myself['waiting'][message.author.id]=['delete',char]
                    else:
                        await client.send_message(message.channel, char+' belongs to <@'+myself['characters'][char]['__creator__']+'>. Only the creator or an administrator can delete them.')
                else:
                    await client.send_message(message.channel, "That character does not exist.") 
        elif message.content.startswith(myself['prefix']+'editattr'):
            work = shlex.split(message.content)
            if len(work)==1:
                await client.send_message(message.channel, 'editattr usage: '+myself['prefix']+'editattr [character name] <attributes>')
            else:
                char = work[1]
                if char in myself['characters']:
                    if message.author.id == myself['characters'][char]['__creator__'] or message.author.server_permissions.administrator:
                        work = work[2:]
                        while len(work)>0:
                            if work[0].find('!')==0:
                                w = work[0][1:]
                                if w in myself['characters'][char]:
                                    del myself['characters'][char][w]
                            elif work[0].find('=')!=-1:
                                w = work[0].split('=')
                                if not(w[0] in ["__creator__",'__hidden__']):
                                    print(w)
                                    myself['characters'][char][w[0]]=w[1]
                            elif work[0].find(':')!=-1:
                                w = work[0].split(':')
                                if not(w[0] in ["__creator__",'__hidden__']):
                                    print(w)
                                    myself['characters'][char][w[0]]=w[1]
                            work = work[1:]
                        with open('characters.json','w') as data_file:
                            json.dump(myself['characters'],data_file,indent=4)
                        await client.send_message(message.channel, char + " edited!")
                    else:
                        await client.send_message(message.channel, char+' belongs to <@'+myself['characters'][char]['__creator__']+'>. Only the creator or an administrator can edit them.')
                else:
                    await client.send_message(message.channel, "That character does not exist; use newchar to create them.") 
        elif message.content.startswith(myself['prefix']+'poke'):
            await client.send_message(message.channel, myself['navi'].state())
        elif message.content.startswith(myself['prefix']+'poll'):
            await client.add_reaction(message,"\N{THUMBS UP SIGN}")
            await client.add_reaction(message,"\N{THUMBS DOWN SIGN}")
            await client.add_reaction(message,"\U0001F937")
        elif message.content.startswith(myself['prefix']+'ref'):
            work = message.content.split(" ",1)
            poss = myself['bookdata'].keys()
            poss = process.extractOne(work[1], poss)
            if poss[1]>80: 
                await client.send_message(message.channel, myself['bookdata'][poss[0]])
            else:
                await client.send_message(message.channel, "Sorry <@"+message.author.id+">, I couldn't find a good match.")
        elif message.content.startswith(myself['prefix']+'prefix') or message.content.startswith(myself['prefix']+'charsign'):
            work = message.content.split()
            thing = work[0][len(myself['prefix']):]
            if len(work)==1:
                if message.author.server_permissions.administrator:
                    await client.send_message(message.channel, "<@%s>: My current %s is %s. If you'd like to change it, type %sprefix <new prefix>"%(message.author.id,thing,myself[thing],myself['prefix']))
                else:
                    await client.send_message(message.channel, "<@%s>: My current %s is %s. If you'd like to change it, you'll have to ask an administrator."%(message.author.id,thing,myself[thing]))
            elif len(work)==2:
                if message.author.server_permissions.administrator:
                    myself['waiting'][message.author.id]=[thing,work[1]]
                    await client.send_message(message.channel, '<@%s>: My current %s is %s. Are you sure you want to change it to "%s"? Use %sYes or %sNo'%(message.author.id,thing,myself[thing],work[1],myself['prefix'],myself['prefix']))
                else:
                    await client.send_message(message.channel, "I'm afraid I can't do that, <@%s>. Only administrators can change my prefix."%(message.author.id))
            else:
                await client.send_message(message.channel, "My "+thing+"s can't have spaces.")

client.run(token)