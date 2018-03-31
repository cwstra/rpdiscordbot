import json
x = 0
data = {}
data['Move']={}
data['Abil']={}
with open('Moves and Abilities.txt') as data_file:
    string = data_file.readline()
    while not(string in ["Moves Doxy wants DEAD\r\n",""]):
        print(repr(""))
        print(repr(string))
        print(""==string)
        print("GRAAAAH")
        if x==0:
            if string == 'Moves\n':
                x=1
            elif not(string in ["\ufeffAbilities\n","Updated Abilities\n","\n","________________\n","New Abilities\n"]):
                entry = string[9:].rstrip('\n')
                data['Abil'][entry]=""
                while not(string in ["\n","________________\n"]):
                    print("in"+repr(string))
                    data['Abil'][entry]+=string
                    string = data_file.readline()
        else:
            if not(string in ["\n","________________\n"] or string[-5:]=="Moves"):
                entry = string[:string.find(" - ")].rstrip('\n')
                data['Move'][entry]=""
                while not(string in ["\n","________________\n"] or string[-5:]=="Moves"):
                    data['Move'][entry]+=string
                    string = data_file.readline()
        string = data_file.readline()
with open('journeys.json','w') as data_file:
    json.dump(data,data_file,indent=4)
