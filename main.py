# https://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv
# pip install .\opencv_python-4.2.0-cp38-cp38-win32.whl
# pip install pyautogui

# todo: kaikki etäisyydet relatiivisiks

from pyautogui import locateOnScreen, click, screenshot, moveTo
import numpy
import sys
import time
import random
import os
import cv2


def sleep(preciseSleepTime):
    humanizedSleepTime = 1.0 * preciseSleepTime * random.uniform(0.9, 1.1)
    #print('sleeping for', humanizedSleepTime)
    time.sleep(humanizedSleepTime)

def logOut():
    print('logOut() called..')
    click(blueStacksTopLeftCorner[0]+1070+random.randrange(15),\
          blueStacksTopLeftCorner[1]+600+random.randrange(15))
    sleep(1)
    click(blueStacksTopLeftCorner[0]+855+random.randrange(1000-855),\
          blueStacksTopLeftCorner[1]+570+random.randrange(600-570))

def hibernateComputer():
    print('hibernateComputer() called..')
    click(5, 5)
    sleep(3)
    click(5, 800, button='right')
    sleep(3)
    click(10, 650)
    sleep(1)
    click(10, 650)

def fail(reason, onlyPrintStats=False):
    runTime = time.time() - startTime
    if runTime > 60*60:
        runTime = str(int(runTime/60/60)) + ' hours'
    elif runTime > 60:
        runTime = str(int(runTime/60)) + ' minutes'
    else:
        runTime = str(int(runTime)) + ' seconds'
    stats = '\n\nScript ran for ' + runTime + ' and managed to kill ' + str(mobsKilled) + ' Cows\n\n'

    if not onlyPrintStats:
        logOut()
        hibernateComputer()

    exitReason = stats + 'ERROR: '+ reason
    sys.exit(exitReason)

def getBlueStacksLocation():
    # BlueStacks options: 1600x900 resolution, 320 DPI
    widthShouldBe = 1131
    heightShouldBe = 624

    mainIcon = locateOnScreen('images/BlueStacksMainIcon.png')
    backIcon = locateOnScreen('images/BlueStacksBackIcon.png')

    print(type(mainIcon))
    print(mainIcon)
    
    if not (widthShouldBe == backIcon.left - mainIcon.left):
        print(widthShouldBe, "!=", backIcon.left - mainIcon.left)
        fail('BlueStacks window has odd width, re-check options and restart the program')
    elif not (heightShouldBe == backIcon.top - mainIcon.top):
        print(heightShouldBe, "!=", backIcon.top - mainIcon.top)
        fail('BlueStacks window has odd height, re-check options and restart the program')
    else:
        print('found a properly sized BlueStacks window at', mainIcon.top, mainIcon.left)

    return (mainIcon.left, mainIcon.top)

def getImages(mobName):
    #print('reading images of mob:', mobName, '..')
    images = []
    for fileName in os.listdir('images'):
        if mobName in fileName:
            images.append(cv2.imread('images/' + fileName))
    #print('read', len(images), 'images of', mobName)
    return images

def tryScreenshot(imagePath, region):
    greatSuccess = False
    while not greatSuccess:
        try:
            screenshot(imagePath, region)
            greatSuccess = True
        except:
            pass

def clickImage(mobImages, threshold, clickCenter):
    print('clickImage() called..', end='', flush=True)

    mobBoxRegion = (mobBox['topLeft'][0],\
                    mobBox['topLeft'][1],\
                    mobBox['bottomRight'][0] - mobBox['topLeft'][0],\
                    mobBox['bottomRight'][1] - mobBox['topLeft'][1])
    print('.', end='', flush=True)

    tryScreenshot('tmp/screenshot.png', region=mobBoxRegion)
    mobBoxImage = cv2.imread('tmp/screenshot.png')

    imageNum = 1
    for mobImage in mobImages:
        if imageNum % 3 == 0:
            tryScreenshot('tmp/screenshot.png', region=mobBoxRegion)
            mobBoxImage = cv2.imread('tmp/screenshot.png')
            print('s', end='', flush=True)
        else:
            print('.', end='', flush=True)
    
        
        imageNum = imageNum + 1

        mobWidth = len(mobImage[0])
        mobHeight = len(mobImage)

        res = cv2.matchTemplate(mobBoxImage, mobImage, cv2.TM_CCOEFF_NORMED)
        loc = numpy.where(res > threshold)
        
        if len(loc[0]) > 0:
            middleIndex = int(len(loc[0]) / 2)
            possibleMobLocationCenter = (mobBox['topLeft'][0] + loc[1][middleIndex] + int(mobWidth/2),\
                                            mobBox['topLeft'][1] + loc[0][middleIndex] + int(mobHeight/2))

            if clickCenter == True:
                click(possibleMobLocationCenter)
            else:
                click(possibleMobLocationCenter[0] + random.randrange(mobWidth),\
                        possibleMobLocationCenter[1] + random.randrange(mobHeight))
            print('')
            return True
            
    print('')
    return False


def xpIconShowing(xpImage):
    xpIconRegion = (mobBox['topLeft'][0] + 600,\
                    mobBox['topLeft'][1] - 30,\
                    100,\
                    100)
    tryScreenshot('tmp/xpIconRegion.png', region=xpIconRegion)
    xpIconBoxImage = cv2.imread('tmp/xpIconRegion.png')
    res = cv2.matchTemplate(xpIconBoxImage, xpImage, cv2.TM_CCOEFF_NORMED)
    loc = numpy.where(res > 0.95)
    return len(loc[0]) > 0
    

def runToMiddleOfField(treeImage):
    minimapRegion = (mobBox['topLeft'][0] + 860,\
                    mobBox['topLeft'][1] - 35,\
                    190,\
                    190)
    tryScreenshot('tmp/minimapRegion.png', region=minimapRegion)
    minimapBoxImage = cv2.imread('tmp/minimapRegion.png')
    res = cv2.matchTemplate(minimapBoxImage, treeImage, cv2.TM_CCOEFF_NORMED)
    loc = numpy.where(res > 0.80)
    if len(loc[0] > 0):
        click(minimapRegion[0] + loc[1][0] + 15,\
              minimapRegion[1] + loc[0][0] + 110)
    else:
        fail('recovery attempt failed')


if __name__ == '__main__':
    try:
        timeout = 1

        mobBox = {}
        cowThresholds = []
        cowTextThresholds = []
        startTime = time.time()
        xpIconLastSeen = time.time()
        mobsKilled = 0
        recoveryAttempted = False

        blueStacksTopLeftCorner = getBlueStacksLocation()

        click(blueStacksTopLeftCorner[0], blueStacksTopLeftCorner[1])
        mobBox['topLeft'] = (blueStacksTopLeftCorner[0] + 50,\
                            blueStacksTopLeftCorner[1] + 90)
        mobBox['bottomRight'] = (blueStacksTopLeftCorner[0] + 830,\
                                blueStacksTopLeftCorner[1] + 650)

        treeImage = getImages('MinimapTree')[0]
        cowImages = getImages('Cow') #WolfMinotaur
        cowTextImage = getImages('AttackCowText')

        #xpImage = getImages('StrXpIcon')
        xpImage = getImages('SwordXpIcon')[0]

        while True:
            timeSinceXpIcon = time.time() - xpIconLastSeen

            if timeSinceXpIcon > (timeout * 60):
                if recoveryAttempted == True:
                    fail(timeout, 'minute(s) passed since XP icon has been seen')
                else:
                    runToMiddleOfField(treeImage)
                    recoveryAttempted = True

            
            print(int(timeSinceXpIcon), 'seconds passed since XP icon last seen')

            if clickImage(cowImages, threshold=0.57, clickCenter=True):
                waitTicks = 0
                print('waiting for combat to start..', end='', flush=True)
                while not xpIconShowing(xpImage) and waitTicks < 20:
                    print('.', end='', flush=True)
                    sleep(0.1)
                    waitTicks = waitTicks + 1
                print('')
                if waitTicks >= 20:
                    pass
                else:
                    print('waiting for combat to end..', end='', flush=True)
                    while xpIconShowing(xpImage):
                        xpIconLastSeen = time.time()
                        recoveryAttempted = False
                        print('.', end='', flush=True)
                        sleep(0.1)
                    mobsKilled = mobsKilled + 1
                    print('')

    except:
        fail('some failure', onlyPrintStats=True)