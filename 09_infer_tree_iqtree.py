"""
Step 09: Maximum Likelihood Phylogenetic Inference with IQ-TREE
Author: Reza Dehjoorian
Description: Runs IQ-TREE on the concatenated supermatrix using ModelFinder
             and ultrafast bootstrap.
"""

import os
import sys
import subprocess

try:
    supermatrix_file = os.path.abspath(sys.argv[1])
    sif_iqtree = os.path.abspath(sys.argv[2])
    prefix = sys.argv[3]
except IndexError:
    print("[ERROR] Missing required arguments.")
    print("Usage: python 09_infer_tree_iqtree.py <supermatrix_file> [path_to_iqtree_sif] [prefix]")
    sys.exit(1)

out_dir = os.path.dirname(supermatrix_file)
prefix_path = os.path.join(out_dir, prefix)

cmd = [
    'apptainer', 'exec', sif_iqtree,
    'iqtree2',
    '-s', supermatrix_file,
    '-m', 'MFP',
    '-B', '1000',
    '-T', '4',
    '--prefix', prefix_path
]

print(f"[INFO] Starting IQ-TREE on {supermatrix_file}...")
try:
    subprocess.run(cmd, check=True)
    print(f"[COMPLETED] Tree inference finished. Results prefix: {prefix_path}")
except subprocess.CalledProcessError as e:
    print(f"[ERROR] IQ-TREE execution failed: {e}")
