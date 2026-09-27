"""
Step 06: Extract Shared Single-Copy Protein Orthologs
Author: Reza Dehjoorian
Description: Identifies shared single-copy BUSCO orthologs across all samples,
             extracts protein sequences (.faa), and renames FASTA headers 
             to match sample identifiers.
"""
import os
import sys

# 1. Parse and validate command-line arguments
try:
    target_dir = os.path.abspath(sys.argv[1])
    output_dir_protein = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(os.getcwd(), 'orthologs_protein')
except IndexError:
    print("[ERROR] Usage: python 06_extract_protein_orthologs.py <target_directory> [output_directory]")
    sys.exit(1)
print(f"[INFO] Scanning target directory: {target_dir}")

# 2. Locate BUSCO single-copy sequence directories
sample_paths = {}
for folder in os.listdir(target_dir):
    if folder.endswith('_result'):
        sample_name = folder.replace('_result', '')
        sample_dir = os.path.join(target_dir, folder)
        
        for root, dirs, _ in os.walk(sample_dir):
            if os.path.basename(root) == 'single_copy_busco_sequences':
                sample_paths[sample_name] = root
                print(f"[INFO] Found single-copy sequences for: {sample_name}")
                break
if not sample_paths:
    print("[ERROR] No single-copy BUSCO directories found.")
    sys.exit(1)


# 3. Identify common single-copy orthologs across all samples
all_gene_sets = []
for path in sample_paths.values():
    gene_list = []
    for gene in os.listdir(path):
        if gene.endswith('.faa'):
            gene_list.append(gene)
    all_gene_sets.append(set(gene_list))

if all_gene_sets:
    single_copy_gene_set = set.intersection(*all_gene_sets)

    print(f"\n[INFO] Total samples evaluated: {len(sample_paths)}")
    print(f"[INFO] Total shared single-copy orthologs: {len(single_copy_gene_set)}\n")
else:
    print("\n[ERROR] No gene sets collected.")
    sys.exit(1)
if not single_copy_gene_set:
    print("[ERROR] No shared single-copy genes found across all samples.")
    sys.exit(1)

os.makedirs(output_dir_protein, exist_ok=True)

# 4. Save shared ortholog identifiers list
list_file_path = os.path.join(output_dir_protein, 'single_copy_orthologs_list.txt')
with open(list_file_path, 'w') as op:
    for gene in sorted(single_copy_gene_set):
        gene_id = gene.split('.')[0]
        op.write(f'{gene_id}\n')


# 5. Extract sequences and standardize FASTA headers to sample names
for gene in sorted(single_copy_gene_set):
    gene_id = gene.split('.')[0]
    out_file_path = os.path.join(output_dir_protein, f"{gene_id}.faa")

    with open(out_file_path, 'w') as op:
        for sample_name, sample_path in sample_paths.items():
            full_file_path = os.path.join(sample_path, gene)

            if os.path.exists(full_file_path):
                with open(full_file_path, 'r') as inpt:
                    for line in inpt:
                        if line.startswith('>'):
                            op.write(f">{sample_name}\n")
                        else:
                            op.write(line)
print(f"[COMPLETED] Extracted {len(single_copy_gene_set)} protein orthologs into '{output_dir_protein}'.")
