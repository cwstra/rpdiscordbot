# -*- coding: UTF-8 -*-
import json

table = {}

table["Deflect"]="""Deflect
Shield
Range: Self
Reaction
Use Requirement: You are the target of a Melee, Cone, Line,hspace{1cm} Sweep, or Projectile attack
Effect: You resist the attack two additional steps."""

with open('bookdata.json','w') as data_file:    
    json.dump(table,data_file,indent=4)