import numpy as np
from PIL import Image

class Bullet:
    # 총알 객체를 초기화함.
    def __init__(self, position, direction, size=10, speed=15):
        # 총알의 초기 위치, 방향, 크기, 속도를 설정함
        self.position = np.array(position)
        self.direction = direction
        self.size = size
        # 이미지 로드 및 크기 조정
        self.image = Image.open("./image/missile.png").resize((size, size))

        # 방향별 속도 벡터 설정
        self.velocity = {
            'U': np.array([0, -speed]),
            'D': np.array([0, speed]),
            'L': np.array([-speed, 0]),
            'R': np.array([speed, 0]),
            'UL': np.array([-speed, -speed]),
            'UR': np.array([speed, -speed]),
            'DL': np.array([-speed, speed]),
            'DR': np.array([speed, speed]),
        }[direction]

        # 대각선 방향일 때 자연스럽게 나오도록 오프셋 적용
        offset = {
            'UL': np.array([-5, -5]),
            'UR': np.array([20, 0]),
            'DL': np.array([0, 10]),
            'DR': np.array([10, 10]),
        }.get(direction, np.array([0, 0]))

        self.position += offset

    def move(self):
        # 총알을 이동시킴
        self.position += self.velocity

    def get_image_position(self):
        # 이미지의 위치를 반한
        return tuple(self.position - np.array([self.size // 2, self.size // 2]))

    def get_rect(self):
        # 총알의 충돌 영역을 반환
        x, y = self.position
        half_size = self.size // 2
        return [x - half_size, y - half_size, x + half_size, y + half_size]