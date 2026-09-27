"""
Step 04: De Novo Genome Assembly (SPAdes)
Author: Reza Dehjoorian
Description: Performs paired-end de novo genome assembly using SPAdes 
             inside an Apptainer container.
"""
import os
import sys
import subprocess

# 1. Parse and validate command-line arguments
try:
    target_dir = os.path.abspath(sys.argv[1])
    sif_path = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else '/mnt/nfs/home/reza.dehjoorian/apps/spades.sif'
except IndexError: 
    print('[ERROR] Invalid input: please provide target directory.')
    sys.exit(1)

# 2. Identify samples and paired-end trimmed reads
data_list = os.listdir(target_dir)
sample_information = {}

for directory in data_list:
    if directory.endswith('_result'):
        sample_name = directory.replace('_result', '')
        folder_path = os.path.join(target_dir, directory)

        full_path_R1 = os.path.join(folder_path, f'{sample_name}_trimmed_1P.fq.gz')
        full_path_R2 = os.path.join(folder_path, f'{sample_name}_trimmed_2P.fq.gz')

        if os.path.exists(full_path_R1) and os.path.exists(full_path_R2):
            sample_information[sample_name] = [full_path_R1, full_path_R2, folder_path]
            print(f'[INFO] Paths confirmed for sample: {sample_name}')


# 3. Execute SPAdes assembly
for sample, paths in sample_information.items():
    R1 = paths[0]
    R2 = paths[1]
    output_path = paths[2]

    spades_out_dir = os.path.join(output_path, f'spades_{sample}_output')
    expected_scaffolds = os.path.join(spades_out_dir, 'scaffolds.fasta')

    # Skip if assembly already completed
    if os.path.exists(expected_scaffolds):
        print(f'[SKIP] Assembly already completed for {sample}, skipping...')
        continue

    cmd = [
        'apptainer', 'exec', sif_path,
        'spades.py',
        '-1', R1,
        '-2', R2,
        '-o', spades_out_dir,
        '-t', '16',
        '-m', '64'
    ]

    print(f'[RUNNING] Running SPAdes for {sample}...')

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f'[DONE] Sample {sample} has been successfully assembled.\n')
    except subprocess.CalledProcessError as e:
        # e.stderr captures the exact error message from the tool for debugging
        print(f'[ERROR] SPAdes failed for sample {sample}: {e.stderr}\n')

