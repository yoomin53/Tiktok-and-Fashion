import glob 
import pandas as pd
import os
csv_files = glob.glob("c:/Users/brian/OneDrive - The University of Hong Kong/Desktop/New folder/tiktok_video_data/tiktok_video_final/*.csv")\


for file in csv_files: 
    df = pd.read_csv(file)
    cleaned_data = df.drop_duplicates(subset=['id'])
    new_filename = os.path.splitext(file)[0] + "_cleaned.csv"
    cleaned_data.to_csv(new_filename, index=False)
    print(f"Cleaned data saved to {new_filename} .")

