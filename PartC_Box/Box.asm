// Box.asm  -  Capstone: Make the Computer Draw a Box
// Name: Ekta Singh   Roll no: 2501730327   K = 27
// Box: starts at row 27, 20 rows tall, 16 * ((27 mod 4) + 1) = 64 pixels wide (4 words)
// Row 27 starts at SCREEN + 32*27 = 16384 + 864 = 17248
// While any key is pressed the box is black; when released it is white.

(LOOP)
    @KBD
    D=M
    @PRESSED
    D;JNE           // key pressed -> paint black
    @color
    M=0             // no key -> paint white (erase)
    @PAINT
    0;JMP
(PRESSED)
    @color
    M=-1            // all 16 bits set = black
(PAINT)
    @17248          // address of row 27, word 0
    D=A
    @addr
    M=D
    @20
    D=A
    @rows
    M=D             // rows = 20
(ROWLOOP)
    @color
    D=M
    @addr
    A=M
    M=D             // word 0 (pixels 0-15)
    A=A+1
    M=D             // word 1 (pixels 16-31)
    A=A+1
    M=D             // word 2 (pixels 32-47)
    A=A+1
    M=D             // word 3 (pixels 48-63)
    @32
    D=A
    @addr
    M=D+M           // go to the next row (+32 words)
    @rows
    MD=M-1
    @ROWLOOP
    D;JGT           // repeat until all 20 rows are done
    @LOOP
    0;JMP
