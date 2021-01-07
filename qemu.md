# Running RISC-V based VM with qemu

This document discusses multiple ways qemu can be used to run a RISC-V virtual machine.

## Based on the Instructions from RISC-V's Website

These instructions are taken from [here](https://risc-v-getting-started-guide.readthedocs.io/en/latest/linux-qemu.html), but some of them did not work as it is for me, and thus, they might be modified slightly.
Moreover, these instructions do not build a disk image to be used with qemu, but relies on a busybox image.

First install pre-requisite libraries:

```sh
sudo apt install autoconf automake autotools-dev curl libmpc-dev libmpfr-dev libgmp-dev \
                 gawk build-essential bison flex texinfo gperf libtool patchutils bc \
                 zlib1g-dev libexpat-dev git
```

To install qemu itself for RISC-V, first set the `$INSTALL_DIR` to whatever path you want qemu to be installed in and then follow

```sh
git clone https://github.com/qemu/qemu
cd qemu
git checkout v5.0.0
./configure --target-list=riscv64-softmmu --prefix=$INSTALL_DIR
make -j $(nproc)
sudo make install
```

Compile Linux kernel (e.g. v5.4) for RISC-V:

```sh
git clone https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
cd linux
git checkout v5.4
make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- defconfig
make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- -j $(nproc)
```

To build busybox (binary containing many UNIX utilities) for RISC-V:

```sh
git clone https://git.busybox.net/busybox
cd busybox
CROSS_COMPILE=riscv64-linux-gnu- make defconfig
CROSS_COMPILE=riscv64-linux-gnu- make -j $(nproc)
```

Then to run qemu:

```sh
$INSTALL_DIR/bin/qemu-system-riscv64 -kernel linux/arch/riscv/boot/Image -append "root=/dev/vda ro console=ttyS0" -drive file=busybox/busybox,format=raw,id=hd0 -device virtio-blk-device,drive=hd0
```

## Based on the Instructions from Debian's Website

These instructions are based on the documentation of [Debian port for RISC-V](https://wiki.debian.org/RISC-V).

Follow the same instructions as above to build qemu and Linux kernel for RISC-V.

Next, install the required libraries:

```sh
sudo apt-get install debootstrap qemu-user-static binfmt-support debian-ports-archive-keyring
```

We also need to update the package sources to be able to access debian-ports repository. Do the following:

```sh
vim  /etc/apt/sources.list
```

Add the following in  `/etc/apt/sources.list`:

```sh
deb http://ftp.ports.debian.org/debian-ports unstable main
```

And run:

```sh
apt-get update
```

If you see an error about key expiration, run :

```sh
sudo apt-key adv --keyserver keys.gnupg.net --recv-keys [expired key]
```

Or

```sh
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys [expired key]
```

Next, we need to create a riscv chroot (operation that changes the apparent root directory of the current running process) using [`debootstrap`](https://wiki.debian.org/Debootstrap) tool.

Use the following command to that (this will create a chroot in `/tmp/riscv64-chroot`):

```sh
sudo debootstrap --arch=riscv64 --foreign --variant=buildd  --keyring /usr/share/keyrings/debian-ports-archive-keyring.gpg --include=debian-ports-archive-keyring unstable /tmp/riscv64-chroot http://deb.debian.org/debian-ports
```

Some further processing is needed to prepare this chroot to be used as the base of the virtual machine.

`qemu-static` for RISC-V is needed to be able to update packages (or run RISC-V specific applications) inside the file-system of the qemu disk image (virtual machine) from the host, once we `chroot` to the RISC-V debian file-system.

To install qemu-static in chroot:

```sh
cat >/tmp/qemu-riscv64 <<EOF
package qemu-user-static
type magic
offset 0
magic \x7f\x45\x4c\x46\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\xf3\x00
mask \xff\xff\xff\xff\xff\xff\xff\x00\xff\xff\xff\xff\xff\xff\xff\xff\xfe\xff\xff\xff
interpreter /usr/bin/qemu-riscv64-static
EOF
```

```sh
sudo update-binfmts --import /tmp/qemu-riscv64
```

Also copy the previously built Linux image to inside the debain chroot:

```sh
[path to the linux source folder]/linux/arch/riscv/boot/Image /tmp/riscv64-chroot/boot/
```

This is needed as we will see in the later part when qemu is started.

Then run `chroot` on the previously created directory:

```sh
sudo chroot /tmp/riscv64-chroot
```

Then inside the chroot, to prepare the virtual machine:

```sh
apt-get update
```

To set-up networking inside the VM:

```sh
cat >>/etc/network/interfaces <<EOF
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet dhcp
EOF
# Set root password
passwd
# Disable the getty on hvc0 as hvc0 and ttyS0 share the same console device in qemu.
ln -sf /dev/null /etc/systemd/system/serial-getty@hvc0.service
# Install kernel and bootloader infrastructure
apt-get install linux-image-riscv64 u-boot-menu
# Install and configure ntp tools
apt-get install openntpd ntpdate
sed -i 's/^DAEMON_OPTS="/DAEMON_OPTS="-s /' /etc/default/openntpd
# Configure syslinux-style boot menu
cat >>/etc/default/u-boot <<EOF
U_BOOT_PARAMETERS="rw noquiet root=/dev/vda1"
U_BOOT_FDT_DIR="noexist"
EOF
```

This tutorial uses u-boot as the bootloader. To generate the menu files used by u-boot in the chroot directory, run:

```sh
u-boot-update
```

To exit the chroot:
```sh
exit
```

Create disk image `rootfs.img` from previous chroot directory:

```sh
sudo apt-get install libguestfs-tools
sudo virt-make-fs --partition=gpt --type=ext4 --size=10G /tmp/riscv64-chroot/ rootfs.img
sudo chown ${USER} rootfs.img
```

Then run qemu with this disk image:

```sh
$INSTALL_DIR/bin/qemu-system-riscv64 -nographic -machine virt -m 1.9G -kernel /usr/lib/riscv64-linux-gnu/opensbi/generic/fw_jump.elf -device loader,file=/usr/lib/u-boot/qemu-riscv64_smode/uboot.elf -object rng-random,filename=/dev/urandom,id=rng0 -device virtio-rng-device,rng=rng0 -append "console=ttyS0 rw root=/dev/vda1" -device virtio-blk-device,drive=hd0 -drive file=rootfs.img,format=raw,id=hd0 -device virtio-net-device,netdev=usernet -netdev user,id=usernet,hostfwd=tcp::22222-:22
```

Running the above command shows the following error and fall back to OpenSBI:

```sh
TFTP error: 'Access violation' (2)
Not retrying...
BOOTP broadcast 1
DHCP client bound to address 10.0.2.15 (0 ms)
Using virtio-net#2 device
TFTP from server 10.0.2.2; our IP address is 10.0.2.15
Filename 'boot.scr.uimg'.
Load address: 0x81000000
Loading: *
TFTP error: 'Access violation' (2)
Not retrying...
```

However, the kernel booting process can be continued from this point by running the following ([reference](https://lists.denx.de/pipermail/u-boot/2019-May/367836.html)):

```sh
load virtio 0:1 ${kernel_addr_r} /boot/Image
```

```sh
booti ${kernel_addr_r} - ${fdtcontroladdr}
```


## Booting Ubuntu RISCV With qemu:

There are some cloud images provided [here](http://cloud-images.ubuntu.com/) for different Ubuntu versions with RISC-V and instructions to use them with qemu are [here](https://wiki.ubuntu.com/RISC-V).
