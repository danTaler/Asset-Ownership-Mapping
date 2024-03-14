class AwsAccount:
    id = ""
    name = ""
    email = ""
    status = ""
    metadata_bu = ""
    metadata_customer_name = ""
    metadata_primary_contact = ""
    metadata_contact_email = ""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
