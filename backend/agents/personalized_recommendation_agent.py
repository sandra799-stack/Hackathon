import os
import sys
import json
import pandas as pd
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_loyal_users_order_history, get_users_emails
from cloud_functions import send_email

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# GCP imports
from google.cloud import bigquery
from google.cloud import storage
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account

# LangChain imports
from langchain_google_vertexai import ChatVertexAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecommendationItem(BaseModel):
    """Pydantic model for recommendation items"""
    item_id: str = Field(description="Unique identifier for the item")
    item_name: str = Field(description="Name of the recommended item")
    category: str = Field(description="Category of the item")
    confidence_score: float = Field(description="Confidence score between 0 and 1")
    reason: str = Field(description="Reason for recommendation")

class CustomerRecommendations(BaseModel):
    """Pydantic model for customer recommendations"""
    customer_id: str = Field(description="Customer identifier")
    recommendations: List[RecommendationItem] = Field(description="List of recommended items")


class GCPRecommendationSystem:
    """
    A recommendation system using GCP services, LangChain, and Gemini
    """
    
    def __init__(self, project_id: str = None, region: str = None):
        """
        Initialize the recommendation system
        """
        # Load configuration from .env file
        self.project_id = project_id or os.getenv("PROJECT_ID")
        self.region = region or os.getenv("REGION", "us-central1")
        
        if not self.project_id:
            raise ValueError("GCP_PROJECT_ID must be set in .env file or passed as parameter")
        
        # Initialize GCP clients
        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.region)
        
        # Initialize LangChain with Gemini model
        self.llm = ChatVertexAI(
            model_name="gemini-2.5-pro", 
            temperature=0.3,
            max_output_tokens=2048,
            project=self.project_id,
            location=self.region
        )
    
    def analyze_purchase_history(self, purchase_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Analyze purchase history to extract patterns and insights
        """
        logger.info("Analyzing purchase history...")
        
        customer_stats = purchase_data.groupby('customer_id').agg({
            'item_id': 'count',
            'price': ['sum', 'mean'],
            'purchase_date': ['min', 'max']
        }).round(2)
        
        item_popularity = purchase_data.groupby(['item_id', 'item_name']).agg({
            'customer_id': 'nunique',
            'quantity': 'sum',
            'price': 'mean'
        }).sort_values('customer_id', ascending=False)
        
        return {
            'customer_stats': customer_stats,
            'item_popularity': item_popularity,
            'total_customers': purchase_data['customer_id'].nunique(),
            'total_items': purchase_data['item_id'].nunique()
        }
    
    def generate_recommendations(self, purchase_data: pd.DataFrame, 
                                 loyal_customers: List[str] = None) -> Dict[str, CustomerRecommendations]:
        """
        Generate recommendations for customers using Gemini with structured output.
        """
        logger.info("Generating recommendations using Gemini with structured output...")
        
        structured_llm = self.llm.with_structured_output(CustomerRecommendations)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert e-commerce recommendation engine. Analyze the provided customer data and generate exactly 5 personalized product recommendations. The customer_id in your response MUST match the customer_id provided in the input."),
            ("human", """
            Please generate recommendations for the following customer:
            
            Customer ID: {customer_id}
            
            Recent Purchase History:
            {customer_history}
            
            Popular Items Across All Customers (for context):
            {popular_items}
            
            Based on the customer's purchase history and general trends, provide 5 recommendations they are likely to be interested in.
            """)
        ])
        
        chain = prompt | structured_llm

        analysis = self.analyze_purchase_history(purchase_data)
        
        logger.info(f"Generating recommendations for {len(loyal_customers)} loyal customers")
        
        popular_items = analysis['item_popularity'].head(20).reset_index().to_dict('records')
        recommendations = {}
        
        for customer_id in loyal_customers[:10]:
            try:
                customer_purchases_df = purchase_data[purchase_data['customer_id'] == customer_id].copy()
                if 'purchase_date' in customer_purchases_df.columns:
                    customer_purchases_df['purchase_date'] = customer_purchases_df['purchase_date'].dt.strftime('%Y-%m-%d')
                customer_purchases = customer_purchases_df.to_dict('records')
                
                result = chain.invoke({
                    "customer_id": customer_id,
                    "customer_history": json.dumps(customer_purchases[-5:], indent=2),
                    "popular_items": json.dumps(popular_items[:10], indent=2)
                })
                
                recommendations[customer_id] = result
                logger.info(f"Successfully generated recommendations for customer {customer_id}")

            except Exception as e:
                logger.error(f"Structured output generation failed for {customer_id}: {e}")
                logger.info(f"Using fallback recommendations for customer {customer_id}")
                # We need customer_purchases for fallback, ensure it's defined
                customer_purchases_df = purchase_data[purchase_data['customer_id'] == customer_id].copy()
                customer_purchases = customer_purchases_df.to_dict('records')
                recommendations[customer_id] = self.create_fallback_recommendations(
                    customer_id, customer_purchases, popular_items
                )
        
        return recommendations
    
    def create_fallback_recommendations(self, customer_id: str, 
                                        customer_history: List[Dict], 
                                        popular_items: List[Dict]) -> CustomerRecommendations:
        """
        Create fallback recommendations if LLM generation fails
        """
        logger.info(f"Creating fallback recommendations for {customer_id}")
        
        customer_categories = set(item.get('category', 'Unknown') for item in customer_history)
        fallback_recs = []
        
        for item in popular_items:
            if len(fallback_recs) >= 5: break
            if item.get('category') in customer_categories:
                fallback_recs.append(RecommendationItem(
                    item_id=str(item.get('item_id', f'FALLBACK_{len(fallback_recs)}')),
                    item_name=str(item.get('item_name', 'Popular Item')),
                    category=str(item.get('category', 'Unknown')),
                    confidence_score=0.7,
                    reason=f"Popular item in your preferred category: {item.get('category')}"
                ))
        
        added_ids = {rec.item_id for rec in fallback_recs}
        for item in popular_items:
            if len(fallback_recs) >= 5: break
            item_id_str = str(item.get('item_id', ''))
            if item_id_str not in added_ids:
                fallback_recs.append(RecommendationItem(
                    item_id=item_id_str,
                    item_name=str(item.get('item_name', 'Popular Item')),
                    category=str(item.get('category', 'Unknown')),
                    confidence_score=0.5,
                    reason="Popular item among all customers"
                ))
                added_ids.add(item_id_str)
        
        return CustomerRecommendations(
            customer_id=customer_id,
            recommendations=fallback_recs[:5]
        )
    
    def store_recommendations_to_bigquery(self, recommendations: Dict[str, CustomerRecommendations], 
                                          dataset_id: str, table_id: str):
        """
        Store recommendations to BigQuery for analytics and tracking
        """
        logger.info("Storing recommendations to BigQuery...")
        
        rows_to_insert = []
        for customer_id, customer_recs in recommendations.items():
            for rec in customer_recs.recommendations:
                rows_to_insert.append({
                    'customer_id': customer_id,
                    'item_id': rec.item_id,
                    'item_name': rec.item_name,
                    'category': rec.category,
                    'confidence_score': rec.confidence_score,
                    'reason': rec.reason,
                    'recommendation_date': datetime.now().isoformat(),
                    'status': 'sent'
                })
        
        if not rows_to_insert:
            logger.warning("No recommendation rows to insert into BigQuery.")
            return

        table_ref = self.bq_client.dataset(dataset_id).table(table_id)
        
        try:
            errors = self.bq_client.insert_rows_json(table_ref, rows_to_insert)
            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
            else:
                logger.info(f"Successfully inserted {len(rows_to_insert)} recommendation records")
        except Exception as e:
            logger.error(f"Failed to insert recommendations to BigQuery: {e}")
    
    def generate_email_content(self, customer_id: str, 
                               recommendations: CustomerRecommendations) -> tuple[str, str]:
        """
        Generate personalized email content using Gemini
        """
        email_prompt = f"""
        Create a personalized marketing email for customer {customer_id} with the following recommendations:
        
        {json.dumps([rec.dict() for rec in recommendations.recommendations], indent=2)}
        
        The email should be:
        - Friendly and personalized
        - Highlight the top 3 recommendations
        - Include compelling reasons to purchase
        - Have a clear call-to-action
        - Be professional but engaging
        
        Generate both a subject line and email body.
        Format as:
        SUBJECT: [subject linE]
        BODY: [email body]
        """
        
        try:
            response = self.llm.invoke([HumanMessage(content=email_prompt)])
            content = response.content
            
            subject_match = re.search(r"SUBJECT:(.*)", content)
            body_match = re.search(r"BODY:(.*)", content, re.DOTALL)

            subject = subject_match.group(1).strip() if subject_match else f"Personalized Recommendations Just for You!"
            body = body_match.group(1).strip() if body_match else self.create_fallback_email_body(recommendations)
            
            return subject, body
            
        except Exception as e:
            logger.error(f"Error generating email content: {e}")
            return self.create_fallback_email_content(customer_id, recommendations)
    
    def create_fallback_email_content(self, customer_id: str, 
                                      recommendations: CustomerRecommendations) -> tuple[str, str]:
        """
        Create fallback email content if LLM generation fails
        """
        subject = "Special Recommendations Just for You!"
        
        body = f"""
        <html><body>
        <h2>Hi there, valued customer!</h2>
        <p>Based on your purchase history, we've found some items you might love:</p>
        <ul>
        """
        
        for rec in recommendations.recommendations[:3]:
            body += f"<li><strong>{rec.item_name}</strong> ({rec.category})<br><em>{rec.reason}</em></li>"
        
        body += """
        </ul>
        <p>Don't miss out on these great recommendations!</p>
        <p><a href="#" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Shop Now</a></p>
        <p>Best regards,<br>Your Shopping Team</p>
        </body></html>
        """
        
        return subject, body
    
    def send_email_notification(self, customer_email: str, subject: str, 
                                html_body: str, customer_id: str) -> bool:
        """
        Send email notification to customer
        """
        try:
            send_email(to_email=customer_email,
                        subject=subject,
                        body=html_body)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to customer {customer_id}: {e}")
            return False
    
    def run_recommendation_pipeline(self, purchase_data: pd.DataFrame, 
                                    customer_emails: Dict[str, str],
                                    ):
        """
        Run the complete recommendation pipeline
        """
        logger.info("Starting recommendation pipeline...")
        
        try:
            loyal_customers = list(set(purchase_data['customer_id']))
            recommendations = self.generate_recommendations(purchase_data, loyal_customers)
            
            if not recommendations:
                logger.warning("No recommendations were generated.")
                return
            
            email_results = {}
            for customer_id, customer_recs in recommendations.items():
                if customer_id in customer_emails:
                    subject, body = self.generate_email_content(customer_id, customer_recs)
                    
                    # for testing
                    email_sent = self.send_email_notification(
                        'nhelmy@deloitte.com', subject, body, customer_id
                    )

                    email_sent = self.send_email_notification(
                        customer_emails[customer_id], subject, body, customer_id
                    )
                    email_results[customer_id] = email_sent
                else:
                    logger.warning(f"No email address found for customer {customer_id}")
            
            successful_emails = sum(1 for sent in email_results.values() if sent)
            logger.info(f"Pipeline completed: {len(recommendations)} recommendations generated, "
                        f"{successful_emails} emails sent successfully")
            
            return {
                'recommendations': recommendations,
                'email_results': email_results
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise

def setup_bigquery_table(project_id: str, dataset_id: str, table_id: str):
    """
    Create BigQuery table for storing recommendations
    """
    client = bigquery.Client(project=project_id)
    
    # Create dataset if it doesn't exist
    dataset_ref = client.dataset(dataset_id)
    try:
        client.get_dataset(dataset_ref)
    except:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US"
        client.create_dataset(dataset)
        logger.info(f"Created dataset {dataset_id}")
    
    # Define table schema
    schema = [
        bigquery.SchemaField("customer_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("item_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("item_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("category", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("confidence_score", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("reason", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("recommendation_date", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("status", "STRING", mode="REQUIRED"),
    ]
    
    # Create table
    table_ref = dataset_ref.table(table_id)
    try:
        client.get_table(table_ref)
        logger.info(f"Table {table_id} already exists")
    except:
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)
        logger.info(f"Created table {table_id}")

def load_purchase_data_from_bigquery(project_id: str, query: str) -> pd.DataFrame:
    """
    Load purchase data from BigQuery
    """
    client = bigquery.Client(project=project_id)
    return client.query(query).to_dataframe()

def load_customer_emails_from_bigquery(project_id: str, query: str) -> Dict[str, str]:
    """
    Load customer email addresses from BigQuery
    """
    client = bigquery.Client(project=project_id)
    df = client.query(query).to_dataframe()
    return dict(zip(df['customer_id'], df['email']))

def schedule_recommendations_with_cloud_functions():
    """
    Example of how to schedule this system using Cloud Functions
    This would be deployed as a separate Cloud Function
    """
    pass

def recommend_personalized_products(merchant_id):
    """
    Main function to run the recommendation system
    """
    try:
        # Initialize the recommendation system (will read from .env automatically)
        rec_system = GCPRecommendationSystem()
        
        # Create sample data (replace with your actual data loading)
        purchase_data = get_loyal_users_order_history(merchant_id)
        users_ids = list(set(purchase_data['customer_id']))
        customer_emails = get_users_emails(users_ids)
        
        logger.info(f"Loaded {len(purchase_data)} purchase records for {purchase_data['customer_id'].nunique()} customers")
        
        #setup_bigquery_table(rec_system.project_id, bq_dataset, bq_table)
        
        # Run the recommendation pipeline
        results = rec_system.run_recommendation_pipeline(
            purchase_data=purchase_data,
            customer_emails=customer_emails
        )
        
        # Print results summary
        if results:
            print(f"\n=== Recommendation Pipeline Results ===")
            print(f"Recommendations generated for {len(results['recommendations'])} customers")
            print(f"Emails sent successfully: {sum(results['email_results'].values())}")
            
            # Show sample recommendation
            if results['recommendations']:
                sample_customer = list(results['recommendations'].keys())[0]
                sample_recs = results['recommendations'][sample_customer]
                print(f"\nSample recommendations for {sample_customer}:")
                for rec in sample_recs.recommendations[:3]:
                    print(f"- {rec.item_name} ({rec.confidence_score:.2f}): {rec.reason}")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        raise

# Example BigQuery queries for loading data:
SAMPLE_PURCHASE_QUERY = """
SELECT 
    customer_id,
    item_id,
    item_name,
    category,
    purchase_date,
    quantity,
    price
FROM `your-project.your-dataset.purchase_history`
WHERE purchase_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
ORDER BY customer_id, purchase_date
"""

SAMPLE_CUSTOMER_EMAIL_QUERY = """
SELECT 
    customer_id,
    email
FROM `your-project.your-dataset.customers`
WHERE email IS NOT NULL
AND marketing_opt_in = true
"""

if __name__ == "__main__":
    # Example usage
    recommend_personalized_products(94025)