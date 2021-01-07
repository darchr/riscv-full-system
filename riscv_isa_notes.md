# Summary of RISC-V ISA

This document is a collection of random notes on RISC-V ISA. 

References:

- [Official - RISC-V Instruction Set Manual (2 parts)](https://github.com/riscv/riscv-isa-manual)
- [RISC-V Cheat Sheet](https://github.com/jameslzhu/riscv-card/blob/master/riscv-card.pdf)
- [RISC-V: An Overview of the Instruction Set Architecture](https://web.cecs.pdx.edu/~harry/riscv/RISCV-Summary.pdf)


## General Features

- Little endian
- 32 registers (x0 .. x31)
- x0 = zero register

- Register size is 32 bit for RV32, 64 for RV64 and 128 for RV128.
- In the RISC-V “E” extension (only available in 32 bit machines), the number of registers is reduced to 16.
- With floating point support, floating point registers (f0 ... f31) are available.
- No special support for a “stack pointer,” a “frame pointer,” or a “link register”.
- In RISCV-C extension, compilers are encouraged (but not required) to use only registers x8, x9, ... x15.
- PC width matches the width of general purpose registers.
- There is no "status register" (this makes processing of interrupts easier), used for processing of branches.
- Branch operations perform both "test" and "conditional jump".
- The other registers available are "CSR" registers (control and status registers), used for protection and privilige system (used for interrupt processing, 
  thread switching and page table manipulation).
- There can be upto 4096 CSRs, spec define only a dozen.
- Data is not required to be alligned for load and store operations but encouraged. Alignment is required for instructions (otherwise instruction misaligned     exception). 


## Instructions

- All instructions are 32 bit long (RV32, RV64, RV128), except compressed "C" extension/mode, which can have 16 bit instructions (both sizes may be intermixed).
- Most instructions are 3 operand instructions, with destination on the extreme left.

### Compressed instructions

- Identified by C prefix in assembly e.g. C.ADDW
- Many of the compressed instructions restrict access to only 8 of the registers.
- Certain other registers are (by convention and habit) used for special purposes, such as for a “stack pointer” (x2) or “link register/return address” (x1), and some compressed instructions implicitly refer to these registers.


### Instruction Encoding

- The least signi2icant 2 bits always indicate whether the instruction is 16 or 32 bits.
- Specification also allows instrutions of longer length (must be multiple of 16 bits in length).
- Instruction formats: R-type instructions (RegD, Reg1, Reg2), I-type instructions (RegD, Reg1 Imm-12), S-type instructions (Reg1, Reg2, Imm-12), B-type instructions (Reg1, Reg2, Imm-12), U-type instructions (RegD, Imm-20), J-type instructions (RegD, Imm-20).
- In an B-type instruction, the immediate value is multiplied by 2 (i.e., shifted left 1 bit) before being used. In the S-type instruction, the value is not shifted.
- In a U-type instruction, the immediate value is shifted left by 12 bits to give a 32 bit value. In a J-type instruction, the immediate value is shifted left by 1 bit (i.e., multiplied by 2). It is also sign-extended.
- Reg1, Reg2, and RegD occur in the same place in all instruction formats.
- Immediate data values in an instruction are sometimes not always in contiguous bits.
- ADDI (32 bit addition) and ADDIW (64 bit addition) differ in if they will sign extend the result or not (former does not).

## Notes on Branch Operations

- The target address is given as a PC-relative offset.  The offset is multiplied by 2, since all instructions must be halfword aligned. This gives an effective range of -4,096 .. 4,094 (in multiples of 2), relative to the PC.
- No conditionally executed (predicated) instructions.
- LUI places the U-immediate value in the top 20 bits of the destination register rd, filling in the lowest 12 bits with zeros.
- By convention, x1 is used as a link register.
- JAL target address = 20 bit max. CALL target address = 32 bit

## Notes on Memory Operations

- Address of memory location does not need to be word aligned for load/store operations, but unaligned access can be slow and is not gauranteed to be atomic.
- There are both signed and unsigned versions of load/store operations

## Notes on ALU Operations

- There are separate instructions to compute upper and lower halves of multiplication results.
- 32 bit multiplication on 64 bit machines need special attention.

## RISC-V Privilige Modes

- 4 strictly ordered privilige levels (U, S, H and M mode)
- User and supervisor modes are pretty similar to each other. Virtual memory and page tables are managed by the supervisor mode.
- Current mode is not available in a user-visible register, but needs to be figured out from the current available functionality. 
- A processor might not implement all modes, but will have at least M mode.
- Theoretically it might be possible for any sort of code to run in any mode.
- OS can implement more than one ABIs.
- OS meets the specifications of a "Supervisor Execution Environment (SEE)". Specification: SBI (Supervisor Binary Interface).
