import numpy as np
from PIL import Image
from bullet import Bullet  # bullet 모듈에서 Bullet 클래스를 가져옴

class Character:
    def __init__(self, width, height):
        # 캐릭터 객체를 초기화함
        self.size = 30  # 캐릭터의 크기
        # 캐릭터의 초기 위치를 화면 중앙에 설정
        self.position = np.array([
            width // 2 - self.size // 2, 
            height // 2 - self.size // 2,
            width // 2 + self.size // 2, 
            height // 2 + self.size // 2
        ])  
        self.direction = 'U'  # 캐릭터의 초기 방향 (위쪽)

        # 방향별 이미지 로드 및 크기 조정
        self.images = {
            'U': Image.open("./image/tank_U.png").resize((self.size-5, self.size+15)),
            'D': Image.open("./image/tank_D.png").resize((self.size-5, self.size+15)),
            'L': Image.open("./image/tank_L.png").resize((self.size+15, self.size-5)),
            'R': Image.open("./image/tank_R.png").resize((self.size+15, self.size-5)),
            'UL': Image.open("./image/tank_UL.png").resize((self.size+15, self.size+15)),
            'UR': Image.open("./image/tank_UR.png").resize((self.size+15, self.size+15)),
            'DL': Image.open("./image/tank_DL.png").resize((self.size+15, self.size+15)),
            'DR': Image.open("./image/tank_DR.png").resize((self.size+15, self.size+15)),
        }

    def move(self, command_list=None):
        # 캐릭터를 이동시킴
        speed = 10  # 기본 이동 속도
        diagonal_speed = int(speed / (2 ** 0.5))  # 대각선 이동 속도 계산

        if command_list:  # command_list가 비어있지 않으면
            # 키 입력에 따라 캐릭터의 방향과 위치를 업데이트
            if 'up_pressed' in command_list:
                if 'left_pressed' in command_list:
                    self.direction = 'UL'
                    self.position[0] -= diagonal_speed
                    self.position[2] -= diagonal_speed
                    self.position[1] -= diagonal_speed
                    self.position[3] -= diagonal_speed
                elif 'right_pressed' in command_list:
                    self.direction = 'UR'
                    self.position[0] += diagonal_speed
                    self.position[2] += diagonal_speed
                    self.position[1] -= diagonal_speed
                    self.position[3] -= diagonal_speed
                else:
                    self.direction = 'U'
                    self.position[1] -= speed
                    self.position[3] -= speed

            elif 'down_pressed' in command_list:
                if 'left_pressed' in command_list:
                    self.direction = 'DL'
                    self.position[0] -= diagonal_speed
                    self.position[2] -= diagonal_speed
                    self.position[1] += diagonal_speed
                    self.position[3] += diagonal_speed
                elif 'right_pressed' in command_list:
                    self.direction = 'DR'
                    self.position[0] += diagonal_speed
                    self.position[2] += diagonal_speed
                    self.position[1] += diagonal_speed
                    self.position[3] += diagonal_speed
                else:
                    self.direction = 'D'
                    self.position[1] += speed
                    self.position[3] += speed

            if 'left_pressed' in command_list and 'up_pressed' not in command_list and 'down_pressed' not in command_list:
                self.direction = 'L'
                self.position[0] -= speed
                self.position[2] -= speed
            elif 'right_pressed' in command_list and 'up_pressed' not in command_list and 'down_pressed' not in command_list:
                self.direction = 'R'
                self.position[0] += speed
                self.position[2] += speed

    def get_current_image(self):
        #현재 방향에 맞는 이미지를 반환함
        return self.images[self.direction]

    def fire_bullet(self):
        # 캐릭터의 중앙에서 포탄 발사
        center = [(self.position[0] + self.position[2]) // 2,
                  (self.position[1] + self.position[3]) // 2]
        return Bullet(center, self.direction)  # Bullet 객체 생성 및 반환

    def get_rect(self):
        #캐릭터의 충돌 영역을 반환
        return self.position[0], self.position[1], self.position[2], self.position[3]