from dataclasses import dataclass
from functools import total_ordering

@total_ordering
@dataclass(eq=False)
class Pod:
    hostname: str
    ip_address: str
    mac_address: str
    is_running: bool = False

    def __eq__(self, other):
        return (self.hostname == other.hostname) and \
                (self.ip_address == other.ip_address) and \
                (self.mac_address == other.mac_address)

    def __lt__(self, other):
        raise NotImplementedError
