import os
import subprocess
import glob
import mdtraj as md
from data_analysis.config import processed_dir, xtc_file, pdb_dir, p2rank_processed_dir

def xtc_to_pdb(xtc_file,topology, pdb_dir):
    """Convert XTC file to a series of PDB files."""
    # Load XTC file 
    traj = md.load_xtc(xtc_file, topology)
    for i, frame in enumerate(traj):
        pdb_file = os.path.join(pdb_dir, f"{os.path.splitext(os.path.basename(xtc_file))[0]}_{i}.pdb")
        frame.save_pdb(pdb_file)
        print(f"Frame {i} saved as {pdb_file}")
    return [os.path.join(pdb_dir, f"{os.path.splitext(os.path.basename(xtc_file))[0]}_{i}.pdb") for i in range(len(traj))]

def write_pdb_list(pdb_dir, output_file):
    """Write a list of PDB files to a file."""
    pdb_list = glob.glob(os.path.join(pdb_dir, '*.pdb'))
    with open(output_file, 'w') as f:
        for pdb_file in pdb_list:
            f.write(os.path.relpath(pdb_file, start=processed_dir))
            f.write('\n')
    print(f"PDB list written to {output_file}")
    return output_file

def run_p2rank(pdb_list_file, output_dir, threads=4):
    """Run P2Rank with the specified list of PDB files."""
    command = f'~/p2rank_2.3.1/prank predict {pdb_list_file} -o {output_dir} -threads {threads}'
    subprocess.call(command, shell=True)
    print(f"P2Rank output written to {output_dir}")
    return output_dir

# If you want the script to remain executable standalone
if __name__ == "__main__":
    # Convert XTC to PDB
    pdb_files = xtc_to_pdb(xtc_file, pdb_dir)

    # Write PDB list to a file
    pdb_list_file = os.path.join(processed_dir, 'pdb_list.ds')
    write_pdb_list(pdb_dir, pdb_list_file)

    # Run P2Rank
    run_p2rank(pdb_list_file, p2rank_processed_dir)
