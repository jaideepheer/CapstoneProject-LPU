from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
my_doc = SimpleDocTemplate('myfile.pdf')
sample_style_sheet = getSampleStyleSheet()
flowables = []
paragraph_1 = Paragraph("A title", sample_style_sheet['Heading1'])
paragraph_2 = Paragraph(
    "Some normal body text",
    sample_style_sheet['BodyText']
)
flowables.append(paragraph_1)
flowables.append(paragraph_2)
my_doc.build(flowables)