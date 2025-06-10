# 📚 Rokey3 Library Book Organizing Collaborative Robot

도서관 책 정리 업무를 자동화하여 사서의 업무 부담을 줄이고, 도서 정리의 정확성과 효율을 향상시키는 ROS2 기반 협동로봇 프로젝트입니다.

---

## 프로젝트 개요

### **프로젝트 주제 및 선정 배경**

강북구 등 공공도서관의 사서 수는 전국 평균에 비해 절반에도 못 미치며, 1인이 모든 업무를 도맡는 비정상적 상황이 지속되고 있습니다.  
이에 따라 반납된 책을 자동으로 정리하는 협동로봇을 개발하여 사서의 업무 부담을 줄이고 도서관 운영의 효율성을 향상시키고자 하였습니다.

---

## 사용 장비 및 기술 스택

- **로봇**: 두산 M0609 협동로봇
  
![image](https://github.com/user-attachments/assets/e6115195-658b-4864-abc5-638ba14c0478)
  
- **그리퍼**: OnRobot RG2

![image](https://github.com/user-attachments/assets/fe5fe635-e9d0-42cb-b05a-40d173ad6d6e)

- **통신**: Simple Socket Tool [(링크)](https://sourceforge.net/projects/simple-socket-tool/)  
- **소프트웨어**
  - ROS2 Humble (Ubuntu 22.04)
  - Python3
  - Flask (웹 시각화 서버)
  - Gazebo (시뮬레이션 환경)
- **외부 패키지**: [DoosanBootcamInt1](https://github.com/ROKEY-SPARK/DoosanBootcamInt1)

---

## 프로젝트 트리 구조

```bash
cobotics_ws/
├── book_visualizer/ # 책 정보를 시각화하는 웹앱 (Flask)
│   ├── app_book.py
│   └── templates/
│   └── index.html
├── src/
│   ├── book_organizing_bot/ # ROS2 패키지: 책 정리 봇
│   │   ├── book_organizing_bot/
│   │   │   ├── BookOrganizing.py
│   │   │   └── init.py
│   │   ├── package.xml
│   │   ├── resource/
│   │   │   └── book_organizing_bot
│   │   ├── setup.cfg
│   │   └── setup.py
│   └── DoosanBootcamInt1/ # 의존 프로젝트
│   └── ... (외부 종속 요소 포함)
├── build/ # colcon 빌드 디렉토리
├── install/
├── log/
```

---

## 사전 요구 사항


### ROS2 및 필수 패키지 설치

Ubuntu 22.04 + ROS2 Humble 환경에서 개발되었습니다. 다음 패키지를 설치해 주세요:

```bash
sudo apt-get update
sudo apt-get install -y \
  libpoco-dev libyaml-cpp-dev wget \
  ros-humble-control-msgs ros-humble-realtime-tools ros-humble-xacro \
  ros-humble-joint-state-publisher-gui ros-humble-ros2-control \
  ros-humble-ros2-controllers ros-humble-gazebo-msgs ros-humble-moveit-msgs \
  dbus-x11 ros-humble-moveit-configs-utils ros-humble-moveit-ros-move-group \
  ros-humble-gazebo-ros-pkgs ros-humble-ros-gz-sim ros-humble-ign-ros2-control
```

## Gazebo 시뮬레이터 설치
```
sudo sh -c 'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" > /etc/apt/sources.list.d/gazebo-stable.list'
wget http://packages.osrfoundation.org/gazebo.key -O - | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y \
  libignition-gazebo6-dev \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-ros-gz-sim \
  ros-humble-ros-gz
```

## 외부 패키지 DoosanBootcamInt1 설치
이 프로젝트는 다음 외부 패키지의 설치를 요구합니다:

[DoosanBootcamInt1 GitHub](https://github.com/ROKEY-SPARK/DoosanBootcamInt1)

```
cd cobotics_ws_/
cd src/
git clone https://github.com/ROKEY-SPARK/DoosanBootcamInt1.git
```

## 사용한 소켓 툴

<img src="https://github.com/user-attachments/assets/1704d6bb-76c2-4ff9-86c6-52c667c6a4cc" width="400"/>

[simple socket tool](https://sourceforge.net/projects/simple-socket-tool/)


---


## 빌드 및 실행 방법
```
# 워크스페이스 루트로 이동
cd ~/cobotics_ws
# 의존성 설치
rosdep install --from-paths src --ignore-src -r -y
# 빌드
colcon build 
# 환경 설정
source install/setup.bash



## 협동로봇 연결 및 rviz 화면 열기 예시

# 1번 터미널 (협동로봇 연결 및 rviz 화면 열기)
ros2 launch dsr_bringup2 dsr_bringup2_rviz.launch.py mode:=real host:=192.168.1.100 port:=12345 model:=m0609

# 2번 터미널
# 노드 실행 (책 정리 봇)
ros2 run book_organizing_bot BookOrganizing

# 3번 터미널
## 소켓툴 열기 예시
java -jar /home/bako98/cobotics_ws/SST_1v3.jar

# 소켓툴을 클라이언트로 127.0.0.1에 2000포트로 연결
# 소켓툴에 입력으로 red, purple, red, brown 등 입력 (사용한 책 예시)

# 4번 터미널
## 웹 시각화 서버 실행
# 접속 주소: http://localhost:5000 를 웹 주소에 입력
cd book_visualizer
python3 app_book.py

```
1. 협동로봇 연결
2. 책 정리 봇 노드 실행
3. 웹 시각화 서버 실행
4. 소켓툴 실행
5. 소켓툴을 클라이언트로 127.0.0.1에 2000포트로 연결
6. 소켓툴에 입력으로 red, purple, red, brown 등 입력 (사용한 책 예시)
![image](https://github.com/user-attachments/assets/fbd92686-016a-4e8a-ba93-a18ab77a92be)

---

## 동작 예시
## 소켓에서 입력받은 구역으로 책 정리

<img src="https://github.com/user-attachments/assets/c9140dc1-b196-4005-a6d1-2db99a74ae05" width="400"/>

## 높이 측정 및 집기 동작

![image](https://github.com/user-attachments/assets/8d5aef60-5066-4196-8b7a-daf5afe3984b)

## 웹 시각화 결과
![image](https://github.com/user-attachments/assets/30f49cf6-ee17-4482-a90e-0fa77f6dfd95)


## 예시영상

[![Video Label](http://img.https://youtube/DNa9JIxyISo/0.jpg)](https://youtu.be/DNa9JIxyISo)
[![Video Label](http://img.youtube.com/vi/DNa9JIxyISo/0.jpg)](https://youtu.be/DNa9JIxyISo)

---

## 참고
ROS2: https://docs.ros.org/en/humble/index.html

Gazebo: https://gazebosim.org/

DoosanBootcamInt1: https://github.com/ROKEY-SPARK/DoosanBootcamInt1

---

## 🙋‍♂️ 팀 소개
Team Cobotics
김동건 · 김현창 · 변재승 · 조성훈

