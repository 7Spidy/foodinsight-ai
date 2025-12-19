#!/usr/bin/env python3
"""
FoodInsight AI - Configuration Template
Copy this to create your custom configuration
"""

# ============================================================================
# NOTION CONFIGURATION
# ============================================================================

# Your Notion workspace token (from https://www.notion.so/my-integrations)
# Format: secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_TOKEN = "YOUR_NOTION_TOKEN_HERE"

# Your Notion database ID (extract from database URL)
# Format: 32-character UUID (e.g., a1b2c3d4e5f67890abcdef1234567890)
NOTION_DATABASE_ID = "YOUR_DATABASE_ID_HERE"

# Notion API version (generally safe to leave as-is)
NOTION_API_VERSION = "2024-04-04"

# ============================================================================
# OPENAI CONFIGURATION
# ============================================================================

# Your OpenAI API key (from https://platform.openai.com/api/keys)
# Format: sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"

# Model to use for food analysis
# Recommended: gpt-4o-mini (cost-efficient, excellent for vision)
# Alternative: gpt-4-vision-preview (more expensive, similar results)
OPENAI_MODEL = "gpt-4o-mini"

# Max tokens for response (helps control costs)
OPENAI_MAX_TOKENS = 1000

# Temperature for AI responses (0 = deterministic, 1 = creative)
# 0.3 recommended for consistent nutrition analysis
OPENAI_TEMPERATURE = 0.3

# ============================================================================
# NUTRITION CONFIGURATION (Customize for your profile)
# ============================================================================

NUTRITION_CONFIG = {
    # Daily targets
    'daily_kcal_target': 2000,      # Calories (2000 KCal for Indian baseline)
    'daily_protein_target': 50,     # Grams
    'daily_carbs_target': 250,      # Grams
    'daily_fat_target': 65,         # Grams
    
    # User profile (for AI context)
    'user_age': 35,                 # Age in years
    'user_location': 'Mumbai, India',  # Location (helps with local food recognition)
    'user_gender': 'Male',          # For more accurate nutrition estimates
    'user_height_cm': 175,          # Height (optional, for BMI calculations)
    'user_weight_kg': 75,           # Weight (optional, for calorie adjustment)
    
    # Dietary preferences (for recommendations)
    'diet_type': 'balanced',        # Options: balanced, vegetarian, vegan, keto, low-carb
    'dietary_restrictions': [],     # E.g., ['gluten-free', 'dairy-free', 'nuts']
    
    # Health goals
    'health_goal': 'maintenance',   # Options: weight-loss, muscle-gain, maintenance
    'activity_level': 'moderate',   # Options: sedentary, light, moderate, active, very-active
}

# ============================================================================
# PDF GENERATION CONFIGURATION
# ============================================================================

# Modern 2026 color palette (customize here)
PDF_COLOR_PALETTE = {
    'primary': '#2DD4BF',           # Teal (main brand color)
    'secondary': '#F472B6',         # Pink (accent)
    'accent_1': '#A78BFA',          # Purple
    'accent_2': '#FBBF24',          # Amber
    'dark_bg': '#0F172A',           # Dark slate
    'light_bg': '#F8FAFC',          # Light slate
    'text_dark': '#1E293B',         # Dark text
    'text_light': '#64748B',        # Light gray text
    'success': '#10B981',           # Green (healthy)
    'warning': '#F97316',           # Orange (caution)
    'danger': '#EF4444',            # Red (unhealthy)
}

# Food score thresholds (used for color coding)
FOOD_SCORE_THRESHOLDS = {
    'excellent': 80,    # Green - Score >= 80
    'good': 60,         # Amber - Score >= 60
    'fair': 40,         # Orange - Score >= 40
    'poor': 0,          # Red - Score < 40
}

# PDF page size (letter = 8.5" x 11", A4 = 210mm x 297mm)
PDF_PAGE_SIZE = 'letter'

# ============================================================================
# GITHUB ACTIONS CONFIGURATION
# ============================================================================

# Polling frequency (cron format)
# Examples:
#   '*/5 * * * *'    = Every 5 minutes
#   '*/30 * * * *'   = Every 30 minutes
#   '0 * * * *'      = Every hour
#   '0 8 * * *'      = Daily at 8 AM UTC
#   '0 8 * * 1'      = Weekly on Monday at 8 AM UTC
POLLING_FREQUENCY = "*/5 * * * *"

# Max entries to process per run (prevents rate limiting)
MAX_ENTRIES_PER_RUN = 10

# Timeout for image download (seconds)
IMAGE_DOWNLOAD_TIMEOUT = 10

# Timeout for OpenAI API call (seconds)
OPENAI_TIMEOUT = 30

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# Log format
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# ============================================================================
# FEATURE FLAGS (Experimental features)
# ============================================================================

# Generate PDF infographics (set False to skip PDF generation for faster processing)
ENABLE_PDF_GENERATION = True

# Auto-detect dietary restrictions from meal analysis
ENABLE_ALLERGY_DETECTION = True

# Calculate adjusted calorie targets based on activity level
ENABLE_DYNAMIC_TARGETS = False

# Use advanced nutrition models for better accuracy
ENABLE_ADVANCED_ANALYSIS = False  # Requires gpt-4-turbo or better

# Save meal images locally for debugging
ENABLE_LOCAL_IMAGE_STORAGE = False

# Upload PDFs to Notion (requires additional setup)
ENABLE_NOTION_PDF_UPLOAD = False

# ============================================================================
# OPTIONAL: INTEGRATIONS (Future features)
# ============================================================================

# Apple Health Integration (for future use)
APPLE_HEALTH_ENABLED = False
# APPLE_HEALTH_USER_ID = "your_user_id"

# Google Fit Integration (for future use)
GOOGLE_FIT_ENABLED = False
# GOOGLE_FIT_CLIENT_ID = "your_client_id"
# GOOGLE_FIT_CLIENT_SECRET = "your_client_secret"

# Strava Integration (for future use)
STRAVA_ENABLED = False
# STRAVA_ACCESS_TOKEN = "your_token"

# ============================================================================
# NOTES FOR CUSTOMIZATION
# ============================================================================

"""
SETTING UP YOUR CONFIGURATION:

1. Copy this file to your project: cp config_template.py config.py
2. Replace YOUR_*_HERE values with actual credentials
3. Customize NUTRITION_CONFIG for your profile
4. Adjust colors in PDF_COLOR_PALETTE
5. Set POLLING_FREQUENCY based on your needs

FOR GITHUB ACTIONS:
- Never commit this file with secrets!
- Use GitHub Secrets instead (Settings → Secrets and variables)
- Reference in workflow: ${{ secrets.NOTION_TOKEN }}

ENVIRONMENT VARIABLES (Recommended for GitHub Actions):
- NOTION_TOKEN
- NOTION_DATABASE_ID
- OPENAI_API_KEY

LOCAL DEVELOPMENT:
- Create .env file with credentials
- Load with: from dotenv import load_dotenv; load_dotenv()

COST OPTIMIZATION:
- Reduce OPENAI_MAX_TOKENS to lower costs (min: 300)
- Increase POLLING_FREQUENCY to save GitHub Actions minutes
- Use gpt-4o-mini for cost efficiency (~$0.04/month)
- Monitor openai.com/account/billing/overview weekly

NUTRITION TARGETS:
- Indian baseline (2000 KCal): Provided as default
- Adjust based on:
  * Your activity level (activity_level field)
  * Your goals (health_goal field)
  * Your body metrics (height, weight)
- Use online calculators for personalized TDEE
"""

# ============================================================================
# VALIDATE CONFIGURATION
# ============================================================================

def validate_config():
    """Check that all required fields are set"""
    required_fields = [
        NOTION_TOKEN,
        NOTION_DATABASE_ID,
        OPENAI_API_KEY,
    ]
    
    if any(field == "YOUR_*_HERE" for field in required_fields):
        raise ValueError("⚠️  Configuration incomplete! Update the *_HERE placeholders")
    
    print("✅ Configuration validated successfully")

if __name__ == "__main__":
    validate_config()
