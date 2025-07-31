# utils/drl_utils.py

def compute_drl_state(pred):
    """
    Constructs a state vector from prediction fields to feed into a DRL agent.
    """
    return [
        pred.get("confidence", 0) / 100,
        pred.get("trap_risk", 0),
        pred.get("readiness", 0) / 10,
        (pred.get("operator_cost", 1) - pred.get("ltp", 1)) / pred.get("operator_cost", 1)
    ]

def compute_reward(pred, actual_profit=0.1):
    """
    Reward function used during DRL training.
    Penalizes trap risk and delay. Rewards fast profit with low risk.
    """
    trap = pred.get("trap_risk", 0)
    days = pred.get("days_to_profit", 10)
    reward = actual_profit / (days + 1)
    penalty = trap * 0.2

    return round(reward - penalty, 4)
