#Copyright (c) 2021 The Regents of the University of California.
#All Rights Reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import m5
from m5.objects import *
from m5.util import convert
from .fs_tools import *
from .caches import *

class MySystem(System):

    def __init__(self, kernel, disk, cpu_type, num_cpus):
        super(MySystem, self).__init__()

        # Set up the clock domain and the voltage domain
        self.clk_domain = SrcClockDomain()
        self.clk_domain.clock = '3GHz'
        self.clk_domain.voltage_domain = VoltageDomain()

        self.mem_ranges = [AddrRange(start=0x80000000, size='256MB')]

        # Create the main memory bus
        # This connects to main memory
        self.membus = SystemXBar(width = 64) # 64-byte width
        self.membus.badaddr_responder = BadAddr()
        self.membus.default = Self.badaddr_responder.pio

        # Set up the system port for functional access from the simulator
        self.system_port = self.membus.cpu_side_ports

        self.initFS(self.membus, num_cpus, kernel, disk)

        # Create the CPUs for our system.
        self.createCPU(cpu_type, num_cpus)

        # Create the cache heirarchy for the system.

        self.createCacheHierarchy()

        self.createMemoryControllersDDR4()

        # Set up the interrupt controllers for the system (x86 specific)
        self.setupInterrupts()

    def totalInsts(self):
        return sum([cpu.totalInsts() for cpu in self.cpu])

    def createCPU(self, cpu_type, num_cpus):
        if cpu_type == "atomic":
            self.cpu = [AtomicSimpleCPU(cpu_id = i)
                              for i in range(num_cpus)]
            self.mem_mode = 'atomic'
        elif cpu_type == "o3":
            self.cpu = [DerivO3CPU(cpu_id = i)
                        for i in range(num_cpus)]
            self.mem_mode = 'timing'
        elif cpu_type == "simple":
            self.cpu = [TimingSimpleCPU(cpu_id = i)
                        for i in range(num_cpus)]
            self.mem_mode = 'timing'
        else:
            m5.fatal("No CPU type {}".format(cpu_type))

        for cpu in self.cpu:
            cpu.createThreads()

    def createCacheHierarchy(self):
        for cpu in self.cpu:
            # Create a memory bus, a coherent crossbar, in this case
            cpu.l2bus = L2XBar()

            # Create an L1 instruction and data cache
            cpu.icache = L1ICache()
            cpu.dcache = L1DCache()
            cpu.mmucache = MMUCache()

            # Connect the instruction and data caches to the CPU
            cpu.icache.connectCPU(cpu)
            cpu.dcache.connectCPU(cpu)
            cpu.mmucache.connectCPU(cpu)

            # Hook the CPU ports up to the l2bus
            cpu.icache.connectBus(cpu.l2bus)
            cpu.dcache.connectBus(cpu.l2bus)
            cpu.mmucache.connectBus(cpu.l2bus)

            # Create an L2 cache and connect it to the l2bus
            cpu.l2cache = L2Cache()
            cpu.l2cache.connectCPUSideBus(cpu.l2bus)

            # Connect the L2 cache to the L3 bus
            cpu.l2cache.connectMemSideBus(self.membus)

    def setupInterrupts(self):
        for cpu in self.cpu:
            # create the interrupt controller CPU and connect to the membus
            cpu.createInterruptController()

    def createMemoryControllersDDR4(self):
        self._createMemoryControllers(1, DDR4_2400_8x8)

    def _createMemoryControllers(self, num, cls):
        self.mem_cntrls = [
            MemCtrl(dram = cls(range = self.mem_ranges[0]),
                    port = self.membus.mem_side_ports)
            for i in range(num)
        ]

    def initFS(self, membus, cpus, kernel, disk):

        self.workload = RiscvBareMetal()
        self.workload.bootloader = kernel

        self.iobus = IOXBar()
        self.intrctrl = IntrControl()
        # HiFive platform
        self.platform = HiFive()

        # CLNT
        self.platform.clint = Clint()
        self.platform.clint.frequency = Frequency("100MHz")
        self.platform.clint.pio = self.membus.master

        # PLIC
        self.platform.plic = Plic()
        self.platform.clint.pio_addr = 0x2000000
        self.platform.plic.pio_addr = 0xc000000
        self.platform.plic.n_src = 11
        self.platform.plic.pio = self.membus.master

        # UART
        self.uart = Uart8250(pio_addr=0x10000000)
        self.terminal = Terminal()
        self.platform.uart_int_id = 0xa
        self.uart.pio = self.iobus.master

        # VirtIOMMIO
        image = CowDiskImage(child=RawDiskImage(read_only=True), read_only=False)
        image.child.image_file = disk
        self.platform.disk = MmioVirtIO(
            vio=VirtIOBlock(image=image),
            interrupt_id=0x8,
            pio_size = 4096
        )
        self.platform.disk.pio_addr = 0x10008000
        self.platform.disk.pio = self.iobus.master

        # PMA
        self.pma = PMA()
        self.pma.uncacheable = [
            AddrRange(0x10000000, 0x10000008),
            AddrRange(0x10008000, 0x10009000),
            AddrRange(0xc000000, 0xc210000),
            AddrRange(0x2000000, 0x2010000)
        ]

        self.bridge = Bridge(delay='50ns')
        self.bridge.master = self.iobus.slave
        self.bridge.slave = self.membus.master
        self.bridge.ranges = [
            AddrRange(0x10000000, 0x10000080),
            AddrRange(0x10008000, 0x10009000)
        ]

