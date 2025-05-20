"""
Report generator module for PDF generation of feedback reports.
"""
import io
import base64
import logging
import matplotlib
matplotlib.use('Agg')  # Use Agg backend to avoid requiring a display
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from fpdf import FPDF
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)

class FeedbackReportPDF(FPDF):
    """Custom PDF class for generating feedback reports."""
    
    def __init__(self, title="Feedback Analysis Report", orientation='P', unit='mm', format='A4'):
        # For FPDF, parameter documentation shows: orientation='P'|'L', unit='pt'|'mm'|'cm'|'in', format='A3'|'A4'|'A5'|'Letter'|'Legal'|tuple of width and height (in unit)
        # We're providing 'P', 'mm', and 'A4' which all should be acceptable
        super().__init__()
        self.title = title
        self.WIDTH = 210  # A4 width in mm
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, self.title, 0, 1, 'C')
        self.set_font('Arial', '', 12)
        self.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'C')
        self.ln(10)
    
    def chapter_title(self, title):
        """Add a chapter title to the PDF."""
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)
    
    def section_title(self, title):
        """Add a section title to the PDF."""
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
    
    def add_paragraph(self, text):
        """Add a paragraph of text to the PDF."""
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 5, text)
        self.ln(4)
    
    def add_image(self, img_data, width=160):
        """Add an image to the PDF."""
        x = (self.WIDTH - width) / 2  # Center the image
        self.image(img_data, x=x, w=width)
        self.ln(4)
    
    def add_table(self, headers, data):
        """Add a table to the PDF."""
        # Set column width
        col_width = self.WIDTH / len(headers)
        
        # Table headers
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(200, 220, 255)
        for header in headers:
            self.cell(col_width, 7, header, 1, 0, 'C', True)
        self.ln()
        
        # Table data
        self.set_font('Arial', '', 10)
        self.set_fill_color(255, 255, 255)
        odd_row = True
        for row in data:
            if odd_row:
                self.set_fill_color(245, 245, 245)
            else:
                self.set_fill_color(255, 255, 255)
            for item in row:
                self.cell(col_width, 6, str(item), 1, 0, 'C', True)
            self.ln()
            odd_row = not odd_row


from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

def create_feedback_report(data):
    """Generate a PDF report with feedback analysis"""
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Feedback Analysis Report', ln=True, align='C')

    # Department and date range
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Department: {data['department']}", ln=True)
    pdf.cell(0, 10, f"Time Period: Last {data['days']} days", ln=True)

    # Summary statistics
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Summary', ln=True)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Total Feedback: {data['total_feedback']}", ln=True)
    pdf.cell(0, 10, f"Categories Analyzed: {data['num_categories']}", ln=True)

    # Charts
    if data.get('category_ratings'):
        # Create category ratings chart
        fig, ax = plt.subplots(figsize=(10, 6))
        categories = list(data['category_ratings'].keys())
        ratings = list(data['category_ratings'].values())
        ax.bar(categories, ratings)
        plt.xticks(rotation=45)
        plt.title('Average Ratings by Category')
        plt.tight_layout()

        # Save chart to bytes
        img_bytes = BytesIO()
        plt.savefig(img_bytes, format='png')
        img_bytes.seek(0)

        # Add to PDF
        pdf.image(img_bytes, x=10, w=190)
        plt.close()

    # Add improvement suggestions
    if data.get('improvement_suggestions'):
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Improvement Suggestions', ln=True)
        pdf.set_font('Arial', '', 12)
        for suggestion in data['improvement_suggestions']:
            pdf.multi_cell(0, 10, f"• {suggestion['theme']}: {suggestion['suggestion']}")

    # Get PDF bytes
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes


def create_sentiment_trends_chart(trend_data):
    """
    Create a sentiment trends chart for the report.
    
    Args:
        trend_data: List of (period, data) tuples with sentiment counts
    
    Returns:
        BytesIO object containing the image
    """
    periods = [item[0] for item in trend_data]
    positive_counts = [item[1]['positive'] for item in trend_data]
    neutral_counts = [item[1]['neutral'] for item in trend_data]
    negative_counts = [item[1]['negative'] for item in trend_data]
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create stacked bar chart
    ax.bar(periods, positive_counts, label='Positive', color='#4CAF50', alpha=0.8)
    ax.bar(periods, neutral_counts, bottom=positive_counts, label='Neutral', color='#FFC107', alpha=0.8)
    ax.bar(periods, [p + n + neg for p, n, neg in zip(positive_counts, neutral_counts, negative_counts)], 
           bottom=0, label='Total', color='#2196F3', alpha=0.2)
    
    # Plot negative sentiment as a line
    ax.plot(periods, negative_counts, label='Negative', color='#F44336', 
            marker='o', linestyle='-', linewidth=2, markersize=8)
    
    # Add labels and title
    ax.set_title('Sentiment Trends Over Time', fontsize=14)
    ax.set_xlabel('Time Period', fontsize=12)
    ax.set_ylabel('Number of Feedback Items', fontsize=12)
    
    # Configure x-axis
    plt.xticks(rotation=45)
    
    # Add a grid for better readability
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Add legend
    ax.legend()
    
    # Adjust layout to make room for the rotated x-axis labels
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buf)
    plt.close(fig)
    
    return buf


def create_sentiment_ratio_chart(sentiment_ratio_data):
    """
    Create a sentiment ratio chart for the report.
    
    Args:
        sentiment_ratio_data: List of (period, data) tuples with sentiment ratios
    
    Returns:
        BytesIO object containing the image
    """
    periods = [item[0] for item in sentiment_ratio_data]
    pos_ratios = [item[1]['positive_ratio'] for item in sentiment_ratio_data]
    neu_ratios = [item[1]['neutral_ratio'] for item in sentiment_ratio_data]
    neg_ratios = [item[1]['negative_ratio'] for item in sentiment_ratio_data]
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create the area plots for each sentiment
    x = np.arange(len(periods))
    ax.fill_between(x, 0, pos_ratios, label='Positive', color='#4CAF50', alpha=0.5)
    ax.fill_between(x, pos_ratios, [p + n for p, n in zip(pos_ratios, neu_ratios)], 
                    label='Neutral', color='#FFC107', alpha=0.5)
    ax.fill_between(x, [p + n for p, n in zip(pos_ratios, neu_ratios)], 
                    [p + n + neg for p, n, neg in zip(pos_ratios, neu_ratios, neg_ratios)], 
                    label='Negative', color='#F44336', alpha=0.5)
    
    # Add labels and title
    ax.set_title('Sentiment Ratio Over Time', fontsize=14)
    ax.set_xlabel('Time Period', fontsize=12)
    ax.set_ylabel('Percentage', fontsize=12)
    
    # Configure x-axis
    plt.xticks(x, periods, rotation=45)
    
    # Configure y-axis to show percentages
    ax.set_ylim(0, 100)
    ax.set_yticks(np.arange(0, 101, 10))
    ax.set_yticklabels([f"{i}%" for i in range(0, 101, 10)])
    
    # Add a grid for better readability
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Add legend
    ax.legend()
    
    # Adjust layout to make room for the rotated x-axis labels
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buf)
    plt.close(fig)
    
    return buf


def create_category_ratings_chart(category_ratings):
    """
    Create a bar chart showing average ratings by category.
    
    Args:
        category_ratings: Dictionary mapping category names to average ratings
    
    Returns:
        BytesIO object containing the image
    """
    categories = list(category_ratings.keys())
    ratings = list(category_ratings.values())
    
    # Create color gradient based on ratings
    colors = []
    for rating in ratings:
        if rating < 2.5:
            colors.append('#F44336')  # Red for low ratings
        elif rating < 3.5:
            colors.append('#FFC107')  # Yellow for medium ratings
        else:
            colors.append('#4CAF50')  # Green for high ratings
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bar chart
    bars = ax.bar(categories, ratings, color=colors, alpha=0.8)
    
    # Add labels and title
    ax.set_title('Average Rating by Category', fontsize=14)
    ax.set_xlabel('Category', fontsize=12)
    ax.set_ylabel('Average Rating (1-5)', fontsize=12)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{height:.2f}', ha='center', va='bottom')
    
    # Configure y-axis
    ax.set_ylim(0, 5.5)  # Scale from 0 to 5 with space for labels
    
    # Configure x-axis
    plt.xticks(rotation=45, ha='right')
    
    # Add a grid for better readability
    ax.grid(True, linestyle='--', alpha=0.7, axis='y')
    
    # Add a horizontal line at rating 3 (neutral)
    ax.axhline(y=3, color='gray', linestyle='--', alpha=0.5)
    
    # Adjust layout to make room for the rotated x-axis labels
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    canvas = FigureCanvas(fig)
    canvas.print_png(buf)
    plt.close(fig)
    
    return buf