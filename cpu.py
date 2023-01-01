import copy, json
from factorio_bp import encode_bp

blueprint = {
   'blueprint': {
      'icons': [{'signal':{'type':'virtual','name':'signal-R'},'index':1},{'signal':{'type':'virtual','name':'signal-O'},'index':2},{'signal':{'type':'virtual','name':'signal-M'},'index':3}],
      'entities': [],
      'item': 'blueprint',
      'version': 281479276396544
   }
}

head = [
   {
      'entity_number': 0,
      'name': 'arithmetic-combinator',
      'position': {'x':0, 'y':0},
      'direction': 2,
      'control_behavior':{'arithmetic_conditions':{'first_signal':{'type':'virtual','name':'signal-D'},'second_constant':-1,'operation':'*','output_signal':{'type':'virtual','name':'signal-D'}}},
      'connections': {'1':{'red':[{'entity_id':1,'circuit_id':1}]},'2':{'red':[{'entity_id':1,'circuit_id':2}],'green':[{'entity_id':1,'circuit_id':2}]}}
   },
   {
      'entity_number': 0,
      'name': 'arithmetic-combinator',
      'position': {'x':0, 'y':1},
      'direction': 2,
      'control_behavior':{'arithmetic_conditions':{'first_signal':{'type':'virtual','name':'signal-D'},'second_constant':-1,'operation':'*','output_signal':{'type':'virtual','name':'signal-D'}}},
      'connections': {'1':{'red':[{'entity_id':1,'circuit_id':1}]},'2':{'red':[{'entity_id':1,'circuit_id':2}],'green':[{'entity_id':1,'circuit_id':2}]}}
   },
   {
      'entity_number': 0,
      'name': 'decider-combinator',
      'position': {'x':0,'y':2},
      'direction': 2,
      'control_behavior':{'decider_conditions':{'first_signal':{'type':'virtual','name':'signal-X'},'constant':0,'comparator':'>=','output_signal':{'type':'virtual','name':'signal-D'},'copy_count_from_input':True}},
      'connections': {'1':{'red':[{'entity_id':1,'circuit_id':1}]},'2':{'red':[{'entity_id':1,'circuit_id':2}],'green':[{'entity_id':1,'circuit_id':2}]}}
   },
]

body = {
   'entity_number': 0,
   'name': 'decider-combinator',
   'position': {'x':0,'y':3},
   'direction': 2,
   'control_behavior':{'decider_conditions':{'first_signal':{'type':'virtual','name':'signal-X'},'constant':0,'comparator':'=','output_signal':{'type':'virtual','name':'signal-D'},'copy_count_from_input':True}},
   'connections': {'1':{'red':[{'entity_id':1,'circuit_id':1}]},'2':{'red':[{'entity_id':1,'circuit_id':2}],'green':[{'entity_id':1,'circuit_id':2}]}}
}

foot = [
   {
      'entity_number': 0,
      'name': 'decider-combinator',
      'position': {'x':0,'y':0},
      'direction': 2,
      'control_behavior':{'decider_conditions':{'first_signal':{'type':'virtual','name':'signal-X'},'constant':0,'comparator':'>','output_signal':{'type':'virtual','name':'signal-D'},'copy_count_from_input':True}},
   },
]

n = 0 # no connect
s = 1 # self connect
r = 2 # row connect
c = 4 # control connect

srcs = [0, -1, -1, -2, -2, 1, 1, 2, -3, -3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
dsts = [
   'J', 'C', 'A', 'B', 'X', 'Y', 'Z', 'R', 'W', 'L', #'K'
]
conns = [
   [s,  c,  s,  s,  s,  s,  s,  s,  s,  s], #  0
   [n,  n,  s,  s,  s,  s,  s,  s,  s,  s], # -1
   [n,  n,  r,  r,  r,  r,  r,  r,  r,  r], # -1
   [n,  n,  s,  s,  s,  s,  s,  s,  s,  s], # -2
   [n,  n,  r,  r,  r,  r,  r,  r,  r,  r], # -2
   [n,  n,  n,  n,  n,  n,  n,  n,  n,  n], #  1
   [n,  n,  n,  n,  n,  n,  n,  n,  n,  n], #  1
   [r,  r,  r,  r,  r,  r,  r,  r,  r,  r], #  2
   [r,  r,  r|s,r,  r,  r,  r,  r,  r,  r], # -3
   [r,  r,  r,  r|s,r,  r,  r,  r,  r,  r], # -3
   [r,  r,  r,  r,  r,  r,  r,  r,  r,  r], #  4
   [r,  r,  r,  r,  r,  r,  r,  r,  r,  r], #  5
   [r,  r,  r,  r,  r,  r,  r,  r,  r,  r], #  6
   [r,  r,  r,  r,  r,  r,  r,  r,  r,  r], #  7
   [r,  r,  r,  r,  r,  r,  r,  r,  r,  r], #  8
   [r,  r,  r,  r,  r,  r,  r,  r,  r,  r], #  9
   [r,  r,  r,  r,  r,  r,  r,  r,  r,  r], # 10
   [r,  r,  r,  r,  r,  r,  r,  r,  r,  r], # 11
   [r,  r,  r,  r,  r,  r,  r,  r,  r,  r], # 12
   [r,  r,  r,  r,  r,  r,  r,  r,  r,  r], # 13
   [n,  r,  r,  r,  r,  r,  r,  r,  r,  r], # 14
   [n,  r,  r,  r,  r,  r,  r,  r,  r,  r], # 15
   [n,  r,  r,  r,  r,  r,  r,  r,  r,  r], # 16
   [n,  r,  r,  r,  r,  r,  r,  r,  r,  r], # 17
   [n,  r,  r,  r,  r,  r,  r,  r,  r,  r], # 18
   [n,  r,  r,  r,  r,  r,  r,  r,  r,  r], # 19
   [n,  r,  r,  r,  r,  r,  r,  r,  r,  r], # 20
   [n,  r,  r,  r,  r,  r,  r,  r,  r,  r], # 21
   [r,  r,  r|s,r,  r,  r,  r,  r,  r,  r], # 22
   [r,  r,  r,  r|s,r,  r,  r,  r,  r,  r], # 23
   [r,  r,  r,  r,  r|s,r,  r,  r,  r,  r], # 24
   [r,  r,  r,  r,  r,  r|s,r,  r,  r,  r], # 25
   [r,  r,  r,  r,  r,  r,  r|s,r,  r,  r], # 26
]

rows = len(head) + len(srcs) + len(foot)
breaks = 5

count = 0
def update_number(entity):
   global count
   entity['entity_number'] = count
   for node in entity.get('connections', {}).values():
      for wire in node.values():
         for conn in wire:
            conn['entity_id'] += count
   count += 1

for col, dst in enumerate(dsts):
   hh = copy.deepcopy(head)
   for h in hh:
      update_number(h)
      h['position']['x'] += col*2 + col // breaks * 2

   col_conn = {
      'circuit_id': 2,
      'entity_id': hh[0]['entity_number'] + rows,
   }
   hh[0]['connections']['1']['red'].append({
      'circuit_id': 1,
      'entity_id': hh[0]['entity_number'] + rows,
   })

   hh[2]['control_behavior']['decider_conditions']['first_signal']['name'] = 'signal-' + dst

   blueprint['blueprint']['entities'] += hh

   for row, v in enumerate(srcs):
      b = copy.deepcopy(body)
      update_number(b)
      b['position']['y'] += row
      b['position']['x'] += col*2 + col // breaks * 2
      b['control_behavior']['decider_conditions']['first_signal']['name'] = 'signal-' + dst
      b['control_behavior']['decider_conditions']['constant'] = v
      blueprint['blueprint']['entities'].append(b)

      # connections
      for wire in ['green', 'red']:
         if wire not in b['connections']['1']:
            b['connections']['1'][wire] = []

      # connections of same rows
      if conns[row][col] & r:
         next_conn = next((i for i, v in enumerate(conns[row]) if i > col and conns[row][i] & r), -1)
         if next_conn > 0:
            b['connections']['1']['green'].append({
               'circuit_id': 1,
               'entity_id': b['entity_number'] + (next_conn - col) * rows,
            })

      # green connection to self (feedback)
      if conns[row][col] & s:
         b['connections']['1']['green'].append({
            'circuit_id': 2,
            'entity_id': b['entity_number'],
         })

      # red connection to self (control)
      if conns[row][col] & c:
         b['connections']['1']['red'].append({
            'circuit_id': 2,
            'entity_id': b['entity_number'],
         })

   ff = copy.deepcopy(foot)
   for f in ff:
      update_number(f)
      f['position']['x'] = col*2 + col // breaks * 2
      f['position']['y'] = len(srcs) + len(head)
      f['control_behavior']['decider_conditions']['first_signal']['name'] = 'signal-' + dst
      f['control_behavior']['decider_conditions']['constant'] = srcs[-1]

   blueprint['blueprint']['entities'] += ff

#print(json.dumps(blueprint))
print(encode_bp(blueprint))
