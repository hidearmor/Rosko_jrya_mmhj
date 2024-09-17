import os

# call it in you file like this: 
    # timeNowRaw = datetime.datetime.now()
    # plotsDir = getPlotsDirectory(timeNowRaw, os.getcwd())

# and do this in the import, where  '../../..' is whatever path that leads to repository's root directory:
    # sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
    # from plotslib.plot_utils import getPlotsDirectory

# cwd = current working directory, time is datetime.datetime.now()
def getPlotsDirectory(time, cwd):
    resDir = cwd + '/results/'
    resDateDir = resDir + str(time.date())
    if not (os.path.exists(resDir) & os.path.isdir(resDir)) :
        os.mkdir(resDir)
        if not (os.path.exists(resDateDir + '/') & os.path.isdir(resDateDir + '/')):
                os.mkdir(resDateDir)

    return resDateDir + '/'