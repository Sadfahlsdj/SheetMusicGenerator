from maintest2 import *
import LinkGenerator

def main():
    permlinks = LinkGenerator.get_permlinks()
    open('pdflinks.txt', 'w').close()  # i use append so clear file on each iteration
    warnings.filterwarnings("ignore") # LIVING ON A PRAYER


    i = 5000

    while i < len(permlinks):
        threads = 10 # higher than 10 gets banned
        cooldown = 20 # lower than 20 gets banned
        print(f"trying with starting i as {i}")
        test = Test(i, i + threads, permlinks) # this is the function from maintest2.py
        succeeded = test.a()  # returns true if it worked, false if it didn't

        i += threads
        if succeeded:
            print(f"succeeded, forcing {cooldown} sec timeout")
        else:
            print(f"something failed, moving on to the next bunch after {cooldown} seconds")
        sleep(cooldown)

if __name__ == "__main__":
    main()