# Linux Arctis Manager — Sidney's Fork

## Install on this machine

LAM is installed via the custom overlay `app-misc/linux-arctis-manager`
(`/var/db/repos/linux-arctis-manager`, which is a checkout of this fork's
`feature/arctis-7-support` branch).

```bash
sudo emerge app-misc/linux-arctis-manager
```

The systemd user service is shipped by the ebuild at
`/usr/lib/systemd/user/arctis-manager.service` and runs `/usr/bin/lam-daemon`.

Service management:
```bash
systemctl --user status arctis-manager
systemctl --user restart arctis-manager
journalctl --user -u arctis-manager -f
```

## Development workflow

This Projects clone is for editing source. To exercise changes on the system,
push them through the overlay:

1. Edit and commit in `~/Projects/Code/Linux-Arctis-Manager`
2. Push to the fork
3. `sudo emerge --sync linux-arctis-manager` then `sudo emerge app-misc/linux-arctis-manager`

For ebuild changes specifically, see
`~/.sysadmin/docs/configuration/overlay-management.md` — the Manifest must be
regenerated after every ebuild edit.

## Git remotes

- `origin` — upstream: https://github.com/elegos/Linux-Arctis-Manager
- `fork` — Sidney's fork: https://github.com/haysidney/Linux-Arctis-Manager
