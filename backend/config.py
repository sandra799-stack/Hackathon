from dataclasses import dataclass
from typing import List

@dataclass
class AgentConfig:
    project_id: str = ""
    location: str = "us-central1"
    model_name: str = "gemini-1.5-pro"
    bigquery_dataset: str = "consumer_data"
    bigquery_table: str = "sales_metrics"
    simulate: bool = True  # True -> use dummy; False -> call real GCP
    notification_users: List[str] = None

    def __post_init__(self):
        if self.notification_users is None:
            self.notification_users = ["marketing@example.com"]
