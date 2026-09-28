# World migration - carry inventories into the fresh 26.2 map

Transplants each player's inventory (and ender chest, XP, etc.) from the OLD
1.21.11 world into a brand-new 26.2 world, so a map reset doesn't wipe everyone's
stuff. Vanilla items are format-migrated automatically by the server's
DataFixerUpper on boot; modded items carry over as long as their mod is present on
26.2 with the same item IDs.

## Two ways to run it
- **Python script** - `transplant_inventories.py` (needs Python 3.8+ and `pip install nbtlib`).
- **Standalone exe (no Python needed)** - built with PyInstaller into `dist/`, which is not
  tracked here. Give the exe to whoever has the backup; it runs on Windows with nothing installed,
  and takes the same arguments as the script (drop the `python transplant_inventories.py`).
  `HOW-TO.md` is written for that audience.

## Prerequisites
- Every item-adding mod ported to 26.2 with unchanged item IDs (confirmed).
- A fresh 26.2 world already generated on the server, with the full modset.

## Steps (Modrinth-hosted server)

1. **Get the OLD world off the server.** Easiest + safest: make a **Backup** in the
   Modrinth panel and download it (it's your safety net too). Or SFTP the world
   folder with the **server stopped**. You need `world/playerdata/` (optionally also
   `stats/` and `advancements/` if you want those carried too).

2. **Run the transplant locally** on the downloaded copy:
   ```
   python transplant_inventories.py  <OLD>/playerdata  ./out  --dry-run
   ```
   Review the report, then drop `--dry-run` to actually write `./out`.

3. **Upload** every file from `./out` into the **new 26.2 world's `playerdata/`**
   (server stopped). Then start the server. On load, DataFixerUpper migrates each
   file; players spawn at the new world's spawn holding their old inventory.

4. **Test first.** Before doing it for real, try one or two profiles (ideally ones
   holding modded items) on a copy of the new world and confirm the items look right.

## Options
- (default) keep inventory + ender chest + XP + held slot + gamemode + mod data;
  strip position/dimension/spawn/motion/effects.
- `--items-only`  keep ONLY inventory, ender chest, held slot (drop XP/mod data/etc.)
- `--reset-xp` / `--reset-health` / `--reset-gamemode`  reset those too.
- `--dry-run`  preview without writing.

## Safety notes
- The script **never edits the source** - it only writes to the output folder.
- It **never changes `DataVersion`** - that stamp is what makes the server's
  DataFixerUpper migrate items to the 26.2 format. Don't upload a file that the
  report flags as missing `DataVersion`.
- Always pull from a **stopped server or a backup** so files aren't mid-write.
- An item only survives if its mod is loaded on 26.2 with the **same item ID**. A
  mod that renamed an item, or wasn't ported, loses that item.
