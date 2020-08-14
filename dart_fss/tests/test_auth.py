def test_auth(dart):
    api_key = dart.get_api_key()
    assert api_key is not None
