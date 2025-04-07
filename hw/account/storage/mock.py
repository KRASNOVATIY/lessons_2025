from typing import Optional, List

from account.model import Account, AccountStatus
from account.storage.protocol import AccountsStorageProtocol


class MockAccountsStorage(AccountsStorageProtocol):
    def __init__(self):
        self.accounts = []

    def get_all_accounts(self) -> List[Account]:
        return self.accounts

    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        for x in self.accounts:
            if x.id == account_id:
                return x

    def mark_account_as_blocked(self, account_id: int):
        acc = self.get_account_by_id(account_id)
        if acc:
            acc.status = AccountStatus.BLOCKED

    def add_account(self) -> int:
        curr_accounts_count = len(self.accounts)
        new_acc_id = curr_accounts_count + 1
        new_acc = Account(
            id=new_acc_id,
            password='password',
            phone_number='88002000600',
        )
        self.accounts.append(new_acc)

        return new_acc_id

    def set_account_processing(self, account_id: int) -> Optional[Account]:
        acc = self.get_account_by_id(account_id)
        if acc:
            acc.status = AccountStatus.PROCESSING
            return acc

    def set_account_pending(self, account_id: int) -> Optional[Account]:
        acc = self.get_account_by_id(account_id)
        if acc:
            acc.status = AccountStatus.PENDING
            return acc

    def clear(self):
        self.accounts = []
