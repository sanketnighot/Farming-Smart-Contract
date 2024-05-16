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
        start_time=sp.timestamp,
        end_time=sp.timestamp,
        lock_duration=sp.int,
        bonuses=sp.set[sp.record(end_time=sp.timestamp, multipier=sp.nat)],
        owner=sp.address,
    )

    # Ledger bigmap key type
    ledger_key_type: type = sp.pair[sp.nat, sp.address]

    # Ledger bigmap value type
    ledger_value_type: type = sp.record(
        amount=sp.nat, reward_debt=sp.nat, lock_end_time=sp.timestamp
    )
