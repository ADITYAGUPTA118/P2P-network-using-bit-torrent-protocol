import os

with open("large_random_file.bin", 'rb') as f1:
    with open("demoFile_downloaded.bin", 'rb') as f2:
        while True:
            c1 = f1.read(1)
            c2 = f2.read(1)
            if c1 != c2:
                 print(False)
            if not c1 and not c2:
                print(True)