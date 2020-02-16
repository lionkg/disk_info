import subprocess


class BlkDev(object):

    """
    A class for block devices registered in the OS.
    The drives can be SAS/SATA/SSD or raid arrays controlled by MegaRaid
    or Adaptec
    """
    raid_card_types = {'MegaRaid': ['avago', 'lsi', 'megaraid'],
                       'Adaptec': ['adaptec', 'asr8805']}

    def __init__(self, name, array_vendor=None, id_in_array=None):
        self.name = name
        self.array_vendor = array_vendor
        self.id_in_array = id_in_array
        self.type = self.size_str = self.size_int = None
        self.model = self.vendor = self.sn = self.unit_id = None
        self.get_info()
        if self.type is None:
            raise 'Could not detect drive type'
        elif self.type != 'raid_array':
            self.get_dev_stats()
            self.get_dev_errors()

    def print_info(self):
        print('Block device name is {}'.format(self.name))
        print('Block device type is {}'.format(self.type))
        print('Block device vendor is {}'.format(self.vendor))
        print('Block device model is {}'.format(self.model))
        print('Block device size is {} bytes'.format(self.size_str))

    # get all drive info via smartctl
    def get_smartctl_info(self):
        if self.array_vendor == 'megaraid':
            megaraid_member_id = '-d megaraid,'+self.id_in_array
        else:
            megaraid_member_id = ''
        try:
            self.info = \
                subprocess.check_output(
                    'smartctl -i '+megaraid_member_id+' /dev/'+self.name,
                    shell=True, universal_newlines=True).splitlines()
        except subprocess.CalledProcessError:
            self.info = None
        return None

    # get block device info
    def get_info(self):
        self.get_smartctl_info()
        if self.info is not None:
            for line in self.info:
                if line.lower().startswith('vendor:'):
                    self.vendor = line.split()[-1].lower()
                elif line.lower().startswith('user capacity:'):
                    self.size_str = line.split()[2].lower()
                    self.size_int = self.size_str.replace(',', '')
                elif 'solid state device' in line.lower():
                    self.type = 'ssd'
                elif line.lower().startswith('serial number:'):
                    self.dev_sn = line.split()[-1].lower()
                elif line.lower().startswith('logical unit id:'):
                    self.dev_unit_id = \
                        line.split()[-1].lower().replace('0x', '', 1)
                elif (line.lower().startswith('device model:') or
                      line.lower().startswith('product:')):
                    self.model = line.split(':')[-1].lstrip('')
            if self.vendor in sum(BlkDev.raid_card_types.values(), []):
                for raid_vendor, model in BlkDev.raid_card_types.items():
                    if self.vendor in model:
                        self.vendor = raid_vendor
                        break
                self.type = 'raid_array'
            elif self.type is None:
                self.type = 'disk'
            if self.vendor is None:
                self.vendor = self.model.split()[-2]
                self.model = self.model.split()[-1]
        else:
            self.type = None
        return None

    # get drive statistics
    def get_dev_stats(self):
        print('Some stats')

    # get drive errors
    def get_dev_errors(self):
        print('Some errors')

    def __repr__(self):
        if self.array_vendor is not None:
            return "BlkDev({}, {}, {})".format(
                self.name, self.array_vendor, self.id_in_array)
        return "BlkDev({})".format(self.name)

    def __str__(self):
        return self.name
