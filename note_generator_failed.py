import random
from typing import List
import music21
import pathlib

# FAILED EXPERIMENT
# TRIED BEING LAZY AND COPYING SCHOOL PROJECT CODE FOR NGRAM GENERATION
# DIDN'T WORK XDD

music21.environment.set('musescoreDirectPNGPath',
                        pathlib.PosixPath('/Applications/MuseScore 4.app/Contents/MacOS/mscore'))
music21.environment.set('musicxmlPath',
                        pathlib.PosixPath('/Applications/MuseScore 4.app/Contents/MacOS/mscore'))
def process(text: str) -> List[str]:
    """explanation - format of processed_words column in parsed_song2.csv
    is hard to work with for ngrams, so we are going again from the initial lyrics
    this will make more realistic lyrics because it will have caps and punctuation
    caps largely are at the start of sentences so this is not an issue
    """
    # basic reprocessing
    t = text.strip().split()
    return t
def get_ngrams(n: int, tokens: list):
  """
  n is the n in ngrams to generate
  tokens is modified list of words
  returns lists of tuples
  """
  tokens = (n - 1) * ['<START>'] + tokens
  l = [(tuple([tokens[i - p - 1] for p in reversed(range(n - 1))]),
        tokens[i]) for i in range(n - 1, len(tokens))]
  return l

class NgramModel(object):
  def __init__(self, n):
    self.n = n # n in ngrams

    # dictionary for list of candidate words given previous ones
    self.context = {}

    # keeps track of how many times ngram has appeared in the text before
    self.ngram_counter = {}

  def update(self, sentence: str) -> None:
    """
    updates ngrams given input sentence
    """
    n = self.n
    ngrams = get_ngrams(n, process(sentence)) # calls function from before
    for ngram in ngrams:
      if ngram in self.ngram_counter:
        self.ngram_counter[ngram] += 1.0
        # it exists in the dict? add 1 to the count
      else:
        self.ngram_counter[ngram] = 1.0
        # doesn't exist in the dict? create it with count 1

      prev_words, target_word = ngram
      if prev_words in self.context:
        self.context[prev_words].append(target_word)
        # exists? append target word
      else:
        self.context[prev_words] = [target_word]
        # doesn't exist? add target word, in a list so it can be appended to later

  def prob(self, context, token):
    """
    conditional probability function
    """
    try:
      count_of_token = self.ngram_counter[(context, token)]
      count_of_context = float(len(self.context[context]))
      result = count_of_token / count_of_context

      # conditional probability that a word (token) will be the next one chosen
      # given preceding word(s) (context)

    except KeyError:
      """
      catch-all in case the context or token do not exist
      result of 0 means the proceeding word will not be returned
      """
      result = 0.0
    return result

  def random_token(self, context):
    """
    using prob function that we just defined
    given a context semi-randomly choose the next word
    """
    r = random.random()
    map_to_probs = {}
    token_of_interest = self.context[context]
    for token in token_of_interest:
      map_to_probs[token] = self.prob(context, token)

    summ = 0
    for token in sorted(map_to_probs):
      summ += map_to_probs[token]
      if summ > r:
        return token

  def generate_text(self, token_count: int):
    """
    token_count is the number of words to generate
    """
    n = self.n # (n)gram count
    context_queue = (n - 1) * ['<START>'] # random starting word
    result = [] # array to return
    for _ in range(token_count):
      obj = self.random_token(tuple(context_queue))
      # refers to random starting word
      result.append(obj)
      if n > 1:
        context_queue.pop(0)
        if obj == '.':
          # if period encountered, treat as end of sentence
          # and restart again, choosing a random word
          context_queue = (n - 1) * ['<START>']
        else:
          context_queue.append(obj) # normal behavior of just continuing
    return ' '.join(result)

def create_ngram_model(n, words):
  m = NgramModel(n)
  for sentence in words:
    m.update(sentence) # generates the ngrams based on the starting input
  return m

with open('notes.txt', 'r+') as f:
    notes_list = f.readlines()

print('finished reading notes (lol)')
def generate_ngram_artist(length, ngram_count):

  # words = df['processed_words'].tolist()
  words = notes_list[:20000]
  print("read in words list")

  m = create_ngram_model(ngram_count, words)
  # random.seed(10)

  print(f'{"=" * 50}\nGenerated notes:')
  print(m.generate_text(length))
  print(f'{"=" * 50}')

  return m.generate_text(length).strip()

pitch_list = generate_ngram_artist(60, 3).split(' ')
stream1 = music21.stream.Stream()
for p in pitch_list:
    stream1.append(music21.note.Note(p))

stream1.show()