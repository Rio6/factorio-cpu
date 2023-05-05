# Factorio CPU
Yet another CPU implementation in Factorio.

The main goal of this implementation is to run operations at 60Hz (one update per game tick).

## Files
- progs - programs that runs on the CPU
  - chess - an interactive chess board
  - hellworld - prints "hello world" on the display
  - fibonacci - calculates Fibonacci sequence at 60Hz
  - paint - draw on the display using the chests input
- assembler.py  
  The assembler. Usage: `python assembler.py -i <input file> -o <output file>`. By default, input file and output file are stdin and stdout.
- cpu.blueprint
  The blueprint string of the CPU
- decode.py
  Command line tool to decode Factorio blueprint into json
- encode.py
  Command line tool to encode json into Factorio blueprint
- factorio_bp.py
  Code to handle Factorio blueprint stuff
- registers.py
  Helper code to generate the registers in the CPU. Rest of the CPU are manually constructed in game.
- rom.py
  Code to generate ROM as blueprint strings containing constant combinators

## Instructions and Registers
![Image](https://user-images.githubusercontent.com/15951245/236565149-c926879f-af84-42bf-932a-56dbc77fdc88.png)
![Image](https://user-images.githubusercontent.com/15951245/236565095-01f072c1-e77e-4bdc-bf49-3d95f976ed91.png)
![Image](https://user-images.githubusercontent.com/15951245/236565188-db346269-f815-4791-8883-29c777dd3406.png)

## Video Demo
[![Video](https://img.youtube.com/vi/WpxZ9LE9LhM/0.jpg)](https://www.youtube.com/watch?v=WpxZ9LE9LhM)
