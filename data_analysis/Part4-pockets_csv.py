#HER ŞEYİ CSV'YE YAZDIRMA #HER ŞEYİ CSV'YE YAZDIRMA #HER ŞEYİ CSV'YE YAZDIRMA #HER ŞEYİ CSV'YE YAZDIRMA 

import os
import glob
import csv
import pandas as pd
import seaborn as sns
import scipy.cluster.hierarchy as sch
import matplotlib.pyplot as plt
import numpy as np

from scipy.spatial.distance import cdist
from config import processed_dir, xtc_file, pdb_dir, p2rank_processed_dir
from config import pdb_list

# Open CSV file for writing
csv_filename = os.path.join(processed_dir, "pockets.csv")
with open(csv_filename, "w", newline="") as csvfile:
    csvwriter = csv.writer(csvfile)

    # Write header
    csvwriter.writerow(["File name",'Frame', "pocket_index", "probability","residues"])

    for pdb_file in pdb_list:
        predictions_file = os.path.join(processed_dir, 'p2rank_output', os.path.basename(pdb_file).replace('.pdb', '.pdb_predictions.csv'))
        residues_file = os.path.join(processed_dir, 'p2rank_output', os.path.basename(pdb_file).replace('.pdb', '.pdb_residues.csv'))
        print(predictions_file,residues_file)
        # Check if predictions_file exists
        if not os.path.exists(predictions_file):
            continue

        # Open predictions CSV file
        with open(predictions_file, 'r') as pred_file:
            reader = csv.DictReader(pred_file)
            for row in reader:
                # Check if probability is higher than 0.5
                print(row)
                if float(row[' probability']) > 0.5:
                    pocket_index = row['  rank']  # Pocket index
                    full_name = os.path.basename(pdb_file)[:-4]  # Get the PDB file name as the Frame attribute
                    prot_name = os.path.basename(xtc_file)[:-4]
                    frame_name = full_name.replace(prot_name,"")
                    frame_name = frame_name[1:]
                    probability = row[' probability']
                    residues = row[' residue_ids']
                    #print("PROTLANBU",prot_name,full_name,frame_name)
                    # Write data to the CSV file
                    csvwriter.writerow([full_name,frame_name, pocket_index, probability,residues])
print(predictions_file)


# Sort the CSV file by frame_name as integers
with open(csv_filename, 'r') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    sorted_rows = sorted(csv_reader, key=lambda x: int(x['Frame']))

# Rewrite the CSV file with sorted rows
with open(csv_filename, 'w', newline='') as csvfile:
    fieldnames = ["File name",'Frame', 'pocket_index', 'probability', 'residues']
    csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    csv_writer.writeheader()
    for row in sorted_rows:
        csv_writer.writerow(row)

print("CSV file sorted and saved.")

