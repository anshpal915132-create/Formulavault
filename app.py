import streamlit as st
from fpdf import FPDF
import tempfile
import os
import google.generativeai as genai

Configure Gemini API using Streamlit Secrets (Yeh key secure rahegi aur users ko enter nahi karni padegi)
if "GEMINI_API_KEY" in st.secrets:
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
st.error("⚠️ GEMINI_API_KEY missing in Streamlit Secrets! Please configure it in your deployment settings.")

st.set_page_config(page_title="FormulaVault", page_icon="📚", layout="centered")

st.title("📚 FormulaVault")
st.subheader("Instant AI-Powered Chapter Summary & Formula Notes Generator")
st.write("Apni class, exam aur chapter select karein, aur AI ek click me professional PDF notes taiyar kar dega!")

Inputs
class_name = st.selectbox("Select Class", ["Class 11", "Class 12"])
exam = st.selectbox("Select Exam / Category", ["JEE Main & Advanced", "NEET", "Board Exams"])
subject = st.selectbox("Select Subject", ["Physics", "Chemistry", "Mathematics"])
chapter_name = st.text_input("Enter Chapter Name", "Laws of Motion")

if st.button("Generate AI Notes & PDF", type="primary"):
if not chapter_name.strip():
st.warning("Please enter a valid chapter name!")
else:
with st.spinner("🚀 AI is generating chapter summary and formulas... Please wait!"):
try:
# Prompting Gemini for structured notes
prompt = f"""
You are an expert tutor for {exam} ({class_name}) for {subject}.
Generate comprehensive revision notes for the chapter: "{chapter_name}".

Provide the response strictly using these exact markers so they can be parsed:

---SUMMARY---
[Write a concise, high-yield chapter summary in 4-5 bullet points or sentences covering core concepts.]

---MAIN_FORMULAS---
[List 4 to 6 high-weightage formulas, one formula per line, with brief notation/meaning]

---OTHER_FORMULAS---
[List other useful formulas, one formula per line]
"""

model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content(prompt)
text = response.text

# Parsing response safely
summary = "Summary generation failed."
main_formulas_text = ""
other_formulas_text = ""

if "---SUMMARY---" in text and "---MAIN_FORMULAS---" in text:
parts = text.split("---SUMMARY---")[1].split("---MAIN_FORMULAS---")
summary = parts[0].strip()

formulas_part = parts[1].split("---OTHER_FORMULAS---")
main_formulas_text = formulas_part[0].strip()
other_formulas_text = formulas_part[1].strip() if len(formulas_part) > 1 else ""
else:
summary = text
main_formulas_text = "F = ma"
other_formulas_text = "Check generated text above"

except Exception as e:
st.error(f"Error connecting to AI: {e}")
summary = "Could not generate summary due to an error."
main_formulas_text = "N/A"
other_formulas_text = "N/A"

# PDF Generation Logic
class PDFReport(FPDF):
def header(self):
self.set_font('helvetica', 'B', 16)
self.set_text_color(33, 37, 41)
self.cell(0, 10, 'FormulaVault - Revision Notes', 0, 1, 'C')
self.ln(5)

def footer(self):
self.set_y(-15)
self.set_font('helvetica', 'I', 9)
self.set_text_color(100, 100, 100)
self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

pdf = PDFReport()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)

# Metadata Box
pdf.set_font('helvetica', 'B', 11)
pdf.set_fill_color(240, 240, 240)
pdf.cell(0, 8, f"Class: {class_name} | Exam: {exam} | Subject: {subject}", 0, 1, 'L', fill=True)
pdf.ln(5)

# Chapter Title
pdf.set_font('helvetica', 'B', 14)
pdf.set_text_color(13, 110, 253)
pdf.cell(0, 8, f"Chapter: {chapter_name}", 0, 1, 'L')
pdf.ln(3)

# Summary Section
pdf.set_font('helvetica', 'B', 12)
pdf.set_text_color(33, 37, 41)
pdf.cell(0, 8, "1. Chapter Summary", 0, 1, 'L')
pdf.set_font('helvetica', '', 10)
pdf.multi_cell(0, 6, summary)
pdf.ln(5)

# Main Formulas Section
pdf.set_font('helvetica', 'B', 12)
pdf.set_text_color(220, 53, 69)
pdf.cell(0, 8, "2. High-Weightage (Main) Formulas", 0, 1, 'L')
pdf.set_font('helvetica', 'B', 10)
pdf.set_text_color(33, 37, 41)
for f in main_formulas_text.split('\n'):
if f.strip():
pdf.cell(0, 6, f" [★] {f}", 0, 1, 'L')
pdf.ln(5)

# Other Formulas Section
pdf.set_font('helvetica', 'B', 12)
pdf.set_text_color(108, 117, 125)
pdf.cell(0, 8, "3. All Other Formulas & Key Relations", 0, 1, 'L')
pdf.set_font('helvetica', '', 10)
for f in other_formulas_text.split('\n'):
if f.strip():
pdf.cell(0, 6, f" • {f}", 0, 1, 'L')

# Save temporary file for download
with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
pdf.output(tmp_file.name)
tmp_path = tmp_file.name

with open(tmp_path, "rb") as file:
st.download_button(
label="📥 Click Here to Download PDF Notes",
data=file,
file_name=f"{chapter_name.replace(' ', '_')}_Notes.pdf",
mime="application/pdf"
)
st.success("🎉 Aapka PDF taiyar hai! Upar diye gaye download button par click karein.")