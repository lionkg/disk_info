import subprocess
import re

from raidarray import RaidArrayMegaRaid


class RaidControllers(object):
    """
    An abstract class for RAID controllers.
    """

    def __init__(self):
        self.raid_controllers = {}
        self.get_controllers()

    # abstract method, do not use directly
    def get_controllers(self):
        raise NotImplementedError

    # abstract method, do not use directly, should be overridden in
    # vendorspecific subclass
    def get_controller_arrays(self):
        raise NotImplementedError

    # abstract method, do not use directly
    # get array by some attribute
    def fetch_array(self, array_attr_name, array_attr_value):
        raise NotImplementedError

    # abstract method, do not use directly
    # get array's physical devices list by some attribute
    def fetch_array_pd_list(self, array_attr_name, array_attr_value):
        raise NotImplementedError


class RaidControllersMegaRaid(RaidControllers):
    """
    A class for MegaRaid controllers
    """

    # added population of actual arrays detected on a MegaRaid controller
    def __init__(self):
        super().__init__()
        self.raid_vendor = 'MegaRaid'
        for controller_id in self.raid_controllers:
            arrays_list = self.get_controller_arrays(controller_id)
            self.raid_controllers[controller_id] = []
            for array_id in arrays_list:
                array = RaidArrayMegaRaid(controller_id, array_id)
                self.raid_controllers[controller_id].append(
                    (array_id, array.blk_dev_name, array))

    # get controllers list
    def get_controllers(self):
        self.controller_id_pattern = 'Controller ='
        self.controller_get_info_command = 'storcli64 /call show'

        try:
            self.raid_controller_info = subprocess.check_output(
                self.controller_get_info_command, shell=True,
                universal_newlines=True).splitlines()
        except subprocess.CalledProcessError:
            self.raid_controllers_list = None
            return None

        for line in self.raid_controller_info:
            if line.startswith(self.controller_id_pattern):
                self.raid_controllers[int(line.split()[-1])] = []
        return None

    # get raid arrays for raid controller
    def get_controller_arrays(self, raid_controller_id):
        arrays_list = []
        get_arrays_command = \
            'storcli64 /c'+str(raid_controller_id)+'/vall show'
        arrays = subprocess.check_output(
            get_arrays_command, shell=True,
            universal_newlines=True).splitlines()
        for line in arrays:
            if re.match('^[0-9]+/[0-9]+', line):
                arrays_list.append(
                    int(line.split('/')[1].split()[0]))
        return arrays_list

    # get array coordinates by attribute
    def fetch_array(self, array_attr_name, array_attr_value):
        for controller_id in self.raid_controllers:
            for array in self.raid_controllers[controller_id]:
                try:
                    if getattr(array[2], array_attr_name) == \
                            array_attr_value:
                        return controller_id, array[0], array[2]
                except AttributeError:
                    return None

    # get array's physical devices list
    def fetch_array_pd_list(self, array_attr_name, array_attr_value):
        for controller_id in self.raid_controllers:
            for array in self.raid_controllers[controller_id]:
                try:
                    if getattr(array[2], array_attr_name) == \
                            array_attr_value:
                        return array[2].pd_list
                except AttributeError:
                    return None


'''
class RaidControllersAdaptec(RaidControllers):
    """
    A class for Adaptec controllers
    """
    # get controllers list
    def get_raid_controllers_list(self):
        self.controller_id_pattern = 'Controller [0-9]+:'
        self.controller_get_info_command = 'arcconf list'

        try:
            self.raid_controller_info = subprocess.check_output(
                self.controller_get_info_command,
                shell=True, universal_newlines=True).splitlines()
        except subprocess.CalledProcessError:
            print('Could not get controllers list')
            self.raid_controllers_list = "NA"

        for line in self.raid_controller_info:
            if re.match(self.controller_id_pattern, line):
                self.raid_controllers_list.append(line.split()[1]).rstrip(':')
        return None
'''
