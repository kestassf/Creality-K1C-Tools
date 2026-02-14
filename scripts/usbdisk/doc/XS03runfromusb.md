> [!CAUTION]
> Do a proper testing before applying to a live K1C-2025.

# Prapare USB

Partiton and format USB
* /dev/sda1 - vfat
* /dev/sda2 - ext4 for deplibs
* /dev/sda3 - ext4 for apps
* /dev/sda4 - ext4 for data

Mount `sda1` create `init.d` and copy `XS03runfromusb` to `./init.d/XS03runfromusb`

Mount `sda2,3,4` and copy content of squashfs and ext4 partitions there (either use OTA-Parser,
MMC dump, or live filesystem as a source):
* squashfs -> `sda2/`
* rootfs2 -> `sda3/`
* userdata -> `sda4/`

NOTE: Creality binaries have hardcoded path `/media/sreality` so missbehave if there are active
partitions mounted there (`nexusp` is trying to index files, load goes up.). 

Adjust as You see fit.

Advised to copy `S04harden` to `sda2/etc/init.d` for extra safety.

Initially `init.d/CS*` scripts should be moved out to prevent their startup, so You can check manually and enable
once everything is ok.

The script:
- removes `/dev/sd*` related configuration from `mdev` to prevent in interfering later.
- mounts `sda2` ext4 partition
- replaces MMC partitions mounts with bind-mount from sda2 (unmounts MMC, bind-mounts folders)
- halts the system if there is still any MMC partition mounted (extra safety measyre)
- runs `/usr/apps/etc/init.d/U*` scripts

The script intentionally does not start `creality` services from `/usr/apps/etc/init.d/CS*`.

# Prepare MMC

Highly advised to have `S00unlock` working properly.

The script requires `S02usbscripts` to be run from `/tmp` (handled by `/usr/appsw/etc/init.d/S01release_rootfs2`
and symlink `/usr/apps/etc/init.d/S02usbscripts`). Othervise `/usr/apps` is used by script itself and unmounting fails.

`/bin/seed.sh` expands the list `/usr/apps/etc/init.d/S*` before remounting is done, so if lists in MMC and USB `init.d`
are different, only names which were present in MMC will be run by `seed.sh` authomatically.

# Expectet result

When this USB is attached printer should start with relatively safe environment without any MMC partition mounted.
It is still possible to brick the system!!!
