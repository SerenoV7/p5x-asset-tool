import tkinter as tk
from tkinter import filedialog, messagebox

import os
import concurrent.futures

window = tk.Tk()
window.withdraw()  # Hide the main window

def process_bundle_file(file_path, bundles_dir, extraction_dir):
    with open(file_path, 'rb') as file:
        content = file.read()

    second_unityfs_offset = content.find(b'UnityFS', content.find(b'UnityFS') + 1)

    if second_unityfs_offset == -1:
        print(f"{file_path} is not a valid AssetBundle or uses different formatting/encryption method")
        return

    modified_content = content[second_unityfs_offset:]

    output_path = os.path.join(extraction_dir, os.path.relpath(file_path, bundles_dir))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'wb') as file:
        file.write(modified_content)

    print(f"Converted: {output_path}")

def process_directory(bundles_dir, extraction_dir, num_threads):
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_file = {executor.submit(process_bundle_file, os.path.join(root, file), bundles_dir, extraction_dir): file for root, _, files in os.walk(bundles_dir) for file in files if file.endswith('.bundle')}
        for future in concurrent.futures.as_completed(future_to_file):
            file = future_to_file[future]
            try:
                future.result()
            except Exception as exc:
                print(f'{file} generated an exception: {exc}')

def main():

    num_cores = os.cpu_count()
    if num_cores is None:
        num_cores = 1

    num_threads = 0

    if num_cores <= 6:
        num_threads = num_cores // 2
    else:
        num_threads = num_cores - 4

    bundles_directory = filedialog.askdirectory(title="Select the Bundles Directory")
    if not bundles_directory:
        messagebox.showinfo("Info", "The bundles directory was not selected. Exiting.")
        return
    
    extraction_directory = filedialog.askdirectory(title="Select the Extraction Directory")
    if not extraction_directory:
        messagebox.showinfo("Info", "The extraction directory was not selected. Exiting.")
        return
    
    process_directory(bundles_directory, extraction_directory, num_threads)
    
if __name__ == "__main__":
    main()