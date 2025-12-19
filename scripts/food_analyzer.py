import os
import logging
from datetime import datetime
import requests
from openai import OpenAI
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get environment variables
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# DEBUG: Log secret values (without exposing full secrets)
logger.info(f"NOTION_TOKEN: {NOTION_TOKEN[:20] if NOTION_TOKEN else 'NOT SET'}...")
logger.info(f"NOTION_DATABASE_ID: {NOTION_DATABASE_ID} (length: {len(NOTION_DATABASE_ID) if NOTION_DATABASE_ID else 0})")
logger.info(f"OPENAI_API_KEY: {OPENAI_API_KEY[:20] if OPENAI_API_KEY else 'NOT SET'}...")

# Verify database ID is 32 chars
if NOTION_DATABASE_ID and len(NOTION_DATABASE_ID) != 32:
    logger.error(f"❌ DATABASE ID IS WRONG LENGTH: {len(NOTION_DATABASE_ID)} chars (should be 32)")
    logger.error(f"Database ID: {NOTION_DATABASE_ID}")
    exit(1)

# Set up headers
notion_headers = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Notion-Version': '2025-09-03',
    'Content-Type': 'application/json'
}

# Initialize OpenAI
openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    http_client=httpx.Client()
)

logger.info("Starting FoodInsight AI analysis...")

def get_notion_database_items() -> list:
    """Fetch all entries from Notion database"""
    url = f'https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query'
    
    logger.info(f"Request URL: {url}")
    logger.info(f"Headers: Authorization=*****, Notion-Version=2025-09-03, Content-Type=application/json")
    
    payload = {}
    
    try:
        response = requests.post(url, headers=notion_headers, json=payload, timeout=10)
        logger.info(f"Response Status: {response.status_code}")
        response.raise_for_status()
        results = response.json().get('results', [])
        logger.info(f"✅ Fetched {len(results)} entries from Notion")
        
        # Filter locally for unanalyzed entries
        unanalyzed = []
        for entry in results:
            try:
                properties = entry.get('properties', {})
                if 'AI Analysis Done' in properties:
                    checkbox_value = properties['AI Analysis Done'].get('checkbox', False)
                    if not checkbox_value:
                        unanalyzed.append(entry)
                else:
                    unanalyzed.append(entry)
            except Exception as e:
                logger.warning(f"Error processing entry: {e}")
                continue
        
        logger.info(f"Found {len(unanalyzed)} unanalyzed entries")
        return unanalyzed
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch Notion database: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response Status: {e.response.status_code}")
            logger.error(f"Response: {e.response.text}")
        return []

# Run the function
get_notion_database_items()
logger.info("Completed!")

def extract_meal_photo_url(entry):
    """Extract the meal photo URL from Notion entry"""
    try:
        properties = entry.get('properties', {})
        meal_photo = properties.get('Meal Photo', {})
        
        if meal_photo.get('type') == 'files':
            files = meal_photo.get('files', [])
            if files and len(files) > 0:
                file_obj = files[0]
                if 'file' in file_obj:
                    return file_obj['file'].get('url')
                elif 'external' in file_obj:
                    return file_obj['external'].get('url')
        return None
    except Exception as e:
        logger.warning(f"Error extracting meal photo: {e}")
        return None

def analyze_food_image(image_url):
    """Send image to OpenAI for analysis"""
    try:
        logger.info(f"Analyzing food image: {image_url}")
        
        message = openai_client.messages.create(
            model="gpt-4o-mini",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this food image and provide the following in JSON format:
                            {
                                "food_name": "name of the food",
                                "estimated_calories": number,
                                "protein_g": number,
                                "carbs_g": number,
                                "fat_g": number,
                                "health_score": number between 0-100,
                                "insight": "one sentence insight about this meal",
                                "healthy_tips": "one suggestion to make this healthier"
                            }
                            
                            For the health_score, consider:
                            - Nutritional balance (protein, carbs, healthy fats)
                            - Calories relative to 2000 KCal daily target (35-year-old male, Mumbai)
                            - Presence of vegetables, whole grains, lean proteins
                            - Portion size reasonableness
                            
                            Score: 80-100 = Excellent, 60-79 = Good, 40-59 = Fair, 0-39 = Needs Improvement"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]
        )
        
        # Extract JSON from response
        response_text = message.content[0].text
        logger.info(f"OpenAI Response: {response_text}")
        
        # Try to parse JSON
        try:
            analysis = json.loads(response_text)
        except json.JSONDecodeError:
            # If response is not pure JSON, extract JSON from text
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                logger.error("Could not extract JSON from OpenAI response")
                return None
        
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing food image: {e}")
        return None

def update_notion_entry(entry_id, analysis, pdf_url=None):
    """Update Notion entry with analysis results"""
    try:
        url = f'https://api.notion.com/v1/pages/{entry_id}'
        
        payload = {
            "properties": {
                "KCal Count": {
                    "number": analysis.get('estimated_calories', 0)
                },
                "Protein (g)": {
                    "number": analysis.get('protein_g', 0)
                },
                "Carbs (g)": {
                    "number": analysis.get('carbs_g', 0)
                },
                "Fat (g)": {
                    "number": analysis.get('fat_g', 0)
                },
                "Food Score": {
                    "number": analysis.get('health_score', 0)
                },
                "AI Insight": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": analysis.get('insight', '')
                            }
                        }
                    ]
                },
                "Healthy Tips": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": analysis.get('healthy_tips', '')
                            }
                        }
                    ]
                },
                "AI Analysis Done": {
                    "checkbox": True
                }
            }
        }
        
        # Add PDF report if available
        if pdf_url:
            payload["properties"]["PDF Report"] = {
                "files": [
                    {
                        "type": "external",
                        "name": "Food Analysis Report",
                        "external": {
                            "url": pdf_url
                        }
                    }
                ]
            }
        
        response = requests.patch(url, headers=notion_headers, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"✅ Updated Notion entry: {entry_id}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to update Notion entry: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Response: {e.response.text}")
        return False

def main():
    logger.info("Starting FoodInsight AI analysis...")
    
    # Validate environment variables
    if not NOTION_TOKEN or not NOTION_DATABASE_ID or not OPENAI_API_KEY:
        logger.error("Missing required environment variables")
        return
    
    # Fetch unanalyzed entries
    entries = get_notion_database_items()
    logger.info(f"Found {len(entries)} unprocessed entries")
    
    if not entries:
        logger.info("No new entries to process")
        return
    
    # Process each entry
    for entry in entries:
        try:
            entry_id = entry['id']
            properties = entry['properties']
            food_name = properties.get('Food Name', {}).get('title', [{}])[0].get('text', {}).get('content', 'Unknown')
            
            logger.info(f"Processing: {food_name}")
            
            # Extract meal photo URL
            meal_photo_url = extract_meal_photo_url(entry)
            if not meal_photo_url:
                logger.warning(f"No meal photo found for {food_name}")
                continue
            
            # Analyze food image
            analysis = analyze_food_image(meal_photo_url)
            if not analysis:
                logger.error(f"Failed to analyze {food_name}")
                continue
            
            logger.info(f"Analysis results: {analysis}")
            
            # Generate PDF infographic
            try:
                pdf_path = generate_food_infographic(food_name, analysis, meal_photo_url)
                logger.info(f"Generated PDF: {pdf_path}")
            except Exception as e:
                logger.warning(f"PDF generation failed: {e}")
                pdf_path = None
            
            # Update Notion entry
            update_notion_entry(entry_id, analysis, pdf_url=pdf_path)
            
            logger.info(f"✅ Completed processing: {food_name}")
            
        except Exception as e:
            logger.error(f"Error processing entry: {e}")
            continue

if __name__ == "__main__":
    main()
