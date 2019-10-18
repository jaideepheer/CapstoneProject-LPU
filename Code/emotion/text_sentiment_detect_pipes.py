from pipedefs.core_pipes import PushPipe
from utils.typedefs import TextSentimentVader
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
class SentimentExtractorVaderPipe(PushPipe[str, TextSentimentVader]):
    def __init__(self, postProcessCallback=None):
        super().__init__(postProcessCallback=postProcessCallback)
        self.analyzer = SentimentIntensityAnalyzer()
    def process(self, data, passThrough):
        data = self.analyzer.polarity_scores(data)
        return TextSentimentVader(data['pos'], data['neg'], data['neu'], data['compound'])
    def __del__(self):
        del self.analyzer