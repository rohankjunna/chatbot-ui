import pandas as pd
import random

# ── Load dataset ───────────────────────
df = pd.read_csv("dataset.csv", on_bad_lines="skip")

df["intent"] = df["intent"].astype(str).str.strip().str.lower()
df["pattern"] = df["pattern"].astype(str).str.strip().str.lower()
df["response"] = df["response"].astype(str).str.strip()

# ── REMOVE BAD DATA ───────────────────
bad_words = ["ok", "yes", "hmm", "1", "fine"]
df = df[~df["pattern"].isin(bad_words)]

# ── MERGE SIMILAR INTENTS 🔥 ──────────
merge_map = {
    "demo_request": "demo",
    "trial_demo": "demo",
    "demo_class": "demo",

    "fees_info": "fees",
    "price_query": "fees",

    "subjects_info": "subjects",
    "course_query": "subjects",

    "teacher": "tutor",
    "faculty": "tutor"
}

df["intent"] = df["intent"].replace(merge_map)

# ── SYNONYMS FOR EXPANSION 🔥 ─────────
SYNONYMS = {
    "fees": ["price", "cost", "charges", "fee structure"],
    "demo": ["trial", "sample class", "demo class"],
    "subjects": ["courses", "topics"],
    "tutor": ["teacher", "faculty"]
}

# ── GENERATE VARIATIONS 🔥 ────────────
new_rows = []

for _, row in df.iterrows():
    intent = row["intent"]
    pattern = row["pattern"]
    response = row["response"]

    new_rows.append([intent, pattern, response])

    # add variations
    for word, syns in SYNONYMS.items():
        if word in pattern:
            for s in syns:
                new_pattern = pattern.replace(word, s)
                new_rows.append([intent, new_pattern, response])

    # add question formats
    new_rows.append([intent, f"what is {pattern}", response])
    new_rows.append([intent, f"tell me {pattern}", response])
    new_rows.append([intent, f"can you explain {pattern}", response])

# ── CREATE NEW DATAFRAME ──────────────
new_df = pd.DataFrame(new_rows, columns=["intent", "pattern", "response"])

# ── REMOVE DUPLICATES ────────────────
new_df = new_df.drop_duplicates()

# ── BALANCE DATASET 🔥 ───────────────
balanced_rows = []

for intent in new_df["intent"].unique():
    subset = new_df[new_df["intent"] == intent]

    # ensure minimum 20 samples
    if len(subset) < 20:
        subset = pd.concat([subset] * (20 // len(subset) + 1))

    balanced_rows.append(subset.sample(20, replace=True))

final_df = pd.concat(balanced_rows)

# ── SAVE ─────────────────────────────
final_df.to_csv("dataset_optimized.csv", index=False)

print("✅ Optimized dataset created!")
print("Total patterns:", len(final_df))
print("Total intents:", final_df['intent'].nunique())