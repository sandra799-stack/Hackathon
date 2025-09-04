#!/usr/bin/env python3
"""
Weather-Based Product Recommendation System with GCP and Gemini
Fetches weather data, recommends products, and generates customer notifications
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_products_by_merchant_id

# Google Cloud and LangChain imports
import vertexai
from vertexai.generative_models import GenerativeModel
from langchain_google_vertexai import ChatVertexAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from google.oauth2 import service_account


@dataclass
class WeatherData:
    """Weather data structure"""
    temperature: float
    condition: str
    humidity: int
    wind_speed: float
    location: str
    date: str


@dataclass
class ProductRecommendation:
    """Product recommendation structure"""
    products: List[str]
    reasoning: str


class WeatherProductRecommender:
    def __init__(self, project_id: str, location: str, debug: bool):
        """
        Initialize the recommender with GCP project settings
        
        Args:
            project_id: GCP project ID
            location: GCP region for Vertex AI
            debug: Enable debug output for troubleshooting
        """
        # Load environment variables
        load_dotenv()
        
        self.project_id = project_id
        self.location = location
        self.debug = debug
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Initialize LangChain with Gemini
        self.llm = ChatVertexAI(
            model_name="gemini-2.5-pro",
            project=project_id,
            location=location,
            temperature=0.3,  # Lower temperature for more consistent JSON output
        )
    
    def get_weather_data(self, city: str) -> WeatherData:
        """
        Fetch current weather data from OpenWeatherMap API
        
        Args:
            city: City name for weather lookup
            
        Returns:
            WeatherData object with current weather information
        """
        try:
            # Get API key from environment variable
            api_key = os.getenv("OPENWEATHER_API_KEY")
            if not api_key:
                raise ValueError("OPENWEATHER_API_KEY not found in environment variables")
            
            # OpenWeatherMap API endpoint
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": city,
                "appid": api_key,
                "units": "metric"  # Use Celsius
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return WeatherData(
                temperature=data["main"]["temp"],
                condition=data["weather"][0]["description"],
                humidity=data["main"]["humidity"],
                wind_speed=data["wind"]["speed"],
                location=f"{data['name']}, {data['sys']['country']}",
                date=datetime.now().strftime("%Y-%m-%d")
            )
            
        except requests.RequestException as e:
            print(f"Error fetching weather data: {e}")
            # Fallback weather data for demo purposes
            return WeatherData(
                temperature=22.0,
                condition="partly cloudy",
                humidity=65,
                wind_speed=3.2,
                location=city,
                date=datetime.now().strftime("%Y-%m-%d")
            )
    
    def recommend_products(self, weather: WeatherData, input_products: List[str]) -> ProductRecommendation:
        """
        Use Gemini LLM to recommend products based on weather conditions
        
        Args:
            weather: Current weather data
            input_products: List of available products
            
        Returns:
            ProductRecommendation with selected products and reasoning
        """
        # Create prompt template for product recommendation
        recommendation_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are an expert product recommendation system. 
            Based on the current weather conditions, recommend the most suitable products 
            from the given list. Consider temperature, weather conditions, humidity, and 
            wind speed when making recommendations.
            
            You MUST respond with ONLY valid JSON in exactly this format, with no additional text:
            {
                "recommended_products": ["product1", "product2", "product3"],
                "reasoning": "Brief explanation of why these products are recommended"
            }
            
            Only recommend products that are exactly as listed in the available products."""),
            
            HumanMessage(content=f"""
            Current Weather:
            - Location: {weather.location}
            - Temperature: {weather.temperature}°C
            - Condition: {weather.condition}
            - Humidity: {weather.humidity}%
            - Wind Speed: {weather.wind_speed} m/s
            - Date: {weather.date}
            
            Available Products:
            {', '.join(input_products)}
            
            Recommend 2-4 products that would be most relevant for these weather conditions. Respond with JSON only.
            """)
        ])
        
        try:
            # Get recommendation from Gemini
            response = self.llm.invoke(recommendation_prompt.format_messages())
            
            # Clean the response content
            content = response.content.strip()
            if self.debug:
                print(f"Raw LLM response: {content}")  # Debug output
            
            # Try to extract JSON from the response if it's wrapped in markdown or other text
            if "```json" in content:
                # Extract JSON from markdown code block
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                # Extract from generic code block
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            # Find JSON object bounds if response has extra text
            if content.find("{") != -1 and content.find("}") != -1:
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                content = content[json_start:json_end]
            
            if self.debug:
                print(f"Cleaned JSON: {content}")  # Debug output
            
            # Parse JSON response
            recommendation_data = json.loads(content)
            
            # Validate that recommended products are in the input list
            valid_products = []
            for product in recommendation_data["recommended_products"]:
                if product in input_products:
                    valid_products.append(product)
                else:
                    # Try to find close matches
                    for available_product in input_products:
                        if product.lower() in available_product.lower() or available_product.lower() in product.lower():
                            valid_products.append(available_product)
                            break
            
            # If no valid products found, use first few from input
            if not valid_products:
                valid_products = input_products[:3]
            
            return ProductRecommendation(
                products=valid_products,
                reasoning=recommendation_data.get("reasoning", "Weather-based recommendation")
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Response content was: {response.content if 'response' in locals() else 'No response'}")
            
            # Fallback recommendation based on weather
            if weather.temperature < 10:
                fallback_products = [p for p in input_products if any(word in p.lower() for word in ['winter', 'coat', 'sweater', 'thermal'])]
            elif weather.temperature > 25:
                fallback_products = [p for p in input_products if any(word in p.lower() for word in ['shorts', 'sunglasses', 'hat', 't-shirt'])]
            elif 'rain' in weather.condition.lower():
                fallback_products = [p for p in input_products if any(word in p.lower() for word in ['umbrella', 'rain', 'waterproof'])]
            else:
                fallback_products = input_products[:2]
            
            return ProductRecommendation(
                products=fallback_products[:3] if fallback_products else input_products[:3],
                reasoning=f"Weather-based fallback recommendation for {weather.condition}, {weather.temperature}°C"
            )
    
    def generate_notification_message(self, weather: WeatherData, 
                                    recommended_products: List[str]) -> str:
        """
        Use Gemini LLM to generate customer notification message
        
        Args:
            weather: Current weather data
            recommended_products: List of recommended products
            
        Returns:
            Customer notification message as string
        """
        # Create prompt template for notification generation
        notification_prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content="""You are a creative marketing copywriter. 
            Create an engaging customer notification message about free delivery 
            on weather-appropriate products. ONLY include the notification message in your response. The message should be:
            - Friendly and conversational
            - Weather-aware and contextual
            - Include urgency (limited time offer)
            - Mention the free delivery benefit
            - Be concise but compelling (2-3 sentences max)
            - Include relevant weather emoji if appropriate"""),
            
            HumanMessage(content=f"""
            Current Weather: {weather.condition}, {weather.temperature}°C in {weather.location}
            Recommended Products: {', '.join(recommended_products)}
    
            Create a raw JSON only containing a customer notification message about free delivery on these recommended products and a subject.
            """)
        ])
        
        try:
            # Generate notification with Gemini
            response = self.llm.invoke(notification_prompt.format_messages())
            return response.content.strip()
            
        except Exception as e:
            print(f"Error generating notification: {e}")
            return f"🌤️ Perfect weather for {', '.join(recommended_products)}! Get FREE delivery on these items today only. Order now!"
    
    def run_recommendation_pipeline(self, city: str, input_products: List[str]) -> Dict[str, Any]:
        """
        Run the complete recommendation pipeline
        
        Args:
            city: City for weather lookup
            input_products: Available products list
            
        Returns:
            Dictionary with weather, recommendations, and notification
        """
        print(f"🌍 Starting weather-based product recommendation for {city}...")
        
        # Step 1: Get weather data
        print("☁️ Fetching weather data...")
        weather = self.get_weather_data(city)
        print(f"Weather: {weather.condition}, {weather.temperature}°C")
        
        # Step 2: Get product recommendations
        print("🤖 Generating product recommendations...")
        recommendations = self.recommend_products(weather, input_products)
        print(f"Recommended: {', '.join(recommendations.products)}")
        
        # Step 3: Generate notification message
        print("📱 Creating customer notification...")
        notification = self.generate_notification_message(weather, recommendations.products)
        
        # Compile results
        results = {
            "weather": {
                "location": weather.location,
                "temperature": weather.temperature,
                "condition": weather.condition,
                "humidity": weather.humidity,
                "wind_speed": weather.wind_speed,
                "date": weather.date
            },
            "recommendations": {
                "products": recommendations.products,
                "reasoning": recommendations.reasoning
            },
            "notification_message": notification,
            "timestamp": datetime.now().isoformat()
        }
        
        print("\n✅ Pipeline completed successfully!")
        return results


def recommend_products_by_weather(merchant_id):
    """
    Main execution function - example usage
    """
    # Configuration - get project ID from environment or use default
    PROJECT_ID = os.getenv("PROJECT_ID", "your-gcp-project-id")
    LOCATION_ID = os.getenv("LOCATION_ID", "your-gcp-location-id")
    DEBUG = "True"
    CITY = os.getenv("CITY", "London")  # City for weather lookup
    
    INPUT_PRODUCTS = get_products_by_merchant_id(merchant_id)
    try:
        # Initialize the recommender system
        recommender = WeatherProductRecommender(PROJECT_ID, LOCATION_ID, DEBUG)
        
        # Run the recommendation pipeline
        results = recommender.run_recommendation_pipeline(CITY, INPUT_PRODUCTS)
        
        # Display results
        print("\n" + "="*60)
        print("🎯 RECOMMENDATION RESULTS")
        print("="*60)
        
        print(f"\n📍 Location: {results['weather']['location']}")
        print(f"🌡️ Temperature: {results['weather']['temperature']}°C")
        print(f"☁️ Condition: {results['weather']['condition']}")
        print(f"💧 Humidity: {results['weather']['humidity']}%")
        print(f"💨 Wind Speed: {results['weather']['wind_speed']} m/s")
        
        print(f"\n🛍️ Recommended Products:")
        for product in results['recommendations']['products']:
            print(f"   • {product}")
        
        print(f"\n🧠 Reasoning: {results['recommendations']['reasoning']}")
        
        print(f"\n📱 Customer Notification:")
        print(f"   {results['notification_message']}")
        
        # Save results to JSON file
        # output_file = f"weather_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        # with open(output_file, 'w') as f:
        #     json.dump(results, f, indent=2)
        # print(f"\n💾 Results saved to: {output_file}")
        return results["notification_message"]
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        raise


def validate_environment():
    """
    Validate that all required environment variables are configured
    """
    load_dotenv()
    
    required_env_vars = ["OPENWEATHER_API_KEY", "PROJECT_ID"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file with the following variables:")
        print("KEY_PATH=path/to/service-account-key.json")
        print("OPENWEATHER_API_KEY=your_openweather_api_key")
        print("GCP_PROJECT_ID=your-gcp-project-id")
        print("CITY=London  # Optional, defaults to London")
        return False
    
    return True


if __name__ == "__main__":
    # Validate environment before running
    if validate_environment():
        recommend_products_by_weather(94025)
    else:
        print("❌ Environment validation failed. Please configure your .env file.")


"""
INSTALLATION REQUIREMENTS:
pip install google-cloud-aiplatform
pip install langchain-google-vertexai
pip install langchain
pip install requests
pip install vertexai
pip install python-dotenv

SETUP INSTRUCTIONS:

1. Create a .env file in your project root with the following content:
   
   # .env file
   KEY_PATH=path/to/your/service-account-key.json
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   GCP_PROJECT_ID=your-gcp-project-id
   CITY=London

2. Enable Required GCP APIs:
   - Vertex AI API
   
3. Create Service Account:
   gcloud iam service-accounts create weather-recommender
   
4. Grant Required Permissions:
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
     --member="serviceAccount:weather-recommender@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/aiplatform.user"

5. Create and Download Service Account Key:
   gcloud iam service-accounts keys create key.json \
     --iam-account=weather-recommender@YOUR_PROJECT_ID.iam.gserviceaccount.com

6. Get OpenWeatherMap API Key:
   - Sign up at https://openweathermap.org/api
   - Get free API key from your account dashboard

USAGE EXAMPLE:

from weather_product_recommender import WeatherProductRecommender
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize
recommender = WeatherProductRecommender(os.getenv("GCP_PROJECT_ID"))

# Define your product catalog
products = ["Winter Jacket", "Sunscreen", "Umbrella", "Shorts", "Rain Boots"]

# Run recommendation pipeline
results = recommender.run_recommendation_pipeline("New York", products)

# Access results
print("Recommended Products:", results['recommendations']['products'])
print("Notification:", results['notification_message'])
"""