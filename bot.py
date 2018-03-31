#!/usr/bin/env python
import discord
import asyncio
import random
import json
import os
import re
import shlex
import math
import numpy
import scipy.special
import asteval
import itertools
import time
import matplotlib.pyplot as plt
from collections import OrderedDict
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

#Adding functions to asteval
aeval = asteval.Interpreter()
aeval.symtable["r_randint"]=random.randint
aeval.symtable["r_randrange"]=random.randrange
aeval.symtable["r_choice"]=random.choice
if hasattr(random,'choices'):
    aeval.symtable["r_choices"]=random.choices
else:
    def f(population, weights=None, k=1):
        """
        Replacement for `random.choices()`, which is only available in Python 3.6+.
        """
        return numpy.random.choice(population, size=k, p=weights)
    aeval.symtable["r_choices"]=random.choices
aeval.symtable["r_shuffle"]=random.shuffle
aeval.symtable["r_sample"]=random.sample
aeval.symtable["r_random"]=random.random

#print(aeval.symtable)
random.seed(os.urandom(64))

#Building myself
myself = {}

with open('settings.json') as data_file:    
    settings = json.load(data_file)
myself['git'] = settings['git_link']
myself['prefix'] = settings['prefix']
myself['charsign'] = settings['charsign']
if myself['charsign'] == "$":
    myself['recharsign'] = "\\"+myself['charsign']
else:
    myself['recharsign'] = myself['charsign']
myself['help'] = settings['help']

with open('characters.json') as data_file:    
    characters = json.load(data_file)
myself['characters'] = characters

with open('statistics.json') as data_file:    
    statistics = json.load(data_file, object_pairs_hook=OrderedDict)
myself['statistics'] = statistics

with open('bookdata.json') as data_file:    
    bookdata = json.load(data_file)
myself['bookdata']={}
def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z
for i in bookdata:
    myself['bookdata']=merge_two_dicts(myself['bookdata'], bookdata[i])
myself['bookdata'] = {"all":myself['bookdata']}
myself['bookdata'] = merge_two_dicts(myself['bookdata'],bookdata)


plt.bar([1],[1])
plt.savefig('work.png')
plt.clf()

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

def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start

def singleRoll(s):
    t = s.split('d')
    if t[0]=='':
        t[0]=1
    else:
        t[0]=int(t[0])
    t[1]=int(t[1])
    return [random.randint(1,t[1]) for i in range(t[0])]

def explodingRoll(s,n=False,test='='):
    t = s.split('d')
    if t[0]=='':
        t[0]=1
    else:
        t[0]=int(t[0])
    t[1]=int(t[1])
    if not(n):
        n = t[1]
    else:
        n = int(n)
    if test=='>':
        def f(x):
            return x>=n
    elif test=='<':
        def f(x):
            return x<=n
    else:
        def f(x):
            return x==n
    out = tab = [random.randint(1,t[1]) for i in range(t[0])]
    while len([x for x in tab if f(x)])>0:
        tab = [random.randint(1,t[1]) for i in range(len([x for x in tab if f(x)]))]
        out += tab
    return out
            
def gBinom(n,k):
    if n<0:
        return (-1)**k*scipy.special.binom(-n,k)
    else:
        return scipy.special.binom(n,k)

def diceProb(n,t,d):
    def singleRollSum(j):
        return ((-1)**j)*gBinom(n,j)*gBinom(t-d*j-1,n-1)
    return d**(-n)*sum([singleRollSum(j) for j in range(int((t-n)/d)+1)])

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
    dicereg = r"((\d+#)?\d*d\d+((\+|-)(\d*d|)\d+)*|"+myself['recharsign']+r"(.*):(.*)"+myself['recharsign']+")"
    test = re.search(dicereg,message.content)
    if message.content.startswith(myself['prefix']):
        print(message.content)
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
        elif message.content.startswith(myself['prefix']+'poke'):
            await client.send_message(message.channel, myself['navi'].state())
        elif message.content.startswith(myself['prefix']+'git'):
            await client.send_message(message.channel, myself['git'])
        elif message.content.startswith(myself['prefix']+'poll'):
            await client.add_reaction(message,"\N{THUMBS UP SIGN}")
            await client.add_reaction(message,"\N{THUMBS DOWN SIGN}")
            await client.add_reaction(message,"\U0001F937")
        elif message.content.startswith(myself['prefix']+'statistics'):
            work = shlex.split(message.content)
            if len(work)==1:
                await client.send_message(message.channel, '<@'+message.author.id+'>: You need to look up someone in particular')
            else:
                if "<@" in work[1]:
                    lookup = work[1][1:-1]
                    try:
                        mentioned = message.server.get_member(lookup[1:])
                        mentioned = mentioned.nick
                        if not(mentioned):
                            raise ValueError('No nickname')
                    except:
                        mentioned = await client.get_user_info(lookup[1:])
                        mentioned = mentioned.name
                else:
                    if work[1].lower()=="myself":
                        mentioned = message.author.name
                        lookup = '@'+message.author.id
                    else:
                        mentioned = work[1]
                        if message.server:
                            lookup = "@"+message.server.get_member_named(work[1])
                        else:
                            lookup = "@"+message.channel.recipients[0].id
                if not(lookup):
                    await client.send_message(message.channel, '<@'+message.author.id+">: There doesn't seem to be a member of this server that goes by "+mentioned+'.')
                else:
                    if lookup in myself['statistics']:
                        stats = myself['statistics'][lookup]
                        probs = myself['statistics']['probability']
                        if len(work)==2:
                            await client.send_message(message.channel, '<@'+message.author.id+'>: Results for '+mentioned+"'s rolls.\n")
                            for i,j in stats.items():
                                n = j['rolls']
                                t = [[],[]]
                                for k,l in j.items():
                                    if k!='rolls':
                                        t[0].append(int(k))
                                        t[1].append(l/n)
                                if len(t[0])>100:
                                    plt.plot(t[0],t[1],'b-')
                                else:
                                    plt.bar(t[0],t[1])
                                plt.savefig('work.png')
                                plt.clf()
                                await client.send_file(message.channel, 'work.png',content="Recorded "+i)
                                if 'image' in probs[i]:
                                    await client.send_file(message.channel, probs[i]['image'],content="Expected "+i)
                                else:
                                    t = [[],[]]
                                    for k,l in probs[i].items():
                                        t[0].append(int(k))
                                        t[1].append(l)
                                    if len(t[0])>100:
                                        plt.plot(t[0],t[1],'b-')
                                    else:
                                        plt.bar(t[0],t[1])
                                    plt.savefig('Probabilities/'+i+'.png')
                                    plt.clf()
                                    await client.send_file(message.channel,'Probabilities/'+i+'.png',content="Expected "+i)
                                    probs[i]['image']='Probabilities/'+i+'.png'
                                    with open('statistics.json','w') as data_file:    
                                        json.dump(myself['statistics'],data_file,indent=4)
                        else:
                            await client.send_message(message.channel, '<@'+message.author.id+'>: Results for '+mentioned+"'s rolls of "+work[2]+".\n")
                            if work[2] in stats:
                                s="Recorded "+work[2]+":\n"
                                n = stats[work[2]]['rolls']
                                t = [[],[]]
                                for i,j in stats[work[2]].items():
                                    if i!='rolls':
                                        t[0].append(int(i))
                                        t[1].append(j/n)
                                plt.bar(t[0],t[1])
                                plt.savefig('work.png')
                                plt.clf()
                                await client.send_file(message.channel, 'work.png',content="Recorded "+work[2])
                                if 'image' in probs[work[2]]:
                                    await client.send_file(message.channel ,probs[work[2]]['image'],content="Expected "+work[2])
                                else:
                                    t = [[],[]]
                                    for i,j in probs[work[2]].items():
                                        t[0].append(int(i))
                                        t[1].append(j)
                                    plt.bar(t[0],t[1])
                                    plt.savefig('Probabilities/'+i+'.png')
                                    plt.clf()
                                    await client.send_file(message.channel,'Probabilities/'+i+'.png',content="Expected "+work[2])
                                    probs[work[2]]['image']='Probabilities/'+work[2]+'.png'
                                    with open('statistics.json','w') as data_file:    
                                        json.dump(myself['statistics'],data_file,indent=4)
                            else:
                                await client.send_message(message.channel, '<@'+message.author.id+'>: '+mentioned+" doesn't seem to have ever rolled "+work[2]+".")
                    else:
                        await client.send_message(message.channel, '<@'+message.author.id+'>: '+mentioned+" doesn't have any rolls on record")
        elif message.content.startswith(myself['prefix']+'ref'):
            test = message.content.split(" ",2)
            if len(test)==3 and test[1] in myself['bookdata'].keys():
                bookdata = myself['bookdata'][test[1]]
                work = (test[0],test[2])
            else:
                bookdata = myself['bookdata']['all']
                work = message.content.split(" ",1)
            poss = bookdata.keys()
            poss = process.extractOne(work[1], poss)
            if poss[1]>80: 
                await client.send_message(message.channel, bookdata[poss[0]])
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
                        elif len(attrs)==1:
                            attrs = attrs[0]
                        elif len(attrs)==2:
                            attrs = attrs[0]+' and '+attrs[1]
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
    elif test != None and not(message.author.bot):
        work = message.content[test.end():]
        roll = message.content[test.start():test.end()]
        output = '<@'+message.author.id+">:\n" + roll + ':'
        while roll != None:
            if roll.find(myself['charsign'])>-1:
                print('charsign')
                try:
                    character = roll[1:-1]
                    character, attribute= character.split(':')
                    attribute = myself['characters'][character][attribute]
                    roll = attribute
                except:
                    roll = ''
            if roll.find('#')>-1:
                number, individual = roll.split('#')
                roll = [int(number),individual]
            else:
                roll = [1,roll]
            roll.append([])
            rollparse = roll[1]
            if rollparse[0] == "-":
                sign = -1
                rollparse=rollparse[1:]
            else:
                sign = 1
            while len(rollparse) > 0:
                if rollparse.find('+')>-1 or rollparse.find('-')>-1:
                    if rollparse.find('+')>-1 and rollparse.find('-')>-1:
                        ind = min(rollparse.find('+'),rollparse.find('-'))
                    elif rollparse.find('+')>-1:
                        ind = rollparse.find('+')
                    else:
                        ind = rollparse.find('-')
                    oneRoll = rollparse[:ind]
                    roll[2].append((sign,oneRoll))
                    rollparse = rollparse[ind:]
                    if rollparse[0] == '-':
                        sign = -1
                    else:
                        sign = 1
                    rollparse = rollparse[1:]
                else:
                    roll[2].append((sign,rollparse))
                    rollparse = ''
            print(roll)
            result = []
            for i in range(roll[0]):
                strResult = ''
                oneResult = 0
                for j in roll[2]:
                    if j[1].find('d')>-1:
                        rollout = singleRoll(j[1])
                        strResult += ('-' if j[0]<0 else '+')+'('+'+'.join([str(k) for k in rollout])+')'
                        oneResult += j[0]*sum(rollout)
                    else:
                        try:
                            strResult += ('-' if j[0]<0 else '+')+j[1] 
                            oneResult += j[0]*int(j[1])
                        except:
                            pass
                if strResult[0]=='+':
                    strResult=strResult[1:]
                result.append(strResult+"="+str(oneResult))

            output += '`'+','.join(result)+'`'
            test = re.search(dicereg,work)
            if test == None:
                roll = None
            else:
                roll = work[test.start():test.end()]
                work = work[test.end():]
                output += '\n' + roll + ':'
        await client.send_message(message.channel, output)
sleeptime=0
sleeptimes=[5,5,30,60,60*5]
while True:
    try: 
        client.loop.run_until_complete(client.start(token))
    except discord.errors.LoginFailure as e:
        print("The client failed to login with error: "+e.args[0])
        if e.args[0]=="Improper token has been passed.":
            print("Did you put a valid token into settings.json?")
            break
    except BaseException as e:
        print("Something went wrong:") 
        print("Error: "+e.args[0])
        time.sleep(sleeptimes[sleeptime])
        if sleeptime<4:
            sleeptime+=1