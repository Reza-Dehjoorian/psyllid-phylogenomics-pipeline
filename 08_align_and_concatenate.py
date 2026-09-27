"""
Step 08: Multiple Sequence Alignment, Trimming, and Supermatrix Concatenation
Author: Reza Dehjoorian
Description: Performs MSA using MAFFT, trims alignment blocks with trimAl,
             and concatenates aligned orthologs into a phylogenomic supermatrix
             (supports both protein .faa and nucleotide .fna files).
"""

import os
import sys
import subprocess

# 1. Parse and validate arguments
try:
    input_dir = os.path.abspath(sys.argv[1])
    sif_mafft = os.path.abspath(sys.argv[2])
    sif_trimal = os.path.abspath(sys.argv[3])
    output_dir = os.path.abspath(sys.argv[4])
except IndexError:
    print("[ERROR] Missing required arguments.")
    print("Usage: python 08_align_and_concatenate.py <input_dir_with_orthologs> [path_to_mafft_sif] [path_to_trimal_sif] [output_dir]")
    sys.exit(1)

# Detect file extension (.faa or .fna)
sample_files = os.listdir(input_dir)
is_protein = any(f.endswith('.faa') for f in sample_files)
is_nucleotide = any(f.endswith('.fna') for f in sample_files)

if is_protein:
    ext = '.faa'
    seq_type = 'Protein'
elif is_nucleotide:
    ext = '.fna'
    seq_type = 'Nucleotide'
else:
    print(f"[ERROR] No valid .faa or .fna sequence files found in {input_dir}")
    sys.exit(1)

print(f"[INFO] Detected {seq_type} mode (extension: {ext})")

# Setup working directories
mafft_dir = os.path.join(output_dir, 'mafft_results')
trimal_dir = os.path.join(output_dir, 'trimal_results')
os.makedirs(mafft_dir, exist_ok=True)
os.makedirs(trimal_dir, exist_ok=True)

# --- Phase 1: MAFFT Alignment ---
print("\n" + "="*50)
print(f"[1/3] Running MAFFT Alignment for {seq_type} sequences...")
print("="*50)

ortholog_files = []
for f in os.listdir(input_dir):
    if f.endswith(ext):
        ortholog_files.append(f)
ortholog_files.sort()

for file_name in ortholog_files:
    gene_id = os.path.splitext(file_name)[0]
    in_file = os.path.join(input_dir, file_name)
    aligned_file = os.path.join(mafft_dir, f"{gene_id}_aligned{ext}")

    if os.path.exists(aligned_file):
        continue

    cmd = (
        f"apptainer exec {sif_mafft} "
        f"mafft --auto --quiet {in_file} > {aligned_file}"
    )

    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] MAFFT failed for {gene_id}: {e}")

print("[DONE] MAFFT alignments completed.")

# --- Phase 2: trimAl Trimming ---
print("\n" + "="*50)
print(f"[2/3] Running trimAl Trimming...")
print("="*50)

aligned_files = []
for f in os.listdir(mafft_dir):
    if f.endswith(ext):
        aligned_files.append(f)
aligned_files.sort()

for file_name in aligned_files:
    gene_id = file_name.replace(f'_aligned{ext}', '')
    in_aligned = os.path.join(mafft_dir, file_name)
    out_trimmed = os.path.join(trimal_dir, f"{gene_id}_trimmed{ext}")

    if os.path.exists(out_trimmed):
        continue

    cmd = [
        'apptainer', 'exec', sif_trimal,
        'trimal',
        '-in', in_aligned,
        '-out', out_trimmed,
        '-automated1'
    ]

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] trimAl failed for {gene_id}: {e.stderr}")

print("[DONE] trimAl trimming completed.")

# --- Phase 3: Supermatrix Concatenation ---
print("\n" + "="*50)
print(f"[3/3] Concatenating Genes into Supermatrix...")
print("="*50)

supermatrix = {}
trimmed_files = []
for f in os.listdir(trimal_dir):
    if f.endswith(ext):
        trimmed_files.append(f)
trimmed_files.sort()

for file_name in trimmed_files:
    file_path = os.path.join(trimal_dir, file_name)
    with open(file_path, 'r') as inpt:
        current_species = ''
        for line in inpt:
            line = line.strip()
            if not line:
                continue

            if line.startswith('>'):
                current_species = line.replace('>', '')
                if current_species not in supermatrix:
                    supermatrix[current_species] = ''
            else:
                supermatrix[current_species] += line

supermatrix_out = os.path.join(output_dir, f'supermatrix{ext}')
with open(supermatrix_out, 'w') as opt:
    for species, sequence in sorted(supermatrix.items()):
        opt.write(f">{species}\n")
        opt.write(f"{sequence}\n")

print(f"[COMPLETED] Supermatrix generated at: {supermatrix_out}")
print(f"[INFO] Total taxa concatenated: {len(supermatrix)}")
