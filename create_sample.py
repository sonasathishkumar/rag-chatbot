import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_sample_pdf():
    os.makedirs('sample_docs', exist_ok=True)
    pdf_path = 'sample_docs/sample.pdf'
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 700, "AI Technology Report 2024")
    
    c.setFont("Helvetica", 12)
    intro_text = [
        "1. Introduction",
        "Artificial Intelligence (AI) has rapidly evolved in 2024, becoming deeply integrated into",
        "enterprise operations, software engineering, and customer service.",
        "This report outlines the key advancements and impacts of AI over the past year.",
        "We are seeing a massive shift towards retrieval-augmented generation (RAG) applications",
        "that allow companies to converse with their private documents."
    ]
    
    y = 650
    for line in intro_text:
        c.drawString(100, y, line)
        y -= 20
        
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y, "2. Key Findings")
    y -= 20
    
    c.setFont("Helvetica", 12)
    findings_text = [
        "- Adoption Rates: 78% of fortune 500 companies have adopted generative AI.",
        "- Productivity: Developers using AI coding assistants report a 40% increase in productivity.",
        "- Cost Reduction: Automated customer support has reduced operational costs by 30%.",
        "- Local Models: There is a growing trend to run smaller, efficient models locally to",
        "  preserve data privacy and reduce API costs.",
        "- Vector Databases: Tools like FAISS, Pinecone, and Milvus have seen a 200% increase",
        "  in enterprise adoption as RAG becomes the standard for corporate AI."
    ]
    
    for line in findings_text:
        c.drawString(100, y, line)
        y -= 20

    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y, "3. Recommendations")
    y -= 20
    
    c.setFont("Helvetica", 12)
    recs_text = [
        "1. Invest in Local Infrastructure: Companies should begin moving away from reliance on",
        "   external API providers for sensitive data processing.",
        "2. Train Employees: Focus on prompt engineering and AI literacy across all departments.",
        "3. Implement RAG Systems: Deploy internal Q&A bots linked to company wikis and documents",
        "   to streamline knowledge discovery.",
        "4. Monitor Security: Ensure that vector databases are properly secured and that AI models",
        "   do not hallucinate critical business information."
    ]
    
    for line in recs_text:
        c.drawString(100, y, line)
        y -= 20
        
    c.save()
    print(f"Created sample PDF at: {pdf_path}")

if __name__ == "__main__":
    create_sample_pdf()
