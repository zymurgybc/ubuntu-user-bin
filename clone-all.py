#!/usr/bin/env python3
import os
import json
import urllib.request  # urllib2 in Python before 3.x
import git             # /usr/local/lib/python3.6/dist-packages/git/
import pathlib

HOME=pathlib.Path.home()
REPO="zymurgybc"

folder = "{}/source/github.com/{}".format(HOME,REPO)

os.makedirs(folder, 777, True)

giturl="https://api.github.com/users/{}/repos?per_page=200".format(REPO)
response = urllib.request.urlopen(giturl)
json_object=json.load(response)

for gitrepo in json_object:
    repo_dir = "{}/{}".format(folder, gitrepo["name"])
    if os.path.exists(repo_dir):
        os.chdir(repo_dir)
        g1 = git.cmd.Git()
        print("Pulling git for {}".format(os.getcwd()))
        print(g1.pull())
    else:
        print("Cloning git for {}".format(repo_dir))
        g2 = git.cmd.Git(folder)
        print(g2.clone(json_object["ssh_url"]))
