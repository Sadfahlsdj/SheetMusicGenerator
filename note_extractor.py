import music21
import os

# duration is measured in multiples of quarter notes
# documentation: https://web.mit.edu/music21/doc/usersGuide/index.html


s = music21.converter.parse('./mxls/pdf12517.mvt27.mxl')
# test.plot('horizontalbar')

# test.show('text')
# test.show()

"""for thisNote in test.recurse().getElementsByClass(music21.note.Note):
    print(thisNote, thisNote.offset)"""
# above code block will skip chords

def extract_notes(music_stream):
    note_list = []
    for tN in music_stream.recurse().notes: # .recurse() is needed, idk why
        # .notes is equal to getting only notes & chords
        if isinstance(tN, music21.chord.Chord):
            # print('found chord')
            for p in tN.pitches:
                # print(p)
                note_list.append(p)
                # appends chords as arpeggios
        else:
            # print([tN.step, tN.octave, tN.duration.quarterLength])
            # print(tN.pitch)
            note_list.append(tN.pitch)
    print('finished song')
    with open('notes.txt', 'a+') as note_file:
        for n in note_list:
            note_file.write(str(n) + ' ')
        note_file.write('\n')

for f in os.listdir('./mxls'):
    s = music21.converter.parse('./mxls/' + f.strip())
    extract_notes(s)



