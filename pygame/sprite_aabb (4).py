import pygame
import sys
import base64
import io

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sprite AABB Demo")
clock = pygame.time.Clock()
SPEED = 5

# ──────────────────────────────────────────────────────────────────
# ★ 여기에 Base64 데이터를 붙여넣으세요 ★
#
# sprites.py 파일을 열고 아래 두 변수를 그대로 복사해 오면 됩니다.
#   - _ADVENTURER = ( "iVBOR..." ) 전체
#   - _STONE      = ( "iVBOR..." ) 전체
# ──────────────────────────────────────────────────────────────────

_ADVENTURER = (
    # 여기에 sprites.py의 _ADVENTURER 내용을 붙여넣으세요
)

_STONE = (
    # 여기에 sprites.py의 _STONE 내용을 붙여넣으세요
)

# ──────────────────────────────────────────────────────────────────

def load_surface(b64_data, size):
    raw = base64.b64decode("".join(b64_data))
    buf = io.BytesIO(raw)
    surf = pygame.image.load(buf).convert_alpha()
    return pygame.transform.scale(surf, size)

# 스프라이트 크기 (sprites.py 주석 기준)
adv_img   = load_surface(_ADVENTURER, (80, 110))   # adventurer: 80x110
stone_img = load_surface(_STONE,      (70, 70))    # stone:       70x70

# 오브젝트 위치 (Rect)
adv_rect   = adv_img.get_rect(topleft=(100, 240))           # 좌측 시작
stone_rect = stone_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # 화면 중앙 고정

# 색상
BG_NORMAL = (30,  30,  40)
BG_HIT    = (240, 220, 50)
AABB_COL  = (220, 60,  60)
GRID_COL  = (40,  40,  50)

font_sm = pygame.font.SysFont("Arial", 15)
font_lg = pygame.font.SysFont("Arial", 22, bold=True)

def draw_grid(col):
    for x in range(0, WIDTH, 40):
        pygame.draw.line(screen, col, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, 40):
        pygame.draw.line(screen, col, (0, y), (WIDTH, y))

def label(text, x, y, color):
    screen.blit(font_sm.render(text, True, color), (x, y))

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # 방향키 입력 (adventurer만 이동)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:  adv_rect.x -= SPEED
    if keys[pygame.K_RIGHT]: adv_rect.x += SPEED
    if keys[pygame.K_UP]:    adv_rect.y -= SPEED
    if keys[pygame.K_DOWN]:  adv_rect.y += SPEED
    adv_rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    # AABB = 스프라이트 Rect 그 자체
    aabb_adv   = adv_rect.copy()
    aabb_stone = stone_rect.copy()

    # 충돌 검사
    hit = aabb_adv.colliderect(aabb_stone)

    # ── 렌더링 ──────────────────────────────────
    bg       = BG_HIT   if hit else BG_NORMAL
    grid_col = (200, 180, 30) if hit else GRID_COL
    screen.fill(bg)
    draw_grid(grid_col)

    # 스프라이트 그리기
    screen.blit(adv_img,   adv_rect)
    screen.blit(stone_img, stone_rect)

    # AABB 테두리
    aabb_color = (255, 60, 60) if hit else AABB_COL
    pygame.draw.rect(screen, aabb_color, aabb_adv,   2)
    pygame.draw.rect(screen, aabb_color, aabb_stone, 2)

    # 레이블
    lc = (30, 30, 30) if hit else (240, 240, 240)
    label("Adventurer  (← → ↑ ↓)", adv_rect.x, adv_rect.y - 22, lc)
    label("Stone  (fixed)",          stone_rect.x, stone_rect.y - 22, lc)

    # 상태 표시
    c = (180, 40, 40) if hit else (140, 200, 140)
    s = font_lg.render("AABB : " + ("HIT" if hit else "--"), True, c)
    screen.blit(s, (16, 14))

    label("Arrow keys: move Adventurer  |  ESC: quit", 12, HEIGHT - 22,
          (80, 80, 60) if hit else (80, 80, 100))

    pygame.display.flip()

pygame.quit()
sys.exit()
