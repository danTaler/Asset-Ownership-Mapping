class AwsEntry:
    account_id = ""
    region = ""
    region_ec2_count = ""
    instance_id = ""
    instance_type = ""
    instance_public_ip = ""
    instance_public_dns_name = ""
    instance_private_ip = ""
    instance_state = ""
    instance_launch_date = ""
    instance_platform_details = ""
    app_code = ""
    service_owner = ""
    tags_names = ""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
