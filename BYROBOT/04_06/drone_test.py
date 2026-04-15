from e_drone.drone import *
from e_drone.protocol import *
from time import sleep
import keyboard  

def emergency_stop(drone):
    print("비상 착륙")
    # 모든 이동 명령을 0으로 초기화 
    drone.sendControl(0, 0, 0, 0)
    time.sleep(0.1)
    # 즉시 착륙 
    drone.sendLanding()
    time.sleep(1)
    drone.close()
    exit() # 프로그램 강제 종료

if __name__ == '__main__':
    drone = Drone()
    drone.open("COM3") 

    # 배터리 정보 요청
    print("배터리 잔량 확인 중...")
    drone.sendRequest(DeviceType.Drone, DataType.State)
    time.sleep(0.5)

    print("드론 비행 시작! (중단하려면 'Space' 키를 누르세요)")

    # Space 키를 누르면 emergency_stop 함수 실행
    keyboard.on_press_key("space", lambda _: emergency_stop(drone))

    try:
        print("이륙...")
        drone.sendTakeOff()
        time.sleep(5)

        print("전진 중...")
        for _ in range(30): # 약 3초 동안 조금씩 이동
            drone.sendControl(0, 40, 0, 0)
            time.sleep(0.1) 
            
        print("정상 비행 완료")
        drone.sendLanding()

    except Exception as e:
        print(f"오류 발생: {e}")
    
    finally:
        drone.close()      