# Part B - Assembler in Python (3 marks)

`assembler.py` turns a Hack `.asm` file into a `.hack` file.

- First reading: removes comments and blank lines, records the ROM address of each label.
- Second reading: converts every line to 16 bits. New variables get RAM addresses 16, 17, 18, ...
- Extra feature (K = 27, K mod 3 = 0): writes all labels and variables with their addresses to `symbols.txt`.
- Errors such as an invalid instruction are reported with the line number.

Usage:
```
python assembler.py File.asm
```

Checklist - output must match the official assembler:
- [ ] Add.asm
- [ ] Max.asm
- [ ] Rect.asm
- [ ] Pong.asm
