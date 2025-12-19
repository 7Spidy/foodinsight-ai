#!/usr/bin/env python3
"""
FoodInsight AI - Main Food Analysis Script
Polls Notion, analyzes food images via OpenAI, generates PDFs, updates Notion
"""

import os
import sys
import json
import base64
import requests
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from io import BytesIO
import logging

from openai import OpenAI
from pdf_generator import generate_food_infographic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment variables
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize clients
notion_headers = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Notion-Version': '2024-04-04',
    'Content-Type': 'application/json'
}

import httpx
openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    timeout=30.0,
    max_retries=2
)


# Configuration for India-specific nutrition
NUTRITION_CONFIG = {
    'daily_kcal_target': 2000,
    'user_age': 35,
    'user_location': 'Mumbai, India',
    'daily_protein_target': 50,  # grams
    'daily_carbs_target': 250,   # grams
    'daily_fat_target': 65,      # grams
}


def get_notion_database_items() -> list:
    """Fetch all entries from Notion database that haven't been analyzed"""
    url = f'https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query'
    
    # Get all entries, filter locally
    payload = {'page_size': 10}
    
    try:
        response = requests.post(url, headers=notion_headers, json=payload)
        response.raise_for_status()
        results = response.json().get('results', [])
        
        # Filter locally for unanalyzed entries
        unanalyzed = []
        for entry in results:
            properties = entry.get('properties', {})
            analysis_done = properties.get('AI Analysis Done', {})
            
            if analysis_done.get('type') == 'checkbox':
                if not analysis_done.get('checkbox', False):
                    unanalyzed.append(entry)
            else:
                unanalyzed.append(entry)
        
        return unanalyzed
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch Notion database: {e}")
        return []

    
    try:
        response = requests.post(url, headers=notion_headers, json=payload)
        response.raise_for_status()
        return response.json().get('results', [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch Notion database: {e}")
        return []


def download_image_from_notion(file_url: str) -> Optional[bytes]:
    """Download image file from Notion URL"""
    try:
        # Notion file URLs have expiry, we need to include auth header
        headers = {'Authorization': f'Bearer {NOTION_TOKEN}'}
        response = requests.get(file_url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download image: {e}")
        return None


def extract_image_from_notion_entry(entry: Dict) -> Optional[bytes]:
    """Extract and download image from Notion entry"""
    try:
        properties = entry.get('properties', {})
        meal_photo_prop = properties.get('Meal Photo', {})
        
        if meal_photo_prop.get('type') != 'files':
            return None
        
        files = meal_photo_prop.get('files', [])
        if not files:
            return None
        
        file_obj = files[0]
        if file_obj.get('type') == 'file':
            file_url = file_obj.get('file', {}).get('url')
            if file_url:
                return download_image_from_notion(file_url)
    
    except Exception as e:
        logger.error(f"Error extracting image: {e}")
    
    return None


def analyze_food_with_openai(image_data: bytes) -> Optional[Dict[str, Any]]:
    """
    Send food image to OpenAI GPT-4 Vision for analysis
    Returns structured nutrition data
    """
    try:
        # Convert image to base64
        base64_image = base64.standard_b64encode(image_data).decode('utf-8')
        
        # Create prompt for food analysis
        analysis_prompt = f"""You are a professional nutritionist and food analyst. 
Analyze this food image and provide detailed nutritional insights.

User Profile:
- Age: {NUTRITION_CONFIG['user_age']} years
- Location: {NUTRITION_CONFIG['user_location']}
- Daily KCal Target: {NUTRITION_CONFIG['daily_kcal_target']} KCal
- Daily Protein Target: {NUTRITION_CONFIG['daily_protein_target']}g
- Daily Carbs Target: {NUTRITION_CONFIG['daily_carbs_target']}g
- Daily Fat Target: {NUTRITION_CONFIG['daily_fat_target']}g

Please analyze this meal and return a JSON response with:
{{
    "food_name": "Name of the dish (e.g., Chicken Biryani)",
    "estimated_kcal": <estimated total calories as integer>,
    "protein_g": <estimated protein in grams>,
    "carbs_g": <estimated carbohydrates in grams>,
    "fat_g": <estimated fat in grams>,
    "food_score": <health score 0-100 where 100 is perfectly healthy>,
    "ai_insight": "<1-2 sentences about this food's nutritional profile>",
    "healthy_tips": "<1-2 sentences on how to make this meal healthier>",
    "food_type": "<category: vegetarian/non-vegetarian/vegan/etc>",
    "portion_size": "<estimated portion size>"
}}

Be conservative in calorie estimates. Use Indian food nutrition databases when applicable.
Return ONLY valid JSON, no markdown or extra text."""
        
        response = openai_client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {
                    'role': 'user',
                    'content': [
                        {
                            'type': 'text',
                            'text': analysis_prompt
                        },
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': f'data:image/jpeg;base64,{base64_image}',
                                'detail': 'high'
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        # Parse JSON response
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON from response (in case it's wrapped in markdown)
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0]
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0]
        
        analysis = json.loads(response_text)
        logger.info(f"Successfully analyzed food: {analysis.get('food_name')}")
        return analysis
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse OpenAI response as JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Error analyzing food with OpenAI: {e}")
        return None


def update_notion_entry(entry_id: str, analysis: Dict[str, Any], pdf_file_id: Optional[str] = None):
    """Update Notion entry with analysis results"""
    try:
        url = f'https://api.notion.com/v1/pages/{entry_id}'
        
        # Prepare update payload
        payload = {
            'properties': {
                'Food Name': {
                    'title': [
                        {
                            'text': {'content': analysis.get('food_name', 'Unknown')}
                        }
                    ]
                },
                'AI Analysis Done': {
                    'checkbox': True
                },
                'KCal Count': {
                    'number': analysis.get('estimated_kcal', 0)
                },
                'Protein (g)': {
                    'number': analysis.get('protein_g', 0)
                },
                'Carbs (g)': {
                    'number': analysis.get('carbs_g', 0)
                },
                'Fat (g)': {
                    'number': analysis.get('fat_g', 0)
                },
                'Food Score': {
                    'number': analysis.get('food_score', 0)
                },
                'AI Insight': {
                    'rich_text': [
                        {
                            'text': {'content': analysis.get('ai_insight', '')}
                        }
                    ]
                },
                'Healthy Tips': {
                    'rich_text': [
                        {
                            'text': {'content': analysis.get('healthy_tips', '')}
                        }
                    ]
                },
                'Analysis DateTime': {
                    'date': {
                        'start': datetime.now().isoformat()
                    }
                }
            }
        }
        
        response = requests.patch(url, headers=notion_headers, json=payload)
        response.raise_for_status()
        logger.info(f"Updated Notion entry {entry_id}")
        return True
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to update Notion entry: {e}")
        return False


def upload_pdf_to_notion(entry_id: str, pdf_data: bytes, filename: str) -> bool:
    """Upload generated PDF to Notion as file attachment"""
    try:
        # First, create file in Notion (simplified approach)
        # In production, you'd need to handle file uploads more carefully
        # For now, we'll just mark completion and store PDF locally
        logger.info(f"PDF generated for entry {entry_id}: {filename}")
        return True
    
    except Exception as e:
        logger.error(f"Error uploading PDF: {e}")
        return False


def process_food_entry(entry: Dict) -> bool:
    """
    Complete workflow for single food entry:
    1. Extract image from Notion
    2. Analyze with OpenAI
    3. Generate PDF infographic
    4. Update Notion with results
    """
    try:
        entry_id = entry.get('id')
        logger.info(f"Processing entry {entry_id}")
        
        # Step 1: Extract image
        image_data = extract_image_from_notion_entry(entry)
        if not image_data:
            logger.warning(f"No image found in entry {entry_id}")
            return False
        
        # Step 2: Analyze with OpenAI
        analysis = analyze_food_with_openai(image_data)
        if not analysis:
            logger.warning(f"Failed to analyze food in entry {entry_id}")
            return False
        
        # Step 3: Generate PDF infographic
        try:
            pdf_data = generate_food_infographic(
                food_image=image_data,
                analysis=analysis,
                user_config=NUTRITION_CONFIG
            )
        except Exception as e:
            logger.error(f"Failed to generate PDF: {e}")
            pdf_data = None
        
        # Step 4: Update Notion
        success = update_notion_entry(entry_id, analysis)
        
        if success and pdf_data:
            # Save PDF locally for GitHub Actions artifact
            pdf_filename = f"foodinsight_{entry_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            output_dir = Path('artifacts')
            output_dir.mkdir(exist_ok=True)
            
            with open(output_dir / pdf_filename, 'wb') as f:
                f.write(pdf_data)
            
            logger.info(f"PDF saved: {pdf_filename}")
            upload_pdf_to_notion(entry_id, pdf_data, pdf_filename)
        
        return success
    
    except Exception as e:
        logger.error(f"Error processing entry: {e}")
        return False


def main():
    """Main execution function"""
    logger.info("Starting FoodInsight AI analysis...")
    
    # Validate environment variables
    if not all([NOTION_TOKEN, NOTION_DATABASE_ID, OPENAI_API_KEY]):
        logger.error("Missing required environment variables")
        sys.exit(1)
    
    # Fetch unprocessed entries
    entries = get_notion_database_items()
    logger.info(f"Found {len(entries)} unprocessed entries")
    
    if not entries:
        logger.info("No new entries to process")
        return
    
    # Process each entry
    success_count = 0
    for entry in entries:
        if process_food_entry(entry):
            success_count += 1
    
    logger.info(f"Processing complete: {success_count}/{len(entries)} entries processed successfully")


if __name__ == '__main__':
    main()
