import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
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

# 삼각형 플레이어
TRIANGLE_SPEED = 5
TRIANGLE_SIZE = 5  # 중심에서 꼭짓점까지 거리
triangle_x = float(WIDTH // 2)
triangle_y = float(HEIGHT // 2)
triangle_dir = 0  # 0=위, 1=오른쪽, 2=아래, 3=왼쪽


def get_triangle_points(x, y, direction, size):
    """방향에 따라 삼각형 꼭짓점 3개 반환 (진행 방향이 앞쪽 꼭짓점)"""
    if direction == 0:   # 위
        return [(x, y - size), (x - size, y + size), (x + size, y + size)]
    elif direction == 1: # 오른쪽
        return [(x + size, y), (x - size, y - size), (x - size, y + size)]
    elif direction == 2: # 아래
        return [(x, y + size), (x - size, y - size), (x + size, y - size)]
    else:                # 왼쪽
        return [(x - size, y), (x + size, y - size), (x + size, y + size)]


def get_level_params(elapsed_s):
    if elapsed_s < 10:
        spawn_interval = 1500
        speed_mult = 0.4
        level = 1
    else:
        level = min(2 + int((elapsed_s - 10) // 10), 11)
        extra = level - 1
        spawn_interval = max(200, 1500 - extra * 130)
        speed_mult = 0.4 + extra * 0.25
    return int(spawn_interval), speed_mult, int(level)


def spawn_circle(speed_mult):
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    max_radius = random.randint(60, 150)
    growth_speed = random.uniform(0.5, 2.5) * speed_mult
    return {"x": x, "y": y, "radius": 0, "max_radius": max_radius, "speed": growth_speed, "alpha": 255}


running = True
while running:
    dt = clock.tick(60)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 방향키 입력 처리 (누르고 있는 동안 연속 이동)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
        triangle_y -= TRIANGLE_SPEED
        triangle_dir = 0
    if keys[pygame.K_RIGHT]:
        triangle_x += TRIANGLE_SPEED
        triangle_dir = 1
    if keys[pygame.K_DOWN]:
        triangle_y += TRIANGLE_SPEED
        triangle_dir = 2
    if keys[pygame.K_LEFT]:
        triangle_x -= TRIANGLE_SPEED
        triangle_dir = 3

    # 화면 경계 처리
    triangle_x = max(TRIANGLE_SIZE, min(WIDTH - TRIANGLE_SIZE, triangle_x))
    triangle_y = max(TRIANGLE_SIZE, min(HEIGHT - TRIANGLE_SIZE, triangle_y))

    # 경과 시간
    elapsed_ms = current_time - start_time
    elapsed_s = elapsed_ms / 1000.0

    spawn_interval, speed_mult, level = get_level_params(elapsed_s)

    # 원 생성
    if current_time - last_spawn_time > spawn_interval:
        circles.append(spawn_circle(speed_mult))
        last_spawn_time = current_time

    # 원 업데이트
    for circle in circles:
        if circle["radius"] < circle["max_radius"]:
            circle["radius"] += circle["speed"]
        else:
            circle["alpha"] -= 3
    circles = [c for c in circles if c["alpha"] > 0]

    # --- 그리기 ---
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

    # 삼각형 그리기
    pts = get_triangle_points(triangle_x, triangle_y, triangle_dir, TRIANGLE_SIZE)
    pygame.draw.polygon(screen, (220, 50, 50), pts)
    pygame.draw.polygon(screen, (140, 0, 0), pts, 2)

    # FPS / 원 개수
    fps_surface = font.render("FPS: " + str(int(clock.get_fps())), True, BLACK)
    screen.blit(fps_surface, (10, 10))
    count_surface = font.render(f"Circles: {len(circles)}", True, BLACK)
    screen.blit(count_surface, (10, 40))

    # 레벨 표시
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
