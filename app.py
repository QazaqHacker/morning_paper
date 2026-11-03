import os
import json
from flask import Flask, render_template
from datetime import datetime, timezone, timedelta
from google import genai

base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(__name__, template_folder=template_dir)

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))

def generate_daily_content(day_str):
    prompt = f"""
    Бүгінгі күн: {day_str}. Сен шағын азық-түлік дүкенінің иесіне арналған күнделікті таңғы газет редакторысың.
    Оқырманға көбірек пайдалы мәлімет беру үшін 6 өзекті жаңалық пен 1 бизнес-идея дайында.

    Төмендегі талаптарға сай тек қана таза JSON қайтар:
    1. "idea": Дүкен табысын арттыратын тың, нақты идея ("title", "desc", "step").
    2. "news": 6 жаңалықтан тұратын массив ("tag", "title", "desc", "takeaway", "src"):
       - 1 және 2: ИИ және жаңа технологиялар (ритейлде, бизнесте немесе күнделікті өмірде)
       - 3 және 4: Бизнес, сауда және қаржы
       - 5: Қазақстанның маңызды жаңалығы (заңдар, сауда, экономика)
       - 6: Әлемдік маңызды жаңалық

    Формат:
    {{
      "idea": {{
        "title": "...",
        "desc": "...",
        "step": "..."
      }},
      "news": [
        {{"tag": "ИИ", "title": "...", "desc": "...", "takeaway": "Бұл не береді: ...", "src": "Дереккөз"}},
        {{"tag": "ИИ / Автоматтандыру", "title": "...", "desc": "...", "takeaway": "Нәтиже: ...", "src": "Дереккөз"}},
        {{"tag": "Бизнес", "title": "...", "desc": "...", "takeaway": "Маңыздысы: ...", "src": "Дереккөз"}},
        {{"tag": "Ритейл", "title": "...", "desc": "...", "takeaway": "Пайдасы: ...", "src": "Дереккөз"}},
        {{"tag": "Қазақстан", "title": "...", "desc": "...", "takeaway": "Кәсіпкерге әсері: ...", "src": "Дереккөз"}},
        {{"tag": "Әлем", "title": "...", "desc": "...", "takeaway": "Түйін: ...", "src": "Дереккөз"}}
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
        return {
            "idea": {
                "title": "«Таңғы комбо» касса маңында",
                "desc": "Кофе мен жаңа піскен сэндвичті бірыңғай арзан бағамен таңғы уақытта ұсыну.",
                "step": "Жергілікті наубайханамен күніне 10-15 сэндвич әкелуге келісіңіз."
            },
            "news": [
                {"tag": "ИИ", "title": "Сөредегі тауарды бақылайтын жасанды интеллект", "desc": "Шағын камералар тауардың таусылғанын көріп, сатушыға хабарлайды.", "takeaway": "Сөре бос тұрмайды, сауда 10% артады.", "src": "Tech Review"},
                {"tag": "ИИ", "title": "Тауар бағасын автоматты талдау", "desc": "ИИ бәсекелестердің бағасын салыстырып, ең ұтымды бағаны ұсынады.", "takeaway": "Бағаны қолмен тексеруге уақыт кетпейді.", "src": "AI Market"},
                {"tag": "Бизнес", "title": "Шағын дүкендердегі сұраныстың өзгеруі", "desc": "Тұтынушылар алыс гипермаркеттерден гөрі үй жанындағы дүкендерді жиі таңдауда.", "takeaway": "Дайын тағамдар мен сусындар ассортиментін арттыру ұтымды.", "src": "RetailKZ"},
                {"tag": "Ритейл", "title": "Тікелей жеткізу шығынды азайтты", "desc": "Өнімді делдалсыз тікелей жергілікті шаруалардан алу тренді өсуде.", "takeaway": "Тауар жаңа әрі маржасы жоғары болады.", "src": "Бизнес жаңалықтары"},
                {"tag": "Қазақстан", "title": "Цифрлық төлемдер мен QR чек талаптары", "desc": "Сауда орындарында кассалық түбіртектерді онлайн беру процесі оңтайландырылуда.", "takeaway": "Салықтық есептеу жеңілдейді.", "src": "Zakon.kz"},
                {"tag": "Әлем", "title": "Азық-түлік логистикасының тұрақтануы", "desc": "Жаһандық деңгейде тасымал бағасы түсіп, бағалар қалыпқа келуде.", "takeaway": "Импорттық тауар тапшылығы болмайды.", "src": "Global Trade"}
            ]
        }

@app.route("/")
def home():
    weekdays = ["дүйсенбі", "сейсенбі", "сәрсенбі", "бейсенбі", "жұма", "сенбі", "жексенбі"]
    months = ["ҚАҢТАР", "АҚПАН", "НАУРЫЗ", "СӘУІР", "МАМЫР", "МАУСЫМ", 
              "ШІЛДЕ", "ТАМЫЗ", "ҚЫРКҮЙЕК", "ҚАЗАН", "ҚАРАША", "ЖЕЛТОҚСАН"]
    
    kz_timezone = timezone(timedelta(hours=5))
    now = datetime.now(kz_timezone)
    
    day_num = now.day
    weekday_str = weekdays[now.weekday()]
    month_str = months[now.month - 1]
    day_full = f"{day_num} {month_str} {now.year}, {weekday_str}"
    
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
