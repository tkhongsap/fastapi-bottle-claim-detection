# utils/cost_utils.py

# Model token cost per 1M tokens from Azure OpenAI Pricing (as of 2025-04)
MODEL_COSTS = {
    "gpt-4.1": {"input": 2.00, "output": 8.00},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
    "gpt-4.1-nano": {"input": 0.10, "output": 0.40},
    "gpt-4o-2024-1120": {"input": 2.50, "output": 10.00},
    "gpt-4o-2024-1120-eu": {"input": 2.75, "output": 11.00},
    "gpt-4o-2024-1120-regional": {"input": 2.75, "output": 11.00},
    "gpt-4o-mini-0718": {"input": 0.15, "output": 0.60},
    "gpt-4o-mini-0718-eu": {"input": 0.165, "output": 0.66},
    "gpt-4o-mini-0718-regional": {"input": 0.165, "output": 0.66},
    "gpt-4.5-preview": {"input": 75.00, "output": 150.00},
    "o3": {"input": 10.00, "output": 40.00},
    "o3-mini": {"input": 1.10, "output": 4.40},
    "o3-mini-eu": {"input": 1.21, "output": 4.84},
    "o1": {"input": 15.00, "output": 60.00},
    "o1-mini": {"input": 1.10, "output": 4.40},
    "gpt-4o-2024-08-06": {"input": 2.50, "output": 10.00},
    "gpt-4o-2024-08-06-eu": {"input": 2.75, "output": 11.00},
    "gpt-4o-2024-08-06-regional": {"input": 2.75, "output": 11.00},
    "gpt-4o-2024-0513": {"input": 5.00, "output": 15.00},
}

# Exchange rate for conversion
USD_TO_THB_RATE = 35.0

def get_model_cost(model_name: str):
    return MODEL_COSTS.get(model_name, {"input": 1.00, "output": 1.00})  # Fallback default 