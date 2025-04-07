from dataclasses import dataclass

from account.model import AccountStatus
from account.storage.mock import MockAccountsStorage
from account.storage.protocol import AccountsStorageProtocol
# from account.storage.postgres import AccountsPostgresStorage
# from account.storage.mongo import AccountsMongoStorage
# from account.storage.redis import AccountsRedisStorage


@dataclass
class AccountManager:
    accounts_storage: AccountsStorageProtocol

    def register_10_accounts(self):
        for _ in range(10):
            self.accounts_storage.add_account()

    def block_last_account(self):
        accounts = self.accounts_storage.get_all_accounts()
        last_account = accounts[-1]
        self.accounts_storage.mark_account_as_blocked(last_account.id)

    def work_with_2_and_4_accounts(self):
        accounts = self.accounts_storage.get_all_accounts()
        second = accounts[1]
        fourth = accounts[3]
        self.accounts_storage.set_account_processing(second.id)
        self.accounts_storage.set_account_processing(fourth.id)

    def clear(self):
        self.accounts_storage.clear()


def test_main():
    realisations = [MockAccountsStorage]  # [AccountsRedisStorage, AccountsPostgresStorage, AccountsMongoStorage]
    for r in realisations:
        am = AccountManager(r())
        try:
            accounts = am.accounts_storage.get_all_accounts()
            assert len(accounts) == 0
            am.register_10_accounts()
            am.work_with_2_and_4_accounts()
            am.block_last_account()
            accounts = am.accounts_storage.get_all_accounts()
            assert len(accounts) == 10
            assert accounts[0].status == AccountStatus.PENDING
            assert accounts[1].status == AccountStatus.PROCESSING
            assert accounts[2].status == AccountStatus.PENDING
            assert accounts[3].status == AccountStatus.PROCESSING
            assert accounts[4].status == AccountStatus.PENDING
            assert accounts[5].status == AccountStatus.PENDING
            assert accounts[6].status == AccountStatus.PENDING
            assert accounts[7].status == AccountStatus.PENDING
            assert accounts[8].status == AccountStatus.PENDING
            assert accounts[9].status == AccountStatus.BLOCKED
            print(f'With realisation {r} everything is OK')
        finally:
            am.clear()


if __name__ == '__main__':
    test_main()