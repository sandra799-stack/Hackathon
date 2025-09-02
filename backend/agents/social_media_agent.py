import os, shutil
import sys
import json
import requests
from typing import List, Dict, Any
from datetime import datetime
import logging
from dataclasses import dataclass
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import get_best_selling_products_by_merchant_id, get_least_selling_products_by_merchant_id
import instabot
# Environment variable loading
from dotenv import load_dotenv
import time

# Google and LangChain imports
import vertexai
from langchain_google_vertexai import ChatVertexAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from google.oauth2 import service_account

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Product:
    """Product data structure"""
    name: str
    description: str
    price: float
    category: str
    image_url: str = ""
    key_features: List[str] = None

@dataclass
class SocialMediaPost:
    """Social media post structure"""
    platform: str
    content: str
    hashtags: List[str]
    image_url: str = ""
    call_to_action: str = ""

class EnvConfigManager:
    """Handles environment variable operations (replaces GCPSecretManager)"""
    
    def __init__(self):
        pass
    
    def get_secret(self, secret_name: str) -> str:
        """Retrieve secret from environment variables"""
        try:
            # Map secret names to environment variable names
            env_var_map = {
                "gemini-api-key": "GEMINI_API_KEY",
                "instagram-access-token": "INSTAGRAM_ACCESS_TOKEN",
                "instagram-business-account-id": "INSTAGRAM_BUSINESS_ACCOUNT_ID",
                "facebook-access-token": "FACEBOOK_ACCESS_TOKEN",
                "facebook-page-id": "FACEBOOK_PAGE_ID"
            }
            
            env_var_name = env_var_map.get(secret_name, secret_name.upper().replace("-", "_"))
            value = os.getenv(env_var_name)
            
            if not value:
                raise ValueError(f"Environment variable {env_var_name} not found")
            
            return value
        except Exception as e:
            logger.error(f"Error retrieving environment variable for {secret_name}: {e}")
            raise

class ContentGenerator:
    """Generates social media content using Gemini via LangChain"""
    
    def __init__(self, project_id: str, location: str):
        # Load environment variables
        load_dotenv()
        
        self.project_id = project_id
        self.location = location
        KEY_PATH = os.getenv("KEY_PATH")
        credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Initialize LangChain with Gemini
        self.llm = ChatVertexAI(
            model_name="gemini-2.5-pro",
            project=project_id,
            location=location,
            temperature=0.3,  # Lower temperature for more consistent JSON output
            credentials=credentials
        )
    
    def generate_best_selling_post(self, product: Product, platform: str) -> SocialMediaPost:
        """Generate content for best-selling products (social proof strategy)"""
        
        prompt_template = PromptTemplate(
            input_variables=["product_name", "description", "price", "category", "platform"],
            template="""
            Create an engaging {platform} post for our BEST-SELLING product that leverages social proof and popularity.
            
            Product: {product_name}
            Description: {description}
            Price: ${price}
            Category: {category}
            
            Strategy: Emphasize popularity, customer satisfaction, and social proof.
            
            Requirements:
            - Platform: {platform}
            - Tone: Exciting, confident, social proof-focused
            - Length: {platform_length}
            - Include call-to-action
            - Suggest 5-7 relevant hashtags
            - Highlight why it's popular
            
            Format your response as JSON:
            {{
                "content": "main post text",
                "hashtags": ["hashtag1", "hashtag2", ...],
                "call_to_action": "specific CTA text"
            }}
            """
        )
        
        platform_length = "150-200 characters" if platform == "instagram" else "100-150 characters"
        
        formatted_prompt = prompt_template.format(
            product_name=product.name,
            description=product.description,
            price=product.price,
            category=product.category,
            platform=platform,
            platform_length=platform_length
        )
        
        response = self.llm.invoke([HumanMessage(content=formatted_prompt)])
        return self._parse_response(response.content, product, platform)
    
    def generate_worst_selling_post(self, product: Product, platform: str) -> SocialMediaPost:
        """Generate content for worst-selling products (value/urgency strategy)"""
        
        prompt_template = PromptTemplate(
            input_variables=["product_name", "description", "price", "category", "platform"],
            template="""
            Create an engaging {platform} post for a product that needs a sales boost using value and urgency tactics.
            
            Product: {product_name}
            Description: {description}
            Price: ${price}
            Category: {category}
            
            Strategy: Emphasize unique value, special offers, limited time, hidden gem angle.
            
            Requirements:
            - Platform: {platform}
            - Tone: Compelling, value-focused, creates urgency
            - Length: {platform_length}
            - Focus on unique benefits and value proposition
            - Create sense of discovery or limited opportunity
            - Include strong call-to-action
            - Suggest 5-7 relevant hashtags
            
            Format your response as JSON:
            {{
                "content": "main post text",
                "hashtags": ["hashtag1", "hashtag2", ...],
                "call_to_action": "specific CTA text"
            }}
            """
        )
        
        platform_length = "150-200 characters" if platform == "instagram" else "100-150 characters"
        
        formatted_prompt = prompt_template.format(
            product_name=product.name,
            description=product.description,
            price=product.price,
            category=product.category,
            platform=platform,
            platform_length=platform_length
        )
        
        response = self.llm.invoke([HumanMessage(content=formatted_prompt)])
        return self._parse_response(response.content, product, platform)
    
    def _parse_response(self, response_content: str, product: Product, platform: str) -> SocialMediaPost:
        """Parse LLM response into SocialMediaPost object"""
        try:
            # Extract JSON from response
            start_idx = response_content.find('{')
            end_idx = response_content.rfind('}') + 1
            json_str = response_content[start_idx:end_idx]
            
            parsed = json.loads(json_str)
            
            return SocialMediaPost(
                platform=platform,
                content=parsed["content"],
                hashtags=parsed["hashtags"],
                image_url=product.image_url,
                call_to_action=parsed["call_to_action"]
            )
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            # Fallback post
            return SocialMediaPost(
                platform=platform,
                content=f"Check out our amazing {product.name}! Perfect for {product.category} lovers.",
                hashtags=["sale", "products", product.category.lower().replace(" ", "")],
                image_url=product.image_url,
                call_to_action="Shop now!"
            )

class InstagramAPI:
    """Handle Instagram posting via Instagram Basic Display API"""
    
    def __init__(self, access_token: str, business_account_id: str):
        self.access_token = access_token
        self.business_account_id = business_account_id
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def post_content(self, post: SocialMediaPost) -> Dict[str, Any]:
        """Post content to Instagram"""
        try:
            # Step 1: Create media container
            media_url = f"{self.base_url}/{self.business_account_id}/media"
            
            full_caption = f"{post.content}\n\n{post.call_to_action}\n\n"
            full_caption += " ".join([f"#{tag}" for tag in post.hashtags])
            
            media_params = {
                "caption": full_caption,
                "access_token": self.access_token
            }
            
            # Add image if available
            if post.image_url:
                media_params["image_url"] = post.image_url
            
            media_response = requests.post(media_url, data=media_params)
            media_data = media_response.json()
            
            if "id" not in media_data:
                raise Exception(f"Failed to create media container: {media_data}")
            
            # Step 2: Publish the media
            publish_url = f"{self.base_url}/{self.business_account_id}/media_publish"
            publish_params = {
                "creation_id": media_data["id"],
                "access_token": self.access_token
            }
            
            publish_response = requests.post(publish_url, data=publish_params)
            publish_data = publish_response.json()
            
            logger.info(f"Instagram post published: {publish_data}")
            return publish_data
            
        except Exception as e:
            logger.error(f"Error posting to Instagram: {e}")
            raise

class FacebookAPI:
    """Handle Facebook posting via Facebook Graph API"""
    
    def __init__(self, access_token: str, page_id: str):
        self.access_token = access_token
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v18.0"
    
    def post_content(self, post: SocialMediaPost) -> Dict[str, Any]:
        """Post content to Facebook"""
        try:
            url = f"{self.base_url}/{self.page_id}/feed"
            
            full_message = f"{post.content}\n\n{post.call_to_action}\n\n"
            full_message += " ".join([f"#{tag}" for tag in post.hashtags])
            
            params = {
                "message": full_message,
                "access_token": self.access_token
            }
            
            # Add image if available
            if post.image_url:
                params["link"] = post.image_url
            
            response = requests.post(url, data=params)
            result = response.json()
            
            logger.info(f"Facebook post published: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error posting to Facebook: {e}")
            raise

class SocialMediaMarketingBot:
    """Main orchestrator class"""
    
    def __init__(self):
        self.config_manager = EnvConfigManager()
        
        # Initialize APIs
        self._setup_apis()
    
    def _setup_apis(self):
        PROJECT_ID = os.getenv("PROJECT_ID", "your-gcp-project-id")
        LOCATION_ID = os.getenv("LOCATION_ID", "your-gcp-location-id")
    

        """Initialize all API clients with credentials from environment variables"""
        try:
            # Get API keys from environment variables
            #instagram_token = self.config_manager.get_secret("instagram-access-token")
            #instagram_account_id = self.config_manager.get_secret("instagram-business-account-id")
            #facebook_token = self.config_manager.get_secret("facebook-access-token")
            #facebook_page_id = self.config_manager.get_secret("facebook-page-id")
            
            # Initialize services
            self.content_generator = ContentGenerator(PROJECT_ID, LOCATION_ID)
            #self.instagram_api = InstagramAPI(instagram_token, instagram_account_id)
            #self.facebook_api = FacebookAPI(facebook_token, facebook_page_id)
            
            logger.info("All APIs initialized successfully")
            
        except Exception as e:
            logger.error(f"Error setting up APIs: {e}")
            raise
    
    def generate_and_post_campaigns(self, 
                                  best_selling_products: List[Product], 
                                  worst_selling_products: List[Product],
                                  platforms: List[str] = ["instagram", "facebook"]) -> Dict[str, List[Dict]]:
        """Generate and post social media campaigns for all products"""
        
        results = {
            "best_selling_campaigns": [],
            "worst_selling_campaigns": [],
            "errors": []
        }
        
        # Process best-selling products
        for product in best_selling_products:
            try:
                campaign_results = self._create_product_campaign(
                    product, platforms, is_best_selling=True
                )
                results["best_selling_campaigns"].append({
                    "product": product.name,
                    "posts": campaign_results
                })
            except Exception as e:
                error_msg = f"Error with best-selling product {product.name}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        # Process worst-selling products
        for product in worst_selling_products:
            try:
                campaign_results = self._create_product_campaign(
                    product, platforms, is_best_selling=False
                )
                results["worst_selling_campaigns"].append({
                    "product": product.name,
                    "posts": campaign_results
                })
            except Exception as e:
                error_msg = f"Error with worst-selling product {product.name}: {e}"
                logger.error(error_msg)
                results["errors"].append(error_msg)
        
        return results
    
    def _create_product_campaign(self, 
                               product: Product, 
                               platforms: List[str], 
                               is_best_selling: bool) -> List[Dict[str, Any]]:
        """Create and post campaign for a single product across platforms"""
        
        campaign_results = []
        
        for platform in platforms:
            try:
                # Generate content based on product performance
                if is_best_selling:
                    post = self.content_generator.generate_best_selling_post(product, platform)
                else:
                    post = self.content_generator.generate_worst_selling_post(product, platform)
                
                # Post to platform
                self._post_to_platform(post, platform)
                
                campaign_results.append({
                    "platform": platform,
                    "post_content": post.content,
                    "hashtags": post.hashtags,
                    #"post_id": post_result.get("id", "unknown"),
                    "status": "success",
                    "timestamp": datetime.now().isoformat()
                })
                
                logger.info(f"Successfully posted {product.name} to {platform}")
                
            except Exception as e:
                campaign_results.append({
                    "platform": platform,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
                logger.error(f"Failed to post {product.name} to {platform}: {e}")
        
        return campaign_results
    
    def _post_to_platform(self, post: SocialMediaPost, platform: str) -> Dict[str, Any]:
        """Route post to appropriate platform API"""
        bot = instabot.Bot(save_logfile=False)
        username = os.getenv('INSTAGRAM_USERNAME')
        password = os.getenv('INSTAGRAM_PASSWORD')
        bot.login(username= username, password=password, force=True)
        caption = post.content
        if post.call_to_action:
            caption += post.call_to_action
        if post.hashtags:
            caption += " ".join([f"#{tag}" for tag in post.hashtags])
        if platform.lower() == "instagram":
            original_file = r".\agents\coffee.jpg"
            temp_file = r".\agents\temp_am.jpg"
            shutil.copy(original_file, temp_file)
            bot.upload_photo(temp_file, caption)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
        bot.logout()
        os.remove(r'.\agents\temp_am.jpg.REMOVE_ME')
        shutil.rmtree(r".\config", ignore_errors=True) 
        time.sleep(3)
    
    def generate_content_preview(self, 
                               best_selling_products: List[Product], 
                               worst_selling_products: List[Product],
                               platforms: List[str] = ["instagram", "facebook"]) -> Dict[str, Any]:
        """Generate content previews without posting"""
        
        previews = {
            "best_selling_previews": [],
            "worst_selling_previews": []
        }
        
        # Preview best-selling products
        for product in best_selling_products:
            product_previews = []
            for platform in platforms:
                post = self.content_generator.generate_best_selling_post(product, platform)
                product_previews.append({
                    "platform": platform,
                    "content": post.content,
                    "hashtags": post.hashtags,
                    "call_to_action": post.call_to_action
                })
            
            previews["best_selling_previews"].append({
                "product": product.name,
                "posts": product_previews
            })
        
        # Preview worst-selling products
        for product in worst_selling_products:
            product_previews = []
            for platform in platforms:
                post = self.content_generator.generate_worst_selling_post(product, platform)
                product_previews.append({
                    "platform": platform,
                    "content": post.content,
                    "hashtags": post.hashtags,
                    "call_to_action": post.call_to_action
                })
            
            previews["worst_selling_previews"].append({
                "product": product.name,
                "posts": product_previews
            })
        
        return previews

# Example usage and setup
def post_products_to_instagram(merchant_id):
    """Example usage of the Social Media Marketing Bot"""
    products = get_best_selling_products_by_merchant_id(merchant_id)
    best_selling_products = []
    for product in products:
        shutil.rmtree(r".\config", ignore_errors=True) 
        best_selling_products.append(
            Product(
            name = product['product'],
            description = '',
            price = product['price'],
            category = product['category'],
            image_url = '',
            key_features = []
        )
        )   
    
    products = get_least_selling_products_by_merchant_id(merchant_id)
    least_selling_products = []
    for product in products:
        shutil.rmtree(r".\config", ignore_errors=True) 
        least_selling_products.append(
            Product(
            name = product['product'],
            description = '',
            price = product['price'],
            category = product['category'],
            image_url = '',
            key_features = []
        )
        )   

    try:
        # Initialize the marketing bot
        bot = SocialMediaMarketingBot()
        
        # Option 1: Generate previews first
        print("Generating content previews...")
        previews = bot.generate_content_preview(
            best_selling_products, 
            least_selling_products,
            platforms=["instagram"]
        )
        
        print("Preview Generated:")
        # print(json.dumps(previews, indent=2))
        
        # Option 2: Generate and post campaigns
        print("\nGenerating and posting campaigns...")
        results = bot.generate_and_post_campaigns(
            best_selling_products,
            least_selling_products,
            platforms=["instagram"]
        )
        
        print("Campaign Results:")
        # print(json.dumps(results, indent=2))
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    # Setup environment
    print("Social Media Marketing Automation Bot")
    print("Make sure to create and configure your .env file first")
    # Run the main application
    post_products_to_instagram(94025)

    # .env file setup instructions
"""
# Google AI/Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Instagram API Configuration
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_instagram_business_account_id_here

# Facebook API Configuration
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token_here
FACEBOOK_PAGE_ID=your_facebook_page_id_here
"""