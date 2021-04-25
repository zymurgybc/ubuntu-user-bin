#!/usr/bin/env python3

import time
from tendo import singleton
me = singleton.SingleInstance()  # will sys.exit(-1) if other instance is running

from sys import platform
# from BingSearchRewards.common import *
from BingSearchRewards.EdgeBatch import EdgeBatch
from BingSearchRewards.MobileBatch import MobileBatch
from inspect import currentframe, getframeinfo


class Daily:
    def __init__(self):
        pass

    def bing_daily(self, userid, passwd):
        # Use a new infrastructure for each pass so the session is cleaned up
        # because the selenium driver discards all session data
        # (aka. private mode browsing)
        if platform == "win32":
            # be sure to use '/' rather than '\\'
            self.driver_path = "F:/Downloads/Google Chrome/chromedriver_win32/chromedriver.exe"
        elif platform == "linux" or platform == "linux2":
            self.driver_path = "/usr/bin/chromedriver"

        try:
            self.edge = EdgeBatch(driver_path=self.driver_path)
            self.edge.bing_daily(userid, passwd, 40)
        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(2)
        if self.edge != None:
            self.edge.quit()

        try:
            self.mobile = MobileBatch(driver_path=self.driver_path)
            self.mobile.bing_daily(userid, passwd, 40)
        except Exception as e2:
            print(e2)
            time.sleep(2)
        if self.mobile != None:
            self.mobile.quit()

    def quit(self):
        pass


if __name__ == "__main__":

    engine = Daily()

    try:
        engine.bing_daily("ted_250@hotmail.com", "Quantico2014")
        pass
    except Exception as e1:
        print(e1)
        time.sleep(2)

    try:
        engine.bing_daily("ted_604@hotmail.com", "Quesnel2018")
        pass
    except Exception as e1:
        print(e1)
        time.sleep(2)

    try:
        engine.bing_daily("ted.heatherington@outlook.com", "Qualicum2017")
        pass
    except Exception as e1:
        print(e1)
        time.sleep(2)
