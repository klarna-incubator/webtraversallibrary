"""
Helper code to check versions of installed dependencies.
"""

import logging
from subprocess import CalledProcessError, run

logger = logging.getLogger("wtl")


class VERSION_CMD:
    """Terminal strings for getting version info"""

    CHROME = "google-chrome --version"
    CHROMIUM = "chromium --version"
    CHROMEDRIVER = "chromedriver --version"
    FIREFOX = "firefox --version"
    GECKODRIVER = "geckodriver --version"


def run_cmd(cmd: str, title: str = None) -> bool:
    """Runs given command. Outputs data if descriptive title is given"""
    try:
        result = run(cmd.split(" "), check=True, capture_output=True)
        if title:
            logger.info(f"{title}: {str(result.stdout.decode('ascii').strip())}")
        return True
    except CalledProcessError:
        if title:
            logger.info(f"{title}: [FAILED]")

    return True  # TODO Temporary fix to avoid problems on Mac/Windows, should really return False
