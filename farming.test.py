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
