from .OpenStackProject import OpenStackProject


class OpenStackServer:
    env = ""
    id = ""
    name = ""
    status = ""
    created = ""
    ip_address = ""
    ip_address_0 = ""
    ip_address_1 = ""
    ip_address_access = ""
    mac_address = ""
    mac_address_2 = ""
    metadata_appcode = ""
    metadata_hostname = ""
    metadata_owner = ""
    project = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        # Default to an empty project if one isn't set
        self.project = self.project or OpenStackProject()
