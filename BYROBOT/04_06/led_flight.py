from time import sleep
from CodingDrone.drone import *
from CodingDrone.protocol import *
import keyboard
import sys

PORT = "COM3"
emergency_requested = False


def request_emergency():
    global emergency_requested
    emergency_requested = True
    print("Space 입력 감지 -> 비상 착륙 요청")


def set_led_connected(drone):
    # 연결 완료 -> 초록
    drone.sendLightModeColor(LightModeDrone.BodyHold, 200, 0, 255, 0)
    sleep(0.2)


def set_led_flying(drone):
    # 비행 중 -> 파랑
    drone.sendLightModeColor(LightModeDrone.BodyHold, 200, 0, 0, 255)
    sleep(0.2)


def set_led_midflight(drone):
    # 비행 중간 -> 보라
    drone.sendLightModeColor(LightModeDrone.BodyHold, 200, 255, 0, 255)
    sleep(0.2)


def set_led_landing(drone):
    # 착륙 직전 -> 노랑
    drone.sendLightModeColor(LightModeDrone.BodyHold, 200, 255, 255, 0)
    sleep(0.2)


def set_led_emergency(drone):
    # 비상 상황 -> 빨강
    drone.sendLightModeColor(LightModeDrone.BodyHold, 200, 255, 0, 0)
    sleep(0.2)


def led_off(drone):
    # LED 끄기
    drone.sendLightManual(DeviceType.Drone, 0xFF, 0)
    sleep(0.2)


def emergency_stop(drone):
    print("비상 착륙 실행")
    set_led_emergency(drone)

    # 이동 중지
    drone.sendControl(0, 0, 0, 0)
    sleep(0.3)

    # 착륙
    drone.sendLanding()
    sleep(3)

    led_off(drone)


if __name__ == '__main__':
    drone = Drone()

    try:
        ok = drone.open(PORT)
        if not ok:
            raise RuntimeError(f"포트 열기 실패: {PORT}")

        sleep(1.0)

        # 연결 끊김 대비: 마지막 조종 명령 후 1초 뒤 중립, 1.5초 뒤 착륙
        drone.sendLostConnection(1000, 1500, 0)
        sleep(0.2)

        # 연결 완료 LED
        set_led_connected(drone)

        print("드론 비행 시작! (중단하려면 Space 키를 누르세요)")
        keyboard.on_press_key("space", lambda _: request_emergency())

        print("이륙...")
        drone.sendTakeOff()
        sleep(4)

        # 비행 시작 LED
        set_led_flying(drone)

        print("전진 중...")
        for i in range(30):   # 약 3초
            if emergency_requested:
                emergency_stop(drone)
                sys.exit(0)

            # 중간 지점에서 색상 변경
            if i == 15:
                set_led_midflight(drone)

            drone.sendControl(0, 40, 0, 0)
            sleep(0.1)

        # 정지
        drone.sendControl(0, 0, 0, 0)
        sleep(0.5)

        if emergency_requested:
            emergency_stop(drone)
            sys.exit(0)

        print("정상 비행 완료")

        # 착륙 LED
        set_led_landing(drone)

        drone.sendLanding()
        sleep(3)

        led_off(drone)
        print("종료")

    except Exception as e:
        print(f"오류 발생: {e}")
        try:
            set_led_emergency(drone)
            drone.sendControl(0, 0, 0, 0)
            sleep(0.3)
            drone.sendLanding()
            sleep(3)
            led_off(drone)
        except:
            pass

    finally:
        try:
            drone.close()
        except:
            pass 