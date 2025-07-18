
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from num2words import num2words
import os
from reportlab.platypus import Paragraph

# Register font
FONT_PATH = os.path.join("/Users/venu/Documents/project_invoice/fonts", "NotoSans-Regular.ttf")
pdfmetrics.registerFont(TTFont("NotoSans-Bold", "/Users/venu/Documents/project_invoice/fonts/NotoSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("NotoSans", FONT_PATH))

# Styles
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Normal-Noto", fontName="NotoSans", fontSize=9))
styles.add(ParagraphStyle(name="Small-Noto", fontName="NotoSans", fontSize=8))
styles.add(ParagraphStyle(name="Bold-Noto", fontName="NotoSans-Bold", fontSize=9, fontWeight='bold'))
styles.add(ParagraphStyle(name="Title-Noto", fontName="NotoSans", fontSize=10, leading=14, fontWeight='bold'))
styles.add(ParagraphStyle(name="Bold-Title-Noto", fontName="NotoSans-Bold", fontSize=11, leading=14, fontWeight='bold'))


def read_metadata(path):
    metadata = {}
    with open(path, 'r') as file:
        for line in file:
            if "=" in line:
                k, v = line.strip().split("=", 1)
                metadata[k.strip()] = v.strip()
    return metadata

def read_items(path):
    items = []
    with open(path, 'r') as file:
        for line in file:
            if line.strip():
                parts = line.strip().split(",")
                if len(parts) == 3:
                    desc = parts[0].strip()
                    qty = int(parts[1].strip())
                    rate = float(parts[2].strip())
                    items.append({
                        "description": desc,
                        "quantity": qty,
                        "rate": rate,
                        "amount": qty * rate
                    })
    return items

def format_currency(amount):
    return f"₹{amount:,.2f}"

def convert_to_words(amount):
    words = num2words(amount, lang='en_IN').replace(",", "")
    return f"{words.title()} Rupees"

def generate_receipt(meta, items, output_file):
    doc = SimpleDocTemplate(output_file, pagesize=A4, leftMargin=30, rightMargin=30, topMargin=40, bottomMargin=40)
    inner_elements = []

    # Header: Firm and Invoice Info
    firm_info = [
        Paragraph("Shankari Madhushree Fabrications & Metals", styles["Bold-Title-Noto"]),
        Paragraph("18,1 Sharadhanagar", styles["Normal-Noto"]),
        Paragraph("Bengaluru - 560061", styles["Normal-Noto"]),
        Paragraph("Mobile : 9164117781", styles["Normal-Noto"]),       
        Paragraph("Email : smfabricsnmetals@gmail.com", styles["Normal-Noto"]),
        Paragraph("GSTIN : 29GBVPM6491K1ZE", styles["Normal-Noto"]),
        Paragraph("PAN Number : GBVPM6491K", styles["Normal-Noto"])
    ]

    total = sum(i['amount'] for i in items)
    invoice_info = Table([
        [
            Paragraph("TAX INVOICE", styles["Title-Noto"]),
            Paragraph("ORIGINAL FOR RECIPIENT", ParagraphStyle(
                name='OriginalBox',
                fontName='NotoSans',
                fontSize=8,
                textColor=colors.grey,
                backColor=colors.white,
                alignment=0,
                leftPadding=2,
                rightPadding=4,
                topPadding=2,
                bottomPadding=2
            ))
        ],
        [Paragraph("INVOICE No. " + "\u00A0\u00A0\u00A0:" + "\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0" + meta.get('InvoiceNumber', ''), styles["Small-Noto"]), ""],
        [Paragraph("INVOICE Date " + "\u00A0:" + "\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0" + meta.get('InvoiceDate', ''), styles["Small-Noto"]), ""],
        [Paragraph("DUE Date  " + "\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0:" + "\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0" + meta.get('DueDate', ''), styles["Small-Noto"]), ""],
    ], colWidths=[80, 110])
    invoice_info.setStyle(TableStyle([
        ('SPAN', (0, 1), (1, 1)),
        ('SPAN', (0, 2), (1, 2)),
        ('SPAN', (0, 3), (1, 3)),
        ('FONTNAME', (0, 0), (-1, -1), 'NotoSans'),
        ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ('BOX', (1, 0), (1, 0), 0.5, colors.grey)
    ]))

    header_table = Table([[firm_info, invoice_info]], colWidths=[310, 210])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (1, 1), 'TOP')
    ]))
    inner_elements.append(header_table)
    inner_elements.append(Spacer(1, 12))

    # Build unified two-column address layout with continuous grey header
    address_table = Table([
        [
            Paragraph("BILLING ADDRESS", ParagraphStyle(
                name="BillHeader", fontName='NotoSans', fontSize=10,
                textColor=colors.black, alignment=0)),
            Paragraph("DELIVERY ADDRESS", ParagraphStyle(
                name="DelHeader", fontName='NotoSans', fontSize=10,
                textColor=colors.black, alignment=0))
        ],
        [
            Paragraph(f"<b>{meta.get('ClientName', '')}</b>", styles["Bold-Noto"]),
            Paragraph(f"<b>{meta.get('DeliveryName', '')}</b>", styles["Bold-Noto"])
        ],
        [
            Paragraph(meta.get("ClientAddress", ""), styles["Normal-Noto"]),
            Paragraph(meta.get("DeliveryAddress", ""), styles["Normal-Noto"])
        ],
        [
            Paragraph(f"GSTIN: {meta.get('ClientGST', '')}", styles["Normal-Noto"]),
        ],
        [
            Paragraph(f"Mobile: {meta.get('ClientPhone', '')}", styles["Normal-Noto"]),
            Paragraph(f"Mobile: {meta.get('DeliveryPhone', '')}", styles["Normal-Noto"])
        ]
    ], colWidths=[250, 250])

    address_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),  # full-width grey header
        ('FONTNAME', (0, 0), (-1, -1), 'NotoSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    inner_elements.append(address_table)
    inner_elements.append(Spacer(1, 24))

    
# Item Table
    data = [["S. No.", "SERVICES", "QTY", "RATE", "TAX", "AMOUNT"]]
    subtotal = 0
    total_qty = 0
    total_tax = 0

    for idx, item in enumerate(items, start=1):
        tax = item["amount"] * 0.18
        total_amt = item["amount"] + tax
        subtotal += item["amount"]
        total_qty += item["quantity"]
        total_tax += tax
        data.append([
            str(idx),
            Paragraph(item["description"].replace("\\n", "<br/>"), styles["Normal-Noto"]),
            str(item["quantity"]),
            format_currency(item["rate"]),
            format_currency(tax),
            format_currency(total_amt)
        ])

    transport_charge = float(meta.get("TransportAmount", 0))

    # Add 5 blank rows before summary
    num_items = len(items)
    min_rows = 7
    if num_items < min_rows:
        for _ in range(min_rows - num_items):
            data.append(["", "", "", "", "", ""])

    grand_total = subtotal + total_tax + transport_charge
    cgst = total_tax / 2
    sgst = total_tax / 2

    # Subtotal row: bold + grey background
    data.append([
        "", "Subtotal",
        str(total_qty),
        "",
        format_currency(total_tax),
        format_currency(grand_total)
    ])

    # Tax breakdown rows
    data.append(["", "", "", "", "TAXABLE AMOUNT", format_currency(subtotal)])
    data.append(["", "", "", "", "CGST @ 9%", format_currency(cgst)])
    data.append(["", "", "", "", "SGST @ 9%", format_currency(sgst)])
    if transport_charge > 0:
        data.append(["", "", "", "", "Transport Charge", format_currency(transport_charge)])

    data.append(["", "", "", "", "Total", format_currency(grand_total)])

    table = Table(data, colWidths=[40, 180, 50, 70, 70, 90])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'NotoSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (2, 0), (-1, 0), 'RIGHT'),  # 👈 header labels
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        # Subtotal row formatting
        ('FONTNAME', (0, -6), (-1, -6), 'NotoSans-Bold'),
        ('BACKGROUND', (0, -6), (-1, -6), colors.lightgrey),
        ('FONTSIZE', (0, -1), (-1, -1), 9),  # small font for final Total
        # Total row formatting
        ('FONTNAME', (0, -1), (-1, -1), 'NotoSans-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
    ]))
    inner_elements.append(table)
    inner_elements.append(Spacer(1, 16))

# Total in Words
    total_words = convert_to_words(int(grand_total))

    line = Paragraph(
    f'<font name="NotoSans-Bold">Total Amount (in words):</font> '
    f'<font name="NotoSans">{total_words}</font>',
    styles["Normal-Noto"]
    )
    inner_elements.append(line)
    inner_elements.append(Spacer(1, 24))

    # Signature Block
    sig_lines = [
        ["", "", "", "Authorized Signatory"],
        ["", "", "", "For Shankari Madhushree Fabrications & Metals"]
    ]
    sig_table = Table(sig_lines, colWidths=[250, 80, 80, 100])
    sig_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'NotoSans'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
    ]))
    inner_elements.append(sig_table)

    # Optional Signature Image
    sig_path = "assets/signature.png"
    if os.path.exists(sig_path):
        img = Image(sig_path, width=100, height=50)
        img_table = Table([["", "", "", img]], colWidths=[250, 80, 80, 100])
        img_table.setStyle(TableStyle([
            ('ALIGN', (3, 0), (3, 0), 'RIGHT'),
        ]))
        inner_elements.append(img_table)

    # Outer Border
    outer = Table([[inner_elements]], colWidths=[doc.width])
    outer.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1.5, colors.black),
        ('LEFTPADDING', (0, 0), (0, 0), 12),
        ('RIGHTPADDING', (0, 0), (0, 0), 12),
        ('TOPPADDING', (0, 0), (0, 0), 12),
        ('BOTTOMPADDING', (0, 0), (0, 0), 12),
    ]))

    doc.build([outer])
# MAIN
if __name__ == "__main__":
    metadata = read_metadata("/Users/venu/Documents/project_invoice/data/invoice_details.txt")
    items = read_items("/Users/venu/Documents/project_invoice/data/items.txt")
    
    output_dir = "/Users/venu/Documents/project_invoice/invoices"
    os.makedirs(output_dir, exist_ok=True)  # Create the folder if it doesn't exist

    filename = f"Receipt_{metadata.get('InvoiceNumber', 'INV0001')}.pdf"
    output_path = os.path.join(output_dir, filename)
    
    generate_receipt(metadata, items, output_path)
