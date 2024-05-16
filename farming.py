import smartpy as sp  # type: ignore
import utilities.Address as Address  # Dummy Addresses
from farming_contract_types import farming_types  # Contract variable types


@sp.module
def farming_contract_module():

    class FarmingContract(sp.Contract):
        def __init__(
            self,
            administrator,
            metadata,
        ):
            # Metadata of the contract
            self.data.metadata = sp.cast(metadata, sp.big_map[sp.string, sp.bytes])
            # Administration panel to handle the contract
            self.data.administration_panel = sp.cast(
                sp.record(
                    administrator=administrator,
                    pendingAdministrator=None,
                    paused=False,
                ),
                farming_types.administration_panel_type,
            )
            self.data.farms = sp.cast(
                sp.big_map(), sp.big_map[sp.nat, farming_types.farm_type]
            )
            self.data.next_farm_id = sp.cast(0, sp.nat)
            self.data.ledger = sp.cast(
                sp.big_map(),
                sp.big_map[
                    farming_types.ledger_key_type, farming_types.ledger_value_type
                ],
            )
            self.data.vaults = sp.cast(sp.big_map(), sp.big_map[sp.address, sp.address])

        @sp.private(with_storage="read-only")
        def _isAdmin(self):
            assert sp.sender == self.data.administration_panel.administrator, "NotAdmin"

        # Update Admin
        @sp.entrypoint
        def proposeAdmin(self, newAdminAddress):
            sp.cast(newAdminAddress, sp.address)
            self._isAdmin()
            self.data.administration_panel.pendingAdministrator = sp.Some(
                newAdminAddress
            )

        # Verify Admin
        @sp.entrypoint
        def updateAdmin(self):
            assert (
                self.data.administration_panel.pendingAdministrator.is_some()
            ), "NoPendingAdministrator"
            assert (
                sp.sender
                == self.data.administration_panel.pendingAdministrator.unwrap_some()
            ), "NotAuthorized"
            self.data.administration_panel.administrator = (
                self.data.administration_panel.pendingAdministrator.unwrap_some()
            )
            self.data.administration_panel.pendingAdministrator = None
