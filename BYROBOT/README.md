# 🛸 BYROBOT BRC-105 Drone Coding Series

바이로봇(BYROBOT)사의 **BRC-105** 드론과 파이썬 `e_drone` 라이브러리를 활용

기초 비행부터 고도화된 군집 비행(Swarm Flight)까지 구현한 실습 저장소

<br>

## 📌 Project Overview
단일 기체의 정밀 제어를 시작으로, 통신 신뢰도를 높이기 위한 ACK(수신 확인) 로직 구현

그리고 여러 대의 드론을 동시에 제어하는 군집 비행 시스템 구축이 목표

<br>

## 🛠 Tech Stack
- **Hardware:** BYROBOT BRC-105 Drone
- **Language:** Python
- **Library:** `e_drone`, `keyboard` (Emergency Switch), `time`

<br>

## 📅 Curriculum & Milestones

### 🟢 [Phase 1] 기초 비행 및 LED 피드백 (04.06)
드론의 기본적인 움직임과 상태를 시각적으로 확인하는 인터페이스를 구축
- **Position Control:** 앞, 뒤, 좌, 우 0.5m 이동을 통한 사각형(Square) 궤적 비행
- **Visual Feedback:** 이륙, 비행, 착륙 등 상태별 LED 색상 변화 로직 구현
- **Safety First:** `Space` 키를 활용한 실시간 비상 착륙(Emergency Stop) 기능

### 🔵 [Phase 2] 고난도 미션 및 군집 비행 (04.13)
통신 안정성을 확보하고 다수의 기체를 유기적으로 제어하는 시스템을 설계
- **Advanced Missions:** - `Yaw Scan`: 제자리 회전을 통한 주변 탐색
  - `Patrol`: 삼각형 및 다이아몬드 경로 순찰
  - `Stair Mission`: 계단식 고도 변화 제어
- **Swarm Flight:** - 딕셔너리 구조(`ack_status`)를 활용한 기체별 상태 추적
  - **ACK 기반 양방향 통신:** 명령 수신 확인 후 다음 동작을 수행하는 신뢰성 높은 제어 로직 구현
  - **Sequential vs Simultaneous:** 순차 제어와 동시 제어 방식의 비교 및 구현

<br>

## 🚀 Key Technical Insights

### 1. ACK(Acknowledgement) 로직 구현
일방적인 명령 송신 방식의 한계를 극복하기 위해, 드론으로부터 응답(ACK)이 올 때까지 명령을 재전송하는 `send_to_drone_until_ack` 함수를 구현, 통신 로스 최소화

### 2. 하드웨어 트러블슈팅 기록
- **전력 문제:** 3대 이상 연결 시 발생하는 통신 단절을 **유전원 USB 허브** 사용으로 해결
- **자원 정리:** 프로그램 종료 시 마지막 기체의 명령 미이행 문제를 **`sleep(2)` 기반의 물리적 시간 확보**를 통해 해결

<br>

## 📂 Directory Structure
- [`04_06/`](./04_06): 기초 비행, 사각형 비행, LED 기본 제어 코드
- [`04_13/`](./04_13): 군집 비행(순차/동시), ACK 통신, 다이아몬드/삼각형 순찰 코드
