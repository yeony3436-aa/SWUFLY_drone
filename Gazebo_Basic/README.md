# 🎡 Gazebo Drone Simulation (ROS2)

가제보(Gazebo) 시뮬레이터 환경에서 **MAVROS**를 이용하여 드론의 상태 정보를 수신하고, 자율 비행 알고리즘을 테스트하는 프로젝트

<br>

## 📂 주요 소스 코드

### 1. 텔레메트리 모니터링 (`telemetry_listener.py`)
- `/mavros/state`, `/mavros/local_position/pose` 등 주요 토픽 구독
- 드론의 연결 상태, 실시간 위치($x, y, z$), 배터리 잔량 등을 1초 간격으로 출력

### 2. 기초 호버링 테스트 (`hovering_test.py`)
- OFFBOARD 모드 전환 및 Arming 서비스 호출 로직 구현
- 이륙 후 목표 고도(2.0m)에서 안정적으로 유지되는지 확인하는 기초 제어 테스트

### 3. 웨이포인트 자율 비행 (`waypoint_navigator.py`)
- 사전 정의된 4개 지점(0,0,2 -> 2,0,2 -> 2,2,2 -> 0,0,2)을 순차적으로 비행
- **거리 계산 알고리즘:** 유클리드 거리를 계산하여 목표 지점의 0.3m 이내 진입 시 다음 지점으로 이동
- **자동 미션 종료:** 모든 지점 도달 시 `CommandTOL` 서비스를 호출하여 자동 착륙(LAND) 수행

<br>

## 💡 주요 학습 내용
- ROS2 Service Client를 이용한 드론 제어 명령(Arming, Land, Mode Change) 전송
- `PoseStamped` 메시지를 활용한 실시간 위치 제어(Setpoint) 방식 이해
- 시뮬레이션 환경에서의 비동기 이벤트 처리 및 상태 기반 로직 설계
