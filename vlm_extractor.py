import os
import re
import sqlite3
try:
    import google.generativeai as genai
except ImportError:
    genai = None

from PIL import Image

CACHE_DB = 'vlm_cache.db'

# Try configuring gemini
api_key = os.environ.get("GEMINI_API_KEY")
if api_key and genai:
    genai.configure(api_key=api_key)

def _init_db():
    with sqlite3.connect(CACHE_DB) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS vlm_results (
                image_id TEXT PRIMARY KEY,
                extracted_amount REAL
            )
        ''')
        conn.commit()

_init_db()

def _call_gemini_vision(img_path):
    if not api_key:
        return None
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        img = Image.open(img_path)
        prompt = "Extract the financial amount from this image. Return ONLY the number."
        response = model.generate_content([prompt, img])
        text = response.text
        # extract number
        match = re.search(r'[\d\.]+', text.replace(',', ''))
        if match:
            return float(match.group())
    except:
        pass
    return None

def extract_amount_from_image(img_path: str, image_id: str):
    if not os.path.exists(img_path):
        return None

    with sqlite3.connect(CACHE_DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT extracted_amount FROM vlm_results WHERE image_id = ?", (image_id,))
        row = cursor.fetchone()
        if row:
            return row[0]
            
    amt = _call_gemini_vision(img_path)
        
    if amt is not None:
        with sqlite3.connect(CACHE_DB) as conn:
            conn.execute("INSERT OR REPLACE INTO vlm_results (image_id, extracted_amount) VALUES (?, ?)", (image_id, amt))
            conn.commit()
            
    return amt
