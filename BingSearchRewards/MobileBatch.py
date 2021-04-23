#!/usr/bin/env python3
# https://medium.com/@prateekrm/earn-500-daily-microsoft-rewards-points-automatically-with-a-simple-python-program-38fe648ff2a9

import os
import time
from inspect import currentframe, getframeinfo

from BingSearchRewards.BasicSearch import BasicSearch

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


class MobileBatch(BasicSearch):

    def __init__(self, driver_path, useragent="Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) " +
                                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 " +
                                              "Mobile Safari/537.36"):
        super().__init__()
        print("Executing {0}".format(__file__))
        self.userAgent = useragent
        options = Options()
        options.add_argument("user-agent=" + self.userAgent)
        # options.add_argument("--headless")
        self.driver_path = driver_path
        self.chrome_driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
        print("Executing {0}".format(__file__))

    def bing_daily(self, userid, passwd, search_count):
        super().bing_daily(self.chrome_driver, userid, passwd, search_count)

    def quit(self):
        super().quit(self.chrome_driver)


if __name__ == "__main__":
    try:
        # engine = MobileBatch(os.path.expandvars("$HOMEDRIVE/$HOMEPATH/Downloads/edgedriver_win64/msedgedriver.exe"))
        engine = MobileBatch("F:/Downloads/Google Chrome/chromedriver_win32/chromedriver.exe")
        time.sleep(5)
        engine.BingDaily("user@hotmail.com", "password", 40)
    except Exception as e1:
        frame_info = getframeinfo(currentframe())
        print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e1))
        time.sleep(5)
    engine.quit()
