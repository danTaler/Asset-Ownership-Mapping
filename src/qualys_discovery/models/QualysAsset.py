class QualysAsset:
    # pylint: disable=too-many-instance-attributes
    # These are reasonable for this case
    id = 0
    name = ""
    agent_status = ""
    aws_instance_id = ""
    fqdn = ""
    ip_address = ""
    last_checked_in = ""
    os = ""
    qweb_host_id = 0

    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
