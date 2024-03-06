# -*- coding: utf-8 -*-
from yaspin import yaspin

# Global Spinner Control
spinner_enable = True

if spinner_enable:
    class Spinner:
        """
        yaspin 라이브러리를 이용한 Spinner
        """
        def __init__(self, text):
            """ 초기화
            Parameters
            ----------
            text: str
                spinner 사용시 표시할 text
            """
            self.spinner = yaspin(text=text, spinner='dots')

        def start(self):
            """ Spinner Start"""
            if spinner_enable:
                self.spinner.start()

        def stop(self):
            """ Spinner Stop """
            if spinner_enable:
                self.spinner.stop()
else:
    class Spinner:
        def __init__(self, text):
            pass

        def start(self):
            pass

        def stop(self):
            pass