#helper file to create lilypond files from mingus

def to_LilyPond_file(ly_string, filename):
    ly_string = '\\version "2.10.33"\n' + ly_string 
    filename = filename + ".ly"
    try:
        f = open(filename,'w+')
        f.write(ly_string)
        f.close()
    except:
        return False
    return True