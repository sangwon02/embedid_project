import numpy as np
import random
import time
from PIL import Image, ImageDraw, ImageFont
from digitalio import DigitalInOut, Direction
from adafruit_rgb_display import st7789
import board

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
            img = Image.open("ammo.png").resize((self.size, self.size))
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


# 포탄 클래스
class Bullet:
    def __init__(self, position, direction, size=10, speed=15):
        self.position = np.array(position)
        self.direction = direction
        self.size = size
        self.image = Image.open("missile.png").resize((size, size))  # 이미지 크기 조정
        # 각 방향에 따른 속도 벡터 설정
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

    def move(self):
        self.position += self.velocity

    def get_image_position(self):
        # 이미지의 위치를 중앙에 맞추기 위한 계산
        return tuple(self.position - np.array([self.size // 2, self.size // 2]))

    def get_rect(self):
        x, y = self.position
        half_size = self.size // 2
        return [x - half_size, y - half_size, x + half_size, y + half_size]



class Character:
    def __init__(self, width, height):
        self.size = 30
        self.position = np.array([width // 2 - self.size // 2, height // 2 - self.size // 2,
                                  width // 2 + self.size // 2, height // 2 + self.size // 2])
        self.direction = 'U'

        # 이미지 로드
        self.images = {
            'U': Image.open("tank_U.png").resize((self.size-5, self.size+15)),
            'D': Image.open("tank_D.png").resize((self.size-5, self.size+15)),
            'L': Image.open("tank_L.png").resize((self.size+15, self.size-5)),
            'R': Image.open("tank_R.png").resize((self.size+15, self.size-5)),
            'UL': Image.open("tank_UL.png").resize((self.size+15, self.size+15)),
            'UR': Image.open("tank_UR.png").resize((self.size+15, self.size+15)),
            'DL': Image.open("tank_DL.png").resize((self.size+15, self.size+15)),
            'DR': Image.open("tank_DR.png").resize((self.size+15, self.size+15)),
        }

    def move(self, command_list=None):
        speed = 10  # 기본 이동 속도
        diagonal_speed = int(speed / (2 ** 0.5))  # 대각선 이동 속도 계산 (피타고라스의 정리)

        if command_list:
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
        return self.images[self.direction]

    def fire_bullet(self):
        # 캐릭터의 중앙에서 포탄 발사
        center = [(self.position[0] + self.position[2]) // 2,
                  (self.position[1] + self.position[3]) // 2]
        return Bullet(center, self.direction)

    def get_rect(self):
        # 캐릭터의 충돌 범위를 계산하여 반환
        return self.position[0], self.position[1], self.position[2], self.position[3]  # (left, top, right, bottom)



class Enemy:
    def __init__(self, width, height, spawn_sides):
        self.size = 50
        self.image = Image.open("enemy.png").resize((self.size, self.size))  # 크기 조정된 이미지
        self.dead_image = Image.open("enemy_d.png").resize((self.size, self.size))
        self.is_dead = False
        self.dead_time = None

        # 위치 설정
        side = random.choice(spawn_sides)
        if side == 'top':
            self.position = np.array([random.randint(0, width), 0])
            self.direction = [random.uniform(-1, 1), random.uniform(0.5, 1)]
        elif side == 'bottom':
            self.position = np.array([random.randint(0, width), height])
            self.direction = [random.uniform(-1, 1), random.uniform(-1, -0.5)]
        elif side == 'left':
            self.position = np.array([0, random.randint(0, height)])
            self.direction = [random.uniform(0.5, 1), random.uniform(-1, 1)]
        else:
            self.position = np.array([width, random.randint(0, height)])
            self.direction = [random.uniform(-1, -0.5), random.uniform(-1, 1)]

        # 이동 속도 설정
        self.velocity = np.array([random.choice([-5, -4, -3, 3, 4, 5]), random.choice([-5, -4, -3, 3, 4, 5])])

    def move(self):
        if not self.is_dead:
            self.position += self.velocity

    def get_rect(self):
        return [
            self.position[0] - self.size // 2, self.position[1] - self.size // 2,
            self.position[0] + self.size // 2, self.position[1] + self.size // 2,
        ]

    def get_current_image(self):
        # 적이 죽은 상태인지 확인
        if self.is_dead:
            if self.dead_time is None:  # 처음으로 죽었을 때 시간 기록
                self.dead_time = time.time()
                return self.dead_image
            elif time.time() - self.dead_time <= 1:  # 죽은 지 1초 이내면 dead_image 반환
                return self.dead_image
        return self.image  # 살아있는 경우 기본 이미지 반환

    def get_draw_position(self):
        # 이미지 중앙을 맞추기 위한 계산
        return tuple(self.position - np.array([(self.size // 2) + 20, (self.size // 2) + 20]))



# 조이스틱 및 디스플레이 설정
class Joystick:
    def __init__(self):
        self.cs_pin = DigitalInOut(board.CE0)
        self.dc_pin = DigitalInOut(board.D25)
        self.reset_pin = DigitalInOut(board.D24)
        self.BAUDRATE = 24000000

        self.spi = board.SPI()
        self.disp = st7789.ST7789(
            self.spi,
            height=240,
            y_offset=80,
            rotation=180,
            cs=self.cs_pin,
            dc=self.dc_pin,
            rst=self.reset_pin,
            baudrate=self.BAUDRATE,
        )

        # Input pins
        self.button_A = DigitalInOut(board.D5) 
        self.button_A.direction = Direction.INPUT

        self.button_B = DigitalInOut(board.D6) 
        self.button_B.direction = Direction.INPUT

        self.button_L = DigitalInOut(board.D27)
        self.button_L.direction = Direction.INPUT

        self.button_R = DigitalInOut(board.D23)
        self.button_R.direction = Direction.INPUT

        self.button_U = DigitalInOut(board.D17)
        self.button_U.direction = Direction.INPUT

        self.button_D = DigitalInOut(board.D22)
        self.button_D.direction = Direction.INPUT

        # Turn on the Backlight
        self.backlight = DigitalInOut(board.D26)
        self.backlight.switch_to_output()
        self.backlight.value = True

        self.width = self.disp.width
        self.height = self.disp.height

    def get_command(self):
        commands = []
        if not self.button_U.value:
            commands.append('up_pressed')
        if not self.button_D.value:
            commands.append('down_pressed')
        if not self.button_L.value:
            commands.append('left_pressed')
        if not self.button_R.value:
            commands.append('right_pressed')
        if not self.button_A.value:
            commands.append('a_pressed')
        if not self.button_B.value:
            commands.append('b_pressed')
        return commands if commands else None

def main():
    joystick = Joystick()
    my_image = Image.new("RGB", (joystick.width, joystick.height))
    my_draw = ImageDraw.Draw(my_image)

    # 배경 이미지
    background_image = Image.open("/home/sangw/embedid_project/background.jpg").resize((joystick.width, joystick.height))

    # 플레이어와 글꼴 초기화
    player = Character(joystick.width, joystick.height)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    font1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    # 라운드 설정
    rounds_config = [
        {'duration': 5, 'spawn_sides': ['top', 'bottom'], 'spawn_rate': 0.2},
        {'duration': 5, 'spawn_sides': ['top', 'bottom', 'left', 'right'], 'spawn_rate': 0.2},
        {'duration': 5, 'spawn_sides': ['top', 'bottom', 'left', 'right'], 'spawn_rate': 0.2},
    ]

    # 점수 초기화
    score = 0

    for current_round, config in enumerate(rounds_config, start=1):
        round_start = time.time()
        enemys = []
        bullets = []
        ammo_items = []
        ammo_count = 10  # 탄알 개수 초기화
        max_ammo_items = 1  # 동시에 생성될 수 있는 탄약 아이템 개수 제한
        spawn_interval = config['spawn_rate']
        last_spawn_time = round_start
        last_fire_time = 0  # 마지막 발사 시간

        while time.time() - round_start < config['duration']:
            command_list = joystick.get_command()
            player.move(command_list)

            # 탄알 발사
            current_time = time.time()
            if (not joystick.button_A.value or not joystick.button_B.value) and ammo_count > 0:
                if current_time - last_fire_time >= 0.5:  # 발사 간격 제한
                    bullets.append(player.fire_bullet())
                    ammo_count -= 1
                    last_fire_time = current_time

            # 적 생성 및 탄약 아이템 생성
            if current_time - last_spawn_time > spawn_interval:
                enemys.append(Enemy(joystick.width, joystick.height, config['spawn_sides']))
                last_spawn_time = current_time
                if len(ammo_items) < max_ammo_items and random.random() < 0.2:
                    ammo_items.append(AmmoItem(joystick.width, joystick.height))

            # 탄알 이동 및 화면 밖 제거
            for bullet in bullets[:]:
                bullet.move()
                if (bullet.position[0] < 0 or bullet.position[0] > joystick.width or
                        bullet.position[1] < 0 or bullet.position[1] > joystick.height):
                    bullets.remove(bullet)

            # 적 이동 및 화면 밖 제거
            for enemy in enemys[:]:
                enemy.move()
                margin = 50  # 화면 경계에서 여유를 줄 마진 값
                if (enemy.position[0] < -margin or enemy.position[0] > joystick.width + margin or
                        enemy.position[1] < -margin or enemy.position[1] > joystick.height + margin):
                    enemys.remove(enemy)

            # 탄알과 적 충돌 처리
            for bullet in bullets[:]:
                bullet_rect = bullet.get_rect()
                for enemy in enemys[:]:
                    if enemy.is_dead:  # 죽은 적은 충돌 체크 제외
                        continue
                    enemy_rect = enemy.get_rect()
                    if (abs(bullet_rect[0] - enemy_rect[0]) < 18 and  # 충돌 범위
                            abs(bullet_rect[1] - enemy_rect[1]) < 18):
                        enemy.is_dead = True
                        enemy.dead_time = time.time()
                        bullets.remove(bullet)
                        score += 1
                        break

            # 죽은 적 제거
            for enemy in enemys[:]:
                if enemy.is_dead and time.time() - enemy.dead_time > 1:
                    enemys.remove(enemy)

            # 플레이어와 적 충돌 처리
            player_rect = player.get_rect()
            for enemy in enemys[:]:
                if enemy.is_dead:  # 죽은 적은 충돌 체크 제외
                    continue
                enemy_rect = enemy.get_rect()
                if (abs(player_rect[0] - enemy_rect[0]) < 15 and  # 충돌 범위
                        abs(player_rect[1] - enemy_rect[1]) < 15):
                    my_draw.rectangle((0, 0, joystick.width, joystick.height), fill=(255, 255, 255))
                    my_draw.text((joystick.width // 2 - 70, joystick.height // 2 - 16), "Game Over", font=font, fill=(255, 0, 0))
                    joystick.disp.image(my_image)
                    return

            # 플레이어와 탄약 아이템 충돌 처리
            for item in ammo_items[:]:
                item_rect = item.get_rect()
                if (abs(player_rect[0] - item_rect[0]) < 15 and 
                        abs(player_rect[1] - item_rect[1]) < 15):
                    ammo_count = 10  # 탄약 충전
                    ammo_items.remove(item)

            my_image.paste(background_image, (0, 0))

            # 플레이어 이미지
            tank_image = player.get_current_image()
            my_image.paste(tank_image, tuple(player.position[:2]), tank_image)

            # 총알 그리기
            for bullet in bullets:
                bullet_position = bullet.get_image_position()
                my_image.paste(bullet.image, bullet_position, bullet.image)

            # 적 그리기
            for enemy in enemys:
                enemy_image = enemy.get_current_image()
                enemy_position = enemy.get_draw_position()  # 중앙 정렬된 위치 계산
                my_image.paste(enemy_image, enemy_position, enemy_image)


            # 탄약 아이템 그리기
            for item in ammo_items:
                my_image.paste(item.image, tuple(item.position), item.image)

            # UI 업데이트
            remaining_time = max(0, config['duration'] - int(current_time - round_start))
            text_elements = [
                (f"Time: {remaining_time}", (joystick.width // 2 - 40, 10)),
                (f"Score: {score}", (10, joystick.height - 30)),
                (f"Ammo: {ammo_count}", (10, joystick.height - 60)),
            ]
            for text, position in text_elements:
                my_draw.text(
                    (position[0] - 1, position[1] - 1), text, font=font1, fill=(128, 128, 128)  # 테두리
                )
                my_draw.text(
                    (position[0] + 1, position[1] + 1), text, font=font1, fill=(128, 128, 128)
                )
                my_draw.text(position, text, font=font1, fill=(255, 255, 255))  # 흰색 본문

            joystick.disp.image(my_image)
            time.sleep(0.05)

        # 라운드 종료 메시지
        my_draw.rectangle((0, 0, joystick.width, joystick.height), fill=(0, 0, 0))  # 검은 배경
        if current_round < len(rounds_config):
            my_draw.text(
                (joystick.width // 2 - 95, joystick.height // 2 - 16),
                f"Round {current_round + 1} START",
                font=font,
                fill=(255, 255, 255)  # 흰색 글자
            )
            joystick.disp.image(my_image)
            time.sleep(1.5)

    # 게임 종료 메시지
    my_draw.rectangle((0, 0, joystick.width, joystick.height), fill=(0, 0, 0))  # 검은 배경
    my_draw.text(
        (joystick.width // 2 - 60, joystick.height // 2 - 40),
        "Mission Complete!",
        font=font1,
        fill=(255, 255, 255)  # 흰색 글자
    )
    my_draw.text(
        (joystick.width // 2 - 50, joystick.height // 2 + 10),
        f"Score: {score}",
        font=font,
        fill=(255, 255, 255)  # 흰색 글자
    )
    joystick.disp.image(my_image)
    time.sleep(1.5)


if __name__ == "__main__":
    main()