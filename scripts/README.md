# Modifications to V1.0.0.26 firmware

> [!CAUTION]
> Do a proper testing before applying to a live K1C-2025

## Backgreound

The path Creality has took with removal of root access, implementation of "secure boot",
false advertisements ("DIY friendly", "OpenSource" in https://store.creality.com/eu/),
excessive telemetry (without proper authorization) I see as hostile activity to it's user base.
This makes Creality an untrusted vendor.

This is a documentation of my attempts to make K1C-2025 firmware DIY-friendly and reasonably safe to modify.

If You see risks I've missed - please leave comments.

## Setup

* K1C-2025_V1.0.0.26 firmware installed
  * (`MD5(CR4SU200382C13_ota_K1C-2025_V1.0.0.26.20251024S.img)= b4306fe87d75ad94525fb73b4905a52e`)
* internet access blocked (potential side channels like DNS also blocked)
* CrealityPrint has any access to network blocked (local and internet), OrcaSlicer ir working
* working root via SSH over WiFi (root exploit successfuly applied)
* working serial connection

## Modifications

Idea: get a shell prompt on boot as early as possibble. `/usr/apps/etc/init.d/S*` scripts is the first
location suitable for modification.

* [`S00unlock`](rootfs2/etc/init.d/S00unlock) - unlock `root` and `creality` accounts, reset password to a known value.
* [`S01usbscripts`](rootfs2/etc/init.d/S01usbscripts) - run scripts from USB, if it is present on boot.
* [`S02testusr`](rootfs2/etc/init.d/S02testusr) - create one more unprivileged user with a known password.
* [`S80persistence`](rootfs2/etc/init.d/S80persistence) - slightly modified root-exploit's script to prevent server
ssh key changeing on every boot.
* [`S90custom`](rootfs2/etc/init.d/S90custom) - any remaining changes (make system more resistant to changes by
untrusted users, install fake SSL CA).

In case of trouble (as long as boot successfuly gets to `S00unlock` and `S01usbscripts`) You can put extra scripts to
USB disk, attach it and get them executed by `S01usbscripts`. Sample scripts:

* [`XS02break`](usbdisk/init.d/XS02break) - stop boot, allow login as `root` or `creality` login.
* [`XS03runfromusb`](usbdisk/init.d/XS03runfromusb) - unmount MMC partitions and run from USB, [more info](usbdisk/doc/XS03runfromusb.md)
