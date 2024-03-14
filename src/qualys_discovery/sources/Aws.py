#! /usr/bin/env python3
import json
import logging

import boto3
from botocore.exceptions import ClientError

from models.AwsEntry import AwsEntry
from models.AwsAccount import AwsAccount

logging.basicConfig(
    level="INFO", format="%(asctime)s %(levelname)s %(filename)s:%(lineno)d %(message)s"
)


class Aws:
    def __init__(self, db):
        self._db = db
        self._orgs = boto3.client("organizations")

    def sync(self):
        self._db.reset()

        regions = self._fetch_ec2_regions()
        accounts = self._fetch_aws_accounts_details()

        self._save_accounts_and_tags(accounts)
        for account_id in accounts:
            logging.info("Fetching and saving details for %s", account_id)
            creds = self._assume_qualys_discovery_role(account_id)

            if isinstance(creds, dict):
                try:
                    self._fetch_and_save_ec2_instances_per_region(
                        account_id,
                        creds,
                        regions,
                    )
                except Exception as e:
                    logging.error("Could not assume role for %s", account_id)
                    logging.exception(e)
            else:
                logging.error("Could not assume role for %s", account_id)

    def _fetch_aws_accounts_details(self):
        """
        Returns dictionary of Account IDs lists: of account name and email:
        : [accountname, account email, status]
        """
        return {
            acct["Id"]: [acct["Name"], acct["Email"], acct["Status"]]
            for page in self._orgs.get_paginator("list_accounts").paginate()
            for acct in page["Accounts"]
        }

    def _save_accounts_and_tags(self, accounts):
        """
        AWS Account Details
        AWS Account Tags
        BusinessUnit, CustomerName, PrimaryContact, ContactEmail
        """
        for account_id, details in accounts.items():
            tags = self._orgs.list_tags_for_resource(ResourceId=account_id)
            tags = {tag.get("Key"): tag.get("Value") for tag in tags["Tags"]}

            self._db.insert_aws_account(
                AwsAccount(
                    id=account_id,
                    name=details[0],
                    email=details[1],
                    status=details[2],
                    metadata_bu=tags.get("BusinessUnit") or "",
                    metadata_customer_name=tags.get("CustomerName") or "",
                    metadata_primary_contact=tags.get("PrimaryContact") or "",
                    metadata_contact_email=tags.get("ContactEmail") or "",
                )
            )

    def _assume_qualys_discovery_role(self, account_id):
        """
        Get the assume role from the account id
        """
        try:
            # Call the assume_role method of the STSConnection object and pass the role
            # ARN and a role session name.
            assumed_role_object = boto3.client("sts").assume_role(
                RoleArn=f"arn:aws:iam::{account_id}:role/QualysDiscovery",
                RoleSessionName="qualys_assume",
            )

            # From the response that contains the assumed role, get the temporary
            # creds that can be used to make subsequent API calls
            return assumed_role_object["Credentials"]
        except ClientError as ex:
            logging.info("Consuming Issue: %s", ex.response["Error"]["Message"])
            return ""

    def _ec2_client(self, region, creds):
        """
        Use the temporary creds that AssumeRole returns to make a connection
        """
        return boto3.resource(
            "ec2",
            region_name=region,
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
        )

    def _fetch_ec2_regions(self):
        """
        Return a list of: all regions (creds from memory)
        """
        return [
            region["RegionName"]
            for region in boto3.client("ec2").describe_regions()["Regions"]
        ]

    def _add_ec2_metadata(self, entry, instance):
        """
        Add instance metadata to entry
        """
        entry.instance_id = instance.id
        entry.instance_type = instance.platform_details
        entry.instance_public_ip = instance.public_ip_address
        entry.instance_public_dns_name = instance.public_dns_name
        entry.instance_private_ip = instance.private_ip_address
        entry.instance_state = instance.state["Name"]
        entry.instance_launch_date = instance.launch_time

        if instance.tags:
            tags = {tag["Key"]: tag["Value"] for tag in instance.tags}
            entry.app_code = tags.get("AppCode") or ""
            entry.service_owner = tags.get("ServiceOwner") or ""
            entry.tags_names = json.dumps(instance.tags)

    def _fetch_and_save_ec2_instances_per_region(self, account_id, creds, regions):
        """
        Per each region, get EC2s from each account id by assuming a role for each org id.
        Steps:
            1. Iterate each region
            2. Assume accound id role (receive new STS role session)
            3. Get instances metadata
        """

        # -- Iterate each region: --
        for region in regions:
            # Use the temporary creds that AssumeRole returns to make a connection
            # to look up ec2 instances
            instances = self._ec2_client(region, creds).instances.all()
            entry = AwsEntry(account_id=account_id, region=region)

            try:
                # -- Count EC2s in region --
                region_ec2_count = len(set(instances))

                if region_ec2_count:
                    for instance in instances:
                        entry.region_ec2_count = region_ec2_count
                        self._add_ec2_metadata(entry, instance)
                        self._db.insert_aws_entry(entry)
                else:
                    entry.region_ec2_count = 0
                    self._db.insert_aws_entry(entry)

            except ClientError:
                entry.region_ec2_count = 0
                self._db.insert_aws_entry(entry)
