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
myself['prefix'] = settings['prefix']
myself['charsign'] = settings['charsign']
myself['help'] = settings['help']

with open('characters.json') as data_file:    
    characters = json.load(data_file)
myself['characters'] = characters

with open('statistics.json') as data_file:    
    statistics = json.load(data_file, object_pairs_hook=OrderedDict)
myself['statistics'] = statistics

with open('bookdata.json') as data_file:    
    bookdata = json.load(data_file)
myself['bookdata'] = bookdata


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

def diceRoll(s):
    bigmatches = []
    out=[]
    while s.count('('):
        pos=[s.find('(')+1,None]
        while s[pos[0]:pos[1]].find('(')>-1 and s[pos[0]:pos[1]].find('(')<s[pos[0]:pos[1]].find(')'):
            pos[0]=pos[0]+s[pos[0]:pos[1]].find('(')+1
        if s[pos[0]:pos[1]].find(')')>-1: 
            pos[1]=pos[0]+s[pos[0]:pos[1]].find(')')
        if pos[0]-6>-1 and s[pos[0]-6:pos[0]-1] in ['floor','round'] or pos[0]-5>-1 and s[pos[0]-6:pos[0]-1]=='ceil' or pos[0]-4>-1 and s[pos[0]-6:pos[0]-1]=='abs':
            j1='{'
            j2='}'
        else:
            if pos[0]-2<0 or s[pos[0]-2] in ['+','-','*','/','d']:
                j1 = ''
            else:
                j1 = '*'
            if pos[1]+1>=len(s) or s[pos[1]+1] in ['+','-','*','/','d']:
                j2 = ''
            else:
                j2 = '*'
        roll = diceRoll(s[pos[0]:pos[1]])
        s = s[:pos[0]-1]+j1+str(roll[0][1])+j2+s[pos[1]+1:]
        bigmatches = bigmatches + roll[1]
    """
    while s.count('{'):
        pos=[s.find('{')+1,None]
        while s[pos[0]:pos[1]].find('{')>-1 and s[pos[0]:pos[1]].find('{')<s[pos[0]:pos[1]].find('}'):
            pos[0]=s[pos[0]:pos[1]].find('{')+1
        if s[pos[0]:pos[1]].find(')')>-1: 
            pos[1]=s[pos[0]:pos[1]].find('}')
        sub = s[pos[0]:pos[1]]
        if sub.find(','):
            sub = sub.split(',')
            tab = []
            for i in sub:
                tab.append(diceRoll(i)[0][1])
            sub = 
        else:
            
        roll = diceRoll(s[pos[0],pos[1]])
        s = s[:pos[0]-1]+j1+str(roll[0][1])+j2+s[pos[1]+1:]
        bigmatches = bigmatches + roll[1]
    """
    matches = re.findall('floor{[\d.]+}', s)
    matches = re.findall('\d*d\d+!>\d+', s)
    matches = [[i,explodingRoll(i.split('!>')[0],i.split('!>')[1]),'>'] for i in matches]
    bigmatches = bigmatches + matches
    matches = re.findall('\d*d\d+!<\d+', s)
    matches = [[i,explodingRoll(i.split('!<')[0],i.split('!<')[1]),'<'] for i in matches]
    bigmatches = bigmatches + matches
    matches = re.findall('\d*d\d+!\d+', s)
    matches = [[i,explodingRoll(i.split('!')[0],i.split('!')[1])] for i in matches]
    bigmatches = bigmatches + matches
    matches = re.findall('\d*d\d+!', s)
    matches = [[i,explodingRoll(i.split('!')[0])] for i in matches]
    bigmatches = bigmatches + matches
    matches = re.findall('\d*d\d+', s)
    matches = [[i,singleRoll(i)] for i in matches]
    bigmatches = bigmatches + matches
    firstpart = s
    for i in matches:
        firstpart = firstpart.replace(i[0],'('+' + '.join([str(x) for x in i[1]])+')',1)
        s = s.replace(i[0],str(sum(i[1])),1)
    out.append(firstpart)
    while re.search(r'\d+\*\*\d+',s):
        match = re.search(r'\d+\*\*\d+',s)
        s = s[:match.start()]+str(aeval(s[match.start():match.end()]))+s[match.end():]
    while re.search(r'\d+\*\d+|\d+/\d+|\d+%\d+',s):
        match = re.search(r'\d+\*\d+|\d+/\d+|\d+%\d+',s)
        s = s[:match.start()]+str(aeval(s[match.start():match.end()]))+s[match.end():]
    while re.search(r'\d+\+\d+|\d+-\d+',s):
        match = re.search(r'\d+\+\d+|\d+-\d+',s)
        s = s[:match.start()]+str(aeval(s[match.start():match.end()]))+s[match.end():]
    out.append(s)
    return [out,bigmatches]
            
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
            test = work.split()
            if len(test)<2 or test[1]=='' and len(test)<3:
                await client.send_message(message.channel, '<@'+message.author.id+'>'+" tried to roll, but didn't know how the syntax works!")
            if work.count('`')>1:
                try:
                    initial = '<@'+message.author.id+'>'+ ' calculated '+work
                    if not(initial[len(initial)-1] in ['!','.','?']):
                        initial = initial + '!'
                    await client.send_message(message.channel, initial)
                    rolls = []
                    s = work.split('`')[1:]
                    while len(s)>1:
                        rolls.append(s[0])
                        s = s[2:]
                    out = "'<@'+message.author.id+">'s result"
                    if len(rolls)>1:
                        out+='s'
                    out+=':\n'
                    for roll in rolls:
                        evaluation = aeval(roll)
                        out += "`"+roll+'='+str(evaluation)
                        if aeval.error!=[]:
                            out+= " ("+aeval.error[0].msg+")"
                        out+= '`\n'
                    await client.send_message(message.channel, out)
                except Exception as e:
                    print(e)
                    await client.send_message(message.channel, '<@'+message.author.id+'>'+" calculation didn't make any sense to me!")
            else:
                work = work.split()
                if len(work)>2:
                    details = ' '.join(work[2:])
                else:
                    details = ''
                work = work[1]
                initial = '<@'+message.author.id+'>'+ ' rolled '+work
                if details != '':
                    initial += ' for ' + details
                await client.send_message(message.channel, initial)
                result,matches = diceRoll(work)
                out = '<@'+message.author.id+">'s result:`"+result[0]+'='+result[1]+'`'
                await client.send_message(message.channel, out)
                if len(matches)>0:
                    if not('@'+message.author.id in myself['statistics']):
                        myself['statistics']['@'+message.author.id]={}
                    for i in matches:
                        if not(i[0][0].isdigit()):
                            i[0]='1'+i[0]
                        if not(i[0] in myself['statistics']['probability']):
                            if '!' in i[0]:
                                pass
                                """
                                p1,p2 = i[0].split('d')
                                p2,cond = p2.split('!')
                                p1 = int(p1)
                                p2 = int(p2)
                                if cond=='':
                                    cond = p2
                                    def test(x):
                                        return x==cond
                                else:
                                    if cond[0]=='>':
                                        cond = int(cond[1:])
                                        def test(x):
                                            return x>=cond
                                    elif cond[0]=='<':
                                        cond = int(cond[1:])
                                        def test(x):
                                            return x<=cond
                                    else:
                                        cond = int(cond[1:])
                                        def test(x):
                                            return x==cond
                                d=p2**p1
                                myself['statistics']['probability'][i[0]]={}
                                m = p1*p2+1
                                mult = 1/d
                                lim = 5
                                splode = []
                                for j in range(p1,m):
                                    count = [k for k in partition_min_max(j,p1,1,p2)]
                                    volatile = [x for x in count if any(map(test,x))]
                                    stable = [x for x in count if not(any(map(test,x)))]
                                    if len(volatile)>0:
                                        for k in volatile:
                                            volatilemult = numPerms(k)
                                            splode.append([sum(k),len([x for x in k if test(x)]),volatilemult*mult])
                                    if len(stable)>0:
                                        stable = [k for k in map(numPerms,stable)]
                                        stable = sum(stable)
                                        myself['statistics']['probability'][i[0]][str(j)]=stable*mult
                                itercount = 0
                                while itercount<lim:
                                    newsplode = []
                                    for j in splode:
                                        p1 = j[1]
                                        m = p1*p2+1
                                        mult = j[2]*(1/p2**p1)
                                        for k in range(p1,m):
                                            count = [x for x in partition_min_max(k,p1,1,p2)]
                                            volatile = [x for x in count if any(map(test,x))]
                                            stable = [x for x in count if not(any(map(test,x)))]
                                            if len(volatile)>0:
                                                for k in volatile:
                                                    volatilemult = numPerms(j)
                                                    newsplode.append([j[0]+sum(k),len([x for x in k if test(x)]),volatilemult*mult])
                                            if len(stable)>0:
                                                stable = [x for x in map(numPerms,stable)]
                                                stable = sum(stable)
                                                if str(j[0]+k) in myself['statistics']['probability'][i[0]]:
                                                    myself['statistics']['probability'][i[0]][str(j[0]+k)]+=stable*mult
                                                else:
                                                    myself['statistics']['probability'][i[0]][str(j[0]+k)]=stable*mult
                                    splode = newsplode
                                    itercount += 1
                                """
                            else:
                                p1,p2 = i[0].split('d')
                                p1=int(p1)
                                p2=int(p2)
                                myself['statistics']['probability'][i[0]]={}
                                if p1 == 1:
                                    d = p2**p1
                                    for j in range(p1,p1*p2+1):
                                        myself['statistics']['probability'][i[0]][str(j)]=1/d
                                else:
                                    m = p1*p2+1
                                    for j in range(p1,p1+math.ceil((m-p1)/2)):
                                        myself['statistics']['probability'][i[0]][str(j)]=myself['statistics']['probability'][i[0]][str(m-j+p1-1)]=diceProb(p1,j,p2)
                        if '!' in i[0]:
                            pass
                        elif i[0] in myself['statistics']['@'+message.author.id]:
                            myself['statistics']['@'+message.author.id][i[0]][str(sum(i[1]))] += 1
                            myself['statistics']['@'+message.author.id][i[0]]['rolls'] += 1
                        else:
                            myself['statistics']['@'+message.author.id][i[0]]={}
                            myself['statistics']['@'+message.author.id][i[0]]['rolls']=1
                            for j in myself['statistics']['probability'][i[0]].keys():
                                myself['statistics']['@'+message.author.id][i[0]][j]=0
                            myself['statistics']['@'+message.author.id][i[0]][str(sum(i[1]))] += 1
                    with open('statistics.json','w') as data_file:    
                        json.dump(myself['statistics'],data_file,indent=4)
        elif message.content.startswith(myself['prefix']+'poke'):
            await client.send_message(message.channel, myself['navi'].state())
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
                                    plt.bar(t[0],t[1])
                                    plt.savefig('Probabilities/'+i+'.png')
                                    plt.clf()
                                    await client.send_file(message.channel,'Probabilities/'+i+'.png',content="Expected "+i)
                                    probs[i]['image']='Probabilities/'+i+'.png'
                                    with open('statistics.json','w') as data_file:    
                                        json.dump(myself['statistics'],data_file,indent=4)
                            """ Text version
                            for i,j in stats.items():
                                s+="Recorded "+i+":\n"
                                n = j['rolls']
                                for k,l in j.items():
                                    if k!='rolls':
                                        s+=k+":"+str(round(l/n*100,2))+"%"+" "
                                s = s[:-1]+"\n"
                                s+="Expected "+i+":\n"
                                for k,l in probs[i].items():
                                    s+=k+":"+str(l)+"%"+" "
                                s = s[:-1]+"\n"
                            """
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

client.run(token)