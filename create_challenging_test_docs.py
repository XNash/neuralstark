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
    
    # Geographic Performance
    story.append(Paragraph("GEOGRAPHIC PERFORMANCE ANALYSIS", styles['Heading2']))
    geo_text = """
    Regional Revenue Distribution for Q3 2024:
    
    North America: $28.4 million (60.0% of total)
    - United States: $24.1 million (major clients: TechGiant Inc., DataFlow Corp)
    - Canada: $4.3 million (expansion in Toronto and Vancouver markets)
    
    Europe: $13.7 million (28.9% of total)  
    - United Kingdom: $6.2 million (new enterprise contracts with FinanceMax Ltd)
    - Germany: $4.8 million (automotive sector partnerships)
    - France: $2.7 million (healthcare AI implementations)
    
    Asia-Pacific: $5.2 million (11.0% of total)
    - Japan: $2.8 million (partnership with Sakura Technologies)
    - Australia: $1.7 million (government contracts)
    - Singapore: $0.7 million (emerging market entry)
    
    The North American market continues to be our strongest performer, with particularly strong growth 
    in the enterprise AI solutions segment. European expansion showed promising results with 
    45% quarter-over-quarter growth, driven primarily by demand for our predictive analytics platform.
    """
    story.append(Paragraph(geo_text, styles['Normal']))
    story.append(PageBreak())
    
    # Detailed Financial Metrics
    story.append(Paragraph("DETAILED FINANCIAL METRICS", styles['Heading2']))
    
    metrics_data = [
        ['Metric', 'Q3 2024', 'Q2 2024', 'Q3 2023', 'QoQ Change', 'YoY Change'],
        ['Total Revenue', '$47.3M', '$41.2M', '$35.3M', '+14.8%', '+34.0%'],
        ['Gross Profit', '$31.2M', '$26.8M', '$22.1M', '+16.4%', '+41.2%'],
        ['Operating Expenses', '$22.4M', '$21.1M', '$17.8M', '+6.2%', '+25.8%'],
        ['Net Income', '$8.8M', '$5.7M', '$4.3M', '+54.4%', '+104.7%'],
        ['Cash & Equivalents', '$23.6M', '$18.9M', '$12.4M', '+24.9%', '+90.3%'],
        ['Total Assets', '$78.3M', '$71.2M', '$56.8M', '+10.0%', '+37.9%'],
        ['Customer Count', '2,847', '2,634', '2,103', '+8.1%', '+35.4%'],
        ['Avg Contract Value', '$52,300', '$48,900', '$41,200', '+7.0%', '+26.9%']
    ]
    
    metrics_table = Table(metrics_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 20))
    
    # Risk Analysis Section
    story.append(Paragraph("RISK ANALYSIS & MITIGATION", styles['Heading2']))
    risk_text = """
    Key Business Risks Identified for Q4 2024 and 2025:
    
    1. MARKET COMPETITION RISK (High Priority)
       Risk Level: 7/10
       Description: Increased competition from established players (Google, Microsoft, Amazon) 
       entering the AI consulting space with aggressive pricing strategies.
       Mitigation: Focus on specialized vertical solutions and proprietary IP development.
       Budget Allocated: $3.2M for competitive response initiatives.
    
    2. TALENT ACQUISITION RISK (Medium Priority)  
       Risk Level: 6/10
       Description: Difficulty recruiting senior AI engineers and data scientists in competitive market.
       Current Vacancy Rate: 18% (target: <10%)
       Mitigation: Enhanced compensation packages, remote work flexibility, equity participation.
       Budget Allocated: $1.8M for talent acquisition and retention programs.
    
    3. TECHNOLOGY OBSOLESCENCE RISK (Medium Priority)
       Risk Level: 5/10  
       Description: Rapid evolution of AI technologies may render current solutions outdated.
       Mitigation: Continuous R&D investment (15% of revenue), strategic partnerships with research institutions.
       Budget Allocated: $7.1M for R&D activities in Q4 2024.
    
    4. REGULATORY COMPLIANCE RISK (Low Priority)
       Risk Level: 4/10
       Description: Evolving AI governance regulations in EU and US markets.
       Mitigation: Proactive compliance framework, legal counsel engagement, ethics committee establishment.
       Budget Allocated: $650K for compliance and legal advisory services.
    """
    story.append(Paragraph(risk_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Future Projections
    story.append(Paragraph("Q4 2024 PROJECTIONS & 2025 OUTLOOK", styles['Heading2']))
    projection_text = """
    Q4 2024 Financial Projections (Conservative Estimates):
    • Expected Revenue: $52-58 million (10-22% growth over Q4 2023)
    • Projected Net Income: $9.8-11.2 million 
    • Anticipated Customer Additions: 180-220 new enterprise clients
    • Planned Capital Expenditure: $4.3 million (infrastructure and technology)
    
    Strategic Initiatives for 2025:
    • Launch of NeuralCorp AI Platform 3.0 with advanced natural language processing
    • International expansion into Latin American markets (Brazil, Mexico)
    • Acquisition of 2-3 complementary technology companies (budget: $25M)
    • IPO preparation with target listing date Q2 2025
    
    CEO Statement: "Our Q3 performance demonstrates NeuralCorp's ability to execute on our 
    strategic vision while maintaining strong financial discipline. We are well-positioned 
    for continued growth and market leadership in the AI solutions space."
    - Alexandra Chen, Chief Executive Officer
    
    CFO Note: "The 34% revenue growth coupled with improved margins reflects our operational 
    excellence and scalable business model. Our strong balance sheet provides flexibility 
    for strategic investments and potential acquisitions."  
    - Robert Kumar, Chief Financial Officer
    """
    story.append(Paragraph(projection_text, styles['Normal']))
    
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
    story.append(PageBreak())
    
    # API Specifications
    story.append(Paragraph("API SPECIFICATIONS & ENDPOINTS", styles['Heading2']))
    api_text = """
    Authentication Service API (v2.1):
    
    Base URL: https://api.neuralplatform.com/auth/v2
    Authentication: Bearer Token (JWT with RS256 signature)
    Rate Limiting: 1000 requests/hour per API key
    
    Core Endpoints:
    
    POST /auth/login
    Description: Authenticate user credentials and return JWT token
    Request Body: {"email": "string", "password": "string", "mfa_code": "string"}
    Response: {"access_token": "jwt_string", "refresh_token": "string", "expires_in": 3600}
    Error Codes: 401 (Invalid credentials), 429 (Rate limited), 423 (Account locked)
    
    GET /auth/verify
    Description: Validate JWT token and return user context
    Headers: Authorization: Bearer <token>
    Response: {"user_id": "uuid", "email": "string", "roles": ["admin", "user"], "permissions": []}
    
    POST /auth/refresh
    Description: Generate new access token using refresh token
    Request Body: {"refresh_token": "string"}
    Response: {"access_token": "jwt_string", "expires_in": 3600}
    
    AI Inference Engine API (v3.0):
    
    Base URL: https://api.neuralplatform.com/ai/v3
    Authentication: API Key + Bearer Token
    Rate Limiting: 100 requests/minute per user (Premium: 500/minute)
    
    POST /inference/text/analyze
    Description: Perform text analysis using specified ML model
    Request Body: {
        "text": "string (max 10KB)",
        "model_id": "gpt-4-turbo|claude-3|gemini-pro", 
        "options": {"temperature": 0.7, "max_tokens": 1024}
    }
    Response: {
        "analysis_id": "uuid",
        "results": {"sentiment": 0.85, "entities": [], "summary": "string"},
        "processing_time_ms": 234,
        "model_version": "4.0.1"
    }
    
    GET /inference/status/{analysis_id}
    Description: Check status of long-running inference job
    Response: {"status": "pending|processing|completed|failed", "progress": 0.75, "eta_seconds": 45}
    """
    story.append(Paragraph(api_text, styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Database Schemas
    story.append(Paragraph("DATABASE SCHEMAS & RELATIONSHIPS", styles['Heading2']))
    schema_text = """
    User Management Schema (PostgreSQL):
    
    Table: users
    Columns:
    - user_id (UUID, PRIMARY KEY) 
    - email (VARCHAR(255), UNIQUE, NOT NULL)
    - password_hash (VARCHAR(512), NOT NULL) 
    - first_name (VARCHAR(100))
    - last_name (VARCHAR(100))
    - created_at (TIMESTAMP WITH TIME ZONE DEFAULT NOW())
    - updated_at (TIMESTAMP WITH TIME ZONE DEFAULT NOW())
    - last_login_at (TIMESTAMP WITH TIME ZONE)
    - is_active (BOOLEAN DEFAULT TRUE)
    - email_verified (BOOLEAN DEFAULT FALSE)
    - subscription_tier (ENUM: 'free', 'premium', 'enterprise')
    
    Table: user_sessions
    Columns:
    - session_id (UUID, PRIMARY KEY)
    - user_id (UUID, FOREIGN KEY REFERENCES users.user_id)
    - refresh_token_hash (VARCHAR(512), UNIQUE)
    - expires_at (TIMESTAMP WITH TIME ZONE)  
    - ip_address (INET)
    - user_agent (TEXT)
    - created_at (TIMESTAMP WITH TIME ZONE DEFAULT NOW())
    
    Indexes:
    - idx_users_email (users.email)
    - idx_users_created_at (users.created_at)  
    - idx_sessions_user_id (user_sessions.user_id)
    - idx_sessions_expires_at (user_sessions.expires_at)
    
    AI Models Schema (MongoDB):
    
    Collection: ml_models
    Document Structure:
    {
        "_id": ObjectId,
        "model_id": "string (unique)",
        "name": "string", 
        "version": "semver string",
        "model_type": "classification|regression|nlp|vision",
        "framework": "pytorch|tensorflow|scikit-learn|huggingface",
        "training_data": {
            "dataset_id": "string",
            "samples_count": int,
            "features_count": int, 
            "training_date": ISODate,
            "validation_accuracy": double
        },
        "hyperparameters": {
            "learning_rate": double,
            "batch_size": int,
            "epochs": int,
            "optimizer": "string"
        },
        "performance_metrics": {
            "accuracy": double,
            "precision": double, 
            "recall": double,
            "f1_score": double,
            "inference_time_ms": double
        },
        "deployment_status": "development|staging|production|deprecated",
        "created_at": ISODate,
        "updated_at": ISODate
    }
    
    Indexes:
    - model_id (unique)
    - deployment_status + created_at (compound)
    - model_type + performance_metrics.accuracy (compound)
    """
    story.append(Paragraph(schema_text, styles['Normal']))
    story.append(PageBreak())
    
    # Security Architecture
    story.append(Paragraph("SECURITY ARCHITECTURE", styles['Heading2']))
    security_text = """
    Zero-Trust Security Implementation:
    
    1. Network Security:
       • All inter-service communication encrypted with mTLS
       • Service mesh (Istio) provides automatic certificate rotation
       • Network segmentation using Kubernetes NetworkPolicies
       • WAF (Web Application Firewall) protection via Cloudflare
       • DDoS protection with rate limiting and traffic shaping
    
    2. Authentication & Authorization:
       • JWT tokens with 1-hour expiration (RS256 algorithm)
       • Refresh tokens with 30-day expiration (stored hashed)
       • Multi-factor authentication (TOTP + SMS backup)
       • Role-Based Access Control (RBAC) with 15 predefined roles
       • API key authentication for service-to-service calls
    
    3. Data Protection:
       • Encryption at rest (AES-256) for all databases
       • Encryption in transit (TLS 1.3) for all communications  
       • PII data anonymization for non-production environments
       • GDPR compliance with right-to-be-forgotten implementation
       • SOC 2 Type II certification maintained annually
    
    4. Audit & Monitoring:
       • Comprehensive audit logging to Elasticsearch cluster
       • Real-time security monitoring with Splunk SIEM
       • Vulnerability scanning (Trivy) integrated into CI/CD pipeline
       • Penetration testing quarterly by external security firm
       • Security incident response plan with 4-hour SLA
    
    Security Metrics (Last 30 days):
    • Authentication failures: 1,247 (0.03% of total requests)
    • Suspicious IP addresses blocked: 89
    • Security patches applied: 23 (critical: 3, medium: 20)
    • Vulnerability scan results: 0 critical, 2 medium, 15 low
    • Security incidents: 0 confirmed breaches
    """
    story.append(Paragraph(security_text, styles['Normal']))
    story.append(Spacer(1, 15))
    
    # Deployment Architecture  
    story.append(Paragraph("DEPLOYMENT & INFRASTRUCTURE", styles['Heading2']))
    deployment_text = """
    Kubernetes Cluster Configuration:
    
    Production Environment:
    • Cloud Provider: Amazon EKS (Elastic Kubernetes Service)
    • Region: us-west-2 (primary), eu-west-1 (disaster recovery)
    • Node Groups: 3 auto-scaling groups (min: 6 nodes, max: 50 nodes)
    • Instance Types: m5.2xlarge (general workloads), c5.4xlarge (AI inference)
    • Total CPU Capacity: 384 vCPUs, Total Memory: 1.5TB
    
    Container Registry & CI/CD:
    • Container Images: Amazon ECR with automated vulnerability scanning
    • CI/CD Pipeline: GitHub Actions with GitOps deployment (ArgoCD)
    • Deployment Strategy: Blue-Green with automated rollback triggers
    • Quality Gates: Unit tests (90% coverage), integration tests, security scans
    • Deployment Frequency: 23 deployments/week (average)
    
    Monitoring & Observability Stack:
    • Metrics: Prometheus + Grafana with 150+ custom dashboards
    • Logging: ELK Stack (Elasticsearch, Logstash, Kibana) 
    • Tracing: Jaeger for distributed request tracing
    • APM: New Relic for application performance monitoring
    • Alerting: PagerDuty integration with escalation policies
    
    Performance Benchmarks (Production):
    • Average Response Time: 145ms (target: <200ms)
    • 99th Percentile Latency: 450ms (target: <500ms)
    • Request Throughput: 15,000 requests/second (peak)
    • System Uptime: 99.97% (SLA: 99.9%)
    • Error Rate: 0.02% (target: <0.1%)
    
    Disaster Recovery:
    • RTO (Recovery Time Objective): 30 minutes
    • RPO (Recovery Point Objective): 15 minutes  
    • Cross-region data replication for critical databases
    • Automated failover testing monthly
    • Full disaster recovery drill quarterly
    """
    story.append(Paragraph(deployment_text, styles['Normal']))
    
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
        
        # Sheet 4: Customer Segmentation Analysis
        customer_segments = ['Enterprise', 'Mid-Market', 'Small Business', 'Startup', 'Non-Profit']
        industries = ['Technology', 'Healthcare', 'Finance', 'Retail', 'Manufacturing', 
                     'Education', 'Government', 'Real Estate', 'Media', 'Transportation']
        
        customer_data = []
        customer_id = 50001
        for segment in customer_segments:
            for i in range(random.randint(25, 60)):
                annual_spend = random.randint(5000, 500000)
                if segment == 'Enterprise':
                    annual_spend = random.randint(100000, 2000000)
                elif segment == 'Mid-Market':
                    annual_spend = random.randint(25000, 150000)
                
                customer_data.append({
                    'Customer_ID': f'CUST{customer_id}',
                    'Company_Name': f'{random.choice(industries)} Corp {customer_id}',
                    'Segment': segment,
                    'Industry': random.choice(industries),
                    'Annual_Contract_Value': annual_spend,
                    'Contract_Start_Date': (datetime.now() - timedelta(days=random.randint(30, 900))).strftime('%Y-%m-%d'),
                    'Contract_End_Date': (datetime.now() + timedelta(days=random.randint(90, 730))).strftime('%Y-%m-%d'),
                    'Number_of_Users': random.randint(5, 500),
                    'Products_Used': random.randint(1, 4),
                    'Support_Priority': random.choice(['Standard', 'Priority', 'Premium']),
                    'Health_Score': random.randint(65, 98),
                    'Renewal_Probability': round(random.uniform(0.45, 0.95), 3),
                    'Expansion_Opportunity': random.choice(['Low', 'Medium', 'High']),
                    'Last_Login_Days_Ago': random.randint(0, 45),
                    'Feature_Adoption_Score': random.randint(20, 95),
                    'NPS_Score': random.randint(-20, 80),
                    'Total_Support_Tickets': random.randint(0, 25),
                    'Account_Manager': f'Manager {random.randint(1, 8)}'
                })
                customer_id += 1
        
        customer_df = pd.DataFrame(customer_data)
        customer_df.to_excel(writer, sheet_name='Customer_Segmentation', index=False)
        
        # Sheet 5: Technical Metrics Dashboard
        services = ['Authentication API', 'User Management', 'Data Processing', 'ML Inference', 
                   'Notification Service', 'File Storage', 'Analytics Engine', 'Billing System']
        
        tech_metrics = []
        for service in services:
            for day in range(1, 31):  # 30 days of data
                tech_metrics.append({
                    'Service_Name': service,
                    'Date': f'2024-09-{day:02d}',
                    'Request_Count': random.randint(50000, 500000),
                    'Average_Response_Time_MS': random.randint(45, 350),
                    'P99_Response_Time_MS': random.randint(200, 1200),
                    'Error_Rate_Percent': round(random.uniform(0.01, 0.15), 3),
                    'CPU_Usage_Percent': round(random.uniform(25.5, 78.2), 1),
                    'Memory_Usage_Percent': round(random.uniform(45.0, 85.3), 1),
                    'Disk_Usage_GB': round(random.uniform(120.5, 890.7), 1),
                    'Network_Throughput_Mbps': round(random.uniform(150.0, 950.0), 1),
                    'Active_Connections': random.randint(100, 2500),
                    'Database_Query_Time_MS': random.randint(15, 120),
                    'Cache_Hit_Rate_Percent': round(random.uniform(85.5, 98.7), 1),
                    'Uptime_Minutes': random.randint(1430, 1440),  # Out of 1440 minutes per day
                    'Deployment_Version': f'v{random.randint(1,3)}.{random.randint(0,9)}.{random.randint(0,15)}'
                })
        
        tech_df = pd.DataFrame(tech_metrics)
        tech_df.to_excel(writer, sheet_name='Technical_Metrics', index=False)
    
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
    
    # Service details table
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
    draw1.text((50, 770), "• For questions, contact: billing@neuralcorp.com", font=small_font, fill='black')
    
    # Footer
    draw1.text((50, 850), "Thank you for your business!", font=normal_font, fill='gray')
    draw1.text((50, 880), "NeuralCorp Technologies | 555-NEURAL-1 | www.neuralcorp.com", font=small_font, fill='gray')
    
    img1_path = EXTERNAL_KB / "complex_invoice_ocr_test.png"
    img1.save(img1_path)
    
    # Image 2: Meeting Notes with Handwriting Style
    img2 = Image.new('RGB', (700, 900), color='white')
    draw2 = ImageDraw.Draw(img2)
    
    # Meeting header
    draw2.text((50, 30), "PRODUCT STRATEGY MEETING", font=title_font, fill='blue')
    draw2.text((50, 70), "Date: October 8, 2024, 2:00 PM - 4:30 PM", font=normal_font, fill='black')
    draw2.text((50, 95), "Location: Conference Room Delta (Hybrid Meeting)", font=normal_font, fill='black')
    
    # Attendees
    draw2.text((50, 140), "ATTENDEES:", font=header_font, fill='black')
    attendees = [
        "• Michael Chen - VP Product Strategy (Meeting Chair)",
        "• Sarah Kim - Senior Product Manager (In-person)",
        "• David Rodriguez - Engineering Lead (Remote)",
        "• Lisa Wang - UX Research Director (In-person)",
        "• James Thompson - Data Science Manager (Remote)",
        "• Anna Kowalski - Marketing Director (In-person)",
        "• Robert Singh - Customer Success VP (Remote)"
    ]
    
    y_pos = 165
    for attendee in attendees:
        draw2.text((50, y_pos), attendee, font=small_font, fill='black')
        y_pos += 20
    
    # Agenda and notes
    draw2.text((50, 310), "KEY DISCUSSION POINTS:", font=header_font, fill='black')
    
    discussion_points = [
        "1. Q4 2024 Product Roadmap Review",
        "   - AI Assistant feature development (ETA: Nov 15, 2024)",
        "   - Advanced analytics dashboard redesign",
        "   - Mobile app performance optimization (iOS & Android)",
        "",
        "2. Customer Feedback Analysis (Sept 2024 Survey Results)",
        "   - 89% satisfaction rate (target: 92%)",
        "   - Top requested features: Real-time collaboration, API rate limiting",
        "   - Pain points: Complex onboarding process, limited integrations",
        "",
        "3. Competitive Analysis Update",
        "   - Competitor X launched similar AI features (pricing 20% lower)",
        "   - Market opportunity in healthcare vertical ($2.3B TAM)",
        "   - Partnership opportunity with TechFlow Corp (action: Sarah to follow up)",
        "",
        "4. Technical Architecture Decisions", 
        "   - Migration to microservices architecture (6-month timeline)",
        "   - Database scaling strategy for 10M+ users",
        "   - Security audit findings and remediation plan",
        "",
        "5. Resource Allocation & Budget",
        "   - Additional 3 engineers needed for Q1 2025 (hiring priority)",
        "   - Marketing budget increase: $500K for Q4 campaigns",
        "   - R&D investment: $1.2M for experimental AI projects"
    ]
    
    y_pos = 335
    for point in discussion_points:
        if point.startswith(('1.', '2.', '3.', '4.', '5.')):
            draw2.text((50, y_pos), point, font=normal_font, fill='darkblue')
        elif point.strip() == '':
            y_pos += 5
            continue
        else:
            draw2.text((70, y_pos), point, font=small_font, fill='black')
        y_pos += 18
    
    # Action items
    draw2.text((50, 650), "ACTION ITEMS:", font=header_font, fill='red')
    actions = [
        "□ Sarah: Contact TechFlow Corp partnership team by Oct 15",
        "□ David: Complete microservices architecture proposal by Oct 20", 
        "□ Lisa: Conduct user interviews for onboarding improvements by Oct 25",
        "□ Anna: Prepare Q4 marketing campaign budget breakdown by Oct 12",
        "□ Michael: Schedule follow-up meeting with engineering leadership",
        "□ James: Analyze customer churn patterns for healthcare segment"
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
    
    # Image 3: Technical Diagram with Code Snippets
    img3 = Image.new('RGB', (900, 700), color='white')
    draw3 = ImageDraw.Draw(img3)
    
    # Title
    draw3.text((50, 20), "API INTEGRATION DIAGRAM", font=title_font, fill='black')
    draw3.text((50, 60), "Neural Platform Authentication Flow v2.1", font=header_font, fill='darkblue')
    
    # Draw boxes for API flow
    # Step 1 box
    draw3.rectangle([(50, 100), (200, 150)], fill='lightblue', outline='black')
    draw3.text((60, 115), "Client Application", font=normal_font, fill='black')
    draw3.text((70, 130), "(Web/Mobile)", font=small_font, fill='black')
    
    # Arrow 1
    draw3.text((220, 120), "→", font=title_font, fill='red')
    draw3.text((240, 105), "POST /auth/login", font=small_font, fill='black')
    draw3.text((240, 125), "credentials", font=small_font, fill='black')
    
    # Step 2 box
    draw3.rectangle([(300, 100), (450, 150)], fill='lightgreen', outline='black')
    draw3.text((310, 115), "Auth Service", font=normal_font, fill='black')
    draw3.text((325, 130), "(Port 8001)", font=small_font, fill='black')
    
    # Arrow 2  
    draw3.text((470, 120), "→", font=title_font, fill='red')
    draw3.text((490, 105), "validate", font=small_font, fill='black')
    draw3.text((490, 125), "credentials", font=small_font, fill='black')
    
    # Step 3 box
    draw3.rectangle([(550, 100), (700, 150)], fill='lightyellow', outline='black')
    draw3.text((570, 115), "User Database", font=normal_font, fill='black')
    draw3.text((575, 130), "(PostgreSQL)", font=small_font, fill='black')
    
    # Return arrows
    draw3.text((470, 170), "←", font=title_font, fill='green')
    draw3.text((490, 175), "user data", font=small_font, fill='black')
    
    draw3.text((220, 170), "←", font=title_font, fill='green')
    draw3.text((240, 175), "JWT token", font=small_font, fill='black')
    
    # Code example
    draw3.text((50, 220), "EXAMPLE REQUEST/RESPONSE:", font=header_font, fill='black')
    
    # Request box
    draw3.rectangle([(50, 250), (400, 350)], fill='#f5f5f5', outline='black')
    code_lines = [
        "POST /api/auth/login HTTP/1.1",
        "Content-Type: application/json",
        "User-Agent: NeuralApp/2.1.0",
        "",
        "{",
        '  "email": "admin@techcorp.com",',
        '  "password": "SecurePass123!",',
        '  "mfa_code": "847291"',
        "}"
    ]
    
    y_pos = 260
    for line in code_lines:
        draw3.text((60, y_pos), line, font=small_font, fill='darkgreen')
        y_pos += 12
    
    # Response box
    draw3.rectangle([(450, 250), (850, 350)], fill='#f0f8ff', outline='black')
    response_lines = [
        "HTTP/1.1 200 OK",
        "Content-Type: application/json",
        "",
        "{",
        '  "access_token": "eyJhbGciOiJSUzI1NiIs...",',
        '  "refresh_token": "rt_8f7a9b2c...",',
        '  "expires_in": 3600,',
        '  "token_type": "Bearer",',
        '  "user_id": "uuid-123-456-789"',
        "}"
    ]
    
    y_pos = 260
    for line in response_lines:
        draw3.text((460, y_pos), line, font=small_font, fill='darkblue')
        y_pos += 12
    
    # Security notes
    draw3.text((50, 380), "SECURITY CONSIDERATIONS:", font=header_font, fill='red')
    security_notes = [
        "• JWT tokens signed with RS256 algorithm using 2048-bit RSA keys",
        "• Access tokens expire after 1 hour, refresh tokens after 30 days",
        "• Rate limiting: 100 login attempts per hour per IP address",
        "• Failed login attempts logged with IP, timestamp, and user agent",
        "• Multi-factor authentication required for admin accounts",
        "• Session invalidation on password change or suspicious activity"
    ]
    
    y_pos = 405
    for note in security_notes:
        draw3.text((50, y_pos), note, font=small_font, fill='darkred')
        y_pos += 18
    
    # Error codes table
    draw3.text((50, 550), "ERROR CODES:", font=header_font, fill='black')
    error_codes = [
        "400 - Invalid request format or missing required fields",
        "401 - Invalid credentials or expired MFA code", 
        "403 - Account locked due to too many failed attempts",
        "429 - Rate limit exceeded (too many requests)",
        "500 - Internal server error (check system status)",
        "503 - Service temporarily unavailable (maintenance mode)"
    ]
    
    y_pos = 575
    for error in error_codes:
        draw3.text((50, y_pos), error, font=small_font, fill='black')
        y_pos += 18
    
    img3_path = EXTERNAL_KB / "technical_diagram_with_code.png"
    img3.save(img3_path)
    
    print(f"✓ Created complex OCR images:")
    print(f"  - {img1_path}")
    print(f"  - {img2_path}")  
    print(f"  - {img3_path}")
    
    return [img1_path, img2_path, img3_path]

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
            "user_management": {
                "enabled": True,
                "port": 8002,
                "replicas": 2,
                "resources": {
                    "cpu": {"request": "300m", "limit": "600m"},
                    "memory": {"request": "256Mi", "limit": "512Mi"}
                },
                "database": {
                    "type": "postgresql",
                    "host": "postgres-users.internal",
                    "port": 5432,
                    "name": "users_db",
                    "connection_pool": {
                        "min_connections": 5,
                        "max_connections": 20,
                        "connection_timeout": 30
                    }
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
                },
                "scaling": {
                    "auto_scaling_enabled": True,
                    "min_replicas": 2,
                    "max_replicas": 10,
                    "target_cpu_utilization": 70,
                    "scale_up_stabilization_seconds": 300,
                    "scale_down_stabilization_seconds": 600
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
            },
            "logging": {
                "level": "INFO",
                "format": "json",
                "destinations": [
                    {"type": "stdout"},
                    {"type": "elasticsearch", "endpoint": "https://logs.neuralcorp.com", "index": "neural-platform-logs"}
                ],
                "sensitive_fields": ["password", "token", "api_key", "credit_card"]
            },
            "tracing": {
                "enabled": True,
                "jaeger": {
                    "endpoint": "http://jaeger:14268/api/traces",
                    "sampling_rate": 0.1
                }
            }
        },
        "security": {
            "tls": {
                "enabled": True,
                "certificate_path": "/etc/ssl/certs/neural-platform.crt",
                "private_key_path": "/etc/ssl/private/neural-platform.key",
                "ca_certificate_path": "/etc/ssl/certs/ca.crt"
            },
            "cors": {
                "allowed_origins": ["https://app.neuralcorp.com", "https://admin.neuralcorp.com"],
                "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allowed_headers": ["Content-Type", "Authorization", "X-API-Key"],
                "max_age_seconds": 86400
            },
            "rate_limiting": {
                "global": {"requests_per_second": 10000},
                "per_user": {"requests_per_minute": 1000},
                "per_api_key": {"requests_per_hour": 50000}
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
                    "description": "Fine-tuned BERT model for multi-class sentiment analysis with emotion detection",
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
                    "rollback_version": "2.8.3",
                    "resource_requirements": {
                        "cpu_cores": 2.0,
                        "memory_gb": 4.0,
                        "gpu_memory_gb": 8.0
                    }
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
                "features": {
                    "supported_formats": ["pdf", "docx", "txt", "html", "markdown"],
                    "max_document_size_mb": 25.0,
                    "preprocessing_steps": [
                        "text_extraction",
                        "noise_removal", 
                        "tokenization",
                        "stopword_removal",
                        "tfidf_vectorization"
                    ],
                    "feature_count": 50000
                },
                "categories": {
                    "financial": {"training_samples": 185000, "precision": 0.9145, "recall": 0.8967},
                    "legal": {"training_samples": 142000, "precision": 0.8834, "recall": 0.8756},
                    "technical": {"training_samples": 198000, "precision": 0.9012, "recall": 0.9134},
                    "marketing": {"training_samples": 163000, "precision": 0.8723, "recall": 0.8891},
                    "hr": {"training_samples": 162000, "precision": 0.8945, "recall": 0.8798}
                }
            },
            "customer_churn_predictor": {
                "metadata": {
                    "name": "Customer Churn Prediction Model",
                    "description": "Predicts customer churn probability based on usage patterns and engagement metrics",
                    "version": "1.7.2",
                    "created_date": "2024-07-30T16:20:00Z",
                    "model_type": "regression",
                    "framework": "xgboost",
                    "model_size_mb": 89.2,
                    "training_samples": 450000,
                    "validation_auc": 0.8756
                },
                "input_features": [
                    {"name": "days_since_last_login", "type": "numeric", "importance": 0.23},
                    {"name": "monthly_api_calls", "type": "numeric", "importance": 0.19},
                    {"name": "support_tickets_count", "type": "numeric", "importance": 0.15},
                    {"name": "feature_usage_score", "type": "numeric", "importance": 0.12},
                    {"name": "contract_value", "type": "numeric", "importance": 0.11},
                    {"name": "user_satisfaction_rating", "type": "numeric", "importance": 0.09},
                    {"name": "company_size", "type": "categorical", "importance": 0.07},
                    {"name": "industry_sector", "type": "categorical", "importance": 0.04}
                ],
                "thresholds": {
                    "high_risk": 0.75,
                    "medium_risk": 0.50,
                    "low_risk": 0.25
                },
                "business_impact": {
                    "prevented_churn_revenue_ytd": 2340000,
                    "early_intervention_success_rate": 0.67,
                    "avg_customer_lifetime_value": 89500
                }
            }
        },
        "experiments": {
            "active_experiments": [
                {
                    "name": "multi_modal_sentiment_v4",
                    "description": "Sentiment analysis incorporating text, images, and audio",
                    "start_date": "2024-09-25T10:00:00Z",
                    "expected_completion": "2024-11-15T17:00:00Z",
                    "status": "training",
                    "progress_percentage": 34.7,
                    "resource_allocation": {
                        "gpu_hours_used": 892.3,
                        "gpu_hours_budget": 2500.0,
                        "training_cost_usd": 1247.82
                    }
                },
                {
                    "name": "real_time_fraud_detection",
                    "description": "Real-time transaction fraud detection with <100ms latency",
                    "start_date": "2024-10-01T14:30:00Z", 
                    "expected_completion": "2024-12-01T12:00:00Z",
                    "status": "data_preparation",
                    "progress_percentage": 12.1,
                    "datasets": {
                        "transaction_history": {"samples": 5800000, "timerange": "2022-01-01 to 2024-09-30"},
                        "fraud_labels": {"positive_samples": 23400, "negative_samples": 5776600}
                    }
                }
            ]
        }
    }
    
    config2_path = INTERNAL_KB / "ml_model_registry_config.json"
    with open(config2_path, 'w') as f:
        json.dump(model_registry, f, indent=2)
    
    print(f"✓ Created complex JSON configurations:")
    print(f"  - {config1_path}")
    print(f"  - {config2_path}")
    
    return [config1_path, config2_path]

def create_markdown_documentation_with_code():
    """Create complex markdown documentation with code blocks and tables"""
    
    markdown_content = """# NeuralCorp API Integration Guide v3.1

## Table of Contents
1. [Authentication](#authentication)
2. [Rate Limiting](#rate-limiting)
3. [API Endpoints](#api-endpoints)
4. [Error Handling](#error-handling)
5. [SDK Examples](#sdk-examples)
6. [Webhooks](#webhooks)
7. [Best Practices](#best-practices)

---

## Authentication

The NeuralCorp API uses **JWT (JSON Web Tokens)** with RS256 signature algorithm for authentication. All API requests must include a valid Bearer token in the Authorization header.

### Getting Started

1. **Register for API Access**
   - Visit: https://developers.neuralcorp.com
   - Create developer account
   - Generate API credentials

2. **Obtain Access Token**

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

### Token Validation

All requests must include the token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Rate Limiting

API requests are subject to rate limiting to ensure fair usage and system stability.

| Plan Type | Requests/Hour | Burst Limit | Concurrent Requests |
|-----------|---------------|-------------|-------------------|
| **Free Tier** | 1,000 | 100/minute | 5 |
| **Professional** | 10,000 | 500/minute | 25 |
| **Enterprise** | 100,000 | 2,000/minute | 100 |
| **Custom** | Negotiable | Negotiable | Negotiable |

### Rate Limit Headers

Every API response includes rate limit information:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1696780800
X-RateLimit-Window: 3600
```

### Handling Rate Limits

When you exceed the rate limit, the API returns HTTP 429:

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 45 seconds.",
    "retry_after": 45,
    "documentation_url": "https://docs.neuralcorp.com/rate-limits"
  }
}
```

---

## API Endpoints

### Text Analysis

#### POST /v3/text/analyze

Perform comprehensive text analysis including sentiment, entities, and classification.

**Request:**
```bash
curl -X POST https://api.neuralcorp.com/v3/text/analyze \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "Our Q3 revenue exceeded expectations by 15%. The new AI product line is performing exceptionally well.",
    "options": {
      "sentiment": true,
      "entities": true,
      "classification": true,
      "language": "en",
      "model_version": "3.1.0"
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
      },
      {
        "text": "AI product line",
        "type": "PRODUCT",
        "confidence": 0.87,
        "start": 55,
        "end": 70
      }
    ],
    "classification": {
      "category": "financial_report",
      "confidence": 0.92,
      "subcategories": ["earnings", "product_performance"]
    }
  },
  "model_info": {
    "version": "3.1.0",
    "last_updated": "2024-09-15T10:30:00Z"
  }
}
```

### Document Processing

#### POST /v3/documents/upload

Upload and process documents for analysis.

**Supported Formats:** PDF, DOCX, TXT, HTML, MD, CSV, XLSX

```python
import requests
import json

# Python example
url = "https://api.neuralcorp.com/v3/documents/upload"
headers = {
    "Authorization": "Bearer YOUR_TOKEN"
}

files = {
    'document': ('financial_report.pdf', open('financial_report.pdf', 'rb'), 'application/pdf')
}

data = {
    'options': json.dumps({
        'extract_text': True,
        'ocr_enabled': True,
        'classification': True,
        'entity_extraction': True,
        'callback_url': 'https://yourapp.com/webhook/document-processed'
    })
}

response = requests.post(url, headers=headers, files=files, data=data)
```

**Response:**
```json
{
  "document_id": "doc_8g9h0i1j2k3l4m5n",
  "filename": "financial_report.pdf",
  "file_size_bytes": 2847392,
  "pages": 23,
  "status": "processing",
  "estimated_completion": "2024-10-08T15:45:30Z",
  "processing_options": {
    "extract_text": true,
    "ocr_enabled": true,
    "classification": true,
    "entity_extraction": true
  },
  "created_at": "2024-10-08T15:42:15Z"
}
```

---

## Error Handling

The API uses conventional HTTP response codes to indicate success or failure.

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| **200** | OK | Request successful |
| **201** | Created | Resource created successfully |
| **400** | Bad Request | Invalid request parameters |
| **401** | Unauthorized | Invalid or missing authentication |
| **403** | Forbidden | Insufficient permissions |
| **404** | Not Found | Resource not found |
| **429** | Too Many Requests | Rate limit exceeded |
| **500** | Internal Server Error | Server error |
| **503** | Service Unavailable | Temporary service outage |

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_REQUEST_FORMAT",
    "message": "The request body contains invalid JSON syntax.",
    "details": {
      "line": 12,
      "column": 34,
      "expected": "string",
      "received": "number"
    },
    "request_id": "req_9a8b7c6d5e4f3g2h",
    "documentation_url": "https://docs.neuralcorp.com/errors/invalid-request-format",
    "timestamp": "2024-10-08T15:42:15Z"
  }
}
```

---

## SDK Examples

### JavaScript/TypeScript SDK

```typescript
import { NeuralCorpClient } from '@neuralcorp/sdk';

const client = new NeuralCorpClient({
  apiKey: process.env.NEURALCORP_API_KEY,
  baseURL: 'https://api.neuralcorp.com/v3',
  timeout: 30000,
  retryConfig: {
    maxRetries: 3,
    backoffMultiplier: 2,
    initialDelay: 1000
  }
});

// Text analysis
async function analyzeSentiment(text: string) {
  try {
    const result = await client.text.analyze({
      text,
      options: {
        sentiment: true,
        entities: false,
        classification: false
      }
    });
    
    console.log('Sentiment:', result.sentiment.overall);
    console.log('Confidence:', result.sentiment.confidence);
    
    return result;
  } catch (error) {
    if (error instanceof NeuralCorpAPIError) {
      console.error('API Error:', error.message);
      console.error('Error Code:', error.code);
    } else {
      console.error('Unexpected error:', error);
    }
    throw error;
  }
}

// Document processing with async/await
async function processDocument(filePath: string) {
  const uploadResult = await client.documents.upload({
    file: fs.createReadStream(filePath),
    options: {
      extract_text: true,
      ocr_enabled: true,
      classification: true
    }
  });
  
  // Poll for completion
  let status = 'processing';
  while (status === 'processing') {
    await new Promise(resolve => setTimeout(resolve, 2000));
    const statusResult = await client.documents.getStatus(uploadResult.document_id);
    status = statusResult.status;
  }
  
  if (status === 'completed') {
    return await client.documents.getResults(uploadResult.document_id);
  } else {
    throw new Error(`Document processing failed: ${status}`);
  }
}
```

### Python SDK

```python
import asyncio
from neuralcorp import AsyncNeuralCorpClient, NeuralCorpError

client = AsyncNeuralCorpClient(
    api_key=os.environ['NEURALCORP_API_KEY'],
    base_url='https://api.neuralcorp.com/v3',
    timeout=30.0,
    max_retries=3
)

async def batch_text_analysis(texts: List[str]) -> List[dict]:
    """Process multiple texts concurrently"""
    tasks = []
    
    for text in texts:
        task = client.text.analyze({
            'text': text,
            'options': {
                'sentiment': True,
                'entities': True,
                'classification': True
            }
        })
        tasks.append(task)
    
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results and exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, NeuralCorpError):
                print(f"Error processing text {i}: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results
    
    except Exception as e:
        print(f"Batch processing failed: {e}")
        raise

# Usage
async def main():
    texts = [
        "Our sales team exceeded targets by 20% this quarter.",
        "The new security vulnerability needs immediate attention.", 
        "Customer satisfaction scores improved significantly this month."
    ]
    
    results = await batch_text_analysis(texts)
    
    for i, result in enumerate(results):
        if result:
            print(f"Text {i+1}: {result['results']['sentiment']['overall']}")

asyncio.run(main())
```

---

## Webhooks

Configure webhooks to receive real-time notifications about processing status.

### Webhook Configuration

```bash
curl -X POST https://api.neuralcorp.com/v3/webhooks \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "url": "https://yourapp.com/webhooks/neuralcorp",
    "events": ["document.processed", "analysis.completed", "error.occurred"],
    "secret": "your_webhook_secret_key",
    "active": true,
    "description": "Production webhook for document processing"
  }'
```

### Webhook Payload Example

```json
{
  "id": "evt_1a2b3c4d5e6f7g8h",
  "type": "document.processed",
  "created": "2024-10-08T15:45:30Z",
  "data": {
    "object": {
      "document_id": "doc_8g9h0i1j2k3l4m5n",
      "status": "completed",
      "processing_time_seconds": 47.3,
      "results": {
        "text_extracted": true,
        "pages_processed": 23,
        "entities_found": 47,
        "classification": "financial_report",
        "confidence": 0.94
      }
    }
  },
  "request_id": "req_9a8b7c6d5e4f3g2h",
  "signature": "t=1696780800,v1=sha256hash..."
}
```

---

## Best Practices

### 1. Authentication Security
- **Never expose API keys** in client-side code or version control
- **Rotate API keys** regularly (recommended: every 90 days)
- **Use environment variables** for API key storage
- **Implement proper token refresh** logic for long-running applications

### 2. Error Handling
- **Always check HTTP status codes** before parsing response body
- **Implement exponential backoff** for retrying failed requests
- **Log errors with request IDs** for debugging and support
- **Handle rate limits gracefully** with proper retry logic

### 3. Performance Optimization
- **Use batch operations** when processing multiple items
- **Implement caching** for frequently requested data
- **Process large documents asynchronously** using webhooks
- **Monitor API usage** to optimize request patterns

### 4. Data Management
- **Validate input data** before sending to API
- **Implement proper timeout handling** for long-running operations
- **Use compression** for large payloads when supported
- **Clean up processed documents** to manage storage costs

### Example: Production-Ready Error Handling

```typescript
interface APIConfig {
  maxRetries: number;
  initialDelay: number;
  maxDelay: number;
  backoffMultiplier: number;
}

class RobustAPIClient {
  private config: APIConfig = {
    maxRetries: 3,
    initialDelay: 1000,
    maxDelay: 30000,
    backoffMultiplier: 2
  };

  async makeRequestWithRetry<T>(
    requestFn: () => Promise<T>,
    attempt: number = 1
  ): Promise<T> {
    try {
      return await requestFn();
    } catch (error) {
      if (this.shouldRetry(error, attempt)) {
        const delay = this.calculateDelay(attempt);
        await this.sleep(delay);
        return this.makeRequestWithRetry(requestFn, attempt + 1);
      }
      throw error;
    }
  }

  private shouldRetry(error: any, attempt: number): boolean {
    if (attempt >= this.config.maxRetries) return false;
    
    // Retry on specific error codes
    const retryableErrors = [429, 500, 502, 503, 504];
    return retryableErrors.includes(error.status);
  }

  private calculateDelay(attempt: number): number {
    const delay = this.config.initialDelay * 
      Math.pow(this.config.backoffMultiplier, attempt - 1);
    return Math.min(delay, this.config.maxDelay);
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}
```

---

## Support & Resources

- **Documentation:** https://docs.neuralcorp.com
- **API Reference:** https://api.neuralcorp.com/docs
- **Developer Support:** developers@neuralcorp.com
- **Status Page:** https://status.neuralcorp.com
- **Community Forum:** https://community.neuralcorp.com

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
    financial_pdf = create_complex_financial_report()
    technical_pdf = create_technical_architecture_document() 
    excel_file = create_complex_spreadsheet_with_formulas()
    ocr_images = create_ocr_test_images_with_complex_text()
    json_configs = create_json_config_with_nested_structure()
    markdown_doc = create_markdown_documentation_with_code()
    
    print("\n" + "="*60)
    print("✅ ALL CHALLENGING TEST DOCUMENTS CREATED SUCCESSFULLY!")
    print(f"📁 Internal KB: {len(os.listdir(INTERNAL_KB))} files")
    print(f"📁 External KB: {len(os.listdir(EXTERNAL_KB))} files")
    print("\nDocuments created:")
    print("- Complex financial report (23 pages, tables, metrics)")
    print("- Technical architecture spec (API docs, schemas, security)")
    print("- Enterprise Excel file (5 sheets, formulas, complex data)")
    print("- OCR test images (invoice, meeting notes, technical diagrams)")
    print("- Nested JSON configurations (microservices, ML registry)")
    print("- Comprehensive markdown guide (code examples, tables)")