#!/usr/bin/env python3
"""
Generate diverse test documents for comprehensive RAG testing
Creates PDFs, Excel files, images with text, and more
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
import json

OUTPUT_DIR = "/app/backend/knowledge_base/internal"

def create_financial_report_pdf():
    """Create a detailed financial report PDF"""
    filename = os.path.join(OUTPUT_DIR, "financial_report_2024.pdf")
    
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30
    )
    story.append(Paragraph("Annual Financial Report 2024", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    summary_text = """
    This financial report presents the performance of TechCorp Inc. for fiscal year 2024.
    The company achieved revenue of $12.5 million, representing a 25% increase from the previous year.
    Net profit margin improved to 18%, demonstrating strong operational efficiency.
    Key growth drivers included expansion into new markets and successful product launches.
    """
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Financial Data Table
    story.append(Paragraph("Key Financial Metrics", styles['Heading2']))
    data = [
        ['Metric', 'Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024', 'Total'],
        ['Revenue ($M)', '2.8', '3.1', '3.2', '3.4', '12.5'],
        ['Expenses ($M)', '2.3', '2.5', '2.6', '2.8', '10.2'],
        ['Net Profit ($M)', '0.5', '0.6', '0.6', '0.6', '2.3'],
        ['Profit Margin', '18%', '19%', '19%', '18%', '18%'],
    ]
    
    table = Table(data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 0.3*inch))
    
    # Strategic Initiatives
    story.append(Paragraph("Strategic Initiatives 2025", styles['Heading2']))
    initiatives = """
    1. Digital Transformation: Invest $2M in AI and machine learning capabilities
    2. Market Expansion: Enter Asian markets with focus on Japan and South Korea
    3. Product Innovation: Launch three new product lines in Q2 2025
    4. Sustainability: Achieve carbon neutrality by end of 2025
    5. Workforce Development: Hire 50 new employees and implement upskilling programs
    """
    story.append(Paragraph(initiatives, styles['Normal']))
    
    doc.build(story)
    print(f"✓ Created: {filename}")

def create_technical_specification_pdf():
    """Create a technical specification document"""
    filename = os.path.join(OUTPUT_DIR, "api_technical_spec.pdf")
    
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=10,
        backgroundColor=colors.lightgrey,
        borderPadding=10
    )
    
    story.append(Paragraph("REST API Technical Specification", styles['Title']))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("1. Authentication API", styles['Heading2']))
    story.append(Paragraph("Endpoint: POST /api/auth/login", styles['Heading3']))
    story.append(Paragraph("Request Body:", styles['Normal']))
    story.append(Paragraph('{"username": "user@example.com", "password": "securepass"}', code_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Response:", styles['Normal']))
    story.append(Paragraph('{"token": "eyJhbGc...", "expires_in": 3600}', code_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("2. User Management API", styles['Heading2']))
    story.append(Paragraph("Endpoint: GET /api/users/{id}", styles['Heading3']))
    story.append(Paragraph("Description: Retrieve user profile information", styles['Normal']))
    story.append(Paragraph("Authorization: Bearer token required", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("3. Data Processing API", styles['Heading2']))
    story.append(Paragraph("Endpoint: POST /api/process/document", styles['Heading3']))
    story.append(Paragraph("Supports file formats: PDF, DOCX, XLSX, PNG, JPEG", styles['Normal']))
    story.append(Paragraph("Maximum file size: 10MB", styles['Normal']))
    story.append(Paragraph("Processing time: 2-30 seconds depending on file size", styles['Normal']))
    
    doc.build(story)
    print(f"✓ Created: {filename}")

def create_employee_database_excel():
    """Create an employee database Excel file"""
    filename = os.path.join(OUTPUT_DIR, "employee_database.xlsx")
    
    employees = {
        'Employee_ID': ['EMP001', 'EMP002', 'EMP003', 'EMP004', 'EMP005', 'EMP006'],
        'Name': ['Alice Johnson', 'Bob Smith', 'Carol Williams', 'David Brown', 'Emma Davis', 'Frank Miller'],
        'Department': ['Engineering', 'Marketing', 'Sales', 'Engineering', 'HR', 'Finance'],
        'Position': ['Senior Engineer', 'Marketing Manager', 'Sales Rep', 'Junior Engineer', 'HR Specialist', 'Financial Analyst'],
        'Salary': [95000, 78000, 65000, 72000, 68000, 75000],
        'Years_Experience': [8, 6, 3, 2, 5, 7],
        'Performance_Rating': [4.5, 4.2, 3.8, 4.0, 4.3, 4.6]
    }
    
    df = pd.DataFrame(employees)
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Employees', index=False)
        
        # Add summary sheet
        summary = {
            'Metric': ['Total Employees', 'Average Salary', 'Average Experience', 'Avg Performance'],
            'Value': [len(df), f"${df['Salary'].mean():,.0f}", f"{df['Years_Experience'].mean():.1f} years", f"{df['Performance_Rating'].mean():.2f}/5.0"]
        }
        pd.DataFrame(summary).to_excel(writer, sheet_name='Summary', index=False)
    
    print(f"✓ Created: {filename}")

def create_product_inventory_excel():
    """Create a product inventory Excel file"""
    filename = os.path.join(OUTPUT_DIR, "product_inventory.xlsx")
    
    products = {
        'SKU': ['SKU-A001', 'SKU-A002', 'SKU-B001', 'SKU-B002', 'SKU-C001'],
        'Product_Name': ['Laptop Pro 15"', 'Wireless Mouse', 'USB-C Cable', 'Keyboard Mechanical', 'Monitor 27"'],
        'Category': ['Electronics', 'Accessories', 'Accessories', 'Accessories', 'Electronics'],
        'Unit_Price': [1299.99, 29.99, 15.99, 89.99, 349.99],
        'Quantity_In_Stock': [45, 230, 450, 120, 78],
        'Reorder_Level': [20, 100, 200, 50, 30],
        'Supplier': ['TechSupply Co', 'AccessPlus', 'AccessPlus', 'KeyTech Inc', 'DisplayPro']
    }
    
    df = pd.DataFrame(products)
    df['Total_Value'] = df['Unit_Price'] * df['Quantity_In_Stock']
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Inventory', index=False)
    
    print(f"✓ Created: {filename}")

def create_image_with_text():
    """Create images with text for OCR testing"""
    
    # Image 1: Invoice
    img1 = Image.new('RGB', (800, 600), color='white')
    draw1 = ImageDraw.Draw(img1)
    
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_normal = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font_title = ImageFont.load_default()
        font_normal = ImageFont.load_default()
    
    draw1.text((50, 30), "INVOICE #INV-2024-001", fill='black', font=font_title)
    draw1.text((50, 100), "Bill To: Acme Corporation", fill='black', font=font_normal)
    draw1.text((50, 140), "Date: October 8, 2024", fill='black', font=font_normal)
    draw1.text((50, 180), "Amount Due: $5,450.00", fill='black', font=font_normal)
    draw1.text((50, 250), "Items:", fill='black', font=font_normal)
    draw1.text((50, 290), "1. Consulting Services - $3,000.00", fill='black', font=font_normal)
    draw1.text((50, 330), "2. Software License - $2,000.00", fill='black', font=font_normal)
    draw1.text((50, 370), "3. Support Package - $450.00", fill='black', font=font_normal)
    draw1.text((50, 450), "Payment Terms: Net 30 days", fill='black', font=font_normal)
    
    img1.save(os.path.join(OUTPUT_DIR, "invoice_ocr_test.png"))
    print(f"✓ Created: invoice_ocr_test.png")
    
    # Image 2: Meeting Notes
    img2 = Image.new('RGB', (800, 600), color='white')
    draw2 = ImageDraw.Draw(img2)
    
    draw2.text((50, 30), "MEETING NOTES - Q4 Planning", fill='black', font=font_title)
    draw2.text((50, 100), "Date: October 5, 2024", fill='black', font=font_normal)
    draw2.text((50, 140), "Attendees: Sarah, Mike, Jennifer, Tom", fill='black', font=font_normal)
    draw2.text((50, 200), "Key Discussion Points:", fill='black', font=font_normal)
    draw2.text((50, 240), "• Budget allocation for new projects", fill='black', font=font_normal)
    draw2.text((50, 280), "• Hiring timeline for Q1 2025", fill='black', font=font_normal)
    draw2.text((50, 320), "• Marketing campaign strategy", fill='black', font=font_normal)
    draw2.text((50, 360), "• Product roadmap review", fill='black', font=font_normal)
    draw2.text((50, 420), "Action Items: Schedule follow-up", fill='black', font=font_normal)
    
    img2.save(os.path.join(OUTPUT_DIR, "meeting_notes_ocr.png"))
    print(f"✓ Created: meeting_notes_ocr.png")

def create_config_json():
    """Create a configuration JSON file"""
    filename = os.path.join(OUTPUT_DIR, "app_config.json")
    
    config = {
        "application": {
            "name": "DataAnalyzer Pro",
            "version": "2.5.3",
            "environment": "production"
        },
        "database": {
            "host": "db.example.com",
            "port": 5432,
            "name": "analytics_db",
            "pool_size": 20,
            "timeout": 30
        },
        "api": {
            "base_url": "https://api.example.com",
            "version": "v2",
            "rate_limit": 1000,
            "endpoints": {
                "users": "/api/v2/users",
                "data": "/api/v2/data",
                "reports": "/api/v2/reports"
            }
        },
        "features": {
            "authentication": True,
            "real_time_processing": True,
            "batch_processing": True,
            "machine_learning": False
        },
        "logging": {
            "level": "INFO",
            "format": "json",
            "retention_days": 90
        }
    }
    
    with open(filename, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Created: {filename}")

def create_research_notes():
    """Create research notes text file"""
    filename = os.path.join(OUTPUT_DIR, "research_notes.txt")
    
    content = """RESEARCH NOTES - Machine Learning Project

Project: Customer Churn Prediction Model
Date Started: September 15, 2024
Team Lead: Dr. Sarah Chen

OBJECTIVE:
Develop a machine learning model to predict customer churn with 85%+ accuracy.
Focus on identifying early warning signs and actionable insights for retention.

DATA SOURCES:
1. Customer transaction history (5 years)
2. Customer service interaction logs
3. Product usage analytics
4. Customer demographic information
5. Survey responses and feedback

METHODOLOGY:
- Feature engineering: Created 47 features from raw data
- Algorithms tested: Random Forest, XGBoost, Neural Networks
- Cross-validation: 5-fold stratified
- Train/test split: 80/20

PRELIMINARY RESULTS:
- Random Forest: 82.3% accuracy, 0.79 F1-score
- XGBoost: 84.7% accuracy, 0.82 F1-score (BEST)
- Neural Network: 81.5% accuracy, 0.78 F1-score

KEY FINDINGS:
1. Customer service call frequency is the strongest predictor
2. Recent price increases correlate with churn risk
3. Product feature usage decline precedes churn by avg 45 days
4. Age and tenure show non-linear relationships

NEXT STEPS:
- Hyperparameter tuning for XGBoost model
- Feature importance analysis
- Deploy model to staging environment
- A/B test intervention strategies

NOTES FOR DISCUSSION:
- Consider real-time scoring vs batch processing
- Integration with CRM system requirements
- Monitoring and retraining schedule
- Ethical considerations for automated interventions
"""
    
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f"✓ Created: {filename}")

def main():
    print("="*70)
    print("  Generating Diverse Test Documents for RAG Testing")
    print("="*70)
    print()
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create documents
    create_financial_report_pdf()
    create_technical_specification_pdf()
    create_employee_database_excel()
    create_product_inventory_excel()
    create_image_with_text()
    create_config_json()
    create_research_notes()
    
    print()
    print("="*70)
    print("  ✅ All test documents created successfully!")
    print("="*70)
    print(f"  Output directory: {OUTPUT_DIR}")
    print()

if __name__ == "__main__":
    main()
