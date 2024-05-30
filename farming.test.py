import smartpy as sp  # type: ignore
from farming import farming_contract_module
import utilities.Address as Address
from farming_contract_types import farming_types

if __name__ == "__main__":

    @sp.add_test()
    def test():
        # Create test scenarios and import the required modules
        sc = sp.test_scenario(
            "FarmingContractTest", [farming_types, sp.utils, farming_contract_module]
        )

        # Originate the farming contract
        sc.h1("Farming Contract")
        sc.h2("Originate Farming Contract")
        farming_contract = farming_contract_module.FarmingContract(
            administrator=Address.admin,
            metadata=sp.scenario_utils.metadata_of_url("https://example.com"),
        )
        sc += farming_contract

        # Log the initial storage
        sc.h2("Initial Storage")
        sc.show(farming_contract.data)

        # Create New Farm 0
        sc.h2("Create Farm 0")
        createFarmParams = sp.record(
            pool_token=sp.record(
                address=sp.address("KT1PoolToken"),
                token_id=sp.nat(0),
                token_type=sp.variant.fa2(()),
            ),
            reward_token=sp.record(
                address=sp.address("KT1PoolToken"),
                token_id=sp.nat(0),
                token_type=sp.variant.fa2(()),
            ),
            reward_supply=sp.nat(1000000000),
            start_time=sp.timestamp(12),
            end_time=sp.timestamp(112),
            lock_duration=sp.int(0),
            bonuses=set(),
        )
        farming_contract.createFarm(
            createFarmParams,
            _sender=Address.admin,
            _now=sp.timestamp(12),
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)

        # Create New Farm 1
        sc.h2("Create Farm 1")
        createFarmParams = sp.record(
            pool_token=sp.record(
                address=sp.address("KT1PoolToken2"),
                token_id=sp.nat(0),
                token_type=sp.variant.fa2(()),
            ),
            reward_token=sp.record(
                address=sp.address("KT1PoolToken3"),
                token_id=sp.nat(0),
                token_type=sp.variant.fa12(()),
            ),
            reward_supply=sp.nat(2342343243),
            start_time=sp.timestamp(324),
            end_time=sp.timestamp(3423),
            lock_duration=sp.int(0),
            bonuses=set(),
        )
        farming_contract.createFarm(
            createFarmParams,
            _sender=Address.alice,
            _now=sp.timestamp(12),
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)

        # Deposit to Farm
        sc.h2("Deposit to Farm")
        farming_contract.deposit(
            sp.record(farm_id=sp.nat(0), token_amount=sp.nat(10000)),
            _sender=Address.alice,
            _now=sp.timestamp(12),
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)

        # # Deposit to Farm
        # sc.h2("Deposit to Farm")
        # farming_contract.deposit(
        #     sp.record(farm_id=sp.nat(0), token_amount=sp.nat(1000000)),
        #     _sender=Address.alice,
        #     _now=sp.timestamp(13),
        # )

        # # Log the current storage
        # sc.h2("Current Data")
        # sc.show(farming_contract.data)

        # Harvest from Farm
        sc.h2("Harvest from Farm")
        farming_contract.harvest(
            sp.nat(0),
            _sender=Address.alice,
            _now=sp.timestamp(13),
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)

        sc.h2("Harvest from Farm")
        farming_contract.harvest(
            sp.nat(0),
            _sender=Address.alice,
            _now=sp.timestamp(110),
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)

        # Withdraw from Farm
        sc.h2("Withdraw from Farm")
        farming_contract.withdraw(
            sp.record(farm_id=sp.nat(0), token_amount=sp.nat(5000)),
            _sender=Address.alice,
            _now=sp.timestamp(122),
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)

        # Withdraw from Farm
        sc.h2("Withdraw from Farm")
        farming_contract.withdraw(
            sp.record(farm_id=sp.nat(0), token_amount=sp.nat(5000)),
            _sender=Address.alice,
            _now=sp.timestamp(130),
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)
