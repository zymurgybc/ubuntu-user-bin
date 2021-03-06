#!/usr/bin/env python3

import os
import requests
import random
import json
import time
from datetime import datetime
from inspect import currentframe, getframeinfo

#from selenium.webdriver import dimension
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class BasicSearch:
    def __init__(self):
        print("Executing {0}".format(__file__))
        # Accommodate using a Raspberry Pi more slowly because some of the
        # JavaScript heavy pages render more slowly. uname isn't on Windows?
        if hasattr(os, "uname") and os.uname()[4][:3] == 'arm' :
            self.pause = 10
        else:
            self.pause = 5
        pass

    def get_first_elem(self, elem):
        if elem is None:
            return None  # no reference value
        else:
            if hasattr(elem, "__iter__"):
                if len(elem) < 1:
                    return None  # Empty collection
                else:
                    return elem[0]
            else:
                return elem

    def click_first_elem(self, elems):
        elem = self.get_first_elem(elems)
        if elem is not None:
            elem.click()
            time.sleep(self.pause)
            return True   # something was clicked on
        return False

    # This simply looks for the option to "Log in" rather than "Log Out"
    # using the rewards page since its where we need the login/out to happen
    def is_logged_in(self, driver):
        try:
            driver.get("https://account.microsoft.com/rewards/")
            time.sleep(self.pause)
            elem = driver.find_elements_by_css_selector("div.mectrl_root span.mectrl_screen_reader_text")
            return len(elem) < 1 or elem[0].text != "Sign in to your account"

        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(self.pause)

    def get_word_list(self, count):
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
        time.sleep(self.pause)
        btn = driver.find_elements_by_css_selector("#clearBrowsingDataConfirm")
        self.click_first_elem(btn, 2)

    def log_me_out_MS(self, driver, url):
        try:
            driver.get(url)
            time.sleep(self.pause)

            # when this is found, an account is already/still logged in
            # notably, it throws an exception when not found, not none
            elem = driver.find_elements_by_css_selector('mectrl_headerPicture')
            if self.click_first_elem(elem):
                elem = driver.find_elements_by_css_selector('mectrl_body_signOut')
                self.click_first_elem(elem)
            # Try and reload the page
        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(self.pause)

        # The Bing Search page doesn't use the same format as most Microsoft headers
        try:
            elem = driver.find_elements_by_css_selector('#id_l')
            if self.click_first_elem(elem):
                elem = driver.find_elements_by_css_selector('#b_idProviders > li > a > span.id_link_text')
                self.click_first_elem(elem)
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
            time.sleep(self.pause)
            elem1 = driver.find_element_by_name('passwd')
            elem1.clear()
            elem1.send_keys(passwd)  # add your password
            elem1.send_keys(Keys.ENTER)
            time.sleep(self.pause)
        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(self.pause)

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
            self.click_first_elem(anchor)
        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(self.pause)

    # This simply looks for the option to "Log in" rather than "Log Out"
    # using the rewards page since its where we need the login/out to happen
    def is_logged_in(self, driver):
        try:
            driver.get("https://account.microsoft.com/rewards/")
            time.sleep(self.pause)
            elems = driver.find_elements_by_css_selector("div.mectrl_root span.mectrl_screen_reader_text")
            elem = self.get_first_elem(elems)
            if elem is not None:
                return elem.text != "Sign in to your account"

        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(self.pause)

        return False  # default is to assume an account is still logged in

    def set_window_size(self, driver):
        if hasattr(os, "uname") and os.uname()[4][:3] == 'arm':
            # Maximize current window using anything like the Pi
            driver.maximize_window()
        else:
            # set window size to a common desktop size without using the entire 4K desktop
            # the width of 1024 is too narrow to show the user icon that shows you logged in
            driver.set_window_size(1080, 768)

    def check_points(self, driver, userid, tag_string):
        try:
            driver.get("https://account.microsoft.com/rewards/")
            time.sleep(self.pause)
            elements = None
            element = None
            # Elements being present is highly dependent on screen sizes, so we look for several
            # different presentation styles to try and find it.
            try:
                elements = driver.find_elements_by_css_selector("div#userBanner p.number span")
                element = self.get_first_elem(elements)
            except:  # Exception as e1:
                pass

            if element is None:
                try:
                    elements = driver.find_elements_by_css_selector("meeBanner > div > div > mee-persona > div:nth-child(2) > persona-body > p.description.ng-binding.ng-scope.c-caption-1.hideAll > b:nth-child(1)")
                    element = self.get_first_elem(elements)
                except:  # Exception as e3:
                    pass

            if element is not None:
                points = element.text
                print('{0} {1} points for {2}'.format(tag_string, points, userid))
            else:
                print('{0} Did not find points for {1}'.format(tag_string, userid))

        except Exception as e:
            frame_info = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
            time.sleep(self.pause)

    # TODO: complete the quiz steps?
    def earn_rewards(self, driver):

        url_base = 'https://account.microsoft.com/rewards/'
        self.ensure_loggedin(url_base)
        try:
            elements = driver.find_element_by_css_selector("span.mee-icon-AddMedium[aria-label='plus']")
            # element = self.get_first_elem(elements)
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
            time.sleep(self.pause)

    # common login.live header
    def click_logmein(self, driver, selector):
        # Look for the "your account" anchor and see if it has an name associated
        # and click the anchor if its not there to round-trip the login info
        # Look for the "your account" anchor and see if it has an name associated
        # and click the anchor if its not there to round-trip the login info
        try:
            elem = driver.find_elements_by_css_selector(selector)
            # if this element is not found, it shows the page isn't currently logged in
            # or it may not be displayed which also means you're not logged in
            return self.click_first_elem(elem)

        except Exception as e1:
            frame_info1 = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}\n    Looking for %s".format(
                frame_info1.filename,
                frame_info1.lineno,
                e1,
                selector))
            time.sleep(self.pause)
            return False

    # the bing page shows a stupid 'We use cookies" bar that makes it hard to
    # see the top of the page of check if you're properly logged in
    def hide_the_cookies_note(self, driver):

        try:
            elems = driver.find_elements_by_css_selector("div#b_notificationContainer")
            div = self.get_first_elem(elems)
            if div is not None:
                if driver.execute_script:
                    driver.execute_script("document.querySelector('div#b_notificationContainer').style.display = 'none'")

        except Exception as e1:
            frame_info1 = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info1.filename, frame_info1.lineno, e1))
            time.sleep(self.pause)
        try:
            elems = driver.find_elements_by_css_selector("div#bnp_ttc_div")
            div = self.get_first_elem(elems)
            if div is not None:
                if driver.execute_script:
                    driver.execute_script("document.querySelector('div#bnp_ttc_div').style.display = 'none'")

        except Exception as e1:
            frame_info1 = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info1.filename, frame_info1.lineno, e1))
            time.sleep(self.pause)

    # The search page may need a poke to refresh the login to Live.com
    def verify_logged_in(self, driver):

        panel = self.get_first_elem(driver.find_elements_by_css_selector(".slidein_ltr"))
        if panel is None:
            self.click_first_elem(driver.find_elements_by_css_selector("#mHamburger"))

        if self.click_logmein(driver, "#hb_s"):
            bFound = True
            print("Found log-in header for live.com")
        if self.click_logmein(driver, "#HBSignIn > a"):
            print("Found bing log-in header for live.com")


    def do_search_list(self, driver, word_count):
        words_list = self.get_word_list(count=word_count)

        url_base = 'http://www.bing.com/search?q='
        driver.get(url_base + datetime.today().strftime("%A"))
        self.hide_the_cookies_note(driver)

        time.sleep(self.pause)
        self.verify_logged_in(driver)

        try:
            for num, word in enumerate(words_list):
                print('{0}. URL : {1}'.format(str(num + 1), url_base + word))
                try:
                    driver.get(url_base + word)
                    self.hide_the_cookies_note(driver)
                    print('\t' + driver.find_element_by_tag_name('h2').text)
                    # this is a REALLY slow page!
                    time.sleep(self.pause * 2)
                except Exception as e1:
                    frame_info1 = getframeinfo(currentframe())
                    print("Exception in {0}:{1} -- {2}".format(frame_info1.filename, frame_info1.lineno, e1))
                    time.sleep(self.pause)
        except Exception as e2:
            frame_info2 = getframeinfo(currentframe())
            print("Exception in {0}:{1} -- {2}".format(frame_info2.filename, frame_info2.lineno, e2))
            time.sleep(self.pause)

    def bing_daily(self, driver, userid, passwd, search_count):
        self.set_window_size(driver)
        self.login_to_live(driver, userid, passwd)
        self.check_points(driver, userid, "Starting")
        # self.earn_rewards()
        self.do_search_list(driver, search_count)
        time.sleep(self.pause)
        self.check_points(driver, userid, "Finished")

    def quit(self, driver):
        driver.quit()
