import pygame
import sys
import random
import math
from collections import deque

pygame.init()

WIDTH, HEIGHT = 1500, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Expanding Circles")

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0  )
RED    = (220, 50,  50 )

clock      = pygame.time.Clock()
font       = pygame.font.Font(None, 36)
font_timer = pygame.font.Font(None, 52)
font_level = pygame.font.Font(None, 30)
font_go    = pygame.font.Font(None, 100)
font_sub   = pygame.font.Font(None, 42)

circles        = []
last_spawn_time = 0

# 타이머
start_time = pygame.time.get_ticks()

# 삼각형
TRIANGLE_SPEED = 5
TRIANGLE_SIZE  = 5
TRIANGLE_HIT_R = 14   # 충돌 판정용 원 반지름 (삼각형 내접원)
triangle_x     = float(WIDTH  // 2)
triangle_y     = float(HEIGHT // 2)
triangle_dir   = 0    # 0=위 1=오른쪽 2=아래 3=왼쪽

# 삼각형 위치 히스토리 (최근 1초 = 60프레임 분량)
pos_history = deque(maxlen=60)

game_over = False
final_time_str = ""


def get_triangle_points(x, y, direction, size):
    if direction == 0:
        return [(x, y - size), (x - size, y + size), (x + size, y + size)]
    elif direction == 1:
        return [(x + size, y), (x - size, y - size), (x - size, y + size)]
    elif direction == 2:
        return [(x, y + size), (x - size, y - size), (x + size, y - size)]
    else:
        return [(x - size, y), (x + size, y - size), (x + size, y + size)]


def get_level_params(elapsed_s):
    if elapsed_s < 10:
        return 1500, 0.4, 1
    level  = min(2 + int((elapsed_s - 10) // 10), 11)
    extra  = level - 1
    return max(200, 1500 - extra * 130), 0.4 + extra * 0.25, int(level)


def spawn_circle(speed_mult, safe_pos):
    """safe_pos: 현재 삼각형 위치 — 너무 가까우면 재시도"""
    SAFE_DIST = TRIANGLE_SIZE + 30   # 이 거리 이내엔 생성 안 함
    for _ in range(50):              # 최대 50번 시도
        x = random.randint(50, WIDTH  - 50)
        y = random.randint(50, HEIGHT - 50)
        dx, dy = x - safe_pos[0], y - safe_pos[1]
        if math.hypot(dx, dy) >= SAFE_DIST:
            break
    max_radius   = random.randint(60, 150)
    growth_speed = random.uniform(0.5, 2.5) * speed_mult
    return {"x": x, "y": y, "radius": 0,
            "max_radius": max_radius, "speed": growth_speed, "alpha": 255}


def check_collision(tx, ty, circle):
    """삼각형 중심점과 원의 거리 비교로 충돌 판정"""
    dist = math.hypot(tx - circle["x"], ty - circle["y"])
    return dist < circle["radius"] + TRIANGLE_HIT_R


def draw_game_over(screen, time_str):
    # 반투명 검정 오버레이
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    # GAME OVER 텍스트
    go_surf = font_go.render("GAME OVER", True, (255, 60, 60))
    go_rect = go_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
    screen.blit(go_surf, go_rect)

    # 생존 시간
    time_surf = font_sub.render(f"생존 시간: {time_str}", True, WHITE)
    time_rect = time_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    screen.blit(time_surf, time_rect)

    # 종료 안내
    quit_surf = font_level.render("ESC 키를 눌러 종료", True, (200, 200, 200))
    quit_rect = quit_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70))
    screen.blit(quit_surf, quit_rect)


running = True
while running:
    dt           = clock.tick(60)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and game_over:
                running = False

    # ── 게임 오버 상태면 오버레이만 그리고 대기 ──────────────────────
    if game_over:
        draw_game_over(screen, final_time_str)
        pygame.display.flip()
        continue

    # ── 삼각형 이동 ───────────────────────────────────────────────────
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

    triangle_x = max(TRIANGLE_SIZE, min(WIDTH  - TRIANGLE_SIZE, triangle_x))
    triangle_y = max(TRIANGLE_SIZE, min(HEIGHT - TRIANGLE_SIZE, triangle_y))

    # 현재 위치를 히스토리에 저장
    pos_history.append((triangle_x, triangle_y))

    # ── 시간 / 레벨 ───────────────────────────────────────────────────
    elapsed_ms = current_time - start_time
    elapsed_s  = elapsed_ms / 1000.0
    spawn_interval, speed_mult, level = get_level_params(elapsed_s)

    # ── 원 생성 (현재 삼각형 위치 회피) ─────────────────────────────
    if current_time - last_spawn_time > spawn_interval:
        circles.append(spawn_circle(speed_mult, (triangle_x, triangle_y)))
        last_spawn_time = current_time

    # ── 원 업데이트 ───────────────────────────────────────────────────
    for circle in circles:
        if circle["radius"] < circle["max_radius"]:
            circle["radius"] += circle["speed"]
        else:
            circle["alpha"] -= 3
    circles = [c for c in circles if c["alpha"] > 0]

    # ── 충돌 판정 ─────────────────────────────────────────────────────
    for circle in circles:
        if circle["radius"] > 0 and check_collision(triangle_x, triangle_y, circle):
            game_over = True
            # 최종 시간 문자열 저장
            total_s   = int(elapsed_s)
            final_time_str = (
                f"{total_s // 60:02d}:{total_s % 60:02d}"
                f".{(elapsed_ms % 1000) // 10:02d}"
            )
            break

    # ── 그리기 ────────────────────────────────────────────────────────
    screen.fill(WHITE)

    for circle in circles:
        r = int(circle["radius"])
        if r <= 0:
            continue
        surf  = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        alpha = max(0, min(255, int(circle["alpha"])))
        pygame.draw.circle(surf, (0, 0, 255, alpha), (r, r), r)
        pygame.draw.circle(surf, (0, 0, 180, alpha), (r, r), r, 2)
        screen.blit(surf, (circle["x"] - r, circle["y"] - r))

    pts = get_triangle_points(triangle_x, triangle_y, triangle_dir, TRIANGLE_SIZE)
    pygame.draw.polygon(screen, RED,      pts)
    pygame.draw.polygon(screen, (140, 0, 0), pts, 2)

    # UI
    screen.blit(font.render("FPS: " + str(int(clock.get_fps())), True, BLACK), (10, 10))
    screen.blit(font.render(f"Circles: {len(circles)}", True, BLACK), (10, 40))

    if elapsed_s < 10:
        next_level_in = 10 - elapsed_s
        level_color, level_label = (0, 150, 0), "SLOW"
    else:
        next_level_in = 10 - ((elapsed_s - 10) % 10)
        level_color   = (180, 60, 0) if level < 6 else (200, 0, 0)
        level_label   = f"LV {level}"

    screen.blit(font.render(f"{level_label}  (next: {next_level_in:.1f}s)", True, level_color), (10, 70))
    screen.blit(font_level.render(f"Spawn: {spawn_interval}ms  Speed: x{speed_mult:.2f}", True, (80, 80, 80)), (10, 100))

    # 타이머
    elapsed_total_s  = int(elapsed_s)
    timer_str        = f"{elapsed_total_s // 60:02d}:{elapsed_total_s % 60:02d}.{(elapsed_ms % 1000) // 10:02d}"
    timer_surface    = font_timer.render(timer_str, True, (30, 30, 30))
    timer_rect       = timer_surface.get_rect(center=(WIDTH // 2, 30))
    padding          = 10
    bg_rect          = timer_rect.inflate(padding * 2, padding)
    pygame.draw.rect(screen, (220, 230, 255), bg_rect, border_radius=8)
    pygame.draw.rect(screen, (0, 0, 200),     bg_rect, 2, border_radius=8)
    screen.blit(timer_surface, timer_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
