import pandas as pd
import numpy as np
from scipy.cluster import hierarchy
from sklearn.preprocessing import MultiLabelBinarizer
import seaborn as sns
import matplotlib.pyplot as plt
#from config import processed_dir

def load_data(csv_file_path):
    """
    Load the CSV file into a DataFrame.
    """
    return pd.read_csv(csv_file_path)

def preprocess_data(data):
    """
    Preprocess the data: split residues into lists and encode them.
    """
    residues = data['residues'].str.split()  # Split residues strings into lists
    mlb = MultiLabelBinarizer()
    residues_encoded = mlb.fit_transform(residues)
    return residues_encoded, mlb

def perform_clustering(residues_encoded, method='ward'):
    """
    Perform hierarchical clustering and return the linkage matrix.
    """
    linkage = hierarchy.linkage(residues_encoded, method=method)
    return linkage

def plot_clustermap(residues_encoded, method='ward', cmap='viridis'):
    """
    Generate and display a clustermap.
    """
    sns.clustermap(residues_encoded, method=method, cmap=cmap, row_cluster=True, col_cluster=False)
    plt.show()

def get_cluster_representatives(data, residues_encoded, linkage, depth=3):
    """
    Identify representative pockets for each cluster at the given depth.
    """
    cutree = hierarchy.cut_tree(linkage, n_clusters=depth)
    representatives = []

    def euclidean_distance(p, q):
        return np.sqrt(np.sum((p - q) ** 2))

    for cluster_id in range(depth):
        indices = [i for i, c in enumerate(cutree) if c[0] == cluster_id]
        if indices:
            cluster_points = residues_encoded[indices]
            centroid = np.mean(cluster_points, axis=0)
            distances = [euclidean_distance(centroid, point) for point in cluster_points]
            representative_index = np.argmin(distances)
            representative = cluster_points[representative_index]
            representative_pockets = data.iloc[indices[representative_index]]
            representatives.append((cluster_id, representative_pockets))

    return representatives

def save_representatives_to_file(representatives, file_path):
    """
    Save representative pockets to a text file.
    """
    # Clean the contents of the text file
    with open(file_path, "w") as file:
        pass 

    for rep in representatives:
        rep[1].to_csv(file_path, mode='a', index=True, header=False)

# Wrapper function to run the entire process
def cluster_and_save_representatives(csv_file_path, output_file_path, depth=3):
    """
    Full workflow: load data, preprocess, cluster, and save representatives.
    """
    data = load_data(csv_file_path)
    residues_encoded, _ = preprocess_data(data)
    linkage = perform_clustering(residues_encoded)
    representatives = get_cluster_representatives(data, residues_encoded, linkage, depth)
    save_representatives_to_file(representatives, output_file_path)
    return representatives
