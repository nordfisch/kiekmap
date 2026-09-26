"""Switching the device off -- the half of it a container can do.

The backend runs as uid 1000 in a container, with no docker socket, no sudo line and no host mount
beyond the data directory. It therefore cannot power the Pi off, and it should not be able to: the
privilege would belong to the whole admin area, which stands behind four digits. So it leaves a
note, and one root script on the host does the rest -- the same shape as the USB mounter, which
udev calls. See ``deploy/pi/kiekmap-shutdown`` and decisions.md, point 95.
"""

import logging

from app.config import Settings
from app.services.dates import utc_now

log = logging.getLogger(__name__)


def host_can_switch_off(settings: Settings) -> bool:
    """Is there anything on this host that acts on a request?

    ``setup-pi.sh`` writes the file; a development machine and the online instance have none.
    """
    return settings.shutdown_watcher_path.is_file()


def request_shutdown(settings: Settings) -> None:
    """Ask the host to power the device off.

    The timestamp is for whoever finds the file and for the journal. The script on the host judges
    by the file's own mtime, which needs no parser in a shell.
    """
    settings.shutdown_request_path.write_text(f"{utc_now().isoformat()}\n", encoding="utf-8")


def clear_stale_request(settings: Settings) -> None:
    """Throw away a request from before this start. Called once, while starting up.

    **Any marker that is already there belongs to nobody.** This process is the only writer, so it
    was either never acted on -- no watcher on this host -- or the power went between the request
    and the poweroff. Left lying, ``kiekmap-shutdown.path`` would switch the device off seconds
    after this boot. The script on the host guards the same case from its side.
    """
    try:
        settings.shutdown_request_path.unlink()
    except FileNotFoundError:
        return
    except OSError as error:
        log.warning("A shutdown request could not be cleared (%s)", error)
        return
    log.info("A shutdown request from before this start was cleared")
