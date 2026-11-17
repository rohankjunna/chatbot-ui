import sqlite3

conn = sqlite3.connect("chatbot.db")
cursor = conn.cursor()

faqs = [
    ("Fees", "Fees start from ₹2000/month.", "fees,price"),
    ("Demo", "We provide a demo class.", "demo,class"),
    ("Subjects", "Maths, Science, English.", "subjects,course")
]

cursor.executemany("""
INSERT INTO faqs (question, answer, keywords)
VALUES (?, ?, ?)
""", faqs)

conn.commit()
print("FAQs added!")