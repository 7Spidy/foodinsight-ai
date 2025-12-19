# 🍽️ FoodInsight AI

> Automated food analysis powered by AI, generating beautiful nutrition infographics for your Notion database

## 🎯 What is FoodInsight AI?

FoodInsight AI is an intelligent food logging system that:

1. **Captures** your meals in Notion with photos
2. **Analyzes** them using OpenAI GPT-4 Vision
3. **Generates** beautiful, colorful nutrition infographics (PDFs)
4. **Updates** your Notion database automatically
5. **Runs** completely on GitHub Actions (serverless, cost-efficient)

### Key Features

✅ **Automated 5-minute polling** - Checks for new meals automatically  
✅ **AI-powered food recognition** - Uses GPT-4 Vision for accurate analysis  
✅ **Beautiful PDF infographics** - Modern 2026 design aesthetic  
✅ **India-specific nutrition** - Baseline: 2000 KCal diet for 35-year-old Indian male  
✅ **Zero hosting costs** - Runs on free GitHub Actions tier  
✅ **Minimal API costs** - GPT-4o Mini: ~$0.04/month (50 meals)  
✅ **No databases needed** - Everything in Notion  

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER WORKFLOW                            │
│  1. Take food photo → 2. Upload to Notion → 3. Wait 5 minutes   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Notion Database │
                    │  (New Entry)    │
                    └────────┬────────┘
                             │
                ┌────────────▼────────────┐
                │  GitHub Actions        │
                │  (5-min polling)       │
                └────────┬───────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐  ┌────────────┐  ┌─────────────┐
    │  Image  │  │  OpenAI    │  │ PDF Gen     │
    │ Download│  │ GPT-4 Vision│ │ (ReportLab) │
    └────┬────┘  └──────┬─────┘  └──────┬──────┘
         │              │               │
         └──────────────┼───────────────┘
                        │
                ┌───────▼─────────┐
                │  Notion Update  │
                │  • Food Name    │
                │  • KCal Count   │
                │  • Macros       │
                │  • Food Score   │
                │  • PDF Report   │
                └─────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- GitHub account
- Notion account
- OpenAI API key ($0+ credit needed)

### Setup (5 minutes)

1. **Create Notion Database**
   - Go to [Notion.so](https://notion.so)
   - Create database with fields listed in `DEPLOYMENT_GUIDE.md`
   - Copy database ID and create API integration

2. **Fork/Clone Repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/foodinsight-ai.git
   cd foodinsight-ai
   ```

3. **Add GitHub Secrets**
   - Go to repo → Settings → Secrets
   - Add: `NOTION_TOKEN`, `NOTION_DATABASE_ID`, `OPENAI_API_KEY`

4. **Enable GitHub Actions**
   - Go to Actions tab
   - Click workflow and "Run workflow"

5. **Start Logging**
   - Add new entry to Notion with food photo
   - Wait 5 minutes for analysis
   - See auto-updated entry with PDF

### Detailed Guide
👉 **See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for step-by-step instructions**

---

## 💻 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **API** | Notion API | Database read/write |
| **Orchestration** | GitHub Actions | 5-min polling scheduler |
| **AI Analysis** | OpenAI GPT-4 Vision | Food recognition & nutrition |
| **PDF Generation** | ReportLab, Pillow | Beautiful infographics |
| **Language** | Python 3.11 | Main script logic |
| **Storage** | GitHub Artifacts | PDF backup (optional) |

---

## 📁 Project Structure

```
foodinsight-ai/
├── .github/
│   └── workflows/
│       └── foodinsight.yml           # GitHub Actions workflow (5-min trigger)
│
├── scripts/
│   ├── food_analyzer.py              # Main logic (Notion → OpenAI → PDF → Notion)
│   └── pdf_generator.py              # PDF infographic generation
│
├── requirements.txt                  # Python dependencies
├── DEPLOYMENT_GUIDE.md               # Step-by-step setup guide
├── README.md                         # This file
└── .gitignore
```

---

## 🎨 Design System

The PDF infographics use a modern 2026 aesthetic with vibrant colors:

```
Primary:     Teal (#2DD4BF)
Secondary:   Pink (#F472B6)
Accent 1:    Purple (#A78BFA)
Accent 2:    Amber (#FBBF24)
Success:     Green (#10B981)
Warning:     Orange (#F97316)
Dark BG:     Slate (#0F172A)
Light BG:    Slate (#F8FAFC)
```

---

## 💰 Cost Analysis

### OpenAI API (per meal analysis)
- Input tokens: ~500-700 (image + prompt)
- Output tokens: ~100-150 (analysis response)
- Cost: ~$0.0005-0.0008 per meal
- **Monthly (50 meals):** $0.025-0.04

### GitHub Actions
- **Free tier:** 2,000 workflow minutes/month
- **Our usage:** ~200 minutes/month (5-min polling × 24 × 30)
- **Cost:** $0 (well within free tier)

### Total Monthly Cost
- 50 meals/month: **~$0.04 + free GitHub = $0.04 total**
- 100 meals/month: **~$0.08 + free GitHub = $0.08 total**

---

## 🍽️ Nutrition Configuration

Default baseline (customize in `scripts/food_analyzer.py`):

```python
NUTRITION_CONFIG = {
    'daily_kcal_target': 2000,
    'user_age': 35,
    'user_location': 'Mumbai, India',
    'daily_protein_target': 50,  # grams
    'daily_carbs_target': 250,   # grams
    'daily_fat_target': 65,      # grams
}
```

### Food Score Calculation
- **80-100:** Green (Healthy)
- **60-79:** Amber (Moderate)
- **40-59:** Orange (Less Healthy)
- **0-39:** Red (High Caution)

---

## 📊 Example Output

### PDF Infographic Contains:
- 🍽️ Food name (AI-recognized)
- 📷 Original meal photo
- 🔥 KCal count (large, prominent)
- ⭐ Health score (color-coded)
- 📊 Macro breakdown (protein/carbs/fat with daily targets)
- 💡 AI insight (nutritional highlights)
- 🥗 Healthy tips (how to improve meal)
- 📅 Analysis timestamp

---

## 🔧 Customization

### Change Polling Frequency
Edit `.github/workflows/foodinsight.yml`:
```yaml
schedule:
  - cron: '*/5 * * * *'  # Every 5 minutes
  # - cron: '*/10 * * * *'  # Every 10 minutes
  # - cron: '0 * * * *'     # Every hour
```

### Modify Nutrition Targets
Edit `scripts/food_analyzer.py` `NUTRITION_CONFIG` dictionary

### Change PDF Colors
Edit `scripts/pdf_generator.py` `COLOR_PALETTE` dictionary

### Adjust Analysis Prompt
Edit the `analysis_prompt` variable in `food_analyzer.py` to customize AI behavior

---

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| Workflow not running | Check Actions enabled in Settings |
| "No module named 'openai'" | Run `pip install -r requirements.txt` |
| OpenAI API error | Verify API key and payment method |
| Notion API error | Check token, database ID, and permissions |
| PDF not generating | Check image upload and ReportLab install |
| Analysis takes too long | Reduce `max_tokens` in OpenAI call |

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md#-troubleshooting) for detailed troubleshooting.

---

## 🎯 Future Features (Roadmap)

### Phase 2: Analytics
- [ ] Weekly nutrition reports
- [ ] Macro distribution charts
- [ ] Meal trends analysis
- [ ] Monthly summaries

### Phase 3: Recommendations
- [ ] Recipe suggestions
- [ ] Healthier alternatives
- [ ] Meal plan generation
- [ ] Grocery list auto-generation

### Phase 4: Integrations
- [ ] Apple Health sync
- [ ] Google Fit integration
- [ ] Strava/fitness tracker sync
- [ ] Multi-user support

### Phase 5: Mobile
- [ ] Browser extension
- [ ] Mobile app
- [ ] Push notifications
- [ ] Offline mode

---

## 📝 API Rate Limits

| Service | Limit | Status |
|---------|-------|--------|
| **Notion API** | 100 requests/minute | ✅ Safe |
| **OpenAI API** | 90k tokens/minute (free tier) | ✅ Safe |
| **GitHub Actions** | 2,000 minutes/month | ✅ Safe |

Current usage: **~200 min/month (10%)** of GitHub Actions free tier

---

## 🔐 Security Notes

1. **Never commit secrets** - Use GitHub Secrets only
2. **Rotate API keys** - Regularly update OpenAI keys
3. **Monitor costs** - Check OpenAI dashboard weekly
4. **Rate limiting** - Current setup is within all API limits
5. **Data privacy** - Only Notion API sees food data (encrypted in transit)

---

## 📚 Documentation

- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Complete step-by-step setup
- **Notion API:** https://developers.notion.com
- **OpenAI API:** https://platform.openai.com/docs
- **GitHub Actions:** https://docs.github.com/actions
- **ReportLab:** https://www.reportlab.com/docs

---

## 🤝 Contributing

Have ideas to improve FoodInsight AI?

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 💬 Feedback

Found a bug? Have a feature request? [Open an issue!](https://github.com/YOUR_USERNAME/foodinsight-ai/issues)

---

## 🙏 Acknowledgments

- OpenAI for GPT-4 Vision
- Notion for their excellent API
- GitHub for free Actions
- ReportLab for PDF generation
- The open-source community

---

## 🌟 Show Your Support

If FoodInsight AI helped you track your nutrition better, please consider:
- ⭐ Starring this repository
- 📢 Sharing with friends
- 🐛 Reporting issues
- 💡 Suggesting improvements

**Happy meal logging! 🥗**

---

**Last Updated:** December 2024  
**Version:** 1.0.0  
**Status:** Production Ready ✅
