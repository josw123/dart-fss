

def test_stock_market_list(dart):
    _ = dart.api.market.get_stock_market_list('Y')


def test_trading_halt_list(dart):
    _ = dart.api.market.get_trading_halt_list('Y')
