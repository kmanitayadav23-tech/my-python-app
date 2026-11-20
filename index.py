from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import urllib.request, urllib.parse, json, re, html
import os
from functools import lru_cache
import datetime
import sqlite3

MY_UPI_ID = "yourname@upi"
MY_NAME = "AI Krishna Vinod"

@lru_cache(maxsize=128)
def translate_text(text, tl="hi"):
    if not text: return text
    try:
        u = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={tl}&dt=t&q=" + urllib.parse.quote(text)
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as res:
            d = json.loads(res.read().decode("utf-8"))
            if d and d[0]: return "".join(item[0] for item in d[0])
    except Exception: pass
    return text

def hinglish_to_hindi(text):
    if re.search(r"[\u0900-\u097F]", text): return text
    try:
        u = f"https://inputtools.google.com/request?text={urllib.parse.quote(text)}&itc=hi-t-i0-und&num=1"
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as res:
            d = json.loads(res.read().decode("utf-8"))
            if d and d[0] == "SUCCESS":
                j = "".join(t for t in d[1][0][1] if t).strip()
                if j and j != text: return j
    except Exception: pass
    return translate_text(text, "hi")

@lru_cache(maxsize=64)
def fetch_weather(city):
    try:
        en_city = translate_text(city, "en")
        u = f"https://wttr.in/{urllib.parse.quote(en_city)}?format=j1"
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as res:
            data = json.loads(res.read().decode("utf-8"))
            curr = data["current_condition"][0]
            return f"{city} का वर्तमान तापमान {curr['temp_C']}°C है। मौसम: {translate_text(curr['weatherDesc'][0]['value'], 'hi')}।"
    except Exception: pass
    return None

def get_youtube_video_id(query):
    headers = {"User-Agent": "Mozilla/5.0", "Cookie": "CONSENT=YES+cb.20230531-07-p0.en+FX+410"}
    en_q = translate_text(query, "en")
    for q in ([query, en_q] if en_q.lower() != query.lower() else [query]):
        try:
            u = f"https://www.youtube.com/results?search_query={urllib.parse.quote(q)}"
            req = urllib.request.Request(u, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as res:
                ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', res.read().decode("utf-8", errors="ignore"))
                if ids: return ids[0]
        except Exception: pass
    return None
def smart_dynamic_search(hq, oq):
    qc = re.sub(r"[?!\.,]", "", (hq + " " + oq).lower()).strip()
    if any(w in qc for w in ["मौसम", "weather", "temperature", "तापमान", "mausam"]):
        clean_city = re.sub(r"\b(weather|temperature|forecast|report|today|now|ka|ki|ke|in|of|at|tell|me|what|is|the|kaun|kaisa|hai|mausam)\b", "", oq, flags=re.I)
        clean_city = re.sub(r"(मौसम|तापमान|हाल|कैसा|है|का|की|के|में|आज|बताओ|जरा|\?|\.,)", "", clean_city).strip()
        city = clean_city if len(clean_city) >= 2 else "Delhi"
        w_ans = fetch_weather(city)
        if w_ans: return f"लाइव मौसम अपडेट ({city})", w_ans, ""

    # 1. Wikipedia REST Summary API (तस्वीर के साथ डेटा लाने के लिए)
    for query in [oq, hq]:
        for lang in ["hi", "en"]:
            try:
                u = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/" + urllib.parse.quote(query)
                req = urllib.request.Request(u, headers={"User-Agent": "AIKrishnaVinod/1.0"})
                with urllib.request.urlopen(req, timeout=4) as res:
                    d = json.loads(res.read().decode("utf-8"))
                    extract = d.get("extract", "")
                    title = d.get("title", "परिणाम")
                    img_url = ""
                    if "thumbnail" in d and "source" in d["thumbnail"]:
                        img_url = d["thumbnail"]["source"]
                    if extract:
                        if lang == "en":
                            extract = translate_text(extract, "hi")
                            title = translate_text(title, "hi")
                        return title, extract, img_url
            except Exception: pass

    # 2. DuckDuckGo Fallback
    try:
        ddg_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(oq)}&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(ddg_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as res:
            abstract = json.loads(res.read().decode("utf-8")).get("AbstractText", "")
            if abstract: return "वेब सारांश (DuckDuckGo)", translate_text(abstract, "hi"), ""
    except Exception: pass

    if "rashtrapati" in qc or "president" in qc: return "द्रौपदी मुर्मू", "भारत की वर्तमान राष्ट्रपति द्रौपदी मुर्मू हैं।", ""
    elif "pradhanmantri" in qc or "prime minister" in qc: return "नरेंद्र मोदी", "भारत के वर्तमान प्रधानमंत्री नरेंद्र मोदी हैं।", ""
    return "AI कृष्णा विनोद स्मार्ट सर्च", f"'{oq}' के संबंध में इंटरनेट पर अभी विस्तृत डेटा उपलब्ध नहीं है।", ""

def generate_ai_chat_reply(user_msg):
    low = user_msg.lower().strip()
    if any(g in low for g in ["hello", "hi", "namaste", "नमस्ते", "हेलो", "कैसे हो"]):
        return "नमस्ते! मैं AI कृष्णा विनोद हूँ। मैं आपकी क्या सहायता कर सकता हूँ?"
    hq = hinglish_to_hindi(user_msg)
    title, ans, img = smart_dynamic_search(hq, user_msg)
    if ans: return f"📌 {title}:\n\n{ans}"
    return "मुझे इस विषय पर अभी सटीक जानकारी नहीं मिल पाई है।"
HTML_PAGE = """<!DOCTYPE html><html lang="hi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Krishna Vinod - स्मार्ट हिंदी AI सर्च इंजन</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<style>
body{font-family:Arial, sans-serif;background:#f8f9fa;color:#202124;text-align:center;padding:15px;margin:0}
body.dark{background:#121212; color:#e8eaed}
.top-bar{display:flex;justify-content:space-between;max-width:800px;margin:0 auto 10px}
.mode-btn{padding:8px 15px;border-radius:20px;border:1px solid #ccc;background:transparent;color:inherit;cursor:pointer}
.sub-btn{padding:8px 18px;border-radius:20px;border:none;background:#cc0000;color:#fff;font-weight:bold;cursor:pointer}
.logo{font-size:32px;font-weight:bold; color:#1a73e8;margin:15px 0}.logo span{color:#ea4335}
.tab-container{display:flex;justify-content:center;gap:10px;margin:15px 0}
.tab-btn{padding:10px 20px;border-radius:20px;border:1px solid #1a73e8;background:transparent;color:#1a73e8;font-weight:bold;cursor:pointer}
.tab-btn.active{background:#1a73e8;color:#fff}
body.dark .tab-btn{border-color:#8ab4f8;color:#8ab4f8}
body.dark .tab-btn.active{background:#8ab4f8;color:#121212}
.search-container{display:flex;justify-content:center;gap:8px;max-width:550px;margin:0 auto}
input[type="text"]{flex:1;padding:14px 20px; font-size:16px;border:1px solid #dfe1e5;border-radius:25px; outline:none}
body.dark input[type="text"]{background:#202124; color:#fff;border-color:#5f6368}
.mic-btn{padding:12px 15px;font-size:18px; background:#ea4335;color:#fff;border:none;border-radius:50%;cursor:pointer}
.search-btn{margin-top:15px;padding:10px 25px;font-size:16px; background:#1a73e8;color:#fff;border:none;border-radius:20px;cursor:pointer}
.result-box{max-width:650px;margin:20px auto;background:#fff;padding:18px;border-radius:15px;text-align:left;box-shadow:0 2px 10px rgba(0,0,0,0.08); line-height:1.6}
body.dark .result-box{background:#202124}
.ai-tag{color:#1a73e8;font-weight:bold;font-size:14px;margin-bottom:8px;display:flex; justify-content:space-between; align-items:center}
.speak-btn{background:#e8f0fe;color:#1a73e8;border:none; padding:5px 12px;border-radius:15px;cursor:pointer;font-weight:bold}
.direct-ans{background:#e8f0fe; color:#174ea6;padding:12px 15px;border-radius:10px;font-weight:bold; margin-bottom:12px; font-size:19px;border-left:5px solid #1a73e8}
body.dark .direct-ans{background:#1e2a38;color:#8ab4f8}
.wiki-img{float:right;max-width:130px;max-height:130px;border-radius:10px;margin-left:12px;margin-bottom:8px;object-fit:cover;border:1px solid #ddd}
.hindi-note{font-size:13px;color:#5f6368;margin-top:10px}
.tv-frame{border:6px solid #202124;border-radius:16px;background:#000;overflow:hidden;margin-top:12px}
.video-container{position:relative;padding-bottom:56.25%;height:0;overflow:hidden}
.video-container iframe{position:absolute;top:0;left:0;width:100%;height:100%;border:0}
.yt-open-btn{display:inline-block;margin-top:10px;padding:8px 16px;background:#cc0000;color:#fff;text-decoration:none;border-radius:20px;font-size:13px;font-weight:bold}
.chat-box{max-width:650px;margin:25px auto;background:#fff;border-radius:15px;box-shadow:0 2px 12px rgba(0,0,0,0.1);overflow:hidden;text-align:left}
body.dark .chat-box{background:#202124}
.chat-header{background:#1a73e8;color:#fff;padding:12px 18px;font-weight:bold;font-size:16px}
.chat-messages{height:240px;overflow-y:auto;padding:15px;display:flex;flex-direction:column;gap:10px}
.msg-user{align-self:flex-end;background:#1a73e8;color:#fff;padding:10px 14px;border-radius:15px 15px 0 15px;max-width:80%;font-size:14px}
.msg-ai{align-self:flex-start;background:#f1f3f4;color:#202124;padding:10px 14px;border-radius:15px 15px 15px 0;max-width:80%;font-size:14px;line-height:1.5}
body.dark .msg-ai{background:#303134;color:#e8eaed}
.chat-input-area{display:flex;border-top:1px solid #dfe1e5;padding:10px}
body.dark .chat-input-area{border-color:#5f6368}
.chat-input-area input{flex:1;border:none;outline:none;padding:8px 12px;font-size:15px;background:transparent;color:inherit}
.chat-send-btn{background:#1a73e8;color:#fff;border:none;padding:8px 18px;border-radius:20px;font-weight:bold;cursor:pointer}
.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6); justify-content:center;align-items:center;z-index:1000}
.modal-content{background:#fff;color:#202124;padding:25px;border-radius:18px;max-width:350px;width:90%;text-align:center}
body.dark .modal-content{background:#202124;color:#fff}
.amt-btn{padding:10px 16px; margin:5px;border:1px solid #1a73e8;background:#e8f0fe;color:#1a73e8;border-radius:10px;font-weight:bold;cursor:pointer}
.pay-now-btn{display:block;width:100%;margin-top:15px;padding:12px 0;background:#1e8e3e;color:#fff;text-decoration:none;border-radius:25px;font-weight:bold}
.close-btn{margin-top:12px;background:transparent;border:none;color:#5f6368;cursor:pointer}
.popular-box{margin-top:35px;font-size:14px;color:#5f6368}
.popular-box a{color:#1a73e8;margin:0 8px;text-decoration:none;display:inline-block;margin-top:5px}
.tab-content{display:none;}
.tab-content.active{display:block;}
</style></head><body>

<div class="top-bar"><button class="sub-btn" onclick="openPayModal()">Subscribe / Support</button><button class="mode-btn" onclick="toggleDark()">डार्क मोड</button></div>
<div class="logo"><span>AI</span> Krishna Vinod</div>

<div class="tab-container">
  <button class="tab-btn active" onclick="switchTab('searchTab', this)">🔍 सर्च और वीडियो</button>
  <button class="tab-btn" onclick="switchTab('mapTab', this)">📍 लाइव मैप</button>
  <button class="tab-btn" onclick="switchTab('chatTab', this)">💬 AI चैट</button>
</div>

<div id="searchTab" class="tab-content active">
  <form id="searchForm" method="GET" action="/">
    <div class="search-container">
      <input type="text" id="searchInput" name="q" value="__QUERY__" placeholder="English या हिंदी में कुछ भी लिखें..." list="suggestionList" autocomplete="off" required>
      <datalist id="suggestionList">
        <option value="भारत के वर्तमान राष्ट्रपति"><option value="भारत के वर्तमान प्रधानमंत्री"><option value="दिल्ली का मौसम"><option value="वाराणसी का मौसम"><option value="ताजमहल">
      </datalist>
      <button type="button" id="micBtn" class="mic-btn" onclick="startVoice()">🎤</button>
    </div>
    <button type="submit" class="search-btn">खोजें (Search)</button>
  </form>
  __HINDI_TAG__
  __RESULT__
  <div class="popular-box">
    <p><b>लोकप्रिय खोज:</b></p>
    <a href="/?q=Bharat+ke+vartaman+Rashtrapati">• राष्ट्रपति</a>
    <a href="/?q=Bharat+ke+vartaman+Pradhanmantri">• प्रधानमंत्री</a>
    <a href="/?q=Delhi+ka+mausam">• दिल्ली मौसम</a>
  </div>
</div>

<div id="mapTab" class="tab-content">
  <div class="result-box" style="text-align: center;">
    <div class="ai-tag"><span>📍 लाइव मैप और लोकेशन सर्च</span></div>
    <div style="display: flex; gap: 8px; margin-bottom: 12px; flex-wrap: wrap;">
      <input type="text" id="placeInput" placeholder="जगह का नाम लिखें..." style="flex: 1; min-width: 180px; padding: 10px 15px; border: 1px solid #dfe1e5; border-radius: 20px;" />
      <button type="button" onclick="searchLocation()" class="search-btn" style="margin-top: 0;">खोजें</button>
      <button type="button" onclick="myLocation()" class="search-btn" style="margin-top: 0; background: #1e8e3e;">मेरी लोकेशन</button>
    </div>
    <div id="liveMap" style="height: 380px; width: 100%; border-radius: 12px; border: 1px solid #dfe1e5;"></div>
  </div>
</div>

<div id="chatTab" class="tab-content">
  <div class="chat-box">
    <div class="chat-header">💬 AI कृष्णा विनोद चैट</div>
    <div class="chat-messages" id="chatMessages">
      <div class="msg-ai">नमस्ते! मैं AI कृष्णा विनोद हूँ। मुझसे कुछ भी पूछें!</div>
    </div>
    <div class="chat-input-area">
      <input type="text" id="chatInput" placeholder="यहाँ संदेश लिखें..." onkeypress="if(event.key==='Enter') sendChat()">
      <button class="chat-send-btn" onclick="sendChat()">भेजें</button>
    </div>
  </div>
</div>

<div id="payModal" class="modal"><div class="modal-content"><h3>सपोर्ट करें</h3>
<div><button class="amt-btn" onclick="setAmount(10)">₹10</button><button class="amt-btn" onclick="setAmount(50)">₹50</button></div>
<p style="font-size:13px;margin-top:12px;">UPI ID: <b>__RAW_UPI_ID__</b></p>
<a id="upiLink" href="upi://pay?pa=__UPI_ID__&pn=__UPI_NAME__&am=50&cu=INR" class="pay-now-btn">UPI ऐप से भेजें</a>
<button class="close-btn" onclick="closePayModal()">बंद करें</button></div></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
function switchTab(tabId, btn){
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById(tabId).classList.add('active');
  btn.classList.add('active');
  if(tabId === 'mapTab' && window.mapObj) { setTimeout(() => { window.mapObj.invalidateSize(); }, 200); }
}
var map = L.map('liveMap').setView([25.3176, 82.9739], 6);
window.mapObj = map;
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '© OpenStreetMap' }).addTo(map);
var marker;

function myLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(pos) {
      var lat = pos.coords.latitude, lon = pos.coords.longitude;
      map.setView([lat, lon], 15);
      if (marker) map.removeLayer(marker);
      marker = L.marker([lat, lon]).addTo(map).bindPopup("आप यहाँ हैं!").openPopup();
    }, function() { alert("कृपया GPS ऑन करें।"); });
  }
}

function searchLocation() {
  var place = document.getElementById('placeInput').value;
  if (!place) return alert("जगह का नाम लिखें!");
  fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${place}`)
    .then(res => res.json())
    .then(data => {
      if (data.length > 0) {
        map.setView([data[0].lat, data[0].lon], 14);
        if (marker) map.removeLayer(marker);
        marker = L.marker([data[0].lat, data[0].lon]).addTo(map).bindPopup(data[0].display_name).openPopup();
      } else { alert("जगह नहीं मिली।"); }
    });
}

function openPayModal(){document.getElementById("payModal").style.display="flex"}
function closePayModal(){document.getElementById("payModal").style.display="none"}
function setAmount(a){const l=document.getElementById("upiLink");l.href="upi://pay?pa=__UPI_ID__&pn=__UPI_NAME__&am="+a+"&cu=INR";l.innerText="UPI ऐप से ₹"+a+" भेजें"}
function toggleDark(){document.body.classList.toggle("dark")}

function startVoice(){
  const S = window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!S){alert("वॉइस सर्च सपोर्ट नहीं है।");return}
  const btn=document.getElementById("micBtn"),inp=document.getElementById("searchInput"),r=new S();
  r.lang="hi-IN";
  r.onstart=function(){btn.style.background="#1e8e3e";inp.placeholder="सुन रहा हूँ..."};
  r.onend=function(){btn.style.background="#ea4335";inp.placeholder="कुछ भी लिखें..."};
  r.onresult=function(e){inp.value=e.results[0][0].transcript;document.getElementById("searchForm").submit()};
  r.start()
}

function speakAnswer(){
  window.speechSynthesis.cancel();
  const n=document.getElementById("exactNameBox")?document.getElementById("exactNameBox").innerText+"|":"";
  const d=document.getElementById("answerText")?document.getElementById("answerText").innerText:"";
  const s=new SpeechSynthesisUtterance(n+d);s.lang="hi-IN";window.speechSynthesis.speak(s)
}

async function sendChat(){
  const inp = document.getElementById("chatInput");
  const msg = inp.value.trim();
  if(!msg) return;
  const box = document.getElementById("chatMessages");
  box.innerHTML += '<div class="msg-user">' + msg.replace(/</g,"&lt;") + '</div>';
  inp.value = ""; box.scrollTop = box.scrollHeight;
  const waitId = "wait_" + Date.now();
  box.innerHTML += '<div class="msg-ai" id="'+waitId+'">सोच रहा हूँ...</div>';
  box.scrollTop = box.scrollHeight;
  try {
    const res = await fetch("/api/chat?q=" + encodeURIComponent(msg));
    const data = await res.json();
    document.getElementById(waitId).innerText = data.reply;
  } catch(e) { document.getElementById(waitId).innerText = "संपर्क नहीं हो पा रहा है।"; }
  box.scrollTop = box.scrollHeight;
}
</script></body></html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            p = urllib.parse.urlparse(self.path)
            host = self.headers.get("Host", "onrender.com")
            base_url = f"https://{host}"

            if p.path == "/favicon.ico":
                self.send_response(204); self.end_headers(); return
            if p.path == "/robots.txt":
                self.send_response(200); self.send_header("Content-type", "text/plain; charset=utf-8"); self.end_headers()
                self.wfile.write(f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n".encode("utf-8")); return

            if p.path == "/api/chat":
                q = dict(urllib.parse.parse_qsl(p.query)).get("q", "").strip()
                reply = generate_ai_chat_reply(q)
                self.send_response(200); self.send_header("Content-type", "application/json; charset=utf-8"); self.end_headers()
                self.wfile.write(json.dumps({"reply": reply}).encode("utf-8")); return

            q = dict(urllib.parse.parse_qsl(p.query)).get("q", "").strip()
            res_html, h_tag = "", ""
            if q:
                hq = hinglish_to_hindi(q)
                if hq != q: h_tag = '<div class="hindi-note">हिंदी में खोजा गया: <b>' + html.escape(hq) + '</b></div>'
                t, ans, img = smart_dynamic_search(hq, q)
                if ans:
                    img_tag = f'<img src="{html.escape(img)}" class="wiki-img" alt="image">' if img else ''
                    res_html += f'<div class="result-box"><div class="ai-tag"><span>AI कृष्णा विनोद सटीक जवाब</span><button class="speak-btn" onclick="speakAnswer()">सुनें</button></div><div id="exactNameBox" class="direct-ans">{html.escape(t)}</div><div>{img_tag}<span id="answerText">{html.escape(ans)}</span></div><div style="clear:both;"></div></div>'
                
                vid = get_youtube_video_id(q) or (get_youtube_video_id(hq) if hq != q else None)
                e_url = f"https://www.youtube-nocookie.com/embed/{vid}" if vid else f"https://www.youtube-nocookie.com/embed?listType=search&list={urllib.parse.quote(q)}"
                yt_link = f"https://www.youtube.com/results?search_query={urllib.parse.quote(q)}"
                res_html += '<div class="result-box"><div class="ai-tag"><span>AI टीवी - YouTube वीडियो</span></div><div class="tv-frame"><div class="video-container"><iframe src="' + html.escape(e_url) + '" allow="autoplay; encrypted-media; fullscreen" allowfullscreen></iframe></div></div><div style="text-align:center;"><a href="' + html.escape(yt_link) + '" target="_blank" class="yt-open-btn">YouTube ऐप में देखें</a></div></div>'
            
            page = HTML_PAGE.replace("__QUERY__", html.escape(q)).replace("__HINDI_TAG__", h_tag).replace("__RESULT__", res_html)
            page = page.replace("__RAW_UPI_ID__", html.escape(MY_UPI_ID)).replace("__UPI_ID__", urllib.parse.quote(MY_UPI_ID)).replace("__UPI_NAME__", urllib.parse.quote(MY_NAME))
            
            self.send_response(200); self.send_header("Content-type", "text/html; charset=utf-8"); self.end_headers()
            self.wfile.write(page.encode("utf-8"))
        except Exception as e: print("Error:", e)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8085))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Server running on port {port}")
    server.serve_forever()
