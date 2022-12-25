import sys
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
      if self.merge and len(control) > 0:
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
   offset = 1
   debug = False

   for [k, v] in getopt(args[1:], 'i:o:s:d')[0]:
      match k:
         case '-i':
            fdi = open(v, 'r')
         case '-o':
            fdo = open(v, 'w')
         case '-s':
            try:
               offset = int(v)
            except ValueError:
               print(f"offset must be a number")
               return 1
         case '-d':
            debug = True

   controls = Controls(offset=offset)
   labels = {}

   # convert each line to control signals
   for line in fdi:
      merge_next = '\\' in line
      line = line.strip(' \n\r\t\\')

      match line.split(' '):
         case ['mov', dst, src]:
            if src.isnumeric():
               # mov immediate
               controls.add(genmov(dst, 'immed', int(src)))
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

         case ['']:
            pass

         case [label] if label[-1] == ':':
            # position of labels
            label = label[:-1]
            if label in labels:
               print(f"duplicated label {label}", file=sys.stderr)
               return 1
            labels[label] = controls.current_addr()

         case [op, *args]:
            print(f"unknown instruction {line}", file=sys.stderr)
            return 1

      if merge_next:
         controls.merge_next()

   # set label values
   for control in controls:
      d = control.get('D')
      if type(d) == str and d[-1] == ':':
         label = d[:-1]
         if label not in labels:
            print(f"unknown label {label}", file=sys.stderr)
            return 1
         control['D'] = labels[label]

   if debug:
      fdo.write(repr(controls))
   else:
      fdo.write(encode_bp(generate_rom(controls.controls, start=offset, columns=16)))

if __name__ == '__main__':
   sys.exit(main(sys.argv))
