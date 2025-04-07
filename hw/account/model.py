from dataclasses import dataclass
from enum import Enum


class AccountStatus(Enum):
    BLOCKED = 'blocked'
    PENDING = 'pending'
    PROCESSING = 'processing'


@dataclass
class Account:
    id: int
    phone_number: str
    password: str
    status: AccountStatus = AccountStatus.PENDING
