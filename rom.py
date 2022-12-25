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
      'position': {'x':-3, 'y':-10},
      'control_behavior':{'arithmetic_conditions':{'first_signal':{'type':'virtual','name':'signal-D'},'second_constant':-1,'operation':'*','output_signal':{'type':'virtual','name':'signal-D'}}},
      'connections': {'1':{'red':[{'entity_id':1,'circuit_id':1}]},'2':{'red':[{'entity_id':1,'circuit_id':2}],'green':[{'entity_id':1,'circuit_id':2}]}}
   },
   {
      'entity_number': 1,
      'name': 'decider-combinator',
      'position': {'x':-2,'y':-10},
      'control_behavior':{'decider_conditions':{'first_signal':{'type':'virtual','name':'signal-D'},'constant':123,'comparator':'<','output_signal':{'type':'virtual','name':'signal-D'},'copy_count_from_input':True}},
      'connections': {'1':{'red':[{'entity_id':2,'circuit_id':1}]},'2':{'red':[{'entity_id':2,'circuit_id':2}],'green':[{'entity_id':2,'circuit_id':2}]}}
   },
   {
      'entity_number': 2,
      'name': 'decider-combinator',
      'position': {'x':-1,'y':-10},
      'control_behavior':{'decider_conditions':{'first_signal':{'type':'virtual','name':'signal-D'},'constant':123,'comparator':'>=','output_signal':{'type':'virtual','name':'signal-D'},'copy_count_from_input':True}},
      'connections': {'1':{'red':[{'entity_id':3,'circuit_id':1}]},'2':{'red':[{'entity_id':3,'circuit_id':2}],'green':[{'entity_id':3,'circuit_id':2}]}}
   },
]

cell_template = [
   {
      'entity_number': 3,
      'name': 'decider-combinator',
      'position': {'x':0,'y':-10},
      'control_behavior':{'decider_conditions':{'first_signal':{'type':'virtual','name':'signal-D'},'constant':123,'comparator':'=','output_signal':{'type':'virtual','name':'signal-everything'},'copy_count_from_input':True}},
      'connections': {'1':{'green':[{'entity_id':4}],'red':[{'entity_id':5,'circuit_id':1}]},'2':{'red':[{'entity_id':5,'circuit_id':2}],'green':[{'entity_id':5,'circuit_id':2}]}}
   },
   {
      'entity_number': 4,
      'name': 'constant-combinator',
      'position': {'x':0,'y':-8.5},
      'control_behavior': {'filters':[]}
   }
]

comb_template = {'signal':{'type':'virtual','name':'signal-D'},'count':1,'index':1}

def generate_rom(data, start=1, columns=16, addr_signal='D'):

   def update_head_cond(entity, num):
      cond = entity.get('control_behavior', {}).get('decider_conditions')
      if 'constant' in cond:
         cond['constant'] = num

   bp = copy.deepcopy(bp_template)

   head = copy.deepcopy(head_template)
   update_head_cond(head[1], start)
   update_head_cond(head[2], start + len(data))
   bp['blueprint']['entities'] += head

   for i in range(0, len(data)):
      for cell in cell_template:
         entity = copy.deepcopy(cell)
         entity['entity_number'] += i * 2
         entity['position']['x'] += i % columns if (i // columns) % 2 == 0 else columns - i % columns - 1
         entity['position']['y'] += i // columns * 3

         ctl = entity.get('control_behavior', {})
         cond = ctl.get('decider_conditions', {})

         if 'constant' in cond:
            cond['constant'] = start + i
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

         for conn in entity.get('connections', {}).values():
            for wire in conn.values():
               for wire_conn in list(wire):
                  wire_conn['entity_id'] += i * 2
                  if not (0 <= wire_conn['entity_id'] < len(head_template) + len(data) * len(cell_template)):
                     wire.remove(wire_conn)

         bp['blueprint']['entities'].append(entity)

   return bp
