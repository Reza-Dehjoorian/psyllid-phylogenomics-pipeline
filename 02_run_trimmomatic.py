"""
Step 02: Read Trimming (Trimmomatic)
Author: Reza Dehjoorian
Description: Performs adapter and quality trimming on paired-end FASTQ reads 
             using Trimmomatic inside an Apptainer container.
"""

import os
import sys
import subprocess

# 1. Parse and validate command-line arguments
try:
    target_dir = os.path.abspath(sys.argv[1])
    sif_path = os.path.abspath(sys.argv[2])
except (IndexError, FileNotFoundError): 
    print("[ERROR] Missing required arguments.")
    print("Usage: python 02_run_trimmomatic.py <target_directory> <path_to_trimmomatic_sif>")    
    sys.exit(1)

print(f"[INFO] Scanning target directory: {target_dir}")

# 2. Identify target samples and collect FASTQ paths
data_list = os.listdir(target_dir)
sample_information = {}

for folder in data_list:
    if folder.endswith('_result'):
        sample_name = folder.replace('_result', '')
        folder_path = os.path.join(target_dir, folder)

        r1 = os.path.join(folder_path, 'unmapped_target_R1.fastq.gz')
        r2 = os.path.join(folder_path, 'unmapped_target_R2.fastq.gz')

        if os.path.exists(r1) and os.path.exists(r2):
            sample_information[sample_name] = [r1, r2, folder_path]        

print(f"[INFO] Found {len(sample_information)} valid samples ready for processing.")

# 3. Execute Trimmomatic in paired-end mode with idempotency check
for sample, paths in sample_information.items():
    R1 = paths[0]
    R2 = paths[1]
    output_path = paths[2]

    summary_file = os.path.join(output_path, f'{sample}_summary.txt')
    baseout_path = os.path.join(output_path, f'{sample}_trimmed.fq.gz')

    # Skip if trimming summary already exists
    if os.path.exists(summary_file):
        print(f"[SKIP] Sample '{sample}' already processed (summary file exists).")        
        continue

    cmd = [
        'apptainer', 'exec', sif_path,
        'trimmomatic', 'PE',
        '-threads', '4',
        '-phred33',
        '-summary', summary_file,
        R1, R2,
        '-baseout', baseout_path,
        'LEADING:3', 'TRAILING:3', 'SLIDINGWINDOW:4:13', 'MINLEN:36'
    ]

    print(f"[RUNNING] Executing Trimmomatic for '{sample}'...")
    trimmomatic_cmd = subprocess.run(cmd, capture_output=True, text=True, check=True)
    print(f"[DONE] Successfully completed trimming for '{sample}'.")
    
print("[COMPLETED] Step 02 (Trimmomatic) finished for all samples.")
