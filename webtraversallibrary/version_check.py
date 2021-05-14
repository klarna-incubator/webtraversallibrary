"""
Helper code to check versions of installed dependencies.
"""

import logging
from subprocess import CalledProcessError, run

logger = logging.getLogger("wtl")


class _VERSION_CMD:
    """Terminal strings for getting version info"""

    @staticmethod
    def deprecated_warning():
        logger.warning(
            "VERSION_CMD is deprecated and will be removed in a future version."
            "Please use the SystemCheck class instead."
        )

    @property
    def CHROME(self) -> str:
        """
        Returns a Linux like command for getting the version of Google Chrome.
        """
        _VERSION_CMD.deprecated_warning()
        return "google-chrome --version"

    @property
    def CHROMIUM(self) -> str:
        """
        Returns a Linux like command for getting the version of Chromium.
        """
        _VERSION_CMD.deprecated_warning()
        return "chromium --version"

    @property
    def CHROMEDRIVER(self) -> str:
        """
        Returns a Linux like command for getting the version of Chromedriver.
        """
        _VERSION_CMD.deprecated_warning()
        return "chromedriver --version"

    @property
    def FIREFOX(self) -> str:
        """
        Returns a Linux like command for getting the version of Firefox.
        """
        _VERSION_CMD.deprecated_warning()
        return "firefox --version"

    @property
    def GECKODRIVER(self) -> str:
        """
        Returns a Linux like command for getting the version of Geckodriver.
        """
        _VERSION_CMD.deprecated_warning()
        return "geckodriver --version"


# Hack right now to preserve the attributes to the class but have them as callable properties
VERSION_CMD = _VERSION_CMD()


def run_cmd(cmd: str, title: str = None) -> bool:
    """Runs given command. Outputs data if descriptive title is given"""
    logger.warning(
        "version_check.run_cmd() is deprecated and will be removed in a future version."
        "Please use the system_check.get_cmd_output() function instead."
    )
    try:
        result = run(cmd.split(" "), check=True, capture_output=True)
        if title:
            logger.info(f"{title}: {str(result.stdout.decode('ascii').strip())}")
        return True
    except CalledProcessError:
        if title:
            logger.info(f"{title}: [FAILED]")

    return True  # TODO Temporary fix to avoid problems on Mac/Windows, should really return False
