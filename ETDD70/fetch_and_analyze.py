import os
import zipfile
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

ETDD70_ZENODO_URL = "https://zenodo.org/records/13332134/files/data.zip?download=1" 
DATA_DIR = "raw_data"

def download_and_extract(url, extract_to):
    os.makedirs(extract_to, exist_ok=True)
    
    # Keywords indicating pre-calculated or aggregate files to skip
    skip_keywords = ['saccade', 'fixation', 'event', 'metric', 'aoi']
    
    if os.path.exists(extract_to) and len(os.listdir(extract_to)) > 0:
        for root, dirs, files in os.walk(extract_to):
            for file in files:
                name = file.lower()
                if name.endswith('.csv') and not any(kw in name for kw in skip_keywords):
                    return os.path.join(root, file)

    print("Downloading ETDD70 dataset from Zenodo (133.7 MB)...")
    response = requests.get(url, stream=True)
    
    if response.status_code == 200:
        print("Download complete. Extracting files...")
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            z.extractall(extract_to)
            for root, dirs, files in os.walk(extract_to):
                for file in files:
                    name = file.lower()
                    if name.endswith('.csv') and not any(kw in name for kw in skip_keywords):
                        return os.path.join(root, file)
    else:
        print(f"Failed to download. HTTP Status: {response.status_code}")
        return None

def analyze_gaze_sample(filepath):
    print(f"\n--- Analyzing ETDD70 Sample: {os.path.basename(filepath)} ---")
    
    # Use python engine with sep=None to auto-detect commas vs semicolons
    df = pd.read_csv(filepath, sep=None, engine='python')
    
    # Normalize headers (strip whitespace and make lowercase)
    df.columns = df.columns.str.strip().str.lower()
    print(f"Detected Columns: {list(df.columns)}")
    
    # Dynamically map X and Y columns if they aren't exactly 'x' and 'y'
    if 'x' not in df.columns or 'y' not in df.columns:
        x_candidates = [c for c in df.columns if c == 'x' or 'x_' in c or '_x' in c]
        y_candidates = [c for c in df.columns if c == 'y' or 'y_' in c or '_y' in c]
        
        if x_candidates and y_candidates:
            df.rename(columns={x_candidates[0]: 'x', y_candidates[0]: 'y'}, inplace=True)
            print(f"Mapped coordinate columns: {x_candidates[0]} -> 'x', {y_candidates[0]} -> 'y'")
        else:
            raise KeyError("Could not identify X/Y coordinate columns in the dataset.")

    # 1. Data Quality & Acquisition Gates
    total_frames = len(df)
    # Filter out tracker-loss artifacts (assuming 0.0 or NaN indicates a blink/loss)
    valid_mask = df['x'].notna() & (df['x'] != 0) & df['y'].notna() & (df['y'] != 0)
    
    usable_frames = valid_mask.sum()
    tracking_loss_pct = 100 - ((usable_frames / total_frames) * 100)
    
    print(f"Total Recorded Frames: {total_frames}")
    print(f"Usable Data: {(usable_frames / total_frames) * 100:.2f}%")
    print(f"Tracking Loss / Blinks: {tracking_loss_pct:.2f}%")

    # Ensure a time column exists for plotting
    if 'time' not in df.columns:
        # If ETDD70 lacks a time column, generate a mock one assuming 60Hz
        df['time'] = np.arange(len(df)) * (1000/60.0)

    # 2. Exploratory Data Visualization
    fig = plt.figure(figsize=(16, 10))
    
    ax1 = fig.add_subplot(2, 2, 1)
    ax1.plot(df['time'], df['x'], label='X Position', color='blue', alpha=0.7)
    ax1.set_title("X Coordinate over Time (Horizontal Reading)")
    ax1.set_xlabel("Time (ms)")
    ax1.set_ylabel("X Pixel")
    ax1.legend()

    ax2 = fig.add_subplot(2, 2, 2)
    ax2.plot(df['time'], df['y'], label='Y Position', color='red', alpha=0.7)
    ax2.set_title("Y Coordinate over Time (Line Transitions)")
    ax2.set_xlabel("Time (ms)")
    ax2.set_ylabel("Y Pixel")
    ax2.invert_yaxis() 
    ax2.legend()

    ax3 = fig.add_subplot(2, 2, 3)
    ax3.plot(df.loc[valid_mask, 'x'], df.loc[valid_mask, 'y'], 
             marker='o', markersize=2, linestyle='-', linewidth=0.5, alpha=0.5, color='purple')
    ax3.set_title("2D Gaze Scanpath")
    ax3.set_xlabel("X Pixel")
    ax3.set_ylabel("Y Pixel")
    ax3.invert_yaxis() 
    
    ax4 = fig.add_subplot(2, 2, 4)
    df['dx'] = df['x'].diff()
    df['dy'] = df['y'].diff()
    df['dt'] = df['time'].diff().replace(0, np.nan)
    df['velocity'] = np.sqrt(df['dx']**2 + df['dy']**2) / df['dt']
    
    ax4.plot(df['time'], df['velocity'], color='green', alpha=0.6)
    ax4.set_title("Raw Velocity Profile (Unfiltered)")
    ax4.set_xlabel("Time (ms)")
    ax4.set_ylabel("Velocity (px/ms)")
    
    # Safely cap Y limit avoiding NaNs
    valid_vel = df['velocity'].replace([np.inf, -np.inf], np.nan).dropna()
    if not valid_vel.empty:
        ax4.set_ylim(0, valid_vel.quantile(0.95) * 2) 

    plt.tight_layout()
    plot_path = os.path.join(DATA_DIR, 'etdd70_eda_plot.png')
    plt.savefig(plot_path)
    print(f"\nAnalysis plots saved to: {plot_path}")
    plt.show()

if __name__ == "__main__":
    sample_csv = download_and_extract(ETDD70_ZENODO_URL, DATA_DIR)
    if sample_csv:
        analyze_gaze_sample(sample_csv)
