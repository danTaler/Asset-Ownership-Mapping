class OpenStackProject:
    id = ""
    name = ""
    description = ""
    tags = ""
    enabled = ""
    domain_id = ""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
