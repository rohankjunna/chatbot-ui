import pandas as pd

data = {
    "fees": [
        "fees", "price", "cost", "charges", "monthly fees",
        "tuition fees", "fee structure", "how much fees"
    ],
    "demo": [
        "demo", "trial", "trial class", "sample class",
        "free demo", "demo available"
    ],
    "subjects": [
        "subjects", "courses", "topics", "what subjects",
        "what do you teach"
    ]
}

responses = {
    "fees": "Fees start from ₹2000/month",
    "demo": "We provide demo classes",
    "subjects": "Maths Science English available"
}

rows = []

for intent, patterns in data.items():
    for p in patterns:
        rows.append([intent, p, responses[intent]])

df = pd.DataFrame(rows, columns=["intent", "pattern", "response"])
df.to_csv("dataset_new.csv", index=False)

print("✅ New dataset created!")