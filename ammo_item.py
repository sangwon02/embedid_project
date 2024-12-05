import numpy as np
from PIL import Image, ImageDraw

class AmmoItem:
    def __init__(self, screen_width, screen_height):
        self.size = 20  # 아이템 크기
        self.position = np.array([
            np.random.randint(self.size, screen_width - self.size),
            np.random.randint(self.size, screen_height - self.size)
        ])  # 랜덤한 위치 생성
        self.image = self.create_image()

    def create_image(self):
        # `ammo.png` 이미지를 로드하고 리사이즈
        try:
            img = Image.open("./image/ammo.png").resize((self.size, self.size))
            return img
        except FileNotFoundError:
            # 이미지가 없으면 기본 원형 이미지 생성
            img = Image.new("RGBA", (self.size, self.size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.ellipse((0, 0, self.size, self.size), fill=(255, 165, 0, 255))  # 오렌지 색상
            return img

    def get_rect(self):
        # 충돌 영역 반환
        return [
            self.position[0] - self.size // 2,  # 왼쪽
            self.position[1] - self.size // 2,  # 위쪽
            self.position[0] + self.size // 2,  # 오른쪽
            self.position[1] + self.size // 2   # 아래쪽
        ]
