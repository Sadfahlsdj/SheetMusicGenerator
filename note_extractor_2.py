from music21 import *

s_chords = converter.parse('./mxls/pdf10013.mvt3.mxl').chordify()
k = s_chords.analyze('key')

key_raw = str(k).split(' ')[0]
print(key_raw)

# print(k)
s_chords_new = stream.Stream()

for c in s_chords.recurse().getElementsByClass(chord.Chord):
    c_n = c.closedPosition()
    s_chords_new.append(c_n)
    r = roman.romanNumeralFromChord(c_n, k)
    print(r.figure)

s_chords_new.show()