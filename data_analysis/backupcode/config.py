import os
import glob

with open("/home/bogrum/project_files/2XIR/inputs/xtc_directory.txt","r") as f:
    xtc_file = f.read().strip()

with open("/home/bogrum/project_files/2XIR/inputs/sdf_directory.txt","r") as g:
    sdf_file = g.read().strip()

with open("/home/bogrum/project_files/2XIR/inputs/pdb_directory.txt","r") as g:
    pdb_files = g.read().strip()

with open("/home/bogrum/project_files/2XIR/inputs/topology_directory.txt","r") as g:
    topology = g.read().strip()

# Save frames as PDB files
project_files_path = "/home/bogrum/project_files/4FOB"

inputs = os.path.join(project_files_path, "inputs")
processed_dir = os.path.join(project_files_path, "processed")


"""topology_file = os.path.join(inputs, topology)"""

# Directory for PDB files
pdb = os.path.splitext(os.path.basename(xtc_file))[0] + "_pdb_files"
pdb_dir = os.path.join(processed_dir, pdb )
os.makedirs(pdb_dir, exist_ok=True)

# P2Rank Prediction
p2rank_processed_dir = os.path.join(processed_dir, 'p2rank_output')
os.makedirs(p2rank_processed_dir, exist_ok=True)
pdb_list = glob.glob(os.path.join(pdb_dir, '*.pdb'))
#print(pdb_list)
