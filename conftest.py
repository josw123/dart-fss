import os
import sys
import pytest


def pytest_addoption(parser):
    print("add option")
    if sys.version_info[0] != 3:
        pytest.skip('This Python version({}) is not supported'.format(sys.version))

    parser.addoption("--loc", action="store", default="local", metavar="LOCATION",
                     help="Test environment")
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


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
