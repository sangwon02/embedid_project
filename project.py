import numpy as np
import random
import time
from PIL import Image, ImageDraw, ImageFont
from digitalio import DigitalInOut, Direction
from adafruit_rgb_display import st7789
import board
from ammo_item import AmmoItem
from bullet import Bullet
from character import Character
from enemy import Enemy
from joystick import Joystick

def main():
    joystick = Joystick()
    my_image = Image.new("RGB", (joystick.width, joystick.height))
    my_draw = ImageDraw.Draw(my_image)

    # 플레이어와 글꼴 초기화
    player = Character(joystick.width, joystick.height)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    font1 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)  # 더 작은 글꼴

    # 시작 화면
    start_image = Image.open("./image/start.png").resize((joystick.width, joystick.height))
    start_draw = ImageDraw.Draw(start_image)
    # 시작 화면 글자 (흰색, 검은색 테두리)
    start_draw.text((joystick.width // 2 - 70, joystick.height // 2 - 30), "TANK WAR", font=font, fill=(0, 0, 0))  # 검은색 글씨 (테두리 효과를 위해)
    start_draw.text((joystick.width // 2 - 70, joystick.height // 2 - 30), "TANK WAR", font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))  # 흰색 글씨, 검은색 테두리
    start_draw.text((joystick.width // 2 - 105, joystick.height // 2 + 10), "Press button to start", font=font1, fill=(0, 0, 0))  # 검은색 글씨 (테두리 효과를 위해)
    start_draw.text((joystick.width // 2 - 105, joystick.height // 2 + 10), "Press button to start", font=font1, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))  # 흰색 글씨, 검은색 테두리
    joystick.disp.image(start_image)

    # 버튼 입력 대기
    while joystick.get_command() is None:  # 어떤 버튼이든 눌리면 게임 시작
        time.sleep(0.1)

    # 배경 이미지
    background_image = Image.open("./image/background.png").resize((joystick.width, joystick.height))

    # 폭발 이미지 로드
    boom_image = Image.open("./image/effect_boom.png").resize((50, 50))  # 폭발 이미지 로드 및 크기 조정

    # 라운드 설정
    rounds_config = [
        {'duration': 30, 'spawn_sides': ['top', 'bottom'], 'spawn_rate': 0.4},
        {'duration': 30, 'spawn_sides': ['top', 'bottom', 'left', 'right'], 'spawn_rate': 0.6},
        {'duration': 30, 'spawn_sides': ['top', 'bottom', 'left', 'right'], 'spawn_rate': 0.5},
    ]

    # 점수 담을 변수
    score = 0

    for current_round, config in enumerate(rounds_config, start=1):
        round_start = time.time()
        enemys = []
        bullets = []
        ammo_items = []
        explosions = []  # 폭발 효과를 저장할 리스트
        ammo_count = 5  # 탄알 개수
        max_ammo_items = 1  # 동시에 생성될 수 있는 탄약 아이템 개수 제한
        spawn_interval = config['spawn_rate']
        last_spawn_time = round_start
        last_fire_time = 0  # 마지막 발사 시간

        while time.time() - round_start < config['duration']:
            command_list = joystick.get_command()
            player.move(command_list)

            # 탄알 발사
            current_time = time.time()
            if (not joystick.button_A.value or not joystick.button_B.value):
                if current_time - last_fire_time >= 0.5:  # 발사 간격 제한
                    if ammo_count > 0:
                        bullets.append(player.fire_bullet())
                        ammo_count -= 1
                        last_fire_time = current_time
                    else:  # 탄약 부족 메시지 표시
                        ammo_message_start = time.time()  # 메시지 표시 시작 시간
                        while time.time() - ammo_message_start < 0.3:  # 0.3초 동안 메시지 표시
                            # 게임 계속 진행
                            command_list = joystick.get_command()  # 조이스틱 입력 받기
                            player.move(command_list)  # 플레이어 이동

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

                                        # 폭발 효과 추가
                                        explosion_position = ((bullet_rect[0] + enemy_rect[0]) // 2, (bullet_rect[1] + enemy_rect[1]) // 2)  # 폭발 위치 계산
                                        explosions.append((explosion_position, time.time()))  # 폭발 효과와 시간을 explosions 리스트에 추가

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
                                    # 게임 오버 글자 (빨간색, 검은색 테두리)
                                    my_draw.text((joystick.width // 2 - 75, joystick.height // 2 - 16), "Game Over", font=font, fill=(255, 0, 0), stroke_width=2, stroke_fill=(0, 0, 0))
                                    joystick.disp.image(my_image)
                                    return

                            # 플레이어와 탄약 아이템 충돌 처리
                            for item in ammo_items[:]:
                                item_rect = item.get_rect()
                                if (abs(player_rect[0] - item_rect[0]) < 15 and
                                        abs(player_rect[1] - item_rect[1]) < 15):
                                    ammo_count = 5  # 탄약 충전
                                    ammo_items.remove(item)


                            my_image.paste(background_image, (0, 0))  # 배경 그리기

                            # 폭발 효과 그리기
                            for explosion_position, explosion_time in explosions[:]:
                                elapsed_time = time.time() - explosion_time
                                if elapsed_time <= 0.3:  # 0.3초 동안 폭발 이미지 표시
                                    my_image.paste(boom_image, tuple(np.array(explosion_position) - np.array([boom_image.width // 2, boom_image.height // 2])), boom_image)  # 폭발 이미지 그리기
                                else:
                                    explosions.remove((explosion_position, explosion_time))  # 0.3초가 지나면 폭발 효과 제거

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

                            # 플레이어 이미지
                            tank_image = player.get_current_image()
                            my_image.paste(tank_image, tuple(player.position[:2]), tank_image)


                            # UI 업데이트
                            remaining_time = max(0, config['duration'] - int(current_time - round_start))
                            text_elements = [
                                (f"Time: {remaining_time}", (joystick.width // 2 - 40, 10)),
                                (f"Score: {score}", (10, joystick.height - 30)),
                                (f"Ammo: {ammo_count}", (10, joystick.height - 60)),
                            ]
                            for text, position in text_elements:
                                my_draw.text((position[0] - 1, position[1] - 1), text, font=font1, fill=(0, 0, 0))
                                my_draw.text((position[0] + 1, position[1] + 1), text, font=font1, fill=(0, 0, 0))
                                my_draw.text(position, text, font=font1, fill=(255, 255, 255), stroke_width=1, stroke_fill=(0, 0, 0))

                            # 탄약 부족 메시지 (더 작은 글씨, 회색)
                            my_draw.text((joystick.width // 2 - 50, joystick.height // 2 - 10), "No Ammo!", font=font1, fill=(255, 255, 255), stroke_width=1, stroke_fill=(0, 0, 0))

                            joystick.disp.image(my_image)
                            time.sleep(0.05)
                            
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

                        # 폭발 효과 추가
                        explosion_position = ((bullet_rect[0] + enemy_rect[0]) // 2, (bullet_rect[1] + enemy_rect[1]) // 2)  # 폭발 위치 계산
                        explosions.append((explosion_position, time.time()))  # 폭발 효과와 시간을 explosions 리스트에 추가

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
                    # 게임 오버 글자 (빨간색, 검은색 테두리)
                    my_draw.text((joystick.width // 2 - 75, joystick.height // 2 - 16), "Game Over", font=font, fill=(255, 0, 0), stroke_width=2, stroke_fill=(0, 0, 0))
                    joystick.disp.image(my_image)
                    return

            # 플레이어와 탄약 아이템 충돌 처리
            for item in ammo_items[:]:
                item_rect = item.get_rect()
                if (abs(player_rect[0] - item_rect[0]) < 15 and
                        abs(player_rect[1] - item_rect[1]) < 15):
                    ammo_count = 5  # 탄약 충전
                    ammo_items.remove(item)

            my_image.paste(background_image, (0, 0))

            # 폭발 효과 그리기
            for explosion_position, explosion_time in explosions[:]:
                elapsed_time = time.time() - explosion_time
                if elapsed_time <= 0.3:  # 0.3초 동안 폭발 이미지 표시
                    my_image.paste(boom_image, tuple(np.array(explosion_position) - np.array([boom_image.width // 2, boom_image.height // 2])), boom_image)  # 폭발 이미지 그리기
                else:
                    explosions.remove((explosion_position, explosion_time))  # 0.3초가 지나면 폭발 효과 제거

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


            # 플레이어 이미지
            tank_image = player.get_current_image()
            my_image.paste(tank_image, tuple(player.position[:2]), tank_image)

            # UI 업데이트
            remaining_time = max(0, config['duration'] - int(current_time - round_start))
            text_elements = [
                (f"Time: {remaining_time}", (joystick.width // 2 - 40, 10)),
                (f"Score: {score}", (10, joystick.height - 30)),
                (f"Ammo: {ammo_count}", (10, joystick.height - 60)),
            ]
            for text, position in text_elements:
                # 게임 중 UI 글자 (흰색, 검은색 테두리)
                my_draw.text((position[0] - 1, position[1] - 1), text, font=font1, fill=(0, 0, 0))  # 검은색 글씨 (테두리 효과를 위해)
                my_draw.text((position[0] + 1, position[1] + 1), text, font=font1, fill=(0, 0, 0))  # 검은색 글씨 (테두리 효과를 위해)
                my_draw.text(position, text, font=font1, fill=(255, 255, 255), stroke_width=1, stroke_fill=(0, 0, 0))  # 흰색 글씨, 검은색 테두리


            joystick.disp.image(my_image)
            time.sleep(0.05)

        # 라운드 종료 화면
        end_image = Image.open("./image/end.png").resize((joystick.width, joystick.height))
        end_draw = ImageDraw.Draw(end_image)
        if current_round < len(rounds_config):
            # 라운드 종료 글자 (흰색, 검은색 테두리)
            end_draw.text((joystick.width // 2 - 105, joystick.height // 2 - 16), f"Round {current_round + 1} START", font=font, fill=(0, 0, 0))  # 검은색 글씨 (테두리 효과를 위해)
            end_draw.text((joystick.width // 2 - 105, joystick.height // 2 - 16), f"Round {current_round + 1} START", font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))  # 흰색 글씨, 검은색 테두리
            joystick.disp.image(end_image)
            time.sleep(1.5)
        else:  # 마지막 라운드면 게임 종료 메시지 출력
            end_draw.text((joystick.width // 2 - 90, joystick.height // 2 - 40), "Mission Complete!", font=font1, fill=(0, 0, 0))  # 검은색 글씨 (테두리 효과를 위해)
            end_draw.text((joystick.width // 2 - 90, joystick.height // 2 - 40), "Mission Complete!", font=font1, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))  # 흰색 글씨, 검은색 테두리
            end_draw.text((joystick.width // 2 - 50, joystick.height // 2 + 10), f"Score: {score}", font=font, fill=(0, 0, 0))  # 검은색 글씨 (테두리 효과를 위해)
            end_draw.text((joystick.width // 2 - 50, joystick.height // 2 + 10), f"Score: {score}", font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))  # 흰색 글씨, 검은색 테두리
            joystick.disp.image(end_image)
            time.sleep(1.5)
            break  # 게임 종료

if __name__ == "__main__":
    main()