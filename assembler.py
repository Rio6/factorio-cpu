import sys, ast
from getopt import getopt
from rom import generate_rom
from factorio_bp import encode_bp

src_regs = {
   'dec'   : -2,
   'inc'   : -1,
   'immed' : 1,
   'rd'    : 2,
   'add'   : -3,
   'sub'   : 4,
   'mul'   : 5,
   'div'   : 6,
   'mod'   : 7,
   'exp'   : 8,
   'ls'    : 9,
   'rs'    : 10,
   'and'   : 11,
   'or'    : 12,
   'xor'   : 13,
   'eq'    : 14,
   'ne'    : 15,
   'lt'    : 16,
   'gt'    : 17,
   'le'    : 18,
   'ge'    : 19,
   'a'     : 20,
   'b'     : 21,
   'x'     : 22,
   'y'     : 23,
   'z'     : 24,
}

dst_regs = {
   'a': 'A',
   'b': 'B',
   'x': 'X',
   'y': 'Y',
   'z': 'Z',
   'jmp': 'J',
   'cj': 'K',
   'cd': 'C',
   'ra': 'R',
   'wa': 'W',
   'wd': 'L',
}

class Controls:
   def __init__(self, *args, offset=1):
      self.controls = []
      self.offset = offset
      self.merge = False;

   def add(self, control):
      if self.merge and len(self.controls) > 0:
         for k, v in control.items():
            if k in self.controls[-1].keys() and self.controls[-1][k] != v:
               raise ValueError("can not merge instructions with conflicting controls")
         self.controls[-1].update(control)
      else:
         self.controls.append(control)
      self.merge = False

   def merge_next(self):
      self.merge = True

   def current_addr(self):
      return len(self.controls) + self.offset

   def __iter__(self):
      return iter(self.controls)

   def __repr__(self):
      return self.controls.__repr__()

def genmov(dst, src, data=None):
   dst = dst.lower().split(',')
   src = src.lower()
   if data:
      return {**{dst_regs[d]: src_regs[src] for d in dst}, 'D': data}
   else:
      return {dst_regs[d]: src_regs[src] for d in dst}

def main(args):
   fdi = sys.stdin
   fdo = sys.stdout
   debug = False
   offset = 1
   romoffset = 1

   for [k, v] in getopt(args[1:], 'i:o:s:d')[0]:
      match k:
         case '-i':
            fdi = open(v, 'r')
         case '-o':
            fdo = open(v, 'w')
         case '-s':
            romoffset = int(v)
         case '-d':
            debug = True

   controls = Controls(offset=offset)
   labels = {}
   consts = {}
   romaddr = {}
   romdata = []

   # convert each line to control signals
   for line in fdi:
      merge_next = '\\' in line
      line = line.strip(' \n\r\t\\')

      match line.split(' '):
         case ['mov', dst, src]:
            if src.isnumeric():
               # mov immediate
               controls.add(genmov(dst, 'immed', int(src)))
            elif src[0] in ['.', '#']:
               # mov immediate with build time variable
               controls.add(genmov(dst, 'immed', src))
            else:
               # mov register
               controls.add(genmov(dst, src))

         case ['inc', reg]:
            controls.add(genmov(reg, 'inc'))

         case [j, tgt] if j[0] == 'j':
            cond = j[1:]
            immed = None

            if tgt.isnumeric():
               # jump immediete
               immed = int(tgt)

            elif tgt[-1] == ':':
               # jump to label, use as place holder and set values later
               immed = tgt

            else:
               # jump to register
               pass

            if not cond:
               if immed is not None:
                  controls.add(genmov('jmp', 'immed', immed))
               else:
                  controls.add(genmov('jmp', tgt))
            else:
               if immed is not None:
                  controls.add(genmov('cj', cond))
                  controls.add({'D': immed})
               else:
                  controls.add({
                     **genmov('cj', cond),
                     **genmov('cd', tgt)
                  })
                  controls.add({})

         case ['noop']:
            controls.add({})

         case [label] if len(label) > 1 and label[-1] == ':':
            # labels
            if label in labels:
               raise ValueError(f"duplicated label {label}")
            labels[label] = controls.current_addr()

         case [name, value] if len(name) > 1 and name[0] == '#':
            # constant define
            if not value.isnumeric():
               raise ValueError("only int constant is supported")
            consts[name] = int(value)

         case [name, *values] if len(name) > 1 and name[0] == '.':
            # data in rom
            romaddr[name] = len(romdata) + romoffset

            for vv in values:
               vv = ast.literal_eval(vv)
               if type(vv) == str:
                  vv = [ord(c) for c in vv]
               elif type(vv) == int:
                  vv = [vv]
               else:
                  raise ValueError(f"only int and string data is supported")

               for v in vv:
                  romdata.append({'D': v})

         case ['']:
            pass

         case _:
            raise ValueError(f"error parsing {line}")

      if merge_next:
         controls.merge_next()

   # populate labels, constants, rom addresses
   for control in controls:
      d = control.get('D')
      if type(d) == str:
         if d[-1] == ':':
            if d not in labels:
               print(f"unknown label {d}", file=sys.stderr)
               return 1
            control['D'] = labels[d]

         if d[0] == '.':
            if d not in romaddr:
               print(f"unknown name {d}", file=sys.stderr)
               return 1
            control['D'] = romaddr[d]

         if d[0] == '#':
            if d not in consts:
               print(f"unknown constant {d}", file=sys.stderr)
               return 1
            control['D'] = consts[d]

   if debug:
      fdo.write(repr(controls) + '\n')
      fdo.write(repr(romdata) + '\n')
   else:
      # generate blueprints for 2 roms
      controlbp = generate_rom(controls.controls, start_addr=offset, columns=10)
      romdatabp = generate_rom(romdata, start_addr=romoffset, columns=10, entity_start=len(controlbp['blueprint']['entities'])+1)

      # merge blueprints
      for e in romdatabp['blueprint']['entities']:
         e['position']['x'] += 14
      controlbp['blueprint']['entities'] += romdatabp['blueprint']['entities']

      # print blueprint
      fdo.write(encode_bp(controlbp) + '\n')

if __name__ == '__main__':
   try:
      sys.exit(main(sys.argv))
   except ValueError as e:
      print(e, file=sys.stderr)
