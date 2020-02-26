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

        self.dev_type = self.size = self.model = \
            self.vendor = self.sn = self.unit_id = None

        self.info = self.get_smart_info()
        self.dev_type = self.get_type()

        if self.dev_type is None:
            raise ValueError('Could not detect drive type')

    def print_info(self):
        print('Block device name is {}'.format(self.name))
        print('Block device type is {}'.format(self.dev_type))
        print('Block device vendor is {}'.format(self.vendor))
        print('Block device model is {}'.format(self.model))
        print('Block device size is {} bytes'.format(self.size[0]))

    # get all drive info via smartctl
    def get_smart_info(self):
        if self.array_vendor == 'megaraid':
            cmd = \
                'smartctl -i -d megaraid,'+self.id_in_array+' /dev/'+self.name
        elif self.array_vendor == 'adaptec':
            cmd = 'smartctl -i /dev/'+self.name
        else:
            cmd = 'smartctl -i /dev/'+self.name
        try:
            info = \
                subprocess.check_output(cmd, shell=True,
                                        universal_newlines=True).splitlines()
        except subprocess.CalledProcessError:
            info = None
            raise subprocess.CalledProcessError(
                'Could not get S.M.A.R.T. info')
        return info

    def get_vendor(self):
        for line in self.info:
            if line.lower().startswith('vendor:'):
                vendor = line.split()[-1].lower()
                break
        if vendor in sum(BlkDev.raid_card_types.values(), []):
            for raid_vendor, model in BlkDev.raid_card_types.items():
                if vendor in model:
                    vendor = raid_vendor
                    break
        if vendor is None:
            self.get_model()
            vendor = self.model.split()[-2]
            self.model = self.model.split()[-1]
        if vendor is None:
            raise ValueError('Could not detect drive vendor.')
        return vendor

    def get_model(self):
        for line in self.info:
            if (line.lower().startswith('device model:') or
                    line.lower().startswith('product:')):
                model = line.split(':')[-1].lstrip()
                return model
        if model is None:
            raise ValueError('Could not detect drive model.')
        return model

    def get_type(self):
        for line in self.info:
            if 'solid state device' in line.lower():
                dev_type = 'ssd'
                return dev_type

        self.vendor = self.get_vendor()

        if self.vendor in BlkDev.raid_card_types.keys():
            for raid_vendor, model in BlkDev.raid_card_types.items():
                if self.vendor in model:
                    self.vendor = raid_vendor
                    break
            dev_type = 'raid_array'
        else:
            dev_type = 'disk'
        if dev_type is None:
            raise ValueError('Could not detect drive type.')
        return dev_type

    # get block device info
    def get_size(self):
        for line in self.info:
            if line.lower().startswith('user capacity:'):
                size = []
                size.append(line.split()[2].lower())
                size.append(size[0].replace(',', ''))
                break
        if size is None:
            raise ValueError('Could not detect drive size.')
        return size

    def get_sn(self):
        for line in self.info:
            if line.lower().startswith('serial number:'):
                sn = line.split()[-1].lower()
                break
        if sn is None:
            raise ValueError('Could not detect drive serial number.')
        return sn

    def get_dev_unit_id(self):
        for line in self.info:
            if line.lower().startswith('logical unit id:'):
                dev_unit_id = \
                    line.split()[-1].lower().replace('0x', '', 1)
                break
        return dev_unit_id

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
