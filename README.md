# DockSpot: Ensemble Docking Tool

This repository contains the code and resources for a web-based tool designed to predict ligand-binding sites on proteins and facilitate molecular docking simulations. The tool leverages state-of-the-art algorithms to enhance the accuracy and efficiency of protein-ligand interaction analysis, making it an invaluable resource for researchers in drug design, bioinformatics, and computational biology.

## Key Features
- **Ligand-Binding Site Prediction**: Accurate identification of potential binding pockets on protein structures using advanced computational methods.
- **Molecular Docking**: Integrates various docking algorithms to simulate and predict ligand binding poses.
- **Web-based Interface**: User-friendly interface to upload protein structures, run simulations, and visualize results in real-time.
- **Open-source**: Free and open to contributions, ensuring constant improvement and adaptation to the latest advancements in computational chemistry.

## Technologies
- **Python**: The core backend is developed in Python, utilizing popular libraries such as [NumPy](https://numpy.org/), [SciPy](https://scipy.org/), and [RDKit](https://www.rdkit.org/).
- **Flask**: Lightweight web framework for building the web interface and handling user interactions.
- **Cloud Integration**: Utilizes cloud hosting for computationally intensive tasks and provides easy access to users worldwide.

## Installation
To run the project locally, clone the repository and install the necessary dependencies:

```bash
git clone https://github.com/bogrum/DockSpot.git
cd DockSpot
pip install -r requirements.txt
```

## Usage
Start the Flask server:
```bash
python app.py
```
Access the web interface via http://localhost:5000.
Upload a protein structure, configure docking parameters, and view the results directly in your browser.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
