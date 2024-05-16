import smartpy as sp  # type: ignore


@sp.module
def farming_types():
    administration_panel_type: type = sp.record(
        administrator=sp.address,
        pendingAdministrator=sp.option[sp.address],
        paused=sp.bool,
    )
