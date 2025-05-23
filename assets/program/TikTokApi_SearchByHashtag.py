from TikTokApi import TikTokApi
import asyncio
import os
import pandas as pd
from datetime import datetime
import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve the ms_token from environment variables
ms_token = os.environ.get("ms_token", None)

# Define an asynchronous function to get videos for multiple hashtags
async def get_hashtag_videos(hashtags, count):
    retries = 5  # Number of retries for handling session closure
    for attempt in range(retries):
        try:
            # Create an asynchronous context for the TikTokApi
            async with TikTokApi() as api:
                # Create sessions with the TikTok API
                await api.create_sessions(headless=False, ms_tokens=[ms_token], num_sessions=1, sleep_after=3)
                # Initialize a list to store DataFrames for each hashtag
                all_data = []
                # Iterate over each hashtag in the provided list
                for hashtag in hashtags:
                    logger.info(f"Fetching videos for hashtag: {hashtag}")
                    # Initialize an empty list to store video data
                    data = []
                    # Initialize a set to store unique video IDs
                    unique_video_ids = set()
                    # Get the hashtag object from the API
                    tag = api.hashtag(name=hashtag)
                    fetched_count = 0
                    offset = 0
                    consecutive_no_new_videos = 0

                    while fetched_count < count:
                        try:
                            # Track the number of videos fetched in this iteration
                            iteration_fetched_count = 0
                            # Fetch videos for the current hashtag with pagination
                            async for video in tag.videos(count=1000, cursor=offset):
                                # Convert video data to a dictionary
                                video_data = video.as_dict
                                video_id = video_data.get('id', '')
                                # Check if the video ID is already in the set of unique video IDs
                                if video_id in unique_video_ids:
                                    continue

                                # Get author data from the video data
                                author_data = video_data.get('author', {})
                                # Get the creation time of the video
                                created_at = video_data.get('createTime', '')
                                # Convert the creation time to a datetime object
                                created_date = datetime.utcfromtimestamp(created_at)

                                # Log the creation date of the video
                                logger.info(f"Video ID: {video_id}, Created Date: {created_date}")

                                # Filter videos created in 2023 and 2024
                                if created_date.year in [2023, 2024]:
                                    # Extract hashtags from the video data
                                    video_hashtags = [hashtag.name for hashtag in video.hashtags]

                                    # Append the video data to the list
                                    data.append({
                                        'id': video_id,
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
                                        'hashtags': video_hashtags,
                                    })
                                    # Add the video ID to the set of unique video IDs
                                    unique_video_ids.add(video_id)
                                    fetched_count += 1
                                    iteration_fetched_count += 1
                                    # Log progress every 10 videos
                                    if fetched_count % 10 == 0:
                                        logger.info(f"Fetched {fetched_count} videos for hashtag {hashtag}")
                                # Add a delay to avoid hitting rate limits
                                await asyncio.sleep(0.01)

                                if fetched_count >= count:
                                    break

                            if iteration_fetched_count == 0:
                                consecutive_no_new_videos += 1
                                logger.info(f"No new videos fetched in this iteration, consecutive no new videos: {consecutive_no_new_videos}")
                                if consecutive_no_new_videos >= 3:
                                    logger.info(f"No new videos fetched for 3 consecutive iterations, breaking the loop for hashtag: {hashtag}")
                                    break
                            else:
                                consecutive_no_new_videos = 0

                            offset += 30
                            logger.info(f"Updated offset: {offset}")
                        except Exception as e:
                            logger.error(f"Error fetching videos for hashtag {hashtag}: {e}")
                            break

                    logger.info(f"Total videos fetched for hashtag {hashtag}: {fetched_count}")
                    # Create a DataFrame from the list of video data
                    df = pd.DataFrame(data)
                    # Add a column with the date of the video creation
                    df['date'] = df['created_at'].apply(lambda x: datetime.utcfromtimestamp(x).strftime('%Y-%m-%d'))
                    # Drop duplicate videos based on the video ID
                    df = df.drop_duplicates(subset=['id'])
                    # Sort the DataFrame by the 'created_at' column in ascending order (oldest to newest)
                    df = df.sort_values(by='created_at', ascending=True)
                    logger.info(f"Total unique videos: {len(df)}")
                    all_data.append(df)

                return pd.concat(all_data, ignore_index=True)
        except Exception as e:
            logger.error(f"Error in attempt {attempt + 1}/{retries}: {e}")
            if attempt < retries - 1:
                sleep_time = 2 ** attempt + random.uniform(0, 1)
                logger.info(f"Retrying in {sleep_time:.2f} seconds...")
                await asyncio.sleep(sleep_time)
            else:
                logger.error(f"Failed after {retries} attempts")
                raise

if __name__ == "__main__":
    # List of hashtags to scrape
    count = 1000  # Change this to the number of videos you want to fetch per hashtag
    ##hashtags = ["barbiecore", "barbieoutfit", "barbiecoreaesthetic", "barbiegirl", "pinkoutift"] #add more hastags as needed 
    hashtags = ["mermaidcore", "mermaidcorefashion", "mermaidcoreaesthetic", "sirencore", "sirencoreaesthetic"]
    #hashtags = ["tomatogirl", "tomatogirloutfit", "tomatogirlaesthetic", "tomatogirlmakeup", "tomatogirlsummer"]
    #hashtags = ["quietluxury", "quietluxuryfashion", "quietluxuryaesthetic", "stealthwealth", "oldmoneyoutfits", "oldmoney"]
    #hashtags = ["coastalcowgirl", "coastalcowgirloutfit", "coastalcowgirlaesthetic", "coastalcowgirlsummer", "cowgirlboots", "coastalcowboy", "cowboyboots"]
    #hashtags = ["blokecore", "blokecoreoutfit", "blokecoreaesthetic", "blokettecore", "jerseyoutfit"]

    df = asyncio.run(get_hashtag_videos(hashtags, count))
    # Drop duplicate videos based on the video ID
    df = df.drop_duplicates(subset=['id'])
    # Sort the DataFrame by the 'created_at' column in ascending order (oldest to newest)
    df = df.sort_values(by='created_at', ascending=True)
    print(df)
    # Save the DataFrame to a CSV file
    df.to_csv('tiktok_videos.csv', index=False, encoding='utf-8-sig')

    """
    API Limitations: The TikTok API has limitations on the number of videos that can be fetched per request. If you're trying to fetch too many videos at once, the API might not return any new videos.

No New Videos: It's possible that there are no new videos available for the hashtag you're searching for. If the hashtag is not very popular or if there are no new videos being uploaded, the API will not return any new videos.

API Rate Limiting: TikTok has rate limiting in place to prevent abuse of their API. If you're making too many requests in a short period of time, you might be hitting these rate limits and not being able to fetch any new videos.
    """