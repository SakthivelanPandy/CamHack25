from flask import Flask, request
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import os
import pyautogui

app = Flask(__name__)


@app.route("/", methods=["GET"])
def peer():
    msg = request.args.get("msg", "Hello, Peer!")
    name = request.args.get("name", "Peer")
    group = request.args.get("group", "General")
    local = request.args.get("local", "False")
    add_message_to_text_file(msg, name, group)
    add_messages_to_pdf(group)

    # The following commands are for macOS to close and reopen Adobe Acrobat
    os.system("osascript -e 'tell application \"Adobe Acrobat\" to quit'")

    if local == "True":
        # Adobe acrobat will ask if you want to save changes, use pyautogui to click "Don't Save"
        pyautogui.sleep(5)
        pyautogui.click(x=960, y=540)  # Coordinates for "Don't Save" button

    os.system("osascript -e 'tell application \"Chrome\" to quit'")
    os.system("sleep 10;open -a Adobe\ Acrobat new_message.pdf")

    return "Message Received"


def add_message_to_text_file(msg, name, group):
    with open(group + ".txt", "a") as f:
        f.write(f"{name}:{msg}\n")


def add_messages_to_pdf(group):
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012)
