import os
import sys
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
    Flowable,
)


# =============================
# Configuration & Design System
# =============================

PRIMARY_BLUE = colors.HexColor("#2E86AB")
SECONDARY_PURPLE = colors.HexColor("#A23B72")
ACCENT_ORANGE = colors.HexColor("#F18F01")
NEUTRAL_DARK = colors.HexColor("#2D2D2D")
NEUTRAL_TEXT = colors.HexColor("#3A3A3A")
NEUTRAL_MUTED = colors.HexColor("#6F6F6F")
NEUTRAL_BORDER = colors.HexColor("#DDDDDD")
NEUTRAL_BG = colors.HexColor("#F7F9FB")

PAGE_SIZE = A4
MARGIN = 72  # 72pt margins per requirement

# Target screenshot size: 6.5in x 4in (468 x 288 pt)
SHOT_W = 6.5 * inch
SHOT_H = 4.0 * inch


def repo_basename() -> str:
    try:
        return os.path.basename(os.getcwd()) or "project"
    except Exception:
        return "project"


OUTPUT_PDF = f"{repo_basename()}_Modern_Report.pdf"


# =============================
# Styles
# =============================

def build_styles():
    ss = getSampleStyleSheet()

    title = ParagraphStyle(
        name="Title",
        parent=ss["Title"],
        fontName="Helvetica-Bold",
        fontSize=28,
        textColor=PRIMARY_BLUE,
        leading=34,
        spaceAfter=16,
    )

    subtitle = ParagraphStyle(
        name="Subtitle",
        parent=ss["Normal"],
        fontName="Helvetica",
        fontSize=12,
        textColor=NEUTRAL_MUTED,
        leading=16,
        spaceAfter=12,
    )

    h2 = ParagraphStyle(
        name="H2",
        parent=ss["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=NEUTRAL_DARK,
        leading=22,
        spaceBefore=6,
        spaceAfter=8,
    )

    h2_color = ParagraphStyle(
        name="H2Color",
        parent=h2,
        textColor=PRIMARY_BLUE,
    )

    body = ParagraphStyle(
        name="Body",
        parent=ss["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        textColor=NEUTRAL_TEXT,
        leading=16,
        spaceAfter=8,
    )

    caption = ParagraphStyle(
        name="Caption",
        parent=ss["Italic"],
        fontName="Helvetica-Oblique",
        fontSize=9,
        textColor=NEUTRAL_MUTED,
        leading=12,
        alignment=1,  # center
        spaceBefore=4,
        spaceAfter=12,
    )

    small = ParagraphStyle(
        name="Small",
        parent=ss["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=NEUTRAL_MUTED,
        leading=12,
    )

    # Table text styles
    table_header = ParagraphStyle(
        name="TableHeader",
        parent=ss["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=colors.white,
        leading=14,
    )

    table_cell = ParagraphStyle(
        name="TableCell",
        parent=ss["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=NEUTRAL_TEXT,
        leading=14,
    )

    callout = ParagraphStyle(
        name="Callout",
        parent=ss["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        textColor=NEUTRAL_DARK,
        backColor=NEUTRAL_BG,
        leading=16,
        leftIndent=8,
        rightIndent=8,
        spaceBefore=6,
        spaceAfter=10,
        borderPadding=8,
    )

    return {
        "title": title,
        "subtitle": subtitle,
        "h2": h2,
        "h2c": h2_color,
        "body": body,
        "caption": caption,
        "small": small,
        "th": table_header,
        "tc": table_cell,
        "callout": callout,
    }


# =============================
# Helpers / Components
# =============================

class Divider(Flowable):
    def __init__(self, width=1, color=NEUTRAL_BORDER):
        super().__init__()
        self.width = width
        self.color = color

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.width)
        w = self.canv._pagesize[0] - 2 * MARGIN
        self.canv.line(0, 0, w, 0)


def section_header(text: str, styles, accent=PRIMARY_BLUE):
    # Emoji included per requirement; note some PDF viewers may not render emoji with Helvetica
    return [
        Spacer(1, 10),
        Paragraph(text, styles["h2c"]),
        Spacer(1, 4),
        Divider(width=1.2, color=accent),
        Spacer(1, 8),
    ]


def colored_table(data, colWidths=None, header_bg=PRIMARY_BLUE, grid_color=NEUTRAL_BORDER):
    # data: first row is header (Paragraphs already styled)
    t = Table(data, colWidths=colWidths, hAlign="LEFT")
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("LINEABOVE", (0, 0), (-1, 0), 1, header_bg),
        ("LINEBELOW", (0, 0), (-1, 0), 1, header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, grid_color),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t


def info_table(rows, styles):
    data = [
        [Paragraph("Field", styles["th"]), Paragraph("Details", styles["th"])],
    ]
    for k, v in rows:
        data.append([Paragraph(k, styles["tc"]), Paragraph(v, styles["tc"])])
    return colored_table(data, colWidths=[1.7 * inch, 4.6 * inch])


def deliverables_table(items, styles):
    data = [
        [Paragraph("Deliverable", styles["th"]), Paragraph("Status", styles["th"])],
    ]
    for text, status in items:
        color = SECONDARY_PURPLE if status == "In Progress" else PRIMARY_BLUE if status == "Done" else ACCENT_ORANGE
        data.append([
            Paragraph(text, styles["tc"]),
            Paragraph(f"{status}", ParagraphStyle(name="Status", parent=styles["tc"], textColor=color, fontName="Helvetica-Bold")),
        ])
    return colored_table(data, colWidths=[4.5 * inch, 1.8 * inch], header_bg=SECONDARY_PURPLE)


def success_metrics_table(metrics, styles):
    data = [
        [Paragraph("Metric", styles["th"]), Paragraph("Value", styles["th"]), Paragraph("Notes", styles["th"])],
    ]
    for m, v, n in metrics:
        data.append([Paragraph(m, styles["tc"]), Paragraph(v, styles["tc"]), Paragraph(n, styles["tc"])])
    return colored_table(data, colWidths=[2.2 * inch, 1.6 * inch, 2.5 * inch], header_bg=PRIMARY_BLUE)


def screenshot_flowable(path, caption, styles):
    items = []
    if not os.path.exists(path):
        items.append(Paragraph(f"[Missing screenshot: {os.path.basename(path)}]", ParagraphStyle(name="Missing", parent=styles["tc"], textColor=ACCENT_ORANGE)))
        return items

    # Ensure width matches 6.5in; allow slight overflow beyond frame by using an Indenter-like trick via negative space
    try:
        img = Image(path, width=SHOT_W, height=SHOT_H)
        img.hAlign = "CENTER"
        items.append(img)
        items.append(Paragraph(caption, styles["caption"]))
    except Exception as e:
        items.append(Paragraph(f"[Error loading {os.path.basename(path)}: {e}]", ParagraphStyle(name="Err", parent=styles["tc"], textColor=ACCENT_ORANGE)))
    return items


# =============================
# Content
# =============================

PROJECT_TITLE = "Static Website Deployment with AWS S3 and CloudFront"
PROJECT_SUBTITLE = "Infrastructure-as-Code with Terraform for a globally distributed static portfolio site"

# Adjust or auto-detect where relevant
LIVE_URL = "https://dbnp3womfvfzi.cloudfront.net"
AUTHOR = "thaboxan"
REPO = repo_basename()
TODAY = datetime.now().strftime("%B %d, %Y")

ORIGINAL_TASK_DESCRIPTION = (
    "Deploy a production-ready static website on AWS using S3 for website hosting and CloudFront for global content delivery. "
    "Automate infrastructure with Terraform, enable secure access via Origin Access Control, and publish the built site assets. "
    "Provide documentation, cost-conscious configuration, and verification screenshots."
)


def build_story():
    styles = build_styles()
    story = []

    # Cover Page
    story.append(Paragraph(PROJECT_TITLE, styles["title"]))
    story.append(Paragraph(PROJECT_SUBTITLE, styles["subtitle"]))

    # Info table
    info_rows = [
        ("Project", PROJECT_TITLE),
        ("Repository", REPO),
        ("Author", AUTHOR),
        ("Date", TODAY),
        ("Live URL", f"<link href='{LIVE_URL}' color='{PRIMARY_BLUE}'>" + LIVE_URL + "</link>"),
        ("Stack", "AWS S3, AWS CloudFront, Terraform, HTML/CSS, AWS CLI"),
    ]
    story.append(Spacer(1, 12))
    story.append(info_table(info_rows, styles))
    story.append(Spacer(1, 18))
    story.append(Paragraph("Corporate-ready PDF generated via Python ReportLab with modern styling.", styles["small"]))
    story.append(PageBreak())

    # Executive Summary
    story += section_header("📄 Executive Summary", styles, accent=PRIMARY_BLUE)
    summary_text = (
        "This engagement delivers a robust, cost-effective static website platform on AWS. The site is hosted in Amazon S3 "
        "and distributed globally via Amazon CloudFront. Terraform codifies the infrastructure for consistency and repeatability. "
        "Security follows best practices with CloudFront as the single entry point and S3 protected by Origin Access Control."
    )
    story.append(Paragraph(summary_text, styles["body"]))

    # Requirements
    story += section_header("📋 Requirements", styles, accent=SECONDARY_PURPLE)
    story.append(Paragraph("Original Task Description", styles["h2"]))
    story.append(Paragraph(ORIGINAL_TASK_DESCRIPTION, styles["callout"]))

    deliverables = [
        ("Terraform IaC for S3 + CloudFront (OAC, default root object, HTTPS)", "Done"),
        ("S3 bucket static website configuration and policy", "Done"),
        ("Build and publish site artifacts (index.html, assets)", "Done"),
        ("Verification screenshots (S3, CloudFront, Live)", "Done"),
        ("Documentation (README, PDF report)", "Done"),
    ]
    story.append(Spacer(1, 6))
    story.append(deliverables_table(deliverables, styles))
    story.append(PageBreak())

    # Implementation Details
    story += section_header("🧩 Implementation Details", styles, accent=PRIMARY_BLUE)
    impl_points = [
        "Provisioned AWS resources via Terraform: S3 bucket with versioning, CloudFront distribution, and Origin Access Control.",
        "Restricted bucket access to CloudFront using OAC; public website access flows exclusively through CloudFront.",
        "Configured default root object (index.html) and optimized CloudFront behaviors for static assets.",
        "Uploaded built website artifacts to S3; validated correct content-types for CSS/JS/images.",
        "Performed deployment validation and recorded evidence screenshots.",
    ]
    for p in impl_points:
        story.append(Paragraph(f"• {p}", styles["body"]))

    story.append(Spacer(1, 10))

    # Testing and Verification with Screenshots
    story += section_header("🧪 Testing & Verification", styles, accent=SECONDARY_PURPLE)

    screenshots = [
        (os.path.join("screenshots", "s3-settings.png"), "S3 bucket configuration and static website settings."),
        (os.path.join("screenshots", "bucket-policy.png"), "Bucket policy allowing least-privilege access for website content."),
        (os.path.join("screenshots", "cloudfront-distribution.png"), "CloudFront distribution settings with OAC and default behavior."),
        (os.path.join("screenshots", "website-live.png"), "Live website served via CloudFront global edge locations."),
        (os.path.join("screenshots", "week_8.png"), "Deployment summary overview of resources and outcomes."),
    ]

    missing = []
    for pth, cap in screenshots:
        if not os.path.exists(pth):
            missing.append(os.path.basename(pth))
        story += screenshot_flowable(pth, cap, styles)
        story.append(Spacer(1, 16))

    story.append(PageBreak())

    # Conclusion
    story += section_header("🏁 Conclusion", styles, accent=PRIMARY_BLUE)
    conclusion_text = (
        "The solution meets all stated objectives: it is globally performant, secure by design, automated via Terraform, "
        "and documented. The platform is production-ready and positioned for low operational overhead and cost efficiency."
    )
    story.append(Paragraph(conclusion_text, styles["body"]))

    metrics = [
        ("Provisioning Time", "~15 minutes", "Includes CloudFront deployment propagation."),
        ("Availability", ">99.9%", "Backed by AWS service SLAs."),
        ("Security Posture", "OAC-enabled", "Direct S3 access restricted; HTTPS enforced."),
        ("Scalability", "Global CDN", "Auto-scales via CloudFront edge network."),
    ]
    story.append(success_metrics_table(metrics, styles))

    story.append(Spacer(1, 18))
    story.append(Paragraph("Technical Summary", styles["h2"]))
    story.append(
        Paragraph(
            "S3 provides durable object storage and static website hosting; CloudFront delivers content with low latency. "
            "Terraform codifies the infrastructure, enabling reproducible deployments and change control.",
            styles["body"],
        )
    )

    return story


def build_pdf(output_path: str) -> int:
    try:
        doc = SimpleDocTemplate(
            output_path,
            pagesize=PAGE_SIZE,
            leftMargin=MARGIN,
            rightMargin=MARGIN,
            topMargin=MARGIN,
            bottomMargin=MARGIN,
            title=f"{PROJECT_TITLE} Report",
            author=AUTHOR,
        )
        story = build_story()
        doc.build(story)
        return 0
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return 1


if __name__ == "__main__":
    out = OUTPUT_PDF
    rc = build_pdf(out)
    if rc == 0:
        print(f"PDF successfully created: {out}")
    else:
        sys.exit(rc)
