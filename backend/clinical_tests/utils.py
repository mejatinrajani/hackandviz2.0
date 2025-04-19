from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from io import BytesIO
from django.conf import settings
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
import os

def generate_clinical_report_pdf(session):
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    story = []

    # Add logo if exists
    logo_path = os.path.join(settings.STATIC_ROOT, 'img', 'logo.png') if settings.STATIC_ROOT else ''
    if os.path.exists(logo_path):
        company_logo = Image(logo_path, width=200, height=50)
        company_logo.hAlign = 'CENTER'
        story.append(company_logo)

    # Title
    title_style = getSampleStyleSheet()['Title']
    title = Paragraph("Clinical Report", title_style)
    story.append(title)

    # User and test info
    user_style = getSampleStyleSheet()['Normal']
    user_info = f"<strong>User:</strong> {session.user.username}<br/>"
    user_info += f"<strong>Test:</strong> {session.test.name}<br/>"
    user_info += f"<strong>Associated Disorder:</strong> {session.prediction.final_prediction if session.prediction else 'Unknown'}<br/>"
    user_info += f"<strong>Date of Test:</strong> {session.started_at.strftime('%Y-%m-%d %H:%M:%S')}<br/>"
    user_info_paragraph = Paragraph(user_info, user_style)
    story.append(user_info_paragraph)

    # Test Results
    test_results_style = ParagraphStyle(
        'TestResults', fontName='Helvetica-Bold', fontSize=12, textColor=colors.black, spaceAfter=12
    )
    test_results = f"<strong>Total Score:</strong> {session.total_score if session.total_score is not None else 'N/A'}<br/>"
    test_results += f"<strong>Severity:</strong> {session.severity if session.severity else 'N/A'}<br/>"
    test_results_paragraph = Paragraph(test_results, test_results_style)
    story.append(test_results_paragraph)

    # Detailed Analysis
    analysis_style = ParagraphStyle(
        'Analysis', fontName='Helvetica', fontSize=10, textColor=colors.black, spaceAfter=12
    )
    analysis_text = "<strong>Detailed Analysis:</strong><br/>"
    for response in session.responses.all():
        question_text = response.question.text.splitlines()[0]
        answer = response.open_ended_answer or (response.selected_option['text'] if response.selected_option else "No response")
        analysis_text += f"<strong>Question {response.question.order}:</strong> {question_text}<br/>"
        analysis_text += f"<strong>User Response:</strong> {answer}<br/>"
        if response.follow_up_questions:
            analysis_text += f"<strong>Follow-Up Questions:</strong> {'; '.join(response.follow_up_questions)}<br/>"
        analysis_text += "<br/>"
    analysis_paragraph = Paragraph(analysis_text, analysis_style)
    story.append(analysis_paragraph)

    # Disclaimer
    disclaimer_style = getSampleStyleSheet()['Normal']
    disclaimer = Paragraph(
        "This is not a diagnosis. Consult a licensed mental health professional for an accurate assessment.",
        disclaimer_style
    )
    story.append(disclaimer)

    # Resources
    resources = Paragraph(
        "For support, consider visiting www.nimh.nih.gov or contacting a local mental health provider.",
        disclaimer_style
    )
    story.append(resources)

    pdf.build(story)
    buffer.seek(0)
    return buffer