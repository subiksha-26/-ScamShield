from flask import Flask, render_template, request, jsonify
from markupsafe import escape
from collections import Counter, deque
import re, time, threading

app = Flask(__name__)
LOCK = threading.Lock()
# Demo baseline so the dashboard is not empty; real scans add on top live.
LEVELS = Counter({"Low": 14, "Uncertain": 7, "High": 11})
FLAGS = Counter({"registration fee": 9, "whatsapp": 8, "telegram": 6, "pay now": 5, "aadhaar": 4})
FEED = deque(maxlen=8)

RED_FLAGS = {
    "registration fee": "Requests an upfront registration fee",
    "pay now": "Creates pressure to pay immediately",
    "security deposit": "Requests a security deposit",
    "processing fee": "Requests a processing fee",
    "telegram": "Uses Telegram for recruitment communication",
    "whatsapp": "Uses WhatsApp for recruitment communication",
    "guaranteed job": "Promises a guaranteed job",
    "no interview": "Claims a job without an interview",
    "urgent": "Uses urgency to pressure the applicant",
    "upi": "Mentions UPI payment",
    "bank details": "Requests bank details",
    "aadhaar": "Mentions sensitive identity information",
    "pan card": "Mentions sensitive identity information",
    "fees katt": "Tanglish: asks you to pay a fee (fees kattunga)",
    "panam anup": "Tanglish: asks you to send money (panam anuppunga)",
    "udane join": "Tanglish: pushes you to join immediately",
}
TYPES = [("Registration fee scam", ("fee", "deposit", "pay now", "upi", "panam", "fees")),
         ("Document harvesting", ("aadhaar", "pan card", "bank details")),
         ("Fake chat recruitment", ("telegram", "whatsapp", "guaranteed", "no interview"))]

def scan_offer(text):
    low = text.lower()
    hits = [p for p in RED_FLAGS if p in low]
    score = min(95, len(hits) * 18)
    level = "High" if score >= 54 else "Uncertain" if score >= 18 else "Low"
    advice = {"High": "Do not pay or share sensitive information. Verify the company on its official website and contact details.",
              "Uncertain": "Pause and independently verify the recruiter, company email domain, job listing and interview process.",
              "Low": "No red-flag phrases found by this basic check. That does not prove the offer is genuine; verify independently."}[level]
    stype = next((n for n, keys in TYPES if any(k in p for p in hits for k in keys)), "None detected")
    html = str(escape(text))
    for p in hits:
        html = re.sub("(%s)" % re.escape(p), r"<mark>\1</mark>", html, flags=re.I)
    reasons = [RED_FLAGS[p] for p in hits]
    complaint = ("To,\nThe Cyber Crime Cell / National Cyber Crime Reporting Portal (cybercrime.gov.in)\n\n"
        "Subject: Complaint about a suspected fake job/internship offer (%s)\n\n"
        "Respectfully,\nI, [Your name], [Your phone/email], received the following job offer message on [date] via [WhatsApp/Telegram/email/other] from [sender number/email/company name].\n\n"
        "Message received:\n\"%s\"\n\nWarning signs noticed:\n- %s\n\n"
        "[I did / did not] pay money. Amount: [Rs. ___], Transaction ID: [___], Date: [___].\n"
        "I request you to investigate and take action. Screenshots are attached.\n\nThank you.\n[Your name]\n\n"
        "(For urgent financial fraud, also call the 1930 helpline immediately.)") % (stype, text.strip()[:400], "\n- ".join(reasons))
    with LOCK:
        LEVELS[level] += 1
        FLAGS.update(hits)
        FEED.appendleft({"level": level, "score": score, "type": stype, "t": time.strftime("%H:%M:%S")})
    return {"score": score, "level": level, "type": stype, "advice": advice, "highlighted": html, "complaint": complaint,
            "reasons": [RED_FLAGS[p] for p in hits] or ["No matching red-flag phrases found"]}

FREE = ("gmail.com", "yahoo.com", "outlook.com", "hotmail.com")

def check_resume(text):
    low, flags, qs = text.lower(), [], []
    emails = re.findall(r"[\w.+-]+@([\w-]+\.[\w.]+)", low)
    if not emails:
        flags.append("No email address found"); qs.append("Can you share your official email and LinkedIn profile?")
    if not re.search(r"\+?\d[\d\s-]{8,}", text):
        flags.append("No phone number found"); qs.append("What is the best number to reach you on a video call?")
    rng = [(int(a), 2026 if b in ("present", "current") else int(b))
           for a, b in re.findall(r"((?:19|20)\d{2})\s*(?:-|–|to)\s*((?:19|20)\d{2}|present|current)", low)]
    rng.sort()
    if any(rng[i + 1][0] < rng[i][1] - 0 and rng[i][1] - rng[i + 1][0] >= 1 for i in range(len(rng) - 1)):
        flags.append("Overlapping job/education timelines"); qs.append("Walk me through your timeline: which roles overlapped and why?")
    if any(int(y) > 2026 for y in re.findall(r"\b(20\d{2})\b", low)):
        flags.append("Contains future dates"); qs.append("Can you clarify the dates marked after 2026?")
    yrs = [int(n) for n in re.findall(r"(\d+)\+?\s*years", low)]
    if yrs and max(yrs) >= 8 and re.search(r"fresher|student|b\.?tech|b\.?e\b", low):
        flags.append("Claims 8+ years of experience as a student/fresher"); qs.append("Which project best shows your 8+ years of experience?")
    lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 25]
    if len(lines) != len(set(lines)):
        flags.append("Repeated/copied lines detected"); qs.append("Explain one project in your own words, step by step.")
    if max((l.count(",") for l in text.splitlines()), default=0) > 25:
        flags.append("Keyword-stuffed skills list"); qs.append("Pick three skills and show how you used them.")
    score = min(95, len(flags) * 22)
    level = "High" if score >= 60 else "Needs checks" if score >= 20 else "Looks consistent"
    return {"score": score, "level": level, "flags": flags or ["No inconsistencies found by these basic checks"],
            "questions": qs or ["Describe your most recent project and your exact role in it."]}

GAME = [
    {"m": "Congratulations! You are selected. Pay Rs.999 registration fee on UPI to confirm your joining.", "scam": True, "why": "Real employers never ask candidates to pay a fee to join."},
    {"m": "Hi, we reviewed your application. Interview is on 24 Oct, 11 AM on Google Meet. Invite sent from careers@company.com.", "scam": False, "why": "Specific interview time, official company email and no payment request."},
    {"m": "Work from home, earn Rs.5000/day by liking videos. Join our Telegram group now. No interview!", "scam": True, "why": "Task-based pay, Telegram and 'no interview' are classic scam signs."},
    {"m": "Send your Aadhaar, PAN and bank details today for offer letter processing. Urgent!", "scam": True, "why": "Document harvesting with urgency. Offer letters never need bank details first."},
    {"m": "Your internship offer letter is attached. Please verify the details on our careers portal before accepting.", "scam": False, "why": "Points you to an official portal and asks for no money or documents."},
    {"m": "Vela guaranteed! Udane join pannunga, security deposit Rs.2000 anuppunga.", "scam": True, "why": "Tanglish scam: guaranteed job, urgency and a security deposit."},
]

@app.route("/", methods=["GET", "POST"])
def home():
    text, result = "", None
    if request.method == "POST":
        text = request.form.get("offer_text", "")[:12000]
        if text.strip():
            result = scan_offer(text)
    return render_template("index.html", result=result, offer_text=text)

@app.route("/recruiter", methods=["GET", "POST"])
def recruiter():
    text, result = "", None
    if request.method == "POST":
        text = request.form.get("resume_text", "")[:20000]
        if text.strip():
            result = check_resume(text)
    return render_template("recruiter.html", result=result, resume_text=text)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/api/stats")
def stats():
    with LOCK:
        return jsonify(levels=dict(LEVELS), total=sum(LEVELS.values()),
                       flags=FLAGS.most_common(6), feed=list(FEED))

@app.route("/game")
def game():
    return render_template("game.html", items=GAME)

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True)
