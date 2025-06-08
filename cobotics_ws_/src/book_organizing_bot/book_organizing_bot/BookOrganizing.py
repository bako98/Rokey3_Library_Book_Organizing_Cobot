import rclpy
import DR_init
import logging
import socket
from DR_tcp_client2 import *
from DR_tcp_server2 import *

import requests




ROBOT_ID = "dsr01"
ROBOT_MODEL = "m0609"
VELOCITY = 70
ACC = 70
VELOCITY_safe2 = 30
ACC_safe2 = 30
# 디지털 IO 핀 번호
GRIP_PIN = 1
RELEASE_PIN = 2

# 디지털 IO 상태
OFF, ON = 0, 1

# 좌표값 모음
START_POS = [367.05, 8.82, 326.53, 7.66, 179.63, 7.25]
# START_POS = [391.37, 8.83, 350.79, 1.61, -180, 1.22]
START_POS_up = [367.05, 8.82, 400.53, 7.66, 179.63, 7.25]
# START_POS_up = [391.37, 8.83, 415.79, 1.61, -180, 1.22]
START_POSJ = [0.11, 10.43, 41.90, -0.07, 123.31, 0.06]
# START_POSJ = [0.21, 15.21, 35.41, -0.18, 129.38, 0.08]
GRIP_BOOK_POS = [352, -60, 92, 91, 91, 180]
init_pos = [0, 0, 90, 0, 90, 0]
ahead_move_1 = [100, 0, 0, 0, 0, 0]
ahead_move_2 = [130, 0, 0, 0, 0, 0]
ahead_move_3 = [230, 0, 0, 0, 0, 0]
ahead_move_4 = [150, 0, 0, 0, 0, 0]
back_move = [-100, 0, 0, 0, 0, 0]
right_move = [0, -50, 0, 0, 0, 0]
left_move = [0, 50, 0, 0, 0, 0]
section1 = [36.76, 21.26, 88.34, 63.47, -38.58, 31.84]
section2 = [-3.27, 5.99, 110.70, 2.68, -26.75, 88.14]
section3 = [-47.19, 12.04, 102.53, 109.31, 49.04, -210.18]

# 상대 좌표 이동
RELATIVE_POS = {
    "down": [0, 0, -50, 0, 0, 0],
    "side": [0, 110, 0, 0, 0, 0],
    "side2": [0, -160, 0, 0, 0, 0],
    "side3": [0, 35, 0, 0, 0, 0],
    "down_book": [0, 0, -40, 0, 0, 0],
    "up_book": [0, 0, 10, 0, 0, 0],
    "push_book": [0, -40, 0, 0, 0, 0],
    "collision_avoid_1": [0, 10, 0, 0, 0, 0],
    "collision_avoid_2": [0, 0, 30, 0, 0, 0],
    "collision_avoid_3": [0, 0, 120, 0, 0, 0],
}

# 반복 횟수
REPEAT_COUNT = 1

DR_init.__dsr__id = ROBOT_ID
DR_init.__dsr__model = ROBOT_MODEL

def main(args=None):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    rclpy.init(args=args)
    node = rclpy.create_node("rokey_Pick_and_Place", namespace=ROBOT_ID)

    DR_init.__dsr__node = node

    try:
        from DSR_ROBOT2 import (
            release_compliance_ctrl,
            check_force_condition,
            task_compliance_ctrl,
            set_desired_force,
            release_force,
            set_digital_output,
            get_digital_input,
            set_tool,
            set_tcp,
            movel,
            movej,
            wait,
            get_current_posx,
            posx,
            DR_FC_MOD_REL,
            DR_FC_MOD_ABS,
            DR_AXIS_X,
            DR_AXIS_Y,
            DR_AXIS_Z,
            DR_BASE,
        )
    except ImportError as e:
        print(f"Error importing DSR_ROBOT2 : {e}")
        return

    # 디지털 입력 대기
    def wait_digital_input(sig_num):
        while not get_digital_input(sig_num):
            wait(0.5)
            print(f"Wait for digital input {sig_num}")

    # 그립과 릴리즈 함수
    def grip():
        set_digital_output(GRIP_PIN, ON)
        set_digital_output(RELEASE_PIN, OFF)
        wait_digital_input(GRIP_PIN)
        wait(1)
        print("grip success")

    def release():
        set_digital_output(RELEASE_PIN, ON)
        set_digital_output(GRIP_PIN, OFF)
        wait_digital_input(RELEASE_PIN)
        wait(1)
        print("release success")
    # 상대좌표 이동 함수
    def movel_relative(offset):
        movel(offset, vel=VELOCITY, acc=ACC, mod=1)

    # 절대좌표 이동 함수
    def movel_absolute(position):
        movel(posx(position), vel=VELOCITY, acc=ACC, mod=0)

    def forcecheck(num): # 1 is z_axis, 2 is x_axis, 3 is y_axis
        cfx = check_force_condition(DR_AXIS_X, max=10) # force < 10 -> true 0, 
        cfy = check_force_condition(DR_AXIS_Y, max=10)  # force > 10 -> false -1
        cfz = check_force_condition(DR_AXIS_Z, max=10)
        cfx_user = check_force_condition(DR_AXIS_X, max=15) # force < 15 -> true 0, 
        cfy_user = check_force_condition(DR_AXIS_Y, max=15)  # force > 15 -> false -1
        cfz_user = check_force_condition(DR_AXIS_Z, max=15)
        if num == 1:
            if cfx == 0 and cfy == 0 and cfz == 0:  # x, y, z force is none
                return 1
            elif cfx_user == -1 or cfy_user == -1 and cfz == 0: # x or y force exist, z force is none
                # print("force XY detected, force Z is none")
                return 2
            elif cfz == -1: # z force is exist
                # print("force Z detected")
                return 3
        
        if num == 2:
            if cfx == 0 and cfy == 0 and cfz == 0:  # x, y, z force is none
                return 1
            elif cfy_user == -1 or cfz_user == -1 and cfx == 0: # y,z force exist, x force is none
                # print("force YZ detected, force X is none")
                return 2
            elif cfx == -1: # x force is exist
                # print("force X detected")
                return 3

        if num == 3:
            if cfx == 0 and cfy == 0 and cfz == 0:  # x, y, z force is none
                return 1        
            elif cfx_user == -1 or cfz_user == -1 and cfy == 0: # x,z force exist, y force is none
                # print("force XZ detected, force Y is none")
                return 2
            elif cfy == -1: # y force is exist
                # print("force Y detected")
                return 3

        # # force control code example
        # task_compliance_ctrl(stx=[3000, 3000, 3000, 200, 200, 200]); wait(0.1)
        # # force to -z
        # set_desired_force(fd=[0, 0, -20, 0, 0, 0], dir=[0, 0, 1, 0, 0, 0], mod=DR_FC_MOD_REL); wait(0.1)
        # while True:
        #     if forcecheck(3) == 3: # force Z detected
        #         # print("z force checked")
        #         wait(0.1)
        #         break
        #     elif forcecheck(3) == 2: # force XY detected
        #         # print("force XY checked")
        #         # print("wait 2")
        #         release_force()
        #         print("force 0 for 1 sec")
        #         wait(1)
        #         set_desired_force(fd=[0, 0, -20, 0, 0, 0], dir=[0, 0, 1, 0, 0, 0], mod=DR_FC_MOD_REL)
        #     elif forcecheck(3) == 1: # force none
        #         #print("force XY not checked")
        #         wait(0.1)
        # release_force(); wait(0.1); print("release force")     
        # release_compliance_ctrl(); wait(0.1); print("release force")

    # 힘 제어 시작
    def force_control_push_z():
        print("force_control_start")
        task_compliance_ctrl(stx=[100, 100, 100, 100, 100, 100])
        wait(0.1)
        set_desired_force(fd=[0, 0, -40, 0, 0, 0], dir=[0, 0, 1, 0, 0, 0], mod=DR_FC_MOD_REL)
        while True:
            if forcecheck(1) == 3: # force Z detected
                # print("z force checked")
                wait(0.1)
                break
            elif forcecheck(1) == 2: # force XY detected
                # print("force XY checked")
                release_force()
                print("force 0 for 3 sec")
                wait(3)
                set_desired_force(fd=[0, 0, -40, 0, 0, 0], dir=[0, 0, 1, 0, 0, 0], mod=DR_FC_MOD_REL)
            elif forcecheck(1) == 1: # force none
                #print("force XY not checked")
                wait(0.1)
        release_force()
        wait(0.1)
        release_compliance_ctrl()
        wait(0.1)
    
    def force_control_push_x():
        print("force_control_start")
        task_compliance_ctrl(stx=[100, 100, 100, 100, 100, 100])
        wait(0.1)
        set_desired_force(fd=[40, 0, 0, 0, 0, 0], dir=[1, 0, 0, 0, 0, 0], mod=DR_FC_MOD_REL)
        while True:
            if forcecheck(2) == 3: # force X detected
                # print("X force checked")
                wait(0.1)
                break
            elif forcecheck(2) == 2: # force YZ detected
                # print("force YZ checked")
                release_force()
                print("force 0 for 3 sec")
                wait(3)
                set_desired_force(fd=[40, 0, 0, 0, 0, 0], dir=[1, 0, 0, 0, 0, 0], mod=DR_FC_MOD_REL)
            elif forcecheck(2) == 1: # force none
                #print("force YZ not checked")
                wait(0.1)
        release_force()
        wait(0.1)
        release_compliance_ctrl()
        wait(0.1)
    
    def force_control_push_y():
        print("force_control_start")
        task_compliance_ctrl(stx=[100, 100, 100, 100, 100, 100])
        wait(0.1)
        set_desired_force(fd=[0, 40, 0, 0, 0, 0], dir=[0, 1, 0, 0, 0, 0], mod=DR_FC_MOD_REL)
        while True:
            if forcecheck(3) == 3: # force Y detected
                # print("Y force checked")
                wait(0.1)
                break
            elif forcecheck(3) == 2: # force XZ detected
                # print("force XZ checked")
                release_force()
                print("force 0 for 3 sec")
                wait(3)
                set_desired_force(fd=[0, 40, 0, 0, 0, 0], dir=[0, 1, 0, 0, 0, 0], mod=DR_FC_MOD_REL)
            elif forcecheck(3) == 1: # force none
                #print("force XZ not checked")
                wait(0.1)
        release_force()
        wait(0.1)
        release_compliance_ctrl()
        wait(0.1)

    def force_control_push_left_y():
        print("force_control_start")
        task_compliance_ctrl(stx=[100, 100, 100, 100, 100, 100])
        wait(0.1)
        set_desired_force(fd=[0, -40, 0, 0, 0, 0], dir=[0, 1, 0, 0, 0, 0], mod=DR_FC_MOD_REL)
        while True:
            if forcecheck(3) == 3: # force Z detected
                # print("z force checked")
                wait(0.1)
                break
            elif forcecheck(3) == 2: # force XY detected
                # print("force XY checked")
                # print("wait 2")
                release_force()
                print("force 0 for 3 sec")
                wait(3)
                set_desired_force(fd=[0, -40, 0, 0, 0, 0], dir=[0, 1, 0, 0, 0, 0], mod=DR_FC_MOD_REL)
            elif forcecheck(3) == 1: # force none
                #print("force XY not checked")
                wait(0.1)
        release_force()
        wait(0.1)
        release_compliance_ctrl()
        wait(0.1)

    # # 힘 제어 시작
    # def force_control_push_z():
    #     print("force_control_start")
    #     task_compliance_ctrl(stx=[100, 100, 100, 100, 100, 100])
    #     wait(0.1)
    #     set_desired_force(fd=[0, 0, -40, 0, 0, 0], dir=[0, 0, 1, 0, 0, 0], mod=DR_FC_MOD_ABS)
    #     while not check_force_condition(DR_AXIS_Z, max=9, ref=DR_BASE):
    #         pass
    #     release_force()
    #     wait(0.1)
    #     release_compliance_ctrl()
    #     wait(0.1)
    
    # def force_control_push_x():
    #     print("force_control_start")
    #     task_compliance_ctrl(stx=[100, 100, 100, 100, 100, 100])
    #     wait(0.1)
    #     set_desired_force(fd=[40, 0, 0, 0, 0, 0], dir=[1, 0, 0, 0, 0, 0], mod=DR_FC_MOD_REL)
    #     while not check_force_condition(DR_AXIS_X, max=7, ref=DR_BASE):
    #         pass
    #     release_force()
    #     wait(0.1)
    #     release_compliance_ctrl()
    #     wait(0.1)
    
    # def force_control_push_y():
    #     print("force_control_start")
    #     task_compliance_ctrl(stx=[100, 100, 100, 100, 100, 100])
    #     wait(0.1)
    #     set_desired_force(fd=[0, 40, 0, 0, 0, 0], dir=[0, 1, 0, 0, 0, 0], mod=DR_FC_MOD_REL)
    #     while not check_force_condition(DR_AXIS_Y, max=7, ref=DR_BASE):
    #         pass
    #     release_force()
    #     wait(0.1)
    #     release_compliance_ctrl()
    #     wait(0.1)

    # def force_control_push_left_y():
    #     print("force_control_start")
    #     task_compliance_ctrl(stx=[100, 100, 100, 100, 100, 100])
    #     wait(0.1)
    #     set_desired_force(fd=[0, -40, 0, 0, 0, 0], dir=[0, 1, 0, 0, 0, 0], mod=DR_FC_MOD_REL)
    #     while not check_force_condition(DR_AXIS_Y, max=7, ref=DR_BASE):
    #         pass
    #     release_force()
    #     wait(0.1)
    #     release_compliance_ctrl()
    #     wait(0.1)

    def arrange_right():
        movel(back_move, vel=VELOCITY, acc=ACC, mod=1)
        grip()
        movej([0,0,0,0,0,-90], vel=VELOCITY, acc=ACC,mod=1)
        movel(right_move, vel=VELOCITY, acc=ACC, mod=1)
        movel(ahead_move_4, vel=VELOCITY, acc=ACC, mod=1)
        force_control_push_y()
        movel(right_move, vel=VELOCITY, acc=ACC, mod=1)

    def arrange_left():
        movel(back_move, vel=VELOCITY, acc=ACC, mod=1)
        grip()
        movej([0,0,0,0,0,-90], vel=VELOCITY, acc=ACC,mod=1)
        movel(left_move, vel=VELOCITY, acc=ACC, mod=1)
        movel(ahead_move_4, vel=VELOCITY, acc=ACC, mod=1)
        force_control_push_left_y()
        movel(left_move, vel=VELOCITY, acc=ACC, mod=1)

    def handle_book(i):
        if i == 1:
            movej(section1, vel=VELOCITY, acc=ACC)
            movel(ahead_move_1, vel=VELOCITY, acc=ACC, mod=1)
            wait(0.1)
            force_control_push_x()
            wait(0.1)
            force_control_push_z()
            wait(0.1)
            release()
            arrange_left()
            movej(section1, vel=VELOCITY, acc=ACC)
            wait(1)
        elif i == 2:
            movej(section2, vel=VELOCITY, acc=ACC)
            movel(ahead_move_2, vel=VELOCITY, acc=ACC, mod=1)
            wait(0.1)
            force_control_push_x()
            wait(0.1)
            force_control_push_z()
            release()
            arrange_right()
            movej(section2, vel=VELOCITY, acc=ACC)
            wait(1)
        elif i == 3:
            movej(section3, vel=VELOCITY, acc=ACC)
            movej([0,0,0,0,0,180], vel=VELOCITY, acc=ACC,mod=1)
            movel(ahead_move_3, vel=VELOCITY, acc=ACC, mod=1)
            wait(0.1)
            force_control_push_x()
            wait(0.1)
            force_control_push_z()
            release()
            arrange_right()
            movej([0,0,0,0,0,-180], vel=VELOCITY, acc=ACC,mod=1)
            movej(section3, vel=VELOCITY, acc=ACC)
            wait(1)
        else:
            logging.warning(f"알 수 없는 명령 번호: {i}")
    
    def socket_connect():
        
        socket1 = server_socket_open(2000) #port=2000, socket_name = socket1, server
        while True:
            if server_socket_state(socket1):  # if server connected 1, not connected -> 0
            # 입력 red, blue, green, red 을 클라이언트에게 받음.
                # 색상 매핑 정의
                color_map = {
                'purple': 1,
                'red': 2,
                'brown': 3,
                # 필요에 따라 더 추가 가능
                }
                # 수신 데이터 처리
                data = server_socket_read(socket1, -1, -1)[1]
                coords = data.decode('utf-8').strip().split(',')
                print(coords)
                # 문자열 -> 숫자 변환
                coord_list = [color_map[color.strip()] for color in coords if color.strip() in color_map]

                server_socket_close(socket1)  #socket1 close
                return coord_list  # while 문 빠져나오기
                #break
                


    # 기본 설정
    set_tool("Tool Weight_250508")
    set_tcp("2FG_TCP")

    start_pos = START_POS.copy()
    grip_book_pos = GRIP_BOOK_POS.copy()


    def place_book(i):
        logging.info(f"{i}번 섹션에 책 배치 중")
        # movel(start_pos,vel=VELOCITY,acc=ACC,mod=0)
        handle_book(i)

        # 새로 배치된 책 한 권만 전송
        if i == 1:
            section = "Section1"
            title = "PurpleBook"
        elif i == 2:
            section = "Section2"
            title = "RedBook"
        elif i == 3:
            section = "Section3"
            title = "BrownBook"

        payload = {
            "section": section,
            "title": title
        }

        try:
            response = requests.post("http://localhost:5000/add", json=payload)
            response.raise_for_status()
            logging.info("서버로 책 정보 전송 성공")
        except requests.exceptions.RequestException as e:
            logging.error(f"서버 전송 실패: {e}")

    movej(START_POSJ, vel=VELOCITY_safe2,acc=ACC)

    coord_list = socket_connect()

    for i in coord_list:
        # 1. 책 위에서 누르기 위치로 이동 후 그립
        # movej(START_POSJ, vel=VELOCITY,acc=ACC)
        movel(start_pos,vel=VELOCITY,acc=ACC,mod=0)
        grip()
        wait(1)

        # 2. 힘 제어로 책을 누르기
        force_control_push_z()
        time.sleep(0.2)
        current_pos, _ = get_current_posx()
        time.sleep(0.2)
        current_pos_z = current_pos[2]
        time.sleep(0.2)
        # 책이 없어서 z값이 일정값 이하로 내려가면 정지후 초기 위치로 이동 >> 예외 처리 1
        if current_pos_z < 80:
            logging.info(f"쌓여 있는 책 없음")
            movej(init_pos, vel=VELOCITY, acc=ACC)
            break

        # 3. 살짝 올라간 후 오른쪽으로 이동
        movel_relative(RELATIVE_POS["up_book"])
        movel_relative(RELATIVE_POS["side"])
        movel_relative(RELATIVE_POS["down_book"])

        # 4. 책을 옆으로 밀기
        movel_relative(RELATIVE_POS["push_book"])

        # 5. 책 충돌 방지 이동
        movel_relative(RELATIVE_POS["collision_avoid_1"])
        movel_relative(RELATIVE_POS["collision_avoid_2"])

        # 6. 초기 위치로 돌아가기 (z축을 살짝 낮추기)
        movel_absolute(start_pos)
        start_pos[2] -= 50

        # 7. 책 잡을 위치로 이동하여 릴리즈, 다시 그립
        movel(RELATIVE_POS["side2"], vel=VELOCITY_safe2, acc=ACC_safe2, mod=1)
        wait(1)

        grip_book_pos[2] = current_pos[2] - 21
        movel_absolute(grip_book_pos)
        wait(1)
        release()
        wait(1)

        movel_relative(RELATIVE_POS["side3"])
        grip()
        wait(1)

        # 8. 책 들어올리기
        movel_relative(RELATIVE_POS["collision_avoid_3"])

        # # 9. 책 세로로 세우기
        # movel(START_POS_up, vel=VELOCITY_safe2, acc=ACC_safe2, mod=0)
        movej(START_POSJ, vel=VELOCITY_safe2, acc=ACC_safe2)
        wait(1)

        # 10. 책 배치하기
        place_book(i)
        
        # 11. 위치 초기화
        movej(START_POSJ, vel=VELOCITY_safe2, acc=ACC_safe2)

if __name__ == "__main__":
    main()

'''
안전구역 설정
책 이동 중 건드리면 멈춤

'''