import pyvjoy
import time

print('You have 3 seconds to tab into the game...')
time.sleep(3)


def resetPlayer(p):
    p.data.wAxisX = 16383
    p.data.wAxisY = 16383
    p.data.wAxisYRot = 16383
    p.data.wAxisXRot = 16383
    p.data.wAxisZ = 0
    p.data.wAxisZRot = 0
    p.data.lButtons = 0
    p.update()


for i in range(1, 5):
    player = pyvjoy.VJoyDevice(i)
    player.data.lButtons = 128
    player.update()
    time.sleep(1)
    resetPlayer(player)
    print(str(i))
