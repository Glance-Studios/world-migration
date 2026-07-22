# How to carry player inventories into the new 26.2 world

This tool moves everyone's **items** from the old world into the brand-new 26.2 map,
so a fresh world doesn't wipe people's stuff. Each player spawns fresh at the new
spawn but keeps their **inventory, ender chest, and XP**.

You only need the file **`transplant_inventories.exe`** - no Python, no install.

---

## What's actually happening (plain English)

Your old world has a folder called `playerdata` - one file per player that holds
their inventory. You'll:

1. Download that folder to your PC,
2. Run the tool on it (it keeps items but forgets *where* each player was standing),
3. Put the results into the **new** world.

Minecraft itself upgrades the item data to 26.2 automatically the first time the new
server starts. You don't have to do anything special for that.

---

## Before you start

- The **new 26.2 world must already exist** on the server, with **all the mods
  installed**.
- **Stop the server** any time you download or upload world files, so nothing is
  saved half-way.

---

## Step 1 - Get the old `playerdata` folder onto your PC

In the **Modrinth server panel**:

- Open the **Backups** tab -> create a backup -> **Download** it. Unzip it on your PC.
  *(This backup is also your safety net - keep it.)*
- **or** open **Files** -> `world` -> `playerdata` -> download that folder.

You should now have a folder on your PC full of files named like
`f81d4fae-7dec-11d0-a765-00a0c91e6bf6.dat`. Example location:
`C:\Users\You\Downloads\playerdata`

## Step 2 - Put the tool somewhere simple

Copy **`transplant_inventories.exe`** into an easy folder, for example:
`C:\invtool\`

## Step 3 - Open a terminal in that folder

Open `C:\invtool\` in File Explorer. **Hold Shift and right-click** an empty spot in
the window, then choose **"Open PowerShell window here"** (or "Open in Terminal").
A text window opens.

## Step 4 - Preview first (this changes nothing)

Type the command below. **Tip:** instead of typing the long folder paths, just
**drag the folder from File Explorer into the terminal window** - it pastes the path
for you.

```
.\transplant_inventories.exe "C:\Users\You\Downloads\playerdata" "C:\invtool\out" --dry-run
```

Press **Enter**. It lists each player, how many items they have, and what it will
strip. **Nothing is written yet.** Check the item counts look reasonable.

> If Windows shows **"Windows protected your PC"**, click **More info -> Run anyway**.
> That warning only appears because the tool isn't code-signed; it's safe.

## Step 5 - Run it for real

Same command, but **remove** `--dry-run`:

```
.\transplant_inventories.exe "C:\Users\You\Downloads\playerdata" "C:\invtool\out"
```

This fills `C:\invtool\out` with the processed files. Your original download is left
untouched.

## Step 6 - Test ONE player first (important!)

1. On the server, upload **just one** file from `out` into the new world's
   `world\playerdata\` folder.
2. Start the server, have that player log in, and check their inventory - especially
   any **modded** items.
3. If it looks right, continue. If something's wrong, stop and ask before doing everyone.

## Step 7 - Upload everyone

1. **Stop the server.**
2. Upload **all** files from `C:\invtool\out` into the new world's `world\playerdata\`.
3. **Start the server.** Everyone joins at the new spawn holding their old inventory,
   ender chest, and XP.

---

## Options (advanced, optional)

Add these to the end of the command if you want:

| Option | Effect |
|---|---|
| `--dry-run` | Preview only, write nothing (use this first). |
| `--items-only` | Keep **only** inventory + ender chest (drop XP, effects, mod data). |
| `--reset-xp` | Also wipe XP / levels. |
| `--reset-health` | Also reset health and hunger. |
| `--reset-gamemode` | Reset gamemode to the world default. |

Default (no options): keeps inventory + ender chest + XP + held slot + gamemode, and
strips position / dimension / spawn point / potion effects.

---

## The 3 golden rules

1. **Keep the backup** you downloaded - it's your undo button.
2. **Always run `--dry-run` first**, and **test one player** before the whole server.
3. An item only survives if **its mod is installed on 26.2 with the same item ID**.
   (You've confirmed every item mod is on 26.2, so you're covered.)
