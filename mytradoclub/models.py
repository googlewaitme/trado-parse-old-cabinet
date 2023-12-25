from dataclasses import dataclass
from typing import Optional


@dataclass
class Distributor:
    club_number: Optional[str] = None
    fio: Optional[str] = None
