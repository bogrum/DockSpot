import pandas as pd
import os
import subprocess
import glob
import mdtraj as md

from config import processed_dir, xtc_file, pdb_dir, p2rank_processed_dir, topology

def xtc_to_pdb(xtc_file, pdb_dir):
    # Load XTC file
    traj = md.load_xtc(xtc_file, topology)
    for i, frame in enumerate(traj):
        pdb_file = os.path.join(pdb_dir, f"{os.path.splitext(os.path.basename(xtc_file))[0]}_{i}.pdb")
        frame.save_pdb(pdb_file)
        
        print(f"Frame {i} saved as {pdb_file}")

# Convert XTC to PDB
xtc_to_pdb(xtc_file, pdb_dir)

# List of PDB files
pdb_list = glob.glob(os.path.join(pdb_dir, '*.pdb'))

# Write PDB list to a file
with open(os.path.join(processed_dir, 'pdb_list.ds'), 'w') as f:
    for pdb_file in pdb_list:
        f.write(os.path.relpath(pdb_file, start=processed_dir))
        f.write('\n')



subprocess.call(f'~/p2rank_2.3.1/prank predict {os.path.join(processed_dir, "pdb_list.ds")} -o {p2rank_processed_dir} -threads 4', shell=True)

print(p2rank_processed_dir)
