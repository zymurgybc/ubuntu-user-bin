#!/usr/bin/env python3

import requests
import random
import json
import time
from inspect import currentframe, getframeinfo


def get_word_list(count: int):
    random_lists_url = "https://www.randomlists.com/data/words.json"
    response = requests.get(random_lists_url)
    words_list = random.sample(json.loads(response.text)['data'], count)
    print('{0} words selected from {1}'.format(len(words_list), random_lists_url))
    return words_list


def create_file(file_name, content):
    text_file = open(file_name, "w")
    text_file.write(content)
    text_file.close()


def log_me_out_MS(driver, url):
    try:
        driver.get(url)
        time.sleep(5)

        # when this is found, an account is already/still logged in
        # notably, it throws an exception when not found, not none
        elem = driver.find_element_by_id('mectrl_headerPicture')
        if elem is not None:
            elem.click()
            time.sleep(2)
            elem = driver.find_element_by_id('mectrl_body_signOut')
            if elem is not None:
                elem.click()
                time.sleep(4)
        # Try and reload the page
    except Exception as e:
        frame_info = getframeinfo(currentframe())
        print("Exception in {0}:{1} -- {2}".format(frame_info.filename, frame_info.lineno, e))
        time.sleep(4)


