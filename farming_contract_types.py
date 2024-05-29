import smartpy as sp  # type: ignore


@sp.module
def farming_types():
    # Administration panel bigmap value type
    administration_panel_type: type = sp.record(
        administrator=sp.address,
        pendingAdministrator=sp.option[sp.address],
        paused=sp.bool,
    )

    # Farm bigmap value type
    farm_type: type = sp.record(
        pool_token=sp.record(
            address=sp.address,
            token_id=sp.nat,
            token_type=sp.variant(fa12=sp.unit, fa2=sp.unit),
        ),
        pool_balance=sp.nat,
        reward_token=sp.record(
            address=sp.address,
            token_id=sp.nat,
            token_type=sp.variant(fa12=sp.unit, fa2=sp.unit),
        ),
        reward_supply=sp.nat,
        reward_paid=sp.nat,
        last_reward_time=sp.timestamp,
        acc_reward_per_share=sp.nat,
        reward_per_second=sp.nat,
        start_time=sp.timestamp,
        end_time=sp.timestamp,
        lock_duration=sp.int,
        bonuses=sp.set[sp.record(end_time=sp.timestamp, multipier=sp.nat)],
        owner=sp.address,
    )

    # Create farm entrypoint params type
    create_farm_params_type: type = sp.record(
        pool_token=sp.record(
            address=sp.address,
            token_id=sp.nat,
            token_type=sp.variant(fa12=sp.unit, fa2=sp.unit),
        ),
        reward_token=sp.record(
            address=sp.address,
            token_id=sp.nat,
            token_type=sp.variant(fa12=sp.unit, fa2=sp.unit),
        ),
        reward_supply=sp.nat,
        reward_per_second=sp.nat,
        start_time=sp.timestamp,
        end_time=sp.timestamp,
        lock_duration=sp.int,
        bonuses=sp.set[sp.record(end_time=sp.timestamp, multipier=sp.nat)],
    )

    # Ledger bigmap key type
    ledger_key_type: type = sp.pair[sp.nat, sp.address]

    # Ledger bigmap value type
    ledger_value_type: type = sp.record(
        amount=sp.nat, reward_debt=sp.nat, lock_end_time=sp.timestamp
    )

    # Transfer FA2 token entrypoint params type
    transfer_fa2_token_params_type: type = sp.record(
        token_address=sp.address,
        token_id=sp.nat,
        token_amount=sp.nat,
        from_address=sp.address,
        to_address=sp.address,
    )

    # FA2 token Transfer params type
    transfer_params_type: type = sp.list[
        sp.record(
            from_=sp.address,
            txs=sp.list[
                sp.record(to_=sp.address, amount=sp.nat, token_id=sp.nat).layout(
                    ("to_", ("token_id", "amount"))
                )
            ],
        ).layout(("from_", "txs")),
    ]

    # Transfer FA12 token entrypoint params type
    transfer_fa12_token_params_type: type = sp.record(
        token_address=sp.address,
        token_amount=sp.nat,
        from_address=sp.address,
        to_address=sp.address,
    )

    # FA12 token Transfer params type
    transfer_fa12_params_type: type = sp.record(
        from_=sp.address, to_=sp.address, value=sp.nat
    ).layout(("from_ as from", ("to_ as to", "value")))

    # Deposit entrypoint params type
    deposit_params_type: type = sp.record(farm_id=sp.nat, token_amount=sp.nat)
