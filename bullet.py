import numpy as np
from PIL import Image

class Bullet:
    def __init__(self, position, direction, size=10, speed=15):
        self.position = np.array(position)
        self.direction = direction
        self.size = size
        self.image = Image.open("./image/missile.png").resize((size, size))

        # 방향별 속도 벡터
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

        # 대각선 방향일 때 약간 오른쪽으로 오프셋 적용
        offset = {
            'UL': np.array([-5, -5]),
            'UR': np.array([20, 0]),
            'DL': np.array([0, 10]),
            'DR': np.array([10, 10]),
        }.get(direction, np.array([0, 0]))  # 대각선이 아니면 오프셋 없음

        self.position += offset

    def move(self):
        self.position += self.velocity

    def get_image_position(self):
        # 이미지의 위치를 중앙에 맞추기 위한 계산
        return tuple(self.position - np.array([self.size // 2, self.size // 2]))

    def get_rect(self):
        x, y = self.position
        half_size = self.size // 2
        return [x - half_size, y - half_size, x + half_size, y + half_size]
