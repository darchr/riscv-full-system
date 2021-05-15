# Keystone on gem5

This document explains how to setup all components to run Keystone on gem5.
Some of the instructions (relevant to building keystone components) are a summarized form of the keystone setup instructions from the keystone [documentation](http://docs.keystone-enclave.org/).

Prerequisite libraries needed:

```sh
sudo apt update
sudo apt install autoconf automake autotools-dev bc \
bison build-essential curl expat libexpat1-dev libexpat-dev flex gawk gcc git \
gperf libgmp-dev libmpc-dev libmpfr-dev libtool texinfo tmux \
patchutils zlib1g-dev wget bzip2 patch vim-common lbzip2 python \
pkg-config libglib2.0-dev libpixman-1-dev libssl-dev screen \
device-tree-compiler expect makeself unzip cpio rsync cmake p7zip-full
```

Clone the main keystone repo:

```sh
git clone https://github.com/keystone-enclave/keystone.git
```

A quick way to do initial set-up is running `fast-setup.sh` script in `keystone` directory:

```sh
cd keystone
./fast-setup.sh
```

This should build/install needed tool-chain as well:

Then to set all the environment variables:

```sh
source source.sh
```

Then to build all components:

```sh
mkdir build
cd build
cmake ..
make
```

The fastest way to build the final disk image with driver, and tests package (containing a test runner application, eyrie runtime and test binaries).

```sh
make image
```

Assuming that you are in the build/ directory, the created disk image can be found in `buildroot.build/images/rootfs.ext2`


Bootloader compiled with SM and the Linux kernel will be here:

`sm.build/platform/generic/firmware/fw_payload.elf`


## To compile/build rv8 benchmarks

First building musl riscv toolchain:

```sh
git clone https://github.com/rv8-io/musl-riscv-toolchain.git
cd musl-riscv-toolchain
for i in riscv32 riscv64 i386 x86_64 arm aarch64; do sh bootstrap.sh $i ; done
```

You might need to apply this patch before building the toolchain:
`https://github.com/michaeljclark/musl-riscv-toolchain/pull/5`.

`RISCV_MUSL` env variable should be set to the path of the built toolchain:

To build the workloads:

```sh
git clone https://github.com/keystone-enclave/rv8-bench.git
cd rv8-bench
make
```
We will have to separately compile eyrie runtime, the one that is built by default as in above instructions will not work for unmodified rv8 benchmarks.

## Using this with gem5

### Changes needed in the disk image

gem5 scripts are available in [configs-riscv-keystone](configs-riscv-keystone/).

The command to use:

```sh
build/RISCV/gem5.opt  configs-riscv-keystone/run_trusted.py [path to fw_payload.elf] [path to rootfs.ext2] [cpu type] [number of cores] [rv8 benchmark name]
```

Note that there are some kernel command line arguments passed in the above scripts that are needed to run keystone on gem5.