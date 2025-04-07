from typing import Optional, Protocol, List

from account.model import Account


class AccountsStorageProtocol(Protocol):

    def get_all_accounts(self) -> List[Account]:
        ...

    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        ...

    def mark_account_as_blocked(self, account_id: int):
        ...

    def add_account(self) -> int:
        ...

    def set_account_processing(self, account_id: int) -> Optional[Account]:
        ...

    def set_account_pending(self, account_id: int) -> Optional[Account]:
        ...

    def clear(self):
        ...
