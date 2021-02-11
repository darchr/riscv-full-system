# riscv-full-system
RISCV full system support on gem5 related files live here


## Current Status of RISCV Full System in gem5:

The details of the issues related to RISCV full system support in gem5 can be found in [JIRA](https://gem5.atlassian.net/browse/GEM5-367).

Following is a summary of the changes pushed to gem5 by Peter Yuen:

- bbl (with linux kernel payload) + busybox disk image is used​

- A device tree is currently compiled into bbl (berkeley boot loader)

- Addtion of a HiFive Platform
  - https://gem5-review.googlesource.com/c/public/gem5/+/40599

- Fixing bugs in interrupt control logic:
  - https://gem5-review.googlesource.com/c/public/gem5/+/40076 (Reviewed)
  - https://gem5-review.googlesource.com/c/public/gem5/+/39035 (Merged)
  - https://gem5-review.googlesource.com/c/public/gem5/+/39036 (Merged)
  - https://gem5-review.googlesource.com/c/public/gem5/+/38578 (Merged)

- Addition of CLINT (Core Local Interrupt Controller)
  - https://gem5-review.googlesource.com/c/public/gem5/+/40597

- Addition of PLIC (Platform Level Interrupt Controller)
  - https://gem5-review.googlesource.com/c/public/gem5/+/40598/2
  
- Addition of RISCV PMA (Physical Memory Attributes)
  - https://gem5-review.googlesource.com/c/public/gem5/+/40596
