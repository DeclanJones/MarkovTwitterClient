import random
import os
import sys

class MarkovChain:

    def __init__(self, numPrior):
        # number of words we will condition on (currently can only condition on 1 word)
        self.numPrior = numPrior
        # number of total words in all tweets
        self.totalWords = 0.0
        # startingDict ----> Key: State,  Value: # Times word appears
        self.startingDict = {}
        # dictOfDicts  ----> Key: State,  Value: Dict{Key: NextWord, Value: # times NextWord follows State}
        self.dictOfDicts = {}
        # Array of ending punctuations
        self.punctuation = [".", "!", "?"]
        # Set of words that should have first letter capitalized
        self.capSet = set(["god", "jesus", "heaven", "mary", "hell", 'i', "america", "republican"])
        # Set of words that should have all letters capitalized
        self.allCapSet = set(["nbc", "abc", "fox", "gop", "usa", "u.s.a"])

    # Fills self.startingDict with {Key: State, Value: # times word appears
    def populateStartingDict(self, tweet):
        wordLst = tweet.split()
        stateIndexStart = 0
        stateIndexEnd = self.numPrior - 1
        while stateIndexEnd < len(wordLst) - 2:
            self.totalWords += 1.0
            index = stateIndexStart
            state = ''
            # Make state = "word0 word1 ... wordN"
            while index <= stateIndexEnd:
                nextWord = wordLst[index]
                if nextWord == "&amp" or nextWord == "&":
                    nextWord = 'and'
                state = state + nextWord + " "
                index += 1
            nextWord = wordLst[stateIndexEnd + 1]
            if nextWord == "&amp" or nextWord == "&":
                nextWord = 'and'
            # Update the state in startingDict
            if state not in self.startingDict.keys():
                self.startingDict[state] = 1.0
            else:
                self.startingDict[state] += 1.0
            self.populateDictOfDicts(state, nextWord)
            stateIndexStart += 1
            stateIndexEnd += 1


    # Makes a dict with {Key: state, Value: map{nextWord: # times nextWord follows state}}
    def populateDictOfDicts(self, state, nextWord):
        # If key doesn't exist add it to dictOfDicts
        if state not in self.dictOfDicts.keys():
            self.dictOfDicts[state] = {nextWord: 1.0}
        # Both the key and value already exist in dictOfDicts
        if state in self.dictOfDicts.keys() and nextWord in self.dictOfDicts[state].keys():
                self.dictOfDicts[state][nextWord] += 1.0
        # State key exists but nextWord not in dict value
        else:
            self.dictOfDicts[state][nextWord] = 1.0

    # Normalizes values in startingDict to be between 0 and 1
    def normalizeStartingDict(self):
        for key in self.startingDict.keys():
            self.startingDict[key] = self.startingDict[key] / self.totalWords

    # Normalizes a sub dictionary from dictOfDicts
    def normalizeValueDict(self, dict):
        numWords = 0.0
        for key in dict.keys():
            numWords += dict[key]
        for key in dict.keys():
            dict[key] = dict[key] / numWords

    # Returns a string relating to state based on probability
    def getBestState(self, seedDouble):
        bestState = ''
        minDist = 100.0
        for key in self.startingDict.keys():
            currentDist = abs(self.startingDict[key] - seedDouble)
            if currentDist < minDist:
                minDist = currentDist
                bestState = key
        return bestState

    # Capitalizes the given word if necessary
    def capCheck(self, word, capitalize):
        punctuation = ''
        if word[-1] in self.punctuation:
            word = word[:-1]
            punctuation = word[-1]
        if word in self.capSet or capitalize:
            word = word.capitalize()
        if word.lower() in self.allCapSet:
            word = word.upper()
        return word + punctuation

    # Return the next word based on the sub dictionary of dictOfDicts and given seed
    def getNext(self, dict, seed, capitalize):
        nextWord = ''
        if len(dict.keys()) == 0:
            return nextWord
        minDist = 100.0
        for key in dict.keys():
            currentDist = abs(dict[key] - seed)
            if currentDist < minDist:
                minDist = currentDist
                nextWord = key
        nextWord = self.capCheck(nextWord, capitalize)
        return nextWord


    # adds the given word to the tweet if it doesn't go over 140 characters, else it adds final punctuation
    def addWord(self, tweet, nextWord, wordCount, capitalize):
        if len(tweet) + len(nextWord) < 139:
            if capitalize:
                nextWord.capitalize()
            tweet += " " + nextWord
        if len(tweet) + len(nextWord) >= 140:
            tweet.capitalize()
            randIndex = random.randint(0, len(self.punctuation) - 1)
            tweet += self.punctuation[randIndex]
        return tweet

    def updateStateWordLst(self, stateWordLst, nextWord):
        index = 1
        updatedLst = stateWordLst
        while index < self.numPrior:
            updatedLst[index - 1] = stateWordLst[index]
            index += 1
        updatedLst[self.numPrior - 1] = nextWord
        return updatedLst

    # Creates a tweet and returns it as a string
    def makeTweet(self):
        self.normalizeStartingDict()
        for key in self.dictOfDicts.keys():
            self.normalizeValueDict(self.dictOfDicts[key])
        randIndex = random.randint(0, len(self.startingDict))
        currentState = self.startingDict.keys()[randIndex][:-1]
        tweet = currentState.capitalize()
        stateWordLst = currentState.split()
        nextWord = ''
        noneCheck = 0
        wordCount = self.numPrior
        capitalize = False
        while len(tweet) + len(nextWord) < 139:
            seed = random.random()
            # get a state that does not have an empty sub dictionary in self.dictOfDicts
            while self.dictOfDicts.get(currentState) == None or len(self.dictOfDicts[currentState].keys()) == 0:
                if noneCheck > 3:
                    currentState = self.startingDict.keys()[random.randint(0, len(self.startingDict.keys()) - 1)]
                    break
                if self.dictOfDicts.get(currentState) == None:
                    noneCheck += 1
                currentState = self.getBestState(seed)
            nextWord = self.getNext(self.dictOfDicts.get(currentState), seed, capitalize)
            if nextWord in stateWordLst:
                nextWord = random.choice(self.dictOfDicts[currentState].keys())
            tweet = self.addWord(tweet, nextWord, wordCount, capitalize)
            wordCount += 1
            tweet = tweet.strip().capitalize()
            stateWordLst = self.updateStateWordLst(stateWordLst, nextWord)
            state = ''
            for i in range(len(stateWordLst)):
                state += stateWordLst[i] + " "
            state = state.lower()
            currentState = state
            capitalize = nextWord[-1] in self.punctuation
        tweet = tweet.capitalize()
        return tweet

path = '/Users/declanjones/Desktop/TweetProj/Tweet_Data/Corpus/'
files = [fn for fn in os.listdir(path) if fn.endswith('.txt')]
markovChain = MarkovChain(1)
for file in files:
    f = open(path + file, 'rb')
    lines = f.readlines()
    for line in lines:
        markovChain.populateStartingDict(line.lower())
tweet = markovChain.makeTweet()
while tweet == '':
    tweet = markovChain.makeTweet()
#if no arguments given it is a test and tweet is printed to terminal, not tweeted
if len(sys.argv) == 1:
    print tweet
else:
    f = open('/Users/declanjones/Desktop/TweetProj/Tweet_Data/Tweets/tweet.txt', 'wb')
    f.write(tweet)
    f.close()





