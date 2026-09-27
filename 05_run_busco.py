"""
Step 05: Genome Assembly Assessment (BUSCO)
Author: Reza Dehjoorian
Description: Evaluates genome assembly completeness using BUSCO with the 
             Hemiptera lineage dataset inside an Apptainer container.
"""

import os
import sys
import subprocess

# 1. Parse and validate command-line arguments
try:
    target_dir = os.path.abspath(sys.argv[1]) 
    sif_path = os.path.abspath(sys.argv[2]) if len(sys.argv) 
    lin_path = os.path.abspath(sys.argv[3]) if len(sys.argv) 

except (IndexError, FileNotFoundError): 
    print("[ERROR] Missing required arguments.")
    print("Usage: python 05_run_busco.py <target_directory> <path_to_busco_sif> <path_to_lineage_dataset>")    
    sys.exit(1)

# 2. Locate scaffolds.fasta for each sample
sample_information = {}
data_list = os.listdir(target_dir)

for folder in data_list:
    if folder.endswith('_result'):
        sample_name = folder.replace('_result', '')
        folder_path = os.path.join(target_dir, folder)
        folders_list = os.listdir(folder_path)
        
        for folder_1 in folders_list:
            if folder_1.endswith('_output'):
                full_path = os.path.join(folder_path, folder_1, 'scaffolds.fasta')

                if os.path.exists(full_path):

                    sample_information[sample_name] = [full_path, folder_path]
                    print(f'[INFO] Scaffolds found for {sample_name}')


# 3. Execute BUSCO assessment
for sample, info in sample_information.items():
    scaffolds_path = info[0]
    output_path = info[1]

    busco_out_folder = f'busco_{sample}_output'
    expected_result_dir = os.path.join(output_path, busco_out_folder)

    if os.path.exists(expected_result_dir):
        print(f'[SKIP] BUSCO for {sample} already completed, skipping...')
        continue

    cmd = [
        'apptainer', 'exec', sif_path,
        'busco',
        '-i', scaffolds_path,
        '-o', busco_out_folder,
        '--out_path', output_path,
        '-m', 'genome',
        '-l', lin_path,
        '-c', '8'
    ]
    
    print(f'[RUNNING] Running BUSCO for {sample}...')
    

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f'[DONE] BUSCO assessment for {sample} completed successfully.\n')
    except subprocess.CalledProcessError as e:
        # e.stderr captures the exact error message from the tool for debugging
        print(f'[ERROR] BUSCO failed for sample {sample}: {e.stderr}\n')

print("[COMPLETED] Step 04 (BUSCO assessment) finished.")
