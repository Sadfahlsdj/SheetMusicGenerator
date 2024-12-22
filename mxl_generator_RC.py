import os
import subprocess
import sys
from threading import Thread, Lock

# note - "why is there all this about weirdly named txt files as input"
# this was run on 10 different scripts and I wanted a way to automate the input index
# so I made 10 txt files to store those values, CLI is used to tell current program which index it is
# other note: the terminal commands here are meant to run on a linux system

mutex = Lock() # needed to avoid race condition

program_index = sys.argv[1] # tells the program what txt file to look in for the start index
txt_file_name = 'mxl_index' + program_index + '.txt'
with open(txt_file_name, 'r') as f:
    s = int(f.read().strip()) # file should only contain a singular numeric value
    start = s

end = int(sys.argv[2]) # end index is given by cmd line arguments

# research cluster
l = os.listdir('/path/to/pdfs')[start:end] # using this one as the list that tells me what index the current file is overall
q = os.listdir('/path/to/pdfs')[start:end] # using this one as the queue, pop filenames from it to feed into audiveris
# windows
# l = os.listdir('./pdfs_sample')

audiveris_dir = '/path/to/audiveris/Audiveris-5.3.1/' # not actually needed anymore I don't think
# os.chdir(audiveris_dir)

def pdf_to_mxl(q, l):
    while(1):
        if len(q) > 0:
            with mutex: # pop from queue with mutex to avoid race condition
                filename = q.pop(0)
                index = l.index(filename) # records index of current file so it can be recorded in txt file for future iterations to know what the start index is
            p = subprocess.Popen(['java', '-cp', '/path/to/audiveris/Audiveris-5.3.1/lib/*', 'Audiveris', '-batch',
                              '-output', '/path/to/mxls/', '-export',
                              '--', '/path/to/pdfs/' + filename])
            # runs audiveris with all the command line arguments
            p.wait() # waits for last audiveris process in this thread to finish before starting a new one

            txt_path = '/path/to/project_folder/' + txt_file_name
            with mutex:
                with open(txt_path, 'w+') as f:
                    f.write(str(index)) # use mutex to avoid race condition; write most recent pdf index into the txt
        else:
            return # if this subsection of the list of pdfs is empty, just end early

def main():
    for i in range(20):
        t = Thread(target=pdf_to_mxl, args=(q, l)) # spawns 20 threads each constantly running audiveris
        t.start()

if __name__ == '__main__':
    main()

