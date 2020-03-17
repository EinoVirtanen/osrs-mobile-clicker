import numpy, sys, time, random, os, cv2, ctypes
from pyautogui import locateOnScreen, click, screenshot, moveTo, scroll
from pynput.mouse import Button, Controller


def hibernateWindows():
    os.system('shutdown /h')
    sys.exit('system should hibernate now')


def sleep(preciseSleepTime):
    humanizedSleepTime = 1.0 * preciseSleepTime * random.uniform(0.9, 1.1)
    time.sleep(humanizedSleepTime)


def fail(reason, hibernate=True):
    runTime = time.time() - startTime
    if runTime > 60*60:
        runTime = str(int(runTime/60/60)) + ' hours'
    elif runTime > 60:
        runTime = str(int(runTime/60)) + ' minutes'
    else:
        runTime = str(int(runTime)) + ' seconds'
    stats = '\n\nScript ran for ' + runTime + ' and managed to kill ' + str(mobsKilled) + ' mobs\n\n'
    exitReason = stats + 'ERROR: '+ reason
    
    if hibernate == True:
        print(exitReason)
        print('hibernating in 30 seconds')
        hibernateWindows()
    else:
        sys.exit(exitReason)


def getBlueStacksLocation():
    # BlueStacks options: 1600x900 resolution, 320 DPI
    widthShouldBe = 1131
    heightShouldBe = 624

    mainIcon = locateOnScreen('images/BlueStacksMainIcon.png')
    backIcon = locateOnScreen('images/BlueStacksBackIcon.png')
    
    if not (widthShouldBe == backIcon.left - mainIcon.left):
        fail('BlueStacks window has odd width, re-check options and restart the program', hibernate=False)
    elif not (heightShouldBe == backIcon.top - mainIcon.top):
        fail('BlueStacks window has odd height, re-check options and restart the program', hibernate=False)
    else:
        print('found a properly sized BlueStacks window at', mainIcon.top, mainIcon.left)

    return (mainIcon.left, mainIcon.top)


def getImages(mobName):
    images = []
    for fileName in os.listdir('images'):
        if mobName in fileName:
            images.append(cv2.imread('images/' + fileName))
    if len(images) > 1:
        return images
    else:
        return images[0]


def tryScreenshot(imagePath, region):
    greatSuccess = False
    while not greatSuccess:
        try:
            screenshot(imagePath, region)
            greatSuccess = True
        except:
            print('failed to take screenshot!')


def clickImage(mobImages, threshold, clickCenter):
    print('clickImage() called')

    mobBoxRegion = (mobBox['topLeft'][0],\
                    mobBox['topLeft'][1],\
                    mobBox['bottomRight'][0] - mobBox['topLeft'][0],\
                    mobBox['bottomRight'][1] - mobBox['topLeft'][1])

    tryScreenshot('tmp/screenshot.png', region=mobBoxRegion)
    mobBoxImage = cv2.imread('tmp/screenshot.png')

    imageNum = 1
    random.shuffle(mobImages)
    for mobImage in mobImages:
        if imageNum % 3 == 0:
            tryScreenshot('tmp/screenshot.png', region=mobBoxRegion)
            mobBoxImage = cv2.imread('tmp/screenshot.png')
        
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
            return True
        else:
            sleep(0.1)
            
    return False


def xpIconShowing(xpImage):
    xpIconRegion = (mobBox['topLeft'][0] + 630,\
                    mobBox['topLeft'][1] + 15,\
                    20,\
                    20)
    tryScreenshot('tmp/xpIconRegion.png', region=xpIconRegion)
    xpIconBoxImage = cv2.imread('tmp/xpIconRegion.png')
    res = cv2.matchTemplate(xpIconBoxImage, xpImage, cv2.TM_CCOEFF_NORMED)
    loc = numpy.where(res > 0.9)
    return len(loc[0]) > 0


def setAngle():
    print('setZoom()')
    click(blueStacksTopLeftCorner[0] + 900 + random.randrange(10), blueStacksTopLeftCorner[1] + 60 + random.randrange(10))
    sleep(1)
    moveTo(blueStacksTopLeftCorner[0] + 700 + random.randrange(10), blueStacksTopLeftCorner[1] + 500 + random.randrange(10))
    mouse = Controller()
    for i in range(10):
        sleep(0.5)
        mouse.scroll(0, 1)


if __name__ == '__main__':
    try:
        mobBox = {}
        mobsKilled = 0
        blueStacksTopLeftCorner = getBlueStacksLocation()
        xpImage = getImages('SwordHandleXpIcon')
        mobBox['topLeft'] = (blueStacksTopLeftCorner[0] + 50,\
                            blueStacksTopLeftCorner[1] + 90)
        mobBox['bottomRight'] = (blueStacksTopLeftCorner[0] + 830,\
                                blueStacksTopLeftCorner[1] + 650)
        click(blueStacksTopLeftCorner[0], blueStacksTopLeftCorner[1])
        sleep(1)
        setAngle()
        mobImages = getImages('Goblin')
        mobClicksWithoutCombat = 0
        startTime = time.time()
        while True:
            if mobClicksWithoutCombat > 10:
                fail('10 clicks without combat, exiting!')
            if not xpIconShowing(xpImage):
                # TODO: jos ukko joutuu oven taakse, nosta thresholdia 0.01
                if clickImage(mobImages, threshold=0.7, clickCenter=True):
                    print('attempted to click a mob', mobClicksWithoutCombat)
                    mobClicksWithoutCombat = mobClicksWithoutCombat + 1
                    waitUntilCombat = 2.5
                    while not xpIconShowing(xpImage) and waitUntilCombat > 0:
                        print('waiting for combat to start', round(waitUntilCombat, 1))
                        sleep(0.1)
                        waitUntilCombat = waitUntilCombat - 0.1
            else:
                print('waiting for combat to end')
                sleep(0.1)
                mobClicksWithoutCombat = 0
                    
    except KeyboardInterrupt:
        fail('keyboardinterrupt caught', hibernate=False)
    
    except:
        fail('something other than keyboardinterrupt happened')