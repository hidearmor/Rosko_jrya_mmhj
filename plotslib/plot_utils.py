import os
import sys
import datetime

# call it in you file like this: 
    # plotsDir, timeNow = getPlotsDirectory(os.getcwd())

# save files like this (look at the string params):
    # plt.savefig("%s%s_%s_dram.pdf" % (plotsDir, dateStr, fname) , bbox_inches='tight')

# and do this in the import, where  '../../..' is whatever path that leads to repository's root directory:
    # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    # from plotslib.plot_utils import getPlotsDirectory

# cwd = current working directory

# created directories for results if they dont exists
# returns: 1) directory for files as string 2) time 
def getPlotsDirectory(cwd):
    time = datetime.datetime.now()
    dir, dateStr = directoriesFromTime(time, cwd)

    return dir, dateStr

def directoriesFromTime(time, cwd):
    resDir = cwd + '/results/'
    resDateDir = resDir + str(time.date())
    if not (os.path.exists(resDir) & os.path.isdir(resDir)) :
        os.mkdir(resDir)
    if not (os.path.exists(resDateDir + '/') & os.path.isdir(resDateDir + '/')):
            os.mkdir(resDateDir)
    
    dateStr = str(time.date()) + '_' + str(time.hour) + '' + str(time.minute)

    return resDateDir + '/', dateStr

# fro running with shell scripts
def main(function_name, param):
    if function_name == "getPlotsDirectory":
        path, time = getPlotsDirectory(param)
        print(path)
        print(time)
    else:
        print(f"Function '{function_name}' not found.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python_script.py function_name param")
        sys.exit(1)
    
    function_name = sys.argv[1]
    param = sys.argv[2]
    main(function_name, param)