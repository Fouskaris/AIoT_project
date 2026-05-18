import os
import pandas as pd
import pymongo
import yaml
from datetime import datetime

# 1. Φόρτωση του config.yml
config_path = os.path.join(os.getcwd(), "config.yml")
with open(config_path, 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

# 2. Σύνδεση στη Βάση
client = pymongo.MongoClient(config["client"])
db = client[config["db"]]
col = db[config["col"]]

# 3. Ορισμός μονοπατιού (κοιτάμε πλέον απευθείας τον φάκελο merged)
data_path = os.path.join(os.getcwd(), "merged")

# 4. Βρίσκουμε μόνο τα αρχεία που τελειώνουν σε _MERGED.csv
merged_files = [f for f in os.listdir(data_path) if f.endswith("_MERGED.csv")]

if not merged_files:
    print(f"Δεν βρέθηκαν αρχεία _MERGED.csv στον φάκελο {data_path}!")

for file_name in merged_files:
    print(f"Ανέβασμα του αρχείου: {file_name}")
    
    # Διαβάζουμε το CSV
    df = pd.read_csv(os.path.join(data_path, file_name))
    
    # --- ΕΞΥΠΝΗ ΕΞΑΓΩΓΗ ΟΝΟΜΑΤΟΣ ΚΑΙ ΚΙΝΗΣΗΣ ---
    # Παράδειγμα: "scroll down alexis _MetaWear_..." -> "scroll down alexis"
    prefix = file_name.split('_MetaWear')[0].strip().lower()
    
    # Χωρίζουμε τις λέξεις (π.χ. ['scroll', 'down', 'alexis'])
    words = prefix.split(' ')
    user_name = words[-1] # Η τελευταία λέξη είναι ο χρήστης (π.χ. alexis)
    gesture_name = " ".join(words[:-1]) # Οι προηγούμενες λέξεις είναι η κίνηση (π.χ. scroll down)
    
    # Φτιάχνουμε το έγγραφο (Document) για τη MongoDB
    document = {
        "data": {
            "acc_x": df["x-axis (g)"].tolist(),
            "acc_y": df["y-axis (g)"].tolist(),
            "acc_z": df["z-axis (g)"].tolist(),
            "gyr_x": df["x-axis (deg/s)"].tolist(),
            "gyr_y": df["y-axis (deg/s)"].tolist(),
            "gyr_z": df["z-axis (deg/s)"].tolist()
        },
        "gesture_id": gesture_name,  # π.χ. "scroll down"
        "user": user_name,           # π.χ. "mitsos"
        "sampling_rate": 100,
        "sensor": "AccGyr",
        "datetime": datetime.now()
    }
    
    # Αποθήκευση στη Βάση
    col.insert_one(document)

print("\nΌλα τα αρχεία ανέβηκαν επιτυχώς στη MongoDB!")