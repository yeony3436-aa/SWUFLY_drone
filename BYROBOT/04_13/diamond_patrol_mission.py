# diamond_patrol_mission_safe_landing.py
from time import sleep
from CodingDrone.drone import *
from CodingDrone.protocol import *
import keyboard
import sys

PORT = "COM3"

drone = Drone()

WAIT_DT = 0.1


def set_led(r, g, b):
    drone.sendLightModeColor(LightModeDrone.BodyHold, 200, r, g, b)
    sleep(0.2)


def led_off():
    drone.sendLightManual(DeviceType.Drone, 0xFF, 0)
    sleep(0.2)


def interruptible_wait(sec):
    loops = int(sec / WAIT_DT)
    for _ in range(loops):
        check_emergency()
        sleep(WAIT_DT)


def emergency_land():
    print("[EMERGENCY] 비상 착륙 시작")
    try:
        set_led(255, 0, 0)

        # 잠깐 자세 안정화
        drone.sendControlWhile(0, 0, 0, 0, 500)
        sleep(0.3)

        # 착륙 명령
        print("[EMERGENCY] sendLanding() 전송")
        drone.sendLanding()

        # 착륙 시간 충분히 확보
        sleep(6.0)

        led_off()
        print("[EMERGENCY] 착륙 종료")
    finally:
        try:
            drone.close()
        except:
            pass

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


def move_pos(label, x, y, z=0.0, speed=0.35, settle=2.8):
    check_emergency()
    print(f"{label} -> x={x}, y={y}, z={z}, speed={speed}")
    drone.sendControlPosition(x, y, z, speed, 0, 30)
    hover(settle)


def yaw_turn(label, yaw_speed, duration_ms):
    check_emergency()
    print(f"{label} -> yaw_speed={yaw_speed}, duration={duration_ms}ms")
    drone.sendControlWhile(0, 0, yaw_speed, 0, duration_ms)
    hover(1.0)


def do_landing(wait_sec=6.0):
    print("Landing")
    set_led(255, 255, 0)

    # 먼저 제자리 안정화
    drone.sendControlWhile(0, 0, 0, 0, 500)
    sleep(0.3)

    # 착륙 명령 전송
    print("sendLanding() 전송")
    drone.sendLanding()

    # 착륙 중에도 비상키 확인 가능하게 대기
    loops = int(wait_sec / WAIT_DT)
    for i in range(loops):
        check_emergency()
        sleep(WAIT_DT)

        # 중간 로그
        if i == int(2.0 / WAIT_DT):
            print("...landing 진행 중")

    led_off()
    print("Mission complete")


if __name__ == "__main__":
    try:
        ok = drone.open(PORT)
        if not ok:
            raise RuntimeError(f"포트 열기 실패: {PORT}")

        interruptible_wait(1.0)

        drone.sendLostConnection(1000, 1500, 0)
        interruptible_wait(0.2)

        drone.sendModeControlFlight(ModeControlFlight.Position)
        interruptible_wait(0.2)

        set_led(0, 255, 0)
        print("연결 완료 - Space: 비상착륙")

        print("TakeOff")
        set_led(0, 200, 255)
        drone.sendTakeOff()

        # 기존 sleep(4) 대신 인터럽트 가능한 대기
        interruptible_wait(4.5)

        hover(1.2)

        set_led(0, 0, 255)
        print("Diamond patrol 시작")

        # 앞-오른쪽
        move_pos("Front-Right", 0.35, -0.35)
        yaw_turn("Yaw right", 25, 600)

        # 뒤-오른쪽
        move_pos("Back-Right", -0.35, -0.35)
        yaw_turn("Yaw left", -25, 1200)

        # 뒤-왼쪽
        move_pos("Back-Left", -0.35, 0.35)
        yaw_turn("Yaw right", 25, 600)

        # 앞-왼쪽
        move_pos("Front-Left", 0.35, 0.35)

        hover(1.5)

        do_landing(wait_sec=6.0)

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