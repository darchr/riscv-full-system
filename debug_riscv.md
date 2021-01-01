## QEMU GDB STUB

To debug user space processes for non-native isa (e.g. riscv), we need to use gdb stub from qemu launch.
In order to do this, do the following (`inst` is the example program to debug):

```sh
qemu-riscv64 -g 12345 ./inst &
```

Separately run gdb for riscv (which should be available in the riscv toolchain):

```sh
 /opt/riscv/bin/riscv64-unknown-linux-gnu-gdb inst
 
 #Inside gdb window:
 
 target remote localhost:12345
```

summary of some useful gdb commands:

`info local:` to list local variables in the current context.
`ptype class/struct:` to print out the definition (`ptype /o` to print all offsets and sizes)
`stepi:` step through a single instruction
`step:` step through a line of code
