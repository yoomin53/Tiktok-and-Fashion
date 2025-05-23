from TikTokApi import TikTokApi
import asyncio
import os
import pandas as pd
import logging
from transformers import pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve the ms_token from environment variables
ms_token = os.environ.get("ms_token", None)

# Initialize the sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

async def fetch_comments(api, video_id):
    video = api.video(id=video_id)
    comments = []
    async for comment in video.comments():
        comments.append(comment.text)
        print(comment)
    return comments

def analyze_sentiment(comments):
    sentiments = sentiment_pipeline(comments)
    if sentiments:
        # Convert sentiment labels to numerical scores
        scores = [int(sentiment['label'].split()[0]) for sentiment in sentiments]
        return sum(scores) / len(scores)
    return None

async def main():
    # Load the CSV file into a DataFrame
    df = pd.read_csv('QuietLuxury.csv')

    # Initialize lists to store sentiment data, comment counts, and accumulated texts
    sentiment_data = []
    comment_counts = []
    accumulated_texts = []

    async with TikTokApi() as api:
        await api.create_sessions(headless=False, ms_tokens=[ms_token], num_sessions=1, sleep_after=3)

        # Iterate over each video ID in the DataFrame
        for video_id in df['id']:
            try:
                # Fetch comments for the video ID
                comments = await fetch_comments(api, video_id)
                # Perform sentiment analysis on the comments
                sentiment = analyze_sentiment(comments)
                sentiment_data.append(sentiment)
                comment_counts.append(len(comments))
                accumulated_text = " ".join(comments)
                cleaned_text = accumulated_text.replace("\n", " ").replace('\t', ' ')
                accumulated_texts.append(cleaned_text)
            except Exception as e:
                logger.error(f"Error fetching comments for video ID {video_id}: {e}")
                sentiment_data.append(None)
                comment_counts.append(0)
                accumulated_texts.append("")

    # Add the sentiment data, comment counts, and accumulated texts to the DataFrame
    df['sentiment'] = sentiment_data
    df['comment_count'] = comment_counts
    df['accumulated_text'] = accumulated_texts

    # Save the updated DataFrame to a new CSV file
    df.to_csv('QuietLuxury_with_sentiment.csv', index=False, encoding='utf-8-sig')

if __name__ == "__main__":
    asyncio.run(main())