from time import sleep
from CodingDrone.drone import *
from CodingDrone.protocol import *

PORT = "COM3"   # 네 환경에 맞게 바꾸기

drone = Drone()

try:
    # 1) 포트 연결
    ok = drone.open(PORT)
    if not ok:
        raise RuntimeError(f"포트 열기 실패: {PORT}")
    sleep(1.0)

    # 2) 연결 끊김 대비 안전 설정
    # 마지막 명령 후 1초 뒤 중립, 1.5초 뒤 착륙, stop은 사용 안 함
    drone.sendLostConnection(1000, 1500, 0)
    sleep(0.2)

    # 3) 위치 제어 모드
    drone.sendModeControlFlight(ModeControlFlight.Position)
    sleep(0.2)

    # 4) 이륙
    print("TakeOff")
    drone.sendTakeOff()
    sleep(4)

    # 5) 짧게 호버링
    print("Hover")
    drone.sendControlWhile(0, 0, 0, 0, 1500)
    sleep(0.3)

    # 6) 앞 0.5m
    print("Front 0.5m")
    drone.sendControlPosition(0.5, 0.0, 0.0, 0.5, 0, 30)
    sleep(3)

    # 7) 오른쪽 0.5m (y는 우측이 음수)
    print("Right 0.5m")
    drone.sendControlPosition(0.0, -0.5, 0.0, 0.5, 0, 30)
    sleep(3)

    # 8) 뒤 0.5m
    print("Back 0.5m")
    drone.sendControlPosition(-0.5, 0.0, 0.0, 0.5, 0, 30)
    sleep(3)

    # 9) 왼쪽 0.5m (y는 좌측이 양수)
    print("Left 0.5m")
    drone.sendControlPosition(0.0, 0.5, 0.0, 0.5, 0, 30)
    sleep(3)

    # 10) 호버링
    print("Hover")
    drone.sendControlWhile(0, 0, 0, 0, 1500)
    sleep(0.3)

    # 11) 착륙
    print("Landing")
    drone.sendControlWhile(0, 0, 0, 0, 300)
    sleep(0.2)
    drone.sendLanding()
    sleep(3)

except Exception as e:
    print("에러:", e)
    try:
        drone.sendStop()
        sleep(1)
    except:
        pass

finally:
    drone.close()
    print("Closed")