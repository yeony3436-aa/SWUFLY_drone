# branch_mission_signal.py
from time import sleep, time
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


def move_pos(label, x, y, z=0.0, speed=0.30, settle=2.4):
    check_emergency()
    print(f"{label}: x={x}, y={y}, z={z}")
    drone.sendControlPosition(x, y, z, speed, 0, 30)
    hover(settle)


def mission_1():
    print("Mission 1: forward & back")
    set_led(0, 0, 255)
    move_pos("Forward", 0.5, 0.0)
    move_pos("Back", -0.5, 0.0)


def mission_2():
    print("Mission 2: side scan")
    set_led(255, 0, 255)
    move_pos("Left", 0.0, 0.3)
    move_pos("Right", 0.0, -0.6)
    move_pos("Center", 0.0, 0.3)


def mission_3():
    print("Mission 3: mini triangle")
    set_led(255, 255, 0)
    move_pos("Front", 0.4, 0.0)
    move_pos("Back-left", -0.2, 0.25)
    move_pos("Back-right", -0.2, -0.25)


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
        print("연결 완료")
        print("1: forward/back | 2: side scan | 3: mini triangle | space: emergency")

        print("TakeOff")
        set_led(0, 200, 255)
        drone.sendTakeOff()
        sleep(4)

        hover(1.2)

        start = time()
        selected = None
        while time() - start < 8.0:
            check_emergency()

            if keyboard.is_pressed("1"):
                selected = "1"
                break
            elif keyboard.is_pressed("2"):
                selected = "2"
                break
            elif keyboard.is_pressed("3"):
                selected = "3"
                break

            hover(0.2)

        if selected == "1":
            mission_1()
        elif selected == "2":
            mission_2()
        elif selected == "3":
            mission_3()
        else:
            print("입력 없음 -> 기본 hover만 수행")
            hover(2.0)

        hover(1.0)

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