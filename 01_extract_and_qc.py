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

except (IndexError, FileNotFoundError): 
    print('invalid input')
    sys.exit(1)
  

# 2. Extract paired-end zip files into separate directories
data_list = os.listdir(target_dir)
for zip_file in data_list:

    if zip_file.endswith('.zip'):

        dir_name = f"{zip_file.split('.')[0]}_result"
        dir_path = os.path.join(target_dir, dir_name)

      # Skip extraction if the output directory already exists
        if os.path.exists(dir_path):
            print(f"Skipping {zip_file}: result directory already exists.")
            continue

        zip_path = os.path.join(target_dir, zip_file)

        mkdir_cmd = subprocess.run(['mkdir', '-p', dir_path], capture_output=True, text=True, check=True)
        unzip_cmd = subprocess.run(['unzip', '-j', '-o', zip_path, '-d', dir_path], capture_output=True, text=True, check=True)


# 3. Run FastQC on extracted reads using Apptainer
data_list = os.listdir(target_dir)

for file in data_list:
    if file.endswith('_result'):

        out_dir = os.path.join(target_dir, file)
        fastqc_report = os.path.join(out_dir, 'unmapped_target_R1_fastqc.html')

        # Skip QC if report is already generated
        if os.path.exists(fastqc_report):
            print(f"Skipping FastQC for {file}: report already exists.")
            continue

        r1 = os.path.join(out_dir, 'unmapped_target_R1.fastq.gz')
        r2 = os.path.join(out_dir, 'unmapped_target_R2.fastq.gz')

        fastqc_cmd = subprocess.run(['apptainer', 'exec', fastqc_path, 'fastqc',
                                    r1, r2, '-o', out_dir], capture_output=True, text=True, check=True)
            
print("Step 01 QC completed successfully.")
