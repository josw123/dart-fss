# -*- coding: utf-8 -*-
from yaspin import yaspin


class Spinner:
    spinner_enable = True
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
        if self.spinner_enable:
            self.spinner.start()

    def stop(self):
        """ Spinner Stop """
        if self.spinner_enable:
            self.spinner.stop()


def enable_spinner(enable: bool):
    """
    Set spinner activation status

    Parameters
    ----------
    enable: bool
       Spinner activation state
    """
    Spinner.spinner_enable = enable

