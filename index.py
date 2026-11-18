import os
import json
import base64
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

# अपने Gemini API Key को यहाँ से उठाएगा
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")

# सुंदर HTML, CSS और JavaScript वाला इंटरफेस
HTML_PAGE = """<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gemini AI Assistant</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #121212; color: white; margin: 0; display: flex; justify-content: center; height: 100vh; }
        .chat-container { width: 100%; max-width: 600px; display: flex; flex-direction: column; background-color: #1e1e1e; height: 100%; }
        .chat-header { background: #4f46e5; color: white; padding: 15px; text-align: center; font-size: 1.2rem; font-weight: bold; }
        .chat-box { flex: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .message { max-width: 80%; padding: 10px 14px; border-radius: 12px; line-height: 1.4; word-wrap: break-word; }
        .user-message { background: #4f46e5; color: white; align-self: flex-end; }
        .bot-message { background: #2d2d2d; color: #e0e0e0; align-self: flex-start; }
        .input-area { display: flex; padding: 10px; background: #181818; gap: 8px; align-items: center; }
        input[type="text"] { flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #333; background: #252525; color: white; outline: none; }
        button, label.upload-btn { background: #4f46e5; color: white; border: none; padding: 10px 14px; border-radius: 8px; cursor: pointer; font-weight: bold; }
        input[type="file"] { display: none; }
        img.preview { max-width: 150px; border-radius: 8px; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">Krishna nand Vinod (Chat & Vision)</div>
        <div class="chat-box" id="chatBox">
            <div class="message bot-message">नमस्ते! मैं आपका जेमिनी AI हूँ। आप मुझसे कुछ भी पूछ सकते हैं या तस्वीर अपलोड करके उसके बारे में जान सकते हैं।</div>
        </div>
        <div class="input-area">
            <label class="upload-btn" for="imageInput">📷 फोटो</label>
            <input type="file" id="imageInput" accept="image/*">
            <input type="text" id="userInput" placeholder="यहाँ अपना संदेश लिखें..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">भेजें</button>
        </div>
    </div>

    <script>
        let selectedImageBase64 = null;
        let selectedMimeType = null;

        document.getElementById('imageInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                selectedMimeType = file.type;
                const reader = new FileReader();
                reader.onload = function(event) {
                    selectedImageBase64 = event.target.result.split(',')[1];
                    alert("फोटो चुन ली गई है! अब अपना सवाल लिखकर भेजें।");
                };
                reader.readAsDataURL(file);
            }
        });

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const text = input.value.trim();
            if (!text && !selectedImageBase64) return;

            const chatBox = document.getElementById('chatBox');
            const userDiv = document.createElement('div');
            userDiv.className = 'message user-message';
            userDiv.innerText = text || "फोटो भेजी गई";
            chatBox.appendChild(userDiv);
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            const payload = { message: text, image: selectedImageBase64, mime_type: selectedMimeType };
            selectedImageBase64 = null;
            selectedMimeType = null;
            document.getElementById('imageInput').value = '';

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await response.json();
                const botDiv = document.createElement('div');
                botDiv.className = 'message bot-message';
                botDiv.innerText = data.reply;
                chatBox.appendChild(botDiv);
                chatBox.scrollTop = chatBox.scrollHeight;
            } catch (err) {
                const errDiv = document.createElement('div');
                errDiv.className = 'message bot-message';
                errDiv.innerText = "कनेक्शन एरर आ गई है।";
                chatBox.appendChild(errDiv);
            }
        }
    </script>
</body>
</html>"""

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode('utf-8'))

    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            user_message = data.get('message', '')
            image_base64 = data.get('image', None)
            mime_type = data.get('mime_type', 'image/jpeg')

            try:
                # सीधे Google AI Studio की ऑफिशियल REST API का उपयोग (Gemini 1.5 Flash Direct URL)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
                
                parts = []
                if user_message:
                    parts.append({"text": user_message})
                if image_base64:
                    parts.append({
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": image_base64
                        }
                    })
                if not parts:
                    parts.append({"text": "Hello"})

                req_body = {"contents": [{"parts": parts}]}
                req_data = json.dumps(req_body).encode('utf-8')

                req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'}, method='POST')
                
                with urllib.request.urlopen(req) as response:
                    res_json = json.loads(response.read().decode('utf-8'))
                    reply_text = res_json['candidates'][0]['content']['parts'][0]['text']
            except Exception as e:
                reply_text = f"एरर आ गई: {str(e)}"

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"reply": reply_text}).encode('utf-8'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), RequestHandler)
    print(f"Server running on port {port}...")
    server.serve_forever()
                
