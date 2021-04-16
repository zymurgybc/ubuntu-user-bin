#!/usr/bin/env python3
# https://medium.com/@prateekrm/earn-500-daily-microsoft-rewards-points-automatically-with-a-simple-python-program-38fe648ff2a9

import os
import time
from inspect import currentframe, getframeinfo
from BingSearchRewards.common import *

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


# This class uses the PyQT toolchain to perform a series of searches while
# claiming to be a mobile browser using distinct, random words so the searches 
# count toward daily quotas
class MobileBatch:

    def __init__(self, driver_path, useragent="Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) " +
                                              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 " +
                                              "Mobile Safari/537.36"):
        print("Executing {0}".format(__file__))
        self.userAgent = useragent
        options = Options()
        options.add_argument("user-agent=" + self.userAgent)
        # options.add_argument("--headless")
        self.driver_path = driver_path
        # self.edge_driver = webdriver.Edge(self.driver_path)
        self.edge_driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
        print("Executing {0}".format(__file__))

    def check_points(self, userid, tag_string):
        try:
            # Maximize current window
            self.edge_driver.maximize_window()
            self.edge_driver.get("https://account.microsoft.com/rewards/")
            time.sleep(8)
            elements = self.edge_driver.find_elements(By.XPATH, "//span[@class='x-hidden-focus']")
            if len(elements) > 0:
                points = elements[0].text
                print('{0} {1} points for {2}'.format(tag_string, points, userid))
        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(4)

    # This simply looks for the option to "Log in" rather than "Log Out"
    # using the rewards page since its where we need the login/out to happen
    def is_logged_in(self):
        try:
            self.edge_driver.get("https://account.microsoft.com/rewards/")
            time.sleep(5)
            elem = self.edge_driver.find_elements_by_css_selector("div.mectrl_root span.mectrl_screen_reader_text")
            return len(elem) < 1 or elem[0].text != "Sign in to your account"

        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(4)

        return True  # default is to assume an account is still logged in

    def _log_me_out_Rewards(self):
        try:
            # Logging out on the live page doesn't reliably log you out of rewards
            # so we'll go there and logout first
            self.edge_driver.get("https://account.microsoft.com/rewards/")
            time.sleep(5)

            # when this is found, an account is already logged in
            # notably, it throws an exception when not found, not none
            elem = self.edge_driver.find_element_by_id('mectrl_headerPicture')
            if elem is not None:
                elem.click()
                time.sleep(2)
                elem = self.edge_driver.find_element_by_id('mectrl_body_signOut')
                if elem is not None:
                    elem.click()
                    time.sleep(5)
            # Try and reload the page
        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(4)

    def _log_me_out_Bing(self):
        # Yet another page we need to be logged out from before starting
        # since it caches credentials on its own
        try:
            self.edge_driver.get("http://www.bing.com/search?q=")
            time.sleep(5)

            # when this is found, an account is already/still logged in
            # notably, it throws an exception when not found, not none
            elem = self.edge_driver.find_element_by_id('mectrl_headerPicture')
            if elem is not None:
                elem.click()
                time.sleep(2)
                elem = self.edge_driver.find_element_by_id('mectrl_body_signOut')
                if elem is not None:
                    elem.click()
                    time.sleep(4)
            # Try and reload the page
        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(4)

    def _log_me_out_Live(self):
        try:
            self.edge_driver.get("https://login.live.com")
            time.sleep(5)

            # when this is found, an account is already/still logged in
            # notably, it throws an exception when not found, not none
            elem = self.edge_driver.find_element_by_id('mectrl_headerPicture')
            if elem is not None:
                elem.click()
                time.sleep(2)
                elem = self.edge_driver.find_element_by_id('mectrl_body_signOut')
                if elem is not None:
                    elem.click()
                    time.sleep(4)
            # Try and reload the page
        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(4)

    # This is an exercise to click the right to controls to logout
    # both the rewards page and the live account
    def logout(self):
        self._log_me_out_Rewards()
        self._log_me_out_Bing()
        self._log_me_out_Live()

    def login_to_live(self, driver, userid, passwd):
        if self.is_logged_in():
            self.logout()

        try:
            driver.get("https://login.live.com")
            time.sleep(5)

            elem = driver.find_element_by_name('loginfmt')
            elem.clear()
            elem.send_keys(userid)  # add your login email id
            elem.send_keys(Keys.RETURN)
            time.sleep(5)
            elem1 = driver.find_element_by_name('passwd')
            elem1.clear()
            elem1.send_keys(passwd)  # add your password
            elem1.send_keys(Keys.ENTER)
            time.sleep(7)
        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(4)

    def do_search_list(self, word_count):
        words_list = get_word_list(count=word_count)

        url_base = 'http://www.bing.com/search?q='
        time.sleep(3)

        # Look for the "your account" anchor and see if it has an name associated
        # and click the anchor if its not there to round-trip the login info
        try:
            self.edge_driver.get(url_base)
            anchor = self.edge_driver.find_elements_by_css_selector("a#id_l")
            # if this element is not found, it shows the page isn't currently logged in
            # or it may not be displayed which also means you're not logged in
            # elem = self.edge_driver.find_elements_by_css_selector("a#id_l span#id_n")
            # if elem is not None and len(elem) >0:
            # if not elem[0].is_displayed():
            #    anchor[0].click()
            # anchor[0].click()
        except Exception as e3:
            frame_info3 = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info3.filename, frame_info3.lineno, e3))
            time.sleep(5)

        try:
            for num, word in enumerate(words_list):
                print('{0}. URL : {1}'.format(str(num + 1), url_base + word))
                try:
                    self.edge_driver.get(url_base + word)
                    print('\t' + self.edge_driver.find_element_by_tag_name('h2').text)
                    time.sleep(5)
                except Exception as e1:
                    frame_info1 = getframeinfo(currentframe())
                    print("Exception in {0}:{1} -- {2}".format(frame_info1.filename, frame_info1.lineno, e1))
                    time.sleep(5)
        except Exception as e2:
            frame_info2 = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info2.filename, frame_info2.lineno, e2))
            time.sleep(5)

    def bing_daily(self, userid, passwd, search_count):
        self.login_to_live(self.edge_driver, userid, passwd)
        self.check_points(userid, "Starting")
        self.do_search_list(search_count)
        time.sleep(10)
        self.check_points(userid, "Finished")

    def quit(self):
        self.edge_driver.quit()


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
