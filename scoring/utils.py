
def detect_trap(df):
    last = df['rate'].iloc[-1]
    avg = df['rate'].rolling(5).mean().iloc[-1]
    return last > avg * 1.1

def compute_replay_match(symbol):
    return 0.8 if symbol.startswith("N") else 0.6
