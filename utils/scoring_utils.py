# utils/scoring_utils.py

from collections import Counter

def aggregate_scores(scores):
    """
    Aggregate list of per-model scores into one final result.
    Each item in scores[] must include: confidence, trap_risk, signal
    """
    if not scores:
        return {
            "confidence": 0,
            "trap_risk": 0,
            "signal": "Hold",
            "sector": "Unknown"
        }

    total_conf = 0
    total_trap = 0
    signal_votes = Counter()
    sector_votes = Counter()

    for s in scores:
        total_conf += s.get("confidence", 0)
        total_trap += s.get("trap_risk", 0)
        signal_votes[s.get("signal", "Hold")] += 1
        sector_votes[s.get("sector", "Unknown")] += 1

    avg_conf = total_conf / len(scores)
    avg_trap = total_trap / len(scores)

    final_signal = signal_votes.most_common(1)[0][0]
    final_sector = sector_votes.most_common(1)[0][0]

    return {
        "confidence": avg_conf,
        "trap_risk": avg_trap,
        "signal": final_signal,
        "sector": final_sector
    }
