#!/usr/bin/python3
# https://medium.com/@prateekrm/earn-500-daily-microsoft-rewards-points-automatically-with-a-simple-python-program-38fe648ff2a9
# https://stackoverflow.com/questions/49565042/way-to-change-google-chrome-user-agent-in-selenium

import os
import time
from BingSearchRewards.BasicSearch import BasicSearch
#import .BasicSearch
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from inspect import currentframe, getframeinfo


# This class uses the Chrome Selenium Driver with the Edge User-Agent string to perform
# a series of searches using distinct, random words so the searches count toward daily quotas
class EdgeBatch(BasicSearch):
    def __init__(self, driver_path, useragent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) " +
                                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 " +
                                              "Safari/537.36 Edg/89.0.774.75"):
        super().__init__()
        print("Executing {0}".format(__file__))
        self.EdgeUserAgent = useragent
        options = Options()
        options.add_argument("user-agent=" + self.EdgeUserAgent)
        # options.add_argument("--headless")
        self.driver_path = driver_path
        # self.edge_driver = webdriver.Edge(self.driver_path)
        self.edge_driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
        print("Executing {0}".format(__file__))

    def bing_daily(self, userid, passwd, search_count):
        super().bing_daily(self.edge_driver, userid, passwd, search_count)

    def quit(self):
        super().quit(self.edge_driver)


if __name__ == "__main__":
    engine = EdgeBatch(os.path.expandvars("$HOMEDRIVE/$HOMEPATH/Downloads/edgedriver_win64/msedgedriver.exe"))
    try:
        time.sleep(5)
        engine.bing_daily("user@hotmail.com", "password")
    except Exception as e:
        frame_info = getframeinfo(currentframe())
        print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
        time.sleep(5)
    engine.quit()
