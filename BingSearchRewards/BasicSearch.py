#!/usr/bin/env python3

import requests
import random
import json
import time
from inspect import currentframe, getframeinfo

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class BasicSearch:
    def __init__(self):
        print("Executing {0}".format(__file__))
        pass

    def click_first_elem(self, elem, pause):
        if elem is None:
            return False  # no reference value
        else:
            if hasattr(elem, "__iter__"):
                if len(elem) < 1:
                    return False  # Empty collection
                else:
                    elem[0].click()
            else:
                elem.click()
            time.sleep(pause)
        return True   # something was clicked on

    # This simply looks for the option to "Log in" rather than "Log Out"
    # using the rewards page since its where we need the login/out to happen
    def is_logged_in(self, driver):
        try:
            driver.get("https://account.microsoft.com/rewards/")
            time.sleep(5)
            elem = driver.find_elements_by_css_selector("div.mectrl_root span.mectrl_screen_reader_text")
            return len(elem) < 1 or elem[0].text != "Sign in to your account"

        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(4)

    def get_word_list(self, count: int):
        random_lists_url = "https://www.randomlists.com/data/words.json"
        response = requests.get(random_lists_url)
        words_list = random.sample(json.loads(response.text)['data'], count)
        print('{0} words selected from {1}'.format(len(words_list), random_lists_url))
        return words_list

    def create_file(self, file_name, content):
        text_file = open(file_name, "w")
        text_file.write(content)
        text_file.close()

    # This is an exercise to click the right to controls to logout
    # from each of bing.com, the rewards page and the live account
    def logout(self, driver):
        self.log_me_out_everywhere(driver)

    def log_me_out_everywhere(self, driver):
        self.log_me_out_MS(driver, "https://account.microsoft.com/rewards/")
        self.log_me_out_MS(driver, "http://www.bing.com/search?q=")
        self.log_me_out_MS(driver, "https://login.live.com")
        driver.get("chrome://settings/clearBrowserData")
        time.sleep(3)
        btn = driver.find_elements_by_css_selector("#clearBrowsingDataConfirm")
        self.click_first_elem(btn, 2)


    def log_me_out_MS(self, driver, url):
        try:
            driver.get(url)
            time.sleep(5)

            # when this is found, an account is already/still logged in
            # notably, it throws an exception when not found, not none
            elem = driver.find_elements_by_css_selector('mectrl_headerPicture')
            if self.click_first_elem(elem, 2):
                elem = driver.find_elements_by_css_selector('mectrl_body_signOut')
                self.click_first_elem(elem, 2)
            # Try and reload the page
        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(4)

        # The Bing Search page doesn't use the same format as most Microsoft headers
        try:
            elem = driver.find_elements_by_css_selector('#id_l')
            if self.click_first_elem(elem, 2):
                elem = driver.find_elements_by_css_selector('#b_idProviders > li > a > span.id_link_text')
                self.click_first_elem(elem, 2)
        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(4)

    def login_to_live(self, driver, userid, passwd):
        if self.is_logged_in(driver):
            self.logout(driver)

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

    def ensure_loggedin(self, driver, url_base):

        # Look for the "your account" anchor and see if it has an name associated
        # and click the anchor if its not there to round-trip the login info
        try:
            driver.get(url_base)
            anchor = self.edge_driver.find_elements_by_css_selector("a#id_l")
            # if this element is not found, it shows the page isn't currently logged in
            # or it may not be displayed which also means you're not logged in
            # elem = self.edge_driver.find_elements_by_css_selector("a#id_l span#id_n")
            # if elem is not None and len(elem) >0:
            # if not elem[0].is_displayed():
            #    anchor[0].click()
            self.click_first_elem(anchor, 2)
        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(5)

    # This simply looks for the option to "Log in" rather than "Log Out"
    # using the rewards page since its where we need the login/out to happen
    def is_logged_in(self, driver):
        try:
            driver.get("https://account.microsoft.com/rewards/")
            time.sleep(5)
            elem = driver.find_elements_by_css_selector("div.mectrl_root span.mectrl_screen_reader_text")
            if elem is not None:
                if hasattr(elem, "__iter__"):
                    if len(elem) > 0:
                        return elem[0].text != "Sign in to your account"
                else:
                    return elem.text != "Sign in to your account"

        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(4)

        return True  # default is to assume an account is still logged in

    def check_points(self, driver, userid, tag_string):
        try:
            # Maximize current window
            driver.maximize_window()
            driver.get("https://account.microsoft.com/rewards/")
            time.sleep(8)
            elements = driver.find_elements(By.XPATH, "//span[@class='x-hidden-focus']")
            if len(elements) > 0:
                points = elements[0].text
                print('{0} {1} points for {2}'.format(tag_string, points, userid))
        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(4)

    def earn_rewards(self, driver):

        url_base = 'https://account.microsoft.com/rewards/'
        self.ensure_loggedin(url_base)
        try:
            elements = driver.find_element_by_css_selector("span.mee-icon-AddMedium[aria-label='plus']")
            if elements is not None:
                if hasattr(elements, '__iter__'):
                    if len(elements)>0:
                        for el in elements:
                            pass
                else:
                    pass
        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(5)

    def do_search_list(self, driver, word_count):
        words_list = self.get_word_list(count=word_count)

        url_base = 'http://www.bing.com/search?q='
        time.sleep(3)

        # Look for the "your account" anchor and see if it has an name associated
        # and click the anchor if its not there to round-trip the login info
        try:
            driver.get(url_base)
            anchor = driver.find_elements_by_css_selector("a#id_l")
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

        # Look for the "your account" anchor and see if it has an name associated
        # and click the anchor if its not there to round-trip the login info
        try:
            anchor = driver.find_elements_by_css_selector("#hb_s")
            # if this element is not found, it shows the page isn't currently logged in
            # or it may not be displayed which also means you're not logged in
            if anchor is not None:
                if hasattr(anchor, "__iter__"):
                    if len(anchor) > 0:
                        anchor[0].click()
                else:
                    anchor.click()
        except Exception as e3:
            frame_info3 = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info3.filename, frame_info3.lineno, e3))
            time.sleep(5)

        try:
           for num, word in enumerate(words_list):
                print('{0}. URL : {1}'.format(str(num + 1), url_base + word))
                try:
                    driver.get(url_base + word)
                    print('\t' + driver.find_element_by_tag_name('h2').text)
                    time.sleep(3)
                except Exception as e1:
                    frame_info1 = getframeinfo(currentframe())
                    print("Exception in {0}:{1} -- {2}".format(frame_info1.filename, frame_info1.lineno, e1))
                    time.sleep(5)
        except Exception as e2:
            frame_info2 = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info2.filename, frame_info2.lineno, e2))
            time.sleep(5)

    def bing_daily(self, driver, userid, passwd, search_count):
        self.login_to_live(driver, userid, passwd)
        self.check_points(driver, userid, "Starting")
        # self.earn_rewards()
        self.do_search_list(driver, search_count)
        time.sleep(10)
        self.check_points(driver, userid, "Finished")

    def quit(self, driver):
        driver.quit()