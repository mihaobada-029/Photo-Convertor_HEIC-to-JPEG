import os
import logging
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Specify your input and output directories here
heic_dir = r"C:\Users\FULL PATH"  # Change to your input folder path
jpg_dir = r"C:\Users\FULL PATH"    # Change to your desired output folder path

output_quality = 85  # Set desired output quality (1-100)
max_workers = 4      # Set number of parallel workers

def convert_single_file(heic_path, jpg_path, output_quality):
    """Convert a single HEIC file to JPG format."""
    try:
        with Image.open(heic_path) as image:
            image.save(jpg_path, "JPEG", quality=output_quality)
        return heic_path, True  # Successful conversion
    except (UnidentifiedImageError, FileNotFoundError, OSError) as e:
        logging.error(f"Error converting '{heic_path}': {e}")
        return heic_path, False  # Failed conversion

def convert_heic_to_jpg(heic_dir, jpg_dir, output_quality=85, max_workers=4):
    """Convert HEIC images in a directory to JPG format using parallel processing."""
    register_heif_opener()

    if not os.path.isdir(heic_dir):
        logging.error(f"Directory '{heic_dir}' does not exist.")
        return

    # Create a directory to store the converted JPG files
    if os.path.exists(jpg_dir):
        user_input = input("Existing 'ConvertedFiles' folder detected. Delete and proceed? (y/n): ")
        if user_input.lower() != 'y':
            print("Conversion aborted.")
            return
        else:
            shutil.rmtree(jpg_dir)
    os.makedirs(jpg_dir, exist_ok=True)

    # Get all HEIC files in the specified directory
    heic_files = [file for file in os.listdir(heic_dir) if file.lower().endswith(".heic")]
    total_files = len(heic_files)

    if total_files == 0:
        logging.info("No HEIC files found in the directory.")
        return

    # Prepare file paths for conversion
    tasks = []
    for file_name in heic_files:
        heic_path = os.path.join(heic_dir, file_name)
        jpg_path = os.path.join(jpg_dir, os.path.splitext(file_name)[0] + ".jpg")

        # Skip conversion if the JPG already exists
        if os.path.exists(jpg_path):
            logging.info(f"Skipping '{file_name}' as the JPG already exists.")
            continue

        tasks.append((heic_path, jpg_path))

    # Convert HEIC files to JPG in parallel using ThreadPoolExecutor
    num_converted = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(convert_single_file, heic_path, jpg_path, output_quality): heic_path
            for heic_path, jpg_path in tasks
        }

        for future in as_completed(future_to_file):
            heic_file = future_to_file[future]
            try:
                _, success = future.result()
                if success:
                    num_converted += 1
                # Display progress
                progress = int((num_converted / total_files) * 100)
                print(f"Conversion progress: {progress}%", end="\r", flush=True)
            except Exception as e:
                logging.error(f"Error occurred during conversion of '{heic_file}': {e}")

    print(f"\nConversion completed successfully. {num_converted} files converted.")

# Convert HEIC to JPG with parallel processing
convert_heic_to_jpg(heic_dir, jpg_dir, output_quality, max_workers)
