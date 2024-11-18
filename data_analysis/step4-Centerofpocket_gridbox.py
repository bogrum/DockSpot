import pandas as pd

# Open the text file
with open("most_similar.txt", "r") as file:
    # Read the entire content
    content = file.read()

# Split the content into blocks based on "File name,"
blocks = content.strip().split('File name,')

# Lists to store file names and residues
file_list = []
residue_list = []


data = {}


# Iterate through the blocks
for block in blocks[1:]:  # Start from index 1 to skip the empty string before the first 'File name,'
    # Split each block by lines
    lines = block.strip().split('\n')
    # Extract file name and residues
    file_name = lines[0]
    residues = lines[-1].split(", ")[1:]  # Extract residues from the last line, skipping the first element which is 'residues'
    
    # Append file name and residues to their respective lists
    file_list.append(file_name)
    residue_list.append(residues)
    data[file_name] = residues


# Print file names and corresponding residues
for file_name, residues in zip(file_list, residue_list):
    print("File name:", file_name)
    print("Residues:", ", ".join(residues))
    print()  # Empty line for separation

pdb_list=[]
for i in file_list:
    pdb_list.append("{}.pdb".format(i))
#retrieve pdb files from the folders
print(pdb_list)



pdb_files = "/home/bogrum/output_p2rank/2IXR_traj/pdb_files"

for x in range(0,len(pdb_list)):
    text = "{}/{}".format(pdb_files,pdb_list[x]),"r"
    with open("{}/{}".format(pdb_files,pdb_list[x]),"r") as file:
        prot = file.read()
        prot = prot.split("ATOM      1")
        print(prot[0])

#annotate atoms that are useful
def keep_atoms(input_pdb_file, output_pdb_file, atom_numbers_to_keep):
    with open(input_pdb_file, 'r') as f:
        lines = f.readlines()

    with open(output_pdb_file, 'w') as f:
        for line in lines:
            if line.startswith('ATOM'):
                atom_name = line[12:16].strip()
                if atom_name in atoms_to_keep:
                    f.write(line)

"""# Define the input PDB file path
input_pdb_file = 'input.pdb'

# Define the output PDB file path
output_pdb_file = 'output.pdb'

# Define the atoms you want to keep
atoms_to_keep = {'CA', 'CB', 'N', 'O'}"""

# Call the function to keep only the specified atoms
keep_atoms(input_pdb_file, output_pdb_file, atoms_to_keep)

#compute the center of the selected pocket

#compute the size of the pocket

#later to be used in docking
