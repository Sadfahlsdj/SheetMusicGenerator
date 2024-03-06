import music21
import random
import pathlib

# required for music21 to recognize my musescore download
music21.environment.set('musescoreDirectPNGPath',
                        pathlib.PosixPath('/Applications/MuseScore 4.app/Contents/MacOS/mscore'))
music21.environment.set('musicxmlPath',
                        pathlib.PosixPath('/Applications/MuseScore 4.app/Contents/MacOS/mscore'))

with open('trigrams_saved.txt', 'r+') as f:
    trigrams_raw = f.read().split('}')

# input is saved in trigrams_saved as just raw to_string of dicts
# it needs some editing to be usable again
# when i was parsing into trigrams i did not have the foresight to save to json instead
def parse_input(trigrams_raw):
    trigrams = {}
    for t in trigrams_raw:
        t = t.strip()
        parsed = (t.replace('{', '').replace("'", '').replace(',', '')
            .replace('(', '').replace(')', '').replace(':', '')
                  .replace('"', '').split(' '))
        if trigrams_raw.index(t) > 0:
            parsed.pop(0)
            # after the first dict is parsed, subsequent ones will have a '' as the first element
            # i could fix the underlying issue, OR
        try:
            key, values = tuple([parsed[0], parsed[1]]), parsed[2:]
            values_dict = {}
            for i in range(0, len(values), 2):
                try:
                    values_dict.update({values[i]: values[i + 1]})
                except:
                    print("odd number of elements here for some reason?? continue")
            trigrams.update({key: values_dict})
        except:
            print(f"this issue is probably because parsed is empty; parsed = {parsed}")
    return trigrams

trigrams = parse_input(trigrams_raw)
# print(trigrams.keys())

# helper function for key_given_number
# given a piano key it will return the range of numbers that it corresponds to
def running_total(keys, values, key):
    index = keys.index(key)
    preceding_values = values[:index + 1]
    s, previous_sum = sum(preceding_values), sum(preceding_values) - int(values[index])
    return tuple([s, previous_sum])
# helper function for probability, given a number it returns the key
# uses running_total
def key_given_number(keys, values, number) -> str:
    # given keys, values, input random number, return the string of a piano key
    # keys and values should be the same size so the proceeding part is allowed

    s, previous_sum = 0, 0

    for k in keys:
        end, start = running_total(keys, values, k)[0], running_total(keys, values, k)[1]
        # print(f"{start} {end}")
        if number >= start and number <= end:
            return k
# given a trigram, generates random number and returns random key
def probability(trigram):
    trigram_keys = [k for k in trigram.keys()]
    trigram_numbers = [int(v) for v in trigram.values()]
    # print(trigram_numbers)
    s = sum(trigram_numbers)
    number = random.randint(0, s)
    # print(number)

    return key_given_number(trigram_keys, trigram_numbers, number)

# print(probability(trigrams[tuple(['A3', 'C4'])]))

def generate_music(trigrams, length, start1='C4', start2='F4'):
    stream1 = music21.stream.base.Part()
    sixteenth = music21.duration.Duration(1)
    # 1 is quarter, this controls duration of all notes in music

    keys_input = tuple([start1, start2]) # hardcoded for now, maybe randomize later
    for k in keys_input:
        stream1.append(music21.note.Note(k, duration=sixteenth))

    for i in range(length):
        t = trigrams[keys_input]

        # next section will be hardcoding to force it to follow a key
        # comment out or delete at will
        # for base behavior, just leave next_key = probability(t)

        c_notes = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        while True:
            next_key = probability(t)
            raw_note = next_key[:len(next_key) - 1]
            prev_note, curr_note = music21.pitch.Pitch(keys_input[1]), music21.pitch.Pitch(next_key)
            difference = abs(prev_note.midi - curr_note.midi)
            # 13 pitches in an octave, large jumps sound like ass so i'm banning them
            if raw_note in c_notes and difference <= 15:
                break

        stream1.append(music21.note.Note(next_key, duration=sixteenth))
        keys_input = tuple([keys_input[1], next_key])

    return stream1

def generate_chord(trigrams, length, list_of_roots):
    stream1 = music21.stream.base.Part()
    duration = music21.duration.Duration(1)
    # the stream.base.Part can be added to a stream.base.Score for 2h music
    notes_1, notes_2, notes_3 = tuple(['C4', 'G4']), tuple(['E4', 'C5']), tuple(['G4', 'E5'])

    for i in range(length):
        # maintain 3 notes at one time to make a chord out of them later
        t1, t2, t3 = trigrams[notes_1], trigrams[notes_2], trigrams[notes_3]
        while True:
            key1, key2, key3 = probability(t1), probability(t2), probability(t3)
            pitch1, pitch2, pitch3 = key1[:len(key1) - 1], key2[:len(key2) - 1], key3[:len(key3) - 1]
            c = music21.chord.Chord([pitch1, pitch2, pitch3], duration=duration).closedPosition()

            c_major_notes = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
            bflat_major_notes = ['A', 'B-', 'C', 'D', 'E-', 'F', 'G']
            csharp_major_notes = ['A#', 'C', 'C#', 'D#', 'F', 'F#', 'G#']

            current_key = csharp_major_notes
            # if any of these conditions trigger, it will regenerate
            if pitch1 not in current_key or pitch2 not in current_key or pitch3 not in current_key or not c.isMajorTriad:
                continue # still locking to one key at once
            midis = [p.midi for p in c.pitches]
            midis.sort()

            # next part is to force each chord to have at least one interval above size 2
            # lot of chords ended up being 3 consecutive notes and they sound bad
            if len(midis) < 3:
                if len(midis) == 2:
                    if abs(midis[1] - midis[0]) > 2:
                        stream1.append(c)
                        list_of_roots.append(c.root())
                        break
            else:
                if abs(midis[1] - midis[0]) > 2 or abs(midis[2] - midis[1]) > 2:
                    stream1.append(c)
                    list_of_roots.append(c.root())
                    break

    return stream1

def generate_accompaniment(list_of_roots):
    stream2 = music21.stream.base.Part()
    duration = music21.duration.Duration(0.25)
    for l in list_of_roots:
        # print(l)
        n1 = music21.note.Note(l, duration=duration)
        # below are hardcoded halfstep lengths for major triads for accompaniment
        n2, n3 = (music21.note.Note(n1.pitch.midi + 4, duration=duration),
                  music21.note.Note(n1.pitch.midi + 7, duration=duration))
        stream2.append(n1)
        stream2.append(n2)
        stream2.append(n3)
        stream2.append(music21.note.Note(n2.pitch, duration=duration))
    return stream2
list_of_roots = []


right_hand = generate_chord(trigrams, 50, list_of_roots)
left_hand = generate_accompaniment(list_of_roots)


final_stream = music21.stream.base.Score()
ks = music21.key.KeySignature(7)
final_stream.insert(0, ks)
final_stream.append(right_hand)
final_stream.append(left_hand)

seed = 601
random.seed = seed
# a.show()
final_stream.show()
filename = './midis/' + str(seed) + '.mid'
# a.write('midi', filename)
right_hand.write('midi', filename)
"""a = generate_music(trigrams, 30)
print(a)"""