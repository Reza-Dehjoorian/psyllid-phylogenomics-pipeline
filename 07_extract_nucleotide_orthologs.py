"""
Step 07: Extract Shared Single-Copy Nucleotide Orthologs (CDS)
Author: Reza Dehjoorian
Description: Extracts CDS nucleotide sequences (.fna) for shared single-copy 
             BUSCO genes using gffread and scaffolds.fasta, and standardizes 
             FASTA headers across samples.
"""
import os
import sys
import subprocess


# 1. Parse and validate command-line arguments
try:
    target_dir = os.path.abspath(sys.argv[1])
    sif_gffread = os.path.abspath(sys.argv[2]) if len(sys.argv) 
    output_dir_genes = os.path.abspath(sys.argv[3]) if len(sys.argv) 
except IndexError:
    print("[ERROR] Missing required arguments.")
    print("Usage: python 07_extract_nucleotide_orthologs.py <target_directory> [path_to_gffread_sif] [output_directory]")
    sys.exit(1)

print(f"[INFO] Scanning target directory: {target_dir}")

# 2. Locate BUSCO single-copy sequence directories containing GFF annotations
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

# 3. Identify common single-copy GFF files across all samples
all_gene_sets = []
for path in sample_paths.values():
    gene_list = []
    for gene in os.listdir(path):
        if gene.endswith('.gff'):
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
    print("[ERROR] No shared single-copy GFF genes found across all samples.")
    sys.exit(1)


# 4. Save shared GFF ortholog identifiers list
os.makedirs(output_dir_genes, exist_ok=True)
list_file_path = os.path.join(output_dir_genes, 'single_copy_orthologs_gff_list.txt')
with open(list_file_path, 'w') as op:
    for gene in sorted(single_copy_gene_set):
        gene_id = gene.replace('.gff', '')
        op.write(f"{gene_id}\n")



# 5. Extract nucleotide CDS per sample using gffread
intermediate_fna_dir = os.path.join(output_dir_genes, 'extracted_busco_fna')
os.makedirs(intermediate_fna_dir, exist_ok=True)

print(f"[RUNNING] Starting CDS extraction for {len(single_copy_gene_set)} genes across {len(sample_paths)} species...")

for sample_name, gff_folder in sample_paths.items():
    sample_out_dir = os.path.join(intermediate_fna_dir, sample_name)
    os.makedirs(sample_out_dir, exist_ok=True)

    scaffold_path = os.path.join(target_dir, f"{sample_name}_result", f"spades_{sample_name}_output", "scaffolds.fasta")

    if not os.path.exists(scaffold_path):
        print(f"[WARN] Scaffold not found for {sample_name} at: {scaffold_path}")
        continue

    print(f"[INFO] Extracting CDS for: {sample_name}")

    for gene_gff in single_copy_gene_set:
        gene_id = gene_gff.replace('.gff', '')
        gff_file_path = os.path.join(gff_folder, gene_gff)
        out_fna_path = os.path.join(sample_out_dir, f"{gene_id}.fna")

        # Skip if already extracted
        if os.path.exists(out_fna_path):
            continue

        cmd = [
            'apptainer', 'exec', sif_gffread,
            'gffread', gff_file_path,
            '-g', scaffold_path,
            '-x', out_fna_path
        ]

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] gffread failed for {gene_id} in {sample_name}: {e.stderr}")

print("[DONE] Nucleotide CDS extraction completed.\n")

# 6. Aggregate by gene and standardize FASTA headers to sample names
for gene in sorted(single_copy_gene_set):
    gene_id = gene.replace('.gff', '')
    out_file_path = os.path.join(output_dir_genes, f"{gene_id}.fna")

    with open(out_file_path, 'w') as op:
        for sample_name in sample_paths.keys():
            full_file_path = os.path.join(intermediate_fna_dir, sample_name, f"{gene_id}.fna")

            if os.path.exists(full_file_path):
                with open(full_file_path, 'r') as inpt:
                    for line in inpt:
                        if line.startswith('>'):
                            op.write(f">{sample_name}\n")
                        else:
                            op.write(line)

print(f"[COMPLETED] Merged {len(single_copy_gene_set)} nucleotide ortholog files into '{output_dir_genes}'.")
