from flask import Flask, request
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import os
import json
import pyautogui

app = Flask(__name__)

file_num = 0


@app.route("/", methods=["GET"])
def peer():
    global file_num
    msg = request.args.get("msg", "Hello, Peer!")
    name = request.args.get("name", "Peer")
    group = request.args.get("group", "General")
    local = request.args.get("local", "False")
    add_message_to_text_file(msg, name, group)
    add_messages_to_pdf(group)

    # The following commands are for macOS to close and reopen Adobe Acrobat
    #os.system("osascript -e 'tell application \"Adobe Acrobat\" to quit'")

    

    if local == "True":
        # Adobe acrobat will ask if you want to save changes, use pyautogui to click "Don't Save"
        pyautogui.sleep(5)
        pyautogui.click(x=960, y=540)  # Coordinates for "Don't Save" button

    os.system("osascript -e 'tell application \"Chrome\" to quit'")
    os.system(f"open -a Adobe\\ Acrobat new_message_{file_num}.pdf")

    file_num += 1

    return "Message Received"


def add_message_to_text_file(msg, name, group):
    with open(group + ".txt", "a") as f:
        f.write(f"{name}:{msg}\\n")


# def add_messages_to_pdf(group):
#     # Create a PDF in memory
#     packet = BytesIO()
#     can = canvas.Canvas(packet, pagesize=letter)

#     # can.drawString(100, 750, f"Message: {msg}")
#     # can.drawString(100, 730, f"From: {name}")
#     # draw a String for each msg in {group}.txt
#     with open(group + ".txt", "r") as f:
#         lines = f.readlines()
#         y = 700
#         for line in lines:  # Show only the last 5 messages
#             can.drawString(100, y, line.strip())
#             y -= 20

#     can.save()

#     # Move to the beginning of the StringIO buffer
#     packet.seek(0)
#     new_pdf = PdfReader(packet)

#     # Read the existing PDF
#     existing_pdf = PdfReader("message.pdf")
#     output = PdfWriter()

#     # Add the "watermark" (which is the new pdf) on the existing page
#     page = existing_pdf.pages[0]
#     page.merge_page(new_pdf.pages[0])
#     output.add_page(page)

#     # Write the result to a new PDF file
#     with open("new_message.pdf", "wb") as outputStream:
#         output.write(outputStream)


def add_messages_to_pdf(group):
    # Read the existing PDF with form fields
    # existing_pdf = PdfReader("message.pdf")
    # output = PdfWriter()

    reader = PdfReader("message.pdf")
    writer = PdfWriter()

    writer.append_pages_from_reader(reader)

    # Add all pages from the existing PDF
    # for page in existing_pdf.pages:
    #     output.add_page(page)

    # Read all messages from the text file
    with open(group + ".txt", "r") as f:
        lines = f.readlines()
    
    # Combine all messages into a single string with newlines
    messages_text = "".join(lines)
    # messages_text = "Peer:hihi\\nPeer:hello"

    # Update the ChatBox form field with the messages
    # output.update_page_form_field_values(
    #     output.pages[0], {"ChatBox": messages_text}
    # )

    # js = "var f = this.getField('Text1'); f.value = 'hihi';"

    # js = "function foo(){var f = this.getField('Text1');f.value = 'hihi';};;app.setTimeOut(foo, 500);"

    # Build safe JS (assign into the ChatBox field, after a small delay)
    code_inner = f'var f = this.getField("Text1"); f.value = {json.dumps(messages_text)};'
    js = f"app.setTimeOut('{code_inner}', 500);"

    writer.add_js(js)
    global file_num

    # Write the result to a new PDF file
    with open(f"new_message_{file_num}.pdf", "wb") as outputStream:
        # output.write(outputStream)
        writer.write(outputStream)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5012)
