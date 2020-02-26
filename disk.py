#!/usr/bin/python3

import subprocess
import distutils.spawn

from diskdrive import BlkDev
from raidcontrollers import RaidControllersMegaRaid, RaidControllersAdaptec


# method to check for required uttilities
def check4tool(name):
    if distutils.spawn.find_executable(name) is None:
        print('CRITICAL: {} could not be found'.format(name))
        exit(1)
    return True


if __name__ == '__main__':
    # Check for lspci
    check4tool('lspci')

    # Check if the server is a VM
    is_vm = subprocess.check_output("lspci", shell=True,
                                    universal_newlines=True).splitlines()
    for line in is_vm:
        if "virtio" in line.lower():
            print("OK: this is a virtual machine")
            exit(0)

    # Check for the other tools
    required_tools = ('lsblk', 'smartctl', 'parted')
    for tool in required_tools:
        check4tool(tool)

    # Get the full list of physical dirves with parameters
    try:
        blkdev_list = \
            subprocess.check_output('lsblk -dn -o NAME', shell=True,
                                    universal_newlines=True).splitlines()
    except subprocess.CalledProcessError:
        print("CRITICAL: could not get list of physical drives")
        exit(2)

    # Run through block devices found
    for blk_device in blkdev_list:
        if blk_device.startswith('sd'):
            drive = BlkDev(blk_device.split()[0])
            if drive.vendor == 'MegaRaid':
                check4tool('storcli64')
                try:
                    megaraid_raid_controllers
                except NameError:
                    megaraid_raid_controllers = RaidControllersMegaRaid()

                raid_array = megaraid_raid_controllers.fetch_array(
                    'blk_dev_name', blk_device)
            elif drive.vendor == 'Adaptec':
                check4tool('arcconf')
                try:
                    adaptec_raid_controllers
                except NameError:
                    adaptec_raid_controllers = RaidControllersAdaptec()

                raid_array = adaptec_raid_controllers.fetch_array(
                    'blk_dev_name', blk_device)
