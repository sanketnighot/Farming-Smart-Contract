import smartpy as sp  # type: ignore
import utilities.Address as Address  # Dummy Addresses
from farming_contract_types import farming_types  # Contract variable types


@sp.module
def farming_contract_module():
    DECIMAL = 1000000000000

    # Transfer FA2 token function
    @sp.effects(with_storage="read-only", with_operations=True)
    def transfer_fa2_token(params):
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
    @sp.effects(with_storage="read-only", with_operations=True)
    def transfer_fa12_token(params):
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

    # Calculate the pending rewards
    @sp.effects(with_storage="read-only")
    def calculate_pending_rewards(params):
        sp.cast(params, sp.record(farm_id=sp.nat, user=sp.address))
        assert self.data.farms.contains(params.farm_id), "FarmNotFound"
        assert self.data.ledger.contains(
            (params.farm_id, params.user)
        ), "DepositsNotFound"
        pending_rewards = sp.as_nat(
            (
                self.data.farms[params.farm_id].acc_reward_per_share
                * self.data.ledger[(params.farm_id, params.user)].amount
                / DECIMAL
            )
            - self.data.ledger[(params.farm_id, params.user)].reward_debt
        )
        sp.trace(sp.record(pending_rewards=pending_rewards))
        return pending_rewards

    # Harvest tokens from farm
    @sp.effects(with_storage="read-write", with_operations=True)
    def harvest_rewards(params):
        sp.cast(params, sp.record(farm_id=sp.nat, user=sp.address))
        assert self.data.farms.contains(params.farm_id), "FarmNotFound"
        assert self.data.ledger.contains(
            (params.farm_id, params.user)
        ), "DepositsNotFound"
        assert self.data.farms[params.farm_id].start_time <= sp.now, "FarmNotStarted"
        assert (
            self.data.ledger[(params.farm_id, params.user)].amount > 0
        ), "NoTokensFound"
        elasped_time = sp.as_nat(
            sp.now - self.data.farms[params.farm_id].last_reward_time
        )
        if sp.now > self.data.farms[params.farm_id].end_time:
            elasped_time = sp.as_nat(
                self.data.farms[params.farm_id].end_time
                - self.data.farms[params.farm_id].last_reward_time
            )
        self.data.farms[params.farm_id].acc_reward_per_share += (
            self.data.farms[params.farm_id].reward_per_second * elasped_time * DECIMAL
        ) / self.data.ledger[(params.farm_id, params.user)].amount
        user_reward = calculate_pending_rewards(
            sp.record(farm_id=params.farm_id, user=params.user)
        )
        with sp.match(self.data.farms[params.farm_id].reward_token.token_type):
            with sp.case.fa12 as data:
                assert data == ()
                trasfer_params = sp.record(
                    token_address=self.data.farms[params.farm_id].reward_token.address,
                    token_amount=user_reward,
                    from_address=params.user,
                    to_address=sp.self_address(),
                )
                transfer_fa12_token(trasfer_params)
            with sp.case.fa2 as data:
                assert data == ()
                trasfer_params = sp.record(
                    token_address=self.data.farms[params.farm_id].reward_token.address,
                    token_id=self.data.farms[params.farm_id].reward_token.token_id,
                    token_amount=user_reward,
                    from_address=params.user,
                    to_address=sp.self_address(),
                )
                transfer_fa2_token(trasfer_params)
        self.data.farms[params.farm_id].reward_paid += user_reward
        self.data.ledger[(params.farm_id, params.user)].reward_debt += user_reward
        self.data.farms[params.farm_id].last_reward_time = sp.now
        sp.emit(
            sp.record(farm_id=params.farm_id, user=params.user, reward=user_reward),
            tag="Harvested",
        )

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
                reward_per_second=(params.reward_supply) / farm_duration,
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
                    transfer_fa12_token(trasfer_params)
                with sp.case.fa2 as data:
                    assert data == ()
                    trasfer_params = sp.record(
                        token_address=params.reward_token.address,
                        token_id=params.reward_token.token_id,
                        token_amount=params.reward_supply,
                        from_address=sp.sender,
                        to_address=sp.self_address(),
                    )
                    transfer_fa2_token(trasfer_params)
            sp.emit(
                sp.record(farm_id=farm_id),
                tag="FarmCreated",
            )

        # Deposit tokens to farm
        @sp.entrypoint
        def deposit(self, params):
            sp.cast(params, farming_types.deposit_params_type)
            assert self.data.farms.contains(params.farm_id), "FarmNotFound"
            farm = self.data.farms[params.farm_id]
            assert farm.start_time <= sp.now, "FarmNotStarted"
            assert farm.end_time >= sp.now, "FarmEnded"
            assert params.token_amount > 0, "InvalidAmount"
            if (
                self.data.ledger.contains((params.farm_id, sp.sender))
                and self.data.ledger[(params.farm_id, sp.sender)].amount > 0
            ):
                harvest_rewards(sp.record(farm_id=params.farm_id, user=sp.sender))
            with sp.match(farm.pool_token.token_type):
                with sp.case.fa12 as data:
                    assert data == ()
                    trasfer_params = sp.record(
                        token_address=farm.pool_token.address,
                        token_amount=params.token_amount,
                        from_address=sp.sender,
                        to_address=sp.self_address(),
                    )
                    transfer_fa12_token(trasfer_params)
                with sp.case.fa2 as data:
                    assert data == ()
                    trasfer_params = sp.record(
                        token_address=farm.pool_token.address,
                        token_id=farm.pool_token.token_id,
                        token_amount=params.token_amount,
                        from_address=sp.sender,
                        to_address=sp.self_address(),
                    )
                    transfer_fa2_token(trasfer_params)
            self.data.farms[params.farm_id].pool_balance += params.token_amount
            if self.data.ledger.contains((params.farm_id, sp.sender)):
                self.data.ledger[
                    (params.farm_id, sp.sender)
                ].amount += params.token_amount
            else:
                self.data.ledger[(params.farm_id, sp.sender)] = sp.record(
                    amount=params.token_amount, reward_debt=0, lock_end_time=sp.now
                )
            sp.emit(
                sp.record(
                    farm_id=params.farm_id,
                    user=sp.sender,
                    amount=params.token_amount,
                ),
                tag="TokensDeposited",
            )

        # Harvest rewards
        @sp.entrypoint
        def harvest(self, farm_id):
            sp.cast(farm_id, sp.nat)
            harvest_rewards(sp.record(farm_id=farm_id, user=sp.sender))
