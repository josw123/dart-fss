# -*- coding: utf-8 -*-
from dart_fss._utils import is_notebook

if is_notebook():
    from halo import HaloNotebook as Halo
else:
    from halo import Halo


class Spinner:
    """
    Halo 라이브러리를 이용한 Spinner
    """
    def __init__(self, text):
        """ 초기화
        Parameters
        ----------
        text: str
            spinner 사용시 표시할 text
        """
        self.spinner = Halo(text=text, spinner='dots')

    def start(self):
        """ Spinner Start"""
        self.spinner.start()

    def stop(self):
        """ Spinner Stop """
        self.spinner.stop()