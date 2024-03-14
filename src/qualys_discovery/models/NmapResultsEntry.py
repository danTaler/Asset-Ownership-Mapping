from dataclasses import dataclass


@dataclass
class NmapResultsEntry:
    datacenter: str
    public_ip: str
    ports: list[str]
    hostname: str
