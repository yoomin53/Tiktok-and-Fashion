import pandas as pd
from TikTokApi import TikTokApi
import asyncio
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve the ms_token from environment variables
ms_token = os.environ.get("ms_token", None)

# List of hashtags to filter
hashtags = ["mermaidcore", "mermaidcorefashion", "mermaidcoreaesthetic", "sirencore", "sirencoreaesthetic"]


#tiktok_video_mermaidcore_V3.csv
# Function to read a CSV file
def read_csv(file):
    df = pd.read_csv(file)
    df = df.drop_duplicates(subset=['id'])
    return df

# Function to process a single video
async def process_video(api, video_id, original_video_ids, filtered_videos, hashtags):
    async for related_video in api.video(id=video_id).related_videos():
        video_data = related_video.as_dict
        related_video_id = video_data.get('id', '')
        # Check if the video ID is already in the original CSV or filtered videos
        if related_video_id in original_video_ids or related_video_id in [v['id'] for v in filtered_videos]:
            continue

        # Get author data from the video data
        author_data = video_data.get('author', {})
        # Get the creation time of the video
        created_at = video_data.get('createTime', '')
        # Convert the creation time to a datetime object
        created_date = datetime.utcfromtimestamp(created_at)
        # Extract hashtags
        video_hashtags = [hashtag.name for hashtag in related_video.hashtags]

        # Check if the video was created between 2023 and 2024 and has the specified hashtags
        if created_date.year in [2023, 2024] and any(tag in hashtags for tag in video_hashtags):
            # Append the video data to the list
            filtered_videos.append({
                'id': related_video_id,
                'username': author_data.get('unique_id', '') or author_data.get('nickname', ''),
                'likes': int(video_data.get('stats', {}).get('diggCount', 0)),
                'views': video_data.get('stats', {}).get('playCount', 0),
                'comments': video_data.get('stats', {}).get('commentCount', 0),
                'shares': video_data.get('stats', {}).get('shareCount', 0),
                'collects': video_data.get('stats', {}).get('collectCount', 0),
                'repost': video_data.get('stats', {}).get('repostCount', 0),
                'isCommerce': video_data.get('isCommerce', False),
                'description': video_data.get('desc', ''),
                'duration': video_data.get('video', {}).get('duration', 0),
                'created_at': created_at,
                'VideoQuality': video_data.get('video', {}).get('videoQuality', 0),
                'hashtags': video_hashtags
            })
            logger.info(f"Added video with ID {related_video_id} to filtered list")
        else:
            logger.info(f"Skipped video with ID {related_video_id}: Hashtags {video_hashtags} or Created date {created_date} not in 2023 or 2024")

# Function to search for related videos and filter by hashtags and creation date
async def search_and_filter_videos(df, hashtags):
    async with TikTokApi() as api:
        await api.create_sessions(headless=False, ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
        filtered_videos = []
        original_video_ids = set(df['id'])
        total_videos = len(df['id'])
        logger.info(f"Total videos to process: {total_videos}")
        for index, video_id in enumerate(df['id']):
            try:
                logger.info(f"Processing video {index + 1}/{total_videos} with ID {video_id}")
                await asyncio.wait_for(process_video(api, video_id, original_video_ids, filtered_videos, hashtags), timeout=10)
            except asyncio.TimeoutError:
                logger.warning(f"Processing video {video_id} took too long, skipping to the next video.")
            except Exception as e:
                logger.error(f"Error fetching related videos for video ID {video_id}: {e}")
        return filtered_videos

# Main function
async def main():
    # Prompt the user to enter the name of the CSV file
    csv_file = "tiktok_videos.csv" #input("Enter the name of the CSV file to read: ")
    
    # Read the CSV file
    df = read_csv(csv_file)
    
    # Search for related videos and filter by hashtags and creation date
    filtered_videos = await search_and_filter_videos(df, hashtags)
    
    # Create a DataFrame from the filtered videos
    filtered_df = pd.DataFrame(filtered_videos)
    
    # Add a column with the date of the video creation
    filtered_df['date'] = filtered_df['created_at'].apply(lambda x: datetime.utcfromtimestamp(x).strftime('%Y-%m-%d'))
    
    # Print the DataFrame before saving
    print(filtered_df)
    
    # Save the filtered DataFrame to a new CSV file
    filtered_df.to_csv(csv_file.replace('.csv','')+'_amplified.csv', index=False, encoding='utf-8-sig')
    logger.info(f"Filtered videos saved to {csv_file.replace('.csv','')}_amplified.csv")

if __name__ == "__main__":
    asyncio.run(main())