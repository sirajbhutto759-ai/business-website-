import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from settings_app.models import ShopSettings

def generate_invoice_pdf(sale):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
    )

    shop = ShopSettings.get_settings()
    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'InvoiceSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#0284c7'),
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'InvoiceBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#334155'),
        leading=12
    )

    import os

    logo_flowable = None
    if shop.logo and hasattr(shop.logo, 'path') and os.path.exists(shop.logo.path):
        try:
            logo_flowable = Image(shop.logo.path, width=75, height=45)
            logo_flowable.hAlign = 'LEFT'
        except Exception:
            logo_flowable = None

    if logo_flowable:
        title_block = [
            Paragraph(f"<b>{shop.shop_name.upper()}</b>", title_style),
            Paragraph(f"<b>{shop.subtitle}</b>", subtitle_style)
        ]
        header_table_data = [
            [
                logo_flowable,
                title_block,
                [
                    Paragraph(f"<b>INVOICE</b><br/><font size=10 color='#64748b'>#{sale.invoice_no}</font>", ParagraphStyle('InvNum', parent=body_style, alignment=2)),
                    Paragraph(f"<b>Date:</b> {sale.sale_date.strftime('%d-%b-%Y %I:%M %p')}", ParagraphStyle('InvDate', parent=body_style, alignment=2))
                ]
            ]
        ]
        header_table = Table(header_table_data, colWidths=[85, 235, 200])
    else:
        header_table_data = [
            [
                Paragraph(f"<b>{shop.shop_name.upper()}</b>", title_style),
                Paragraph(f"<b>INVOICE</b><br/><font size=10 color='#64748b'>#{sale.invoice_no}</font>", ParagraphStyle('InvNum', parent=body_style, alignment=2))
            ],
            [
                Paragraph(f"<b>{shop.subtitle}</b>", subtitle_style),
                Paragraph(f"<b>Date:</b> {sale.sale_date.strftime('%d-%b-%Y %I:%M %p')}", ParagraphStyle('InvDate', parent=body_style, alignment=2))
            ]
        ]
        header_table = Table(header_table_data, colWidths=[320, 200])

    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=15, spaceBefore=10))

    # Customer & Shop info table
    info_data = [
        [
            Paragraph("<b>FROM:</b>", ParagraphStyle('SubHead', parent=body_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#0284c7'))),
            Paragraph("<b>BILL TO:</b>", ParagraphStyle('SubHead', parent=body_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#0284c7')))
        ],
        [
            Paragraph(f"<b>{shop.shop_name}</b><br/>{shop.address}<br/>Phone: {shop.phone}<br/>WhatsApp: {shop.whatsapp}", body_style),
            Paragraph(f"<b>{sale.get_customer_name()}</b><br/>Phone: {sale.get_customer_phone()}<br/>Payment Method: {sale.get_payment_method_display()}", body_style)
        ]
    ]

    info_table = Table(info_data, colWidths=[260, 260])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))

    # Items Table
    table_data = [
        [
            Paragraph("<b>#</b>", ParagraphStyle('Th', parent=body_style, textColor=colors.white)),
            Paragraph("<b>Product Description</b>", ParagraphStyle('Th', parent=body_style, textColor=colors.white)),
            Paragraph("<b>Qty</b>", ParagraphStyle('Th', parent=body_style, textColor=colors.white, alignment=1)),
            Paragraph("<b>Unit Price</b>", ParagraphStyle('Th', parent=body_style, textColor=colors.white, alignment=2)),
            Paragraph("<b>Discount</b>", ParagraphStyle('Th', parent=body_style, textColor=colors.white, alignment=2)),
            Paragraph("<b>Total (Rs.)</b>", ParagraphStyle('Th', parent=body_style, textColor=colors.white, alignment=2)),
        ]
    ]

    for idx, item in enumerate(sale.items.all(), 1):
        table_data.append([
            Paragraph(str(idx), body_style),
            Paragraph(f"<b>{item.product.name}</b><br/><font size=8 color='#64748b'>SKU: {item.product.sku}</font>", body_style),
            Paragraph(str(item.quantity), ParagraphStyle('Center', parent=body_style, alignment=1)),
            Paragraph(f"{item.unit_price:,.2f}", ParagraphStyle('Right', parent=body_style, alignment=2)),
            Paragraph(f"{item.item_discount:,.2f}", ParagraphStyle('Right', parent=body_style, alignment=2)),
            Paragraph(f"{item.total_price:,.2f}", ParagraphStyle('Right', parent=body_style, alignment=2)),
        ])

    items_table = Table(table_data, colWidths=[30, 230, 40, 75, 65, 80])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 15))

    totals_data = [
        [Paragraph("<b>Subtotal:</b>", body_style), Paragraph(f"Rs. {sale.subtotal:,.2f}", ParagraphStyle('R', parent=body_style, alignment=2))],
        [Paragraph("<b>Overall Discount:</b>", body_style), Paragraph(f"- Rs. {sale.overall_discount:,.2f}" if sale.overall_discount > 0 else "Rs. 0.00", ParagraphStyle('R', parent=body_style, alignment=2, textColor=colors.HexColor('#dc2626') if sale.overall_discount > 0 else colors.HexColor('#334155')))],
        [Paragraph("<b>Grand Total:</b>", ParagraphStyle('GB', parent=body_style, fontName='Helvetica-Bold', fontSize=10)), Paragraph(f"<b>Rs. {sale.grand_total:,.2f}</b>", ParagraphStyle('R', parent=body_style, alignment=2, fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#0284c7')))],
        [Paragraph("<b>Paid Amount:</b>", body_style), Paragraph(f"Rs. {sale.paid_amount:,.2f}", ParagraphStyle('R', parent=body_style, alignment=2))],
    ]

    if sale.change_due > 0:
        totals_data.append([
            Paragraph("<b>Change Due / Return:</b>", ParagraphStyle('CD', parent=body_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#16a34a'))),
            Paragraph(f"<b>Rs. {sale.change_due:,.2f}</b>", ParagraphStyle('R', parent=body_style, alignment=2, fontName='Helvetica-Bold', textColor=colors.HexColor('#16a34a')))
        ])
    else:
        totals_data.append([
            Paragraph("<b>Remaining Balance:</b>", ParagraphStyle('RB', parent=body_style, fontName='Helvetica-Bold', textColor=colors.HexColor('#dc2626') if sale.remaining_balance > 0 else colors.HexColor('#16a34a'))),
            Paragraph(f"<b>Rs. {sale.remaining_balance:,.2f}</b>", ParagraphStyle('R', parent=body_style, alignment=2, fontName='Helvetica-Bold', textColor=colors.HexColor('#dc2626') if sale.remaining_balance > 0 else colors.HexColor('#16a34a')))
        ])

    totals_table = Table(totals_data, colWidths=[140, 110])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,2), (-1,2), 1, colors.HexColor('#0f172a')),
    ]))

    wrapper_table = Table([[Paragraph("", body_style), totals_table]], colWidths=[270, 250])
    wrapper_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(wrapper_table)

    elements.append(Spacer(1, 30))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=10))
    footer_text = f"<b>Thank you for choosing Siraj UPS and Solar!</b><br/>{shop.invoice_footer}"
    elements.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=body_style, alignment=1, fontSize=8, textColor=colors.HexColor('#64748b'))))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
