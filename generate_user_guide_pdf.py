import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_pdf():
    pdf_filename = r"C:\Users\siraj\Desktop\Siraj_UPS_Solar_User_Guide.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        rightMargin=36, leftMargin=36, topMargin=40, bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Define Custom Palette
    COLOR_PRIMARY = colors.HexColor('#0f172a')   # Deep Slate/Navy
    COLOR_SECONDARY = colors.HexColor('#0284c7') # Tech Blue
    COLOR_ACCENT = colors.HexColor('#f59e0b')    # Solar Gold
    COLOR_DARK = colors.HexColor('#1e293b')      # Charcoal Text
    COLOR_LIGHT = colors.HexColor('#f8fafc')     # Soft Background
    COLOR_BORDER = colors.HexColor('#e2e8f0')    # Soft Border

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=COLOR_PRIMARY,
        leading=26,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=COLOR_SECONDARY,
        leading=15,
        spaceAfter=15
    )

    heading1_style = ParagraphStyle(
        'H1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=COLOR_PRIMARY,
        leading=18,
        spaceBefore=14,
        spaceAfter=6
    )

    heading2_style = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=COLOR_SECONDARY,
        leading=14,
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        textColor=COLOR_DARK,
        leading=14,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=body_style,
        fontName='Helvetica-Oblique',
        textColor=colors.HexColor('#0369a1'),
        leading=13
    )

    story = []

    # Title Banner / Header Table
    logo_path = r"c:\Users\siraj\Desktop\Siraj UPS\media\shop_logo\design-a-modern--professional-and-premium-logo-for.png"
    
    header_data = []
    if os.path.exists(logo_path):
        logo_img = Image(logo_path, width=70, height=70)
        title_text = [
            Paragraph("<b>SIRAJ UPS & SOLAR</b>", title_style),
            Paragraph("Official User Manual & Operations Guide v1.0", subtitle_style)
        ]
        header_table = Table([[logo_img, title_text]], colWidths=[80, 440])
    else:
        title_text = [
            Paragraph("<b>SIRAJ UPS & SOLAR</b>", title_style),
            Paragraph("Official User Manual & Operations Guide v1.0", subtitle_style)
        ]
        header_table = Table([[title_text]], colWidths=[520])

    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_SECONDARY, spaceBefore=10, spaceAfter=15))

    # Section 1: Introduction & Login Credentials
    story.append(Paragraph("1. System Overview & Quick Access", heading1_style))
    story.append(Paragraph(
        "Welcome to the official desktop software for <b>Siraj UPS and Solar</b>. "
        "This software is custom-designed for managing sales, inventory, customer udhaar (credit), "
        "supplier purchases, repair services, shop expenses, and financial reporting.",
        body_style
    ))

    cred_data = [
        [Paragraph("<b>Access Method</b>", body_style), Paragraph("<b>Details / Location</b>", body_style)],
        [Paragraph("<b>Desktop Shortcut</b>", body_style), Paragraph("Double-click <b>'Siraj UPS and Solar'</b> on your Windows Desktop", body_style)],
        [Paragraph("<b>Standalone EXE</b>", body_style), Paragraph("<b>`SirajUPS_Software.exe`</b> inside `Siraj UPS Software Portable` folder", body_style)],
        [Paragraph("<b>Admin Username</b>", body_style), Paragraph("<b>`admin`</b>", body_style)],
        [Paragraph("<b>Admin Password</b>", body_style), Paragraph("<b>`admin1234`</b>", body_style)],
        [Paragraph("<b>Local Web Address</b>", body_style), Paragraph("`http://127.0.0.1:8000` (Main Shop Computer)", body_style)]
    ]
    cred_table = Table(cred_data, colWidths=[150, 370])
    cred_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_PRIMARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_LIGHT]),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(cred_table)
    story.append(Spacer(1, 12))

    # Section 2: Core Modules Guide
    story.append(Paragraph("2. Core Software Modules & How to Use", heading1_style))

    # POS Billing
    story.append(Paragraph("A. POS Billing & Invoicing (Fast Counter Sales)", heading2_style))
    story.append(Paragraph("• Select or search for products by Name, SKU, or Barcode.", bullet_style))
    story.append(Paragraph("• Adjust quantity, unit price, or apply item discounts dynamically.", bullet_style))
    story.append(Paragraph("• Select Customer (Walk-in Cash or specific Registered Customer).", bullet_style))
    story.append(Paragraph("• Choose Payment Method: <b>Cash</b>, <b>Online / Card</b>, or <b>Udhaar (Credit)</b>.", bullet_style))
    story.append(Paragraph("• Click <b>Complete Sale & Print Invoice</b> to generate a clean PDF receipt with shop logo.", bullet_style))

    # Products & Inventory
    story.append(Paragraph("B. Products & Inventory Management", heading2_style))
    story.append(Paragraph("• <b>Add Products:</b> Enter Product Name, Category (UPS, Battery, Solar Panel, Inverter, Wire, etc.), SKU, Cost Price, Selling Price, and Alert Quantity.", bullet_style))
    story.append(Paragraph("• <b>Quick Category Modal:</b> Click <b>'+ New Category'</b> to add custom categories instantly without leaving the form.", bullet_style))
    story.append(Paragraph("• <b>Stock Adjustment:</b> Click the stock badge to quickly add or remove stock items with audit notes.", bullet_style))
    story.append(Paragraph("• <b>Low Stock Alerts:</b> Automatic visual notifications when stock falls below minimum threshold.", bullet_style))

    # Customers & Udhaar Ledger
    story.append(Paragraph("C. Customers & Udhaar (Credit) Ledger", heading2_style))
    story.append(Paragraph("• Track customer details, phone numbers, addresses, and total outstanding Udhaar balance.", bullet_style))
    story.append(Paragraph("• When a customer pays back credit, click <b>'Record Payment'</b> to update their ledger instantly.", bullet_style))
    story.append(Paragraph("• View complete transaction history and printable customer account statements.", bullet_style))

    # Suppliers & Purchases
    story.append(Paragraph("D. Suppliers & Purchases", heading2_style))
    story.append(Paragraph("• Manage battery/solar wholesalers and suppliers.", bullet_style))
    story.append(Paragraph("• Record incoming inventory shipments (Purchases) which automatically update stock levels.", bullet_style))
    story.append(Paragraph("• Track payable balances to suppliers.", bullet_style))

    # Expenses & Services
    story.append(Paragraph("E. Shop Expenses & Repair Services", heading2_style))
    story.append(Paragraph("• <b>Expenses:</b> Log shop bills, rent, staff salaries, tea/lunch, and transport expenses.", bullet_style))
    story.append(Paragraph("• <b>Services / Repairs:</b> Track UPS/Inverter repair jobs, customer equipment, repair status (Pending, In Progress, Ready, Delivered), and service charges.", bullet_style))

    # Section 3: User Roles & Shop Settings
    story.append(Paragraph("3. Roles & Shop Settings", heading1_style))
    story.append(Paragraph("• <b>Shop Settings:</b> Change Shop Name, Tagline, Phone, Address, Tax NTN, and Upload your Shop Logo.", bullet_style))
    story.append(Paragraph("• <b>Users & Roles:</b> Admin users have full control, while Cashiers are restricted to POS billing.", bullet_style))
    story.append(Paragraph("• <b>Backup & Restore:</b> Create complete database backups to prevent data loss.", bullet_style))

    # Section 4: Multi-PC Sharing Guide
    story.append(Paragraph("4. How to Use on Multiple PCs / Laptops", heading1_style))
    
    multi_pc_data = [
        [
            Paragraph("<b>Scenario</b>", body_style),
            Paragraph("<b>Step-by-Step Procedure</b>", body_style)
        ],
        [
            Paragraph("<b>Option A: Multiple PCs in Shop (Wi-Fi / LAN)</b>", body_style),
            Paragraph(
                "1. Find main PC IP address (e.g. `192.168.1.10`).<br/>"
                "2. Keep software running on main PC.<br/>"
                "3. On other devices, open browser and type: `http://192.168.1.10:8000`",
                body_style
            )
        ],
        [
            Paragraph("<b>Option B: Standalone Portable EXE (USB Copy)</b>", body_style),
            Paragraph(
                "1. Copy folder <b>`Siraj UPS Software Portable`</b> from Desktop to USB Drive.<br/>"
                "2. Paste onto any second laptop or computer.<br/>"
                "3. Double-click <b>`SirajUPS_Software.exe`</b> (No installation required).",
                body_style
            )
        ]
    ]
    multi_table = Table(multi_pc_data, colWidths=[160, 360])
    multi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), COLOR_SECONDARY),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, COLOR_BORDER),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, COLOR_LIGHT]),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(multi_table)

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_BORDER, spaceBefore=10, spaceAfter=10))
    story.append(Paragraph(
        "<b>Siraj UPS and Solar — Management System</b><br/>"
        "<font color='#64748b'>Document generated for shop owner | Support & Operations Manual</font>",
        ParagraphStyle('Footer', parent=body_style, alignment=1, fontSize=8)
    ))

    doc.build(story)
    print(f"User Guide PDF generated successfully at: {pdf_filename}")

if __name__ == "__main__":
    generate_pdf()
