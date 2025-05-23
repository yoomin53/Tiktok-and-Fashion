# Tiktok-and-Fashion-

this project scrapes data from Tiktok and finds its influence in fashion trends.  

<p align="center">
    <img src="./assets/readme/tiktokflowchart.drawio.png" width="250"/>
</p>


The TikTok data collection process involves a multi-step approach to gather a comprehensive dataset of videos related to specific hashtags, such as "mermaidcore" and "tomatogirl". The `TikTokApi_SearchByHashtag.py` script utilizes an unofficial TikTok API wrapper to search for videos by a specific hashtag, retrieving a list of relevant videos that may not necessarily include the exact hashtag due to TikTok's algorithmic collection of related content. However, due to the limitations of the TikTok API, the `Amplify.py` script is employed to enhance the sample size of the video dataset by reading a list of video IDs from a `data.csv` file, sending a request to the API to retrieve related videos, and filtering these results to check if they contain the target hashtag, repeating this process until the dataset reaches a size of over 1000 videos or has been repeated more than 5 times. Finally, the `Sentimental.py` script analyzes the sentiment of sampled comments from the collected videos using a transformer model, providing valuable insights into the emotional tone and public opinion associated with the target hashtags, ultimately allowing for in-depth analysis of trends, sentiment, and engagement metrics related to specific hashtags on TikTok.
