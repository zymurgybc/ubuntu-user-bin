#!/usr/bin/env python3
import sys
from urllib.request import urlopen

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebKit import *

SHOWBROWSER = True
LOGIN = 'name@example.com'
PASS = 'foo'

# https://stackoverflow.com/questions/29047953/login-live-com-with-python-and-mechanize
# https://github.com/Darth4212/Microsoft-Rewards-Auto-Search-Scripts/blob/master/Search%20Script%20Setup.md
class WebPage(QWebPage):
    def __init__(self, parent=None):
        super(WebPage, self).__init__(parent)
        self.loadFinished.connect(self._loadFinished)
        self.mainFrame().load(QUrl('http://login.live.com'))

    def javaScriptConsoleMessage(self, msg, lineNumber, sourceID):
        print("JsConsole(%s:%d): %s" % (sourceID, lineNumber, msg))

    def _loadFinished(self, result):
        frame = self.mainFrame()
        url = frame.requestedUrl().toString()
        print(url)
        if url == 'http://login.live.com/':
            frame.evaluateJavaScript(self.get_jquery())
            frame.evaluateJavaScript(
                '''
                $('input[name="login"]').val('{login}')
                $('input[name="passwd"]').val('{password}')
                $('input[type="submit"]').click()
                '''.format(login=LOGIN, password=PASS)
            )
        if 'auth/complete-signin' in url:
            print('finished login')
            if not SHOWBROWSER:
                QApplication.quit()

    def get_jquery(self):
        response = urlopen('http://code.jquery.com/jquery-2.1.3.js')
        return response.read().decode('utf-8')


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.view = QWebView(self)
        self.view.setPage(WebPage())

        layout = QVBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.view)

    def headless():
        app = QApplication(sys.argv)
        view = QWebView()
        view.setPage(WebPage())
        app.exec_()


    def main():
        app = QApplication(sys.argv)
        window = Window()
        window.show()
        app.exec_()


if __name__ == "__main__":
    if SHOWBROWSER:
        main()
    else:
        headless()
