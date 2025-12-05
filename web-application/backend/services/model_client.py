from typing import Dict, Any


class ModelClient:
    THRESHOLDS = [5, 6, 10, 15, 20, 25, 30]

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        delay = float(features["src_arrival_delay"]) + 3.0

        results = {
            "dst_arrival_delay": delay,
            "model_version": "placeholder_v1",
        }

        for t in self.THRESHOLDS:
            prob = max(0, min(1, (delay - t + 10) / 20))
            results[f"dst_arrival_delay_over_{t}_minutes_prob"] = prob

        return results


model_client = ModelClient()
