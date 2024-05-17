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

        # Create New Farm
        sc.h2("Create Farm")
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
            reward_supply=sp.nat(1000000),
            reward_per_second=sp.nat(12),
            start_time=sp.timestamp(12),
            end_time=sp.timestamp(24),
            lock_duration=sp.int(12),
            bonuses=set(),
        )
        farming_contract.createFarm(
            createFarmParams,
            _sender=Address.admin,
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)

        # Create New Farm
        sc.h2("Create Farm")
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
            reward_per_second=sp.nat(342423),
            start_time=sp.timestamp(324),
            end_time=sp.timestamp(3423),
            lock_duration=sp.int(234),
            bonuses=set(),
        )
        farming_contract.createFarm(
            createFarmParams,
            _sender=Address.alice,
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)
