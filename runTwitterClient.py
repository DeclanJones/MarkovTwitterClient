from TwitterClient import TwitterClient

# Keys for Tweepy TwitterClient
CONSUMER_KEY = 'fKmzykMYS2SfPSmHNyNI5dT9a'
CONSUMER_SECRET = 'Nq2r9E1L8rx4OQ8xIEzvFAfpVnSy4pp7Fva5QJleyOzUqg46jC'
ACCESS_TOKEN = '4608889037-DuDZdgi1wXcJTj5XI2l93SkHx5vnimmIa6fqOEh'
ACCESS_TOKEN_SECRET = 'ylFmbrAu9PuoweHwPx3X1gw158nO3jTD94fuDiL446phw'

TWEET_FILEPATH = "/Users/declanjones/Desktop/TweetProj/Tweet_Data/Tweets/tweet.txt"

# Initialize Tweepy Twitter Client
client = TwitterClient(CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
client.scrape()

# Get tweets to tweet from tweet.txt
f = open(TWEET_FILEPATH, 'rb')
allTweets = f.readlines()
nextTweet = ''
if allTweets:
    nextTweet = allTweets[0]
f.close()

if nextTweet != '':
    client.post(nextTweet)

# Remove tweeted tweet from tweet.txt for next pass
f = open(TWEET_FILEPATH, 'wb')
index = 1
tweetsLeft = len(allTweets) - 1
while index < tweetsLeft:
    f.write(allTweets[i])
    index += 1
f.close()
exit()

