# Rokey3_Library_Book_Organizing_Cobot
rokey3 Library Book Organizing Collaborative Robot

# Cobotics Book Organizing Bot

소켓툴 입력 정보를 바탕으로 책을 정리하고 시각화하는 ROS2 기반 팀 코보틱스 프로젝트입니다.

## 사용 장비
![image](https://github.com/user-attachments/assets/e6115195-658b-4864-abc5-638ba14c0478)


![image](https://github.com/user-attachments/assets/fe5fe635-e9d0-42cb-b05a-40d173ad6d6e)



## 🗂️ 프로젝트 구조
```
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



## 사전 요구 사항

### ROS2 및 시스템 패키지

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

## DoosanBootcamInt1 설치
이 프로젝트는 다음 외부 패키지의 설치를 요구합니다:

[DoosanBootcamInt1 GitHub](https://github.com/ROKEY-SPARK/DoosanBootcamInt1)

```
cd cobotics_ws_/
cd src/
git clone https://github.com/ROKEY-SPARK/DoosanBootcamInt1.git
```
## 사용한 소켓 툴
![image](https://github.com/user-attachments/assets/1704d6bb-76c2-4ff9-86c6-52c667c6a4cc)

[simple socket tool](https://sourceforge.net/projects/simple-socket-tool/)


## 빌드 및 실행 방법
```
# 워크스페이스 루트로 이동
cd ~/cobotics_ws

# 의존성 설치
rosdep install --from-paths src --ignore-src -r -y

# 빌드
colcon build --symlink-install

# 환경 설정
source install/setup.bash

# 협동로봇 연결 및 rviz 화면 열기 예시
ros2 launch dsr_bringup2 dsr_bringup2_rviz.launch.py mode:=real host:=192.168.1.100 port:=12345 model:=m0609

# 노드 실행 (책 정리 봇)
ros2 run book_organizing_bot BookOrganizing

# 소켓툴 열기 예시
java -jar /home/bako98/cobotics_ws/SST_1v3.jar

```

## 웹 시각화 서버 실행
```
cd book_visualizer
python3 app_book.py
```
![image](https://github.com/user-attachments/assets/30f49cf6-ee17-4482-a90e-0fa77f6dfd95)

1. 협동로봇 연결
2. 책 정리 봇 노드 실행
3. 웹 시각화 서버 실행
4. 소켓툴 실행
5. 소켓툴을 클라이언트로 127.0.0.1에 2000포트로 연결
6. 소켓툴에 입력으로 red, purple, red, brown 등 입력 (사용한 책 예시)
![image](https://github.com/user-attachments/assets/fbd92686-016a-4e8a-ba93-a18ab77a92be)

동작 예시
소켓에서 입력받은 구역으로 책 정리

![image](https://github.com/user-attachments/assets/c9140dc1-b196-4005-a6d1-2db99a74ae05)

높이 측정 및 집기 동작

![image](https://github.com/user-attachments/assets/8d5aef60-5066-4196-8b7a-daf5afe3984b)

예시영상

[![Video Label](http://img.youtube.com/vi/mOouOeEV-3M/0.jpg)](https://youtu.be/mOouOeEV-3M)




## 참고
ROS2: https://docs.ros.org/en/humble/index.html

Gazebo: https://gazebosim.org/

DoosanBootcamInt1: https://github.com/ROKEY-SPARK/DoosanBootcamInt1



