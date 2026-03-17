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

# 원 데이터: [x, y, 현재 반지름, 최대 반지름, 성장 속도, 투명도]
circles = []

SPAWN_INTERVAL = 500  # 밀리초 단위로 새 원 생성 간격
last_spawn_time = 0

# 타이머
start_time = pygame.time.get_ticks()

def spawn_circle():
    x = random.randint(50, WIDTH - 50)
    y = random.randint(50, HEIGHT - 50)
    max_radius = random.randint(60, 150)
    growth_speed = random.uniform(0.5, 2.5)
    return {"x": x, "y": y, "radius": 0, "max_radius": max_radius, "speed": growth_speed, "alpha": 255}

running = True
while running:
    dt = clock.tick(60)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 일정 간격마다 새 원 생성
    if current_time - last_spawn_time > SPAWN_INTERVAL:
        circles.append(spawn_circle())
        last_spawn_time = current_time

    # 원 업데이트
    for circle in circles:
        if circle["radius"] < circle["max_radius"]:
            circle["radius"] += circle["speed"]
        else:
            # 최대 크기 도달 후 서서히 사라짐
            circle["alpha"] -= 3

    # 완전히 사라진 원 제거
    circles = [c for c in circles if c["alpha"] > 0]

    screen.fill(WHITE)

    # 원 그리기 (투명도 적용을 위해 Surface 사용)
    for circle in circles:
        r = int(circle["radius"])
        if r <= 0:
            continue
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        alpha = max(0, min(255, int(circle["alpha"])))
        pygame.draw.circle(surf, (0, 0, 255, alpha), (r, r), r)
        # 테두리도 그리기
        pygame.draw.circle(surf, (0, 0, 180, alpha), (r, r), r, 2)
        screen.blit(surf, (circle["x"] - r, circle["y"] - r))

    fps = str(int(clock.get_fps()))
    fps_surface = font.render("FPS: " + fps, True, BLACK)
    screen.blit(fps_surface, (10, 10))

    count_surface = font.render(f"Circles: {len(circles)}", True, BLACK)
    screen.blit(count_surface, (10, 40))

    # 타이머 계산 및 표시
    elapsed_ms = current_time - start_time
    elapsed_total_s = elapsed_ms // 1000
    minutes = elapsed_total_s // 60
    seconds = elapsed_total_s % 60
    milliseconds = (elapsed_ms % 1000) // 10  # 센티초 (0~99)

    timer_str = f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"
    timer_surface = font_timer.render(timer_str, True, (30, 30, 30))
    timer_rect = timer_surface.get_rect(center=(WIDTH // 2, 30))

    # 타이머 배경 박스
    padding = 10
    bg_rect = timer_rect.inflate(padding * 2, padding)
    pygame.draw.rect(screen, (220, 230, 255), bg_rect, border_radius=8)
    pygame.draw.rect(screen, (0, 0, 200), bg_rect, 2, border_radius=8)
    screen.blit(timer_surface, timer_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()