> [!CAUTION]
> Do a proper testing before applying to a live K1C-2025.

# Prapare USB

Partiton and format USB
* /dev/sda1 - vfat
* /dev/sda2 - ext4

Mount `sda1` create `init.d` and copy `XS03runfromusb` to `./init.d/XS03runfromusb`

Mount `sda2` and copy content of squashfs and ext4 partitions there (either use OTA-Parser,
MMC dump, or live filesystem as a source):
* squashfs -> `deplibs`
* rootfs2 -> apps
* userdata -> data

You should get the following filesystem:

```
[root@ /mnt/sda2] # find . -maxdepth 2
.
./deplibs
./deplibs/lib
./deplibs/html
./deplibs/edl-v10
./deplibs/CONTRIBUTING.md
./deplibs/etc
./deplibs/bin
./deplibs/lib32
./deplibs/epl-v10
./deplibs/sbin
./deplibs/libexec
./deplibs/notice.html
./deplibs/README.md
./deplibs/share
./deplibs/LICENSE
./apps
./apps/usr
./apps/lib
./apps/var
./apps/etc
./apps/tmp
./apps/module_driver
./apps/lost+found
./data
./data/core
./data/wpa_supplicant.conf
./data/macaddr.txt
./data/owner
./data/old
./data/printer_data
./data/creality
./lost+found
```

Adjust as You see fit.

Advised to copy `S04harden` to `sda2/etc/init.d` for extra safety.

The script:
- removes `/dev/sd*` related configuration from `mdev` to prevent in interfering later.
- mounts `sda2` ext4 partition
- replaces MMC partitions mounts with bind-mount from sda2 (unmounts MMC, bind-mounts folders)
- halts the system if there is still any MMC partition mounted (extra safety measyre)
- runs `/usr/apps/etc/init.d/S*` scripts

The script intentionally does not start `creality` services from `/usr/apps/etc/init.d/CS*`.

# Prepare MMC

Highly advised to have `S00unlock` working properly.

The script requires `S02usbscripts` to be run from `/tmp` (handled by `/usr/appsw/etc/init.d/S01release_rootfs2`
and symlink `/usr/appsw/etc/init.d/S02usbscripts). Othervise `/usr/apps` is used by script itself and unmounting fails.

Any scripts on MMC after `S02usbscripts` are not started, even if the same named files are present on USB (TODO: why?).

# Expectet result

When this USB is attached printer should start with relatively safe environment without any MMC partition mounted.
It is still possible to brick the system!!!
