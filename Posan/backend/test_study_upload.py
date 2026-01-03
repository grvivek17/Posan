import requests
import os

url = "http://localhost:8000/api/v1/ai/study-material/upload"
params = {"age_group": "9-11"}

# Create a small sample PDF
from reportlab.pdfgen import canvas
sample_pdf = "sample_study.pdf"
c = canvas.Canvas(sample_pdf)
c.drawString(100, 750, "Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize foods with the help of chlorophyll pigments. In plants, photosynthesis generally takes place in leaves, which consist of chloroplasts.")
c.drawString(100, 730, "The process involves the intake of carbon dioxide and water, and the release of oxygen as a byproduct. It is essential for life on Earth as it provides the primary source of energy for almost all organisms.")
c.save()

try:
    with open(sample_pdf, "rb") as f:
        files = {"file": (sample_pdf, f, "application/pdf")}
        response = requests.post(url, params=params, files=files)
        
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success!")
        print(response.json().get("summary")[:200] + "...")
    else:
        print(f"Error: {response.text}")
finally:
    if os.path.exists(sample_pdf):
        os.unlink(sample_pdf)
