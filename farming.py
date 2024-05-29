import smartpy as sp  # type: ignore
import utilities.Address as Address  # Dummy Addresses
from farming_contract_types import farming_types  # Contract variable types


@sp.module
def farming_contract_module():

    class FarmingContract(sp.Contract):
        # intial storage
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
            # Farms big_map to store all the farms data
            self.data.farms = sp.cast(
                sp.big_map(), sp.big_map[sp.nat, farming_types.farm_type]
            )
            # Total farms count
            self.data.next_farm_id = sp.cast(0, sp.nat)
            # Ldeger to store all the user data
            self.data.ledger = sp.cast(
                sp.big_map(),
                sp.big_map[
                    farming_types.ledger_key_type, farming_types.ledger_value_type
                ],
            )
            # Vaults to store all the user assets data
            self.data.vaults = sp.cast(sp.big_map(), sp.big_map[sp.address, sp.address])

        # Check if the sender is the administrator
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

        # Toggle pause contract
        @sp.entrypoint
        def togglePause(self):
            self._isAdmin()
            if self.data.administration_panel.paused:
                self.data.administration_panel.paused = False
            else:
                self.data.administration_panel.paused = True

        # Transfer FA2 token function
        @sp.private(with_storage="read-write", with_operations=True)
        def transfer_fa2_token(self, params):
            sp.cast(params, farming_types.transfer_fa2_token_params_type)
            contractParams = sp.contract(
                farming_types.transfer_params_type,
                params.token_address,
                "transfer",
            ).unwrap_some()
            dataToBeSent = sp.cast(
                [
                    sp.record(
                        from_=params.from_address,
                        txs=[
                            sp.record(
                                to_=params.to_address,
                                amount=params.token_amount,
                                token_id=params.token_id,
                            )
                        ],
                    )
                ],
                farming_types.transfer_params_type,
            )
            sp.transfer(dataToBeSent, sp.mutez(0), contractParams)

        # Transfer FA12 token function
        @sp.private(with_storage="read-write", with_operations=True)
        def transfer_fa12_token(self, params):
            sp.cast(params, farming_types.transfer_fa12_token_params_type)
            contractParams = sp.contract(
                farming_types.transfer_fa12_params_type,
                params.token_address,
                "transfer",
            ).unwrap_some()
            dataToBeSent = sp.cast(
                sp.record(
                    from_=params.from_address,
                    to_=params.to_address,
                    value=params.token_amount,
                ),
                farming_types.transfer_fa12_params_type,
            )
            sp.transfer(dataToBeSent, sp.mutez(0), contractParams)

        # Create a new farm
        @sp.entrypoint
        def createFarm(self, params):
            sp.cast(params, farming_types.create_farm_params_type)
            farm_id = self.data.next_farm_id
            farm_duration = sp.as_nat(params.end_time - params.start_time)
            self.data.farms[farm_id] = sp.record(
                pool_token=params.pool_token,
                pool_balance=0,
                reward_token=params.reward_token,
                reward_supply=params.reward_supply,
                reward_paid=0,
                last_reward_time=params.start_time,
                acc_reward_per_share=0,
                reward_per_second=params.reward_supply / farm_duration,
                start_time=params.start_time,
                end_time=params.end_time,
                lock_duration=params.lock_duration,
                bonuses=params.bonuses,
                owner=sp.sender,
            )
            self.data.next_farm_id += 1
            with sp.match(params.reward_token.token_type):
                with sp.case.fa12 as data:
                    assert data == ()
                    trasfer_params = sp.record(
                        token_address=params.reward_token.address,
                        token_amount=params.reward_supply,
                        from_address=sp.sender,
                        to_address=sp.self_address(),
                    )
                    self.transfer_fa12_token(trasfer_params)
                with sp.case.fa2 as data:
                    assert data == ()
                    trasfer_params = sp.record(
                        token_address=params.reward_token.address,
                        token_id=params.reward_token.token_id,
                        token_amount=params.reward_supply,
                        from_address=sp.sender,
                        to_address=sp.self_address(),
                    )
                    self.transfer_fa2_token(trasfer_params)
            sp.emit(
                sp.record(farm_id=farm_id),
                tag="FarmCreated",
            )