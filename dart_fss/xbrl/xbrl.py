# -*- coding: utf-8 -*-
import os
import sys

from arelle import Cntlr
from dart_fss.xbrl.dart_xbrl import DartXbrl


def get_xbrl_from_file(file_path: str) -> DartXbrl:
    """ XBRL 파일 로드 함수

    XBRL 파일을 로드하기 위한 함수로 로딩완료 후 DartXbrl 클래스를 반환한다

    Parameters
    ----------
    file_path: str
        XBRL 파일 경로
    Returns
    -------
    DartXbrl
        DartXbrl 클래스
    """
    from dart_fss.utils.spinner import Spinner
    spinner = Spinner('XBRL Loading')
    spinner.start()

    # PyPI를 통해 설치된 Arelle 라이브러리 사용시 발생하는 오류 수정을 위한코드
    if sys.platform == 'win32':
        pass
    elif sys.platform == 'darwin':
        arelle_app_dir = os.path.join(os.path.expanduser('~/Library/Application Support'), 'Arelle')
        if not os.path.exists(arelle_app_dir):
            os.makedirs(arelle_app_dir)
    else:
        arelle_app_dir = os.path.join(os.path.expanduser("~/.config"), "arelle")
        if not os.path.exists(arelle_app_dir):
            os.makedirs(arelle_app_dir)
    model_xbrl = Cntlr.Cntlr().modelManager.load(file_path)
    filename = file_path.split('\\')[-1]
    xbrl = DartXbrl(filename, model_xbrl)

    spinner.stop()
    return xbrl
