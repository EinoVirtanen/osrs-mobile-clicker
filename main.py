# https://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv
# pip install .\opencv_python-4.2.0-cp38-cp38-win32.whl
# pip install pyautogui

from pyautogui import locateOnScreen, click, screenshot, moveTo, scroll
import numpy
import sys
import time
import random
import os
import cv2
from pynput.mouse import Button, Controller

def sleep(preciseSleepTime):
    humanizedSleepTime = 1.0 * preciseSleepTime * random.uniform(0.9, 1.1)
    #print('sleeping for', humanizedSleepTime)
    time.sleep(humanizedSleepTime)

def fail(reason):
    runTime = time.time() - startTime
    if runTime > 60*60:
        runTime = str(int(runTime/60/60)) + ' hours'
    elif runTime > 60:
        runTime = str(int(runTime/60)) + ' minutes'
    else:
        runTime = str(int(runTime)) + ' seconds'
    stats = '\n\nScript ran for ' + runTime + ' and managed to kill ' + str(mobsKilled) + ' Cows\n\n'
    exitReason = stats + 'ERROR: '+ reason
    sys.exit(exitReason)

def getBlueStacksLocation():
    # BlueStacks options: 1600x900 resolution, 320 DPI
    widthShouldBe = 1131
    heightShouldBe = 624

    mainIcon = locateOnScreen('images/BlueStacksMainIcon.png')
    backIcon = locateOnScreen('images/BlueStacksBackIcon.png')
    
    if not (widthShouldBe == backIcon.left - mainIcon.left):
        fail('BlueStacks window has odd width, re-check options and restart the program')
    elif not (heightShouldBe == backIcon.top - mainIcon.top):
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

def clickImage(mobImages, startThreshold, minThreshold, step, clickCenter):
    print('clickImage() called..', end='', flush=True)

    currentThreshold = startThreshold
    while currentThreshold > minThreshold:
        print('.', end='', flush=True)
        #print('finding mob with threshold ==', currentThreshold)

        #print('taking screenshot of the mobBox..')
        mobBoxRegion = (mobBox['topLeft'][0],\
                        mobBox['topLeft'][1],\
                        mobBox['bottomRight'][0] - mobBox['topLeft'][0],\
                        mobBox['bottomRight'][1] - mobBox['topLeft'][1])
        tryScreenshot('tmp/screenshot.png', region=mobBoxRegion)

        mobBoxImage = cv2.imread('tmp/screenshot.png')

        imageNum = 1
        for mobImage in mobImages:
            print('.', end='', flush=True)
            #print('searching for image number', imageNum)
            imageNum = imageNum + 1

            mobWidth = len(mobImage[0])
            mobHeight = len(mobImage)

            res = cv2.matchTemplate(mobBoxImage, mobImage, cv2.TM_CCOEFF_NORMED)
            loc = numpy.where(res > currentThreshold)
            #print('len(loc[0]) ==', len(loc[0]))
            if len(loc[0]) > 0:
                print(imageNum, end='', flush=True)
                #print(loc)
                middleIndex = int(len(loc[0]) / 2)
                #print(middleIndex)
                #tryScreenshot('tmp/possibleMob.png', region=(mobBox['topLeft'][0] + loc[1][middleIndex],\
                #                                          mobBox['topLeft'][1] + loc[0][middleIndex],\
                #                                          mobWidth,\
                #                                          mobHeight))
                possibleMobLocationCenter = (mobBox['topLeft'][0] + loc[1][middleIndex] + int(mobWidth/2),\
                                             mobBox['topLeft'][1] + loc[0][middleIndex] + int(mobHeight/2))

                if clickCenter == True:
                    click(possibleMobLocationCenter)
                else:
                    click(possibleMobLocationCenter[0] + random.randrange(mobWidth),\
                          possibleMobLocationCenter[1] + random.randrange(mobHeight))
                print('')
                return True
        currentThreshold = currentThreshold * step
        #print('mob not found')
    print('')
    return False


def xpIconShowing(xpImage):
    xpIconRegion = (mobBox['topLeft'][0] + 637,\
                    mobBox['topLeft'][1] + 20,\
                    9,\
                    6)
    tryScreenshot('tmp/xpIconRegion.png', region=xpIconRegion)
    xpIconBoxImage = cv2.imread('tmp/xpIconRegion.png')
    res = cv2.matchTemplate(xpIconBoxImage, xpImage, cv2.TM_CCOEFF_NORMED)
    loc = numpy.where(res > 0.9)
    return len(loc[0]) > 0

def setZoom():
    click(blueStacksTopLeftCorner[0] + 900 + random.randrange(10), blueStacksTopLeftCorner[1] + 60 + random.randrange(10))
    sleep(1)
    moveTo(blueStacksTopLeftCorner[0] + 700 + random.randrange(10), blueStacksTopLeftCorner[1] + 500 + random.randrange(10))
    mouse = Controller()
    for i in range(10):
        sleep(0.5)
        mouse.scroll(0, 1)
    print('zoom set')

# todo: send mail

if __name__ == '__main__':
    try:
        mobBox = {}
        cowThresholds = []
        cowTextThresholds = []
        startTime = time.time()
        xpIconLastSeen = time.time()
        mobsKilled = 0
        blueStacksTopLeftCorner = getBlueStacksLocation()

        #setZoom()

        mobBox['topLeft'] = (blueStacksTopLeftCorner[0] + 50,\
                            blueStacksTopLeftCorner[1] + 90)
        mobBox['bottomRight'] = (blueStacksTopLeftCorner[0] + 830,\
                                blueStacksTopLeftCorner[1] + 650)
        swordXpImage = getImages('SwordXpIcon')[0]
        cowImages = getImages('Cow')
        cowTextImage = getImages('AttackCowText')

        # v testing
        while True:
            if xpIconShowing(swordXpImage):
                print('xp bar showing')
            else:
                print('xp bar NOT showing')
            sleep(0.2)
        # ^ testing


        while True:
            timeSinceXpIcon = time.time() - xpIconLastSeen

            if timeSinceXpIcon > 120:
                fail('2 minutes passed since XP icon has been seen')
            
            print(int(timeSinceXpIcon), 'seconds passed since XP icon last seen')

            if clickImage(cowImages, startThreshold=0.7, minThreshold=0.6, step=0.95, clickCenter=True):
            #if clickImage(cowTextImage, startThreshold=0.9, minThreshold=0.8, step=0.99, clickCenter=False):
                #print('waiting for a maximum of 3 seconds for combat to start..')
                waitTicks = 0
                print('waiting for combat to start..', end='', flush=True)
                while not xpIconShowing(swordXpImage) and waitTicks < 20:
                    print('.', end='', flush=True)
                    sleep(0.1)
                    #print("waiting", waitTicks)
                    waitTicks = waitTicks + 1
                print('')
                if waitTicks >= 20:
                    #print('combat did not start in 3 seconds, finding a new mob')
                    pass
                else:
                    print('waiting for combat to end..', end='', flush=True)
                    while xpIconShowing(swordXpImage):
                        xpIconLastSeen = time.time()
                        print('.', end='', flush=True)
                        sleep(0.1)
                    mobsKilled = mobsKilled + 1
                    print('')

    except KeyboardInterrupt:
        fail('keyboard interrupt captured')