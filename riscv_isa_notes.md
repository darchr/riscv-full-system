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

- Synchronous Exceptions (illegal inst, inst address misaligned, inst access fault, load access fault, environment call, breakpoint, store/atomic mem operations (AMO) address misaligned/access fault), Asynchronous Exceptions/Interrupts (timer, software, external interrupts)

### CSR (Control and Status Registers):

- Specifications allow around 4K different CSRs (12 bit address is used to point to them).
- Each CSR belongs to one of the privilege modes.

Instructions for managing privilige levels and CSRs:

- ECALL : To make a system call from a lower privilege level to a higher mode
- EBREAK : Used by debuggers to get control; similar to ECALL
- URET : To return from trap handler that was running in User Mode
- SRET : To return from trap handler that - was running in Supervisor Mode
- MRET :  To return from trap handler that was running in Machine Mode
- WFI : Go into sleep/low power state and Wait For Interrupt
- CSR.. :  Instructions to read/write the Control and Status Registers (CSRs)

Following are main CSR.. insts:

- CSRRW : Read and write a CSR
- CSRRS : Read and set selected bits to 1
- CSRRC : Read and clear selected bits to 0
- CSRRWI : Read and write a CSR (from immediate value)
- CSRRSI : Read and set selected bits to 1 (using immediate mask)
- CSRRCI : Read and clear selected bits to 0 (using immediate mask)

- "Each of these instructions reads a CSR by copying its previous value into one of the general purpose registers (x1, x2, ...)."

- "Often, you only want to read the register; if so, you can specify the source value as register x0. (This is a special case. The CSR is remains unchanged; it is not set to zero.)"

### Basic CSRs: CYCLE, TIME, INSTRET

- They are user mode registers, but also have mirrored versions (prepended with letter m, different addresses for both versions) only available to access from machine mode (the advantage of this e.g. is to be able ot reset the cycle count only by higher privilege level).

- Some registers might contain a number of bit fields and these fields can have different accessibility (e.g. status register mirrored for all privilige levels will have some fields not accessible for certain privilige levels).

- mtime is not actually a CSR but a memory mapped register on a real time clock which is a separate IO device.

### Other CSRs:

- misa : information on the machine architecture (like register width)

- mvendorid : machine vendor id

- marchid : machine architecture id

- mhartid : machine hardware thread id

- m/s/utvec: trap vector base address (address for trap handler routine)

- interrupts are always first handled by machine mode and then delegated to the appropriate privilege level (determined by various bits in CSRs).

- There is only a single trap handler at the base which then uses CSRs to determine what kind of exception is raised.

- Last two bits of trap handler address : 00 = single trap handler, 01 = collection of trap handlers (jump table).

- There is only a single trap handler for all syncrhronous exceptions but different ones for each asynchronous interrupt.

- Delegation of exceptions/interrupts to lower privilige levels can be done directly through hardware (medeleg/sedeleg and mideleg/sideleg registers, bits in these registers for each exception/interrupt are used to indicate what the hardware should do).

- three sources of interrupts: software, timer and external

- mie : machine mode interrupt enable (contains bits for all above three sources for all three privilege modes)

- mip : machine mode interrupt pending (contains bits for all above three sources for all three privilege modes)

- There is a M/SIE bit (global interrupt enable) in mstatus register as well.

- "More precisely, an interrupt will be taken (i.e., the trap handler will be invoked) if and only if the corresponding bit in both mie and mip registers is set to 1, and if interrupts are globally enabled."

- status register is also mirrored at all privilige levels and some of its fields might not be available in a particular privilige level.

- When a trap handler is running the previous state (interrupt enable bit and execution mode) is stored (using M/S/UIE, M/SPP bits) to be able to return to that state.

- RV128, RV64 also allow to execute code for smaller register size riscv (controlled through SXL and UXL bits in status register).

- MPRV : this bit in status register allows OS (in machine mode) to use virtual address (more precisely addresses are translated as if the current mode is specified by MPP).

- Address translation can be turned on by satp register.

- m/s/uepc : program counter to return to after trap is handled.

- m/s/uscratch : a scratch register that can be used by the trap handler to save back at least one general purpose register to be able to execute code to save the entire register state that existed before the trap handler started to execute.

- m/s/ucause contains a code to indicate what caused a trap.


### Virtual Memory

- PMAs (physical memory attributes) are defined for various physical memory regions. Core contains a sub-system "PMA checker" to check and enforce these attributes.

- In RISCV virtual memory fault exceptions are different from PMA violations.

- "Accesses to main memory regions are “relaxed”, which means that the exact ordering of the operations is indeterminate (unless atomic instructions are used, of course). The programmer can use atomic instructions to force particular orderings, but for normal instructions, there are no guarantees about ordering."

- Physical memory protection (PMP) is optional.

- PMP is implemented using machine mode CSRs, which contain information like: starting address of the memory region (being protected by PMP), size of the region in bytes,  R/W/X permissions of the region. A lock bit is also available to trigger PMP checks in machine mode as well (if needed).

- Each pmp region is defined by the pmpaddrx (x=0-15) and pmpxcfg registers.

- "Each pmp region must be naturally aligned given its length".

- Virtual memory is handled in supervisor mode and RISCV supports different virtual memory schemes (bare, Sv32, Sv39, Sv48). Here, 32, 39 and 48 represent different number of bits in the virtual address space.

- RV32 supports 2 level page tables and 34 bit physical address space, and RV64 supports 3/4 level page tables with 56 bit physical address space.

- Page size is 4K regardless of the virtual memory scheme.

- satp (supervisor address and translation register) is the CSR which controls address translation and contains 'MODE', 'ASID' and 'PPN' fields.

- PPN contains the physical address of the root page of the page table tree.

- Each entry in the TLB will be tagged with ASID.

- SFENCE.VMA (Supervisor fence for virtual memory) is designed to flush TLBs. It is used to impose order on accesses to memory and updates to page tables. "This instruction can specify a specific virtual address and/or a specific address space"

- A page table entry (PTE) which is 4 bytes in size contains the following fields (from MSB to LSB):

  - Physical page number (22 bits)
  - RSW: undefined, reserved for software (2 bits)
  - D: dirty (1 bit)
  - A: accessed (1 bit)
  - G: global mapping (1 bit)
  - U: user accessible (1 bit)
  - V: valid (1 bit)
  - XWR: executable, writeable, readable (3 bits)


- Megapages (4 MB in size) are supported as well in which case there will be no second level page in the page table tree.

- If G=1 (globally shared among all address spaces) in PTE, ASID checking is suppressed.

- Sv39 and Sv48 virtual addressing schemes are natural extensions of Sv32 virtual addressing.
