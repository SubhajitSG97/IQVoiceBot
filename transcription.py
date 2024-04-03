import pdfkit
def create_transcription_pdf(data):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat Transcript</title>
    <style>
            body {
                font-family: Arial, sans-serif;
                padding: 10px;
            }
            .message-body {
                display: flex,
            
            }
            .message {
                margin-bottom: 10px;
            }
            .user-message {
                color: black;
                margin-left: 20px;
            }
            .saasha-message {
                color: black;
                margin-left: 20px;
                clear:both;
            }
            .message.saasha-message {
                float: left;
                 background: #c0d4f3;
                padding: 16px;
                border-radius: 13px;
            }
            
            .message.user-message {
                float: right;
                margin: 6px 19px 26px 32px;
                clear: both;
                background: #e3efe5;
                padding: 16px;
                border-radius: 13px;
            }
            .participant-class{
             text-transform: capitalize;
             margin-bottom: 4px;
             }
    </style>
    </head>
    <body>
    <h2 style="text-align:center">Transcription</h2>
    """

    for message in data:
        if message.get("participant") and message.get("message"):
            participant = message["participant"]
            message_text = message["message"].replace("\n", "<br>")
            html_content += f'<div class="message {participant}-message"><div class="participant-class"><b>{participant}</b>:</div> {message_text}</div>'

    html_content += """
    </body>
    </html>
    """

    # Save the HTML content to a file
    with open("chat_transcript.html", "w") as f:
        f.write(html_content)

    # Convert HTML to PDF
    pdfkit.from_file("chat_transcript.html", "chat_transcript.pdf")