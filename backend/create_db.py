import sqlite3

def create_db():
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()

    # =========================
    # FAQ TABLE
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS faqs (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT,
        answer   TEXT,
        keywords TEXT
    )
    """)

    # =========================
    # LEADS TABLE (with name & contact included)
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        name     TEXT,
        contact  TEXT,
        class    TEXT,
        subject  TEXT,
        location TEXT,
        mode     TEXT,
        status   TEXT DEFAULT 'new'
    )
    """)

    # =========================
    # CHAT LOGS TABLE
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_logs (
        id        INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id   TEXT NOT NULL,
        role      TEXT NOT NULL,
        message   TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """)

    # =========================
    # USER PROFILES TABLE
    # =========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profiles (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    TEXT UNIQUE NOT NULL,
        name       TEXT,
        phone      TEXT,
        city       TEXT,
        class      TEXT,
        subject    TEXT,
        mode       TEXT,
        created_at TEXT
    )
    """)

    # =========================
    # Safely add columns if they don't exist (for existing DBs)
    # =========================
    for column, col_type in [("name", "TEXT"), ("contact", "TEXT")]:
        try:
            cursor.execute(f"ALTER TABLE leads ADD COLUMN {column} {col_type}")
            print(f"Column '{column}' added to leads.")
        except sqlite3.OperationalError:
            print(f"Column '{column}' already exists, skipping.")

    # =========================
    # DEFAULT FAQ DATA
    # =========================
    faqs_data = [
        ("Fees",            "💰 Our fees depend on class & subject.\n\nDemo session starts from ₹299.\nMonthly plans available after demo.",                   "fees,price,cost,charge,rate"),
        ("Demo Class",      "🎓 Yes! We provide a paid demo class so you can evaluate the tutor before continuing.\n\nDemo starts from ₹299.",                 "demo,trial,sample,test class"),
        ("Subjects",        "📚 We offer tutoring for:\n- Maths\n- Science\n- English\n- Competitive exams\n\nAvailable from Class 1 to 12.",                  "subjects,course,topic,maths,science,english"),
        ("Timing",          "⏰ Flexible timing available:\n- Morning\n- Evening\n- Weekend\n\nSchedule based on your preference.",                             "time,timing,availability,schedule,slot,morning,evening,weekend"),
        ("Tutor Info",      "👨‍🏫 All our tutors are:\n- Verified & background checked\n- Experienced (2+ years)\n- Matched based on your requirement",         "tutor,teacher,instructor,faculty"),
        ("Home Tuition",    "🏠 Yes! We provide home tutors across your area.\n\nShare your pincode and we'll find the best match.",                           "home tuition,home tutor,offline,at home,doorstep"),
        ("Online Classes",  "💻 We provide 1:1 personalized online tuition.\n\nFlexible timing, verified tutors, live sessions.",                             "online,virtual,video class,zoom,remote"),
        ("Contact",         "📞 You can reach us at:\n- Email: support@vidhyagharse.com\n- WhatsApp: +91 XXXXXXXXXX",                                         "contact,reach,phone,whatsapp,email,call,support,help"),
        ("Refund Policy",   "🔄 If you're not satisfied after the demo class, we offer a full refund within 24 hours. No questions asked.",                    "refund,money back,cancel,cancellation,return"),
        ("Classes Covered", "🏫 We cover Class 1 to 12 for all major boards:\n- CBSE\n- ICSE\n- State Board",                                                 "class,grade,standard,cbse,icse,state board,board"),
    ]

    cursor.execute("SELECT COUNT(*) FROM faqs")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO faqs (question, answer, keywords) VALUES (?, ?, ?)", faqs_data)
        print("Default FAQs inserted!")

    conn.commit()
    conn.close()
    print("Database ready!")

if __name__ == "__main__":
    create_db()