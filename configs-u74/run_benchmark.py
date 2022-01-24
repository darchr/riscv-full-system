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

"""
This script is supposed to run keystone benchmarks
"""

import time
import argparse

import m5
import m5.ticks
from m5.objects import *

from system import *

def parse_options():
    parser = argparse.ArgumentParser(description='Runs Linux boot test with'
                'RISCV. Expects the disk image to call the simulator exit'
                'event after boot.')
    parser.add_argument("sbi", help='Path to the opensbi'
                                        'binary with kernel payload')
    parser.add_argument("disk", help="Path to the disk image to boot")
    parser.add_argument("cpu_type", help="The type of CPU in the system")
    parser.add_argument("num_cpus", type=int, help="Number of CPU cores")
    parser.add_argument("bench", help="Benchmark to simulate")
    # pass array_size = 0 for non-memory benchmarks
    parser.add_argument("array_size", type=int, help="Array entries (each 64B) for mem benchmarks")
    return parser.parse_args()

def writeBenchScript(dir, bench):
    """
    This method creates a script in dir which will be eventually
    passed to the simulated system (to run a specific benchmark
    at bootup).
    """
    file_name = '{}/run_{}'.format(dir, bench)
    bench_file = open(file_name,"w+")
    bench_file.write('cd /root/ \n')
    bench_file.write('/sbin/m5 exit \n')
    if args.array_size == 0:
        bench_file.write('microbenchmarks/{} 10000 \n'.format(args.bench))
    else:
        bench_file.write('microbenchmarks/{} 10000 {} \n'.format(args.bench, args.array_size))
    bench_file.write('/sbin/m5 exit \n')
    bench_file.close()
    return file_name


if __name__ == "__m5_main__":

    args = parse_options()

    # create the system we are going to simulate

    system = RiscvSystem(args.sbi, args.disk, args.cpu_type, args.num_cpus)

    # Exit from guest on workbegin/workend
    system.exit_on_work_items = True

    # Create and pass a script to the simulated system to run the reuired
    # benchmark
    system.readfile = writeBenchScript(m5.options.outdir, args.bench)

    # set up the root SimObject and start the simulation
    root = Root(full_system = True, system = system)

    # Required for long-running jobs
    #m5.disableAllListeners()

    # instantiate all of the objects we've created above
    m5.instantiate()

    globalStart = time.time()

    print("Running the simulation")
    exit_event = m5.simulate()

    if exit_event.getCause() == "m5_exit instruction encountered":
        # Reached the start of actual benchmark
        print("Starting actual workload!")
        m5.stats.reset()
        start_tick = m5.curTick()
    else:
        print("Unexpected termination of simulation !")
        exit(1)

    exit_event = m5.simulate()

    if exit_event.getCause() == "m5_exit instruction encountered":
        # Reached the end of workload of interest
        print("Finshed running the workload!")
        print("Dumping the stats!")
        m5.stats.dump()
        end_tick = m5.curTick()
        m5.stats.reset()
        print("Simulated time: %.2fs" % ((end_tick-start_tick)/1e12))
        exit(0)
    else:
        print("Unexpected termination of simulation !")
        exit(1)
