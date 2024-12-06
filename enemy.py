import random
import time
import numpy as np
from PIL import Image

class Enemy:
    # 게임에 등장하는 적을 나타냄
    def __init__(self, width, height, spawn_sides):
        # 적 객체를 초기화함
        # 적의 크기, 이미지, 죽음 상태 등을 설정함.
        self.size = 50
        self.image = Image.open("./image/enemy.png").resize((self.size, self.size))  # 크기 조정된 이미지
        self.dead_image = Image.open("./image/enemy_d.png").resize((self.size, self.size))  # 죽음 상태 이미지
        self.is_dead = False  # 죽음 상태
        self.dead_time = None  # 죽은 시간

        # 위치 설정 (spawn_sides에서 랜덤하게 선택된 면에서 생성)
        side = random.choice(spawn_sides)
        if side == 'top':
            self.position = np.array([random.randint(0, width), 0])
            self.direction = [random.uniform(-1, 1), random.uniform(0.5, 1)]
        elif side == 'bottom':
            self.position = np.array([random.randint(0, width), height+25])
            self.direction = [random.uniform(-1, 1), random.uniform(-1, -0.5)]
        elif side == 'left':
            self.position = np.array([0, random.randint(0, height)])
            self.direction = [random.uniform(0.5, 1), random.uniform(-1, 1)]
        else:
            self.position = np.array([width+20, random.randint(0, height)])
            self.direction = [random.uniform(-1, -0.5), random.uniform(-1, 1)]

        # 이동 속도 설정 (랜덤)
        self.velocity = np.array([random.choice([-5, -4, -3, 3, 4, 5]), random.choice([-5, -4, -3, 3, 4, 5])])

    def move(self):
        if not self.is_dead:  # 죽지 않은 경우에만 이동
            self.position += self.velocity

    def get_rect(self):
        # 적의 충돌 영역을 반환함
        return [
            self.position[0] - self.size // 2, self.position[1] - self.size // 2,
            self.position[0] + self.size // 2, self.position[1] + self.size // 2,
        ]

    def get_current_image(self):
        # 현재 상태에 맞는 이미지를 반환함 (죽음 상태에 따라 이미지 변경)
        if self.is_dead:
            if self.dead_time is None:  # 처음으로 죽었을 때 시간 기록
                self.dead_time = time.time()
                return self.dead_image
            elif time.time() - self.dead_time <= 1:  # 죽은 지 1초 이내면 dead_image 반환
                return self.dead_image
        return self.image  # 살아있는 경우 기본 이미지 반환

    def get_draw_position(self):
        # 이미지 중앙을 맞추기 위한 계산된 위치를 반환함
        return tuple(self.position - np.array([(self.size // 2) + 20, (self.size // 2) + 20]))