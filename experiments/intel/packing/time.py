import datetime
import os

# now = datetime.datetime.now()

# print(now.month)
# print(now.day)
# print(now.hour)
# print(now.minute)

nowRaw = datetime.datetime.now()
date = '' + str(nowRaw.date()) + '_' + str(nowRaw.hour) + '-' + str(nowRaw.minute)
print(date)

print(os.path.exists('./jonas/'), os.path.isdir('./jonas/'))
datePath = './jonas/' + str(nowRaw.date())
print(os.path.exists(datePath + '/'), os.path.isdir(datePath + '/'))
print('')

if not (os.path.exists('./jonas/') & os.path.isdir('./jonas/')) :
    os.mkdir('./jonas')
    datePath = './jonas/' + str(nowRaw.date())
    if not (os.path.exists(datePath + '/') & os.path.isdir(datePath + '/')):
            os.mkdir(datePath)

print(os.path.exists('./jonas/'), os.path.isdir('./jonas/'))
datePath = './jonas/' + str(nowRaw.date())
print(os.path.exists(datePath + '/'), os.path.isdir(datePath + '/'))
print('')