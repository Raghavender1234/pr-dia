# -*- coding: utf-8 -*-
"""
Populate Full 100 UPSC ESE-Style Questions for Topic 70 (ICT Module 1):
Computer Hardware, CPU Registers, Control Unit/ISA, Instruction Cycle,
Memory Hierarchy, Cache, Virtual Memory, I/O Subsystems, Printers & OS Architecture.
"""

import sys
sys.path.insert(0, r'C:\Users\brred\Desktop\AI_Assistant\App\backend')
from app import create_app, db
from app.models.question import Question, MCQOption
from app.models.topic import TopicContent
from app.models.mock_test import MockTest, MockTestQuestion

# 100 Questions Data
QUESTIONS_100 = [
    # ==================== SECTION A: CPU ARCHITECTURE & REGISTERS (Q1 to Q20) ====================
    {
        "q": "[UPSC ESE ICT Module 1 — CPU Registers]\nThe processor register that continuously holds the memory address of the next instruction to be fetched and executed is:",
        "opts": [("Instruction Register (IR)", False), ("Memory Buffer Register (MBR)", False), ("Program Counter (PC)", True), ("Accumulator (AC)", False)],
        "exp": "The Program Counter (PC) holds the memory address of the next instruction. After each instruction fetch, the PC automatically increments by instruction length (or branches on jump instructions)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — CPU Registers]\nWhich internal CPU register acts as a temporary holding buffer for data or instructions fetched directly from the system bus connected to memory?",
        "opts": [("Memory Address Register (MAR)", False), ("Memory Buffer Register (MBR / MDR)", True), ("Instruction Register (IR)", False), ("Program Counter (PC)", False)],
        "exp": "The Memory Buffer Register (MBR), also known as Memory Data Register (MDR), holds the data or machine instruction read from or written to memory."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — CPU Registers]\nUpon fetching an instruction word from primary memory, where is the operation code (opcode) immediately placed for decoding?",
        "opts": [("Program Counter (PC)", False), ("Instruction Register (IR)", True), ("Memory Address Register (MAR)", False), ("Accumulator (AC)", False)],
        "exp": "The Instruction Register (IR) holds the currently executing instruction while the Control Unit decodes its opcode and addressing mode."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — CPU Registers]\nIn single-accumulator processor architectures, the Accumulator (AC) is primarily used to:",
        "opts": [("Store memory segment base addresses", False), ("Hold intermediate arithmetic and logical results from the ALU", True), ("Decode microcode control words", False), ("Generate hardware interrupt vectors", False)],
        "exp": "The Accumulator (AC) is a general/special register that holds operands before an ALU operation and stores the intermediate result of the operation."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — CPU Registers]\nWhich register automatically increments its contents during the fetch phase before instruction decoding begins?",
        "opts": [("Program Counter (PC)", True), ("Memory Address Register (MAR)", False), ("Stack Pointer (SP)", False), ("Instruction Register (IR)", False)],
        "exp": "In the standard fetch cycle, the CPU performs: MAR <- PC, then PC <- PC + 1, and MBR <- M[MAR]. Thus, PC increments during the fetch phase."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Statement-I & Statement-II]\nStatement (I): Internal processor registers provide the fastest data access speeds in the entire computer memory hierarchy.\nStatement (II): Registers are fabricated directly on the processor die using flip-flop circuits and share the CPU internal clock without external bus propagation delays.\nWhich of the following is correct?",
        "opts": [
            ("Both Statement (I) and Statement (II) are individually true and Statement (II) is the correct explanation of Statement (I)", True),
            ("Both Statement (I) and Statement (II) are individually true, but Statement (II) is NOT the correct explanation of Statement (I)", False),
            ("Statement (I) is true, but Statement (II) is false", False),
            ("Statement (I) is false, but Statement (II) is true", False)
        ],
        "exp": "Both statements are true. Internal registers have access times < 0.5–1 ns because they are physically on-die flip-flops operating at full CPU core frequency."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Statement-I & Statement-II]\nStatement (I): The Memory Address Register (MAR) must be directly connected to the unidirectional CPU address bus.\nStatement (II): The Memory Buffer Register (MBR) is connected to the bidirectional CPU data bus to handle both read and write operations.\nWhich of the following is correct?",
        "opts": [
            ("Both Statement (I) and Statement (II) are individually true and Statement (II) is the correct explanation of Statement (I)", False),
            ("Both Statement (I) and Statement (II) are individually true, but Statement (II) is NOT the correct explanation of Statement (I)", True),
            ("Statement (I) is true, but Statement (II) is false", False),
            ("Statement (I) is false, but Statement (II) is true", False)
        ],
        "exp": "Both are true engineering facts: MAR connects to the address bus (CPU outputs addresses), while MBR connects to the bidirectional data bus (data enters on Read and leaves on Write)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Memory Volatility]\nWhich of the following storage components is strictly VOLATILE and loses its stored binary contents immediately upon removal of electrical power?",
        "opts": [("CPU General-Purpose Registers", True), ("Flash EEPROM", False), ("Mask ROM", False), ("Magnetic Hard Disk Drive", False)],
        "exp": "CPU registers (SRAM-based flip-flops) and dynamic RAM (DRAM) are volatile. Flash, ROM, and magnetic disks are non-volatile."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Match the Following]\nMatch List-I (CPU Register) with List-II (Designated Role):\nList-I:\nA. Program Counter (PC)\nB. Instruction Register (IR)\nC. Stack Pointer (SP)\nD. Memory Address Register (MAR)\nList-II:\n1. Holds address of the top of the call stack in RAM\n2. Holds memory address of next instruction to be fetched\n3. Holds current instruction being decoded by Control Unit\n4. Holds memory address targeted for read or write bus cycle\nSelect the correct code:",
        "opts": [
            ("A-2, B-3, C-1, D-4", True),
            ("A-3, B-2, C-1, D-4", False),
            ("A-2, B-1, C-3, D-4", False),
            ("A-4, B-3, C-1, D-2", False)
        ],
        "exp": "PC = Next instruction address (2); IR = Current instruction being decoded (3); SP = Top of stack in RAM (1); MAR = Target bus address for read/write (4)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — ALU Architecture]\nIn standard von Neumann CPU architectures, which register pair directly feeds operands into the Arithmetic Logic Unit (ALU) inputs?",
        "opts": [("Accumulator and Temporary Register / Operand Register", True), ("Program Counter and Memory Address Register", False), ("Instruction Register and Stack Pointer", False), ("Memory Buffer Register and Flag Register only", False)],
        "exp": "The ALU takes one operand from the Accumulator (or register file) and the second operand from a temporary operand register (or MBR), outputting the result back into the Accumulator."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Memory Classification]\nFrom an architectural standpoint, processor registers are categorized as:",
        "opts": [("Primary storage", False), ("Secondary auxiliary storage", False), ("Internal processor memory (Level 0)", True), ("Tertiary storage", False)],
        "exp": "Processor registers sit at Level 0 of the memory hierarchy, designated as internal processor storage directly accessible by the execution datapath."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — CPU Design Constraints]\nThe total number of general-purpose registers (GPRs) in modern CPU cores is strictly constrained (typically 16 to 64) primarily because:",
        "opts": [("Instruction word length restricts the number of address bits available to encode register identifiers, and multi-port register files consume expensive silicon area and power", True), ("Registers cannot operate at clock frequencies above 100 MHz", False), ("Operating systems cannot manage more than 32 registers", False), ("Flip-flops cannot be integrated alongside CMOS transistors", False)],
        "exp": "To reference a register in an instruction, $k$ bits encode $2^k$ registers (e.g. 5 bits for 32 registers). More registers lengthen instruction formats and drastically increase silicon routing area and capacitive load on multi-ported register files."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Branch Instructions]\nWhen an unconditional branch (e.g., JMP address) or conditional branch (e.g., JZ target) occurs, which register's value is directly updated?",
        "opts": [("Program Counter (PC)", True), ("Instruction Register (IR)", False), ("Memory Buffer Register (MBR)", False), ("Stack Pointer (SP)", False)],
        "exp": "Branching modifies the Program Counter (PC) by replacing its sequential increment value with the target jump address (either absolute or PC-relative offset)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Instruction Decoding]\nThe Instruction Register (IR) communicates its output directly to which component of the CPU?",
        "opts": [("Control Unit (Instruction Decoder)", True), ("System Address Bus", False), ("Direct Memory Access (DMA) Controller", False), ("Math Coprocessor FIFO buffer", False)],
        "exp": "The opcode field of the Instruction Register feeds directly into the Instruction Decoder inside the Control Unit to generate timing signals."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Addressing Modes]\nIn Register Indirect Addressing Mode (e.g., MOV A, @R0 or MOV EAX, [EBX]), the operand is located at:",
        "opts": [("The memory address stored inside the specified register", True), ("Inside the specified register directly", False), ("In the immediate operand field of the instruction", False), ("In the Program Counter", False)],
        "exp": "In register indirect mode, the register contains the effective memory address of the operand: Effective Address EA = [R]."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Flags Register]\nIn a microprocessor status word (Flags Register), which flag is asserted when an arithmetic addition produces a result that exceeds the word size representation in two's complement notation?",
        "opts": [("Carry Flag (CY)", False), ("Overflow Flag (OV / V)", True), ("Sign Flag (S)", False), ("Parity Flag (P)", False)],
        "exp": "Carry flag monitors unsigned arithmetic overflow. The Overflow Flag (OV) indicates signed two's complement overflow (e.g. adding two positive numbers produces a negative result)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Stack Pointer]\nIn a downward-growing stack architecture (common in x86 and ARM processors), executing a PUSH operation causes the Stack Pointer (SP) to:",
        "opts": [("Decrement before storing the data", True), ("Increment after storing the data", False), ("Remain unchanged while shifting memory cells", False), ("Reset to zero", False)],
        "exp": "In descending stack architectures, PUSH pre-decrements the Stack Pointer (SP = SP - word_size) and then writes data to M[SP]. POP reads M[SP] and post-increments SP."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Multi-Statement Register Analysis]\nConsider the following statements regarding CPU registers:\n(1) The Program Counter is updated during the instruction fetch phase.\n(2) General-purpose registers can store both memory addresses and arithmetic data.\n(3) The Instruction Register can be directly read and modified by user application programs in unprivileged mode.\nWhich of the above statements is/are correct?",
        "opts": [("(1) and (2) only", True), ("(2) and (3) only", False), ("(1) and (3) only", False), ("(1), (2) and (3)", False)],
        "exp": "Statement (3) is false: The Instruction Register (IR) is an internal architectural register; user assembly programs cannot directly read/write IR as an operand."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Bus Interface Registers]\nDuring a memory WRITE cycle, what are the respective roles of the MAR and MBR?",
        "opts": [("MAR places the target memory location on the address bus; MBR places the data word onto the data bus", True), ("MBR places the address; MAR supplies the data", False), ("MAR holds the bus grant signal; MBR holds parity", False), ("Both MAR and MBR output addresses on alternate clock cycles", False)],
        "exp": "During Write: Address lines = MAR, Data lines = MBR, Control lines = WRITE asserted."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Special vs General Registers]\nWhich of the following registers is strictly a SPECIAL-PURPOSE register rather than a general-purpose register?",
        "opts": [("Program Counter (PC) and Status Register (Flags)", True), ("Data Register R0", False), ("Accumulator (AC) in a general register machine", False), ("Base Register EBX", False)],
        "exp": "PC, IR, MAR, MBR, SP, and Flags are dedicated special-purpose registers with fixed hardware roles, unlike R0–R15."
    },

    # ==================== SECTION B: CONTROL UNIT & ISA (Q21 to Q40) ====================
    {
        "q": "[UPSC ESE ICT Module 1 — Control Unit Function]\nThe fundamental operational role of the Control Unit (CU) in a computer processor is to:",
        "opts": [("Interpret instruction opcodes and issue synchronized control signals to ALUs, registers, and buses across machine cycles", True), ("Perform binary floating-point multiplication", False), ("Store virtual memory page tables permanently", False), ("Convert analog sensor voltages into digital bus words", False)],
        "exp": "The Control Unit acts as the central coordinator of the CPU: it fetches, decodes instructions, and directs datapaths by asserting micro-operations."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Hardwired Control Unit]\nA Hardwired Control Unit is physically implemented using:",
        "opts": [("Fixed combinational logic gates, decoders, and finite state machine (FSM) sequencers", True), ("Microcode stored in control memory ROM", False), ("DRAM capacitors refreshed dynamically", False), ("Magnetic bubble memory", False)],
        "exp": "Hardwired CUs use combinational logic gates, multiplexers, and FSM counter circuits to generate control signals directly without microinstruction lookup."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Microprogrammed Control Unit]\nIn a Microprogrammed Control Unit (Wilkes design), control signals are generated by:",
        "opts": [("Sequentially reading microinstructions (control words) stored in high-speed Control Memory (ROM/PROM)", True), ("Using hardwired logic matrices of NAND/NOR gates only", False), ("Analog operational amplifier circuits", False), ("External software drivers executed from the hard disk", False)],
        "exp": "Invented by Maurice Wilkes (1951), microprogrammed CUs store micro-operations as bit patterns in Control Store ROM. A micro-PC steps through control routines."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Statement-I & Statement-II]\nStatement (I): Hardwired control units offer significantly faster instruction execution speeds than microprogrammed control units.\nStatement (II): Microprogrammed control units incur a clock cycle latency penalty because each microinstruction must be fetched from control store memory before generating signals.\nWhich of the following is correct?",
        "opts": [
            ("Both Statement (I) and Statement (II) are individually true and Statement (II) is the correct explanation of Statement (I)", True),
            ("Both Statement (I) and Statement (II) are individually true, but Statement (II) is NOT the correct explanation of Statement (I)", False),
            ("Statement (I) is true, but Statement (II) is false", False),
            ("Statement (I) is false, but Statement (II) is true", False)
        ],
        "exp": "Statement (I) and (II) are true and (II) explains (I). Hardwired logic propagation delay through gates is much shorter than accessing ROM control memory."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — CISC Processor Design]\nMicroprogrammed control units are predominantly employed in CISC (Complex Instruction Set Computer) processors primarily because:",
        "opts": [("Complex, multi-cycle instructions with diverse addressing modes can be easily implemented and modified via microcode routines without changing silicon wiring", True), ("CISC processors do not support pipelining", False), ("Hardwired logic cannot decode 8-bit opcodes", False), ("CISC processors lack general purpose registers", False)],
        "exp": "CISC architectures (like x86) have hundreds of complex instructions; modifying or bug-fixing instructions via microcode firmware updates is far simpler than re-etching silicon."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — RISC vs CISC Architecture]\nRISC (Reduced Instruction Set Computer) processors typically adopt Hardwired Control Units because:",
        "opts": [("Instructions have fixed length, uniform formats, and execute in single-cycle pipelined stages, maximizing clock speed", True), ("RISC instructions require 10 to 15 clock cycles per instruction", False), ("RISC processors cannot execute conditional jumps", False), ("Control memory ROM cannot be fabricated on RISC chips", False)],
        "exp": "RISC features simple, uniform single-word instructions designed for 1-cycle throughput per pipeline stage, making hardwired FSM control ideal."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Instruction Set Architecture (ISA)]\nThe Instruction Set Architecture (ISA) of a computer represents:",
        "opts": [("The programmer-visible abstract boundary defining supported instructions, registers, memory models, and data representations", True), ("The physical layout and trace spacing on the printed circuit motherboard", False), ("The silicon doping concentration inside the transistor channels", False), ("The operating system kernel scheduler algorithm", False)],
        "exp": "ISA is the boundary between hardware and software (e.g. x86-64, ARMv8, RISC-V). It defines the machine language instructions, register set, and addressing rules."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Horizontal vs Vertical Microcode]\nIn microprogrammed control units, how does Horizontal microprogramming differ from Vertical microprogramming?",
        "opts": [("Horizontal microinstructions have wide control words where each bit directly controls a single gate/signal (no decoding, maximum concurrency); Vertical microinstructions use encoded fields requiring decoders", True), ("Vertical microinstructions are wider than horizontal microinstructions", False), ("Horizontal microcode requires complex external decoders for every control line", False), ("Vertical microcode can execute all micro-operations in parallel without decoders", False)],
        "exp": "Horizontal: 1 bit per control signal -> long control word, zero decoding delay, high parallel execution. Vertical: bits grouped into fields (e.g. 3 bits decoded to 8 signals) -> compact control word, requires decoder."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — RISC Characteristics]\nWhich of the following architectural features is a hallmark characteristic of RISC design?",
        "opts": [("Load/Store architecture where memory access is restricted strictly to LOAD and STORE instructions, and all arithmetic operates on registers", True), ("Variable-length instructions spanning 1 to 15 bytes", False), ("Support for memory-to-memory arithmetic operations (e.g., ADD [addr1], [addr2])", False), ("Large microcode ROM containing specialized polynomial evaluation instructions", False)],
        "exp": "RISC mandates a strict Load-Store architecture. Arithmetic operations (ADD, SUB, AND) can ONLY operate on registers, never directly on memory addresses."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — CISC Characteristics]\nWhich of the following is a characteristic attribute of CISC architectures?",
        "opts": [("Complex addressing modes, variable instruction lengths, and instructions capable of direct memory-to-memory manipulation", True), ("Fixed 32-bit instruction length for all instructions", False), ("Predominance of single-cycle instruction execution", False), ("Very small number of addressing modes (typically 2 or 3)", False)],
        "exp": "CISC architectures provide rich, variable-length instructions (e.g., 1 byte up to 15 bytes in x86) with complex addressing modes to reduce compiled code size."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Addressing Modes Matching]\nMatch List-I (Addressing Mode) with List-II (Effective Address Calculation):\nList-I:\nA. Immediate Addressing\nB. Direct / Absolute Addressing\nC. Indirect Addressing\nD. Base-Register (Displacement) Addressing\nList-II:\n1. Effective Address EA = [R_base] + Offset\n2. Effective Address EA = Address Field in Instruction\n3. Operand is part of the instruction itself\n4. Effective Address EA = M[Address Field]\nSelect the correct code:",
        "opts": [
            ("A-3, B-2, C-4, D-1", True),
            ("A-2, B-3, C-1, D-4", False),
            ("A-3, B-4, C-2, D-1", False),
            ("A-1, B-2, C-4, D-3", False)
        ],
        "exp": "Immediate = operand in instruction (3); Direct = EA is address field (2); Indirect = EA is pointer in memory (4); Base-Register = base + displacement (1)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Zero-Address Machines]\nA Stack-based computer architecture (Zero-Address machine) performs an arithmetic operation like ADD by:",
        "opts": [("Popping the top two operands from the stack, executing addition in the ALU, and pushing the result back onto the stack", True), ("Fetching operands from two registers specified by 5-bit fields", False), ("Reading both operands directly from main memory addresses specified in the opcode", False), ("Storing the result in the Program Counter", False)],
        "exp": "In zero-address architectures (like JVM or Forth stack engines), operands are implicitly on top of the stack (TOS and NOS). ADD pops both, adds them, and pushes the sum."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Relative Addressing Mode]\nProgram-Counter Relative (PC-Relative) addressing mode is primarily utilized in compiler code generation for:",
        "opts": [("Position-independent branch and jump instructions within a local code displacement", True), ("Allocating static arrays in global heap memory", False), ("Accessing memory-mapped peripheral I/O ports", False), ("Executing inter-privilege OS system calls", False)],
        "exp": "PC-relative mode specifies offset: Target = PC + displacement. Because the target is defined relative to the current instruction, code can be loaded anywhere in memory (position-independent code)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Endianness in Computer Architecture]\nA 32-bit hexadecimal word 0x12345678 is stored in memory starting at byte address 0x1000. In a LITTLE-ENDIAN architecture, what byte value is stored at the lowest address (0x1000)?",
        "opts": [("0x78 (Least Significant Byte)", True), ("0x12 (Most Significant Byte)", False), ("0x34", False), ("0x56", False)],
        "exp": "Little-Endian stores the Least Significant Byte (LSB = 0x78) at the lowest memory address (0x1000). Big-Endian stores the Most Significant Byte (MSB = 0x12) at the lowest address."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Instruction Format Bits Numerical]\nA CPU has 16-bit instructions and 64 distinct opcodes. The instruction format supports two register operands from a file of 32 general-purpose registers, plus an immediate operand. How many bits are available for the immediate operand?",
        "opts": [("0 bits (impossible format)", True), ("2 bits", False), ("4 bits", False), ("6 bits", False)],
        "exp": "64 opcodes requires log2(64) = 6 bits. 32 registers requires log2(32) = 5 bits per register. Two registers = 5 + 5 = 10 bits. Total bits used = 6 (opcode) + 10 (registers) = 16 bits. Bits remaining for immediate = 16 - 16 = 0 bits!"
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Multi-Statement ISA Analysis]\nConsider the following statements regarding RISC and CISC architectures:\n(1) CISC architectures typically have smaller compiled binary sizes than RISC architectures for the same program.\n(2) RISC architectures emphasize single-cycle execution of simple instructions.\n(3) Pipelining is substantially simpler to implement on CISC processors than on RISC processors.\nWhich of the above statements are correct?",
        "opts": [("(1) and (2) only", True), ("(2) and (3) only", False), ("(1) and (3) only", False), ("(1), (2) and (3)", False)],
        "exp": "Statement (3) is false: Pipelining is much easier on RISC due to uniform instruction lengths and simple addressing. CISC instructions have variable length and multi-cycle execution, causing complex structural hazards."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Opcode Extension Technique]\nThe technique of 'Expanding Opcodes' in instruction format design allows a fixed-size instruction word to:",
        "opts": [("Support varying numbers of operand addresses (e.g. 3-address, 2-address, 1-address, and 0-address instructions) within the same word length", True), ("Increase physical memory bus width automatically", False), ("Overclock the ALU clock multiplier", False), ("Eliminate pipeline data dependencies", False)],
        "exp": "Expanding opcodes uses unused bit combinations of shorter opcode fields to escape into longer opcodes for instructions requiring fewer operands."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Auto-Increment Addressing]\nIn Auto-Increment addressing mode (e.g., (R)+), after the operand is accessed from M[R], the register R is automatically:",
        "opts": [("Incremented by the size of the accessed data item", True), ("Decremented by 1", False), ("Cleared to zero", False), ("Stored in the Stack Pointer", False)],
        "exp": "Auto-increment mode accesses M[R], then increments R by the data operand size (1 byte for char, 4 bytes for float/int, 8 bytes for double), ideal for array stepping."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Orthogonal ISA]\nAn Instruction Set Architecture is said to be 'Orthogonal' if:",
        "opts": [("Every addressing mode can be used freely with every opcode and every data type without arbitrary architectural restrictions", True), ("All instructions are exactly 90 bits long", False), ("Only binary bitwise instructions are permitted", False), ("Registers cannot store pointers", False)],
        "exp": "Orthogonality means instructions, data types, and addressing modes can be combined independently without special-case restrictions (e.g., VAX-11 and Motorola 68000 were highly orthogonal)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Micro-operation Definition]\nIn computer processor terminology, a 'Micro-operation' is defined as:",
        "opts": [("An elementary hardware operation performed on data stored in registers during a single clock cycle", True), ("A high-level language function call", False), ("A complete operating system process context switch", False), ("A hard disk sector seek operation", False)],
        "exp": "A micro-operation is the most basic atomic step (e.g., register transfer MAR <- PC, or AC <- AC + MBR) executed within a single clock tick."
    },

    # ==================== SECTION C: MACHINE INSTRUCTION CYCLE (Q41 to Q60) ====================
    {
        "q": "[UPSC ESE ICT Module 1 — Machine Instruction Cycle]\nThe fundamental machine instruction cycle executed repetitively by the CPU consists of which sequence of phases?",
        "opts": [("Fetch -> Decode -> Execute -> Writeback / Store", True), ("Decode -> Fetch -> Store -> Interrupt", False), ("Execute -> Fetch -> Store -> Compile", False), ("Store -> Execute -> Decode -> Fetch", False)],
        "exp": "The classic von Neumann cycle proceeds: 1. Fetch instruction from memory, 2. Decode opcode and operands, 3. Execute operation in ALU/datapath, 4. Store/Writeback result to register or memory."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Fetch Phase Micro-operations]\nWhich set of register transfer micro-operations correctly represents the Instruction Fetch phase?",
        "opts": [
            ("T0: MAR <- PC;  T1: MBR <- M[MAR], PC <- PC + 1;  T2: IR <- MBR", True),
            ("T0: PC <- MAR;  T1: IR <- MBR;  T2: MBR <- PC", False),
            ("T0: IR <- PC;   T1: MAR <- IR;   T2: PC <- MBR", False),
            ("T0: MBR <- PC;  T1: MAR <- MBR;  T2: PC <- PC - 1", False)
        ],
        "exp": "During Fetch: 1. MAR receives PC, 2. Memory read cycle places instruction into MBR while PC increments, 3. Instruction moves from MBR into IR."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Statement-I & Statement-II]\nStatement (I): The Program Counter (PC) must be incremented during the Fetch phase rather than waiting until the end of the Execute phase.\nStatement (II): Incrementing the PC during fetch ensures that the CPU is already primed to fetch the subsequent sequential instruction in pipelined execution.\nWhich of the following is correct?",
        "opts": [
            ("Both Statement (I) and Statement (II) are individually true and Statement (II) is the correct explanation of Statement (I)", True),
            ("Both Statement (I) and Statement (II) are individually true, but Statement (II) is NOT the correct explanation of Statement (I)", False),
            ("Statement (I) is true, but Statement (II) is false", False),
            ("Statement (I) is false, but Statement (II) is true", False)
        ],
        "exp": "PC is incremented during fetch so that relative branch offsets calculate correctly and pipelined stages can initiate the next fetch immediately."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Clock Cycles vs Machine Cycles]\nIn microprocessor timing analysis, what is the precise relationship between a Clock Period (T-state), a Machine Cycle, and an Instruction Cycle?",
        "opts": [("An Instruction Cycle is composed of one or more Machine Cycles; each Machine Cycle is composed of multiple Clock States (T-states)", True), ("A Machine Cycle is composed of multiple Instruction Cycles", False), ("A T-state is longer than a Machine Cycle", False), ("An Instruction Cycle always equals exactly one T-state", False)],
        "exp": "Hierarchy: 1 Clock Period = 1 T-state. Several T-states (3 to 6) make 1 Machine Cycle (e.g. Opcode Fetch, Memory Read). Several Machine Cycles make 1 complete Instruction Cycle."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — CPU Pipelining Ideal Speedup]\nIn an ideal $k$-stage linear instruction pipeline executing $n$ independent instructions with clock cycle time $\tau$, the speedup factor $S_k$ compared to a non-pipelined processor as $n \to \infty$ approaches:",
        "opts": [("k (the number of pipeline stages)", True), ("k / 2", False), ("1", False), ("n / k", False)],
        "exp": "Time non-pipelined = $n \cdot k \cdot \tau$. Time pipelined = $(k + n - 1) \cdot \tau$. Speedup $S_k = \frac{n \cdot k}{k + n - 1}$. As $n \to \infty$, $S_k \to k$."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Pipeline Structural Hazards]\nA Structural Hazard (hardware resource conflict) in an instruction pipeline occurs when:",
        "opts": [("Two or more instructions in different stages attempt to access the same physical hardware resource (such as a single-ported memory) simultaneously", True), ("An instruction depends on the result of an earlier instruction that has not yet written back", False), ("A conditional branch instruction alters the Program Counter", False), ("A division by zero exception triggers an OS interrupt", False)],
        "exp": "Structural hazards arise from hardware resource limitations (e.g., trying to fetch an instruction and read data from memory simultaneously on a single unified bus)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Pipeline Data Hazards]\nThe Read-After-Write (RAW) data dependency hazard in a processor pipeline is solved at hardware level using:",
        "opts": [("Operand Forwarding (Bypassing) from ALU output / pipeline registers directly to the ALU input of the dependent stage", True), ("Branch prediction buffer lookup", False), ("Flushing all cache lines to DRAM", False), ("Increasing the clock voltage", False)],
        "exp": "Operand Forwarding routes the newly computed ALU result directly from EX/MEM or MEM/WB pipeline registers back to the ALU input without waiting for register write-back."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Pipeline Control Hazards]\nA Control Hazard (Branch Hazard) in an instruction pipeline is caused by:",
        "opts": [("Branch and jump instructions whose target address is determined after earlier stages have already fetched subsequent sequential instructions", True), ("Simultaneous write-back into the accumulator", False), ("Memory page faults during virtual translation", False), ("Power supply voltage fluctuations", False)],
        "exp": "Control hazards occur when branch decisions redirect instruction flow, requiring pre-fetched instructions in the pipeline to be flushed (causing branch penalty bubbles)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Interrupt Cycle in Instruction Pipeline]\nAt what specific moment during the instruction execution cycle does the CPU check for pending external hardware interrupts?",
        "opts": [("At the very end of the Execute/Store phase of each instruction cycle, prior to initiating the next instruction fetch", True), ("In the middle of the ALU execution stage", False), ("Only when the processor boots up", False), ("Continuously by interrupting arithmetic micro-operations midway", False)],
        "exp": "To maintain architectural state consistency, interrupts are polled and serviced strictly at instruction boundaries (at the end of the current instruction's store phase)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Interrupt Service Routine (ISR)]\nWhen a CPU accepts a hardware interrupt, what critical architectural actions occur automatically before jumping to the Interrupt Service Routine (ISR)?",
        "opts": [("The current Program Counter (and Flags/Status register) are pushed onto the stack, and the PC is loaded with the interrupt vector address", True), ("All register contents are erased to zero", False), ("The CPU enters low-power sleep mode", False), ("The instruction in the IR is deleted from RAM", False)],
        "exp": "Upon interrupt: CPU saves return state (PC and PSW/Flags) onto the stack, disables interrupts, and loads the ISR address from the interrupt vector table."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — CPI Numerical]\nA processor executes a benchmark program of 1,000,000 instructions on a 2 GHz clock (cycle time $\tau = 0.5\text{ ns}$). If the average Cycles Per Instruction (CPI) is 1.5, what is the total execution time of the program?",
        "opts": [("0.75 milliseconds", True), ("1.50 milliseconds", False), ("3.00 milliseconds", False), ("0.50 milliseconds", False)],
        "exp": "CPU Time = Instruction Count $\times$ CPI $\times \tau$ = $10^6 \times 1.5 \times 0.5 \times 10^{-9}\text{ s} = 0.75 \times 10^{-3}\text{ s} = 0.75\text{ ms}$."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Branch Prediction]\nDynamic branch prediction using a 2-bit saturating counter prevents premature branch direction flipping caused by:",
        "opts": [("A single anomalous loop exit iteration in deeply nested repetitive loops", True), ("Cache miss penalties on dirty blocks", False), ("ALU integer divide-by-zero errors", False), ("Unaligned 64-bit memory word access", False)],
        "exp": "A 2-bit predictor requires two consecutive mispredictions to change state (Strongly Taken -> Weakly Taken -> Weakly Not Taken -> Strongly Not Taken), tolerating single loop exits."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Instruction Level Parallelism]\nA Superscalar processor achieves an effective IPC (Instructions Per Cycle) greater than 1.0 primarily by:",
        "opts": [("Incorporating multiple parallel execution units (ALUs, FPUs, Load/Store units) to issue and execute multiple independent instructions per clock cycle", True), ("Increasing the main memory capacity to 1 Terabyte", False), ("Eliminating the control unit entirely", False), ("Using magnetic bubble memory registers", False)],
        "exp": "Superscalar architectures exploit Instruction-Level Parallelism (ILP) by fetching multiple instructions and dispatching them concurrently across redundant execution pipelines."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Multi-Statement Pipeline Analysis]\nConsider the following statements regarding instruction pipelining:\n(1) Pipelining reduces the execution latency of an individual instruction.\n(2) Pipelining increases the overall instruction execution throughput of the processor.\n(3) Pipelining introduces overhead due to inter-stage pipeline register setup and propagation times.\nWhich of the above statements are correct?",
        "opts": [("(2) and (3) only", True), ("(1) and (2) only", False), ("(1) and (3) only", False), ("(1), (2) and (3)", False)],
        "exp": "Statement (1) is false: Individual instruction latency is actually slightly longer due to pipeline register delays. Pipelining increases THROUGHPUT, not individual instruction latency."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Out-of-Order Execution]\nIn high-performance Out-of-Order (OoO) processor engines (Tomasulo's algorithm), what structure guarantees that instructions commit and update architectural registers in original program order?",
        "opts": [("Reorder Buffer (ROB)", True), ("Memory Address Register", False), ("Translation Lookaside Buffer", False), ("Instruction Cache line tags", False)],
        "exp": "The Reorder Buffer (ROB) holds speculative results and ensures instructions commit their state to architectural registers strictly in original program order, preserving precise exceptions."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Register Renaming]\nRegister Renaming in advanced superscalar processor microarchitectures is specifically designed to eliminate which types of pipeline hazards?",
        "opts": [("WAR (Write-After-Read / Anti-dependence) and WAW (Write-After-Write / Output dependence) false hazards", True), ("RAW (Read-After-Write) true data dependencies", False), ("Structural memory port collisions", False), ("Timer interrupt delays", False)],
        "exp": "WAR and WAW are false name dependencies caused by limited architectural register names. Renaming them to physical registers completely eliminates WAR and WAW stalls."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — VLIW Architecture]\nHow does a VLIW (Very Long Instruction Word) processor differ from a Superscalar processor in scheduling parallel instructions?",
        "opts": [("In VLIW, instruction scheduling and dependency analysis are performed entirely at compile-time by software; in Superscalar, it is done at run-time by hardware logic", True), ("VLIW uses microprogrammed control while Superscalar is hardwired only", False), ("VLIW cannot execute arithmetic operations in parallel", False), ("VLIW does not use pipeline registers", False)],
        "exp": "VLIW bundles independent operations into one giant word at compile time. Superscalar uses complex runtime out-of-order hardware logic to find independent instructions."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Pipeline Efficiency Numerical]\nA 4-stage pipeline executes 100 instructions. In the absence of stalls, what is the theoretical speedup over a non-pipelined processor?",
        "opts": [("3.88", True), ("4.00", False), ("2.50", False), ("1.00", False)],
        "exp": "Time non-pipelined = $100 \times 4 = 400$ cycles. Time pipelined = $(k + n - 1) = 4 + 100 - 1 = 103$ cycles. Speedup = $400 / 103 \approx 3.88$."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Machine Cycle Sub-operations]\nDuring the Decode phase of the machine cycle, which internal operation takes place?",
        "opts": [("The opcode in IR is decoded to determine required control signals, and operand addressing is evaluated", True), ("Data is written to the hard drive", False), ("The PC is decremented", False), ("The ALU outputs the remainder of division", False)],
        "exp": "In Decode: Instruction decoder decodes opcode, evaluates addressing mode, and calculates effective address if needed."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Precise Interrupts]\nA processor is said to support 'Precise Interrupts' if, when an interrupt or exception occurs:",
        "opts": [("All instructions prior to the interrupted instruction have completely committed, the interrupted instruction and subsequent instructions have not modified state, and PC points to correct restart address", True), ("The processor halts instantly without saving registers", False), ("Only hardware interrupts can be serviced, ignoring software exceptions", False), ("The pipeline continues executing without acknowledging the interrupt", False)],
        "exp": "Precise interrupt guarantee: All older instructions complete; the faulting instruction and all younger ones leave no architectural side effects."
    },

    # ==================== SECTION D: MEMORY HIERARCHY & ORGANIZATION (Q61 to Q80) ====================
    {
        "q": "[UPSC ESE ICT Module 1 — Memory Hierarchy]\nThe primary governing principle for organizing computer memory in a hierarchical pyramid (Registers -> Cache -> RAM -> SSD/HDD) is to optimize:",
        "opts": [("Average access time while minimizing cost per bit of storage", True), ("Physical weight of the computer cabinet", False), ("Bus line count between Northbridge and Southbridge", False), ("Electromagnetic radiation emissions", False)],
        "exp": "Memory hierarchy exploits locality of reference to provide an effective memory speed close to the fastest level (SRAM cache) at an average cost per bit close to the cheapest level (DRAM/disk)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Fastest Memory]\nWhich memory technology provides the ABSOLUTE FASTEST data access time in modern computing systems?",
        "opts": [("CPU Internal Registers", True), ("Level 1 (L1) Cache", False), ("DDR5 Synchronous DRAM", False), ("NVMe Solid State Drive", False)],
        "exp": "Registers are on-die flip-flops with access times under 0.5 nanoseconds (single clock cycle), faster than L1 cache (1–2 ns)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Cache Memory Purpose]\nCache memory is inserted between the high-speed CPU core and main memory (DRAM) primarily to:",
        "opts": [("Bridge the processor-memory performance gap (memory wall) and reduce average memory access time", True), ("Store the entire operating system permanently", False), ("Act as a backup in case of main memory power failure", False), ("Increase the address bus width from 32-bit to 64-bit", False)],
        "exp": "CPU speeds have outpaced DRAM access speeds (the 'Memory Wall'). High-speed on-chip SRAM cache buffers frequently used blocks to minimize processor stall cycles."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Principle of Locality]\nThe architectural effectiveness of cache memory and virtual memory relies directly on the 'Principle of Locality of Reference', which states that:",
        "opts": [("Programs tend to access a relatively small portion of their address space at any given time (Temporal and Spatial locality)", True), ("Memory addresses are distributed purely randomly across 4 GB space", False), ("Every instruction requires access to the magnetic disk drive", False), ("Data access speeds are identical regardless of physical location", False)],
        "exp": "Locality of reference: Programs execute iteratively in loops and sequential memory blocks, repeatedly referencing recently used addresses (temporal) and nearby addresses (spatial)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Temporal vs Spatial Locality]\nWhich programming construct exhibits strong TEMPORAL locality and strong SPATIAL locality respectively?",
        "opts": [("Temporal: Program loop counter variable repeatedly updated; Spatial: Sequential traversal of elements in a contiguous 1D array", True), ("Temporal: Random pointer chasing in a linked list; Spatial: Jumping to disjoint subroutine addresses", False), ("Both are demonstrated equally by random number generation", False), ("Neither locality exists in modern compiled code", False)],
        "exp": "Loop variables accessed repeatedly in tight time windows demonstrate Temporal locality. Contiguous array elements loaded in sequential order exhibit Spatial locality."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — SRAM vs DRAM Technology]\nWhat are the fundamental physical and operational differences between Static RAM (SRAM) and Dynamic RAM (DRAM)?",
        "opts": [("SRAM uses 6-transistor (6T) flip-flop cells (faster, more expensive, no refresh needed); DRAM uses 1-transistor 1-capacitor (1T-1C) cells (denser, cheaper, requires periodic electrical refreshing)", True), ("SRAM requires dynamic refresh cycles 1000 times per second", False), ("DRAM is faster than SRAM and is used for CPU L1 cache", False), ("SRAM is non-volatile while DRAM is volatile", False)],
        "exp": "SRAM (Cache): 6 transistors per cell, no refresh, high speed, high cost. DRAM (Main memory): 1 transistor + 1 capacitor, charges leak away and must be refreshed every 64 ms."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Effective Access Time Numerical]\nA computer system has a cache access time of $T_c = 2\text{ ns}$ and a main memory access time of $T_m = 50\text{ ns}$. If the cache hit ratio is $h = 95\%$, what is the Average Memory Access Time ($T_{avg}$)?",
        "opts": [("4.5 ns", True), ("2.5 ns", False), ("5.0 ns", False), ("26.0 ns", False)],
        "exp": "$T_{avg} = h \cdot T_c + (1 - h) \cdot T_m = 0.95 \times 2 + (1 - 0.95) \times 50 = 1.9 + 0.05 \times 50 = 1.9 + 2.5 = 4.4\text{ ns} \approx 4.5\text{ ns}$."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Cache Mapping Direct vs Associative]\nIn Direct-Mapped cache organization, a main memory block $j$ maps to cache line index $i$ according to:",
        "opts": [("i = j mod (Total Number of Cache Lines)", True), ("i = j / (Block Size)", False), ("Any arbitrary cache line that happens to be empty", False), ("i = Tag + Offset", False)],
        "exp": "In direct mapping: Cache Line = Block Number mod Number of Cache Lines. (In fully associative mapping, any block can reside in any line. In set-associative: Set = Block mod Number of Sets)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Cache Conflict Misses]\nConflict misses (collision misses) occur in which cache organizations but are ENTIRELY ABSENT in another?",
        "opts": [("Present in Direct-Mapped and Set-Associative caches; entirely absent in Fully Associative caches", True), ("Present in Fully Associative caches only", False), ("Present in main memory DRAM only", False), ("Absent in all modern caches", False)],
        "exp": "The 3 Cs of cache misses: Compulsory (cold start), Capacity, and Conflict. Conflict misses occur when multiple blocks map to the same set/line; they do not exist in Fully Associative caches."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Cache Write Policies]\nCompare Write-Through and Write-Back cache update policies:\n(1) Write-Through writes data simultaneously to both cache and main memory on every write hit.\n(2) Write-Back writes data only to cache, setting a 'dirty bit', and writes to main memory only when the dirty block is evicted.\nWhich of the above statements is/are correct?",
        "opts": [("Both (1) and (2) are correct", True), ("(1) only", False), ("(2) only", False), ("Neither (1) nor (2)", False)],
        "exp": "Both are correct. Write-Through maintains memory coherence at the cost of bus write bandwidth. Write-Back minimizes bus traffic by writing to memory only upon dirty line eviction."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Virtual Memory Purpose]\nThe fundamental architectural role of Virtual Memory in modern computer operating systems is to:",
        "opts": [("Allow processes to execute with an address space larger than physical RAM, provide memory protection between processes, and automate overlay management", True), ("Increase the physical clock speed of RAM sticks", False), ("Eliminate the need for cache memory", False), ("Prevent data corruption on CD-ROMs", False)],
        "exp": "Virtual memory decouples logical address space from physical memory using page tables, mapping large virtual addresses onto smaller physical RAM and disk swap."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Paging vs Segmentation]\nWhat is the essential distinction between Paging and Segmentation in virtual memory management?",
        "opts": [("Paging divides memory into fixed-size physical blocks (pages and frames) transparent to programmer; Segmentation divides memory into variable-sized logical modules (code, stack, data) defined by programmer", True), ("Paging uses variable-sized blocks; Segmentation uses fixed-size blocks", False), ("Paging cannot suffer from internal fragmentation", False), ("Segmentation causes internal fragmentation while paging causes external fragmentation", False)],
        "exp": "Paging: Fixed size (e.g. 4 KB) -> causes internal fragmentation, zero external fragmentation. Segmentation: Variable size -> logical units, causes external fragmentation."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Translation Lookaside Buffer (TLB)]\nThe Translation Lookaside Buffer (TLB) is an associative hardware cache inside the Memory Management Unit (MMU) designed to:",
        "opts": [("Cache recently translated Virtual-to-Physical page table entries, avoiding multi-level page table traversals in RAM", True), ("Store intermediate arithmetic multiplication results", False), ("Hold backup copies of the Program Counter", False), ("Buffer print spooler queues", False)],
        "exp": "Without a TLB, every memory reference requires multiple RAM accesses just to traverse page tables. The TLB caches active Page Number -> Frame Number translations (access time ~1 ns)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Page Fault]\nA Page Fault interrupt is generated by the Memory Management Unit (MMU) hardware when:",
        "opts": [("The valid/invalid bit in the page table entry indicates that the referenced page is not currently present in physical RAM (resident on disk swap)", True), ("A process attempts to divide by zero", False), ("The CPU clock frequency exceeds rated thermal limits", False), ("The stack pointer reaches the top of the accumulator", False)],
        "exp": "If the valid bit = 0 in the page table, the requested virtual page is not loaded in RAM. MMU triggers a Page Fault trap: the OS suspends the process, loads the page from disk swap, and resumes."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Thrashing]\nIn virtual memory systems, the disastrous phenomenon of 'Thrashing' occurs when:",
        "opts": [("The system spends vastly more time swapping pages into and out of disk than executing user instructions, due to insufficient physical memory for active working sets", True), ("Two CPU cores write to the same register simultaneously", False), ("A hard disk spindle motor stalls", False), ("Cache memory runs out of write buffers", False)],
        "exp": "Thrashing occurs when the sum of process working sets exceeds available physical frames. The OS page-fault rate skyrockets, CPU utilization drops to near zero, and the system freezes in constant disk I/O."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Page Replacement Algorithms]\nBelady's Anomaly (where increasing the number of allocated physical frames causes the total number of page faults to INCREASE) can occur in which page replacement algorithm?",
        "opts": [("First-In, First-Out (FIFO)", True), ("Least Recently Used (LRU)", False), ("Optimal Page Replacement (OPT / MIN)", False), ("Least Frequently Used (LFU)", False)],
        "exp": "Belady's Anomaly occurs in FIFO because it is not a 'stack algorithm'. Stack algorithms (like LRU and Optimal) guarantee that pages in memory for $m$ frames are a strict subset of $m+1$ frames."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Set-Associative Cache Address Bits Numerical]\nA system has a 32-bit physical address space, a 64 KB 4-way set-associative cache, and a cache line (block) size of 64 bytes. What are the respective sizes of the Tag, Set Index, and Block Offset fields?",
        "opts": [("Tag = 18 bits, Set Index = 8 bits, Block Offset = 6 bits", True), ("Tag = 20 bits, Set Index = 6 bits, Block Offset = 6 bits", False), ("Tag = 16 bits, Set Index = 10 bits, Block Offset = 6 bits", False), ("Tag = 22 bits, Set Index = 4 bits, Block Offset = 6 bits", False)],
        "exp": "Block offset = $\log_2(64) = 6$ bits. Number of cache lines = $64\text{ KB} / 64\text{ B} = 1024$ lines. Number of sets = $1024 / 4 = 256$ sets. Set Index = $\log_2(256) = 8$ bits. Tag bits = $32 - (8 + 6) = 32 - 14 = 18$ bits."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Multi-Level Caches L1, L2, L3]\nIn multi-level cache hierarchies of modern microprocessors, which of the following is correct regarding L1, L2, and L3 caches?",
        "opts": [("L1 is split (separate L1 Data and L1 Instruction) on-core; L2 is larger, unified, private to core; L3 is the largest, slowest cache shared across all CPU cores", True), ("L3 cache is located off-chip on the motherboard expansion slots", False), ("L1 cache is unified while L3 cache is split into instruction and data", False), ("L1 cache has higher capacity than L3 cache", False)],
        "exp": "Modern processors have split L1 (L1-I and L1-D for concurrent fetch and data access without structural hazard), private L2 per core, and large unified shared on-die L3 (LLC) cache."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Content-Addressable Memory (CAM)]\nAssociative memory, widely utilized in TLB and cache tag matching circuits, is also referred to as Content-Addressable Memory (CAM) because:",
        "opts": [("Data is accessed by matching the search data content in parallel across all storage cells simultaneously, rather than supplying an address", True), ("It stores content exclusively from the hard drive", False), ("It cannot be implemented with semiconductor transistors", False), ("It only stores sequential machine instructions", False)],
        "exp": "CAM compares the input search word with all stored words in parallel within a single clock cycle, returning the match line location if content exists."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Inverted Page Table]\nWhat is the primary advantage of an Inverted Page Table over a traditional forward-mapped hierarchical page table?",
        "opts": [("It scales with physical memory size rather than virtual address space, requiring only one page table entry per physical frame regardless of the number of processes", True), ("It completely eliminates page faults", False), ("It eliminates the need for virtual memory", False), ("It stores user data directly on the CPU register bus", False)],
        "exp": "In 64-bit systems, forward page tables consume massive memory. Inverted Page Tables have exactly 1 entry per physical page frame, indexed by hash of (Process ID + Virtual Page Number)."
    },

    # ==================== SECTION E: I/O, BUSES, PRINTERS & OS ARCHITECTURE (Q81 to Q100) ====================
    {
        "q": "[UPSC ESE ICT Module 1 — Direct Memory Access (DMA)]\nIn high-speed data transfer between peripheral devices (e.g., NVMe SSD, Gigabit Ethernet) and main memory, Direct Memory Access (DMA) enhances system performance primarily by:",
        "opts": [("Transferring blocks of data directly between memory and peripheral controllers via bus cycles without routing bytes through the CPU ALU registers", True), ("Overclocking the system RAM clock frequency", False), ("Translating machine code to assembly code in real time", False), ("Operating with zero electrical power consumption", False)],
        "exp": "DMA offloads block data transfers from the CPU. The DMA controller steals bus cycles to transfer large data buffers directly between device and RAM, interrupting the CPU only upon completion."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — DMA Transfer Modes]\nCompare Burst Mode and Cycle Stealing Mode in Direct Memory Access:\n(1) Burst mode transfers an entire contiguous block of data while retaining continuous control of the system buses.\n(2) Cycle stealing mode transfers one word at a time, releasing the bus between transfers to allow the CPU to interleave instruction execution.\nWhich of the above statements is/are correct?",
        "opts": [("Both (1) and (2) are correct", True), ("(1) only", False), ("(2) only", False), ("Neither (1) nor (2)", False)],
        "exp": "Both are correct. Burst mode is fast for large blocks but halts CPU bus access; Cycle Stealing interleaves one transfer per machine cycle without locking out the CPU."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Programmed I/O vs Interrupt-Driven I/O]\nWhat is the primary operational drawback of Programmed I/O (Polling) compared to Interrupt-Driven I/O?",
        "opts": [("The CPU wastes valuable execution cycles trapped in a tight busy-wait loop repeatedly querying the status register of the I/O device", True), ("Programmed I/O requires expensive DMA controller hardware", False), ("Programmed I/O cannot transfer data across parallel buses", False), ("Interrupt-driven I/O cannot be used with keyboards or mice", False)],
        "exp": "In Polling / Programmed I/O, the CPU is trapped in a busy-wait polling loop checking 'Device Ready' flags, wasting CPU capacity. Interrupts allow the CPU to execute other tasks until the device is ready."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — System Bus Architecture]\nA typical computer system bus consists of three distinct functional signal groups: Data Bus, Address Bus, and Control Bus. Which of the following is correct regarding their signal directions?",
        "opts": [("Address Bus is unidirectional (CPU to peripherals/memory); Data Bus is bidirectional; Control Bus carries mixed bidirectional control and timing signals", True), ("All three buses are strictly unidirectional from memory to CPU", False), ("Address Bus is bidirectional while Data Bus is unidirectional", False), ("Control Bus has zero electrical lines", False)],
        "exp": "CPU drives addresses outward on Address Bus (unidirectional). Data Bus transfers data both ways (bidirectional: Read/Write). Control Bus carries Read, Write, Clock, Reset, and Interrupt lines."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — PCI Express (PCIe) Architecture]\nUnlike legacy parallel PCI buses, PCI Express (PCIe) achieves massive data throughput across expansion slots by utilizing:",
        "opts": [("Point-to-point serial differential signaling lanes (x1, x4, x8, x16) operating at multi-gigahertz clock rates with packetized switching", True), ("A shared 128-bit parallel ribbon cable connecting all cards", False), ("Optical fiber beams inside the CPU socket", False), ("Analog frequency modulation over SATA channels", False)],
        "exp": "Legacy PCI shared a 32/64-bit parallel bus suffering from clock skew. PCIe replaces this with switched point-to-point serial differential lanes (each lane transmitting data packets independently)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Universal Serial Bus (USB) Standards]\nMatch the USB standard in List-I with its maximum theoretical signaling throughput in List-II:\nList-I:\nA. USB 2.0 (HighSpeed)\nB. USB 3.0 / USB 3.1 Gen 1 (SuperSpeed)\nC. USB 3.1 Gen 2 (SuperSpeed+)\nD. USB4 Gen 3x2\nList-II:\n1. 5 Gbps\n2. 480 Mbps\n3. 40 Gbps\n4. 10 Gbps\nSelect the correct code:",
        "opts": [
            ("A-2, B-1, C-4, D-3", True),
            ("A-1, B-2, C-3, D-4", False),
            ("A-2, B-4, C-1, D-3", False),
            ("A-3, B-1, C-4, D-2", False)
        ],
        "exp": "USB 2.0 = 480 Mbps; USB 3.0 = 5 Gbps; USB 3.1 Gen 2 = 10 Gbps; USB4 = up to 40 Gbps (Thunderbolt 3 architecture)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Impact vs Non-Impact Printers]\nWhich of the following printers is classified as an IMPACT PRINTER that relies on physical mechanical force against an inked ribbon to form characters on paper?",
        "opts": [("Dot Matrix Printer (and Daisy Wheel / Line Printer)", True), ("Laser Printer", False), ("Thermal Dye-Sublimation Printer", False), ("Piezoelectric Inkjet Printer", False)],
        "exp": "Impact printers (Dot Matrix, Daisy Wheel, Drum/Line printers) physically strike pins/hammers against an inked ribbon, making them suitable for multipart carbon copies. Laser/Inkjet/Thermal are non-impact."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Laser Printer Electrostatic Process]\nIn an electrophotographic Laser Printer, what is the correct operational sequence of the printing process?",
        "opts": [("Charging (Corona wire) -> Laser Exposure (Latent electrostatic image) -> Developing (Toner attraction) -> Transferring -> Fusing (Heat & Pressure) -> Cleaning", True), ("Developing -> Charging -> Fusing -> Exposure -> Cleaning", False), ("Transferring -> Developing -> Exposure -> Charging -> Fusing", False), ("Exposure -> Transferring -> Developing -> Fusing -> Charging", False)],
        "exp": "Six steps of laser printing: 1. Charge OPC drum uniformly (-600V), 2. Expose via laser to discharge image areas, 3. Develop (toner adheres to discharged areas), 4. Transfer toner to paper, 5. Fuse via heated rollers (200 deg C), 6. Clean residual toner."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Inkjet Printer Technologies]\nHow does a Thermal Inkjet (Bubble Jet) printer generate ink droplets compared to a Piezoelectric Inkjet printer?",
        "opts": [("Thermal inkjet uses electrical heating micro-resistors to boil ink into a rapid vapor bubble that expels a droplet; Piezoelectric uses voltage to mechanically deform a crystal that pumps ink", True), ("Thermal inkjet uses piezoelectric crystals to heat the paper", False), ("Both systems utilize high-pressure laser beams to vaporize liquid ink", False), ("Piezoelectric printers can only print black ink", False)],
        "exp": "Thermal (HP/Canon): Heat pulse vaporizes ink into a steam bubble that forces a droplet out. Piezoelectric (Epson): PZT crystal expands under voltage, mechanically squeezing ink out (compatible with heat-sensitive inks)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Thermal Printers]\nDirect Thermal Printing (widely used in POS billing machines, ATM receipts, and airline boarding passes) functions by:",
        "opts": [("Selectively heating pins on a thermal print head that activate heat-sensitive chemical coatings (leuco dyes) embedded in specialty thermal paper", True), ("Firing drops of liquid dye from a pressurized reservoir", False), ("Striking metal type bars against carbon ribbon", False), ("Exposing photographic silver halide film to ultraviolet light", False)],
        "exp": "Direct thermal printers use no ink or ribbon: a thermal print head applies heat to specialty paper coated with colorless leuco dye and developer, turning black where heated."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Printer Resolution DPI]\nIn printer performance specifications, what does a resolution metric of 1200 DPI (Dots Per Inch) physically quantify?",
        "opts": [("The printer can resolve and print 1,200 individual ink or toner dots along a linear 1-inch span horizontally and vertically", True), ("The printer can output 1,200 pages per minute", False), ("The printer buffer holds 1,200 Kilobytes of PostScript data", False), ("The toner cartridge contains 1,200 grams of carbon black", False)],
        "exp": "DPI measures dot density: 1200 DPI means 1,200 dots per linear inch ($1200 \times 1200 = 1.44 \times 10^6$ dots per square inch), determining image sharpness."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Operating System Architecture Monolithic vs Microkernel]\nWhat is the fundamental architectural design difference between a Monolithic OS Kernel (e.g., standard Linux) and a Microkernel (e.g., Mach, QNX, L4)?",
        "opts": [("Monolithic kernels run all core OS services (VFS, device drivers, network stacks, schedulers) in high-privilege Supervisor Mode (Ring 0); Microkernels keep only minimal primitives (IPC, low-level scheduling) in Ring 0 and run device drivers and file systems as unprivileged user-space servers", True), ("Monolithic kernels run entirely in user space (Ring 3)", False), ("Microkernels cannot communicate across processes", False), ("Monolithic kernels cannot support multi-threading", False)],
        "exp": "Monolithic: everything runs in single kernel address space (Ring 0) -> high performance, but a faulty driver crashes the whole OS. Microkernel: minimal core in Ring 0; drivers/filesystems run in user space (Ring 3) communicating via IPC -> high fault tolerance and modularity."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Dual-Mode CPU Operation]\nModern microprocessors provide Dual-Mode Operation (User Mode vs Kernel / Supervisor Mode) to:",
        "opts": [("Protect operating system code and hardware resources from erratic or malicious user applications by restricting privileged CPU instructions (like CLI, HLT, I/O ports)", True), ("Allow the CPU to run on alternating current", False), ("Enable concurrent execution of Windows and macOS simultaneously", False), ("Double the virtual address space for games", False)],
        "exp": "Dual-mode hardware (ring 0 kernel, ring 3 user) prevents user code from executing privileged instructions or accessing kernel memory. Mode switch occurs via software interrupts (System Calls)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — System Calls Traps]\nWhen an unprivileged user-space program requires an operating system service (e.g., reading a file via `read()` or creating a process via `fork()`), it transitions to kernel mode by triggering a:",
        "opts": [("Software Interrupt / Trap instruction (e.g., `syscall`, `sysenter`, or `int 0x80`)", True), ("Hardware reset pin assertion", False), ("Divide-by-zero hardware exception", False), ("Direct memory address bus short-circuit", False)],
        "exp": "System calls use specialized trap instructions (`syscall` on x86-64) that safely switch the CPU hardware execution level from Ring 3 to Ring 0 and vector to the kernel system call handler."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Process States in OS]\nIn the classic 5-State Process Model of an operating system, when a running process initiates a disk I/O request, it transitions from:",
        "opts": [("RUNNING state to WAITING (BLOCKED) state", True), ("RUNNING state to READY state", False), ("WAITING state to TERMINATED state", False), ("READY state to RUNNING state", False)],
        "exp": "When a process requests I/O, it cannot proceed until data is available, so the scheduler moves it from RUNNING to WAITING/BLOCKED. Upon I/O completion, it moves from WAITING to READY."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Process vs Thread]\nWhat is the fundamental distinction between a Process and a Thread in modern operating system execution?",
        "opts": [("A Process is an independent program execution unit with its own private address space and page tables; Threads share the same address space, code segment, and global data of their parent process while maintaining separate program counters and stacks", True), ("Threads have separate private address spaces and separate page tables", False), ("A Process cannot contain more than one thread", False), ("Threads run without requiring CPU registers", False)],
        "exp": "Process = Heavyweight unit with isolated memory address space. Thread = Lightweight execution unit sharing memory, heap, and open files with other threads in the same process, but having its own PC, registers, and stack."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — CPU Scheduling Algorithms]\nWhich CPU scheduling algorithm provides the theoretical MINIMUM average waiting time for a given set of stationary processes, but is difficult to implement in practice because future CPU burst lengths cannot be known in advance?",
        "opts": [("Shortest Job First (SJF) / Shortest Remaining Time First (SRTF)", True), ("First-Come, First-Served (FCFS)", False), ("Round Robin (RR) with 10 ms quantum", False), ("Priority Scheduling without preemption", False)],
        "exp": "SJF is provably optimal for minimizing average waiting time. However, it cannot be perfectly implemented in general OS schedulers because the exact duration of the next CPU burst cannot be known a priori."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Round Robin Scheduling Quantum]\nIn Round Robin (RR) process scheduling, what happens if the allocated time quantum $q$ is chosen excessively small or excessively large?",
        "opts": [("If quantum is extremely small, CPU overhead from frequent context switching degrades throughput; if quantum is extremely large, RR degenerates into First-Come, First-Served (FCFS)", True), ("If quantum is small, response time becomes infinite", False), ("If quantum is large, context switching overhead doubles", False), ("The time quantum has zero effect on scheduling behavior", False)],
        "exp": "Small quantum: high context-switch overhead wastes CPU time. Very large quantum ($q \to \infty$): each process finishes before time expires, degenerating to FCFS."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Deadlock Necessary Conditions (Coffman)]\nAccording to Coffman's conditions, a system deadlock can arise if and only if which four conditions hold simultaneously in a system?",
        "opts": [("Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait", True), ("Paging, Segmentation, Swapping, and Thrashing", False), ("FIFO, LRU, LFU, and Optimal replacement", False), ("Compilation, Assembly, Linking, and Loading", False)],
        "exp": "Coffman conditions (1971): 1. Mutual exclusion (non-shareable resources), 2. Hold and wait, 3. No preemption (resources cannot be forcibly taken), 4. Circular wait (closed chain of processes waiting)."
    },
    {
        "q": "[UPSC ESE ICT Module 1 — Virtual Memory Page Table Size Numerical]\nA computer system uses 32-bit virtual addresses and 4 KB page size. If each page table entry (PTE) takes 4 bytes, what is the size of a single-level page table for one process?",
        "opts": [("4 Megabytes (MB)", True), ("1 Megabyte (MB)", False), ("4 Kilobytes (KB)", False), ("64 Kilobytes (KB)", False)],
        "exp": "Virtual address space = $2^{32} = 4\text{ GB}$. Page size = $4\text{ KB} = 2^{12}\text{ bytes}$. Number of virtual pages = $2^{32} / 2^{12} = 2^{20} = 1,048,576$ pages. Size of page table = $2^{20}\text{ entries} \times 4\text{ bytes/entry} = 4 \times 2^{20}\text{ bytes} = 4\text{ MB}$."
    }
]

def main():
    app = create_app()
    with app.app_context():
        # 1. Add / Update all 100 questions in database
        print(f"Preparing to insert {len(QUESTIONS_100)} UPSC ESE-style questions into Topic 70...")
        added_count = 0
        existing_count = 0
        all_q_ids = []

        for q_data in QUESTIONS_100:
            ex = Question.query.filter_by(topic_id=70, question_text=q_data["q"]).first()
            if not ex:
                q = Question(
                    exam_id=1,
                    topic_id=70,
                    question_type='MCQ',
                    question_text=q_data["q"],
                    explanation_text=q_data["exp"],
                    difficulty_level='Medium',
                    created_by_user_id=1,
                    visibility='public'
                )
                db.session.add(q)
                db.session.flush()

                for opt_txt, is_corr in q_data["opts"]:
                    db.session.add(MCQOption(question_id=q.id, option_text=opt_txt, is_correct=is_corr))
                all_q_ids.append(q.id)
                added_count += 1
            else:
                existing_count += 1
                all_q_ids.append(ex.id)

        db.session.commit()
        print(f"Question insertion complete: Added {added_count} new questions, {existing_count} already existed.")

        # 2. Append 100-Question Master Question Bank into Module 1 Content (TopicContent ID 2)
        tc2 = TopicContent.query.get(2)
        if tc2:
            print("Appending 100-Question Master Practice Bank into Module 1 interactive reading material...")
            qb_html = """
    <div class="master-question-bank-section" style="margin-top: 40px; padding: 24px; background: #ffffff; border: 2px solid #6366f1; border-radius: 16px; box-shadow: 0 10px 30px rgba(99,102,241,0.08);">
      <div style="background: linear-gradient(135deg, #1e1b4b 0%, #4338ca 100%); color: #ffffff !important; padding: 20px 24px; border-radius: 12px; margin-bottom: 24px;">
        <span style="background: rgba(255,255,255,0.2); padding: 4px 12px; border-radius: 20px; font-size: 11px; text-transform: uppercase; font-weight: 700; letter-spacing: 1px;">Master Question Bank • 100 UPSC ESE Prelims Questions</span>
        <h2 style="color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; margin: 8px 0 4px 0; font-size: 22px;">🎯 Module 1: Comprehensive 100-Question Practice Bank</h2>
        <p style="margin: 0; color: #c7d2fe; font-size: 13px;">CPU Architecture, Registers, Control Unit/ISA, Instruction Cycle, Memory Hierarchy, Cache, Virtual Memory, I/O Subsystems, Printers & OS Architecture.</p>
      </div>
"""
            # Add all questions section by section
            section_names = {
                0: "🧠 Section A: CPU Architecture & Registers (Q1 – Q20)",
                20: "⚙️ Section B: Control Unit & Instruction Set Architecture (Q21 – Q40)",
                40: "💻 Section C: Machine Instruction Cycle & Pipelining (Q41 – Q60)",
                60: "🧩 Section D: Memory Hierarchy, Cache & Virtual Memory (Q61 – Q80)",
                80: "🖨️ Section E: I/O Subsystems, Bus Architecture, Printers & OS Architecture (Q81 – Q100)"
            }

            for idx, qd in enumerate(QUESTIONS_100):
                if idx in section_names:
                    qb_html += f"""
      <h3 style="color: #4338ca; border-bottom: 2px solid #e0e7ff; padding-bottom: 8px; margin-top: 28px; margin-bottom: 16px; font-size: 18px;">{section_names[idx]}</h3>
"""
                correct_letter = "A"
                for o_idx, (opt_t, is_c) in enumerate(qd["opts"]):
                    if is_c:
                        correct_letter = chr(65 + o_idx)

                qb_html += f"""
      <div class="question-card" style="margin-bottom: 18px; padding: 16px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px;">
        <p style="font-weight: 700; color: #1e293b; margin-bottom: 10px; font-size: 14.5px;"><strong>Q{idx+1}.</strong> {qd['q'].replace('[UPSC ESE ICT Module 1 — ', '[').replace(']', '] ')}</p>
        <ul style="list-style: none; padding-left: 0; margin-bottom: 10px; font-size: 13.5px;">
"""
                for o_idx, (opt_t, is_c) in enumerate(qd["opts"]):
                    letter = chr(65 + o_idx)
                    qb_html += f"""          <li style="padding: 4px 0; color: #334155;"><strong>({letter.lower()})</strong> {opt_t}</li>\n"""

                qb_html += f"""        </ul>
        <details style="background: #ede9fe; padding: 10px 14px; border-radius: 8px; font-size: 13px; color: #312e81; cursor: pointer;">
          <summary style="font-weight: 700; color: #4338ca;">✅ View Answer & UPSC Trap Explanation</summary>
          <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #c7d2fe;">
            <p style="margin: 0 0 4px 0;"><strong>Correct Answer: ({correct_letter})</strong></p>
            <p style="margin: 0; color: #1e1b4b; line-height: 1.5;">{qd['exp']}</p>
          </div>
        </details>
      </div>
"""

            qb_html += """
    </div>
"""
            # Check if already appended
            if "Master Question Bank • 100 UPSC ESE Prelims Questions" not in tc2.content_value:
                # Insert right before the last closing tags </div></div></div>
                if "</div>\n</div>\n</div>" in tc2.content_value:
                    tc2.content_value = tc2.content_value.replace("</div>\n</div>\n</div>", qb_html + "</div>\n</div>\n</div>")
                else:
                    tc2.content_value += qb_html
                db.session.commit()
                print("Successfully updated Module 1 TopicContent with 100 interactive practice questions!")
            else:
                print("100-Question bank was already present in Module 1.")

        # 3. Create / Update Dedicated 100-Question Grand Mock Test in LMS
        mt_title = "UPSC ESE 2027 Paper-I: ICT Module 1 (100-Question Master Grand Test)"
        mt = MockTest.query.filter_by(exam_id=1, title=mt_title).first()
        if not mt:
            print("Creating dedicated 100-Question Grand Mock Test...")
            mt = MockTest(
                exam_id=1,
                title=mt_title,
                description="Comprehensive 100-question master test covering all 5 core sections of ICT Module 1: CPU Architecture & Registers, Control Unit/ISA, Instruction Cycle, Memory Hierarchy, Cache/Virtual Memory, I/O Buses, Printers & OS Architecture. Standard UPSC 1/3 negative marking.",
                duration_minutes=120,
                total_marks=200.0,
                passing_marks=66.0,
                status='active',
                default_marks_per_question=2.0,
                negative_marking_enabled=True,
                negative_marking_ratio=0.33,
                created_by_user_id=1
            )
            db.session.add(mt)
            db.session.flush()

            for order_idx, qid in enumerate(all_q_ids, 1):
                db.session.add(MockTestQuestion(
                    mock_test_id=mt.id,
                    question_id=qid,
                    question_order=order_idx,
                    marks=2.0
                ))
            db.session.commit()
            print(f"Created '{mt_title}' with {len(all_q_ids)} questions!")
        else:
            print(f"Mock test '{mt_title}' already exists with ID {mt.id}.")

        total_ict_qs = Question.query.filter_by(topic_id=70, deleted_at=None).count()
        print(f"\nAudit complete! Total Questions under Topic 70 (ICT) in DB: {total_ict_qs}")

if __name__ == '__main__':
    main()
