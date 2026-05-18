from flask import Flask, render_template, request, jsonify
import sqlite3
import psycopg2
import math
from datetime import datetime
import re
import os

app = Flask(__name__)
DB_NAME = "database.db"

# Render ortamındaki PostgreSQL URL'ini alır. 
# Bilgisayarındaysan URL olmadığı için SQLite kullanmaya devam eder.
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    if DATABASE_URL:
        # Render PostgreSQL bağlantısı
        conn = psycopg2.connect(DATABASE_URL)
        return conn, 'postgres'
    else:
        # Yerel SQLite bağlantısı
        conn = sqlite3.connect(DB_NAME)
        return conn, 'sqlite'

# --- VERİTABANI KURULUMU ---
def init_db():
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    if db_type == 'postgres':
        # PostgreSQL için tablo oluşturma (SERIAL kullanılır)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS participants (
                id SERIAL PRIMARY KEY,
                name TEXT,
                birthday TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT
            )
        ''')
    else:
        # SQLite için tablo oluşturma (AUTOINCREMENT kullanılır)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                birthday TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT
            )
        ''')
        
    conn.commit()
    conn.close()

init_db()

# --- MATEMATİKSEL HESAPLAMALAR ---
def calculate_theoretical_prob(n):
    if n > 365:
        return 100.0
    prob_no_collision = 1.0
    for i in range(n):
        prob_no_collision *= (365 - i) / 365
    return (1 - prob_no_collision) * 100

# --- API ENDPOINTLERİ ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    # Toplam Katılımcı
    cursor.execute('SELECT COUNT(*) FROM participants')
    total_participants = cursor.fetchone()[0]
    
    # Olasılık Hesabı
    theoretical_prob = calculate_theoretical_prob(total_participants)
    
    # Çakışmaları Bulma (Veri tabanı lehçesine göre farklı SQL)
    if db_type == 'postgres':
        cursor.execute('''
            SELECT birthday, STRING_AGG(name, ', ') as names, COUNT(*) as count 
            FROM participants 
            GROUP BY birthday 
            HAVING COUNT(*) > 1 
            ORDER BY count DESC, birthday ASC
        ''')
    else:
        cursor.execute('''
            SELECT birthday, GROUP_CONCAT(name, ', ') as names, COUNT(*) as count 
            FROM participants 
            GROUP BY birthday 
            HAVING count > 1 
            ORDER BY count DESC, birthday ASC
        ''')
        
    collisions = cursor.fetchall()
    
    # Toplam Gerçek Eşleşme Sayısı
    total_collisions = sum([row[2] for row in collisions])
    
    # En Popüler Gün
    most_popular = collisions[0][0] if collisions else "-"
    
    # Tüm Günlerin Dağılımı
    cursor.execute('SELECT birthday, COUNT(*) FROM participants GROUP BY birthday')
    distribution = cursor.fetchall()

    conn.close()
    
    return jsonify({
        "total_participants": total_participants,
        "theoretical_prob": round(theoretical_prob, 2),
        "total_collisions": total_collisions,
        "most_popular": most_popular,
        "collisions": [{"date": c[0], "names": c[1], "count": c[2]} for c in collisions],
        "distribution": {d[0]: d[1] for d in distribution}
    })

@app.route('/api/participants', methods=['POST'])
def add_participant():
    data = request.json
    name = data.get('name', 'Anonim').strip()[:50] 
    birthday = data.get('birthday')
    ip_address = request.remote_addr

    # Form Validasyonu
    if not birthday or not re.match(r'^\d{4}-\d{2}-\d{2}$', birthday):
        return jsonify({"error": "Geçersiz tarih formatı."}), 400
    
    if name == "":
        name = "Anonim"

    # Sadece Gün ve Ay kısmını alıyoruz
    date_obj = datetime.strptime(birthday, '%Y-%m-%d')
    bday_formatted = date_obj.strftime('%d-%m')

    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    # Rate Limiting & Anti-Spam (Sunum için limit 500 yapıldı!)
    if db_type == 'postgres':
        cursor.execute('''
            SELECT COUNT(*) FROM participants 
            WHERE ip_address = %s AND created_at >= NOW() - INTERVAL '1 hour'
        ''', (ip_address,))
    else:
        cursor.execute('''
            SELECT COUNT(*) FROM participants 
            WHERE ip_address = ? AND created_at >= datetime('now', '-1 hour')
        ''', (ip_address,))
        
    if cursor.fetchone()[0] >= 500:
        conn.close()
        return jsonify({"error": "Çok fazla istek gönderdiniz. Lütfen bekleyin."}), 429

    # Veritabanına Güvenli Kayıt
    try:
        if db_type == 'postgres':
            cursor.execute('''
                INSERT INTO participants (name, birthday, ip_address) 
                VALUES (%s, %s, %s)
            ''', (name, bday_formatted, ip_address))
        else:
            cursor.execute('''
                INSERT INTO participants (name, birthday, ip_address) 
                VALUES (?, ?, ?)
            ''', (name, bday_formatted, ip_address))
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({"error": "Sunucu hatası oluştu."}), 500
        
    conn.close()
    return jsonify({"success": True, "message": "Doğum günü başarıyla eklendi!"}), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000 , ssl_context='adhoc')