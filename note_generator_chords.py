import music21
import random

with open('chord_trigrams.txt', 'r+') as f:
    trigrams_raw = f.read().split('}')

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

def correct_notes_in_key(final_stream, k):
    for n in final_stream.recurse().notes:
        if isinstance(n, music21.chord.Chord):
            for no in n.notes:
                nStep = no.pitch.step
                rightAccidental = k.accidentalByStep(nStep)
                no.pitch.accidental = rightAccidental
                # need to treat chords separately and iterate through notes in one
        else:
            n_step = n.pitch.step
            right_accidental = k.accidentalByStep(n_step)
            n.pitch.accidental = right_accidental

    return final_stream

# helper function used in generate_chord_rh
# given a chord and a key, return that chord but in the key
def correct_chord(chord, k):
    for no in chord.notes:
        nStep = no.pitch.step
        rightAccidental = k.accidentalByStep(nStep)
        no.pitch.accidental = rightAccidental

    return chord

trigrams = parse_input(trigrams_raw)

def generate_chord_rh(key_name, trigrams, length, list_of_roots):
    previous_chords = []

    stream1 = music21.stream.base.Part()
    duration = music21.duration.Duration(1) # 1 is quarter note
    # the stream.base.Part can be added to a stream.base.Score for 2h music

    k = music21.key.Key(key_name)

    chord_1 = tuple(['I', 'V'])

    for i in range(length):
        c1 = trigrams[chord_1]
        while True:
            chord_new = probability(c1)
            c = music21.roman.RomanNumeral(chord_new, k)

            if len(previous_chords) > 1:
                # if a chord appears 2x in a row, make the second one have the next inversion up
                # from the first one
                if previous_chords[-1].scaleDegree == correct_chord(c, k).scaleDegree:
                    # scaleDegree is a bandaid fix because some chords get marked as minor
                    # despite definitely not being minor
                    # will need to replace this logic if I ever decide not to lock chords to a key
                    # because it treats minor/major etc in the same base as the same

                    if previous_chords[-1].inversion() == 0:
                        chord_inverted = chord_new + "63"
                    elif previous_chords[-1].inversion() == 1:
                        chord_inverted = chord_new + "64"
                    else: # inversions higher than 2nd technically exist but I won't use them
                        chord_inverted = chord_new + "53"
                    # disgusting hardcoding because I cannot find an easy way to change a chord's inversion

                    c = music21.roman.RomanNumeral(chord_inverted, k)
                    print(f"found dupe between {previous_chords[-1]} and {correct_chord(c, k)}")

            stream1.append(c)
            previous_chords.append(c)
            break

    for c in stream1:
        # create list_of_roots here instead of having to retype it multiple times above
        # have to append 1 by 1 because it's a function arg
        list_of_roots.append(music21.note.Note(c.root(), duration=c.duration))
        print(c)
    return stream1

def generate_arpeggio_lh(list_of_roots):
    stream2 = music21.stream.base.Part()

    for l in list_of_roots:
        # rewritten to use relative duration of the input note in list_of_roots
        duration = l.duration.augmentOrDiminish(0.25)
        n = music21.note.Note(l.pitch, duration=duration)

        # minus 12 midi pitches moves it down 1 octave
        n1 = music21.note.Note(n.pitch.midi - 12, duration=duration)
        # 4 and 7 are halfstep lengths to make the arpeggio
        n2, n3 = (music21.note.Note(n1.pitch.midi + 4, duration=duration),
                  music21.note.Note(n1.pitch.midi + 7, duration=duration))

        stream2.append(n1)
        stream2.append(n2)
        stream2.append(n3)
        stream2.append(music21.note.Note(n2.pitch, duration=duration))

    return stream2

def generate_song(key, trigrams, length):
    list_of_roots = []
    right_hand = generate_chord_rh(key, trigrams, length, list_of_roots)
    # generates lh based on rh
    left_hand = generate_arpeggio_lh(list_of_roots)

    final_stream = music21.stream.base.Score()
    k = music21.key.Key(key)
    final_stream.insert(0, k) # key signature

    final_stream.append(right_hand)
    final_stream.append(left_hand)

    # force every note to adhere to the key signature
    final_stream = correct_notes_in_key(final_stream, k)
    return final_stream

def main():
    final_stream = generate_song('E-', trigrams, 30)
    final_stream.show()
    final_stream.write('midi', './midis/chord_bases.mid')

if __name__ == "__main__":
    main()
# print(trigrams)