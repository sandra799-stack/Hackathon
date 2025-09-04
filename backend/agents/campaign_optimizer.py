# campaign_optimizer.py
import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass
from google.cloud import bigquery
import logging
from langchain_google_vertexai import ChatVertexAI
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage, HumanMessage
from langchain.agents import create_tool_calling_agent
from dotenv import load_dotenv
import subprocess
import sys
from google.oauth2 import service_account
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from crud import insert_active_promotion, delete_active_promotion, is_promotion_active
from cloud_functions import schedule_job, delete_job
from app_db import SessionLocal
load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL")
endpoints = {
    'happy-hour': {
        "url": f"{API_BASE_URL}/promotions/happy-hour",
        "schedule": "0 0 * * *" # Runs every day at midnight UTC
    },
    "birthday": {
        "url": f"{API_BASE_URL}/promotions/birthday",
        "schedule": "0 0 * * *"
    },
    'know-your-customer': {
        "url": f"{API_BASE_URL}/promotions/know-your-customer",
        "schedule": "0 0 * * *" # Runs every day at midnight UTC
    },
    'weather-recommendation': {
        "url": f"{API_BASE_URL}/recommendations/weather",
        "schedule": "0 0 * * *" # Runs every day at midnight UTC
    },
    'social-media-posts': {
        "url": f"{API_BASE_URL}/promotions/social-media",
        "schedule": "0 0 * * *" # Runs every day at midnight UTC
    },
    'personalized-recommendation': {
        "url": f"{API_BASE_URL}/promotions/personalized",
        "schedule": "0 0 * * *" # Runs every day at midnight UTC
    }
}
# Load environment variables

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

campaigns_map = {
    'happy_hour_campaign': 'happy-hour',
    'birthday_campaign' : 'birthday',
    'weather_recommendation_agent': 'weather-recommendation',
    'social_media_agent': 'social-media-posts',
    'personalised_recommendation_agent': 'personalized-recommendation'
}

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

@dataclass
class CampaignStatus:
    name: str
    is_active: bool
    last_activated: datetime = None
    performance_score: float = 0.0

class SalesDataAnalyzer:
    """Analyzes sales data to provide insights for campaign optimization"""
    
    def __init__(self, project_id: str):
        self.client = bigquery.Client(project=project_id)
        
    def get_last_month_sales_data(self) -> pd.DataFrame:
        """Retrieve sales data from the last month"""
        query = """
        SELECT 
            DATE(order_date) as date,
            EXTRACT(HOUR FROM order_date) as hour,
            product_id,
            customer_id,
            revenue,
            campaign_source,
            weather_conditions,
            customer_birthday
        FROM `{}.sales.transactions`
        WHERE order_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
        ORDER BY order_date DESC
        """.format(os.getenv('PROJECT_ID'))
        
        try:
            df = self.client.query(query).to_dataframe()
            logger.info(f"Retrieved {len(df)} sales records from last month")
            return df
        except Exception as e:
            logger.error(f"Error retrieving sales data: {e}")
            # Return sample data for testing
            return self._generate_sample_data()
    
    def _generate_sample_data(self) -> pd.DataFrame:
        """Generate sample sales data for testing"""
        import random
        from datetime import datetime, timedelta
        
        data = []
        campaigns = ['birthday_campaign', 'happy_hour_campaign', 'weather_recommendation_agent', 
                    'social_media_agent', 'personalised_recommendation_agent', 'none']
        
        for i in range(1000):
            date = datetime.now() - timedelta(days=random.randint(0, 30))
            data.append({
                'date': date.date(),
                'hour': date.hour,
                'product_id': f'PROD_{random.randint(1, 100)}',
                'customer_id': f'CUST_{random.randint(1, 500)}',
                'revenue': random.uniform(10, 500),
                'campaign_source': random.choice(campaigns),
                'weather_conditions': random.choice(['sunny', 'rainy', 'cloudy', 'snowy']),
                'customer_birthday': random.choice([True, False])
            })
        
        return pd.DataFrame(data)
    
    def analyze_campaign_performance(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze the performance of each campaign"""
        campaign_performance = {}
        
        for campaign in ['birthday_campaign', 'happy_hour_campaign', 'weather_recommendation_agent', 
                        'social_media_agent', 'personalised_recommendation_agent']:
            campaign_sales = df[df['campaign_source'] == campaign]['revenue'].sum()
            total_sales = df['revenue'].sum()
            performance_score = (campaign_sales / total_sales) * 100 if total_sales > 0 else 0
            campaign_performance[campaign] = performance_score
            
        return campaign_performance
    
    def get_hourly_sales_pattern(self, df: pd.DataFrame) -> Dict[int, float]:
        """Analyze hourly sales patterns"""
        hourly_sales = df.groupby('hour')['revenue'].sum().to_dict()
        return hourly_sales
    
    def get_weather_impact(self, df: pd.DataFrame) -> Dict[str, float]:
        """Analyze weather impact on sales"""
        weather_sales = df.groupby('weather_conditions')['revenue'].mean().to_dict()
        return weather_sales

class CampaignController:
    """Controls the activation/deactivation of campaigns"""
    
    def __init__(self):
        self.campaigns = {
            'birthday_campaign': CampaignStatus('birthday_campaign', False),
            'happy_hour_campaign': CampaignStatus('happy_hour_campaign', False),
            'weather_recommendation_agent': CampaignStatus('weather_recommendation_agent', False),
            'social_media_agent': CampaignStatus('social_media_agent', False),
            'personalised_recommendation_agent': CampaignStatus('personalised_recommendation_agent', False)
        }
    
    def get_campaign_status(self, campaign_name: str = None) -> Dict:
        """Get status of campaigns"""
        if campaign_name:
            campaign = self.campaigns.get(campaign_name)
            if campaign:
                return {
                    'name': campaign.name,
                    'is_active': campaign.is_active,
                    'last_activated': campaign.last_activated.isoformat() if campaign.last_activated else None,
                    'performance_score': campaign.performance_score
                }
            return {'error': 'Campaign not found'}
        
        return {name: {
            'name': campaign.name,
            'is_active': campaign.is_active,
            'last_activated': campaign.last_activated.isoformat() if campaign.last_activated else None,
            'performance_score': campaign.performance_score
        } for name, campaign in self.campaigns.items()}

    def activate_campaign(self, campaign_name: str, merchant_id) -> Dict:
        """Activate a campaign"""
        if campaign_name not in self.campaigns:
            return {'success': False, 'message': f'Campaign {campaign_name} not found'}
        
        try:
            # Execute the campaign script
            # script_path = f"campaigns/{campaign_name}.py"
            # result = subprocess.run([sys.executable, script_path, '--activate'], 
            #                       capture_output=True, text=True, timeout=30)
            #
            db_instance = get_db()
            job_name = campaigns_map[campaign_name]
            if not is_promotion_active(db_instance, str(merchant_id), job_name.replace('-',' ')):
                target_url = f"{endpoints[job_name]['url']}/{merchant_id}" 
                cron = endpoints[job_name]['schedule']
                job_id = f"{job_name}-{merchant_id}"
                result = schedule_job(job_id, target_url, cron)
                job_name = job_name.replace('-',' ')
                insert_active_promotion(db_instance, merchant_id, job_name)

                if result == True:
                    self.campaigns[campaign_name].is_active = True
                    self.campaigns[campaign_name].last_activated = datetime.now()
                    logger.info(f"Activated campaign: {campaign_name}")
                    return {'success': True, 'message': f'Campaign {campaign_name} activated successfully'}
                else:
                    logger.error(f"Failed to activate {campaign_name}: {result.stderr}")
                    return {'success': False, 'message': f'Failed to activate {campaign_name}'}
            else:
                return {'success': True, 'message': f'Campaign {campaign_name} already activated'}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'message': f'Timeout activating {campaign_name}'}
        except Exception as e:
            logger.error(f"Error activating {campaign_name}: {e}")
            return {'success': False, 'message': f'Error activating {campaign_name}: {str(e)}'}
    
    def deactivate_campaign(self, campaign_name: str, merchant_id) -> Dict:
        """Deactivate a campaign"""
        if campaign_name not in self.campaigns:
            return {'success': False, 'message': f'Campaign {campaign_name} not found'}
        
        try:
            # Execute the campaign script to deactivate
            # script_path = f"campaigns/{campaign_name}.py"
            # result = subprocess.run([sys.executable, script_path, '--deactivate'], 
            #                       capture_output=True, text=True, timeout=30)
            db_instance = get_db()
            job_name = campaigns_map[campaign_name]
            job_id = f"{job_name}-{merchant_id}"
            result = delete_job(merchant_id, job_id)
            job_name = job_name.replace('-',' ')
            delete_active_promotion(db_instance, merchant_id, job_name)

            if result == True:
                self.campaigns[campaign_name].is_active = False
                logger.info(f"Deactivated campaign: {campaign_name}")
                return {'success': True, 'message': f'Campaign {campaign_name} deactivated successfully'}
            else:
                logger.error(f"Failed to deactivate {campaign_name}: {result.stderr}")
                return {'success': False, 'message': f'Failed to deactivate {campaign_name}'}
                
        except subprocess.TimeoutExpired:
            return {'success': False, 'message': f'Timeout deactivating {campaign_name}'}
        except Exception as e:
            logger.error(f"Error deactivating {campaign_name}: {e}")
            return {'success': False, 'message': f'Error deactivating {campaign_name}: {str(e)}'}

class CampaignOptimizationAgent:
    """LLM-based agent for campaign optimization"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        self.sales_analyzer = SalesDataAnalyzer(project_id)
        self.campaign_controller = CampaignController()
        # Initialize Vertex AI LLM
        self.llm = ChatVertexAI(
            model_name="gemini-2.5-pro",
            project=project_id,
            location=location,
            temperature=0.1
        )
        
        # Create tools for the agent
        self.tools = self._create_tools()
        
        # Create the agent
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the LangChain agent"""
        
        def get_sales_data(input_str: str) -> str:
            """Get and analyze sales data from the last month"""
            df = self.sales_analyzer.get_last_month_sales_data()
            campaign_performance = self.sales_analyzer.analyze_campaign_performance(df)
            hourly_patterns = self.sales_analyzer.get_hourly_sales_pattern(df)
            weather_impact = self.sales_analyzer.get_weather_impact(df)
            
            analysis = {
                'total_records': len(df),
                'total_revenue': df['revenue'].sum(),
                'campaign_performance': campaign_performance,
                'hourly_sales_pattern': hourly_patterns,
                'weather_impact': weather_impact,
                'best_performing_hour': max(hourly_patterns.keys(), key=lambda k: hourly_patterns[k]),
                'worst_performing_hour': min(hourly_patterns.keys(), key=lambda k: hourly_patterns[k])
            }
            
            return json.dumps(analysis, indent=2)
        
        def get_campaign_status(campaign_name: str) -> str:
            """Get current status of campaigns"""
            if campaign_name.strip():
                status = self.campaign_controller.get_campaign_status(campaign_name.strip())
            else:
                status = self.campaign_controller.get_campaign_status()
            return json.dumps(status, indent=2)
        
        def get_current_context(input_str: str) -> str:
            """Get current context including time, day, and other relevant factors"""
            now = datetime.now()
            context = {
                'current_time': now.isoformat(),
                'hour': now.hour,
                'day_of_week': now.strftime('%A'),
                'date': now.strftime('%Y-%m-%d'),
                'is_weekend': now.weekday() >= 5,
                'season': 'winter' if now.month in [12, 1, 2] else 'spring' if now.month in [3, 4, 5] 
                         else 'summer' if now.month in [6, 7, 8] else 'fall'
            }
            return json.dumps(context, indent=2)
        
        return [
            Tool(
                name="get_sales_data",
                description="Analyze sales data from the last month including campaign performance, hourly patterns, and weather impact",
                func=get_sales_data
            ),
            Tool(
                name="get_campaign_status",
                description="Get current status of campaigns. Pass campaign name or leave empty for all campaigns",
                func=get_campaign_status
            ),
            Tool(
                name="get_current_context",
                description="Get current time, date, and contextual information",
                func=get_current_context
            )
        ]
    
    def _create_agent(self):
        """Create the LangChain agent"""
        system_prompt = """You are a Campaign Optimization AI Agent for an e-commerce business. Your role is to analyze sales data and recommend the optimal combination of marketing campaigns to activate or deactivate.

Available campaigns:
1. birthday_campaign: Sends discount to customers on their birthday
2. happy_hour_campaign: Activates discounts during low-sales hours
3. weather_recommendation_agent: Recommends products based on weather
4. social_media_agent: Posts on social media for best/worst selling products
5. personalised_recommendation_agent: Sends personalized recommendations based on purchase history

Your task is to:
1. Analyze the last month's sales data using the available tools
2. Consider current context (time, day, season, etc.)
3. Check current campaign status
4. Provide TWO TO THREE RECOMMENDATIONS about which campaigns to activate/deactivate and when
5. Explain your reasoning based on the data analysis

Important guidelines:
- Make data-driven decisions based on campaign performance
- Consider timing and context for recommendations
- Avoid overwhelming customers with too many active campaigns simultaneously
- Focus on maximizing ROI and customer experience
- Provide clear reasoning for your recommendations

Make your recommendation in this format:
**RECOMMENDATION:**
- Action: [Activate/Deactivate] [campaign_name(s)]
- Timing: [When to implement]
- Reasoning: [Data-based explanation]
- Expected Impact: [Predicted outcome]"""

        # prompt = ChatPromptTemplate.from_messages([
        #     SystemMessage(content=system_prompt),
        #     ("human", "{input}"),
        #     MessagesPlaceholder(variable_name="agent_scratchpad"),
        #     ("assistant", "I'll analyze the current situation and provide a recommendation. Let me gather the necessary data first."),
        #     ("human", "Please use the available tools to analyze sales data, check campaign status, and current context, then provide your recommendation.")
        # ])

        
        # agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        prompt = ChatPromptTemplate.from_messages([
                        ("system", system_prompt),
                        ("human", "{input}"), 
                        MessagesPlaceholder(variable_name="agent_scratchpad"),       
                        ])        
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True, max_iterations=5)
    
    def get_recommendation(self) -> str:
        """Get campaign optimization recommendation from the LLM agent"""
        try:
            result = self.agent.invoke({
                "input": "Analyze current sales data and campaign performance, then provide one specific recommendation for campaign optimization."
            })
            return result['output']
        except Exception as e:
            logger.error(f"Error getting recommendation: {e}")
            return f"Error generating recommendation: {str(e)}"
    
    def implement_recommendation(self, recommendation: str, approved: bool, merchant_id) -> Dict:
        """Implement the approved recommendation"""
        if not approved:
            return {'status': 'declined', 'message': 'Recommendation declined by user'}
        
        # Parse the recommendation to extract actions
        # This is a simplified implementation - in practice, you might want more sophisticated parsing
        actions_taken = []
        
        try:
            lines = recommendation.split('\n')
            for line in lines:
                if 'Activate' in line:
                    campaign_name = self._extract_campaign_name(line)
                    if campaign_name:
                        result = self.campaign_controller.activate_campaign(campaign_name, merchant_id)
                        actions_taken.append(f"Activated {campaign_name}: {result['message']}")
                elif 'Deactivate' in line:
                    campaign_name = self._extract_campaign_name(line)
                    if campaign_name:
                        result = self.campaign_controller.deactivate_campaign(campaign_name, merchant_id)
                        actions_taken.append(f"Deactivated {campaign_name}: {result['message']}")
            
            return {
                'status': 'implemented',
                'actions_taken': actions_taken,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error implementing recommendation: {e}")
            return {
                'status': 'error',
                'message': f'Failed to implement recommendation: {str(e)}'
            }
    
    def _extract_campaign_name(self, text: str) -> str:
        """Extract campaign name from text"""
        campaigns = ['birthday_campaign', 'happy_hour_campaign', 'weather_recommendation_agent', 
                    'social_media_agent', 'personalised_recommendation_agent']
        
        for campaign in campaigns:
            if campaign in text:
                return campaign
        return None

def campaign_optimizer(merchant_id):
    """Main function to run the campaign optimization agent"""
    # Load environment variables
    project_id = os.getenv('PROJECT_ID')
    location = os.getenv('LOCATION', 'us-central1')
    
    if not project_id:
        logger.error("GCP_PROJECT_ID not found in environment variables")
        return
    
    # Initialize the agent
    agent = CampaignOptimizationAgent(project_id, location)
    
    print("🤖 Campaign Optimization AI Agent")
    print("=" * 50)
    
    # Get recommendation
    print("\n📊 Analyzing sales data and generating recommendation...")
    recommendation = agent.get_recommendation()
    
    print("\n💡 RECOMMENDATION:")
    print("-" * 30)
    print(recommendation)
    
    # Get user approval
    print("\n" + "=" * 50)
    # user_input = input("Do you approve this recommendation? (y/n): ").strip().lower()
    
    # approved = user_input in ['y', 'yes']
    approved = True
    
    # Implement recommendation
    print("\n🔄 Processing your decision...")
    result = agent.implement_recommendation(recommendation, approved, merchant_id)
    
    print(f"\n📋 Status: {result['status'].upper()}")
    if 'actions_taken' in result:
        print("Actions taken:")
        for action in result['actions_taken']:
            print(f"  ✓ {action}")
    elif 'message' in result:
        print(f"Message: {result['message']}")