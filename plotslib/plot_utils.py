import os
import datetime

# cwd = current working directory
def getPlotsDirectory(time, cwd):
    resDir = cwd + '/results/'
    resDateDir = resDir + str(time.date())
    if not (os.path.exists(resDir) & os.path.isdir(resDir)) :
        os.mkdir(resDir)
        if not (os.path.exists(resDateDir + '/') & os.path.isdir(resDateDir + '/')):
                os.mkdir(resDateDir)

    return resDateDir + '/'