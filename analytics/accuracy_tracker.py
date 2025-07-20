
import pandas as pd
from datetime import datetime

def log_accuracy(symbol, signal, result, path="analytics/accuracy_log.csv"):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "signal": signal,
        "result": result
    }
    df = pd.DataFrame([entry])
    df.to_csv(path, mode='a', header=not pd.io.common.file_exists(path), index=False)
