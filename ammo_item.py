import numpy as np
from PIL import Image, ImageDraw

class AmmoItem: 
    def __init__(self, screen_width, screen_height):
        # 탄약 아이템 객체를 초기화함.
        self.size = 20  # 아이템 크기
        # 랜덤한 위치 생성 (화면 경계 내)
        self.position = np.array([
            np.random.randint(self.size, screen_width - self.size), 
            np.random.randint(self.size, screen_height - self.size)
        ])  
        self.image = self.create_image()  # 이미지 생성

    def create_image(self): 
        # 아이템의 이미지를 생성함. ammo.png 파일을 읽어와 크기를 조정함
        img = Image.open("./image/ammo.png").resize((self.size, self.size))
        return img

    def get_rect(self):
        # 아이템의 충돌 영역을 반환함
        return [
            self.position[0] - self.size // 2, 
            self.position[1] - self.size // 2, 
            self.position[0] + self.size // 2, 
            self.position[1] + self.size // 2 
        ]