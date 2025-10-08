#!/usr/bin/env python3
"""
Create Challenging Test Documents for RAG System Testing
Generates complex documents with various edge cases and challenging content
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import random
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Directory setup
INTERNAL_KB = Path("/app/backend/knowledge_base/internal")
EXTERNAL_KB = Path("/app/backend/knowledge_base/external")
INTERNAL_KB.mkdir(exist_ok=True, parents=True)
EXTERNAL_KB.mkdir(exist_ok=True, parents=True)

def create_complex_financial_report():
    """Create a complex multi-page financial report PDF with tables, charts metadata"""
    file_path = INTERNAL_KB / "complex_financial_report_2024_q3.pdf"
    
    doc = SimpleDocTemplate(str(file_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center
    )
    story.append(Paragraph("NEURALCORP FINANCIAL REPORT Q3 2024", title_style))
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("EXECUTIVE SUMMARY", styles['Heading2']))
    summary_text = """
    NeuralCorp achieved exceptional financial performance in Q3 2024, with total revenue reaching $47.3 million, 
    representing a 34.2% year-over-year growth. Our AI-powered products division contributed $29.8 million (63% of total revenue), 
    while the consulting services division generated $17.5 million. Net profit margin improved to 18.7%, up from 14.3% in Q3 2023.
    
    Key Performance Indicators:
    • EBITDA: $12.4 million (26.2% margin)
    • Free Cash Flow: $8.9 million
    • Customer Acquisition Cost (CAC): $1,240 (down 15% from Q2)
    • Customer Lifetime Value (CLV): $18,700 (up 22% from Q2)
    • Monthly Recurring Revenue (MRR): $3.2 million (28% growth rate)
    """
    story.append(Paragraph(summary_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Revenue Table
    story.append(Paragraph("REVENUE BREAKDOWN BY DIVISION", styles['Heading2']))
    revenue_data = [
        ['Division', 'Q3 2024 ($M)', 'Q3 2023 ($M)', 'Growth %', 'Margin %'],
        ['AI Products', '29.8', '21.2', '40.6%', '24.1%'],
        ['Consulting Services', '17.5', '14.1', '24.1%', '12.8%'],
        ['Software Licenses', '0.0', '0.0', '0.0%', '0.0%'],
        ['Total', '47.3', '35.3', '34.0%', '18.7%']
    ]
    
    revenue_table = Table(revenue_data)
    revenue_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(revenue_table)
    story.append(Spacer(1, 20))
    
    # CEO Statement
    story.append(Paragraph("CEO STATEMENT", styles['Heading2']))
    ceo_text = """
    "Our Q3 performance demonstrates NeuralCorp's ability to execute on our 
    strategic vision while maintaining strong financial discipline. We are well-positioned 
    for continued growth and market leadership in the AI solutions space."
    - Alexandra Chen, Chief Executive Officer
    
    "The 34% revenue growth coupled with improved margins reflects our operational 
    excellence and scalable business model. Our strong balance sheet provides flexibility 
    for strategic investments and potential acquisitions."  
    - Robert Kumar, Chief Financial Officer
    """
    story.append(Paragraph(ceo_text, styles['Normal']))
    
    doc.build(story)
    print(f"✓ Created complex financial report: {file_path}")
    return file_path

def create_technical_architecture_document():
    """Create a complex technical architecture document"""
    file_path = INTERNAL_KB / "microservices_architecture_spec_v2.pdf"
    
    doc = SimpleDocTemplate(str(file_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    story.append(Paragraph("NEURAL PLATFORM MICROSERVICES ARCHITECTURE", styles['Title']))
    story.append(Spacer(1, 30))
    
    # Document metadata
    metadata_text = """
    Document Version: 2.3.1
    Last Updated: October 8, 2024
    Prepared by: System Architecture Team
    Approved by: Sarah Mitchell, CTO
    Classification: Internal Technical Documentation
    Review Cycle: Quarterly
    """
    story.append(Paragraph(metadata_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Architecture Overview
    story.append(Paragraph("ARCHITECTURE OVERVIEW", styles['Heading1']))
    overview_text = """
    The Neural Platform employs a distributed microservices architecture designed for scalability, 
    fault tolerance, and rapid deployment. The system consists of 23 core services organized into 
    6 primary domains, each responsible for specific business capabilities.
    
    Core Design Principles:
    • Domain-Driven Design (DDD) with bounded contexts
    • Event-driven architecture using Apache Kafka for inter-service communication  
    • API-first design with OpenAPI 3.0 specifications
    • Zero-trust security model with mutual TLS authentication
    • Cloud-native deployment using Kubernetes and Docker containers
    • Observability-first approach with distributed tracing and metrics
    """
    story.append(Paragraph(overview_text, styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Service Catalog
    story.append(Paragraph("MICROSERVICES CATALOG", styles['Heading2']))
    
    services_data = [
        ['Service Name', 'Domain', 'Technology Stack', 'Database', 'API Endpoints', 'Status'],
        ['user-authentication-service', 'Identity', 'Java 17, Spring Boot 3.1', 'PostgreSQL 15', '12', 'Production'],
        ['user-profile-service', 'Identity', 'Node.js 18, Express.js', 'MongoDB 6.0', '8', 'Production'],
        ['ai-inference-engine', 'AI/ML', 'Python 3.11, FastAPI', 'Redis 7.0', '15', 'Production'],
        ['model-training-service', 'AI/ML', 'Python 3.11, MLflow', 'PostgreSQL 15', '6', 'Beta'],
        ['data-ingestion-service', 'Data', 'Go 1.21, Gin', 'ClickHouse 23.3', '10', 'Production'],
        ['real-time-analytics', 'Analytics', 'Scala 2.13, Akka', 'Apache Cassandra', '7', 'Production'],
        ['notification-gateway', 'Communication', 'Node.js 18, Express.js', 'Redis 7.0', '5', 'Production'],
        ['billing-management', 'Finance', 'Java 17, Spring Boot 3.1', 'PostgreSQL 15', '18', 'Production'],
        ['audit-logging-service', 'Security', 'Go 1.21, Echo', 'Elasticsearch 8.8', '4', 'Production'],
        ['file-processing-service', 'Storage', 'Python 3.11, Celery', 'MinIO S3', '9', 'Production']
    ]
    
    services_table = Table(services_data, colWidths=[1.5*inch, 0.8*inch, 1.3*inch, 1*inch, 0.7*inch, 0.7*inch])
    services_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    story.append(services_table)
    
    doc.build(story)
    print(f"✓ Created technical architecture document: {file_path}")
    return file_path

def create_complex_spreadsheet_with_formulas():
    """Create complex Excel spreadsheet with multiple sheets, formulas, and data types"""
    file_path = INTERNAL_KB / "enterprise_data_analysis_2024.xlsx"
    
    # Create Excel writer object
    with pd.ExcelWriter(str(file_path), engine='xlsxwriter') as writer:
        
        # Sheet 1: Employee Performance Data
        employee_data = []
        departments = ['Engineering', 'Sales', 'Marketing', 'Finance', 'HR', 'Operations', 'Customer Success']
        positions = {
            'Engineering': ['Senior Developer', 'Junior Developer', 'DevOps Engineer', 'QA Engineer', 'Team Lead'],
            'Sales': ['Account Executive', 'Sales Manager', 'SDR', 'Sales Director', 'Regional Manager'],
            'Marketing': ['Marketing Manager', 'Content Creator', 'SEO Specialist', 'Campaign Manager', 'Brand Manager'],
            'Finance': ['Financial Analyst', 'Accountant', 'Controller', 'CFO', 'Payroll Specialist'],
            'HR': ['HR Manager', 'Recruiter', 'HR Coordinator', 'Learning Specialist', 'HR Director'],
            'Operations': ['Operations Manager', 'Process Analyst', 'Project Manager', 'Operations Director'],
            'Customer Success': ['CSM', 'Support Specialist', 'Success Manager', 'Technical Support']
        }
        
        employee_id = 1000
        for dept in departments:
            for i in range(random.randint(8, 15)):
                position = random.choice(positions[dept])
                base_salary = random.randint(45000, 180000)
                performance_score = round(random.uniform(2.5, 4.8), 2)
                years_experience = random.randint(1, 15)
                bonus_pct = round(random.uniform(0.05, 0.25), 3)
                
                employee_data.append({
                    'Employee_ID': f'EMP{employee_id}',
                    'Full_Name': f'Employee {employee_id}',
                    'Department': dept,
                    'Position': position,
                    'Base_Salary': base_salary,
                    'Performance_Score': performance_score,
                    'Years_Experience': years_experience,
                    'Bonus_Percentage': bonus_pct,
                    'Quarterly_Bonus': int(base_salary * bonus_pct / 4),
                    'Annual_Compensation': int(base_salary * (1 + bonus_pct)),
                    'Hire_Date': (datetime.now() - timedelta(days=random.randint(30, 2000))).strftime('%Y-%m-%d'),
                    'Manager_ID': f'EMP{random.randint(1001, 1020)}' if position != 'CFO' else 'CEO',
                    'Remote_Work_Days': random.randint(0, 5),
                    'Training_Hours_YTD': random.randint(8, 120),
                    'Satisfaction_Score': round(random.uniform(3.0, 5.0), 1)
                })
                employee_id += 1
        
        employee_df = pd.DataFrame(employee_data)
        employee_df.to_excel(writer, sheet_name='Employee_Performance', index=False)
        
        # Sheet 2: Financial Projections
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        
        financial_data = []
        for month in months:
            base_revenue = random.randint(2800000, 4200000)
            operating_expenses = int(base_revenue * random.uniform(0.65, 0.85))
            
            financial_data.append({
                'Month': month,
                'Revenue_Target': base_revenue,
                'Actual_Revenue': int(base_revenue * random.uniform(0.85, 1.15)),
                'Cost_of_Goods_Sold': int(base_revenue * random.uniform(0.25, 0.35)),
                'Operating_Expenses': operating_expenses,
                'Marketing_Spend': int(base_revenue * random.uniform(0.12, 0.18)),
                'R_and_D_Expenses': int(base_revenue * random.uniform(0.15, 0.22)),
                'Customer_Acquisition_Cost': random.randint(800, 1500),
                'Customer_Lifetime_Value': random.randint(12000, 28000),
                'Monthly_Recurring_Revenue': int(base_revenue * random.uniform(0.75, 0.90)),
                'Churn_Rate_Percent': round(random.uniform(2.1, 7.8), 2),
                'New_Customers_Acquired': random.randint(45, 125),
                'Support_Tickets_Created': random.randint(280, 450),
                'Support_Resolution_Time_Hours': round(random.uniform(4.2, 18.6), 1)
            })
        
        financial_df = pd.DataFrame(financial_data)
        financial_df.to_excel(writer, sheet_name='Financial_Projections', index=False)
        
        # Sheet 3: Product Analytics  
        products = ['NeuralCore Pro', 'AnalyticsMax Enterprise', 'DataFlow Standard', 
                   'PredictiveAI Suite', 'InsightEngine Business', 'AutoML Platform']
        
        product_data = []
        for product in products:
            for month in months[:9]:  # Only 9 months of data
                product_data.append({
                    'Product_Name': product,
                    'Month': month,
                    'Active_Users': random.randint(1200, 8500),
                    'New_Signups': random.randint(85, 320),
                    'Cancellations': random.randint(15, 95),
                    'Feature_Usage_Sessions': random.randint(15000, 45000),
                    'Average_Session_Duration_Minutes': round(random.uniform(8.5, 35.2), 1),
                    'Revenue_Generated': random.randint(180000, 750000),
                    'Support_Tickets': random.randint(25, 85),
                    'User_Satisfaction_Rating': round(random.uniform(3.8, 4.9), 2),
                    'Bug_Reports': random.randint(3, 22),
                    'Feature_Requests': random.randint(8, 45),
                    'API_Calls_Millions': round(random.uniform(2.3, 15.7), 2),
                    'Data_Processing_GB': random.randint(850, 5200),
                    'Uptime_Percentage': round(random.uniform(99.1, 99.98), 2)
                })
        
        product_df = pd.DataFrame(product_data)
        product_df.to_excel(writer, sheet_name='Product_Analytics', index=False)
    
    print(f"✓ Created complex Excel spreadsheet: {file_path}")
    return file_path

def create_ocr_test_images_with_complex_text():
    """Create challenging OCR test images with various text types"""
    
    # Image 1: Financial Invoice with Mixed Fonts
    img1 = Image.new('RGB', (800, 1000), color='white')
    draw1 = ImageDraw.Draw(img1)
    
    # Try to use different fonts, fall back to default if not available
    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        normal_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except:
        title_font = header_font = normal_font = small_font = ImageFont.load_default()
    
    # Invoice header
    draw1.text((50, 30), "NEURALCORP TECHNOLOGIES", font=title_font, fill='black')
    draw1.text((50, 70), "INVOICE #INV-2024-45892", font=header_font, fill='black')
    draw1.text((50, 100), "Date: October 8, 2024", font=normal_font, fill='black')
    draw1.text((450, 100), "Due Date: November 7, 2024", font=normal_font, fill='black')
    
    # Bill to section
    draw1.text((50, 150), "BILL TO:", font=header_font, fill='black')
    draw1.text((50, 180), "DataCentric Solutions Inc.", font=normal_font, fill='black')
    draw1.text((50, 200), "Attn: Jennifer Rodriguez, CFO", font=normal_font, fill='black')
    draw1.text((50, 220), "1847 Innovation Drive, Suite 300", font=normal_font, fill='black')
    draw1.text((50, 240), "San Francisco, CA 94107", font=normal_font, fill='black')
    draw1.text((50, 260), "Tax ID: 94-1234567", font=normal_font, fill='black')
    
    # Service details
    draw1.text((50, 320), "SERVICES PROVIDED:", font=header_font, fill='black')
    
    # Table headers
    draw1.rectangle([(50, 350), (750, 380)], fill='lightgray', outline='black')
    draw1.text((60, 360), "Description", font=normal_font, fill='black')
    draw1.text((350, 360), "Quantity", font=normal_font, fill='black')
    draw1.text((450, 360), "Rate", font=normal_font, fill='black')
    draw1.text((550, 360), "Amount", font=normal_font, fill='black')
    
    # Table rows
    services = [
        ("AI Platform Premium License", "12 months", "$4,200.00", "$50,400.00"),
        ("Custom ML Model Development", "1 project", "$28,500.00", "$28,500.00"),
        ("Technical Support & Maintenance", "12 months", "$1,800.00", "$21,600.00"),
        ("Advanced Analytics Module", "1 license", "$3,400.00", "$3,400.00"),
        ("Training & Implementation Services", "40 hours", "$285.00", "$11,400.00")
    ]
    
    y_pos = 390
    for service, qty, rate, amount in services:
        draw1.text((60, y_pos), service, font=small_font, fill='black')
        draw1.text((350, y_pos), qty, font=small_font, fill='black')
        draw1.text((450, y_pos), rate, font=small_font, fill='black')
        draw1.text((600, y_pos), amount, font=small_font, fill='black')
        y_pos += 25
    
    # Totals
    draw1.text((450, 550), "Subtotal:", font=normal_font, fill='black')
    draw1.text((600, 550), "$115,300.00", font=normal_font, fill='black')
    draw1.text((450, 575), "Sales Tax (8.75%):", font=normal_font, fill='black')
    draw1.text((600, 575), "$10,088.75", font=normal_font, fill='black')
    draw1.text((450, 600), "TOTAL AMOUNT DUE:", font=header_font, fill='black')
    draw1.text((600, 600), "$125,388.75", font=header_font, fill='black')
    
    # Payment terms
    draw1.text((50, 680), "PAYMENT TERMS:", font=header_font, fill='black')
    draw1.text((50, 710), "• Payment due within 30 days of invoice date", font=small_font, fill='black')
    draw1.text((50, 730), "• Wire transfer preferred (Account #: 4567-8901-2345-6789)", font=small_font, fill='black')
    draw1.text((50, 750), "• Late payments subject to 1.5% monthly service charge", font=small_font, fill='black')
    
    img1_path = EXTERNAL_KB / "complex_invoice_ocr_test.png"
    img1.save(img1_path)
    
    # Image 2: Meeting Notes with Complex Information
    img2 = Image.new('RGB', (700, 900), color='white')
    draw2 = ImageDraw.Draw(img2)
    
    # Meeting header
    draw2.text((50, 30), "PRODUCT STRATEGY MEETING", font=title_font, fill='blue')
    draw2.text((50, 70), "Date: October 8, 2024, 2:00 PM - 4:30 PM", font=normal_font, fill='black')
    draw2.text((50, 95), "Location: Conference Room Delta", font=normal_font, fill='black')
    
    # Attendees
    draw2.text((50, 140), "ATTENDEES:", font=header_font, fill='black')
    attendees = [
        "• Michael Chen - VP Product Strategy (Chair)",
        "• Sarah Kim - Senior Product Manager",
        "• David Rodriguez - Engineering Lead", 
        "• Lisa Wang - UX Research Director",
        "• James Thompson - Data Science Manager",
        "• Anna Kowalski - Marketing Director",
        "• Robert Singh - Customer Success VP"
    ]
    
    y_pos = 165
    for attendee in attendees:
        draw2.text((50, y_pos), attendee, font=small_font, fill='black')
        y_pos += 20
    
    # Key decisions
    draw2.text((50, 310), "KEY DECISIONS:", font=header_font, fill='red')
    
    decisions = [
        "1. Q4 Product Roadmap Approved:",
        "   - AI Assistant feature (Nov 15, 2024 release)",
        "   - Mobile app optimization (iOS & Android)",
        "   - Advanced analytics dashboard redesign",
        "",
        "2. Budget Allocation for 2025:",
        "   - R&D Investment: $1.2M for experimental AI",
        "   - Marketing Budget: $500K for Q4 campaigns",
        "   - Additional 3 engineers needed for Q1 2025",
        "",
        "3. Partnership Opportunity:",
        "   - TechFlow Corp partnership (Sarah to follow up)",
        "   - Healthcare vertical expansion ($2.3B TAM)",
        "",
        "4. Customer Feedback Analysis (Sept 2024):",
        "   - 89% satisfaction rate (target: 92%)",
        "   - Top requests: Real-time collaboration, API limits",
        "   - Pain points: Complex onboarding, limited integrations"
    ]
    
    y_pos = 335
    for decision in decisions:
        if decision.startswith(('1.', '2.', '3.', '4.')):
            draw2.text((50, y_pos), decision, font=normal_font, fill='darkblue')
        elif decision.strip() == '':
            y_pos += 5
            continue
        else:
            draw2.text((70, y_pos), decision, font=small_font, fill='black')
        y_pos += 18
    
    # Action items
    draw2.text((50, 650), "ACTION ITEMS:", font=header_font, fill='red')
    actions = [
        "□ Sarah: Contact TechFlow Corp by Oct 15",
        "□ David: Microservices proposal by Oct 20", 
        "□ Lisa: User interviews for onboarding by Oct 25",
        "□ Anna: Q4 marketing budget breakdown by Oct 12",
        "□ Michael: Follow-up with engineering leadership",
        "□ James: Analyze healthcare customer churn patterns"
    ]
    
    y_pos = 675
    for action in actions:
        draw2.text((50, y_pos), action, font=small_font, fill='darkred')
        y_pos += 20
    
    # Meeting conclusion
    draw2.text((50, 810), "NEXT MEETING: October 22, 2024, 2:00 PM", font=normal_font, fill='purple')
    draw2.text((50, 835), "Meeting concluded at 4:35 PM", font=small_font, fill='gray')
    
    img2_path = EXTERNAL_KB / "meeting_notes_complex_ocr.png"
    img2.save(img2_path)
    
    print(f"✓ Created complex OCR images:")
    print(f"  - {img1_path}")
    print(f"  - {img2_path}")
    
    return [img1_path, img2_path]

def create_json_config_with_nested_structure():
    """Create complex JSON configuration files with nested structures"""
    
    # Configuration 1: Microservices Configuration
    microservices_config = {
        "application": {
            "name": "neural-platform",
            "version": "3.2.1",
            "environment": "production",
            "deployment_date": "2024-10-08T10:30:00Z",
            "maintainer": {
                "team": "Platform Engineering",
                "contact": "devops@neuralcorp.com",
                "oncall_rotation": ["alex.chen", "maria.garcia", "david.kim"]
            }
        },
        "services": {
            "authentication": {
                "enabled": True,
                "port": 8001,
                "replicas": 3,
                "resources": {
                    "cpu": {"request": "500m", "limit": "1000m"},
                    "memory": {"request": "512Mi", "limit": "1Gi"}
                },
                "environment_variables": {
                    "JWT_SECRET_KEY": "${JWT_SECRET}",
                    "DATABASE_URL": "postgresql://auth_user:${DB_PASSWORD}@postgres:5432/auth_db",
                    "REDIS_URL": "redis://redis:6379/0",
                    "LOG_LEVEL": "INFO",
                    "RATE_LIMIT_REQUESTS": 1000,
                    "RATE_LIMIT_WINDOW_SECONDS": 3600
                },
                "health_check": {
                    "endpoint": "/health",
                    "interval_seconds": 30,
                    "timeout_seconds": 5,
                    "failure_threshold": 3
                }
            },
            "ai_inference": {
                "enabled": True,
                "port": 8003,
                "replicas": 4,
                "resources": {
                    "cpu": {"request": "1000m", "limit": "2000m"},
                    "memory": {"request": "2Gi", "limit": "4Gi"},
                    "gpu": {"type": "nvidia-tesla-t4", "count": 1}
                },
                "models": {
                    "text_classification": {
                        "model_path": "/models/text-classifier-v2.pkl",
                        "max_sequence_length": 512,
                        "batch_size": 32
                    },
                    "sentiment_analysis": {
                        "model_path": "/models/sentiment-bert-large.pt",
                        "preprocessing": {
                            "lowercase": True,
                            "remove_punctuation": False,
                            "tokenizer": "bert-base-uncased"
                        }
                    }
                }
            }
        },
        "monitoring": {
            "metrics": {
                "enabled": True,
                "prometheus": {
                    "endpoint": "/metrics",
                    "scrape_interval": "15s"
                },
                "custom_metrics": [
                    {"name": "api_requests_total", "type": "counter", "labels": ["service", "endpoint", "status"]},
                    {"name": "request_duration_seconds", "type": "histogram", "buckets": [0.1, 0.5, 1.0, 2.5, 5.0, 10.0]},
                    {"name": "active_user_sessions", "type": "gauge", "labels": ["service"]},
                    {"name": "ml_inference_requests", "type": "counter", "labels": ["model", "status"]}
                ]
            }
        },
        "security": {
            "tls": {
                "enabled": True,
                "certificate_path": "/etc/ssl/certs/neural-platform.crt",
                "private_key_path": "/etc/ssl/private/neural-platform.key"
            },
            "cors": {
                "allowed_origins": ["https://app.neuralcorp.com", "https://admin.neuralcorp.com"],
                "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allowed_headers": ["Content-Type", "Authorization", "X-API-Key"],
                "max_age_seconds": 86400
            }
        }
    }
    
    config1_path = INTERNAL_KB / "microservices_production_config.json"
    with open(config1_path, 'w') as f:
        json.dump(microservices_config, f, indent=2)
    
    # Configuration 2: AI Model Registry
    model_registry = {
        "registry_info": {
            "version": "2.1.0",
            "last_updated": "2024-10-08T14:22:31Z",
            "administrator": "ML Engineering Team",
            "total_models": 47,
            "active_models": 23
        },
        "models": {
            "text_sentiment_v3": {
                "metadata": {
                    "name": "Advanced Sentiment Analysis Model v3.0",
                    "description": "Fine-tuned BERT model for multi-class sentiment analysis",
                    "version": "3.0.1",
                    "created_date": "2024-09-15T09:30:00Z",
                    "model_type": "classification",
                    "framework": "pytorch",
                    "model_size_mb": 438.7,
                    "training_samples": 2800000,
                    "validation_accuracy": 0.9347
                },
                "performance_metrics": {
                    "accuracy": 0.9347,
                    "precision": {"positive": 0.9412, "negative": 0.9201, "neutral": 0.9098},
                    "recall": {"positive": 0.9389, "negative": 0.9284, "neutral": 0.9187},
                    "f1_score": {"positive": 0.9400, "negative": 0.9242, "neutral": 0.9142},
                    "inference_time_ms": 23.4,
                    "throughput_requests_per_second": 145.2
                },
                "deployment": {
                    "status": "production",
                    "endpoint": "https://api.neuralcorp.com/v3/sentiment",
                    "deployment_date": "2024-09-20T15:45:00Z",
                    "rollback_version": "2.8.3"
                }
            },
            "document_classifier_v2": {
                "metadata": {
                    "name": "Multi-format Document Classifier",
                    "description": "Classifies documents into categories: financial, legal, technical, marketing, HR",
                    "version": "2.5.0",
                    "created_date": "2024-08-22T11:15:00Z",
                    "model_type": "classification",
                    "framework": "scikit-learn",
                    "model_size_mb": 127.3,
                    "training_samples": 850000,
                    "validation_accuracy": 0.8923
                },
                "categories": {
                    "financial": {"training_samples": 185000, "precision": 0.9145, "recall": 0.8967},
                    "legal": {"training_samples": 142000, "precision": 0.8834, "recall": 0.8756},
                    "technical": {"training_samples": 198000, "precision": 0.9012, "recall": 0.9134},
                    "marketing": {"training_samples": 163000, "precision": 0.8723, "recall": 0.8891},
                    "hr": {"training_samples": 162000, "precision": 0.8945, "recall": 0.8798}
                }
            }
        }
    }
    
    config2_path = INTERNAL_KB / "ml_model_registry_config.json"
    with open(config2_path, 'w') as f:
        json.dump(model_registry, f, indent=2)
    
    print(f"✓ Created complex JSON configurations:")
    print(f"  - {config1_path}")
    print(f"  - {config2_path}")
    
    return [config1_path, config2_path]

def create_markdown_documentation():
    """Create comprehensive markdown documentation"""
    
    markdown_content = """# NeuralCorp API Integration Guide v3.1

## Authentication

The NeuralCorp API uses **JWT (JSON Web Tokens)** with RS256 signature algorithm for authentication.

### Getting Access Token

```bash
curl -X POST https://api.neuralcorp.com/v3/auth/token \\
  -H "Content-Type: application/json" \\
  -d '{
    "client_id": "your_client_id",
    "client_secret": "your_client_secret",
    "grant_type": "client_credentials",
    "scope": "inference analytics admin"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer", 
  "expires_in": 3600,
  "scope": "inference analytics admin",
  "issued_at": "2024-10-08T15:30:00Z"
}
```

## Rate Limiting

API requests are subject to rate limiting:

| Plan Type | Requests/Hour | Burst Limit | Concurrent Requests |
|-----------|---------------|-------------|-------------------|
| **Free Tier** | 1,000 | 100/minute | 5 |
| **Professional** | 10,000 | 500/minute | 25 |
| **Enterprise** | 100,000 | 2,000/minute | 100 |

### Rate Limit Headers

Every API response includes rate limit information:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1696780800
X-RateLimit-Window: 3600
```

## API Endpoints

### Text Analysis

#### POST /v3/text/analyze

Perform comprehensive text analysis including sentiment, entities, and classification.

```bash
curl -X POST https://api.neuralcorp.com/v3/text/analyze \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "Our Q3 revenue exceeded expectations by 15%.",
    "options": {
      "sentiment": true,
      "entities": true, 
      "classification": true,
      "language": "en"
    }
  }'
```

**Response:**
```json
{
  "analysis_id": "txt_7f8a9b2c3d4e5f6g",
  "text_length": 97,
  "processing_time_ms": 234,
  "results": {
    "sentiment": {
      "overall": "positive",
      "confidence": 0.89,
      "scores": {
        "positive": 0.89,
        "negative": 0.05,
        "neutral": 0.06
      }
    },
    "entities": [
      {
        "text": "Q3 revenue",
        "type": "FINANCIAL_METRIC", 
        "confidence": 0.95,
        "start": 4,
        "end": 14
      }
    ]
  }
}
```

## Error Handling

The API uses conventional HTTP response codes:

| Code | Meaning | Description |
|------|---------|-------------|
| **200** | OK | Request successful |
| **400** | Bad Request | Invalid request parameters |
| **401** | Unauthorized | Invalid authentication |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Server Error | Server error |

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_REQUEST_FORMAT",
    "message": "The request body contains invalid JSON syntax.",
    "request_id": "req_9a8b7c6d5e4f3g2h",
    "timestamp": "2024-10-08T15:42:15Z"
  }
}
```

## Best Practices

### Authentication Security
- **Never expose API keys** in client-side code
- **Rotate API keys** regularly (recommended: every 90 days)
- **Use environment variables** for API key storage

### Error Handling
- **Always check HTTP status codes** before parsing response
- **Implement exponential backoff** for retrying failed requests
- **Handle rate limits gracefully** with proper retry logic

### Performance Optimization
- **Use batch operations** when processing multiple items
- **Implement caching** for frequently requested data
- **Monitor API usage** to optimize request patterns

---

**Last Updated:** October 8, 2024  
**Version:** 3.1.0
"""
    
    markdown_path = INTERNAL_KB / "api_integration_guide_comprehensive.md"
    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"✓ Created comprehensive markdown documentation: {markdown_path}")
    return markdown_path

if __name__ == "__main__":
    print("Creating challenging test documents for RAG system...")
    print("="*60)
    
    # Create all document types
    try:
        financial_pdf = create_complex_financial_report()
        technical_pdf = create_technical_architecture_document() 
        excel_file = create_complex_spreadsheet_with_formulas()
        ocr_images = create_ocr_test_images_with_complex_text()
        json_configs = create_json_config_with_nested_structure()
        markdown_doc = create_markdown_documentation()
        
        print("\n" + "="*60)
        print("✅ ALL CHALLENGING TEST DOCUMENTS CREATED SUCCESSFULLY!")
        print(f"📁 Internal KB: {len(os.listdir(INTERNAL_KB))} files")
        print(f"📁 External KB: {len(os.listdir(EXTERNAL_KB))} files")
        print("\nDocuments created:")
        print("- Complex financial report (tables, metrics, executive summary)")
        print("- Technical architecture spec (microservices, APIs, security)")
        print("- Enterprise Excel file (3 sheets, formulas, complex data)")
        print("- OCR test images (invoice, meeting notes with complex layouts)")
        print("- Nested JSON configurations (microservices, ML registry)")
        print("- Comprehensive markdown guide (code examples, tables)")
        
    except Exception as e:
        print(f"❌ Error creating documents: {e}")
        import traceback
        traceback.print_exc()