from flask import Flask, request
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import os

app = Flask(__name__)


@app.route("/", methods=["GET"])
def peer():
    msg = request.args.get("msg", "Hello, Peer!")
    name = request.args.get("name", "Peer")
    group = request.args.get("group", "General")
    add_message_to_text_file(msg, name, group)
    generate_pdf(group)
    add_message_to_pdf(msg, name, group)

    # kill adobe acrobat process to force reload of updated.pdf
    if os.name == "nt":
        os.system("taskkill /f /im AcroRd32.exe")
    else:
        os.system("osascript -e 'tell application \"Adobe Acrobat\" to quit'")
        os.system("osascript -e 'tell application \"Chrome\" to quit'")

    os.system("sleep 10;open -a Adobe\ Acrobat new_message.pdf")
    return "Message Received"


def add_message_to_text_file(msg, name, group):
    with open(group + ".txt", "a") as f:
        f.write(f"{name}:{msg}\n")


def add_message_to_pdf(msg, name, group):
    # Create a PDF in memory
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # can.drawString(100, 750, f"Message: {msg}")
    # can.drawString(100, 730, f"From: {name}")
    # draw a String for each msg in {group}.txt
    with open(group + ".txt", "r") as f:
        lines = f.readlines()
        y = 700
        for line in lines:  # Show only the last 5 messages
            can.drawString(100, y, line.strip())
            y -= 20

    can.save()

    # Move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfReader(packet)

    # Read the existing PDF
    existing_pdf = PdfReader("message.pdf")
    output = PdfWriter()

    # Add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

    # Write the result to a new PDF file
    with open("new_message.pdf", "wb") as outputStream:
        output.write(outputStream)


def generate_pdf(group):
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    with open(group + ".txt", "r") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            can.drawString(100, 750 - (i * 15), line.strip())

    # label for the editable field
    can.drawString(100, 110, "New Message:")

    # optional visual rectangle behind the field
    can.rect(100, 80, 400, 20, stroke=1, fill=0)

    # Add an AcroForm text field so users can type in a PDF editor
    # ReportLab exposes the form API as can.acroForm (or can.acroform in some versions).
    try:
        can.acroForm.textfield(
            name="new_message",
            tooltip="Type your message here",
            x=100,
            y=80,
            width=400,
            height=20,
            borderStyle="inset",
            forceBorder=True,
            value="",
        )
    except Exception:
        try:
            can.acroform.textfield(
                name="new_message",
                tooltip="Type your message here",
                x=100,
                y=80,
                width=400,
                height=20,
                borderStyle="inset",
                forceBorder=True,
                value="",
            )
        except Exception:
            # If the environment doesn't support AcroForm, continue without a form field.
            pass

    # small submit label and link (optional)
    can.drawString(100, 50, "Submit")
    js = "msg = this.getField('new_message').value; " "alert('Submitting: ' + msg); "

    can.linkURL("javascript:" + js, (100, 40, 150, 60), relative=1)

    can.save()

    packet.seek(0)
    new_pdf = PdfReader(packet)
    output = PdfWriter()
    output.add_page(new_pdf.pages[0])

    with open("updated.pdf", "wb") as outputStream:
        output.write(outputStream)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012)
