"""
Step 01: Raw Reads Extraction and Quality Control (FastQC)
Author: Reza Dehjoorian
Description: Extracts raw sequencing zip archives and performs quality control 
             assessment using FastQC inside an Apptainer container.
"""

import os
import sys
import subprocess

# 1. Parse and validate command-line arguments
try:
    target_dir = os.path.abspath(sys.argv[1])
    fastqc_path = os.path.abspath(sys.argv[2])
except IndexError:
    print("[ERROR] Missing required arguments.")
    print("Usage: python 01_raw_reads_qc.py <target_directory> <path_to_fastqc_sif>")
    sys.exit(1)

if not os.path.exists(target_dir):
    print(f"[ERROR] Target directory not found: {target_dir}")
    sys.exit(1)

if not os.path.exists(fastqc_path):
    print(f"[ERROR] FastQC container image not found: {fastqc_path}")
    sys.exit(1)

print("\n" + "="*50)
print(">>> [1/2] Extracting Raw Sequencing Archives...")
print("="*50)
print(f"[INFO] Target Directory: {target_dir}")

# 2. Extract paired-end zip files into separate directories
data_list = sorted(os.listdir(target_dir))
zip_found = False

for zip_file in data_list:
    if zip_file.endswith('.zip'):
        zip_found = True
        sample_name = zip_file.replace('.zip', '')
        dir_name = f"{sample_name}_result"
        dir_path = os.path.join(target_dir, dir_name)
        zip_path = os.path.join(target_dir, zip_file)

        # Skip extraction if the output directory already exists
        if os.path.exists(dir_path):
            print(f"[SKIP] Directory already exists for: {zip_file}")
            continue

        print(f"[RUNNING] Extracting {zip_file} -> {dir_name}/")
        os.makedirs(dir_path, exist_ok=True)
        subprocess.run(['unzip', '-j', '-o', zip_path, '-d', dir_path], 
                       capture_output=True, text=True, check=True)

if not zip_found:
    print("[INFO] No .zip archives found to extract.")

# 3. Run FastQC on extracted reads using Apptainer
print("\n" + "="*50)
print(">>> [2/2] Running FastQC Quality Assessment...")
print("="*50)

data_list = sorted(os.listdir(target_dir))
qc_count = 0

for folder in data_list:
    if folder.endswith('_result'):
        out_dir = os.path.join(target_dir, folder)
        fastqc_report = os.path.join(out_dir, 'unmapped_target_R1_fastqc.html')

        # Skip QC if report is already generated
        if os.path.exists(fastqc_report):
            print(f"[SKIP] FastQC report already exists for: {folder}")
            continue

        r1 = os.path.join(out_dir, 'unmapped_target_R1.fastq.gz')
        r2 = os.path.join(out_dir, 'unmapped_target_R2.fastq.gz')

        if not (os.path.exists(r1) and os.path.exists(r2)):
            print(f"[WARN] Paired-end reads missing in {folder}, skipping QC.")
            continue

        print(f"[RUNNING] FastQC processing: {folder}")
        cmd = ['apptainer', 'exec', fastqc_path, 'fastqc', r1, r2, '-o', out_dir]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            qc_count += 1
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] FastQC failed for {folder}: {e.stderr}")

print("\n" + "="*50)
print(f"[COMPLETED] Step 01 finished successfully.")
print(f"[INFO] New FastQC reports generated: {qc_count}")
print("="*50 + "\n")
