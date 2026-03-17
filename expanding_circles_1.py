import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 1500, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Expanding Circles")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
font_timer = pygame.font.Font(None, 52)
font_level = pygame.font.Font(None, 30)

circles = []
last_spawn_time = 0

# 타이머
start_time = pygame.time.get_ticks()


def get_level_params(elapsed_s):
    """
    경과 시간(초)에 따라 (생성 간격ms, 속도 배율, 레벨) 반환.
    0~10초:  느린 단계 (레벨 1)
    10초 이후: 10초마다 레벨 상승
    """
    if elapsed_s < 10:
        spawn_interval = 1500   # 1.5초마다 생성
        speed_mult = 0.4
        level = 1
    else:
        level = min(2 + int((elapsed_s - 10) // 10), 11)
        extra = level - 1  # 1~10
        spawn_interval = max(200, 1500 - extra * 130)  # 최소 200ms
        speed_mult = 0.4 + extra * 0.25               # 최대 2.9배
    return int(spawn_interval), speed_mult, int(level)


def spawn_circle(speed_mult):
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    max_radius = random.randint(60, 150)
    growth_speed = random.uniform(0.5, 2.5) * speed_mult
    return {
        "x": x, "y": y,
        "radius": 0,
        "max_radius": max_radius,
        "speed": growth_speed,
        "alpha": 255
    }


running = True
while running:
    dt = clock.tick(60)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 경과 시간 계산
    elapsed_ms = current_time - start_time
    elapsed_s = elapsed_ms / 1000.0

    # 현재 레벨 파라미터
    spawn_interval, speed_mult, level = get_level_params(elapsed_s)

    # 일정 간격마다 새 원 생성
    if current_time - last_spawn_time > spawn_interval:
        circles.append(spawn_circle(speed_mult))
        last_spawn_time = current_time

    # 원 업데이트
    for circle in circles:
        if circle["radius"] < circle["max_radius"]:
            circle["radius"] += circle["speed"]
        else:
            circle["alpha"] -= 3

    # 완전히 사라진 원 제거
    circles = [c for c in circles if c["alpha"] > 0]

    screen.fill(WHITE)

    # 원 그리기
    for circle in circles:
        r = int(circle["radius"])
        if r <= 0:
            continue
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        alpha = max(0, min(255, int(circle["alpha"])))
        pygame.draw.circle(surf, (0, 0, 255, alpha), (r, r), r)
        pygame.draw.circle(surf, (0, 0, 180, alpha), (r, r), r, 2)
        screen.blit(surf, (circle["x"] - r, circle["y"] - r))

    # FPS / 원 개수
    fps_surface = font.render("FPS: " + str(int(clock.get_fps())), True, BLACK)
    screen.blit(fps_surface, (10, 10))

    count_surface = font.render(f"Circles: {len(circles)}", True, BLACK)
    screen.blit(count_surface, (10, 40))

    # 레벨 및 다음 레벨까지 시간 표시
    if elapsed_s < 10:
        next_level_in = 10 - elapsed_s
        level_color = (0, 150, 0)
        level_label = "SLOW"
    else:
        next_level_in = 10 - ((elapsed_s - 10) % 10)
        level_color = (180, 60, 0) if level < 6 else (200, 0, 0)
        level_label = f"LV {level}"

    level_surface = font.render(f"{level_label}  (next: {next_level_in:.1f}s)", True, level_color)
    screen.blit(level_surface, (10, 70))

    # 속도 배율 / 생성 주기 표시
    speed_surface = font_level.render(
        f"Spawn: {spawn_interval}ms  Speed: x{speed_mult:.2f}", True, (80, 80, 80)
    )
    screen.blit(speed_surface, (10, 100))

    # 타이머 (중앙 상단)
    elapsed_total_s = int(elapsed_s)
    minutes = elapsed_total_s // 60
    seconds = elapsed_total_s % 60
    centiseconds = (elapsed_ms % 1000) // 10

    timer_str = f"{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
    timer_surface = font_timer.render(timer_str, True, (30, 30, 30))
    timer_rect = timer_surface.get_rect(center=(WIDTH // 2, 30))

    padding = 10
    bg_rect = timer_rect.inflate(padding * 2, padding)
    pygame.draw.rect(screen, (220, 230, 255), bg_rect, border_radius=8)
    pygame.draw.rect(screen, (0, 0, 200), bg_rect, 2, border_radius=8)
    screen.blit(timer_surface, timer_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
