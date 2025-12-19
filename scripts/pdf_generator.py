#!/usr/bin/env python3
"""
PDF Infographic Generator for FoodInsight AI
Creates beautiful, colorful food analysis infographics
"""

from io import BytesIO
from typing import Dict, Any, Optional
import base64
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import HexColor, Color
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage
import io

# Modern 2026 color palette
COLOR_PALETTE = {
    'primary': '#2DD4BF',      # Teal
    'secondary': '#F472B6',    # Pink
    'accent_1': '#A78BFA',     # Purple
    'accent_2': '#FBBF24',     # Amber
    'dark_bg': '#0F172A',      # Dark slate
    'light_bg': '#F8FAFC',     # Light slate
    'text_dark': '#1E293B',    # Dark text
    'text_light': '#64748B',   # Light text
    'success': '#10B981',      # Green
    'warning': '#F97316',      # Orange
}


def generate_score_color(score: float) -> str:
    """Get color based on food health score (0-100)"""
    if score >= 80:
        return COLOR_PALETTE['success']  # Green
    elif score >= 60:
        return COLOR_PALETTE['accent_2']  # Amber
    elif score >= 40:
        return COLOR_PALETTE['warning']  # Orange
    else:
        return '#EF4444'  # Red


def create_macro_pie_chart(analysis: Dict[str, Any]) -> bytes:
    """
    Create a simple pie chart image showing macro distribution
    Returns PIL Image bytes
    """
    protein = analysis.get('protein_g', 0)
    carbs = analysis.get('carbs_g', 0)
    fat = analysis.get('fat_g', 0)
    
    # Create a simple colored breakdown visualization
    img = Image.new('RGB', (300, 100), color=COLOR_PALETTE['light_bg'])
    draw = ImageDraw.Draw(img)
    
    total = protein + carbs + fat
    if total == 0:
        return img
    
    # Calculate proportions
    protein_width = int(300 * (protein / total))
    carbs_width = int(300 * (carbs / total))
    fat_width = 300 - protein_width - carbs_width
    
    # Draw colored segments
    draw.rectangle([0, 0, protein_width, 100], fill=COLOR_PALETTE['primary'])
    draw.rectangle([protein_width, 0, protein_width + carbs_width, 100], fill=COLOR_PALETTE['secondary'])
    draw.rectangle([protein_width + carbs_width, 0, 300, 100], fill=COLOR_PALETTE['accent_1'])
    
    # Save to bytes
    byte_arr = io.BytesIO()
    img.save(byte_arr, format='PNG')
    byte_arr.seek(0)
    return byte_arr.getvalue()


def create_macro_text_visualization(analysis: Dict[str, Any]) -> str:
    """Create HTML-like macro breakdown text"""
    return f"""
    <b>Protein:</b> {analysis.get('protein_g', 0):.0f}g
    <b>Carbs:</b> {analysis.get('carbs_g', 0):.0f}g
    <b>Fat:</b> {analysis.get('fat_g', 0):.0f}g
    """


def generate_food_infographic(
    food_image: bytes,
    analysis: Dict[str, Any],
    user_config: Dict[str, Any]
) -> Optional[bytes]:
    """
    Generate beautiful PDF infographic with food analysis
    
    Args:
        food_image: Raw image bytes
        analysis: AI analysis dictionary from OpenAI
        user_config: User nutrition configuration
    
    Returns:
        PDF bytes
    """
    
    try:
        # Create PDF document
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=30,
            leftMargin=30,
            topMargin=40,
            bottomMargin=30
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=32,
            textColor=HexColor(COLOR_PALETTE['primary']),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=HexColor(COLOR_PALETTE['text_dark']),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        
        insight_style = ParagraphStyle(
            'CustomInsight',
            parent=styles['BodyText'],
            fontSize=11,
            textColor=HexColor(COLOR_PALETTE['text_light']),
            spaceAfter=10,
            alignment=0  # Left align
        )
        
        # Build PDF content
        content = []
        
        # Title
        food_name = analysis.get('food_name', 'Unknown Food')
        content.append(Paragraph(f"🍽️ {food_name}", title_style))
        content.append(Spacer(1, 0.2*inch))
        
        # Add food image if available
        if food_image:
            try:
                img = Image.open(io.BytesIO(food_image))
                # Resize image to fit PDF
                img.thumbnail((5*inch, 3*inch), Image.Resampling.LANCZOS)
                
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                rl_image = RLImage(img_buffer, width=5*inch, height=3*inch)
                content.append(rl_image)
                content.append(Spacer(1, 0.3*inch))
            except Exception as e:
                print(f"Error adding food image: {e}")
        
        # Calories - Large prominent display
        kcal = analysis.get('estimated_kcal', 0)
        content.append(Paragraph(f"<b>{kcal} KCal</b>", subtitle_style))
        content.append(Spacer(1, 0.15*inch))
        
        # Food Score with color coding
        score = analysis.get('food_score', 0)
        score_color = generate_score_color(score)
        score_style = ParagraphStyle(
            'ScoreStyle',
            parent=styles['Heading2'],
            fontSize=24,
            textColor=HexColor(score_color),
            fontName='Helvetica-Bold'
        )
        content.append(Paragraph(f"Health Score: {score}/100", score_style))
        content.append(Spacer(1, 0.2*inch))
        
        # Macro breakdown table
        content.append(Paragraph("📊 <b>Macronutrient Breakdown</b>", subtitle_style))
        
        macro_data = [
            ['Nutrient', 'Amount', 'Your Daily Target'],
            ['Protein', f"{analysis.get('protein_g', 0):.0f}g", f"{user_config['daily_protein_target']}g"],
            ['Carbohydrates', f"{analysis.get('carbs_g', 0):.0f}g", f"{user_config['daily_carbs_target']}g"],
            ['Fat', f"{analysis.get('fat_g', 0):.0f}g", f"{user_config['daily_fat_target']}g"],
        ]
        
        macro_table = Table(macro_data, colWidths=[2.2*inch, 1.5*inch, 1.8*inch])
        macro_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor(COLOR_PALETTE['primary'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor(COLOR_PALETTE['light_bg'])),
            ('GRID', (0, 0), (-1, -1), 1, HexColor(COLOR_PALETTE['text_light'])),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor(COLOR_PALETTE['light_bg'])]),
        ]))
        
        content.append(macro_table)
        content.append(Spacer(1, 0.3*inch))
        
        # AI Insight
        insight = analysis.get('ai_insight', '')
        if insight:
            content.append(Paragraph("<b>💡 Nutritional Insight</b>", subtitle_style))
            content.append(Paragraph(insight, insight_style))
            content.append(Spacer(1, 0.2*inch))
        
        # Healthy Tips
        tips = analysis.get('healthy_tips', '')
        if tips:
            content.append(Paragraph("<b>🥗 How to Make it Healthier</b>", subtitle_style))
            content.append(Paragraph(tips, insight_style))
            content.append(Spacer(1, 0.2*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=HexColor(COLOR_PALETTE['text_light']),
            alignment=1  # Right align
        )
        content.append(Spacer(1, 0.3*inch))
        from datetime import datetime
        content.append(Paragraph(
            f"Generated by FoodInsight AI • {datetime.now().strftime('%B %d, %Y')}",
            footer_style
        ))
        
        # Build PDF
        doc.build(content)
        
        pdf_buffer.seek(0)
        return pdf_buffer.getvalue()
    
    except Exception as e:
        print(f"Error generating PDF infographic: {e}")
        import traceback
        traceback.print_exc()
        return None
