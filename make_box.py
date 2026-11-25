#!/usr/bin/env python3
"""Generate Box.asm and Box.hack for YOUR K.
Usage:  python make_box.py 2501420041      (full roll number)
        python make_box.py 41              (or just K)
"""
import glob, importlib.util, os, re, sys


def _load_assembler():
    # works even if the file was renamed by the browser, e.g. "assembler (3).py"
    here = os.path.dirname(os.path.abspath(__file__))
    paths = [os.path.join(here, 'assembler.py')] + sorted(glob.glob(os.path.join(here, 'assembler*.py')))
    for path in paths:
        if os.path.isfile(path):
            spec = importlib.util.spec_from_file_location('hack_assembler', path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod.assemble
    sys.exit('assembler.py not found in the same folder as make_box.py')


assemble = _load_assembler()


def box_asm(k):
    w = k % 4 + 1                 # width in words (16 pixels each)
    addr = 16384 + 32 * k         # SCREEN + 32*row, box starts at row K
    return f"""// Box.asm  (K = {k})  - black box while any key is pressed
// Starts at row {k}, 20 rows tall, {16 * w} pixels wide ({w} word{'s' if w > 1 else ''})
// Start address = SCREEN + 32*{k} = {addr}
(LOOP)
@KBD
D=M
@PRESS
D;JNE
@color
M=0
@DRAW
0;JMP
(PRESS)
@color
M=-1
(DRAW)
@{addr}
D=A
@ptr
M=D
@20
D=A
@rows
M=D
(ROW)
@{w}
D=A
@cols
M=D
(COL)
@color
D=M
@ptr
A=M
M=D
@ptr
M=M+1
@cols
MD=M-1
@COL
D;JGT
@{32 - w}
D=A
@ptr
M=D+M
@rows
MD=M-1
@ROW
D;JGT
@LOOP
0;JMP
"""


if __name__ == '__main__':
    if len(sys.argv) < 2 or not re.sub(r'\D', '', sys.argv[1]):
        sys.exit('Usage: python make_box.py <roll number or K>')
    k = int(re.sub(r'\D', '', sys.argv[1])[-2:])
    text = box_asm(k)
    open('Box.asm', 'w').write(text)
    out, _, errors, _ = assemble(text)
    if errors:
        sys.exit('\n'.join(errors))
    open('Box.hack', 'w').write('\n'.join(out) + '\n')
    print(f'K = {k}: Box.asm + Box.hack written (start address {16384 + 32 * k}, '
          f'{16 * (k % 4 + 1)} px wide, rows {k}-{k + 19})')
