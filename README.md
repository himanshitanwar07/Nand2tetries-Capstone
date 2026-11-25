# Capstone Project: Make the Computer Draw a Box

**Course:** Nand to Tetris - I (ETCNTC301), School of Engineering & Technology, K.R. Mangalam University
**Name:** Ekta Singh
**Roll No:** 2501730327
**K (last two digits of roll no):** 27

## My personal values
| Item | Value |
|---|---|
| K | 27 |
| Box start row | 27 |
| Box height | 20 rows |
| Box width | 16 x ((27 mod 4) + 1) = 64 pixels (4 words) |
| Row 27 address | SCREEN + 32*27 = 16384 + 864 = 17248 |
| Extra assembler feature | K mod 3 = 0 -> save labels and variables to `symbols.txt` |

## Folder structure
```
capstone/
  PartA_Computer/        CPU.hdl, Memory.hdl, Computer.hdl + test screenshots
  PartB_Assembler/       assembler.py, symbols.txt
  PartC_Box/             Box.asm, Box.hack, screenshot of the box
  website_dashboard/     dashboard.py (web dashboard running Box.hack)
  report/                Report outline (3-4 page report is submitted on ZOSIMA)
```

## How to run
Assemble the box program with my own assembler:
```
cd PartB_Assembler
python assembler.py ../PartC_Box/Box.asm
```
(Run it from the folder of the .asm file if you want `Box.hack` next to it.)

Start the dashboard (shows name and roll no, and runs Box.hack on an emulated Hack screen):
```
cd website_dashboard
python dashboard.py
```
Then open http://localhost:8000. Hold the button or any key to draw the box.
