from nltk import trigrams
import json

with open('chord_bases_1.txt', 'r+') as f:
    # chord_bases_1 is just progress after one day of parsing
    # replace this file later
    lines = [l.strip().split(' ') for l in f.readlines()]

trigrams_count = {}

for line in lines:
    grams = trigrams(line)
    for gram in grams:
        key, value = gram[0:2], gram[2].strip()
        if key in trigrams_count.keys():
            # trigrams_count[key][1] += 1
            inner_dict = trigrams_count[key]
            if value in inner_dict.keys():
                trigrams_count[key][value] += 1
            else:
                trigrams_count[key][value] = 1
        else:
            trigrams_count[key] = {value: 1}
    print(f"finished line {lines.index(line)}")

# print(trigrams_count)
with open('chord_trigrams.txt', 'w+') as f:
    f.write(str(trigrams_count))