import os
import pytest
from dart_fss.auth import get_api_key

DART_API_KEY = os.getenv("DART_API_KEY")


@pytest.fixture(scope='session')
def dart_api_key():
    api_key = os.getenv("DART_API_KEY")
    if api_key is None:
        pytest.exit('DART_API_KEY not set')
    else:
        return get_api_key()


def test_auth(dart_api_key):
    api_key = os.getenv("DART_API_KEY")
    assert dart_api_key == api_key
