import music21

# duration is measured in multiples of quarter notes
# documentation: https://web.mit.edu/music21/doc/usersGuide/index.html


s = music21.converter.parse('./mxls/pdf0.mvt1.mxl')
test = s
# test.plot('horizontalbar')

# test.show('text')
# test.show()

"""for thisNote in test.recurse().getElementsByClass(music21.note.Note):
    print(thisNote, thisNote.offset)"""
# above code block will skip chords

for tN in test.recurse().notes: # .recurse() is needed, idk why
    # .notes is equal to getting only notes & chords
    if isinstance(tN, music21.chord.Chord):
        for p in tN.pitches:
            print(f"chord pitch: {p}")
    else:
        # print([tN.step, tN.octave, tN.duration.quarterLength])
        print(tN.pitch)



