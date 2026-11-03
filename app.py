import os
import json
from flask import Flask, render_template
from datetime import datetime, timezone, timedelta
from google import genai

base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

# Gemini API клиентін баптау (Кілтті Render-дегі Environment Variables-ке саламыз)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))

def generate_daily_content(day_str):
    """Күн сайын жаңа идея мен жаңалықтарды ЖИ арқылы генерациялау"""
    prompt = f"""
    Бүгінгі күн: {day_str}. Сен шағын азық-түлік дүкені иесіне арналған газет редакторысың.
    Төмендегі талаптар бойынша JSON форматында жауап қайтар:
    1. "idea": Азық-түлік дүкенінің саудасын арттыратын бүгінгі күнге арналған тың, нақты бизнес-идея ("title", "desc", "step").
    2. "news": 4 өзекті жаңалық қысқаша ("tag", "title", "desc", "src"):
       - Біріншісі: ЖИ (ИИ) тақырыбында
       - Екіншісі: Бизнес және бөлшек сауда тақырыбында
       - Үшіншісі: Қазақстан тақырыбында
       - Төртіншісі: Әлемдік маңызды жаңалық

    Тек қана таза JSON қайтар, басқа сөз қоспа:
    {{
      "idea": {{
        "title": "...",
        "desc": "...",
        "step": "..."
      }},
      "news": [
        {{"tag": "ИИ", "title": "...", "desc": "...", "src": "..."}},
        {{"tag": "Бизнес", "title": "...", "desc": "...", "src": "..."}},
        {{"tag": "Қазақстан", "title": "...", "desc": "...", "src": "..."}},
        {{"tag": "Әлем", "title": "...", "desc": "...", "src": "..."}}
      ]
    }}
    """
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        # Егер интернет немесе API кілті болмаса, сайт сөнбей жұмыс істеп тұруы үшін
        return {
            "idea": {
                "title": "Сөрелерді оңтайландыру",
                "desc": "Сұранысы жоғары негізгі тауарларды тұтынушының көз деңгейіне қойыңыз.",
                "step": "Дүкенге кіргенде бірінші көрінетін сөрені қайта қарап шығыңыз."
            },
            "news": [
                {"tag": "ЖИ", "title": "Ритейлге арналған жасанды интеллект", "desc": "Сауда нүктелерін автоматтандыру алгоритмдері дамуда.", "src": "Tech News"},
                {"tag": "Бизнес", "title": "Шағын бизнес қолдау шаралары", "desc": "Бөлшек саудада электронды чек талаптары жүруде.", "src": "Zakon.kz"},
                {"tag": "Қазақстан", "title": "Цифрлық төлемдер өсімі", "desc": "QR арқылы сауда жасау үлесі артып келеді.", "src": "Қазақстан жаңалықтары"},
                {"tag": "Әлем", "title": "Нарықтағы соңғы өзгерістер", "desc": "Жаһандық азық-түлік бағасы тұрақталуда.", "src": "Reuters"}
            ]
        }

@app.route("/")
def home():
    weekdays = ["дүйсенбі", "сейсенбі", "сәрсенбі", "бейсенбі", "жұма", "сенбі", "жексенбі"]
    months = ["ҚАҢТАР", "АҚПАН", "НАУРЫЗ", "СӘУІР", "МАМЫР", "МАУСЫМ", 
              "ШІЛДЕ", "ТАМЫЗ", "ҚЫРКҮЙЕК", "ҚАЗАН", "ҚАРАША", "ЖЕЛТОҚСАН"]
    
    # Қызылорда уақыты (UTC+5)
    kz_timezone = timezone(timedelta(hours=5))
    now = datetime.now(kz_timezone)
    
    day_num = now.day
    weekday_str = weekdays[now.weekday()]
    month_str = months[now.month - 1]
    day_full = f"{day_num} {month_str} {now.year}, {weekday_str}"
    
    # ЖИ арқылы бүгінгі күндік контентті автоматты алу
    content = generate_daily_content(day_full)
    
    context = {
        "day": day_num,
        "month": month_str,
        "weekday": weekday_str,
        "city": "Қызылорда",
        "idea": content.get("idea"),
        "news": content.get("news", []),
        "date_key": now.strftime("%Y-%m-%d")
    }
    
    return render_template("index.html", **context)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
