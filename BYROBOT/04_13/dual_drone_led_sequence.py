from e_drone.drone import *
from e_drone.protocol import *
from time import sleep, time

# 드론별 응답 상태 저장용 딕셔너리
ack_status = {}

# 드론 응답(ACK) 수신 이벤트 핸들러
def event_ack_handler(ack, drone_obj):
    global ack_status
    
    # 응답 수신 상태를 True로 업데이트
    ack_status[drone_obj]["is_received"] = True
    port_name = ack_status[drone_obj]["port"]
    
    # 수신된 데이터 타입과 함께 로그 출력
    print(f"  -> [{port_name}] 응답 수신 완료 (타입: {ack.dataType.name})")

# 특정 드론에 명령을 전송하고 응답을 대기하는 함수
def send_to_drone_until_ack(drone, command_func, *args, timeout=2.0):
    global ack_status
    start_time = time()
    port_name = ack_status[drone]["port"]
    
    while time() - start_time < timeout:
        ack_status[drone]["is_received"] = False
        
        command_func(*args)
        sleep(0.3) 
        
        if ack_status[drone]["is_received"]:
            print(f"  -> [{port_name}] 제어 명령 성공")
            return True
            
    print(f"  -> [{port_name}] 응답 없음 (통신 실패)")
    return False

# 메인 실행부
if __name__ == '__main__':
    # 사용 환경에 맞게 드론 포트 설정
    ports = ["COM5", "COM6"] 
    drones = []

    print("--- 포트 연결 시작 ---")
    for port in ports:
        d = Drone()
        if d.open(port):
            print(f"[{port}] 연결 성공")
            drones.append(d)
            # 드론별 상태 저장소 초기화
            ack_status[d] = {"is_received": False, "port": port}
            # 드론별 ACK 이벤트 핸들러 등록
            d.setEventHandler(DataType.Ack, lambda ack, d_obj=d: event_ack_handler(ack, d_obj))
            sleep(0.5)
        else:
            print(f"[{port}] 연결 실패. 포트를 확인하세요.")

    if not drones:
        print("연결된 드론이 없어 프로그램을 종료합니다.")
        exit()

    # 포트 전체 안정화 대기
    sleep(1.0) 
    
    try:
        print("\n--- 듀얼 드론 순차 제어 테스트 시작 ---")
        
        # 적용할 색상 리스트 (출력명, 색상코드)
        colors_sequence = [
            ("빨간색", Colors.Red),
            ("노란색", Colors.Yellow),
            ("초록색", Colors.Green)
        ]

        # 사이클 반복
        for i in range(1): 
            print(f"\n--- [ {i+1}회차 순환 ] ---")
            
            for color_name, color_code in colors_sequence:
                print(f"\n[{color_name}] 명령 전송 중...")
                
                # 연결된 드론들을 순차적으로 제어
                for idx, d in enumerate(drones):
                    print(f" 기체 {idx+1} ({ack_status[d]['port']}) 전송 시도")
                    send_to_drone_until_ack(d, d.sendLightModeColors, LightModeDrone.BodyHold, 255, color_code)
                    
                    # 순차 제어를 위한 딜레이 설정 (초 단위)
                    sleep(0.5) 
                
                # 색상 변경 후 유지 시간
                sleep(2) 

    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        print("\n--- 테스트 종료 및 포트 반환 ---")
        for d in drones:
            # LED 밝기 0으로 설정하여 소등
            d.sendLightModeColors(LightModeDrone.BodyHold, 0, Colors.Black)
        sleep(1)
        
        for d in drones:
            d.close()
            print(f"[{ack_status[d]['port']}] 닫기 완료")