# 🛸 SWUFLY: Archiving Every Step of Drone Growth

드론 소프트웨어 개발 및 실습 저장소 


실제 하드웨어 제어부터 ROS2 기반의 시뮬레이션까지, 자율 주행 드론 기술을 연구하고 기록합니다.

<br>

## 📂 Project Structure

본 레파지토리는 크게 **실제 기체 제어(BYROBOT)** 와 **가상 환경 시뮬레이션(Gazebo)** 두 파트로 나뉩니다.

<br>

### 1. [BYROBOT](./BYROBOT) - Physical Drone Control
BRC-105 드론과 `e_drone` 라이브러리를 사용한 파이썬 기반 제어 실습입니다.
* **Phase 1 (04.06):** 기초 위치 제어, 사각형 궤적 비행, 비행 상태별 LED 피드백 시스템 구축.
* **Phase 2 (04.13):** 고도화된 미션(Yaw Scan, 다이아몬드 순찰) 및 **ACK 기반 군집 비행(Swarm Flight)** 구현.
* **Key Tech:** 양방향 통신 검증 로직, 실시간 비상 착륙(Kill-Switch) 시스템.

<br>

### 2. [Gazebo_Basic](./Gazebo_Basic) - ROS2 Simulation
Ubuntu 22.04 환경에서 ROS2와 MAVROS를 이용한 드론 시뮬레이션입니다.
* **Telemetry:** 드론의 상태 및 위치 정보를 실시간으로 구독(Subscribe)하여 모니터링.
* **Autonomy:** Offboard 모드 전환 및 유클리드 거리 계산을 활용한 **웨이포인트(Waypoint) 자율 주행**.
* **Environment:** ROS2 Humble/Foxy, Gazebo, MAVROS.

<br>

## 🚀 Key Technical Highlights

### 🛰️ Reliable Communication (ACK Logic)
군집 비행 시 발생하는 통신 유실을 방지하기 위해, 드론으로부터 수신 확인(ACK) 신호를 받을 때까지 명령을 재전송하는 로직을 구현하고, <br>
제어 신뢰성을 극대화하여 다수 기체의 동기화를 맞추는 데 집중했습니다.

### 🤖 ROS2 & MAVROS Integration
시뮬레이션 환경에서 Service와 Topic을 활용하여 기체에 시동을 걸고(Arming), 자동 착륙(Land)시키며, 목표 좌표로 이동시키는 비동기 이벤트 기반 노드를 설계했습니다.

### 🛠️ Hardware Troubleshooting
* **전력 최적화:** 3대 이상의 기체 연결 시 발생하는 전력 부족 문제를 유전원 USB 허브 도입으로 해결.
* **자원 관리:** 프로그램 종료 시 스레드와 시리얼 포트 간의 간섭 문제를 물리적 시간 확보(`sleep`)를 통해 해결.

<br>

## 🛠 Tech Stack
| Category | Details |
| :--- | :--- |
| **Languages** | Python (3.10+), C++ |
| **Frameworks** | ROS2 Humble/Foxy, MAVROS |
| **Tools** | Gazebo, VS Code, Git/GitHub |
| **Hardware** | BYROBOT BRC-105 |

