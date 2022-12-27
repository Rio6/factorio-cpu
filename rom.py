import sys, copy, json
from factorio_bp import encode_bp

bp_template = {
   'blueprint': {
      'icons': [{'signal':{'type':'virtual','name':'signal-R'},'index':1},{'signal':{'type':'virtual','name':'signal-O'},'index':2},{'signal':{'type':'virtual','name':'signal-M'},'index':3}],
      'entities': [],
      'item': 'blueprint',
      'version': 281479276396544
   }
}

head_template = [
   {
      'entity_number': 0,
      'name': 'arithmetic-combinator',
      'position': {'x':0, 'y':0},
      'direction': 4,
      'control_behavior':{'arithmetic_conditions':{'first_signal':{'type':'virtual','name':'signal-D'},'second_constant':-1,'operation':'*','output_signal':{'type':'virtual','name':'signal-D'}}},
      'connections': {'1':{'red':[{'entity_id':1,'circuit_id':1}]},'2':{'red':[{'entity_id':1,'circuit_id':2}],'green':[{'entity_id':1,'circuit_id':2}]}}
   },
]

cell_template = [
   {
      'entity_number': 0,
      'name': 'decider-combinator',
      'position': {'x':1,'y':0},
      'direction': 4,
      'control_behavior':{'decider_conditions':{'first_signal':{'type':'virtual','name':'signal-D'},'constant':123,'comparator':'=','output_signal':{'type':'virtual','name':'signal-everything'},'copy_count_from_input':True}},
      'connections': {'1':{'green':[{'entity_id':1}],'red':[{'entity_id':2,'circuit_id':1}]},'2':{'red':[{'entity_id':2,'circuit_id':2}],'green':[{'entity_id':2,'circuit_id':2}]}}
   },
   {
      'entity_number': 0,
      'name': 'constant-combinator',
      'position': {'x':1,'y':-1.5},
      'direction': 4,
      'control_behavior': {'filters':[]}
   }
]

comb_template = {'signal':{'type':'virtual','name':'signal-D'},'count':1,'index':1}

def generate_rom(data, start_addr=1, columns=16, addr_signal='D', entity_start=0):

   columns -= 1 # there's an extra combinator in the front

   def update_number(entity):
      entity['entity_number'] = update_number.count
      for node in entity.get('connections', {}).values():
         for wire in node.values():
            for conn in wire:
               conn['entity_id'] += update_number.count
      update_number.count += 1
   update_number.count = entity_start

   bp = copy.deepcopy(bp_template)

   head = copy.deepcopy(head_template)
   update_number(head[0])

   bp['blueprint']['entities'] += head

   for i in range(0, len(data)):
      for cell in cell_template:
         entity = copy.deepcopy(cell)
         update_number(entity)
         entity['position']['x'] += i % columns if (i // columns) % 2 == 0 else columns - i % columns - 1
         entity['position']['y'] -= i // columns * 3

         ctl = entity.get('control_behavior', {})
         cond = ctl.get('decider_conditions', {})

         if 'constant' in cond:
            cond['constant'] = start_addr + i
            cond['first_signal']['name'] = 'signal-' + addr_signal
            if addr_signal in data[i]:
               cond['constant'] += data[i][addr_signal]

         if 'filters' in ctl:
            for j, s in enumerate(data[i]):
               comb = copy.deepcopy(comb_template)
               comb['index'] = j+1
               comb['count'] = data[i][s]
               comb['signal']['name'] = 'signal-' + s
               ctl['filters'].append(comb)

         bp['blueprint']['entities'].append(entity)

   return bp
