"""get source page, need define source_page(), quit()"""
import os
from signal import SIGTERM
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.firefox.options import Options


class Webdriver(object):
    """webdriver for scraw js dynamic content."""

    def __init__(self):
        """construct a firefox webdriver"""

        # define profiles
        firefoxProfile = webdriver.FirefoxProfile()
        firefoxProfile.set_preference('permissions.default.stylesheet', 2)
        firefoxProfile.set_preference('permissions.default.image', 2)
        firefoxProfile.set_preference('javascript.enabled', True)
        firefoxProfile.set_preference(
            'dom.ipc.plugins.enabled.libflashplayer.so', 'false')
        # define options
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--safe-mode")
        # maybe you need upgrade your geckodriver to version 2.0
        self.driver = webdriver.Firefox(
            firefox_profile=firefoxProfile,
            firefox_options=options,
            executable_path="/usr/bin/geckodriver",
            log_path=os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "sentence.log"))
        # set page load timeout, script will slower when the number is larger
        self.driver.set_page_load_timeout(3)

    def source_page(self, word):
        """after loading js, get the complete source page of the word."""
        URL = "http://www.iciba.com/" + word
        try:
            self.driver.get(URL)
        except TimeoutException:
            pass
        except:
            return None
        try:
            # sometimes it will return WebDriverException.
            self.driver.page_source
        except WebDriverException:
            self.driver.page_source = ""
        return self.driver.page_source

    def quit(self):
        """quit the webdriver, more safer."""
        self.driver.service.process.send_signal(SIGTERM)
        self.driver.quit()


if __name__ == "__main__":
    wd = Webdriver()
    wd.quit()
