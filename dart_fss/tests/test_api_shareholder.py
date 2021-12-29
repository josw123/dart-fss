# -*- coding: utf-8 -*-
from dart_fss.errors.errors import NoDataReceived


def test_majorstock(dart):
    try:
        _ = dart.api.shareholder.majorstock(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_elestock(dart):
    try:
        _ = dart.api.shareholder.elestock(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e
