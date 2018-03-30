import json
from collections import OrderedDict

with open('ptu_pokedex_1_05_plus.json') as data_file:    
    olddata = json.load(data_file, object_pairs_hook=OrderedDict)

with open('moves.json') as data_file:    
    movedata = json.load(data_file)
    
dexdata = OrderedDict()
indices = ["{0:0=3d}".format(i) for i in range(1,721)]
keys = list(olddata.keys())
maxlength = 0
reverseindex = {}
for i in indices:
    forms = [x for x in keys if x[:3] == i]
    reverseindex[olddata[i]['Species']]=forms
for i in indices:
    forms = [x for x in keys if x[:3] == i]
    work = [('Normal',i)]
    for j in forms:
        print(j)
        #Shortcut for old entry
        oldentry = olddata[j]
        #Making form dex entry
        formentry = OrderedDict()
        #Header for all mini-entries
        startstring = '#'+j[:3]+': '+oldentry['Species']+'\n'
        startstring += oldentry['Form']+(' Form' if oldentry['Form'].find(' ')==-1 else '')+'\n'
        #Stat Entry
        formentry['Stats']=formentry['Basic']=formentry['Evolution']=formentry['Size']=formentry['Breeding']=formentry['Environment']=formentry['Capabilities']=formentry['Skills']=formentry['Level-Up']=formentry['TMs']=formentry['Egg']=formentry['Tutor']=formentry['Mega']=startstring
        formentry['Stats']+= 'Base Stats:'
        for stat in ['HP','Attack','Defense','Special Attack','Special Defense','Speed']:
            formentry['Stats']+='\n'+stat+': '+str(oldentry['BaseStats'][stat.replace(' ','')])
        maxlength = max(maxlength,len(formentry['Stats']))
        #Basic Entry
        formentry['Basic']+= 'Basic Information:\n'
        formentry['Basic']+= 'Type: '+oldentry['Types'][0]+('/'+oldentry['Types'][1] if len(oldentry['Types'])>1 else '')
        for k in range(len(oldentry['Abilities'])):
            formentry['Basic'] += '\n'
            if oldentry['Abilities'][k]['Type']=='Advanced':
                head = 'Adv'
            else:
                head = oldentry['Abilities'][k]['Type']
            if k!=0 and oldentry['Abilities'][k-1]['Type']==oldentry['Abilities'][k]['Type']:
                if k>1 and oldentry['Abilities'][k-2]['Type']==oldentry['Abilities'][k]['Type']:
                    head += ' Ability 3: '
                else:
                    head += ' Ability 2: '
            elif k!=len(oldentry['Abilities'])-1 and oldentry['Abilities'][k+1]['Type']==oldentry['Abilities'][k]['Type']:
                head += ' Ability 1: '
            else:
                head += ' Ability: '
            formentry['Basic'] += head + oldentry['Abilities'][k]['Name']
        maxlength = max(maxlength,len(formentry['Basic']))
        #Evolution Entry
        formentry['Evolution']+='Evolution:'
        futuretrigger = False
        futuretypes=set()
        for k in range(len(oldentry['EvolutionStages'])):
            formentry['Evolution']+='\n'
            formentry['Evolution']+=str(oldentry['EvolutionStages'][k]['Stage']) + ' - '
            formentry['Evolution']+=oldentry['EvolutionStages'][k]['Species']
            if futuretrigger:
                print(reverseindex[oldentry['EvolutionStages'][k]['Species']])
                for l in reverseindex[oldentry['EvolutionStages'][k]['Species']]:
                    futuretypes = futuretypes.union(olddata[l]['Types'])
            if oldentry['EvolutionStages'][k]['Species']==oldentry['Species']:
                futuretrigger = True
            formentry['Evolution']+='' if oldentry['EvolutionStages'][k]['Criteria']=='' else ' '+oldentry['EvolutionStages'][k]['Criteria']
        maxlength = max(maxlength,len(formentry['Evolution']))
        print(oldentry['Species'])
        print(futuretypes)
        #Size Entry
        formentry['Size']+='Size Information:\n'
        if oldentry['Height']['Metric']['Minimum']['Meters'] == oldentry['Height']['Metric']['Maximum']['Meters']:
            meas = str(oldentry['Height']['Imperial']['Minimum']['Feet'])+"' "
            meas += str(oldentry['Height']['Imperial']['Minimum']['Inches'])+'" /'
            meas += str(oldentry['Height']['Metric']['Minimum']['Meters'])+'m '
            meas += '('+oldentry['Height']['Category']['Minimum']+')'
        else:
            meas = str(oldentry['Height']['Imperial']['Minimum']['Feet'])+"' "
            meas += str(oldentry['Height']['Imperial']['Minimum']['Inches'])+'" to'
            meas = str(oldentry['Height']['Imperial']['Maximum']['Feet'])+"' "
            meas += str(oldentry['Height']['Imperial']['Maximum']['Inches'])+'" /'
            meas += str(oldentry['Height']['Metric']['Minimum']['Meters'])+'m '
            if oldentry['Height']['Category']['Minimum']==oldentry['Height']['Category']['Maximum']:
                meas += ' to '+str(oldentry['Height']['Metric']['Maximum']['Meters'])+'m '
                meas += '('+oldentry['Height']['Category']['Minimum']+')'
            else:
                meas += '('+oldentry['Height']['Category']['Minimum'][0]+') '
                meas += ' to '+str(oldentry['Height']['Metric']['Maximum']['Meters'])+'m '
                meas += '('+oldentry['Height']['Category']['Maximum'][0]+') '
        formentry['Size']+='Height: '+meas+'\n'
        if oldentry['Weight']['Metric']['Minimum']['Kilograms'] == oldentry['Weight']['Metric']['Maximum']['Kilograms']:
            meas = str(oldentry['Weight']['Imperial']['Minimum']['Pounds'])+' lbs. /'
            meas += str(oldentry['Weight']['Metric']['Minimum']['Kilograms'])+' kg '
            meas += '('+str(oldentry['Weight']['WeightClass']['Minimum'])+')'
        else:
            meas = str(oldentry['Weight']['Imperial']['Minimum']['Pounds'])+' lbs. to'
            meas += str(oldentry['Weight']['Imperial']['Maximum']['Pounds'])+' lbs. /'
            meas += str(oldentry['Weight']['Metric']['Minimum']['Kilograms'])+' kg '
            if oldentry['Weight']['WeightClass']['Minimum']==oldentry['Weight']['WeightClass']['Maximum']:
                meas += ' to '+str(oldentry['Weight']['Metric']['Maximum']['Kilograms'])+' kg '
                meas += '('+str(oldentry['Weight']['WeightClass']['Minimum'])+')'
            else:
                meas += '('+str(oldentry['Weight']['WeightClass']['Minimum'][0])+') '
                meas += ' to '+str(oldentry['Weight']['Metric']['Maximum']['Kilograms'])+' kg '
                meas += '('+str(oldentry['Weight']['WeightClass']['Maximum'][0])+') '
        formentry['Size']+='Weight: '+meas
        maxlength = max(maxlength,len(formentry['Size']))
        #Breeding Entry
        formentry['Breeding']+='Breeding Information:\n'
        formentry['Breeding']+='Gender Ratio: '
        if oldentry['BreedingData']['HasGender']:
            formentry['Breeding']+= str(oldentry['BreedingData']['MaleChance']*100)+'% M / '
            formentry['Breeding']+= str(oldentry['BreedingData']['FemaleChance']*100)+'% F\n'
        else:
            formentry['Breeding']+='No Gender\n'
        formentry['Breeding']+='Egg Group: '+oldentry['BreedingData']['EggGroups'][0]
        formentry['Breeding']+=(' / '+oldentry['BreedingData']['EggGroups'][1] if len(oldentry['BreedingData']['EggGroups'])>1 else '')
        if oldentry['Species'] == oldentry['EvolutionStages'][0]['Species']:
            formentry['Breeding']+='\nAverage Hatch Rate: '+str(oldentry['BreedingData']['HatchRate'])+' Days'
        maxlength = max(maxlength,len(formentry['Breeding']))
        #Environment Entry
        formentry['Environment']+='Diet: '+', '.join(oldentry['Environment']['Diet'])+'\n'
        formentry['Environment']+='Habitat: '+', '.join(oldentry['Environment']['Habitats'])
        maxlength = max(maxlength,len(formentry['Environment']))
        #Capabilities Entry
        formentry['Capabilities']+='Capability List:\n'
        for k in oldentry['Capabilities']:
            formentry['Capabilities']+=k['CapabilityName']
            if k['CapabilityName']=='Naturewalk':
                formentry['Capabilities']+='('+k['Value']+')'
            elif k['Value']!='':
                formentry['Capabilities']+=' '+k['Value']
            formentry['Capabilities']+=', '
        formentry['Capabilities']=formentry['Capabilities'][:-2]
        maxlength = max(maxlength,len(formentry['Capabilities']))
        #Skills Entry
        formentry['Skills']+='Skill List:\n'
        for k in oldentry['Skills']:
            formentry['Skills']+=k['SkillName']+' '+k['DiceRank']+', '
        formentry['Skills']=formentry['Skills'][:-2]
        maxlength = max(maxlength,len(formentry['Skills']))
        #Level-Up Entry
        formentry['Level-Up']+='Level Up Move List:'
        for k in oldentry['LevelUpMoves']:
            newmove = str(k['LevelLearned'])+' '+k['Name']
            if k['Name'] in movedata:
                newmove += ' - ' + movedata[k['Name']]['Type']
                if movedata[k['Name']]['Type'] in oldentry['Types']:
                    newmove = '\n**'+newmove+'**'
                elif movedata[k['Name']]['Type'] in futuretypes:
                    newmove = '\n_'+newmove+'_'
                else:
                    newmove = '\n'+newmove
            else:
                print('Missing Move: '+k['Name'])
            formentry['Level-Up'] += newmove
        maxlength = max(maxlength,len(formentry['Level-Up']))
        #TMs Entry
        if oldentry['TmHmMoves']==[]:
            formentry['TMs']+='No TMs or HMs'
        else:
            formentry['TMs']+='TM/HM Move List:'
            for k in oldentry['TmHmMoves']:
                newmove = k['TechnicalMachineId']+' '+k['Name']
                if k['Name'] in movedata:
                    if movedata[k['Name']]['Type'] in oldentry['Types']:
                        newmove = '**'+newmove+'**'
                    elif movedata[k['Name']]['Type'] in futuretypes:
                        newmove = '_'+newmove+'_'
                else:
                    print('Missing Move: '+k['Name'])
                formentry['TMs'] += newmove+', '
            formentry['TMs'] = formentry['TMs'][:-2]
        maxlength = max(maxlength,len(formentry['TMs']))
        #Egg Entry
        if oldentry['EggMoves']==[]:
            formentry['Egg']+='No Egg Moves'
        else:
            formentry['Egg']+='Egg Move List:'
            for k in oldentry['EggMoves']:
                newmove = k['Name']
                if k['Name'] in movedata:
                    if movedata[k['Name']]['Type'] in oldentry['Types']:
                        newmove = '**'+newmove+'**'
                    elif movedata[k['Name']]['Type'] in futuretypes:
                        newmove = '_'+newmove+'_'
                else:
                    print('Missing Move: '+k['Name'])
                formentry['Egg'] += newmove+', '
            formentry['Egg'] = formentry['Egg'][:-2]
        maxlength = max(maxlength,len(formentry['Egg']))
        #Tutor Entry
        if oldentry['TutorMoves']==[]:
            formentry['Tutor']+='No Tutor Moves'
        else:
            formentry['Tutor']+='Tutor Move List:'
            for k in oldentry['TutorMoves']:
                newmove = k['Name']
                if k['Natural']:
                    newmove+=' (N)'
                if k['Name'] in movedata:
                    if movedata[k['Name']]['Type'] in oldentry['Types']:
                        newmove = '**'+newmove+'**'
                    elif movedata[k['Name']]['Type'] in futuretypes:
                        newmove = '_'+newmove+'_'
                else:
                    print('Missing Move: '+k['Name'])
                formentry['Tutor'] += newmove+', '
            formentry['Tutor'] = formentry['Tutor'][:-2]
        maxlength = max(maxlength,len(formentry['Tutor']))
        #Mega Entry
        if oldentry['MegaEvolutions']==[]:
            formentry['Mega']+='No Mega Evolutions'
        else:
            for k in oldentry['MegaEvolutions']:
                formentry['Mega']+=k['Name']+'\nType:'
                if k['Types']==oldentry['Types']:
                    formentry['Mega']+='Unchanged'
                else:
                    formentry['Mega']+=k['Types'][0]+('/'+k['Types'][1] if len(k['Types'])>1 else '')
                formentry['Mega']+='\nAbility:'+k['Ability']['Name']+'\nStats: '
                for stat in ['HP','Attack','Defense','Special Attack','Special Defense','Speed']:
                    if k['StatBonuses'][stat.replace(' ','')]>0:
                        formentry['Mega']+='+'+str(k['StatBonuses'][stat.replace(' ','')])+" "+stat+', '
                    elif k['StatBonuses'][stat.replace(' ','')]<0:
                        formentry['Mega']+=str(k['StatBonuses'][stat.replace(' ','')])+" "+stat+', '
                formentry['Mega'] = formentry['Mega'][:-2]
                formentry['Mega'] += '\n\n'
            formentry['Mega'] = formentry['Mega'][:-2]
        maxlength = max(maxlength,len(formentry['Mega']))
        #Defining form structure
        work.append((j,formentry))
        s = olddata[j]["Form"]
        work.append((s.split(' ')[0],j))
        work.append(('('+s.split(' ')[0]+')',j))
        if len(j.split(':'))>1:
            work.append((j.split(':')[1],j))
            work.append(('('+j.split(':')[1]+')',j))
    newentry = OrderedDict(work)    
    dexdata[olddata[i]["Species"]]=newentry
print(maxlength)
with open('dexdata.json','w') as data_file:    
    json.dump(dexdata,data_file,indent=4)