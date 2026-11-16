from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import urllib.request, urllib.parse, json, re, html
import os

MY_UPI_ID = "yourname@upi"
MY_NAME = "Al Krishna Vinod"

HTML_PAGE = """<!DOCTYPE html><html lang="hi"><head><meta charset="UTF-8"><meta
name="viewport" content="width=device-width, initial-scale=1.0"><title>AI कृष्णा विनोद</title>
<style><meta name="google-site-verification" content="ma99Naev2NSEDe9rkOn1opjaRBKTxncemFEchmPa6hY" />
body{font-family:Arial, sans-serif;background:#f8f9fa;color:#202124;text-align:center;padding:15px;margin:0}
body.dark{background:#121212; color:#e8eaed}
.top-bar{display:flex;justify-content:space-between;max-width:800px;margin:0 auto 10px}
.mode-btn{padding:8px 15px;border-radius:20px;border:1px solid #ccc;background:transparent;color:inherit;cursor:pointer}
.sub-btn{padding:8px 18px;border-radius:20px;border:none;background:#cc0000;color:#fff;font-weight:bold;cursor:pointer}
.logo{font-size:32px;font-weight:bold; color:#1a73e8;margin:15px 0}.logo span{color:#ea4335}
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
.hindi-note{font-size:13px;color:#5f6368;margin-top:10px}
.tv-frame{border:6px solid #202124;border-radius:16px;background:#000;overflow:hidden;margin-top:12px}
.video-container{position:relative;padding-bottom:56.25%;height:0;overflow:hidden}
.video-container iframe{position:absolute;top:0;left:0;width:100%;height:100%;border:0}
.yt-open-btn{display:inline-block;margin-top:10px;padding:8px 16px;background:#cc0000;color:#fff;text-decoration:none;border-radius:20px;font-size:13px;font-weight:bold}
.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6); justify-content:center;align-items:center;z-index:1000}
.modal-content{background:#fff;color:#202124;padding:25px;border-radius:18px;max-width:350px;width:90%;text-align:center}
body.dark .modal-content{background:#202124;color:#fff}
.amt-btn{padding:10px 16px; margin:5px;border:1px solid #1a73e8;background:#e8f0fe;color:#1a73e8;border-radius:10px;font-weight:bold;cursor:pointer}
.pay-now-btn{display:block;width:100%;margin-top:15px;padding:12px 0;background:#1e8e3e;color:#fff;text-decoration:none;border-radius:25px;font-weight:bold}
.close-btn{margin-top:12px;background:transparent;border:none;color:#5f6368;cursor:pointer}
</style></head><body>
<div class="top-bar"><button class="sub-btn" onclick="openPayModal()">Subscribe / Support</button><button class="mode-btn" onclick="toggleDark()">डार्क मोड</button></div>
<div class="logo"><span>AI</span> कृष्णा विनोद</div>
<form id="searchForm" method="GET" action="/"><div class="search-container"><input type="text" id="searchInput" name="q" placeholder="English या हिंदी में कुछ भी लिखें..." value="__QUERY__" required><button type="button" class="mic-btn" onclick="startVoice()"></button></div><button type="submit" class="search-btn">खोजें (Search)</button></form>
__HINDI_TAG__
__RESULT__
<div id="payModal" class="modal"><div class="modal-content"><h3>AI कृष्णा विनोद को सपोर्ट करें</h3><p style="font-size:14px;">यह वेबसाइट सबके लिए फ्री है। आप अपनी मर्जी से सहयोग राशि भेज सकते हैं:</p>
<div><button class="amt-btn" onclick="setAmount(10)">₹10</button><button class="amt-btn" onclick="setAmount(50)">₹50</button><button class="amt-btn" onclick="setAmount(100)">₹100</button></div>
<p style="font-size:13px;margin-top:12px;">UPI ID: <b>__RAW_UPI_ID__</b></p>
<a id="upiLink" href="upi://pay?pa=_UPI_ID_&pn=_UPI_NAME_&am=50&cu=INR" class="pay-now-btn">UPI ऐप से ₹50 भेजें</a>
<button class="close-btn" onclick="closePayModal()">अभी नहीं (फ्री में चलाएं)</button></div></div>
<script>
function openPayModal(){document.getElementById("payModal").style.display="flex"}
function closePayModal(){document.getElementById("payModal").style.display="none"}
function setAmount(a){const l=document.getElementById("upiLink");l.href="upi://pay?pa=_UPI_ID_&pn=_UPI_NAME_&am="+a+"&cu=INR";l.innerText="UPI ऐप से ₹"+a+" भेजें"}
function toggleDark(){document.body.classList.toggle("dark")}
function startVoice(){const S=window.SpeechRecognition||window.webkitSpeechRecognition;if(!S){alert("वॉइस सर्च सपोर्ट नहीं है।");return}const r=new S();r.lang="hi-IN";r.start();r.onresult=function(e){document.getElementById("searchInput").value=e.results[0].transcript;document.getElementById("searchForm").submit()}}
function speakAnswer(){window.speechSynthesis.cancel();const n=document.getElementById("exactNameBox")?document.getElementById("exactNameBox").innerText+"|":"";const d=document.getElementById("answerText")?document.getElementById("answerText").innerText:"";const s=new SpeechSynthesisUtterance(n+d);s.lang="hi-IN";window.speechSynthesis.speak(s)}
</script></body></html>"""

def make_url(host, path, q=None):
    return "https://" + host + path + (("?" + urllib.parse.urlencode(q)) if q else "")

def translate_text(text, tl="hi"):
    if not text:
        return text
    try:
        u = make_url("translate.googleapis.com", "/translate_a/single", {"client": "gtx", "sl": "auto", "tl": tl, "dt": "t", "q": text[:1000]})
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode("utf-8"))
            out = "".join(str(i[0]) for i in data[0] if i and i[0])
            if out.strip() and out.strip().lower() != text.strip().lower():
                return out.strip()
    except Exception:
        pass
    try:
        lp = "en|hi" if tl == "hi" else "hi|en"
        u = make_url("api.mymemory.translated.net", "/get", {"q": text[:480], "langpair": lp})
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            t = json.loads(res.read().decode("utf-8")).get("responseData", {}).get("translatedText", "")
            if t and "MYMEMORY" not in t:
                return t.strip()
    except Exception:
        pass
    return text
def hinglish_to_hindi(text):
    if re.search(r"[\u0900-\u097F]", text):
        return text
    try:
        u = make_url("inputtools.google.com", "/request", {"text": text, "itc": "hi-t-i0-und", "num": "1"})
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as res:
            d = json.loads(res.read().decode("utf-8"))
            if d and d[0] == "SUCCESS":
                j = "".join(t for t in d[1][0][1] if t).strip()
                if j and j != text:
                    return j
    except Exception:
        pass
    return translate_text(text, "hi")

def get_youtube_video_id(query):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36", "Cookie": "CONSENT=YES+cb.20230531-07-p0.en+FX+410"}
    en_q = translate_text(query, "en")
    for q in ([query, en_q] if en_q.lower() != query.lower() else [query]):
        try:
            u = make_url("www.youtube.com", "/results", {"search_query": q})
            req = urllib.request.Request(u, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as res:
                ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', res.read().decode("utf-8", errors="ignore"))
                if ids:
                    return ids[0]
        except Exception:
            pass
    return None

def fetch_wiki(lang, title):
    try:
        u = make_url(lang + ".wikipedia.org", "/api/rest_v1/page/summary/" + urllib.parse.quote(title))
        req = urllib.request.Request(u, headers={"User-Agent": "AlKrishnaVinod/1.0"})
        with urllib.request.urlopen(req, timeout=5) as res:
            d = json.loads(res.read().decode("utf-8"))
            ext = d.get("extract", "")
            if ext and len(ext) > 25:
                return (d.get("title", title), ext) if lang == "hi" else (translate_text(d.get("title", title), "hi"), translate_text(ext, "hi"))
    except Exception:
        pass
    return None, None

def get_answer(hq, oq):
    qc = re.sub(r"[?!\.,]", "", (hq + " " + oq).lower()).strip()
    if ("राष्ट्रपति" in qc or "president" in qc) and ("भारत" in qc or "india" in qc):
        if "उपराष्ट्रपति" in qc or "vice" in qc:
            _, ext = fetch_wiki("hi", "जगदीप धनखड़")
            return "जगदीप धनखड़ (भारत के उपराष्ट्रपति)", (ext or "जगदीप धनखड़ भारत के वर्तमान उपराष्ट्रपति हैं।")
        _, ext = fetch_wiki("hi", "द्रौपदी मुर्मू")
        return "द्रौपदी मुर्मू (भारत की वर्तमान राष्ट्रपति)", (ext or "द्रौपदी मुर्मू 25 जुलाई 2022 से भारत की 15वीं और वर्तमान राष्ट्रपति हैं।")
    if ("प्रधानमंत्री" in qc or "prime minister" in qc or re.search(r"\bpm\b", qc)) and ("भारत" in qc or "india" in qc):
        _, ext = fetch_wiki("hi", "नरेन्द्र मोदी")
        return "नरेन्द्र मोदी (भारत के वर्तमान प्रधानमंत्री)", (ext or "नरेन्द्र मोदी भारत के वर्तमान प्रधानमंत्री हैं।")
    if "मुख्यमंत्री" in qc or "chief minister" in qc or re.search(r"\bcm\b", qc):
        if "उत्तर प्रदेश" in qc or "uttar pradesh" in qc or "up" in qc.split():
            _, ext = fetch_wiki("hi", "योगी आदित्यनाथ")
            return "योगी आदित्यनाथ (उत्तर प्रदेश के मुख्यमंत्री)", (ext or "योगी आदित्यनाथ उत्तर प्रदेश के वर्तमान मुख्यमंत्री हैं।")
        if "बिहार" in qc or "bihar" in qc:
            _, ext = fetch_wiki("hi", "नीतीश कुमार")
            return "नीतीश कुमार (बिहार के मुख्यमंत्री)", (ext or "नीतीश कुमार बिहार के वर्तमान मुख्यमंत्री हैं।")
    for lang, q_search in [("hi", hq), ("en", re.sub(r"\b(who is what is kaun hai kya hai current)\b", "", translate_text(oq, "en"), flags=re.I).strip())]:
        try:
            u = make_url(lang + ".wikipedia.org", "/w/api.php", {"action": "query", "list": "search", "srsearch": q_search, "format": "json"})
            req = urllib.request.Request(u, headers={"User-Agent": "AlKrishnaVinod/1.0"})
            with urllib.request.urlopen(req, timeout=5) as res:
                for it in json.loads(res.read().decode("utf-8")).get("query", {}).get("search", [])[:2]:
                    ft = it.get("title", "")
                    if not any(b in ft.replace("\u093c", "").lower() for b in ["फखरुद्दीन", "fakhruddin", "सूची", "list of"]):
                        t, ext = fetch_wiki(lang, ft)
                        if t and ext:
                            return t, ext
        except Exception:
            pass
    return None, None

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            p = urllib.parse.urlparse(self.path)
            if p.path == "/favicon.ico":
                self.send_response(204)
                self.end_headers()
                return
            q = dict(urllib.parse.parse_qsl(p.query)).get("q", "").strip()
            res_html, h_tag = "", ""
            if q:
                hq = hinglish_to_hindi(q)
                if hq != q:
                    h_tag = '<div class="hindi-note">हिंदी में खोजा गया: <b>' + html.escape(hq) + '</b></div>'
                t, ans = get_answer(hq, q)
                if ans:
                    res_html += '<div class="result-box"><div class="ai-tag"><span>AI कृष्णा विनोद सटीक जवाब (हिंदी)</span><button class="speak-btn" onclick="speakAnswer()">सुनें</button></div><div id="exactNameBox" class="direct-ans">' + html.escape(t) + '</div><div id="answerText">' + html.escape(ans) + '</div></div>'
                vid = get_youtube_video_id(q) or (get_youtube_video_id(hq) if hq != q else None)
                e_url = make_url("www.youtube-nocookie.com", "/embed/" + vid) if vid else make_url("www.youtube-nocookie.com", "/embed", {"listType": "search", "list": q})
                yt_link = make_url("www.youtube.com", "/results", {"search_query": q})
                res_html += '<div class="result-box"><div class="ai-tag"><span>AI टीवी - YouTube वीडियो</span></div><div class="tv-frame"><div class="video-container"><iframe src="' + html.escape(e_url) + '" allow="autoplay; encrypted-media; fullscreen" allowfullscreen></iframe></div></div><div style="text-align:center;"><a href="' + html.escape(yt_link) + '" target="_blank" class="yt-open-btn">YouTube ऐप में सभी वीडियो देखें</a></div></div>'
            page = HTML_PAGE.replace("__QUERY__", html.escape(q)).replace("__HINDI_TAG__", h_tag).replace("__RESULT__", res_html)
            page = page.replace("__RAW_UPI_ID__", html.escape(MY_UPI_ID)).replace("__UPI_ID__", urllib.parse.quote(MY_UPI_ID)).replace("__UPI_NAME__", urllib.parse.quote(MY_NAME))
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(page.encode("utf-8"))
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8085))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Server running on port {port}")
    server.serve_forever()
    
