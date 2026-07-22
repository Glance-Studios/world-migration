#!/usr/bin/env python3
"""
transplant_inventories.py

Carry player inventories from an OLD Minecraft world into a FRESH world (e.g. a
1.21.11 -> 26.2 map reset) by transplanting each player's `playerdata/*.dat`.

WHAT IT DOES
------------
For every `<uuid>.dat` in the input folder, it strips the "where you are / current
physical state" tags (position, dimension, spawn point, motion, potion effects, ...)
while KEEPING inventory, ender chest, XP, held slot, gamemode and any mod-attached
player data. The result is written to a separate output folder.

It DELIBERATELY does not touch the `DataVersion` tag. That stamp is what tells the
new server's DataFixerUpper (DFU) which migrations to run, so vanilla items get
converted to the new format automatically when the 26.2 server boots. Modded items
pass through untouched and load fine as long as their mod is present with the same
item IDs.

WORKFLOW
--------
1. Download the OLD world's `playerdata/` off the server (a Modrinth backup is ideal;
   otherwise SFTP it with the server STOPPED). Keep the originals as your backup.
2. Run this script:  python transplant_inventories.py OLD_playerdata OUT_playerdata
   (add --dry-run first to preview).
3. Upload the OUT folder's files into the NEW 26.2 world's `playerdata/` (server
   stopped), then start the server. DFU migrates items on load; players spawn at the
   new world's spawn holding their old stuff.

Requires: pip install nbtlib
"""
import argparse
import sys
from pathlib import Path

try:
    import nbtlib
except ImportError:
    sys.exit("nbtlib is required:  pip install nbtlib")

# Tags that pin the player to the OLD world -> always removed so they spawn fresh.
LOCATION_TAGS = {
    "Pos", "Motion", "Rotation", "FallDistance", "OnGround",
    "Dimension",
    "SpawnX", "SpawnY", "SpawnZ", "SpawnAngle", "SpawnForced", "SpawnDimension",
    "respawn",                      # newer nested spawn-point format, if present
    "LastDeathLocation", "enteredNetherPosition",
    "SleepTimer", "Sleeping",
}
# Transient physical state -> reset to defaults on join.
TRANSIENT_TAGS = {
    "Fire", "Air", "HurtTime", "HurtByTimestamp", "DeathTime", "TicksFrozen",
    "active_effects", "ActiveEffects",   # potion effects (tag name varies by version)
}
# Optional resets (opt-in via flags).
XP_TAGS = {"XpLevel", "XpP", "XpTotal", "XpSeed"}
HEALTH_TAGS = {"Health", "foodLevel", "foodSaturationLevel",
               "foodExhaustionLevel", "foodTickTimer"}
GAMEMODE_TAGS = {"playerGameType", "previousPlayerGameType"}

# In --items-only mode we KEEP only these (everything else is dropped).
ITEMS_ONLY_KEEP = {"DataVersion", "Inventory", "EnderItems", "SelectedItemSlot"}


def process(root, args):
    """Mutate a loaded playerdata compound in place. Returns (kept_info, dropped)."""
    strip = set(LOCATION_TAGS) | set(TRANSIENT_TAGS)
    if args.reset_xp:
        strip |= XP_TAGS
    if args.reset_health:
        strip |= HEALTH_TAGS
    if args.reset_gamemode:
        strip |= GAMEMODE_TAGS

    if args.items_only:
        to_drop = [k for k in list(root.keys()) if k not in ITEMS_ONLY_KEEP]
    else:
        to_drop = [k for k in list(root.keys()) if k in strip]

    for k in to_drop:
        del root[k]

    inv = len(root.get("Inventory", []))
    ender = len(root.get("EnderItems", []))
    dv = int(root["DataVersion"]) if "DataVersion" in root else None
    return {"inv": inv, "ender": ender, "dataversion": dv}, to_drop


def main():
    p = argparse.ArgumentParser(
        description="Transplant player inventories into a fresh world (keeps items, "
                    "strips position). DataVersion is preserved so the new server's "
                    "DataFixerUpper migrates items on load.")
    p.add_argument("input", help="OLD world's playerdata/ folder (read-only source)")
    p.add_argument("output", help="folder to write transplanted .dat files into")
    p.add_argument("--dry-run", action="store_true",
                   help="report what would change; write nothing")
    p.add_argument("--items-only", action="store_true",
                   help="strict: keep ONLY inventory, ender chest, held slot, DataVersion")
    p.add_argument("--reset-xp", action="store_true", help="also wipe XP/levels")
    p.add_argument("--reset-health", action="store_true", help="also reset health/hunger")
    p.add_argument("--reset-gamemode", action="store_true",
                   help="also drop gamemode (use world default)")
    args = p.parse_args()

    src = Path(args.input)
    out = Path(args.output)
    if not src.is_dir():
        sys.exit(f"input folder not found: {src}")
    if out.resolve() == src.resolve():
        sys.exit("output must be a DIFFERENT folder than input (never edit originals)")
    if not args.dry_run:
        out.mkdir(parents=True, exist_ok=True)

    files = sorted(f for f in src.glob("*.dat") if not f.name.endswith(".dat_old"))
    if not files:
        sys.exit(f"no .dat files found in {src}")

    print(f"{'DRY-RUN: ' if args.dry_run else ''}processing {len(files)} player file(s) "
          f"from {src}\n")

    total_items = warnings = ok = 0
    for f in files:
        try:
            root = nbtlib.load(str(f))
        except Exception as e:  # one bad file shouldn't abort the batch
            print(f"  !! {f.name}: FAILED to read ({e})")
            warnings += 1
            continue

        if "Inventory" not in root and "DataVersion" not in root:
            print(f"  !! {f.name}: doesn't look like playerdata (no Inventory/DataVersion) - skipped")
            warnings += 1
            continue

        info, dropped = process(root, args)
        total_items += info["inv"] + info["ender"]

        dv = info["dataversion"]
        flag = ""
        if dv is None:
            flag = "  <-- WARNING: no DataVersion! DFU will NOT run; do NOT upload this file"
            warnings += 1

        print(f"  {f.name}")
        print(f"      inventory={info['inv']} items  enderchest={info['ender']} items  "
              f"DataVersion={dv}{flag}")
        print(f"      dropped: {', '.join(dropped) if dropped else '(nothing)'}")

        if not args.dry_run:
            root.save(str(out / f.name), gzipped=True)
            ok += 1

    print()
    print(f"Summary: {len(files)} file(s), {total_items} item stacks kept, "
          f"{warnings} warning(s).")
    if args.dry_run:
        print("Dry run - nothing written. Re-run without --dry-run to write to:", out)
    else:
        print(f"Wrote {ok} file(s) to {out}")
        print("Next: upload these into the NEW 26.2 world's playerdata/ (server stopped), "
              "then boot - DFU migrates items on load.")


if __name__ == "__main__":
    main()
