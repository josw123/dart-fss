import os
import sys
import pytest


def pytest_addoption(parser):
    print("add option")
    if sys.version_info[0] != 3:
        pytest.skip('This Python version({}) is not supported'.format(sys.version))

    parser.addoption("--loc", action="store", default="local", metavar="LOCATION",
                     help="Test environment")


@pytest.fixture(scope="session", autouse=True)
def local(request):
    location = request.config.getoption("--loc")
    if location == 'local':
        return True
    elif location == 'remote':
        return False
    elif location == 'travis':
        return False
    else:
        raise ValueError('Unknown option')


@pytest.fixture(scope="session")
def dart(local):
    import dart_fss
    if local:
        env_key = 'DART_API_KEY'
    else:
        env_key = 'DART_API_TEST_KEY_V3{}'.format(sys.version_info[1])
    api_key = os.getenv(env_key)
    if api_key is None:
        pytest.skip('Please, set valid "{}" env variable'.format(env_key))
    dart_fss.set_api_key(api_key)

    return dart_fss
