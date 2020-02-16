import subprocess
import re

from diskdrive import BlkDev


class RaidArray(object):
    """
    An abstract class for RAID arrays.
    """
    def __init__(self, controller_id, array_id):
        self.level = self.status = self.scsi_id = self.pd_list = \
            self.access = self.cache = self.size = None
        self.controller_id = controller_id
        self.id = array_id
        self.pd_list = []
        self.get_attrs()
        if self.scsi_id is None:
            pass
        self.get_blk_dev_name()
        self.get_pd_list()

    # get array info
    def get_info(self):
        raise NotImplementedError

    # get corresponding block device name
    def get_blk_dev_name(self):
        raise NotImplementedError

    # get the list of physical drives for a raid array
    def get_pd_list(self):
        raise NotImplementedError

    def __repr__(self):
        return "{}({}, {})".format(
            self.__class__.__name__, self.controller_id, self.id)

    def __str__(self):
        return 'Raid device name is /dev/{} and status is {}'.format(
            self.blk_dev_name, self.status)


class RaidArrayMegaRaid(RaidArray):

    # get array info
    def get_info(self):
        array_get_info_command = \
            'storcli64 /c'+str(
                self.controller_id)+'/v'+str(self.id)+' show all'
        try:
            self.info = subprocess.check_output(
                array_get_info_command, shell=True,
                universal_newlines=True).splitlines()
        except subprocess.CalledProcessError:
            self.info = None

    def get_attrs(self):
        self.get_info()
        if self.info is not None:
            for line in self.info:
                if re.match('^[0-9]+/[0-9]+', line):
                    self.level = line.split()[1]
                    self.status = line.split()[2]
                    self.access = line.split()[3]
                    self.cache = line.split()[3]
                    self.size = line.split()[2]
                elif line.lower().startswith('scsi naa id'):
                    self.scsi_id = line.split()[-1].lower()

    def get_blk_dev_name(self):
        get_blk_dev_name_cmd = \
            'readlink -f /dev/disk/by-id/wwn-0x'+self.scsi_id
        try:
            self.blk_dev_name = subprocess.check_output(
                get_blk_dev_name_cmd, shell=True,
                universal_newlines=True).split('/')[-1].rstrip()
        except subprocess.CalledProcessError:
            self.blk_dev_name = None

    def get_pd_list(self):
        for line in self.info:
            if re.match('^[0-9]+:[0-9]+ ', line):
                self.pd_list.append([line.split()[0], line.split()[1]])
        self.pd_list = tuple(self.pd_list)
        for pd in self.pd_list:
            pd.append(BlkDev(self.blk_dev_name, 'megaraid', pd[1]))
