## Spike: RISC-V Simulator

[Spike](https://github.com/riscv/riscv-isa-sim) is a functional level RISCV simulator. It supports a lot of RISCV extensions.


To build the simulator:

```sh
apt-get install device-tree-compiler
git clone https://github.com/riscv/riscv-isa-sim
cd riscv-isa-sim
mkdir build
cd build
../configure --prefix=$RISCV (path to riscv tool chain e.g. /opt/riscv)
make
sudo make install
```

It can be used to run e.g. a hello binary:

```sh
spike pk hello
```

Here pk refers to the RISCV proxy kernel, which is an application execution environment. To build proxy kernel first, follow the instructions [here](https://github.com/riscv/riscv-pk).


## Note:

If you see the error "bad syscall #98!" when spike is run, it is most probably because the workload to be simulated is using pthreads and `pk` does not support pthreads.


