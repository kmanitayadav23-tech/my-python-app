import os
import json
import base64
from http.server import BaseHTTPRequestHandler, HTTPServer
import google.generativeai as genai

# अपने Gemini API Key को यहाँ सेट करें
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "YOUR_API_KEY_HERE")
genai.configure(api_key=GOOGLE_API_KEY)

# जेमिनी मॉडल सेटअप (gemini-1.5-flash मल्टीमॉडल और चैट दोनों के लिए बेहतरीन है)
model = genai.GenerativeModel('gemini-1.5-flash')
chat_session = model.start_chat(history=[])

# सुंदर HTML, CSS और JavaScript वाला इंटरफेस (UI, Chat Memory और Image Upload के साथ)
HTML_PAGE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini AI Assistant</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #eef2f3; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; height: 100vh; }
        .chat-container { width: 100%; max-width: 600px; background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); display: flex; flex-direction: column; overflow: hidden; height: 85vh; }
        .chat-header { background: #4f46e5; color: white; padding: 15px; text-align: center; font-size: 1.2rem; font-weight: bold; }
        .chat-box { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; background: #f9fafb; }
        .message { max-width: 80%; padding: 10px 14px; border-radius: 8px; line-height: 1.4; word-wrap: break-word; }
        .user-message { background: #4f46e5; color: white; align-self: flex-end; border-bottom-right-radius: 2px; }
        .ai-message { background: #e5e7eb; color: #1f2937; align-self: flex-start; border-bottom-left-radius: 2px; }
        .chat-input-area { display: flex; padding: 10px; background: white; border-top: 1px solid #e5e7eb; gap: 8px; align-items: center; }
        .chat-input-area input[type="text"] { flex: 1; padding: 10px; border: 1px solid #d1d5db; border-radius: 6px; outline: none; font-size: 1rem; }
        .chat-input-area input[type="file"] { display: none; }
        .file-upload-btn { background: #e5e7eb; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-size: 0.9rem; color: #374151; }
        .chat-input-area button { background: #4f46e5; color: white; border: none; padding: 10px 16px; border-radius: 6px; cursor: pointer; font-weight: bold; }
        .chat-input-area button:hover { background: #4338ca; }
        #file-name { font-size: 0.8rem; color: #6b7280; max-width: 100px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">Gemini Pro AI (Chat & Vision)</div>
        <div class="chat-box" id="chat-box">
            <div class="message ai-message">नमस्ते! मैं आपका जेमिनी AI हूँ। आप मुझसे कुछ भी पूछ सकते हैं या तस्वीर अपलोड करके उसके बारे में जान सकते हैं।</div>
        </div>
        <div class="chat-input-area">
            <label for="image-input" class="file-upload-btn">📷 फोटो</label>
            <input type="file" id="image-input" accept="image/*">
            <span id="file-name"></span>
            <input type="text" id="user-input" placeholder="यहाँ अपना संदेश लिखें..." onkeydown="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">भेजें</button>
        </div>
    </div>

    <script>
        let selectedImageBase64 = null;
        let selectedImageMimeType = null;

        document.getElementById('image-input').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                document.getElementById('file-name').innerText = file.name;
                const reader = new FileReader();
                reader.onload = function(uploadEvent) {
                    const base64String = uploadEvent.target.result.split(',')[1];
                    selectedImageBase64 = base64String;
                    selectedImageMimeType = file.type;
                };
                reader.readAsDataURL(file);
            }
        });

        async function sendMessage() {
            const inputField = document.getElementById('user-input');
            const chatBox = document.getElementById('chat-box');
            const text = inputField.value.trim();

            if (!text && !selectedImageBase64) return;

            // यूजर का मैसेज स्क्रीन पर दिखाएं
            let userHtml = `<div class="message user-message">`;
            if (selectedImageBase64) {
                userHtml += `<img src="data:${selectedImageMimeType};base64,${selectedImageBase64}" style="max-width:150px; border-radius:5px; display:block; margin-bottom:5px;">`;
            }
            userHtml += `${text || '[इमेज भेजी गई]'}</div>`;
            chatBox.innerHTML += userHtml;

            const payloadText = text;
            const imgData = selectedImageBase64;
            const mimeType = selectedImageMimeType;

            // इनपुट साफ़ करें
            inputField.value = '';
            selectedImageBase64 = null;
            selectedImageMimeType = null;
            document.getElementById('file-name').innerText = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            // AI का लोडिंग मैसेज
            const loadingId = 'loading-' + Date.now();
            chatBox.innerHTML += `<div class="message ai-message" id="${loadingId}">सोच रहा हूँ...</div>`;
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text: payloadText, image: imgData, mime_type: mimeType })
                });
                const data = await response.json();
                
                document.getElementById(loadingId).remove();
                chatBox.innerHTML += `<div class="message ai-message">${data.reply.replace(/\\n/g, '<br>')}</div>`;
            } catch (error) {
                document.getElementById(loadingId).innerText = "कनेक्शन में एरर आई है!";
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    </script>
</body>
</html>
"""

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            try:
                req_json = json.loads(post_data.decode('utf-8'))
                user_text = req_json.get('text', '')
                image_base64 = req_json.get('image', None)
                mime_type = req_json.get('mime_type', 'image/jpeg')

                contents = []
                if image_base64:
                    image_bytes = base64.b64decode(image_base64)
                    contents.append({
                        'mime_type': mime_type,
                        'data': image_bytes
                    })
                
                if user_text:
                    contents.append(user_text)

                if contents:
                    # चैट सेशन से रिस्पॉन्स लेना ताकि मेमोरी बनी रहे
                    response = chat_session.send_message(contents)
                    reply_text = response.text
                else:
                    reply_text = "कृपया कुछ लिखकर या फोटो भेजकर पूछें।"

                response_data = json.dumps({"reply": reply_text})
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(response_data.encode("utf-8"))

            except Exception as e:
                err_data = json.dumps({"reply": f"एरर आ गई: {str(e)}"})
                self.send_response(500)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(err_data.encode("utf-8"))

def run():
    port = int(os.environ.get("PORT", 10000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Server running on port {port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
