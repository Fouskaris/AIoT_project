import pandas as pd
import os
import glob

# Ορισμός φακέλων
raw_data_path = 'data/'
output_path = 'merged_data/'

if not os.path.exists(output_path):
    os.makedirs(output_path)

# Βρίσκουμε όλα τα αρχεία Accelerometer
acc_files = glob.glob(os.path.join(raw_data_path, "*_Accelerometer_*.csv"))

for acc_file in acc_files:
    # Βρίσκουμε το αντίστοιχο αρχείο Gyroscope αλλάζοντας το όνομα
    gyr_file = acc_file.replace("Accelerometer", "Gyroscope")
    
    if os.path.exists(gyr_file):
        print(f"Merging: {os.path.basename(acc_file)}")
        
        df_acc = pd.read_csv(acc_file)
        df_gyr = pd.read_csv(gyr_file)
        
        # Merge βάσει του epoch (ms) για να είναι συγχρονισμένα
        merged_df = pd.merge_asof(df_acc.sort_values('epoch (ms)'), 
                                 df_gyr.sort_values('epoch (ms)'), 
                                 on='epoch (ms)', 
                                 direction='nearest',
                                 suffixes=('_acc', '_gyr'))
        
        # Δημιουργία νέου ονόματος αρχείου
        new_filename = os.path.basename(acc_file).replace("_Accelerometer_100.000Hz_1.7.3", "_MERGED")
        merged_df.to_csv(os.path.join(output_path, new_filename), index=False)

print("Done! Check the 'merged_data' folder.")