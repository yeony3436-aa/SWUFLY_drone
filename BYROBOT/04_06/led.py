from time import sleep
from CodingDrone.drone import *
from CodingDrone.protocol import *

PORT = "COM3"

if __name__ == '__main__':
    drone = Drone()

    try:
        ok = drone.open(PORT)
        if not ok:
            raise RuntimeError(f"포트 열기 실패: {PORT}")

        sleep(1)

        print("BodyHold cyan")
        drone.sendLightModeColor(LightModeDrone.BodyHold, 200, 0, 200, 200)
        sleep(2)

        print("BodyDimming blue")
        drone.sendLightModeColor(LightModeDrone.BodyDimming, 3, 0, 0, 200)
        sleep(3)

        print("BodyDimming magenta")
        drone.sendLightEventColor(LightModeDrone.BodyDimming, 3, 3, 200, 0, 200)
        sleep(3)

        drone.sendLightManual(DeviceType.Drone, 0xFF, 0)
        sleep(1)

    finally:
        drone.close()