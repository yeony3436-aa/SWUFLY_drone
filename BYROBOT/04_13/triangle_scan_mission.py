# triangle_scan_mission_big.py
from time import sleep
from CodingDrone.drone import *
from CodingDrone.protocol import *
import keyboard
import sys
import math

PORT = "COM3"

MOVE_SPEED = 0.40      # 기존 0.35 -> 약간 증가
HOVER_DT = 0.1

# 삼각형 크기
TRI_SIDE = 0.60        # 기존 체감보다 조금 더 크게
TRI_HALF_BACK = -TRI_SIDE / 2.0
TRI_Y = round((math.sqrt(3) / 2.0) * TRI_SIDE, 2)   # 약 0.52

POP_Z = 0.30           # 기존 0.2 -> 0.3

drone = Drone()

def set_led_connected():
    drone.sendLightModeColor(LightModeDrone.BodyHold, 200, 0, 255, 0)
    sleep(0.2)

def set_led_takeoff():
    drone.sendLightModeColor(LightModeDrone.BodyHold, 200, 0, 200, 255)
    sleep(0.2)

def set_led_scan():
    drone.sendLightModeColor(LightModeDrone.BodyHold, 200, 255, 0, 255)
    sleep(0.2)

def set_led_patrol():
    drone.sendLightModeColor(LightModeDrone.BodyHold, 200, 0, 0, 255)
    sleep(0.2)

def set_led_return():
    drone.sendLightModeColor(LightModeDrone.BodyHold, 200, 255, 255, 0)
    sleep(0.2)

def set_led_emergency():
    drone.sendLightModeColor(LightModeDrone.BodyHold, 200, 255, 0, 0)
    sleep(0.2)

def led_off():
    drone.sendLightManual(DeviceType.Drone, 0xFF, 0)
    sleep(0.2)

def emergency_land():
    print("[EMERGENCY] 비상 착륙")
    try:
        set_led_emergency()
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

def hover(seconds):
    steps = int(seconds / HOVER_DT)
    for _ in range(steps):
        check_emergency()
        drone.sendControlWhile(0, 0, 0, 0, 100)
        sleep(0.03)

def move_relative(label, x, y, z, speed=MOVE_SPEED, settle_sec=3.2):
    check_emergency()
    print(f"{label}: x={x}, y={y}, z={z}")
    drone.sendControlPosition(x, y, z, speed, 0, 30)
    hover(settle_sec)

def yaw_scan():
    print("Yaw scan 시작")
    set_led_scan()

    # 기존보다 조금 더 크게 회전
    print("scan: right")
    drone.sendControlWhile(0, 0, 35, 0, 900)
    hover(1.2)

    print("scan: left")
    drone.sendControlWhile(0, 0, -35, 0, 1800)
    hover(1.2)

    print("scan: center")
    drone.sendControlWhile(0, 0, 35, 0, 900)
    hover(1.2)

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

        set_led_connected()
        print("연결 완료 - Space: 비상착륙")

        print("TakeOff")
        set_led_takeoff()
        drone.sendTakeOff()
        sleep(4)

        hover(1.5)

        # 1) Yaw scan
        yaw_scan()

        # 2) Triangle patrol
        set_led_patrol()
        print("Triangle patrol 시작")

        # 더 큰 삼각형 + 시작점으로 거의 복귀하는 형태
        move_relative("Leg1 front", TRI_SIDE, 0.0, 0.0, speed=0.40, settle_sec=3.2)
        move_relative("Leg2 back-left", TRI_HALF_BACK, TRI_Y, 0.0, speed=0.38, settle_sec=3.4)
        move_relative("Leg3 back-right", TRI_HALF_BACK, -TRI_Y, 0.0, speed=0.38, settle_sec=3.4)

        hover(1.5)

        # 3) 고도 변화도 조금 더 크게
        set_led_return()
        move_relative("Pop-up", 0.0, 0.0, POP_Z, speed=0.25, settle_sec=2.5)
        move_relative("Back to cruise height", 0.0, 0.0, -POP_Z, speed=0.25, settle_sec=2.5)

        hover(1.5)

        print("Landing")
        drone.sendControlWhile(0, 0, 0, 0, 300)
        sleep(0.2)
        drone.sendLanding()
        sleep(3)

        led_off()
        print("Mission complete")

    except Exception as e:
        print(f"오류 발생: {e}")
        try:
            emergency_land()
        except:
            pass
    finally:
        try:
            drone.close()
        except:
            pass