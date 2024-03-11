from music21 import *
import os

def extract_chords(stream):
    chords_list = []

    s_chords = stream.chordify()
    k = s_chords.analyze('key')

    for c in s_chords.recurse().getElementsByClass(chord.Chord):
        c_n = c.closedPosition() # force into one octave
        r = roman.romanNumeralFromChord(c_n, k) # self explanatory

        chords_list.append(r.figure) # will append with inversions and accidentals
        # will try without if this leads to bad data

    print("finished song")
    with open('chords.txt', 'a+') as note_file:
        for c in chords_list:
            note_file.write(str(c) + ' ')
        note_file.write('\n')

for f in os.listdir('./mxls')[:10]:
    s = converter.parse('./mxls/' + f.strip())
    extract_chords(s)

