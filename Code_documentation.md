
# Weather-Based Product Recommendation System Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Installation & Setup](#installation--setup)
5. [Configuration](#configuration)
6. [Core Components](#core-components)
7. [API Reference](#api-reference)
8. [Usage Examples](#usage-examples)
9. [Weather Strategy Logic](#weather-strategy-logic)
10. [Deployment](#deployment)
11. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
12. [Performance Optimization](#performance-optimization)

## 📖 Overview

The Weather-Based Product Recommendation System is an intelligent AI solution that automatically recommends products to customers based on real-time weather conditions. This "set it and forget it" system continuously monitors weather data and generates personalized product recommendations with compelling notification messages, perfect for SMEs looking to boost sales through contextual marketing.

### Key Features
- **Real-Time Weather Integration**: Uses OpenWeatherMap API for current conditions
- **AI-Powered Recommendations**: Google Gemini 2.5 Pro for intelligent product selection
- **Contextual Marketing**: Weather-aware customer notifications
- **Autonomous Operation**: Runs continuously without manual intervention
- **Fallback Intelligence**: Robust error handling with smart defaults
- **Multi-Location Support**: Configurable for different geographic markets

### Business Benefits
- **Increase Relevance**: Products matched to immediate weather needs
- **Boost Conversion Rates**: Contextual recommendations drive higher purchase intent
- **Automated Marketing**: Weather-triggered campaigns without manual oversight
- **Seasonal Optimization**: Automatic adjustment to weather patterns
- **Customer Engagement**: Timely, relevant communications improve brand perception

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│ OpenWeatherMap  │───▶│   Weather    │───▶│   AI Product    │
│     API         │    │ Data Parser  │    │ Recommendation  │
│ (Real-time)     │    │              │    │    Engine       │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                     │
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│  Product        │───▶│   Context    │◀───│ Gemini 2.5 Pro  │
│  Database       │    │  Matching    │    │     LLM         │
│ (Merchant SKUs) │    │   Logic      │    │                 │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                     │
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Customer      │◀───│ Notification │◀───│   Message       │
│ Notifications   │    │  Delivery    │    │  Generation     │
│ (Email/SMS)     │    │   System     │    │                 │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

## 🔧 Prerequisites

### System Requirements
- Python 3.8 or higher
- Google Cloud Platform account with Vertex AI enabled
- OpenWeatherMap API account (free tier available)
- Internet connectivity for real-time weather data

### Required APIs & Services
- **OpenWeatherMap API**: Current weather data
- **Google Vertex AI**: Gemini LLM access
- **Google Cloud Storage**: Optional for logging/analytics
- **Database Access**: Product catalog retrieval

### API Limits & Considerations
- **OpenWeatherMap Free Tier**: 1,000 calls/day, 60 calls/minute
- **Vertex AI**: Pay-per-use pricing for Gemini API calls
- **Rate Limiting**: Built-in exponential backoff for API reliability

## 📦 Installation & Setup

### 1. Environment Setup

```bash
# Create project directory
mkdir weather-recommendation-system
cd weather-recommendation-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Dependencies (requirements.txt)

```text
# Core Dependencies
requests>=2.28.0
python-dotenv>=0.19.0

# Google Cloud Platform
google-cloud-aiplatform>=1.0.0
vertexai>=1.0.0
google-auth>=2.15.0
google-oauth2>=2.15.0

# LangChain & AI
langchain>=0.1.0
langchain-google-vertexai>=0.1.0

# Data Processing
dataclasses  # Built-in for Python 3.7+
typing       # Built-in for Python 3.5+
json         # Built-in
datetime     # Built-in
```

### 3. Service Account Setup

```bash
# Create service account for weather recommender
gcloud iam service-accounts create weather-recommender \
    --display-name="Weather Product Recommender"

# Grant Vertex AI permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:weather-recommender@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Generate and download service account key
gcloud iam service-accounts keys create weather-service-key.json \
    --iam-account=weather-recommender@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### 4. OpenWeatherMap API Setup

1. **Create Account**: Visit [openweathermap.org/api](https://openweathermap.org/api)
2. **Get API Key**: Sign up for free tier (1,000 calls/day)
3. **Verify Access**: Test API key with sample request

```bash
# Test OpenWeatherMap API
curl "http://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_API_KEY&units=metric"
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Google Cloud Configuration
PROJECT_ID=your-gcp-project-id
LOCATION_ID=us-central1
KEY_PATH=./weather-service-key.json

# OpenWeatherMap Configuration
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Application Settings
CITY=London                    # Default city for weather lookup
DEBUG=True                     # Enable debug output
TEMPERATURE_UNIT=metric        # metric, imperial, or standard

# AI Configuration
MODEL_TEMPERATURE=0.3          # LLM temperature (0.0-1.0)
MAX_RECOMMENDATIONS=4          # Maximum products to recommend
MIN_RECOMMENDATIONS=2          # Minimum products to recommend

# Weather Thresholds (Celsius)
COLD_THRESHOLD=10             # Below this = cold weather products
HOT_THRESHOLD=25              # Above this = hot weather products
HIGH_HUMIDITY_THRESHOLD=80    # Above this = humidity-related products

# Notification Settings
ENABLE_NOTIFICATIONS=True
NOTIFICATION_LANGUAGE=en
INCLUDE_WEATHER_EMOJI=True

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=weather_recommendations.log
SAVE_RESULTS_TO_FILE=False    # Save JSON results to files
```

### Configuration Validation

```python
def validate_environment():
    """Validate all required environment variables"""
    load_dotenv()
    
    required_vars = {
        "KEY_PATH": "Path to GCP service account key",
        "OPENWEATHER_API_KEY": "OpenWeatherMap API key", 
        "PROJECT_ID": "Google Cloud Project ID"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        return False
    
    return True
```

## 🔧 Core Components

### 1. Data Models

#### WeatherData
```python
@dataclass
class WeatherData:
    """Comprehensive weather information"""
    temperature: float      # Temperature in configured units
    condition: str         # Weather condition description
    humidity: int          # Humidity percentage (0-100)
    wind_speed: float      # Wind speed in m/s
    location: str          # City, Country format
    date: str             # Date in YYYY-MM-DD format
    
    @property
    def is_cold(self) -> bool:
        """Check if weather is considered cold"""
        return self.temperature < float(os.getenv("COLD_THRESHOLD", 10))
    
    @property  
    def is_hot(self) -> bool:
        """Check if weather is considered hot"""
        return self.temperature > float(os.getenv("HOT_THRESHOLD", 25))
    
    @property
    def is_humid(self) -> bool:
        """Check if humidity is high"""
        return self.humidity > int(os.getenv("HIGH_HUMIDITY_THRESHOLD", 80))
    
    @property
    def is_rainy(self) -> bool:
        """Check if conditions are rainy"""
        rain_keywords = ['rain', 'drizzle', 'shower', 'thunderstorm']
        return any(keyword in self.condition.lower() for keyword in rain_keywords)
```

#### ProductRecommendation
```python
@dataclass
class ProductRecommendation:
    """AI-generated product recommendations"""
    products: List[str]    # List of recommended product names
    reasoning: str         # AI explanation for recommendations
    confidence: float = 0.8  # Confidence score (0.0-1.0)
    weather_context: str = ""  # Weather context used
    
    def __post_init__(self):
        """Validate and clean recommendations"""
        # Remove duplicates while preserving order
        seen = set()
        self.products = [x for x in self.products if not (x in seen or seen.add(x))]
        
        # Limit to max recommendations
        max_recs = int(os.getenv("MAX_RECOMMENDATIONS", 4))
        self.products = self.products[:max_recs]
```

### 2. Weather Data Service

#### WeatherProductRecommender Class

```python
class WeatherProductRecommender:
    """Main recommendation engine"""
    
    def __init__(self, project_id: str, location: str, debug: bool = False):
        """
        Initialize the recommendation system
        
        Args:
            project_id: GCP project ID for Vertex AI
            location: GCP region (e.g., 'us-central1')
            debug: Enable detailed logging and debug output
        """
        self.project_id = project_id
        self.location = location
        self.debug = debug
        
        # Load configuration
        load_dotenv()
        
        # Initialize AI services
        self._setup_vertex_ai()
        self._setup_langchain()
    
    def _setup_vertex_ai(self):
        """Initialize Vertex AI with service account credentials"""
        key_path = os.getenv("KEY_PATH")
        if not key_path or not os.path.exists(key_path):
            raise FileNotFoundError(f"Service account key not found at: {key_path}")
        
        credentials = service_account.Credentials.from_service_account_file(key_path)
        vertexai.init(project=self.project_id, location=self.location)
        self.credentials = credentials
    
    def _setup_langchain(self):
        """Initialize LangChain with Gemini model"""
        self.llm = ChatVertexAI(
            model_name="gemini-2.5-pro",
            project=self.project_id,
            location=self.location,
            temperature=float(os.getenv("MODEL_TEMPERATURE", 0.3)),
            credentials=self.credentials
        )
```

### 3. Weather Data Retrieval

#### `get_weather_data(city: str) -> WeatherData`

```python
def get_weather_data(self, city: str) -> WeatherData:
    """
    Fetch real-time weather data from OpenWeatherMap
    
    Args:
        city: City name (e.g., 'London', 'New York')
        
    Returns:
        WeatherData object with current conditions
        
    Raises:
        requests.RequestException: If API call fails
        ValueError: If API key is missing
    """
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            raise ValueError("OPENWEATHER_API_KEY not found in environment")
        
        # Build API request
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": os.getenv("TEMPERATURE_UNIT", "metric")
        }
        
        # Make API call with timeout
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse response into WeatherData object
        return WeatherData(
            temperature=data["main"]["temp"],
            condition=data["weather"][0]["description"],
            humidity=data["main"]["humidity"],
            wind_speed=data["wind"]["speed"],
            location=f"{data['name']}, {data['sys']['country']}",
            date=datetime.now().strftime("%Y-%m-%d")
        )
        
    except requests.RequestException as e:
        if self.debug:
            print(f"Weather API error: {e}")
        
        # Return fallback weather data for demo/testing
        return self._get_fallback_weather(city)
    
def _get_fallback_weather(self, city: str) -> WeatherData:
    """Provide fallback weather data when API is unavailable"""
    return WeatherData(
        temperature=22.0,
        condition="partly cloudy",
        humidity=65,
        wind_speed=3.2,
        location=city,
        date=datetime.now().strftime("%Y-%m-%d")
    )
```

### 4. AI-Powered Product Recommendation

#### `recommend_products(weather: WeatherData, products: List[str]) -> ProductRecommendation`

```python
def recommend_products(self, weather: WeatherData, input_products: List[str]) -> ProductRecommendation:
    """
    Generate intelligent product recommendations based on weather
    
    Args:
        weather: Current weather data
        input_products: Available product catalog
        
    Returns:
        ProductRecommendation with selected products and reasoning
        
    Process:
        1. Create weather-aware prompt for Gemini
        2. Request structured JSON response
        3. Validate recommended products against catalog
        4. Implement fallback logic for edge cases
    """
    
    # Create sophisticated prompt template
    recommendation_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=self._get_system_prompt()),
        HumanMessage(content=self._build_recommendation_context(weather, input_products))
    ])
    
    try:
        # Get AI recommendation
        response = self.llm.invoke(recommendation_prompt.format_messages())
        
        # Parse and validate JSON response
        recommendation_data = self._parse_llm_response(response.content)
        
        # Validate products exist in catalog
        valid_products = self._validate_product_recommendations(
            recommendation_data["recommended_products"], 
            input_products
        )
        
        return ProductRecommendation(
            products=valid_products,
            reasoning=recommendation_data.get("reasoning", "Weather-based AI recommendation"),
            confidence=0.9,
            weather_context=f"{weather.condition}, {weather.temperature}°C"
        )
        
    except Exception as e:
        if self.debug:
            print(f"AI recommendation error: {e}")
        
        # Intelligent fallback based on weather conditions
        return self._generate_fallback_recommendation(weather, input_products)

def _get_system_prompt(self) -> str:
    """Generate comprehensive system prompt for product recommendations"""
    return """You are an expert product recommendation AI specializing in weather-based suggestions.
    
    TASK: Recommend 2-4 products that are most relevant for the current weather conditions.
    
    WEATHER ANALYSIS GUIDELINES:
    - Cold weather (< 10°C): Focus on warming items, outerwear, hot beverages
    - Hot weather (> 25°C): Emphasize cooling items, sun protection, cold beverages  
    - Rainy conditions: Prioritize waterproof items, umbrellas, indoor activities
    - High humidity (> 80%): Consider comfort items, breathable materials
    - Windy conditions: Suggest wind-resistant or indoor alternatives
    
    OUTPUT FORMAT: Respond with ONLY valid JSON, no additional text:
    {
        "recommended_products": ["exact_product_name_1", "exact_product_name_2"],
        "reasoning": "Brief explanation focusing on weather relevance"
    }
    
    REQUIREMENTS:
    - Use EXACT product names from the provided catalog
    - Prioritize weather relevance over popularity
    - Provide concise, logical reasoning
    - Recommend 2-4 products maximum"""

def _build_recommendation_context(self, weather: WeatherData, products: List[str]) -> str:
    """Build detailed context for AI recommendation"""
    return f"""
    CURRENT WEATHER CONDITIONS:
    Location: {weather.location}
    Temperature: {weather.temperature}°C
    Condition: {weather.condition}
    Humidity: {weather.humidity}%
    Wind Speed: {weather.wind_speed} m/s
    Date: {weather.date}
    
    AVAILABLE PRODUCTS:
    {', '.join(products)}
    
    WEATHER ANALYSIS:
    - Temperature Category: {'Cold' if weather.is_cold else 'Hot' if weather.is_hot else 'Moderate'}
    - Precipitation: {'Yes' if weather.is_rainy else 'No'}
    - Humidity Level: {'High' if weather.is_humid else 'Normal'}
    
    Please recommend the most weather-appropriate products with clear reasoning.
    """
```

### 5. Notification Message Generation

#### `generate_notification_message(weather: WeatherData, products: List[str]) -> str`

```python
def generate_notification_message(self, weather: WeatherData, 
                                recommended_products: List[str]) -> str:
    """
    Create compelling customer notification message
    
    Args:
        weather: Current weather conditions
        recommended_products: AI-selected product list
        
    Returns:
        Customer-ready notification message with weather context
    """
    
    notification_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content="""You are a creative marketing copywriter specializing in weather-based promotions.
        
        CREATE: An engaging customer notification about FREE DELIVERY on weather-appropriate products.
        
        REQUIREMENTS:
        - Friendly, conversational tone
        - Weather-aware and contextual
        - Include urgency (limited time offer)
        - Mention FREE DELIVERY benefit clearly
        - 2-3 sentences maximum
        - Include relevant weather emoji
        - Focus on customer benefit and relevance
        
        AVOID:
        - Generic promotional language
        - Overly salesy tone
        - Long explanations
        - Irrelevant weather details
        
        RETURN: Only the notification message text, nothing else."""),
        
        HumanMessage(content=f"""
        Weather: {weather.condition}, {weather.temperature}°C in {weather.location}
        Recommended Products: {', '.join(recommended_products)}
        
        Create a weather-contextual notification message about FREE DELIVERY on these recommended products.
        """)
    ])
    
    try:
        response = self.llm.invoke(notification_prompt.format_messages())
        message = response.content.strip()
        
        # Clean up any JSON formatting if present
        if message.startswith('{') and message.endswith('}'):
            try:
                parsed = json.loads(message)
                message = parsed.get('message', parsed.get('notification', message))
            except:
                pass  # Use original message if JSON parsing fails
        
        return message
        
    except Exception as e:
        if self.debug:
            print(f"Notification generation error: {e}")
        
        # Fallback notification template
        return self._generate_fallback_notification(weather, recommended_products)

def _generate_fallback_notification(self, weather: WeatherData, products: List[str]) -> str:
    """Generate fallback notification when AI service fails"""
    
    weather_emoji = self._get_weather_emoji(weather)
    product_list = ', '.join(products[:2])  # Limit to first 2 products
    
    if weather.is_cold:
        return f"{weather_emoji} Brrr! {weather.temperature}°C calls for {product_list}! FREE delivery today only - stay cozy! ❄️"
    elif weather.is_hot:
        return f"{weather_emoji} Beat the heat at {weather.temperature}°C! Get {product_list} with FREE delivery. Limited time! 🌞"
    elif weather.is_rainy:
        return f"{weather_emoji} Rainy day essentials! {product_list} with FREE delivery - perfect for {weather.condition}! ☔"
    else:
        return f"{weather_emoji} Perfect weather for {product_list}! FREE delivery on these items today only. Order now! 🚚"

def _get_weather_emoji(self, weather: WeatherData) -> str:
    """Get appropriate emoji for weather conditions"""
    condition_lower = weather.condition.lower()
    
    if 'clear' in condition_lower or 'sunny' in condition_lower:
        return '☀️'
    elif 'rain' in condition_lower or 'drizzle' in condition_lower:
        return '🌧️'
    elif 'snow' in condition_lower:
        return '❄️'  
    elif 'cloud' in condition_lower:
        return '☁️'
    elif 'thunder' in condition_lower:
        return '⛈️'
    else:
        return '🌤️'
```

## 📚 API Reference

### Main Functions

#### `recommend_products_by_weather(merchant_id: str) -> str`
Main entry point for weather-based recommendations.

```python
def recommend_products_by_weather(merchant_id: str) -> str:
    """
    Execute complete weather-based recommendation pipeline
    
    Args:
        merchant_id: Unique merchant identifier for product catalog lookup
        
    Returns:
        str: Generated customer notification message
        
    Process:
        1. Load merchant product catalog from database
        2. Fetch current weather data for configured city
        3. Generate AI-powered product recommendations  
        4. Create customer notification message
        5. Return notification for delivery system integration
        
    Environment Dependencies:
        - PROJECT_ID: GCP project for Vertex AI
        - LOCATION_ID: GCP region
        - CITY: Target city for weather lookup
        - All authentication and API keys
    """
```

#### `run_recommendation_pipeline(city: str, products: List[str]) -> Dict[str, Any]`
Core pipeline orchestration function.

```python
def run_recommendation_pipeline(self, city: str, input_products: List[str]) -> Dict[str, Any]:
    """
    Execute complete recommendation workflow
    
    Args:
        city: City name for weather lookup
        input_products: Available product catalog
        
    Returns:
        Comprehensive results dictionary:
        {
            "weather": {
                "location": str,
                "temperature": float,
                "condition": str,
                "humidity": int,
                "wind_speed": float,
                "date": str
            },
            "recommendations": {
                "products": List[str],
                "reasoning": str
            },
            "notification_message": str,
            "timestamp": str (ISO format)
        }
        
    Raises:
        ValueError: If required environment variables missing
        requests.RequestException: If weather API fails without fallback
        Exception: For other system errors
    """
```

### Utility Functions

#### `validate_environment() -> bool`
Validates all required configuration.

```python
def validate_environment() -> bool:
    """
    Validate environment configuration
    
    Returns:
        bool: True if all required variables present, False otherwise
        
    Checks:
        - KEY_PATH: Service account key file exists
        - OPENWEATHER_API_KEY: API key configured
        - PROJECT_ID: GCP project specified
        - Optional: CITY, LOCATION_ID defaults
    
    Side Effects:
        - Prints missing configuration details
        - Loads .env file if present
    """
```

#### Error Handling Patterns

```python
# Standard error handling for API calls
try:
    weather = recommender.get_weather_data("London")
    recommendations = recommender.recommend_products(weather, products)
    notification = recommender.generate_notification_message(weather, recommendations.products)
    
except requests.RequestException as e:
    # Weather API failure - use fallback data
    logger.warning(f"Weather API failed, using fallback: {e}")
    weather = recommender._get_fallback_weather("London")
    
except json.JSONDecodeError as e:
    # AI response parsing failure - use rule-based fallback
    logger.warning(f"AI response parsing failed, using fallback: {e}")
    recommendations = recommender._generate_fallback_recommendation(weather, products)
    
except Exception as e:
    # System failure - alert and graceful degradation
    logger.error(f"System error in recommendation pipeline: {e}")
    raise
```

## 💡 Usage Examples

### Basic Usage - Single Merchant

```python
from weather_product_recommender import recommend_products_by_weather

# Simple execution for merchant
notification_message = recommend_products_by_weather("94025")
print(f"Customer notification: {notification_message}")

# Example output:
# "☀️ Perfect 24°C weather for Sunglasses and Shorts! 
#  FREE delivery on these summer essentials today only! 🌞"
```

### Advanced Usage - Custom Configuration

```python
from weather_product_recommender import WeatherProductRecommender
import os
from dotenv import load_dotenv

# Load configuration
load_dotenv()

# Initialize with custom settings
recommender = WeatherProductRecommender(
    project_id=os.getenv("PROJECT_ID"),
    location=os.getenv("LOCATION_ID", "us-central1"),
    debug=True  # Enable detailed logging
)

# Define product catalog
products = [
    "Winter Coat", "Sunglasses", "Umbrella", "Rain Boots",
    "Shorts", "Hot Chocolate", "Ice Cream", "Scarf"
]

# Execute pipeline with multiple cities
cities = ["London", "New York", "Sydney", "Tokyo"]

for city in cities:
    try:
        results = recommender.run_recommendation_pipeline(city, products)
        
        print(f"\n--- {city} Weather Recommendations ---")
        print(f"Weather: {results['weather']['condition']}, {results['weather']['temperature']}°C")
        print(f"Recommended: {', '.join(results['recommendations']['products'])}")
        print(f"Reasoning: {results['recommendations']['reasoning']}")
        print(f"Notification: {results['notification_message']}")
        
    except Exception as e:
        print(f"Error processing {city}: {e}")
```

### Integration with E-commerce Platform

```python
class EcommerceWeatherIntegration:
    """Integration wrapper for e-commerce platforms"""
    
    def __init__(self):
        self.recommender = WeatherProductRecommender(
            project_id=os.getenv("PROJECT_ID"),
            location=os.getenv("LOCATION_ID"),
            debug=False
        )
    
    def get_weather_recommendations_for_customer(self, customer_id: str, 
                                               customer_location: str) -> Dict[str, Any]:
        """Get personalized weather recommendations for customer"""
        
        # Get customer's purchase history and preferences
        customer_products = self._get_customer_relevant_products(customer_id)
        
        # Run weather recommendation
        results = self.recommender.run_recommendation_pipeline(
            customer_location, customer_products
        )
        
        # Format for e-commerce system
        return {
            "customer_id": customer_id,
            "recommended_products": results["recommendations"]["products"],
            "weather_context": results["weather"],
            "marketing_message": results["notification_message"],
            "confidence": 0.9,
            "expires_at": self._calculate_expiry_time(),
            "campaign_type": "weather_contextual"
        }
    
    def _get_customer_relevant_products(self, customer_id: str) -> List[str]:
        """Get products relevant to customer based on history/preferences"""
        # This would integrate with your product/customer database
        # For demo, return sample products
        return [
            "Winter Jacket", "Sunscreen", "Umbrella", "Shorts",
            "Rain Boots", "Sunglasses", "Scarf", "T-Shirt"
        ]
    
    def _calculate_expiry_time(self) -> str:
        """Calculate when weather-based recommendations expire"""
        # Weather recommendations typically valid for 6-12 hours
        expiry = datetime.now() + timedelta(hours=8)
        return expiry.isoformat()

# Usage in e-commerce application
integration = EcommerceWeatherIntegration()

# Get recommendations for customer in specific location
recommendations = integration.get_weather_recommendations_for_customer(
    customer_id="CUST_12345",
    customer_location="San Francisco"
)

# Send to marketing automation system
send_personalized_email(
    customer_id=recommendations["customer_id"],
    subject=f"Weather Perfect for {', '.join(recommendations['recommended_products'][:2])}!",
    message=recommendations["marketing_message"],
    products=recommendations["recommended_products"]
)
```

### Batch Processing for Multiple Merchants

```python
import asyncio
import concurrent.futures
from typing import List, Tuple

async def batch_weather_recommendations(merchant_configs: List[Tuple[str, str]]) -> List[Dict]:
    """
    Process weather recommendations for multiple merchants concurrently
    
    Args:
        merchant_configs: List of (merchant_id, city) tuples
        
    Returns:
        List of recommendation results
    """
    
    def process_single_merchant(config: Tuple[str, str]) -> Dict:
        merchant_id, city = config
        try:
            # Override city for this merchant
            os.environ["CITY"] = city
            
            # Run recommendation
            notification = recommend_products_by_weather(merchant_id)
            
            return {
                "merchant_id": merchant_id,
                "city": city,
                "status": "success",
                "notification": notification,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "merchant_id": merchant_id,
                "city": city,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # Process merchants concurrently (limit to avoid API rate limits)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(executor, process_single_merchant, config)
            for config in merchant_configs
        ]
        
        results = await asyncio.gather(*futures)
        return results

# Usage
merchant_configs = [
    ("94025", "London"),
    ("94026", "New York"), 
    ("94027", "Tokyo")]
# Social Media Marketing Bot Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Installation & Setup](#installation--setup)
5. [Configuration](#configuration)
6. [Core Components](#core-components)
7. [API Reference](#api-reference)
8. [Usage Examples](#usage-examples)
9. [Content Strategy](#content-strategy)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)
12. [Performance Optimization](#performance-optimization)

## 📖 Overview

The Social Media Marketing Bot is an AI-powered automation system that generates and posts tailored social media content for SME products. Built for the "set it and forget it" principle, this bot analyzes product performance data and creates strategic social media campaigns without manual intervention.

### Key Features
- **AI-Powered Content Generation**: Uses Google's Gemini 2.5 Pro for intelligent post creation
- **Performance-Based Strategy**: Different approaches for best-selling vs. underperforming products
- **Multi-Platform Support**: Instagram and Facebook integration
- **Autonomous Operation**: Minimal setup with automatic content scheduling
- **Strategic Differentiation**: Social proof for popular items, urgency tactics for slow movers

### Business Benefits
- **Increase Product Visibility**: Automated posting keeps products in front of customers
- **Boost Underperforming Products**: Strategic content for slow-selling items
- **Save Time**: Eliminates manual social media management
- **Consistent Brand Presence**: Regular, professional content across platforms
- **Data-Driven Approach**: Content strategy based on actual sales performance

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│  Sales Database │───▶│   Product    │───▶│ Content Strategy│
│ (Best/Worst     │    │ Performance  │    │   Selection     │
│  Sellers)       │    │  Analysis    │    │                 │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                     │
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│  Social Media   │◀───│ Multi-Platform│◀───│ Gemini 2.5 Pro  │
│   Platforms     │    │   Publisher   │    │ Content Generator│
│ (Instagram/FB)  │    │               │    │                 │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                     │
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Monitoring    │◀───│   Campaign   │◀───│   Post Tracking │
│  & Analytics    │    │   Results    │    │   & Results     │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

## 🔧 Prerequisites

### System Requirements
- Python 3.8 or higher
- Google Cloud Platform account
- Instagram Business Account
- Facebook Page (for Facebook posting)
- Valid API access tokens

### Required Services
- **Google Vertex AI**: For Gemini LLM access
- **Instagram Basic Display API**: For Instagram posting
- **Facebook Graph API**: For Facebook posting
- **Database Access**: For product performance data

### API Permissions Required
- **Instagram**: `instagram_basic`, `instagram_content_publish`, `pages_show_list`
- **Facebook**: `pages_manage_posts`, `pages_show_list`, `publish_to_groups`
- **Google Cloud**: `aiplatform.user`, Vertex AI API access

## 📦 Installation & Setup

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd social-media-marketing-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Dependencies Overview

```python
# Core Python Libraries
os, shutil, sys, json, logging
requests>=2.28.0
python-dotenv>=0.19.0
datetime, time
typing

# AI & Machine Learning
vertexai>=1.0.0
langchain-google-vertexai>=0.1.0
langchain>=0.1.0

# Google Cloud Platform
google-oauth2>=2.15.0
google-auth>=2.15.0

# Social Media APIs
instabot>=0.117.0  # For Instagram posting

# Custom Database Modules
# - db.get_best_selling_products_by_merchant_id
# - db.get_least_selling_products_by_merchant_id
```

### 3. Service Account Setup

```bash
# Create Google Cloud service account
gcloud iam service-accounts create social-media-bot \
    --display-name="Social Media Marketing Bot"

# Grant Vertex AI permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:social-media-bot@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Generate service account key
gcloud iam service-accounts keys create key.json \
    --iam-account=social-media-bot@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# Google Cloud Configuration
PROJECT_ID=your-gcp-project-id
LOCATION_ID=us-central1
KEY_PATH=./path/to/service-account-key.json

# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Instagram Configuration (Basic Display API)
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id_here
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password

# Facebook Configuration
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token_here
FACEBOOK_PAGE_ID=your_facebook_page_id_here

# Content Generation Settings
TEMPERATURE=0.3
MAX_HASHTAGS=7
POST_DELAY_SECONDS=3

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=social_media_bot.log
```

### Instagram API Setup Guide

1. **Create Facebook Developer Account**
   - Go to [developers.facebook.com](https://developers.facebook.com)
   - Create a new app with Instagram Basic Display

2. **Get Access Tokens**
   ```bash
   # Generate long-lived access token
   curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token" \
     -d "grant_type=fb_exchange_token" \
     -d "client_id=YOUR_APP_ID" \
     -d "client_secret=YOUR_APP_SECRET" \
     -d "fb_exchange_token=SHORT_LIVED_TOKEN"
   ```

3. **Configure Instagram Business Account**
   ```bash
   # Get Instagram Business Account ID
   curl -X GET "https://graph.facebook.com/v18.0/me/accounts" \
     -d "access_token=YOUR_ACCESS_TOKEN"
   ```

## 🔧 Core Components

### 1. Data Models

#### Product
```python
@dataclass
class Product:
    """Represents a product with marketing information"""
    name: str                    # Product name
    description: str             # Product description
    price: float                 # Product price
    category: str               # Product category
    image_url: str = ""         # Product image URL (optional)
    key_features: List[str] = None  # Product features (optional)
    
    def __post_init__(self):
        if self.key_features is None:
            self.key_features = []
```

#### SocialMediaPost
```python
@dataclass
class SocialMediaPost:
    """Represents a generated social media post"""
    platform: str               # Target platform (instagram/facebook)
    content: str                # Main post content
    hashtags: List[str]         # List of hashtags
    image_url: str = ""         # Image URL for the post
    call_to_action: str = ""    # Call-to-action text
    
    @property
    def formatted_caption(self) -> str:
        """Get formatted caption with hashtags"""
        caption = self.content
        if self.call_to_action:
            caption += f"\n\n{self.call_to_action}"
        if self.hashtags:
            caption += "\n\n" + " ".join([f"#{tag}" for tag in self.hashtags])
        return caption
```

### 2. Configuration Management

#### EnvConfigManager
```python
class EnvConfigManager:
    """Manages environment variables and secrets"""
    
    def __init__(self):
        """Initialize configuration manager"""
        load_dotenv()  # Load .env file
    
    def get_secret(self, secret_name: str) -> str:
        """
        Retrieve secret from environment variables
        
        Args:
            secret_name: Name of the secret (kebab-case)
            
        Returns:
            str: Secret value
            
        Raises:
            ValueError: If secret not found
        """
        env_var_map = {
            "gemini-api-key": "GEMINI_API_KEY",
            "instagram-access-token": "INSTAGRAM_ACCESS_TOKEN",
            "instagram-business-account-id": "INSTAGRAM_BUSINESS_ACCOUNT_ID",
            "facebook-access-token": "FACEBOOK_ACCESS_TOKEN",
            "facebook-page-id": "FACEBOOK_PAGE_ID"
        }
        
        env_var_name = env_var_map.get(secret_name, 
                                      secret_name.upper().replace("-", "_"))
        value = os.getenv(env_var_name)
        
        if not value:
            raise ValueError(f"Environment variable {env_var_name} not found")
        
        return value
```

### 3. Content Generation Engine

#### ContentGenerator
```python
class ContentGenerator:
    """AI-powered content generation using Gemini"""
    
    def __init__(self, project_id: str, location: str):
        """
        Initialize content generator
        
        Args:
            project_id: GCP project ID
            location: GCP location for Vertex AI
        """
        self.project_id = project_id
        self.location = location
        
        # Initialize Vertex AI and LangChain
        KEY_PATH = os.getenv("KEY_PATH")
        credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
        
        vertexai.init(project=project_id, location=location)
        
        self.llm = ChatVertexAI(
            model_name="gemini-2.5-pro",
            project=project_id,
            location=location,
            temperature=0.3,
            credentials=credentials
        )
```

#### Content Generation Methods

##### `generate_best_selling_post(product: Product, platform: str) -> SocialMediaPost`
Generates content for best-selling products using social proof strategy.

**Strategy Elements:**
- Emphasizes popularity and customer satisfaction
- Uses social proof language ("bestseller", "customer favorite")
- Creates FOMO (fear of missing out)
- Confident, exciting tone

**Example Output:**
```json
{
    "content": "🔥 OUR #1 BESTSELLER! This Premium Coffee Blend has customers coming back for more! ☕️ Loved by coffee enthusiasts everywhere for its rich, smooth taste.",
    "hashtags": ["bestseller", "coffeelover", "premium", "customersfavorite", "richflavor"],
    "call_to_action": "Join thousands of satisfied customers - order yours today! ☕️✨"
}
```

##### `generate_worst_selling_post(product: Product, platform: str) -> SocialMediaPost`
Generates content for underperforming products using value and urgency tactics.

**Strategy Elements:**
- Emphasizes unique value and benefits
- Creates sense of urgency or limited opportunity
- Positions as "hidden gem" or "undiscovered treasure"
- Value-focused messaging

**Example Output:**
```json
{
    "content": "🌟 HIDDEN GEM ALERT! Our Artisan Tea Collection deserves more love! 🍃 Carefully curated blends with unique flavors you won't find anywhere else.",
    "hashtags": ["hiddengem", "artisan", "uniqueflavor", "limitedtime", "teatime"],
    "call_to_action": "Don't let others discover this secret first - grab yours now! 🍃💫"
}
```

### 4. Social Media APIs

#### InstagramAPI
```python
class InstagramAPI:
    """Instagram posting via Instagram Basic Display API"""
    
    def __init__(self, access_token: str, business_account_id: str):
        """
        Initialize Instagram API client
        
        Args:
            access_token: Instagram access token
            business_account_id: Instagram business account ID
        """
        self.access_token = access_token
        self.business_account_id = business_account_id
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def post_content(self, post: SocialMediaPost) -> Dict[str, Any]:
        """
        Post content to Instagram
        
        Args:
            post: SocialMediaPost object
            
        Returns:
            Dict containing post ID and status
            
        Raises:
            Exception: If posting fails
        """
        # Two-step process: create media container, then publish
        media_container_id = self._create_media_container(post)
        return self._publish_media(media_container_id)
```

#### FacebookAPI
```python
class FacebookAPI:
    """Facebook posting via Graph API"""
    
    def __init__(self, access_token: str, page_id: str):
        """
        Initialize Facebook API client
        
        Args:
            access_token: Facebook page access token
            page_id: Facebook page ID
        """
        self.access_token = access_token
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def post_content(self, post: SocialMediaPost) -> Dict[str, Any]:
        """
        Post content to Facebook page
        
        Args:
            post: SocialMediaPost object
            
        Returns:
            Dict containing post ID and status
        """
        url = f"{self.base_url}/{self.page_id}/feed"
        params = {
            "message": post.formatted_caption,
            "access_token": self.access_token
        }
        
        if post.image_url:
            params["link"] = post.image_url
        
        response = requests.post(url, data=params)
        return response.json()
```

### 5. Main Bot Orchestrator

#### SocialMediaMarketingBot
```python
class SocialMediaMarketingBot:
    """Main orchestrator for social media marketing automation"""
    
    def __init__(self):
        """Initialize bot with all required APIs"""
        self.config_manager = EnvConfigManager()
        self._setup_apis()
    
    def generate_and_post_campaigns(self, 
                                  best_selling_products: List[Product], 
                                  worst_selling_products: List[Product],
                                  platforms: List[str] = ["instagram", "facebook"]
                                  ) -> Dict[str, List[Dict]]:
        """
        Generate and post complete social media campaigns
        
        Args:
            best_selling_products: List of top-performing products
            worst_selling_products: List of underperforming products  
            platforms: Target platforms for posting
            
        Returns:
            Campaign results with success/failure status
        """
```

## 📚 API Reference

### Core Functions

#### `post_products_to_instagram(merchant_id: str) -> None`
Main entry point for Instagram marketing campaigns.

```python
def post_products_to_instagram(merchant_id: str) -> None:
    """
    Execute complete Instagram marketing campaign for merchant
    
    Args:
        merchant_id: Unique merchant identifier
        
    Process:
        1. Fetch best/worst selling products from database
        2. Convert to Product objects
        3. Generate AI-powered content
        4. Post to Instagram
        5. Log results
    """
```

#### `_create_product_campaign(product: Product, platforms: List[str], is_best_selling: bool) -> List[Dict[str, Any]]`
Creates campaign for single product across multiple platforms.

```python
def _create_product_campaign(self, 
                           product: Product, 
                           platforms: List[str], 
                           is_best_selling: bool) -> List[Dict[str, Any]]:
    """
    Create multi-platform campaign for single product
    
    Args:
        product: Product object
        platforms: List of target platforms
        is_best_selling: Strategy selection flag
        
    Returns:
        List of campaign results per platform
    """
```

#### `generate_content_preview(products, platforms) -> Dict[str, Any]`
Generates content previews without posting (useful for testing).

```python
def generate_content_preview(self, 
                           best_selling_products: List[Product], 
                           worst_selling_products: List[Product],
                           platforms: List[str] = ["instagram", "facebook"]
                           ) -> Dict[str, Any]:
    """
    Generate content previews without posting
    
    Returns:
        {
            "best_selling_previews": [
                {
                    "product": "Product Name",
                    "posts": [
                        {
                            "platform": "instagram",
                            "content": "Post content...",
                            "hashtags": ["tag1", "tag2"],
                            "call_to_action": "CTA text"
                        }
                    ]
                }
            ],
            "worst_selling_previews": [...]
        }
    """
```

### Error Handling

```python
# Standard error handling pattern
try:
    result = bot.generate_and_post_campaigns(best_products, worst_products)
    logger.info(f"Campaign completed: {result}")
except Exception as e:
    logger.error(f"Campaign failed: {e}")
    # Implement fallback or retry logic
```

### Response Formats

#### Campaign Results
```python
{
    "best_selling_campaigns": [
        {
            "product": "Premium Coffee",
            "posts": [
                {
                    "platform": "instagram",
                    "post_content": "Generated content...",
                    "hashtags": ["coffee", "premium"],
                    "status": "success",
                    "timestamp": "2025-09-04T10:30:00Z"
                }
            ]
        }
    ],
    "worst_selling_campaigns": [...],
    "errors": []
}
```

## 💡 Usage Examples

### Basic Usage - Single Merchant

```python
from social_media_bot import post_products_to_instagram

# Run campaign for specific merchant
post_products_to_instagram("94025")
```

### Advanced Usage - Custom Products

```python
from social_media_bot import SocialMediaMarketingBot, Product

# Define custom products
custom_products = [
    Product(
        name="Artisan Coffee Blend",
        description="Hand-roasted premium coffee beans",
        price=24.99,
        category="Beverages",
        image_url="https://example.com/coffee.jpg"
    )
]

# Initialize bot
bot = SocialMediaMarketingBot()

# Generate previews first
previews = bot.generate_content_preview(
    best_selling_products=custom_products,
    worst_selling_products=[],
    platforms=["instagram"]
)

print("Content Preview:")
for preview in previews["best_selling_previews"]:
    print(f"Product: {preview['product']}")
    for post in preview["posts"]:
        print(f"Platform: {post['platform']}")
        print(f"Content: {post['content']}")
        print(f"Hashtags: {', '.join(post['hashtags'])}")
        print("-" * 50)
```

### Batch Processing Multiple Merchants

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

def process_merchant(merchant_id):
    """Process single merchant"""
    try:
        post_products_to_instagram(merchant_id)
        return {"merchant_id": merchant_id, "status": "success"}
    except Exception as e:
        return {"merchant_id": merchant_id, "status": "failed", "error": str(e)}

async def batch_process_merchants(merchant_ids):
    """Process multiple merchants concurrently"""
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(process_merchant, merchant_id)
            for merchant_id in merchant_ids
        ]
        
        results = []
        for future in futures:
            result = future.result()
            results.append(result)
        
        return results

# Usage
merchant_ids = ["94025", "94026", "94027"]
results = asyncio.run(batch_process_merchants(merchant_ids))
```

### Testing with Preview Mode

```python
# Test content generation without posting
bot = SocialMediaMarketingBot()

# Load test products
test_products = [
    Product("Test Product 1", "Description", 19.99, "Electronics"),
    Product("Test Product 2", "Description", 29.99, "Home & Garden")
]

# Generate previews
previews = bot.generate_content_preview(
    best_selling_products=test_products[:1],
    worst_selling_products=test_products[1:],
    platforms=["instagram"]
)

# Analyze generated content
for category, products in previews.items():
    print(f"\n{category.upper()}:")
    for product_data in products:
        print(f"Product: {product_data['product']}")
        for post in product_data['posts']:
            print(f"Content Quality: {len(post['content'])} chars")
            print(f"Hashtag Count: {len(post['hashtags'])}")
            print(f"Has CTA: {'Yes' if post['call_to_action'] else 'No'}")
```

## 🎯 Content Strategy

### Best-Selling Products Strategy

**Approach**: Social Proof & Momentum
- **Tone**: Confident, exciting, celebratory
- **Key Messages**: 
  - "Customer favorite"
  - "Best-seller"
  - "Proven quality"
  - Social validation
- **CTAs**: "Join thousands of happy customers"
- **Hashtags**: #bestseller, #customerfavorite, #popular, #trendy

### Worst-Selling Products Strategy

**Approach**: Value Discovery & Urgency
- **Tone**: Compelling, value-focused, creates curiosity
- **Key Messages**:
  - "Hidden gem"
  - "Limited opportunity"
  - "Exclusive benefits"
  - "Don't miss out"
- **CTAs**: "Discover before others do"
- **Hashtags**: #hiddengem, #exclusive, #limitedtime, #undiscovered

### Platform-Specific Adaptations

#### Instagram
- **Character Limit**: 150-200 characters for main content
- **Visual Focus**: Emphasis on product imagery
- **Hashtag Strategy**: 5-7 targeted hashtags
- **Story Integration**: Consider Instagram Stories for additional reach

#### Facebook
- **Character Limit**: 100-150 characters for main content
- **Link Sharing**: Better support for external links
- **Audience**: Often older demographic, adjust tone accordingly
- **Engagement**: Encourage comments and shares

## 🚀 Deployment

### Local Development

```bash
# Setup development environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run tests
python -m pytest tests/

# Run single merchant campaign
python social_media_bot.py
```

### Cloud Function Deployment

```yaml
# requirements.txt for Cloud Functions
functions-framework==3.*
google-cloud-aiplatform>=1.0.0
langchain-google-vertexai>=0.1.0
requests>=2.28.0
python-dotenv>=0.19.0
instabot>=0.117.0
```

```python
# main.py for Cloud Functions
import functions_framework
from social_media_bot import post_products_to_instagram

@functions_framework.http
def social_media_campaign(request):
    """Cloud Function entry point"""
    try:
        # Parse request
        request_json = request.get_json(silent=True)
        merchant_id = request_json.get('merchant_id', '94025')
        
        # Run campaign
        post_products_to_instagram(merchant_id)
        
        return {'status': 'success', 'merchant_id': merchant_id}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500
```

```bash
# Deploy to Cloud Functions
gcloud functions deploy social-media-campaign \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated \
    --memory 1GB \
    --timeout 540s \
    --set-env-vars PROJECT_ID=your-project,LOCATION_ID=us-central1
```

### Scheduled Execution

```bash
# Create Cloud Scheduler job (daily at 10 AM)
gcloud scheduler jobs create http social-media-daily \
    --schedule="0 10 * * *" \
    --uri="https://REGION-PROJECT.cloudfunctions.net/social-media-campaign" \
    --http-method=POST \
    --headers="Content-Type=application/json" \
    --message-body='{"merchant_id": "94025"}' \
    --time-zone="America/New_York"
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for instabot
RUN mkdir -p ./config

EXPOSE 8080

CMD ["python", "social_media_bot.py"]
```

## 🔍 Troubleshooting

### Common Issues

#### Issue: "Instagram Login Failed"
```python
# Solution: Check credentials and handle rate limiting
def safe_instagram_login():
    max_retries = 3
    for attempt in range(max_retries):
        try:
            bot = instabot.Bot(save_logfile=False)
            success = bot.login(
                username=os.getenv('INSTAGRAM_USERNAME'),
                password=os.getenv('INSTAGRAM_PASSWORD'),
                force=True
            )
            if success:
                return bot
        except Exception as e:
            logger.warning(f"Login attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(60)  # Wait 1 minute before retry
    
    raise Exception("Instagram login failed after all retries")
```

#### Issue: "Gemini API Rate Limiting"
```python
# Solution: Implement exponential backoff
import time
from random import uniform

def call_gemini_with_backoff(llm, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return llm.invoke([HumanMessage(content=prompt)])
        except Exception as e:
            if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                wait_time = (2 ** attempt) + uniform(0, 1)
                logger.warning(f"Rate limited, waiting {wait_time:.2f}s")
                time.sleep(wait_time)
            else:
                raise e
```

#### Issue: "File Permission Errors"
```python
# Solution: Proper file cleanup and error handling
def cleanup_temp_files():
    try:
        # Remove temporary files
        temp_files = ['temp_am.jpg.REMOVE_ME']
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        # Remove config directory
        if os.path.exists('./config'):
            shutil.rmtree('./config', ignore_errors=True)
    except Exception as e:
        logger.warning(f"Cleanup warning: {e}")
```

#### Issue: "JSON Parsing Errors from LLM"
```python
def robust_json_parse(response_content):
    """Robust JSON parsing with fallbacks"""
    try:
        # Try to find JSON in response
        start_idx = response_content.find('{')
        end_idx = response_content.rfind('}') + 1
        
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON found in response")
        
        json_str = response_content[start_idx:end_idx]
        return json.loads(json_str)
    
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"JSON parsing failed: {e}")
        # Return fallback structure
        return {
            "content": "Check out our amazing products!",
            "hashtags": ["sale", "products", "shopping"],
            "call_to_action": "Shop now!"
        }
```

### Debugging Tools

```python
# Enable verbose logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test individual components
def test_content_generation():
    """Test content generation without posting"""
    generator = ContentGenerator(
        project_id=os.getenv("PROJECT_ID"),
        location=os.getenv("LOCATION_ID")
    )
    
    test_product = Product(
        name="Test Product",
        description="Test description",
        price=19.99,
        category="Test Category"
    )
    
    post = generator.generate_best_selling_post(test_product, "instagram")
    print(f"Generated content: {post.content}")
    print(f"Hashtags: {post.hashtags}")
```

### Performance Monitoring

```python
import time
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} completed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {e}")
            raise
    return wrapper

# Usage
@monitor_performance
def post_products_to_instagram(merchant_id):
    # Your existing function
    pass
```

## ⚡ Performance Optimization

### Batch Processing Optimization

```python
def optimized_batch_processing(products, batch_size=5):
    """Process products in optimized batches"""
    
    for i in range(0, len(products), batch_size):
        batch = products[i:i + batch_size]
        
        # Process batch with concurrent content generation
        with ThreadPoolExecutor(max_workers=3) as executor:
            content_futures = [
                executor.submit(generate_content_for_product, product)
                for product

# Personalized recommendation agent

## 📋 Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Installation & Setup](#installation--setup)
5. [Configuration](#configuration)
6. [Core Components](#core-components)
7. [API Reference](#api-reference)
8. [Usage Examples](#usage-examples)
9. [Deployment](#deployment)
10. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
11. [Performance Optimization](#performance-optimization)

## 📖 Overview

The GCP Recommendation System is an AI-powered platform that delivers personalized product recommendations to customers through automated email campaigns. Built for SMEs, this system operates autonomously once configured, requiring minimal maintenance while maximizing customer engagement and sales.

### Key Features
- **Autonomous Operation**: Set-and-forget functionality with self-improving recommendations
- **Personalized AI**: Leverages Google's Gemini LLM for intelligent product suggestions
- **Scalable Infrastructure**: Built on Google Cloud Platform for enterprise-grade performance
- **Email Integration**: Automated personalized email campaigns
- **Real-time Analytics**: BigQuery integration for data-driven insights

### Business Benefits
- Increase customer retention by up to 30%
- Boost average order value through cross-selling
- Reduce manual marketing efforts by 90%
- Improve customer lifetime value

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Purchase Data │───▶│  BigQuery    │───▶│ Recommendation  │
│   (Historical)  │    │  Analytics   │    │    Engine       │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                     │
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│  Customer Data  │───▶│   Vertex AI  │◀───│  LangChain +    │
│   (Profiles)    │    │   (Gemini)   │    │    Gemini       │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                     │
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Email Service │◀───│ Cloud Storage│◀───│  Recommendations│
│  (Notifications)│    │  (Results)   │    │    Storage      │
└─────────────────┘    └──────────────┘    └─────────────────┘
```

## 🔧 Prerequisites

### System Requirements
- Python 3.8 or higher
- Google Cloud Platform account with billing enabled
- Service account with appropriate permissions

### Required GCP Services
- **BigQuery**: Data warehousing and analytics
- **Vertex AI**: Machine learning platform
- **Cloud Storage**: File storage and artifacts
- **Cloud Functions**: Serverless execution (optional)
- **Cloud Scheduler**: Automated pipeline execution (optional)

### GCP Permissions Required
```json
{
  "roles": [
    "bigquery.dataViewer",
    "bigquery.jobUser",
    "storage.objectViewer",
    "aiplatform.user",
    "cloudfunctions.invoker"
  ]
}
```

## 📦 Installation & Setup

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd gcp-recommendation-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Dependencies Overview

```python
# Core Python libraries
pandas>=1.5.0
python-dotenv>=0.19.0
pydantic>=1.10.0

# Google Cloud Platform
google-cloud-bigquery>=3.4.0
google-cloud-storage>=2.7.0
google-auth>=2.15.0
vertexai>=1.0.0

# LangChain & AI
langchain>=0.1.0
langchain-google-vertexai>=0.1.0

# Custom modules (included in project)
# - db.get_loyal_users_order_history
# - db.get_users_emails  
# - cloud_functions.send_email
```

### 3. Service Account Setup

```bash
# Create service account
gcloud iam service-accounts create recommendation-system \
    --display-name="Recommendation System Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:recommendation-system@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataViewer"

# Generate and download key
gcloud iam service-accounts keys create key.json \
    --iam-account=recommendation-system@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# GCP Configuration
PROJECT_ID=your-gcp-project-id
REGION=us-central1
KEY_PATH=./path/to/service-account-key.json

# BigQuery Configuration
DATASET_ID=recommendation_data
TABLE_ID=customer_recommendations
PURCHASE_HISTORY_TABLE=purchase_history
CUSTOMER_TABLE=customers

# Email Configuration
EMAIL_SENDER=noreply@yourcompany.com
EMAIL_TEMPLATE_BUCKET=recommendation-email-templates

# AI Configuration
MODEL_NAME=gemini-1.5-pro
TEMPERATURE=0.3
MAX_RECOMMENDATIONS=5

# Logging
LOG_LEVEL=INFO
LOG_FILE=recommendation_system.log
```

### BigQuery Schema Setup

```sql
-- Create dataset
CREATE SCHEMA IF NOT EXISTS `your-project.recommendation_data`
OPTIONS(
  description="Recommendation system data",
  location="US"
);

-- Create recommendations table
CREATE OR REPLACE TABLE `your-project.recommendation_data.customer_recommendations` (
  customer_id STRING NOT NULL,
  item_id STRING NOT NULL,
  item_name STRING NOT NULL,
  category STRING,
  confidence_score FLOAT64,
  reason STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  merchant_id STRING
);
```

## 🔧 Core Components

### 1. Data Models

#### RecommendationItem
```python
class RecommendationItem(BaseModel):
    """Represents a single product recommendation"""
    item_id: str = Field(..., description="Unique product identifier")
    item_name: str = Field(..., description="Human-readable product name")
    category: str = Field(..., description="Product category")
    confidence_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="Confidence score (0-1)"
    )
    reason: str = Field(..., description="Explanation for recommendation")
    
    class Config:
        json_encoders = {
            float: lambda v: round(v, 3)
        }
```

#### CustomerRecommendations
```python
class CustomerRecommendations(BaseModel):
    """Container for all recommendations for a customer"""
    customer_id: str = Field(..., description="Unique customer identifier")
    recommendations: List[RecommendationItem] = Field(
        ..., 
        description="List of recommended items"
    )
    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when recommendations were generated"
    )
```

### 2. GCPRecommendationSystem Class

#### Core Methods

##### `__init__(self, project_id: str, region: str, key_path: str)`
Initializes the recommendation system with GCP credentials and AI models.

**Parameters:**
- `project_id`: GCP project identifier
- `region`: GCP region for Vertex AI
- `key_path`: Path to service account key file

**Example:**
```python
system = GCPRecommendationSystem(
    project_id="my-project",
    region="us-central1", 
    key_path="./service-account-key.json"
)
```

##### `analyze_purchase_history(self, purchase_data: pd.DataFrame) -> Dict`
Analyzes customer purchase patterns and identifies popular items.

**Returns:**
```python
{
    "customer_stats": {
        "customer_id": {
            "total_purchases": int,
            "unique_items": int,
            "avg_order_value": float,
            "last_purchase_date": str,
            "favorite_categories": List[str]
        }
    },
    "popular_items": {
        "item_id": {
            "name": str,
            "category": str,
            "purchase_count": int,
            "avg_rating": float
        }
    }
}
```

##### `generate_recommendations(self, purchase_data: pd.DataFrame, loyal_customers: List[str]) -> List[CustomerRecommendations]`
Generates AI-powered recommendations using Gemini LLM.

**Parameters:**
- `purchase_data`: Historical purchase data
- `loyal_customers`: List of loyal customer IDs for prioritization

**Returns:** List of CustomerRecommendations objects

##### `store_recommendations_to_bigquery(self, recommendations: List[CustomerRecommendations], dataset_id: str, table_id: str) -> bool`
Persists recommendations to BigQuery for analytics and tracking.

**Error Handling:**
```python
try:
    success = system.store_recommendations_to_bigquery(
        recommendations, "recommendation_data", "customer_recommendations"
    )
except Exception as e:
    logging.error(f"Failed to store recommendations: {e}")
```

##### `generate_email_content(self, customer_id: str, recommendations: List[RecommendationItem]) -> Tuple[str, str]`
Creates personalized email subject and HTML body using Gemini.

**Returns:** `(subject, html_body)` tuple

##### `run_recommendation_pipeline(self, purchase_data: pd.DataFrame, customer_emails: Dict[str, str]) -> Dict`
Orchestrates the complete recommendation and email pipeline.

**Returns:**
```python
{
    "total_customers": int,
    "recommendations_generated": int,
    "emails_sent": int,
    "errors": List[str],
    "execution_time": float
}
```

## 📚 API Reference

### Utility Functions

#### `setup_bigquery_table(project_id: str, dataset_id: str, table_id: str) -> bool`
Creates BigQuery dataset and table if they don't exist.

```python
# Example usage
success = setup_bigquery_table(
    project_id="my-project",
    dataset_id="recommendation_data", 
    table_id="customer_recommendations"
)
```

#### `load_purchase_data_from_bigquery(project_id: str, query: str) -> pd.DataFrame`
Executes BigQuery query and returns results as DataFrame.

```python
# Example query
query = """
SELECT customer_id, item_id, item_name, category, purchase_date, quantity, price
FROM `my-project.sales.purchase_history`
WHERE purchase_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
ORDER BY customer_id, purchase_date DESC
"""

df = load_purchase_data_from_bigquery("my-project", query)
```

#### `load_customer_emails_from_bigquery(project_id: str, query: str) -> Dict[str, str]`
Loads customer email addresses into a dictionary.

```python
# Example query
query = """
SELECT customer_id, email
FROM `my-project.customers.profiles`
WHERE email IS NOT NULL 
AND marketing_opt_in = true
AND status = 'active'
"""

emails = load_customer_emails_from_bigquery("my-project", query)
# Returns: {"customer_123": "customer@example.com", ...}
```

## 💡 Usage Examples

### Basic Usage

```python
from main import recommend_personalized_products
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Run recommendations for specific merchant
results = recommend_personalized_products(merchant_id="94025")
print(f"Generated recommendations for {results['total_customers']} customers")
```

### Advanced Usage with Custom Parameters

```python
from gcp_recommendation_system import GCPRecommendationSystem
import pandas as pd

# Initialize system
system = GCPRecommendationSystem(
    project_id=os.getenv("PROJECT_ID"),
    region=os.getenv("REGION"),
    key_path=os.getenv("KEY_PATH")
)

# Load custom data
purchase_data = pd.read_csv("custom_purchase_data.csv")
customer_emails = {"customer_1": "test@example.com"}

# Run pipeline with custom data
results = system.run_recommendation_pipeline(purchase_data, customer_emails)

# Process results
for customer_id, recommendations in results['recommendations'].items():
    print(f"Customer {customer_id}:")
    for rec in recommendations.recommendations:
        print(f"  - {rec.item_name} (confidence: {rec.confidence_score:.2f})")
```

### Batch Processing Example

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_merchants_batch(merchant_ids: List[str]):
    """Process multiple merchants concurrently"""
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(recommend_personalized_products, merchant_id)
            for merchant_id in merchant_ids
        ]
        
        results = []
        for future in futures:
            try:
                result = future.result(timeout=300)  # 5 minute timeout
                results.append(result)
            except Exception as e:
                logging.error(f"Failed to process merchant: {e}")
        
        return results

# Usage
merchant_ids = ["94025", "94026", "94027"]
results = asyncio.run(process_merchants_batch(merchant_ids))
```

## 🚀 Deployment

### Cloud Functions Deployment

```yaml
# deploy.yaml
runtime: python39
entry_point: recommend_personalized_products
memory: 2GB
timeout: 540s
environment_variables:
  PROJECT_ID: your-project-id
  REGION: us-central1
```

```bash
# Deploy to Cloud Functions
gcloud functions deploy recommendation-system \
    --runtime python39 \
    --trigger-http \
    --allow-unauthenticated \
    --memory 2GB \
    --timeout 540s \
    --env-vars-file .env.yaml
```

### Cloud Scheduler Setup

```bash
# Create scheduled job (daily at 9 AM)
gcloud scheduler jobs create http recommendation-daily \
    --schedule="0 9 * * *" \
    --uri="https://YOUR_REGION-YOUR_PROJECT.cloudfunctions.net/recommendation-system" \
    --http-method=POST \
    --headers="Content-Type=application/json" \
    --message-body='{"merchant_id": "94025"}'
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

```bash
# Build and deploy
docker build -t recommendation-system .
docker run -p 8080:8080 --env-file .env recommendation-system
```

## 📊 Monitoring & Troubleshooting

### Logging Configuration

```python
import logging
from google.cloud import logging as cloud_logging

# Setup Cloud Logging
client = cloud_logging.Client()
client.setup_logging()

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('recommendation_system.log'),
        logging.StreamHandler()
    ]
)
```

### Common Issues and Solutions

#### Issue: "Permission Denied" Errors
```bash
# Solution: Check service account permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID \
    --flatten="bindings[].members" \
    --filter="bindings.members:serviceAccount:YOUR_SERVICE_ACCOUNT"
```

#### Issue: BigQuery Query Timeouts
```python
# Solution: Add query timeout and retry logic
from google.cloud.exceptions import TimeoutError
import time

def query_with_retry(client, query, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.query(query, timeout=60).result()
        except TimeoutError:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

#### Issue: Memory Errors with Large Datasets
```python
# Solution: Process data in chunks
def process_large_dataset(df, chunk_size=1000):
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i + chunk_size]
        yield process_chunk(chunk)
```

### Performance Metrics

Monitor these key metrics:
- **Recommendation Generation Time**: < 30 seconds per 1000 customers
- **Email Delivery Rate**: > 95%
- **BigQuery Query Performance**: < 10 seconds for historical data
- **Memory Usage**: < 2GB during processing
- **Error Rate**: < 1%

## ⚡ Performance Optimization

### BigQuery Optimization

```sql
-- Use partitioning for better performance
CREATE OR REPLACE TABLE `project.dataset.purchase_history`
PARTITION BY DATE(purchase_date)
CLUSTER BY customer_id, category
AS SELECT * FROM `project.dataset.purchase_history_raw`;

-- Optimize queries with proper filtering
SELECT customer_id, item_id, item_name, category, purchase_date
FROM `project.dataset.purchase_history`
WHERE DATE(purchase_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 6 MONTH)
  AND customer_id IN UNNEST(@customer_ids)  -- Use parameter for IN clause
ORDER BY customer_id, purchase_date DESC;
```

### Caching Strategy

```python
from functools import lru_cache
import pickle
from datetime import datetime, timedelta

class RecommendationCache:
    def __init__(self, cache_duration_hours=24):
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.cache = {}
    
    def get_recommendations(self, customer_id):
        if customer_id in self.cache:
            data, timestamp = self.cache[customer_id]
            if datetime.now() - timestamp < self.cache_duration:
                return data
        return None
    
    def set_recommendations(self, customer_id, recommendations):
        self.cache[customer_id] = (recommendations, datetime.now())

# Usage
cache = RecommendationCache(cache_duration_hours=12)
```

### Batch Processing Optimization

```python
def process_recommendations_in_batches(customers, batch_size=50):
    """Process customers in batches to optimize memory usage"""
    
    for i in range(0, len(customers), batch_size):
        batch = customers[i:i + batch_size]
        
        # Process batch
        batch_results = generate_batch_recommendations(batch)
        
        # Store results immediately to free memory
        store_batch_to_bigquery(batch_results)
        
        # Clear variables to free memory
        del batch_results
        
        # Optional: Add small delay to prevent rate limiting
        time.sleep(0.1)
```
---
# Campaign Optimizer AI Agent - Technical Documentation

## Overview

The Campaign Optimizer AI Agent is an intelligent system that analyzes sales data and provides data-driven recommendations for activating or deactivating marketing campaigns. It uses Google Cloud Platform services, LangChain framework, and Vertex AI to deliver automated campaign optimization decisions.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Campaign Optimizer Agent                 │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────── │
│  │ Sales Data      │  │ Campaign        │  │ LLM Agent      │
│  │ Analyzer        │  │ Controller      │  │ (Vertex AI)    │
│  └─────────────────┘  └─────────────────┘  └─────────────── │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────── │
│  │ BigQuery        │  │ Campaign        │  │ LangChain      │
│  │ Data Source     │  │ Scripts         │  │ Tools          │
│  └─────────────────┘  └─────────────────┘  └─────────────── │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. CampaignStatus (Data Class)

Represents the status and metadata of a marketing campaign.

**Attributes:**
- `name` (str): Campaign identifier
- `is_active` (bool): Current activation status
- `last_activated` (datetime, optional): Timestamp of last activation
- `performance_score` (float): Performance metric (0-100 scale)

### 2. SalesDataAnalyzer

Handles data retrieval and analysis from BigQuery.

**Key Methods:**

#### `__init__(project_id: str)`
Initializes BigQuery client connection.

#### `get_last_month_sales_data() -> pd.DataFrame`
Retrieves 30 days of sales data with the following schema:
- `date`: Transaction date
- `hour`: Hour of transaction (0-23)
- `product_id`: Product identifier
- `customer_id`: Customer identifier
- `revenue`: Transaction revenue
- `campaign_source`: Attribution campaign
- `weather_conditions`: Weather at time of purchase
- `customer_birthday`: Birthday flag

#### `analyze_campaign_performance(df: pd.DataFrame) -> Dict[str, float]`
Calculates performance scores for each campaign as percentage of total revenue.

#### `get_hourly_sales_pattern(df: pd.DataFrame) -> Dict[int, float]`
Analyzes revenue distribution across hours (0-23).

#### `get_weather_impact(df: pd.DataFrame) -> Dict[str, float]`
Calculates average revenue by weather condition.

### 3. CampaignController

Manages campaign lifecycle operations.

**Supported Campaigns:**
- `birthday_campaign`: Birthday discount automation
- `happy_hour_campaign`: Time-based discount activation
- `weather_recommendation_agent`: Weather-based product suggestions
- `social_media_agent`: Social media posting automation
- `personalised_recommendation_agent`: Personalized product recommendations

**Key Methods:**

#### `get_campaign_status(campaign_name: str = None) -> Dict`
Returns status information for specified campaign or all campaigns.

#### `activate_campaign(campaign_name: str) -> Dict`
Executes campaign activation script with `--activate` flag.

#### `deactivate_campaign(campaign_name: str) -> Dict`
Executes campaign deactivation script with `--deactivate` flag.

### 4. CampaignOptimizationAgent

The main AI agent orchestrating the optimization process.

**Key Methods:**

#### `__init__(project_id: str, location: str = "us-central1")`
Initializes the agent with Vertex AI LLM and creates LangChain tools.

#### `_create_tools() -> List[Tool]`
Creates three LangChain tools:
1. **get_sales_data**: Comprehensive sales analysis
2. **get_campaign_status**: Campaign status inquiry
3. **get_current_context**: Time and environmental context

#### `get_recommendation() -> str`
Generates AI-powered campaign optimization recommendations using the agent executor.

#### `implement_recommendation(recommendation: str, approved: bool) -> Dict`
Parses and executes approved recommendations by calling campaign activation/deactivation methods.

## Dependencies

### Required Python Packages
```python
os, json, pandas, datetime, typing, dataclasses
google.cloud.bigquery
logging
langchain_google_vertexai
langchain.tools, langchain.agents, langchain.prompts, langchain.schema
dotenv
subprocess, sys
```

### Environment Variables
```bash
GCP_PROJECT_ID=your-gcp-project-id
GCP_LOCATION=us-central1  # Optional, defaults to us-central1
```

## Installation

1. **Install Dependencies:**
```bash
pip install google-cloud-bigquery pandas python-dotenv
pip install langchain langchain-google-vertexai
```

2. **Set up Google Cloud Authentication:**
```bash
gcloud auth application-default login
# or set GOOGLE_APPLICATION_CREDENTIALS environment variable
```

3. **Configure Environment:**
Create `.env` file with required variables.

4. **Campaign Scripts:**
Ensure campaign scripts exist in `campaigns/` directory:
```
campaigns/
├── birthday_campaign.py
├── happy_hour_campaign.py
├── weather_recommendation_agent.py
├── social_media_agent.py
└── personalised_recommendation_agent.py
```

## Database Schema

### BigQuery Table: `{project_id}.sales.transactions`

| Column | Type | Description |
|--------|------|-------------|
| order_date | TIMESTAMP | Transaction timestamp |
| product_id | STRING | Product identifier |
| customer_id | STRING | Customer identifier |
| revenue | FLOAT | Transaction amount |
| campaign_source | STRING | Attribution campaign |
| weather_conditions | STRING | Weather conditions |
| customer_birthday | BOOLEAN | Birthday flag |

## Usage Examples

### Basic Usage
```python
from campaign_optimizer import CampaignOptimizationAgent

# Initialize agent
agent = CampaignOptimizationAgent(
    project_id="your-project-id",
    location="us-central1"
)

# Get recommendation
recommendation = agent.get_recommendation()
print(recommendation)

# Implement recommendation (with approval)
result = agent.implement_recommendation(recommendation, approved=True)
```

### Analyzing Sales Data Only
```python
from campaign_optimizer import SalesDataAnalyzer

analyzer = SalesDataAnalyzer("your-project-id")
df = analyzer.get_last_month_sales_data()
performance = analyzer.analyze_campaign_performance(df)
```

### Campaign Control Only
```python
from campaign_optimizer import CampaignController

controller = CampaignController()
status = controller.get_campaign_status()
result = controller.activate_campaign("birthday_campaign")
```

## AI Agent Behavior

### System Prompt Guidelines
The AI agent follows these principles:
- **Data-driven decisions**: Based on performance metrics
- **Context awareness**: Considers time, season, and patterns
- **ROI optimization**: Maximizes return on investment
- **Customer experience**: Avoids campaign overload
- **Clear reasoning**: Provides transparent explanations

### Recommendation Format
```
**RECOMMENDATION:**
- Action: [Activate/Deactivate] [campaign_name(s)]
- Timing: [When to implement]
- Reasoning: [Data-based explanation]
- Expected Impact: [Predicted outcome]
```

## Error Handling

### Common Error Scenarios
1. **BigQuery Connection Issues**: Falls back to sample data generation
2. **Campaign Script Failures**: Returns detailed error messages
3. **LLM API Errors**: Provides graceful error responses
4. **Timeout Handling**: 30-second timeout for campaign operations

### Logging
The system uses Python's logging module with INFO level default. Key events logged:
- Data retrieval operations
- Campaign activation/deactivation
- Error conditions
- Performance metrics

## Performance Considerations

### Optimization Strategies
- **Data Caching**: Consider implementing caching for repeated queries
- **Async Operations**: Campaign operations run synchronously but could benefit from async execution
- **Memory Management**: Large datasets may require chunked processing
- **Rate Limiting**: Vertex AI calls should respect API quotas

### Scalability Notes
- BigQuery handles large-scale data efficiently
- Campaign scripts should be lightweight and fast
- Consider implementing queue-based processing for multiple campaigns

## Security Considerations

### Data Protection
- Uses Google Cloud IAM for BigQuery access
- Environment variables for sensitive configuration
- No hardcoded credentials in source code

### Campaign Execution
- Subprocess execution with timeout protection
- Error output capture and logging
- Restricted to predefined campaign scripts

## Monitoring and Maintenance

### Key Metrics to Monitor
- Campaign activation success rate
- Data retrieval performance
- LLM response times and costs
- Campaign performance trends

### Regular Maintenance Tasks
- Update sample data generation logic
- Review and optimize BigQuery queries
- Monitor Vertex AI costs and usage
- Update campaign scripts and dependencies

## Troubleshooting

### Common Issues

**1. "GCP_PROJECT_ID not found"**
- Solution: Set environment variable or create `.env` file

**2. "Campaign script not found"**
- Solution: Ensure all campaign scripts exist in `campaigns/` directory

**3. "BigQuery permission denied"**
- Solution: Verify BigQuery access permissions and authentication

**4. "Vertex AI initialization failed"**
- Solution: Check project ID, location, and API enablement

## Future Enhancements

### Potential Improvements
1. **Real-time Data Processing**: Stream processing for immediate insights
2. **A/B Testing Integration**: Automated campaign testing and optimization
3. **Advanced ML Models**: Custom models for campaign performance prediction
4. **Dashboard Integration**: Web interface for monitoring and control
5. **Multi-channel Support**: Email, SMS, push notification campaigns
6. **Advanced Scheduling**: Cron-like scheduling for automated recommendations

## Contributing

### Development Guidelines
1. Follow existing code structure and naming conventions
2. Add comprehensive logging for new features
3. Include error handling for external service calls
4. Update documentation for any API changes
5. Test with sample data before production deployment

---

**Last Updated**: September 2025  
**Version**: 2.0.0