"""
Step 03: Post-Trimming Quality Control (FastQC)
Author: Reza Dehjoorian
Description: Performs quality control assessment on trimmed paired-end reads 
             (1P and 2P) using FastQC inside an Apptainer container.
"""

import os
import sys
import subprocess

# 1. Parse and validate command-line arguments
try:
    target_dir = os.path.abspath(sys.argv[1])
    fastqc_path = os.path.abspath(sys.argv[2])
except (IndexError, FileNotFoundError): 
    print("[ERROR] Missing required arguments.")
    print("Usage: python 03_qc_trimmed_reads.py <target_directory> <path_to_fastqc_sif>")
    sys.exit(1)

print(f"[INFO] Scanning target directory for trimmed reads: {target_dir}")

data_list = os.listdir(target_dir)

# 2. Run FastQC on trimmed paired-end reads
for file in data_list:
    if file.endswith('_result'):
        out_dir = os.path.join(target_dir, file)
        sample_name = file.replace('_result', '')

        # فایل‌های جفتِ فیلترشده خروجی Trimmomatic با پسوند 1P و 2P
        r1_trimmed = os.path.join(out_dir, f"{sample_name}_trimmed_1P.fq.gz")
        r2_trimmed = os.path.join(out_dir, f"{sample_name}_trimmed_2P.fq.gz")
        
        # نام گزارش برای بررسی شرط عدم تکرار
        fastqc_report = os.path.join(out_dir, f"{sample_name}_trimmed_1P_fastqc.html")

        # اگر گزارش قبلاً تولید شده باشد رد می‌شود
        if os.path.exists(fastqc_report):
            print(f"[SKIP] FastQC report already exists for '{sample_name}'.")
            continue

        # بررسی وجود فایل‌های تریم‌شده قبل از اجرا
        if os.path.exists(r1_trimmed) and os.path.exists(r2_trimmed):
            print(f"[RUNNING] Running FastQC on trimmed reads for '{sample_name}'...")
            fastqc_cmd = subprocess.run(
                ['apptainer', 'exec', fastqc_path, 'fastqc',
                 r1_trimmed, r2_trimmed, '-o', out_dir],
                capture_output=True, text=True, check=True
            )
            print(f"[DONE] Quality assessment completed for '{sample_name}'.")
        else:
            print(f"[WARNING] Trimmed reads missing for '{sample_name}', skipping...")

print("[COMPLETED] Step 03 (Post-trim FastQC) finished for all samples.")
