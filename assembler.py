#!/usr/bin/env python3
"""Hack assembler (Nand to Tetris capstone, Part B).
Usage:  python assembler.py Prog.asm [K or roll no.]      -> writes Prog.hack
K = last two digits of your roll number (you may pass the full roll number). K mod 3 picks the extra feature:
  0 -> symbols.txt   1 -> clear error messages with line numbers   2 -> duplicate-label warning
"""
import re, sys

K = 41  # <-- change to the last two digits of YOUR roll number

COMP = {'0': '101010', '1': '111111', '-1': '111010', 'D': '001100', 'A': '110000',
        '!D': '001101', '!A': '110001', '-D': '001111', '-A': '110011', 'D+1': '011111',
        'A+1': '110111', 'D-1': '001110', 'A-1': '110010', 'D+A': '000010', 'D-A': '010011',
        'A-D': '000111', 'D&A': '000000', 'D|A': '010101'}
JUMP = {'': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011',
        'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'}
PREDEFINED = {'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4, 'SCREEN': 16384, 'KBD': 24576}
PREDEFINED.update({f'R{i}': i for i in range(16)})
NAME = re.compile(r'^[A-Za-z_.$:][\w.$:]*$')


def clean(line):
    return re.sub(r'\s+', '', line.split('//')[0])


def assemble(text):
    symbols = dict(PREDEFINED)
    labels, errors, warnings, instrs = set(), [], [], []

    # ---- First reading: drop comments/blank lines, note label positions ----
    pc = 0
    for n, raw in enumerate(text.splitlines(), 1):
        line = clean(raw)
        if not line:
            continue
        if line.startswith('(') and line.endswith(')'):
            name = line[1:-1]
            if not NAME.match(name):
                errors.append(f'Line {n}: invalid label "{name}"')
                continue
            if name in labels:
                warnings.append(f'Line {n}: warning - label ({name}) is written twice')
            labels.add(name)
            symbols[name] = pc
        else:
            instrs.append((n, line))
            pc += 1

    # ---- Second reading: translate to 16 bits, allocate variables from 16 ----
    next_var, out = 16, []
    for n, line in instrs:
        if line[0] == '@':
            arg = line[1:]
            if arg.isdigit() and int(arg) <= 32767:
                value = int(arg)
            elif NAME.match(arg):
                if arg not in symbols:
                    symbols[arg] = next_var
                    next_var += 1
                value = symbols[arg]
            else:
                errors.append(f'Line {n}: invalid instruction "{line}"')
                continue
            out.append(format(value, '016b'))
            continue
        dest, comp, jump = '', line, ''
        if '=' in comp:
            dest, comp = comp.split('=', 1)
        if ';' in comp:
            comp, jump = comp.split(';', 1)
        key = comp.replace('M', 'A')
        if (key not in COMP or jump not in JUMP
                or not re.fullmatch(r'[ADM]*', dest) or len(set(dest)) != len(dest)):
            errors.append(f'Line {n}: invalid instruction "{line}"')
            continue
        a = '1' if 'M' in comp else '0'
        d = ''.join('1' if c in dest else '0' for c in 'ADM')
        out.append('111' + a + COMP[key] + d + JUMP[jump])

    user_syms = {k: v for k, v in symbols.items() if k not in PREDEFINED}
    return out, user_syms, errors, warnings


def main():
    if len(sys.argv) < 2:
        sys.exit('Usage: python assembler.py Prog.asm [K]')
    k = int(re.sub(r'\D', '', sys.argv[2])[-2:]) if len(sys.argv) > 2 else K
    path = sys.argv[1]
    with open(path) as f:
        out, syms, errors, warnings = assemble(f.read())

    if errors:                       # never crash: print clear messages instead
        print('\n'.join(errors))
        sys.exit(1)
    if k % 3 == 2:                   # extra feature: duplicate-label warning
        for w in warnings:
            print(w)
    if k % 3 == 0:                   # extra feature: symbols.txt
        with open('symbols.txt', 'w') as f:
            f.write('\n'.join(f'{n}={a}' for n, a in syms.items()) + '\n')
    hack = re.sub(r'\.asm$', '', path) + '.hack'
    with open(hack, 'w') as f:
        f.write('\n'.join(out) + '\n')
    print(f'{hack}: {len(out)} instructions')


if __name__ == '__main__':
    main()
