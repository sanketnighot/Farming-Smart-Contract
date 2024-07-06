import smartpy as sp  # type: ignore
from farming import farming_contract_module
import utilities.Address as Address
from farming_contract_types import farming_types
from utilities.fa2_fungible_minimal import fa2_fungible

if __name__ == "__main__":

    @sp.add_test()
    def test():
        # Create test scenarios and import the required modules
        sc = sp.test_scenario(
            "FarmingContractTest",
            [farming_types, sp.utils, fa2_fungible, farming_contract_module],
        )

        # Originate the token contract
        sc.h2("Originate token Contract")
        token = fa2_fungible.Fa2FungibleMinimal(
            administrator=Address.admin,
            metadata=sp.scenario_utils.metadata_of_url("https://token.com"),
        )
        sc += token

        reward_token = fa2_fungible.Fa2FungibleMinimal(
            administrator=Address.admin,
            metadata=sp.scenario_utils.metadata_of_url("https://reward_token.com"),
        )
        sc += reward_token

        token.mint(
            sp.record(
                amount=sp.nat(1_000_000_000_000_000),
                to_=Address.admin,
                token=sp.variant("new", {"0": sp.bytes("0x746f6b656e30")}),
            ),
            _sender=Address.admin,
        )

        reward_token.mint(
            sp.record(
                amount=sp.nat(1_000_000_000_000_000),
                to_=Address.admin,
                token=sp.variant("new", {"0": sp.bytes("0x746f6b656e30")}),
            ),
            _sender=Address.admin,
        )

        token.mint(
            sp.record(
                amount=sp.nat(1_000_000_000_000_000),
                to_=Address.alice,
                token=sp.variant("existing", sp.nat(0)),
            ),
            _sender=Address.admin,
        )

        token.mint(
            sp.record(
                amount=sp.nat(1_000_000_000_000_000),
                to_=Address.bob,
                token=sp.variant("existing", sp.nat(0)),
            ),
            _sender=Address.admin,
        )

        # Current Token Storage
        sc.h2("Current Token Storage")
        sc.show(token.data.ledger)

        # Originate the farming contract
        sc.h1("Farming Contract")
        sc.h2("Originate Farming Contract")
        farming_contract = farming_contract_module.FarmingContract(
            administrator=Address.admin,
            metadata=sp.scenario_utils.metadata_of_url("https://example.com"),
        )
        sc += farming_contract

        # Adding Contract as Operator
        sc.h2("Adding Contract as Operator")
        token.update_operators(
            [
                sp.variant(
                    "add_operator",
                    sp.record(
                        owner=Address.admin,
                        operator=farming_contract.address,
                        token_id=0,
                    ),
                )
            ],
            _sender=Address.admin,
        )

        reward_token.update_operators(
            [
                sp.variant(
                    "add_operator",
                    sp.record(
                        owner=Address.admin,
                        operator=farming_contract.address,
                        token_id=0,
                    ),
                )
            ],
            _sender=Address.admin,
        )

        token.update_operators(
            [
                sp.variant(
                    "add_operator",
                    sp.record(
                        owner=Address.alice,
                        operator=farming_contract.address,
                        token_id=0,
                    ),
                )
            ],
            _sender=Address.alice,
        )

        token.update_operators(
            [
                sp.variant(
                    "add_operator",
                    sp.record(
                        owner=Address.bob,
                        operator=farming_contract.address,
                        token_id=0,
                    ),
                )
            ],
            _sender=Address.bob,
        )

        # Log the initial storage
        sc.h2("Initial Storage")
        sc.show(farming_contract.data)

        # Create New Farm 0
        sc.h2("Create Farm 0")
        createFarmParams = sp.record(
            pool_token=sp.record(
                address=token.address,
                token_id=sp.nat(0),
                token_type=sp.variant.fa2(()),
            ),
            reward_token=sp.record(
                address=reward_token.address,
                token_id=sp.nat(0),
                token_type=sp.variant.fa2(()),
            ),
            reward_supply=sp.nat(100_000_000),
            start_time=sp.timestamp(1),
            end_time=sp.timestamp(101),
            lock_duration=sp.nat(0),
            bonuses=set(),
        )
        farming_contract.createFarm(
            createFarmParams,
            _sender=Address.admin,
            _now=sp.timestamp(0),
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)

        # Deposit to Farm
        sc.h2("Deposit 1 to Farm")
        farming_contract.deposit(
            sp.record(farm_id=sp.nat(0), token_amount=sp.nat(3_000_000)),
            _sender=Address.alice,
            _now=sp.timestamp(2),
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)

        # Deposit to Farm
        sc.h2("Deposit 2 to Farm")
        farming_contract.deposit(
            sp.record(farm_id=sp.nat(0), token_amount=sp.nat(7_000_000)),
            _sender=Address.bob,
            _now=sp.timestamp(7),
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)

        # Harvest from Farm
        sc.h2("Harvest 1 from Farm")
        farming_contract.harvest(
            sp.nat(0),
            _sender=Address.alice,
            _now=sp.timestamp(30),
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)

        sc.h2("Harvest 2 from Farm")
        farming_contract.harvest(
            sp.nat(0),
            _sender=Address.bob,
            _now=sp.timestamp(70),
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)

        # Withdraw from Farm
        sc.h2("Withdraw 1 from Farm")
        farming_contract.withdraw(
            sp.record(farm_id=sp.nat(0), token_amount=sp.nat(3_000_000)),
            _sender=Address.alice,
            _now=sp.timestamp(88),
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)
        sc.show(token.data.ledger)

        # Withdraw from Farm
        sc.h2("Withdraw 2 from Farm")
        farming_contract.withdraw(
            sp.record(farm_id=sp.nat(0), token_amount=sp.nat(7_000_000)),
            _sender=Address.bob,
            _now=sp.timestamp(92),
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)

        sc.h2("Deposit 1 to Farm")
        farming_contract.deposit(
            sp.record(farm_id=sp.nat(0), token_amount=sp.nat(3_000)),
            _sender=Address.alice,
            _now=sp.timestamp(96),
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)

        sc.show(
            farming_contract.getLedger(sp.record(farm_id=sp.nat(0), user=Address.alice))
        )

        sc.h2("Withdraw 1 from Farm")
        farming_contract.withdraw(
            sp.record(farm_id=sp.nat(0), token_amount=sp.nat(3_000)),
            _sender=Address.alice,
            _now=sp.timestamp(102),
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)
        sc.show(token.data.ledger)
        sc.show(reward_token.data.ledger)
        sc.show(farming_contract.getFarm(sp.nat(0)))

        # End Farm
        sc.h2("End Farm")
        farming_contract.endFarm(
            sp.nat(0), _sender=Address.admin, _now=sp.timestamp(103)
        )

        # Log the current storage
        sc.h2("Current Data")
        sc.show(farming_contract.data)
        sc.show(token.data.ledger)
        sc.show(reward_token.data.ledger)
        sc.show(farming_contract.getFarm(sp.nat(0)))
