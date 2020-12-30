
This document contains some notes/pointers on using m5ops.
riscv m5ops abi changes : [1](https://gem5-review.googlesource.com/c/public/gem5/+/25645/1), [2](https://gem5-review.googlesource.com/c/public/gem5/+/38515).

### Instructions to compile any program with m5ops

Example for riscv:

```sh
cd gem5/util/m5
scons -C util/m5 build/riscv/out/m5
```
To build tests:

```sh
scons riscv.CROSS_COMPILE=riscv64-linux-gnu- build/riscv/test/
```

Tests might need to be statically compiled. Following is the compilation command used by the build system:

```sh
riscv64-linux-gnu-g++ -o build/riscv/test/bin/call_type/inst build/riscv/call_type/inst.test.to build/riscv/call_type/inst.to build/riscv/call_type.os build/riscv/args.os build/riscv/m5_mmap.os build/riscv/abi/riscv/m5op.to build/riscv/abi/riscv/verify_inst.to -Lbuild/riscv/googletest -lgtest -lpthread -static
```

Example compilation of m5-exit.c:

```sh
cd gem5/tests/test-progs/m5-exit/src
gcc -static -I include -o m5-exit.out m5-exit.c ../../../../util/m5/build/x86/out/libm5.a
```

### Notes Related to m5ops tests

To run m5 googletests with gem5, make sure to set environment variable "RUNNING_IN_GEM5".

For example:

create a file `env` with:

```
RUNNING_IN_GEM5=1
```

And then run the test:

build/RISCV/gem5.opt configs/example/se.py --cpu-type=AtomicSimpleCPU -e env -c /data/aakahlow/RISCV-Full-System/gem5-push/gem5/util/m5/build/riscv/test/bin/call_type/inst
