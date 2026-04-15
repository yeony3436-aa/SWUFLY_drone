# altitude_stair_mission.py
from time import sleep
from CodingDrone.drone import *
from CodingDrone.protocol import *
import keyboard
import sys

PORT = "COM3"

drone = Drone()


def set_led(r, g, b):
    drone.sendLightModeColor(LightModeDrone.BodyHold, 200, r, g, b)
    sleep(0.2)


def led_off():
    drone.sendLightManual(DeviceType.Drone, 0xFF, 0)
    sleep(0.2)


def emergency_land():
    print("[EMERGENCY] 착륙")
    try:
        set_led(255, 0, 0)
        drone.sendControlWhile(0, 0, 0, 0, 300)
        sleep(0.2)
        drone.sendLanding()
        sleep(3)
        led_off()
    finally:
        drone.close()
    sys.exit(0)


def check_emergency():
    if keyboard.is_pressed("space"):
        emergency_land()


def hover(sec):
    loops = int(sec / 0.12)
    for _ in range(loops):
        check_emergency()
        drone.sendControlWhile(0, 0, 0, 0, 100)
        sleep(0.03)
        sleep(0.09)


def move_z(label, z, speed=0.20, settle=2.5):
    check_emergency()
    print(f"{label}: z={z}")
    drone.sendControlPosition(0.0, 0.0, z, speed, 0, 30)
    hover(settle)


if __name__ == "__main__":
    try:
        ok = drone.open(PORT)
        if not ok:
            raise RuntimeError(f"포트 열기 실패: {PORT}")
        sleep(1.0)

        drone.sendLostConnection(1000, 1500, 0)
        sleep(0.2)

        drone.sendModeControlFlight(ModeControlFlight.Position)
        sleep(0.2)

        set_led(0, 255, 0)
        print("연결 완료 - Space: 비상착륙")

        print("TakeOff")
        set_led(0, 200, 255)
        drone.sendTakeOff()
        sleep(4)

        hover(1.5)

        # 1단 상승
        set_led(0, 0, 255)
        move_z("Step up 1", 0.15, speed=0.18, settle=2.3)

        # 유지
        set_led(255, 0, 255)
        hover(2.0)

        # 2단 상승
        set_led(0, 0, 255)
        move_z("Step up 2", 0.15, speed=0.18, settle=2.3)

        # 유지
        set_led(255, 255, 0)
        hover(2.0)

        # 1단 하강
        set_led(0, 200, 255)
        move_z("Step down 1", -0.15, speed=0.18, settle=2.3)

        # 유지
        hover(1.5)

        # 2단 하강
        move_z("Step down 2", -0.15, speed=0.18, settle=2.3)

        hover(1.2)

        print("Landing")
        set_led(255, 255, 0)
        drone.sendControlWhile(0, 0, 0, 0, 300)
        sleep(0.2)
        drone.sendLanding()
        sleep(3)

        led_off()
        print("Mission complete")

    except Exception as e:
        print("오류:", e)
        try:
            emergency_land()
        except:
            pass
    finally:
        try:
            drone.close()
        except:
            pass