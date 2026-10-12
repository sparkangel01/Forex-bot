# check_symbols.py - Verify account, server, and find correct EURUSD symbol

import MetaTrader5 as mt5
import config

print("🔌 Initializing MT5...")
if not mt5.initialize():
    print(f"❌ initialize failed: {mt5.last_error()}")
    quit()

print("🔐 Logging in...")
if not mt5.login(config.MT5_LOGIN, password=config.MT5_PASSWORD, server=config.MT5_SERVER):
    print(f"❌ Login failed: {mt5.last_error()}")
    print("   Check server name is EXACTLY 'Deriv-Demo'")
    mt5.shutdown()
    quit()

info = mt5.account_info()
print(f"\n✅ LOGGED IN")
print(f"   Login:    {info.login}")
print(f"   Server:   {info.server}")
print(f"   Balance:  {info.balance:.2f} {info.currency}")
print(f"   Leverage: 1:{info.leverage}")

# Find all symbols containing EURUSD
print("\n🔍 Searching for EURUSD symbols...")
all_symbols = mt5.symbols_get()
matches = [s.name for s in all_symbols if "EURUSD" in s.name.upper()]

if matches:
    print(f"   Found {len(matches)} match(es):")
    for name in matches:
        sym = mt5.symbol_info(name)
        if sym:
            # Make sure it's visible in Market Watch
            if not sym.visible:
                mt5.symbol_select(name, True)
            tick = mt5.symbol_info_tick(name)
            print(f"   → {name:<20} bid={tick.bid if tick else 'N/A'} ask={tick.ask if tick else 'N/A'} digits={sym.digits}")
else:
    print("   ❌ No EURUSD symbols found. Try searching another pair.")

# Test copy_rates
print("\n📊 Testing data fetch...")
if matches:
    test_sym = matches[0]
    rates = mt5.copy_rates_from_pos(test_sym, mt5.TIMEFRAME_M5, 0, 50)
    if rates is not None and len(rates) > 0:
        print(f"   ✅ Got {len(rates)} M5 bars for {test_sym}")
        print(f"   Latest close: {rates[-1]['close']}")
    else:
        print(f"   ❌ No data for {test_sym}")

mt5.shutdown()
print("\n🔌 Done.")
