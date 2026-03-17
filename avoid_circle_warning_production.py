import pygame
import sys
import random
import math
from collections import deque

pygame.init()

WIDTH, HEIGHT = 1500, 1000
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

circles         = []
pending_circles = []   # {"x", "y", "spawn_at", "speed_mult"} — 예고 대기 목록
last_spawn_time = 0
WARN_DELAY      = 1000  # 예고점 → 원 생성까지 대기 시간 (ms)

# 타이머
start_time = pygame.time.get_ticks()

# 삼각형
TRIANGLE_SPEED = 5
TRIANGLE_SIZE  = 5
TRIANGLE_HIT_R = 5
triangle_x     = float(WIDTH  // 2)
triangle_y     = float(HEIGHT // 2)
triangle_dir   = 0

pos_history    = deque(maxlen=60)
game_over      = False
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
    level = min(2 + int((elapsed_s - 10) // 10), 11)
    extra = level - 1
    return max(200, 1500 - extra * 130), 0.4 + extra * 0.25, int(level)


def pick_position(safe_pos):
    """삼각형 현재 위치와 최소 거리를 유지하는 랜덤 위치 반환"""
    SAFE_DIST = TRIANGLE_SIZE + 30
    for _ in range(50):
        x = random.randint(50, WIDTH  - 50)
        y = random.randint(50, HEIGHT - 50)
        if math.hypot(x - safe_pos[0], y - safe_pos[1]) >= SAFE_DIST:
            return x, y
    return x, y


def make_circle_from_pending(p, speed_mult):
    max_radius   = random.randint(60, 150)
    growth_speed = random.uniform(0.5, 2.5) * speed_mult
    return {"x": p["x"], "y": p["y"], "radius": 0,
            "max_radius": max_radius, "speed": growth_speed, "alpha": 255}


def check_collision(tx, ty, circle):
    return math.hypot(tx - circle["x"], ty - circle["y"]) < circle["radius"] + TRIANGLE_HIT_R


def draw_game_over(surface, time_str):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    go_surf = font_go.render("GAME OVER", True, (255, 60, 60))
    surface.blit(go_surf, go_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))

    time_surf = font_sub.render(f"생존 시간: {time_str}", True, WHITE)
    surface.blit(time_surf, time_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))

    quit_surf = font_level.render("ESC 키를 눌러 종료", True, (200, 200, 200))
    surface.blit(quit_surf, quit_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70)))


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

    if game_over:
        draw_game_over(screen, final_time_str)
        pygame.display.flip()
        continue

    # ── 삼각형 이동 ───────────────────────────────────────────────────
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:    triangle_y -= TRIANGLE_SPEED; triangle_dir = 0
    if keys[pygame.K_RIGHT]: triangle_x += TRIANGLE_SPEED; triangle_dir = 1
    if keys[pygame.K_DOWN]:  triangle_y += TRIANGLE_SPEED; triangle_dir = 2
    if keys[pygame.K_LEFT]:  triangle_x -= TRIANGLE_SPEED; triangle_dir = 3

    triangle_x = max(TRIANGLE_SIZE, min(WIDTH  - TRIANGLE_SIZE, triangle_x))
    triangle_y = max(TRIANGLE_SIZE, min(HEIGHT - TRIANGLE_SIZE, triangle_y))
    pos_history.append((triangle_x, triangle_y))

    # ── 시간 / 레벨 ───────────────────────────────────────────────────
    elapsed_ms = current_time - start_time
    elapsed_s  = elapsed_ms / 1000.0
    spawn_interval, speed_mult, level = get_level_params(elapsed_s)

    # ── 예고점 예약 (1초 후 원이 생성될 위치 미리 등록) ──────────────
    if current_time - last_spawn_time > spawn_interval:
        px, py = pick_position((triangle_x, triangle_y))
        pending_circles.append({
            "x": px, "y": py,
            "spawn_at": current_time + WARN_DELAY,
            "speed_mult": speed_mult
        })
        last_spawn_time = current_time

    # ── 대기 중인 예고점 → 실제 원으로 변환 ──────────────────────────
    still_pending = []
    for p in pending_circles:
        if current_time >= p["spawn_at"]:
            circles.append(make_circle_from_pending(p, p["speed_mult"]))
        else:
            still_pending.append(p)
    pending_circles = still_pending

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
            total_s = int(elapsed_s)
            final_time_str = (
                f"{total_s // 60:02d}:{total_s % 60:02d}"
                f".{(elapsed_ms % 1000) // 10:02d}"
            )
            break

    # ── 그리기 ────────────────────────────────────────────────────────
    screen.fill(WHITE)

    # 원
    for circle in circles:
        r = int(circle["radius"])
        if r <= 0:
            continue
        surf  = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        alpha = max(0, min(255, int(circle["alpha"])))
        pygame.draw.circle(surf, (0, 0, 255, alpha), (r, r), r)
        pygame.draw.circle(surf, (0, 0, 180, alpha), (r, r), r, 2)
        screen.blit(surf, (circle["x"] - r, circle["y"] - r))

    # 예고 점 — 남은 시간 비율로 크기/투명도 펄스
    for p in pending_circles:
        time_left  = p["spawn_at"] - current_time          # ms, 0~1000
        progress   = 1.0 - time_left / WARN_DELAY          # 0→1 (예고 시작→원 생성)
        dot_radius = max(2, int(4 + progress * 4))         # 2→8px 로 점점 커짐
        dot_alpha  = int(80 + progress * 175)              # 80→255 로 점점 진해짐
        dot_surf   = pygame.Surface((dot_radius * 2, dot_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(dot_surf, (0, 0, 0, dot_alpha),
                           (dot_radius, dot_radius), dot_radius)
        screen.blit(dot_surf, (int(p["x"]) - dot_radius, int(p["y"]) - dot_radius))

    # 삼각형
    pts = get_triangle_points(triangle_x, triangle_y, triangle_dir, TRIANGLE_SIZE)
    pygame.draw.polygon(screen, RED,         pts)
    pygame.draw.polygon(screen, (140, 0, 0), pts, 2)

    # UI
    screen.blit(font.render("FPS: " + str(int(clock.get_fps())), True, BLACK), (10, 10))
    screen.blit(font.render(f"Circles: {len(circles)}", True, BLACK), (10, 40))

    if elapsed_s < 10:
        next_level_in, level_color, level_label = 10 - elapsed_s, (0, 150, 0), "SLOW"
    else:
        next_level_in = 10 - ((elapsed_s - 10) % 10)
        level_color   = (180, 60, 0) if level < 6 else (200, 0, 0)
        level_label   = f"LV {level}"

    screen.blit(font.render(f"{level_label}  (next: {next_level_in:.1f}s)", True, level_color), (10, 70))
    screen.blit(font_level.render(f"Spawn: {spawn_interval}ms  Speed: x{speed_mult:.2f}", True, (80, 80, 80)), (10, 100))

    elapsed_total_s = int(elapsed_s)
    timer_str       = f"{elapsed_total_s // 60:02d}:{elapsed_total_s % 60:02d}.{(elapsed_ms % 1000) // 10:02d}"
    timer_surface   = font_timer.render(timer_str, True, (30, 30, 30))
    timer_rect      = timer_surface.get_rect(center=(WIDTH // 2, 30))
    bg_rect         = timer_rect.inflate(20, 10)
    pygame.draw.rect(screen, (220, 230, 255), bg_rect, border_radius=8)
    pygame.draw.rect(screen, (0, 0, 200),     bg_rect, 2, border_radius=8)
    screen.blit(timer_surface, timer_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
