from e_drone.drone import *
from e_drone.protocol import *
from time import sleep, time
import keyboard

# 드론별 응답 상태 저장용 딕셔너리
ack_status = {}

# 드론 응답(ACK) 수신 이벤트 핸들러 
def event_ack_handler(ack, drone_obj):
    global ack_status
    ack_status[drone_obj]["is_received"] = True
    port_name = ack_status[drone_obj]["port"]

    if ack.dataType != DataType.Control:
        print(f"  -> [{port_name}] 응답 수신 완료 (타입: {ack.dataType.name})")

# 명령 전송 및 응답 대기 함수
def send_to_drone_until_ack(drone, command_func, *args, timeout=2.0):
    global ack_status
    start_time = time()
    port_name = ack_status[drone]["port"]
    
    while time() - start_time < timeout:
        ack_status[drone]["is_received"] = False
        command_func(*args)
        sleep(0.3) 
        
        if ack_status[drone]["is_received"]:
            return True
            
    print(f"  -> [{port_name}] 응답 없음 (통신 실패)")
    return False

# 비상 정지 기능 (스페이스바)
def emergency_stop(drones):
    print("\n!!! 비상 상황: 모든 드론 즉시 착륙 !!!")
    for d in drones:
        d.sendControl(0, 0, 0, 0)
        d.sendLanding()
    sleep(1)
    for d in drones:
        d.close()
    exit()

# 메인 실행부
if __name__ == '__main__':
    ports = ["COM5", "COM6"] # 드론 추가 시 포트 번호 추가
    drones = []

    print("--- 포트 연결 시작 ---")
    for port in ports:
        d = Drone()
        if d.open(port):
            print(f"[{port}] 연결 성공")
            drones.append(d)
            ack_status[d] = {"is_received": False, "port": port}
            d.setEventHandler(DataType.Ack, lambda ack, d_obj=d: event_ack_handler(ack, d_obj))
            sleep(0.5)
        else:
            print(f"[{port}] 연결 실패. 포트를 확인하세요.")

    if not drones:
        print("연결된 드론이 없어 프로그램을 종료합니다.")
        exit()

    sleep(1.0) # 포트 안정화 대기
    
    # 스페이스바 비상 정지 세팅
    keyboard.on_press_key("space", lambda _: emergency_stop(drones))

    try:
        print("\n=============================================")
        print(" 🚦 색상 연동 군집 비행 시작! (Space: 비상착륙) ")
        print("=============================================\n")
        
        # --------------------------------------------------
        # [단계 1] 🔴 빨간불 & 순차 이륙
        # --------------------------------------------------
        print("--- [ 1단계: 🔴 빨간불 (이륙) ] ---")
        for idx, d in enumerate(drones):
            port = ack_status[d]['port']
            print(f"\n기체 {idx+1} ({port}) 빨간불 켜고 이륙!")
            
            # 1. 빨간색 LED 점등
            send_to_drone_until_ack(d, d.sendLightModeColors, LightModeDrone.BodyHold, 255, Colors.Red)
            sleep(0.5)
            # 2. 이륙 명령
            send_to_drone_until_ack(d, d.sendTakeOff)
            
            # 다음 기체 이륙 전 안정화 대기
            sleep(2)

        print("\n=> [대기] 고도 안정화 중...")
        for _ in range(20):
            for d in drones: d.sendControl(0, 0, 0, 0)
            sleep(0.1)

        # --------------------------------------------------
        # [단계 2] 🟡 노란불 & 순차 전진
        # --------------------------------------------------
        print("\n--- [ 2단계: 🟡 노란불 (전진) ] ---")
        for idx, d in enumerate(drones):
            port = ack_status[d]['port']
            print(f"\n기체 {idx+1} ({port}) 노란불 켜고 전진!")
            
            # 1. 노란색 LED 점등
            send_to_drone_until_ack(d, d.sendLightModeColors, LightModeDrone.BodyHold, 255, Colors.Yellow)
            
            # 2. 앞으로 전진 (Pitch 30) - 약 2초간 이동
            for _ in range(20):
                d.sendControl(0, 30, 0, 0)
                sleep(0.1)
                
            # 3. 제자리에 브레이크 잡고 대기
            d.sendControl(0, 0, 0, 0)
            sleep(1)

        print("\n=> [대기] 위치 안정화 중...")
        for _ in range(15):
            for d in drones: d.sendControl(0, 0, 0, 0)
            sleep(0.1)

        # --------------------------------------------------
        # [단계 3] 🟢 초록불 & 순차 착륙
        # --------------------------------------------------
        print("\n--- [ 3단계: 🟢 초록불 (착륙) ] ---")
        for idx, d in enumerate(drones):
            port = ack_status[d]['port']
            print(f"\n기체 {idx+1} ({port}) 초록불 켜고 착륙!")
            
            # 1. 초록색 LED 점등
            send_to_drone_until_ack(d, d.sendLightModeColors, LightModeDrone.BodyHold, 255, Colors.Green)
            sleep(0.5)
            
            # 2. 착륙 명령
            send_to_drone_until_ack(d, d.sendLanding)
            
            # 다음 기체 착륙 전 대기
            sleep(2)

    except Exception as e:
        print(f"오류 발생: {e}")
        emergency_stop(drones)
    finally:
        print("\n--- 비행 종료 및 LED 소등 ---")
        for d in drones:
            d.sendLightModeColors(LightModeDrone.BodyHold, 0, Colors.Black)
        sleep(1)
        for d in drones:
            d.close()
        print("포트 닫기 완료")