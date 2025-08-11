# agent.py
import logging
from typing import Dict, Any, List

from config import AgentConfig

# Simulation stubs
try:
    from dummy_data import DUMMY_SALES_DATA
except Exception:
    DUMMY_SALES_DATA = [
        {"customer_id": 101, "customer_name": "Alice Corp", "total_sales": 50000, "sale_date": "2025-07-15"},
        {"customer_id": 102, "customer_name": "Bob LLC", "total_sales": 42000, "sale_date": "2025-07-30"},
        {"customer_id": 103, "customer_name": "Charlie Inc", "total_sales": 38000, "sale_date": "2025-07-22"},
    ]

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Only import GCP libs if needed
if __name__ != "__main__":
    # no-op; prevents accidental import-time GCP usage in some contexts
    pass

class GCPAIAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.simulate = config.simulate

        # Lazy init clients (only when simulate == False)
        self.bq_client = None
        self.secret_client = None
        self.vertex_model = None

        if not self.simulate:
            # import here so simulation doesn't require these packages
            try:
                import vertexai
                from vertexai.generative_models import GenerativeModel
                from google.cloud import bigquery, secretmanager

                vertexai.init(project=config.project_id, location=config.location)
                # instantiate the model wrapper
                self.vertex_model = GenerativeModel(config.model_name)

                self.bq_client = bigquery.Client(project=config.project_id)
                self.secret_client = secretmanager.SecretManagerServiceClient()
                logger.info("Initialized Vertex AI, BigQuery, and Secret Manager clients.")
            except Exception as e:
                logger.exception("Failed to initialize GCP clients - ensure packages are installed and authenticated.")
                raise

    # -------------------------
    # Utility: retrieve secret
    # -------------------------
    def _get_secret(self, secret_id: str) -> str:
        if self.simulate:
            logger.info(f"[SIM] get_secret('{secret_id}') -> returning placeholder")
            return f"SIMULATED_SECRET_FOR_{secret_id}"
        name = f"projects/{self.config.project_id}/secrets/{secret_id}/versions/latest"
        response = self.secret_client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")

    # -------------------------
    # Tool: rank data
    # -------------------------
    def rank_data(self, timeframe: str = "last_month", metric: str = "total_sales") -> Dict[str, Any]:
        """
        Returns top customers by <metric> for a timeframe.
        timeframe: 'last_month' | 'last_quarter' | 'last_year'
        metric: column name (must exist in dataset)
        """
        if self.simulate:
            ranked = sorted(DUMMY_SALES_DATA, key=lambda x: x.get(metric, 0), reverse=True)
            return {"status": "success", "data": ranked[:10]}

        # Real BigQuery query
        time_expr = {
            "last_month": "DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)",
            "last_quarter": "DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH)",
            "last_year": "DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)",
        }.get(timeframe, "DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)")

        table = f"`{self.config.project_id}.{self.config.bigquery_dataset}.{self.config.bigquery_table}`"
        sql = f"""
            SELECT customer_id, customer_name, SUM({metric}) AS metric_value
            FROM {table}
            WHERE DATE(sale_date) >= {time_expr}
            GROUP BY customer_id, customer_name
            ORDER BY metric_value DESC
            LIMIT 10
        """
        try:
            query_job = self.bq_client.query(sql)
            rows = list(query_job.result())
            data = [
                {"customer_id": r["customer_id"], "customer_name": r["customer_name"], "metric_value": float(r["metric_value"])}
                for r in rows
            ]
            return {"status": "success", "data": data}
        except Exception as e:
            logger.exception("BigQuery rank_data failed")
            return {"status": "error", "message": str(e)}

    # -------------------------
    # Tool: send notifications
    # -------------------------
    def send_notifications(self, content: str, users: List[str] = None) -> Dict[str, Any]:
        """
        Real mode: reads 'gmail-app-password' and 'sender-email' from Secret Manager and sends via SMTP.
        Simulation: prints message and returns success.
        """
        if users is None:
            users = self.config.notification_users

        if self.simulate:
            logger.info("[SIMULATED EMAIL NOTIFICATION]")
            logger.info(f"Subject: AI Agent Notification")
            logger.info(f"Content: {content}")
            logger.info(f"Recipients: {users}")
            return {"status": "completed", "successful_sends": users, "failed_sends": []}

        # Real sending via SMTP using secrets (example)
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        try:
            smtp_password = self._get_secret("gmail-app-password")
            sender_email = self._get_secret("sender-email")

            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["Subject"] = "AI Agent Notification"
            msg.attach(MIMEText(content, "plain"))

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, smtp_password)

            successful_sends = []
            failed_sends = []
            for email in users:
                try:
                    msg["To"] = email
                    server.sendmail(sender_email, email, msg.as_string())
                    successful_sends.append(email)
                except Exception as e:
                    failed_sends.append({"email": email, "error": str(e)})
            server.quit()

            return {"status": "completed", "successful_sends": successful_sends, "failed_sends": failed_sends}
        except Exception as e:
            logger.exception("send_notifications failed")
            return {"status": "error", "message": str(e)}

    # -------------------------
    # Tool: define strategy
    # -------------------------
    def define_strategy(self, group: str, goal: str) -> Dict[str, Any]:
        if self.simulate:
            strategy = [
                f"Target {group} with social-first content.",
                "Use short-form video (TikTok, Reels).",
                "Leverage micro-influencers and user-generated content.",
            ]
            return {"status": "success", "strategy": strategy}

        try:
            # Use the same GenerativeModel instance created in __init__
            prompt = f"Create a practical marketing strategy for group: {group}. Goal: {goal}."
            result = self.vertex_model.generate_content(prompt)
            return {"status": "success", "strategy_text": result.text}
        except Exception as e:
            logger.exception("define_strategy failed")
            return {"status": "error", "message": str(e)}

    # -------------------------
    # Dispatcher used by model function-calls or main code
    # -------------------------
    def execute_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        mapping = {
            "rank_data": self.rank_data,
            "send_notifications": self.send_notifications,
            "define_strategy": self.define_strategy,
        }
        fn = mapping.get(tool_name)
        if not fn:
            return {"status": "error", "message": f"Unknown tool: {tool_name}"}
        return fn(**parameters)

    # -------------------------
    # Chat wrapper: minimal example using model.start_chat + function-calling detection
    # -------------------------
    def chat(self, message: str) -> str:
        if self.simulate:
            # simple heuristic routing so main.py examples work without Vertex AI
            m = message.lower()
            if "rank" in m and "sales" in m:
                out = self.rank_data()
                if out.get("status") == "success":
                    lines = [f"{i+1}. {r['customer_name']} - ${r['metric_value']}" for i, r in enumerate(out["data"])]
                    return "\n".join(lines)
                return str(out)

            if "notify" in m or "notification" in m or "send" in m:
                return self.send_notifications("Our new product is live! Please prepare the campaign.")

            # fallback: marketing strategy
            return "\n".join(self.define_strategy("millennials", "increase engagement")["strategy"])

        # Real Vertex AI flow — start a chat, allow model to ask for tools (simplified)
        try:
            chat = self.vertex_model.start_chat()
            response = chat.send_message(message)
            # If the model returns text directly:
            if hasattr(response, "text") and response.text:
                return response.text
            # If the model makes a function call (function_call detection varies by API version)
            # This pseudocode inspects content parts for function_call and executes them.
            for candidate in getattr(response, "candidates", []):
                for part in getattr(candidate, "content", {}).get("parts", []):
                    fc = getattr(part, "function_call", None)
                    if fc:
                        # `args` may be a JSON-string or dict - handle both
                        args = fc.args
                        if isinstance(args, str):
                            import json
                            try:
                                args = json.loads(args)
                            except Exception:
                                args = {}
                        tool_result = self.execute_tool_call(fc.name, args or {})
                        # send tool result back to chat (so model can incorporate it)
                        follow_up = chat.send_message([{
                            "function_call": {"name": fc.name},
                            "function_response": {"name": fc.name, "response": tool_result}
                        }])
                        if hasattr(follow_up, "text") and follow_up.text:
                            return follow_up.text
            # fallback if nothing returned
            return getattr(response, "text", "[no text returned]")
        except Exception as e:
            logger.exception("chat() failed")
            return f"Error: {e}"
