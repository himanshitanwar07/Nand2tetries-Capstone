"""
Hack assembler (Capstone Part B)
Name: Ekta Singh   Roll no: 2501730327   K = 27
Extra feature (K mod 3 == 0): save all labels and variables to symbols.txt

Usage:  python assembler.py Box.asm      ->  Box.hack + symbols.txt
"""
import sys

# ---- tables ----------------------------------------------------------------
_COMP_A0 = {                      # 6 control bits, used when a = 0
    "0": "101010", "1": "111111", "-1": "111010",
    "D": "001100", "A": "110000", "!D": "001101", "!A": "110001",
    "-D": "001111", "-A": "110011", "D+1": "011111", "A+1": "110111",
    "D-1": "001110", "A-1": "110010", "D+A": "000010", "D-A": "010011",
    "A-D": "000111", "D&A": "000000", "D|A": "010101",
}
COMP = {k: "0" + v for k, v in _COMP_A0.items()}
for k, v in _COMP_A0.items():     # a = 1: same functions but with M instead of A
    if "A" in k:
        COMP[k.replace("A", "M")] = "1" + v

JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011",
        "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}

PREDEFINED = {"SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
              "SCREEN": 16384, "KBD": 24576}
PREDEFINED.update({f"R{i}": i for i in range(16)})


class AsmError(Exception):
    pass


# ---- helpers ---------------------------------------------------------------
def _dest_bits(n, dest):
    if dest and (set(dest) - set("ADM") or len(set(dest)) != len(dest)):
        raise AsmError(f"Line {n}: invalid destination '{dest}'")
    return ("1" if "A" in dest else "0") + \
           ("1" if "D" in dest else "0") + \
           ("1" if "M" in dest else "0")


def _encode_c(n, code):
    dest, jump = "", ""
    if "=" in code:
        dest, code = code.split("=", 1)
    if ";" in code:
        code, jump = code.split(";", 1)
    if code not in COMP:
        raise AsmError(f"Line {n}: invalid instruction (bad computation '{code}')")
    if jump not in JUMP:
        raise AsmError(f"Line {n}: invalid jump '{jump}'")
    return "111" + COMP[code] + _dest_bits(n, dest) + JUMP[jump]


# ---- main assembler ----------------------------------------------------------
def assemble(text):
    """Two readings of the source. Returns a dict with the machine code and tables."""
    # First reading: remove comments/blank lines, record where each label is.
    lines = []
    for n, raw in enumerate(text.splitlines(), 1):
        code = raw.split("//")[0]
        code = "".join(code.split())
        if code:
            lines.append((n, code))

    symbols = dict(PREDEFINED)
    labels = {}
    rom_addr = 0
    instructions = []
    for n, code in lines:
        if code.startswith("("):
            if not code.endswith(")") or len(code) < 3:
                raise AsmError(f"Line {n}: invalid label '{code}'")
            name = code[1:-1]
            if name in labels:
                raise AsmError(f"Line {n}: label '{name}' defined twice")
            labels[name] = rom_addr
            symbols[name] = rom_addr
        else:
            instructions.append((n, code))
            rom_addr += 1

    # Second reading: translate every line to 16 bits; new variables start at RAM[16].
    variables = {}
    next_var = 16
    binary = []
    for n, code in instructions:
        if code.startswith("@"):
            sym = code[1:]
            if not sym:
                raise AsmError(f"Line {n}: invalid instruction (empty @)")
            if sym.isdigit():
                value = int(sym)
            else:
                if sym not in symbols:
                    symbols[sym] = next_var
                    variables[sym] = next_var
                    next_var += 1
                value = symbols[sym]
            if value > 32767:
                raise AsmError(f"Line {n}: address {value} is too large")
            binary.append(format(value, "016b"))
        else:
            binary.append(_encode_c(n, code))

    return {"binary": binary, "labels": labels, "variables": variables}


def symbols_text(result):
    """Extra feature (K mod 3 == 0): all labels and variables with their addresses."""
    out = ["# Labels (ROM addresses)"]
    out += [f"{name} = {addr}" for name, addr in result["labels"].items()]
    out += ["", "# Variables (RAM addresses)"]
    out += [f"{name} = {addr}" for name, addr in result["variables"].items()]
    return "\n".join(out) + "\n"


def main(path):
    with open(path) as f:
        text = f.read()
    try:
        result = assemble(text)
    except AsmError as e:
        print(e)
        sys.exit(1)
    base = path.rsplit(".", 1)[0]
    with open(base + ".hack", "w") as f:
        f.write("\n".join(result["binary"]) + "\n")
    with open("symbols.txt", "w") as f:
        f.write(symbols_text(result))
    print(f"Wrote {base}.hack ({len(result['binary'])} lines) and symbols.txt")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assembler.py File.asm")
        sys.exit(1)
    main(sys.argv[1])
