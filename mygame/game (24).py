import pygame
import sys
import math
import random

# ──────────────────────────────────────────
#  기본 설정
# ──────────────────────────────────────────
pygame.init()

WIDTH, HEIGHT = 1000, 600
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Project: Unnamed")
clock = pygame.time.Clock()

# ──────────────────────────────────────────
#  한글 폰트
# ──────────────────────────────────────────
def get_font(size):
    for name in ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]:
        f = pygame.font.SysFont(name, size)
        if f.get_ascent() > 0:
            return f
    return pygame.font.SysFont(None, size)

# 색상
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (220, 50,  50)
GREEN  = (50,  200, 80)
BLUE   = (50,  120, 220)
YELLOW = (255, 220, 50)
GRAY   = (100, 100, 100)
DARK   = (20,  20,  30)
CYAN   = (0,   220, 255)
ORANGE = (255, 140, 0)
PURPLE = (160, 80,  220)

# ──────────────────────────────────────────
#  물리 상수
# ──────────────────────────────────────────
GRAVITY        = 0.55   # 올려서 더 빨리 떨어지게
MAX_FALL_SPEED = 15

# ──────────────────────────────────────────
#  플레이어 상수
# ──────────────────────────────────────────
PLAYER_W           = 36
PLAYER_H           = 48
MOVE_ACCEL         = 1.2
MOVE_FRICTION      = 0.75
MAX_MOVE_SPEED     = 7
JUMP_POWER         = -15
BASE_BULLET_SPEED  = 27
BASE_BULLET_DAMAGE = 50
BULLET_GRAVITY     = 0.35
MAX_BULLET_FALL    = 16
SHOOT_COOLDOWN     = 150
BASE_MAX_AMMO      = 3
BASE_RELOAD_TIME   = 2000

# ──────────────────────────────────────────
#  맵 상수
# ──────────────────────────────────────────
ZONE_WIDTH    = 2100
TOTAL_WAVES   = 7
TOTAL_MAP_W   = ZONE_WIDTH * (TOTAL_WAVES + 1)
GROUND_Y      = 560
FALL_DEATH_Y  = 750    # 이 아래로 떨어지면 낙사 처리

# ──────────────────────────────────────────
#  게임 상태
# ──────────────────────────────────────────
STATE_PLAY        = "play"
STATE_BUFF_SELECT = "buff_select"
STATE_WAVE_BANNER = "wave_banner"
STATE_GAME_OVER   = "game_over"

# ──────────────────────────────────────────
#  버프 정의
# ──────────────────────────────────────────
PURPLE2 = (160, 80, 220)
PINK    = (220, 80, 160)

ALL_BUFFS = [
    # ── 흔함 ──
    {"id": "burst",        "name": "점사",       "desc": "탄약 +3 / 동시 발사 +2\n데미지 -60% / 재장전 +0.25초",    "color": ORANGE,   "rarity": "common"},
    {"id": "quick_shot",   "name": "고속 사격",  "desc": "탄환속도 +150%\n재장전 +0.25초",                          "color": CYAN,     "rarity": "common"},
    {"id": "fastball",     "name": "강속구",     "desc": "탄환속도 +250%\n공격속도 -50% / 재장전 +0.25초",          "color": CYAN,     "rarity": "common"},
    {"id": "steady_shot",  "name": "고정 사격",  "desc": "HP +40% / 탄환속도 +100%\n재장전 +0.25초",               "color": GREEN,    "rarity": "common"},
    {"id": "wind_up",      "name": "와인드 업",  "desc": "데미지 +60% / 탄환속도 +100%\n공격속도 -100% / 재장전 +0.5초", "color": RED, "rarity": "common"},
    {"id": "fast_forward", "name": "빨리 감기",  "desc": "탄환속도 +100%\n재장전 -30%",                             "color": CYAN,     "rarity": "common"},
    {"id": "dazzle",       "name": "눈부심",     "desc": "피격 시 적 잠깐 스턴\n재장전 +0.25초",                    "color": YELLOW,   "rarity": "common"},
    {"id": "cold_bullets", "name": "빙결 탄환",  "desc": "피격 적 이동속도 -70%\n(2초) / 재장전 +0.25초",           "color": (100, 200, 255), "rarity": "common"},
    {"id": "poison",       "name": "독",         "desc": "데미지 +70% / 재장전 -30%\n탄약 -1 / 피격 시 지속 데미지", "color": GREEN,   "rarity": "common"},
    {"id": "timed_det",    "name": "시한폭탄",   "desc": "피격 위치에 0.5초 후 폭발\n데미지 -15% / 재장전 +0.25초", "color": ORANGE,   "rarity": "common"},
    {"id": "big_bullet",   "name": "큰 탄환",    "desc": "총알 크기 증가\n재장전 +0.25초",                          "color": ORANGE,   "rarity": "common"},
    {"id": "combine",      "name": "결합",       "desc": "데미지 +100% / 탄약 -2\n재장전 +0.5초",                   "color": RED,      "rarity": "common"},
    {"id": "huge",         "name": "거대화",     "desc": "HP +80%",                                                  "color": GREEN,    "rarity": "common"},
    {"id": "tank",         "name": "전차",       "desc": "HP +100%\n공격속도 -25% / 재장전 +0.5초",                 "color": GRAY,     "rarity": "common"},
    {"id": "leech",        "name": "거머리",     "desc": "적 처치 시 HP 흡수\nHP +30%",                             "color": (200, 0, 80), "rarity": "common"},
    {"id": "healing_field","name": "치유장",     "desc": "처치 시 주변에 회복 효과\nHP +30%",                       "color": (80, 220, 120), "rarity": "common"},
    # ── 드묾 ──
    {"id": "barrage",      "name": "포화",       "desc": "발사 탄환 +4 / 탄약 +5\n데미지 -70% / 재장전 +0.25초",   "color": RED,      "rarity": "uncommon"},
    {"id": "bombs_away",   "name": "폭탄 나가신다","desc": "처치 시 주변 폭발\nHP +30%",                            "color": ORANGE,   "rarity": "uncommon"},
    {"id": "bouncy",       "name": "탄력",       "desc": "총알 튕김 +2 / 데미지 +25%\n재장전 +0.25초",             "color": PURPLE2,  "rarity": "uncommon"},
    {"id": "brawler",      "name": "싸움꾼",     "desc": "피해 입히면 3초간 HP +200%",                             "color": RED,      "rarity": "uncommon"},
    {"id": "buckshot",     "name": "산탄",       "desc": "탄환 방사형으로 +4발\n데미지 -60% / 재장전 +0.25초",     "color": ORANGE,   "rarity": "uncommon"},
    {"id": "careful",      "name": "신중한 계획","desc": "데미지 +100%\n공격속도 -150% / 재장전 +0.5초",            "color": PURPLE2,  "rarity": "uncommon"},
    {"id": "chase",        "name": "추격",       "desc": "적 방향 이동 시\n이동속도 +60% / HP +30%",               "color": (220, 60, 60), "rarity": "uncommon"},
]

# ──────────────────────────────────────────
#  맵 생성 (세계 좌표 기준)
# ──────────────────────────────────────────
def build_map():
    plats = []
    zones = []

    # ── 시작 구역 바닥 — 넉넉하게 확보 ──
    plats.append(pygame.Rect(0, GROUND_Y, 900, 20))   # 시작 안전 구간 900px

    for w in range(1, TOTAL_WAVES + 1):
        base_x = w * ZONE_WIDTH
        zones.append(base_x)

        # 이동 구간 시작점 — 첫 웨이브는 시작 바닥 끝 이후부터
        seg_start = (w - 1) * ZONE_WIDTH + 900 if w == 1 else (w - 1) * ZONE_WIDTH + 600
        seg_end   = base_x

        x = seg_start
        while x < seg_end - 200:
            w_seg = random.randint(200, 500)
            w_seg = min(w_seg, seg_end - x - 150)
            if w_seg < 80:
                break

            bump    = random.choice([0, 0, 0, 30, 50])
            floor_y = GROUND_Y - bump
            plats.append(pygame.Rect(x, floor_y, w_seg, 20))

            if bump > 0:
                plats.append(pygame.Rect(x - 30, GROUND_Y, 30, 20))

            # 낭떠러지 간격
            gap = random.randint(100, 250)
            x  += w_seg + gap

        # 웨이브 구역 바닥 (넓고 안정적인 전투 구역)
        plats.append(pygame.Rect(base_x - 400, GROUND_Y, 900, 20))

        # 웨이브 구역 내 공중 발판
        plats.append(pygame.Rect(base_x - 280, 420, 160, 20))
        plats.append(pygame.Rect(base_x - 80,  340, 200, 20))
        plats.append(pygame.Rect(base_x + 160, 420, 160, 20))
        plats.append(pygame.Rect(base_x + 20,  260, 140, 20))
        plats.append(pygame.Rect(base_x - 180, 260, 140, 20))

    return plats, zones

random.seed(42)   # 맵 고정 (매번 같은 지형)
platforms, WAVE_ZONES = build_map()
random.seed()     # 이후 랜덤은 다시 시드 해제

# ──────────────────────────────────────────
#  카메라
# ──────────────────────────────────────────
class Camera:
    def __init__(self):
        self.x       = 0.0   # 카메라 왼쪽 x (세계 좌표)
        self.locked  = False  # True면 고정

    def update(self, player_x):
        if not self.locked:
            # 플레이어가 화면 중앙 우측에 오도록 부드럽게 따라감
            target = player_x - WIDTH * 0.4
            self.x += (target - self.x) * 0.08
            self.x  = max(0, self.x)

    def to_screen(self, world_x, world_y=None):
        """세계 좌표 → 화면 좌표"""
        if world_y is None:
            return world_x - int(self.x)
        return world_x - int(self.x), world_y

    def to_screen_rect(self, rect):
        return pygame.Rect(rect.x - int(self.x), rect.y, rect.w, rect.h)

# ──────────────────────────────────────────
#  총알
# ──────────────────────────────────────────
class Bullet:
    def __init__(self, x, y, dx, dy, damage, radius=5,
                 bouncy=False, homing=False, poison=False,
                 cold=False, dazzle=False):
        self.x        = float(x)
        self.y        = float(y)
        self.dx       = dx
        self.dy       = dy
        self.radius   = radius
        self.alive    = True
        self.damage   = damage
        self.bouncy   = bouncy
        self.bounces  = 0
        self.homing   = homing
        self.poison   = poison
        self.cold     = cold
        self.dazzle   = dazzle

    def update(self, enemies=None):
        # 유도탄 — 가장 가까운 적 방향으로 살짝 휘어짐
        if self.homing and enemies:
            closest = None
            min_d   = 400
            for e in enemies:
                if not e.alive:
                    continue
                d = math.hypot(e.rect.centerx - self.x, e.rect.centery - self.y)
                if d < min_d:
                    min_d   = d
                    closest = e
            if closest:
                tx  = closest.rect.centerx - self.x
                ty  = closest.rect.centery - self.y
                mag = math.hypot(tx, ty)
                if mag > 0:
                    self.dx += (tx / mag) * 0.6
                    self.dy += (ty / mag) * 0.6
                    # 속도 정규화
                    speed = math.hypot(self.dx, self.dy)
                    cap   = BASE_BULLET_SPEED * 1.5
                    if speed > cap:
                        self.dx = self.dx / speed * cap
                        self.dy = self.dy / speed * cap

        self.dy += BULLET_GRAVITY
        if self.dy > MAX_BULLET_FALL:
            self.dy = MAX_BULLET_FALL
        self.x += self.dx
        self.y += self.dy

        br = self.get_world_rect()
        for plat in platforms:
            if br.colliderect(plat):
                if self.bouncy and self.bounces < 1:
                    self.dy      = -abs(self.dy) * 0.8
                    self.bounces += 1
                    return
                self.alive = False
                return

        if self.y > HEIGHT + 50 or self.y < -50:
            self.alive = False

    def draw(self, surface, cam):
        sx = cam.to_screen(int(self.x))
        if -10 < sx < WIDTH + 10:
            if self.poison:
                col = (80, 220, 80)
            elif self.homing:
                col = CYAN
            elif self.bouncy:
                col = (180, 100, 255)
            else:
                col = YELLOW
            pygame.draw.circle(surface, col,   (sx, int(self.y)), self.radius)
            pygame.draw.circle(surface, WHITE, (sx, int(self.y)), max(1, self.radius - 2))

    def get_world_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

# ──────────────────────────────────────────
#  적
# ──────────────────────────────────────────
ENEMY_CHASER  = "chaser"
ENEMY_WALKER  = "walker"
ENEMY_SHOOTER = "shooter"  # 가만히 있으면서 총알 발사

# ──────────────────────────────────────────
#  적 총알 클래스
# ──────────────────────────────────────────
class EnemyBullet:
    def __init__(self, x, y, dx, dy, reflected=False):
        self.x          = float(x)
        self.y          = float(y)
        self.dx         = dx
        self.dy         = dy
        self.radius     = 6
        self.alive      = True
        self.reflected  = reflected   # 반사된 총알 — 적을 맞출 수 있음
        self.damage     = 10

    def update(self):
        self.dy += BULLET_GRAVITY * 0.3   # 중력 약하게
        self.x  += self.dx
        self.y  += self.dy

        br = pygame.Rect(self.x - self.radius, self.y - self.radius,
                         self.radius * 2, self.radius * 2)
        for plat in platforms:
            if br.colliderect(plat):
                self.alive = False
                return

        if self.x < -100 or self.x > TOTAL_MAP_W + 100:
            self.alive = False
        if self.y > HEIGHT + 50 or self.y < -100:
            self.alive = False

    def draw(self, surface, cam):
        sx = cam.to_screen(int(self.x))
        if -10 < sx < WIDTH + 10:
            col = (255, 100, 100) if not self.reflected else (100, 255, 100)
            pygame.draw.circle(surface, col,   (sx, int(self.y)), self.radius)
            pygame.draw.circle(surface, WHITE, (sx, int(self.y)), self.radius - 3)

    def get_world_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)

class Enemy:
    def __init__(self, x, y, is_patrol=False, enemy_type=None):
        self.rect       = pygame.Rect(x, y, 36, 36)
        self.hp         = 100
        self.max_hp     = 100
        self.speed      = 1.8
        self.alive      = True
        self.vy         = 0.0
        self.is_patrol  = is_patrol

        # 타입 미지정이면 랜덤 (추적 50%, 왕복 50%)
        if enemy_type is None:
            self.type = random.choice([ENEMY_CHASER, ENEMY_WALKER])
        else:
            self.type = enemy_type

        self.direction     = random.choice([-1, 1])
        self.on_ground     = False
        self.jump_cooldown = 0
        self.poison_timer  = 0
        self.slow_timer    = 0
        self.stun_timer    = 0
        self.shoot_timer   = random.randint(60, 180)  # 슈터 발사 쿨타임
        self.enemy_bullets = []   # 슈터 전용 총알

    def _check_gap_ahead(self):
        """진행 방향 앞 바닥이 낭떠러지인지 확인"""
        direction = 1 if self._target_x > self.rect.centerx else -1
        # 발 앞쪽 40px 지점에 바닥이 있는지 탐색
        probe_x = self.rect.right + 40 if direction > 0 else self.rect.left - 40
        probe   = pygame.Rect(probe_x, self.rect.bottom + 2, 10, 20)
        for plat in platforms:
            if probe.colliderect(plat):
                return False   # 바닥 있음 — 낭떠러지 아님
        return True   # 바닥 없음 — 낭떠러지

    def _check_obstacle_ahead(self):
        """진행 방향 바로 앞에 벽/발판이 있는지 확인"""
        direction = 1 if self._target_x > self.rect.centerx else -1
        probe_x   = self.rect.right + 2 if direction > 0 else self.rect.left - 10
        probe     = pygame.Rect(probe_x, self.rect.top, 8, self.rect.height - 4)
        for plat in platforms:
            if probe.colliderect(plat):
                if plat.top < self.rect.bottom - 8:
                    return True
        return False

    def update(self, player_x, player_y, all_enemies):
        self._target_x = player_x

        # 스턴/슬로우 타이머 감소
        if self.stun_timer > 0:
            self.stun_timer -= 1
        if self.slow_timer > 0:
            self.slow_timer -= 1

        # 스턴 중이면 이동 스킵
        if self.stun_timer > 0:
            pass
        else:
            cur_speed = self.speed * (0.3 if self.slow_timer > 0 else 1.0)

            # ── 이동 ──
            if self.type == ENEMY_CHASER:
                move_dir     = -1 if player_x < self.rect.centerx else 1
                self.rect.x += int(cur_speed * move_dir)

                for plat in platforms:
                    if self.rect.colliderect(plat):
                        if move_dir > 0:
                            self.rect.right = plat.left
                        else:
                            self.rect.left  = plat.right

                if self.on_ground and self.jump_cooldown <= 0:
                    if self._check_obstacle_ahead() or self._check_gap_ahead():
                        self.vy            = JUMP_POWER * 0.6
                        self.on_ground     = False
                        self.jump_cooldown = 30

            elif self.type == ENEMY_WALKER:
                self.rect.x += int(cur_speed * self.direction)

                if self.rect.left <= 0 or self.rect.right >= TOTAL_MAP_W:
                    self.direction *= -1

                for plat in platforms:
                    if self.rect.colliderect(plat):
                        if self.direction > 0:
                            self.rect.right = plat.left
                        else:
                            self.rect.left  = plat.right
                        self.direction *= -1
                        break

            elif self.type == ENEMY_SHOOTER:
                # 슈터 — 이동 안 함, 플레이어 방향으로 총알 발사
                self.shoot_timer -= 1
                if self.shoot_timer <= 0:
                    self.shoot_timer = random.randint(90, 150)
                    dx = player_x - self.rect.centerx
                    dy = player_y - self.rect.centery
                    dist = math.hypot(dx, dy)
                    if dist > 0:
                        spd = 1.8   # 적 이동속도와 동일
                        self.enemy_bullets.append(EnemyBullet(
                            self.rect.centerx, self.rect.centery,
                            dx / dist * spd, dy / dist * spd
                        ))

        # 적 총알 업데이트
        for eb in self.enemy_bullets:
            eb.update()
        self.enemy_bullets = [eb for eb in self.enemy_bullets if eb.alive]

        # ── 중력 / 수직 이동 ──
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1

        self.vy += GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED

        # 수직 이동 + 수직 충돌
        self.rect.y   += int(self.vy)
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vy >= 0:   # 낙하 중 → 바닥 착지
                    self.rect.bottom = plat.top
                    self.vy          = 0
                    self.on_ground   = True
                elif self.vy < 0:  # 상승 중 → 천장에 막힘
                    self.rect.top = plat.bottom
                    self.vy       = 0

        # ── 적끼리 밀어내기 + 방향 전환 ──
        for other in all_enemies:
            if other is self or not other.alive:
                continue
            if self.rect.colliderect(other.rect):
                # 자신만 밀어냄 (other는 other의 update에서 처리)
                if self.rect.centerx <= other.rect.centerx:
                    self.rect.x -= 2
                else:
                    self.rect.x += 2

                # 왕복형끼리 충돌 → 방향 반전
                if self.type == ENEMY_WALKER and other.type == ENEMY_WALKER:
                    self.direction *= -1

                # 추적형이 왕복형에 닿으면 점프해서 피하기
                if self.type == ENEMY_CHASER and other.type == ENEMY_WALKER:
                    if self.on_ground and self.jump_cooldown <= 0:
                        self.vy            = JUMP_POWER * 0.6
                        self.on_ground     = False
                        self.jump_cooldown = 30

        # ── 낙사 — 즉시 사망 ──
        if self.rect.top > FALL_DEATH_Y:
            self.alive = False

        # ── 독 지속 데미지 ──
        if self.poison_timer > 0:
            self.poison_timer -= 1
            if self.poison_timer % 20 == 0:   # 0.33초마다 데미지
                self.take_damage(8)

    def take_damage(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False

    def draw(self, surface, cam):
        sr = cam.to_screen_rect(self.rect)
        if sr.right > 0 and sr.left < WIDTH:
            # 타입별 색상
            if self.type == ENEMY_WALKER:
                col      = (200, 120, 40)
                col_edge = (150, 80,  20)
            elif self.type == ENEMY_SHOOTER:
                col      = (180, 50, 200)   # 보라 — 슈터
                col_edge = (120, 20, 160)
            elif self.is_patrol:
                col      = (180, 80,  80)
                col_edge = (140, 30,  30)
            else:
                col      = RED
                col_edge = (140, 30,  30)

            pygame.draw.rect(surface, col,      sr, border_radius=4)
            pygame.draw.rect(surface, col_edge, sr, 2, border_radius=4)
            if self.poison_timer > 0:
                pygame.draw.rect(surface, (80, 255, 80), sr, 2, border_radius=4)
            bx, by = sr.x, sr.y - 10
            pygame.draw.rect(surface, GRAY,  (bx, by, sr.w, 5))
            pygame.draw.rect(surface, GREEN, (bx, by, int(sr.w * max(0, self.hp / self.max_hp)), 5))

        # 슈터 총알 그리기 (항상)
        for eb in self.enemy_bullets:
            eb.draw(surface, cam)

# ──────────────────────────────────────────
#  플레이어
# ──────────────────────────────────────────
class Player:
    def __init__(self, x, y):
        self.rect              = pygame.Rect(x, y, PLAYER_W, PLAYER_H)
        self.vx                = 0.0
        self.vy                = 0.0
        self.on_ground         = False
        self.on_wall_left      = False
        self.on_wall_right     = False
        self.last_wall_jump    = 0
        self.hp                = 30
        self.max_hp            = 30
        self.bullets           = []
        self.last_shot         = 0
        self.bullet_damage     = BASE_BULLET_DAMAGE
        self.bullet_speed      = BASE_BULLET_SPEED
        self.max_ammo          = BASE_MAX_AMMO
        self.reload_time       = BASE_RELOAD_TIME
        self.ammo              = BASE_MAX_AMMO
        self.reloading         = False
        self.reload_start      = 0
        self.invincible        = False
        self.invincible_start  = 0
        self.invincible_time   = 1000
        self.blink_visible     = True

        # 버프 추가 변수
        self.bullet_count      = 1       # 동시 발사 수
        self.bullet_bouncy     = False   # 바운스 탄
        self.bullet_homing     = False   # 유도탄
        self.bullet_poison     = False   # 독 탄환
        self.bullet_radius     = 5       # 탄환 크기
        self.shoot_cooldown    = SHOOT_COOLDOWN  # 개별 공격속도
        self.leech             = False   # 흡혈
        self.decay             = False   # 피해 분산
        self.decay_pending     = 0
        self.brawler           = False   # 싸움꾼
        self.brawler_timer     = 0
        self.chase             = False   # 추격
        self.cold_bullets      = False   # 빙결 탄환
        self.dazzle            = False   # 눈부심
        self.timed_det         = False   # 시한폭탄
        self.bombs_away        = False   # 폭탄 나가신다
        self.healing_field     = False   # 치유장

        # 블록 시스템
        self.blocking           = False
        self.block_timer        = 0
        self.block_duration     = 18      # 0.3초 (60fps)
        self.block_cooldown     = 0
        self.block_cooldown_max = 120     # 2초 쿨타임

    def apply_buff(self, buff_id):
        # ── 흔함 ──
        if buff_id == "burst":
            self.max_ammo      += 3
            self.ammo           = min(self.ammo + 3, self.max_ammo)
            self.bullet_count   = min(self.bullet_count + 2, 9)
            self.bullet_damage  = max(5, int(self.bullet_damage * 0.4))
            self.reload_time   += 250
        elif buff_id == "quick_shot":
            self.bullet_speed  = min(self.bullet_speed * 2.5, BASE_BULLET_SPEED * 6)
            self.reload_time  += 250
        elif buff_id == "fastball":
            self.bullet_speed  = min(self.bullet_speed * 3.5, BASE_BULLET_SPEED * 8)
            self.shoot_cooldown = int(self.shoot_cooldown * 1.5)
            self.reload_time  += 250
        elif buff_id == "steady_shot":
            self.max_hp        = int(self.max_hp * 1.4)
            self.hp            = min(int(self.hp * 1.4), self.max_hp)
            self.bullet_speed  = min(self.bullet_speed * 2.0, BASE_BULLET_SPEED * 6)
            self.reload_time  += 250
        elif buff_id == "wind_up":
            self.bullet_damage  = int(self.bullet_damage * 1.6)
            self.bullet_speed   = min(self.bullet_speed * 2.0, BASE_BULLET_SPEED * 6)
            self.shoot_cooldown = int(self.shoot_cooldown * 2.0)
            self.reload_time   += 500
        elif buff_id == "fast_forward":
            self.bullet_speed  = min(self.bullet_speed * 2.0, BASE_BULLET_SPEED * 6)
            self.reload_time   = int(self.reload_time * 0.7)
        elif buff_id == "dazzle":
            self.dazzle         = True
            self.reload_time   += 250
        elif buff_id == "cold_bullets":
            self.cold_bullets   = True
            self.reload_time   += 250
        elif buff_id == "poison":
            self.bullet_damage  = int(self.bullet_damage * 1.7)
            self.reload_time    = int(self.reload_time * 0.7)
            self.max_ammo       = max(1, self.max_ammo - 1)
            self.ammo           = min(self.ammo, self.max_ammo)
            self.bullet_poison  = True
        elif buff_id == "timed_det":
            self.timed_det      = True
            self.bullet_damage  = max(5, int(self.bullet_damage * 0.85))
            self.reload_time   += 250
        elif buff_id == "big_bullet":
            self.bullet_radius  = min(self.bullet_radius + 3, 18)
            self.reload_time   += 250
        elif buff_id == "combine":
            self.bullet_damage  = int(self.bullet_damage * 2.0)
            self.max_ammo       = max(1, self.max_ammo - 2)
            self.ammo           = min(self.ammo, self.max_ammo)
            self.reload_time   += 500
        elif buff_id == "huge":
            bonus = int(self.max_hp * 0.8)
            self.max_hp        += bonus
            self.hp            += bonus
        elif buff_id == "tank":
            bonus = self.max_hp
            self.max_hp        += bonus
            self.hp            += bonus
            self.shoot_cooldown = int(self.shoot_cooldown * 1.25)
            self.reload_time   += 500
        elif buff_id == "leech":
            self.leech          = True
            bonus = int(self.max_hp * 0.3)
            self.max_hp        += bonus
            self.hp            += bonus
        elif buff_id == "healing_field":
            self.healing_field  = True
            bonus = int(self.max_hp * 0.3)
            self.max_hp        += bonus
            self.hp            += bonus
        # ── 드묾 ──
        elif buff_id == "barrage":
            self.bullet_count   = min(self.bullet_count + 4, 9)
            self.max_ammo      += 5
            self.ammo           = min(self.ammo + 5, self.max_ammo)
            self.bullet_damage  = max(5, int(self.bullet_damage * 0.3))
            self.reload_time   += 250
        elif buff_id == "bombs_away":
            self.bombs_away     = True
            bonus = int(self.max_hp * 0.3)
            self.max_hp        += bonus
            self.hp            += bonus
        elif buff_id == "bouncy":
            self.bullet_bouncy  = True
            self.bullet_damage  = int(self.bullet_damage * 1.25)
            self.reload_time   += 250
        elif buff_id == "brawler":
            self.brawler        = True
        elif buff_id == "buckshot":
            self.bullet_count   = min(self.bullet_count + 4, 9)
            self.max_ammo      += 5
            self.ammo           = min(self.ammo + 5, self.max_ammo)
            self.bullet_damage  = max(5, int(self.bullet_damage * 0.4))
            self.reload_time   += 250
        elif buff_id == "careful":
            self.bullet_damage  = int(self.bullet_damage * 2.0)
            self.shoot_cooldown = int(self.shoot_cooldown * 2.5)
            self.reload_time   += 500
        elif buff_id == "chase":
            self.chase          = True
            bonus = int(self.max_hp * 0.3)
            self.max_hp        += bonus
            self.hp            += bonus

    def handle_input(self, cam_x, right_bound):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx -= MOVE_ACCEL
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx += MOVE_ACCEL
        else:
            self.vx *= MOVE_FRICTION
        cap = MAX_MOVE_SPEED * self.move_speed_mult
        self.vx = max(-cap, min(cap, self.vx))
        jump = keys[pygame.K_SPACE]
        now  = pygame.time.get_ticks()

        if jump and self.on_ground:
            self.vy        = JUMP_POWER
            self.on_ground = False

        if jump and not self.on_ground:
            if self.on_wall_left or self.on_wall_right:
                if now - self.last_wall_jump >= 500:
                    self.vy             = JUMP_POWER * 0.55   # 일반 점프의 55% 높이
                    self.last_wall_jump = now

        if not jump and not self.on_ground:
            if self.on_wall_left or self.on_wall_right:
                self.vy += 0.15
                self.vy  = min(self.vy, 3.0)

        # 왼쪽 경계 = 카메라 왼쪽 끝 (화면 밖으로 못 나감)
        screen_left = int(cam_x)
        if self.rect.left < screen_left:
            self.rect.left = screen_left
            self.vx = max(0, self.vx)

        # 오른쪽 경계 (웨이브 중에만 제한)
        if right_bound is not None and self.rect.right > right_bound:
            self.rect.right = right_bound
            self.vx = min(0, self.vx)

    def try_block(self):
        """우클릭 블록 시도"""
        if self.block_cooldown > 0 or self.blocking:
            return
        self.blocking    = True
        self.block_timer = self.block_duration

    def try_shoot(self, mouse_x, mouse_y, cam):
        now = pygame.time.get_ticks()
        if self.reloading or now - self.last_shot < self.shoot_cooldown:
            return
        if self.ammo <= 0:
            self._start_reload(now)
            return

        # 마우스 화면 좌표 → 세계 좌표
        wx = mouse_x + int(cam.x)
        wy = mouse_y

        cx, cy = self.rect.centerx, self.rect.centery
        dx, dy = wx - cx, wy - cy
        dist   = math.hypot(dx, dy)
        if dist == 0:
            return

        ndx = dx / dist * self.bullet_speed
        ndy = dy / dist * self.bullet_speed

        # barrage — 여러 발 동시 발사 (부채꼴)
        angles = [0]
        if self.bullet_count > 1:
            spread = 12  # 발사 각도 간격 (도)
            for i in range(1, self.bullet_count):
                a = spread * ((i + 1) // 2) * (1 if i % 2 == 0 else -1)
                angles.append(math.radians(a))

        for angle in angles:
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            fdx   = ndx * cos_a - ndy * sin_a
            fdy   = ndx * sin_a + ndy * cos_a
            self.bullets.append(Bullet(
                cx, cy, fdx, fdy, self.bullet_damage,
                radius  = self.bullet_radius,
                bouncy  = self.bullet_bouncy,
                homing  = self.bullet_homing,
                poison  = self.bullet_poison,
                cold    = self.cold_bullets,
                dazzle  = self.dazzle,
            ))

        self.last_shot = now
        self.ammo     -= 1
        if self.ammo <= 0:
            self._start_reload(now)

    def _start_reload(self, now):
        self.reloading    = True
        self.reload_start = now

    def update(self, enemies=None):
        now = pygame.time.get_ticks()

        if self.reloading and now - self.reload_start >= self.reload_time:
            self.reloading = False
            self.ammo      = self.max_ammo

        if self.invincible:
            elapsed = now - self.invincible_start
            if elapsed >= self.invincible_time:
                self.invincible    = False
                self.blink_visible = True
            else:
                self.blink_visible = (elapsed // 100) % 2 == 0

        # 싸움꾼 타이머 감소
        if self.brawler and self.brawler_timer > 0:
            self.brawler_timer -= 1

        # 블록 타이머 처리
        if self.blocking:
            self.block_timer -= 1
            if self.block_timer <= 0:
                self.blocking           = False
                self.block_cooldown     = self.block_cooldown_max
        if self.block_cooldown > 0:
            self.block_cooldown -= 1

        # 피해 분산 — 매 프레임 대기 피해 조금씩 적용
        if self.decay and self.decay_pending > 0:
            tick_dmg          = max(1, self.decay_pending // 30)
            self.hp           = max(0, self.hp - tick_dmg)
            self.decay_pending = max(0, self.decay_pending - tick_dmg)

        # 중력
        on_wall = (self.on_wall_left or self.on_wall_right) and not self.on_ground
        self.vy += GRAVITY * 0.2 if on_wall else GRAVITY
        if self.vy > MAX_FALL_SPEED:
            self.vy = MAX_FALL_SPEED

        # 수평 이동 + 벽 감지
        self.rect.x       += int(self.vx)
        self.on_wall_left  = False
        self.on_wall_right = False

        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vx > 0:
                    self.rect.right    = plat.left
                    self.on_wall_right = True
                elif self.vx < 0:
                    self.rect.left    = plat.right
                    self.on_wall_left = True
                self.vx = 0

        if self.rect.left <= 0:
            self.on_wall_left = True
        if self.rect.right >= TOTAL_MAP_W:
            self.on_wall_right = True

        # 수직 이동
        self.rect.y   += int(self.vy)
        self.on_ground = False

        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.vy >= 0:
                    self.rect.bottom = plat.top
                    self.vy          = 0
                    self.on_ground   = True
                elif self.vy < 0:
                    self.rect.top = plat.bottom
                    self.vy       = 0

        for b in self.bullets:
            b.update(enemies)
        self.bullets = [b for b in self.bullets if b.alive]

        # 낙사 감지
        if self.rect.top > FALL_DEATH_Y:
            self.take_damage(10)
            best_y = GROUND_Y
            for plat in platforms:
                if plat.left <= self.rect.centerx <= plat.right:
                    if plat.top < best_y:
                        best_y = plat.top
            self.rect.bottom = best_y - 5
            self.vy          = JUMP_POWER * 1.2
            self.vx          = 0

    def take_damage(self, dmg):
        if self.invincible:
            return False
        if self.decay:
            # 피해 분산 — 즉시 적용 대신 대기열에 추가
            self.decay_pending += dmg
        else:
            self.hp = max(0, self.hp - dmg)
        self.invincible       = True
        self.invincible_start = pygame.time.get_ticks()
        self.blink_visible    = True
        return True

    def on_kill(self, kill_x, kill_y, all_bullets_ref):
        """적 처치 시 호출"""
        if self.leech:
            self.hp = min(self.max_hp, self.hp + int(self.max_hp * 0.05))
        if self.brawler:
            self.brawler_timer = 180   # 3초
        if self.healing_field:
            # 처치 위치에 회복 효과 — 플레이어가 근처 있으면 회복
            if abs(self.rect.centerx - kill_x) < 150:
                self.hp = min(self.max_hp, self.hp + 5)
        if self.bombs_away:
            # 처치 위치에 폭발 탄환 추가 (외부에서 처리)
            return True   # 폭발 신호
        return False

    @property
    def move_speed_mult(self):
        mult = 1.0
        # 싸움꾼 — 피해 입히면 3초간 HP +200% (이동속도는 그대로)
        # 추격 — 앞으로 이동 시 +60%
        if self.chase and self.vx > 0:
            mult *= 1.6
        return mult

    @property
    def hp_mult(self):
        """싸움꾼 활성화 시 HP 배율"""
        if self.brawler and self.brawler_timer > 0:
            return 3.0
        return 1.0

    def draw(self, surface, cam):
        sr = cam.to_screen_rect(self.rect)
        if self.blocking:
            # 블록 중 — 흰색으로 변신
            pygame.draw.rect(surface, WHITE, sr, border_radius=6)
            pygame.draw.rect(surface, CYAN,  sr, 2, border_radius=6)
            # 주변 흰 원
            cx = sr.x + sr.w // 2
            cy = sr.y + sr.h // 2
            radius = int(50 * (self.block_timer / self.block_duration)) + 20
            pygame.draw.circle(surface, WHITE, (cx, cy), radius, 2)
            pygame.draw.circle(surface, (200, 200, 255), (cx, cy), radius - 6, 1)
        elif self.blink_visible:
            pygame.draw.rect(surface, BLUE, sr, border_radius=6)
            pygame.draw.rect(surface, CYAN, sr, 2, border_radius=6)
        for b in self.bullets:
            b.draw(surface, cam)

# ──────────────────────────────────────────
#  웨이브 배너 (플레이 중 오버레이)
# ──────────────────────────────────────────
class WaveBanner:
    def __init__(self, wave_num):
        self.wave_num  = wave_num
        self.timer     = 0
        self.duration  = 120   # 2초
        self.done      = False

    def update(self):
        self.timer += 1
        if self.timer >= self.duration:
            self.done = True

    def draw(self, surface):
        p     = self.timer / self.duration
        alpha = int(255 * (p / 0.2))       if p < 0.2 else \
                255                         if p < 0.7 else \
                int(255 * (1.0 - (p - 0.7) / 0.3))

        font = get_font(100)
        text = font.render(f"Wave {self.wave_num}", True, CYAN)
        surf = pygame.Surface(text.get_size(), pygame.SRCALPHA)
        surf.blit(text, (0, 0))
        surf.set_alpha(alpha)
        surface.blit(surf, (WIDTH // 2 - text.get_width() // 2,
                             HEIGHT // 2 - text.get_height() // 2))

# ──────────────────────────────────────────
#  HUD
# ──────────────────────────────────────────
def draw_hud(surface, player, wave):
    fs = get_font(24)
    fb = get_font(32)

    # HP 바
    pygame.draw.rect(surface, GRAY, (20, 20, 200, 20), border_radius=4)
    r = max(0, player.hp / player.max_hp)
    c = GREEN if r > 0.5 else ORANGE if r > 0.25 else RED
    pygame.draw.rect(surface, c,     (20, 20, int(200 * r), 20), border_radius=4)
    pygame.draw.rect(surface, WHITE, (20, 20, 200, 20), 2, border_radius=4)
    surface.blit(fs.render(f"HP  {player.hp} / {player.max_hp}", True, WHITE), (228, 22))

    # 탄약
    if player.reloading:
        now  = pygame.time.get_ticks()
        prog = min(1.0, (now - player.reload_start) / player.reload_time)
        pygame.draw.rect(surface, GRAY,   (20, 50, 120, 14), border_radius=3)
        pygame.draw.rect(surface, ORANGE, (20, 50, int(120 * prog), 14), border_radius=3)
        pygame.draw.rect(surface, WHITE,  (20, 50, 120, 14), 1, border_radius=3)
        surface.blit(fs.render("재장전 중...", True, ORANGE), (148, 50))
    else:
        for i in range(player.max_ammo):
            cx = 26 + i * 22
            pygame.draw.circle(surface, YELLOW if i < player.ammo else GRAY, (cx, 57), 8)
            pygame.draw.circle(surface, WHITE, (cx, 57), 8, 1)

    # 웨이브
    wt = fb.render(f"Wave {wave}", True, CYAN)
    surface.blit(wt, (WIDTH // 2 - wt.get_width() // 2, 15))

    # 조준 커서
    mx, my = pygame.mouse.get_pos()
    pygame.draw.circle(surface, WHITE, (mx, my), 6, 1)
    pygame.draw.circle(surface, CYAN,  (mx, my), 3, 1)

# ──────────────────────────────────────────
#  버프 선택 화면
# ──────────────────────────────────────────
def draw_buff_select(surface, cards, hovered):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    ft = get_font(48)
    fn = get_font(30)
    fd = get_font(22)

    t = ft.render("버프를 선택하세요", True, WHITE)
    surface.blit(t, (WIDTH // 2 - t.get_width() // 2, 60))

    cw, ch  = 220, 260
    start_x = (WIDTH - (cw * 3 + 80)) // 2
    cy_base = HEIGHT // 2 - ch // 2

    for i, buff in enumerate(cards):
        cx    = start_x + i * (cw + 40)
        hover = (i == hovered)
        cy    = cy_base - (10 if hover else 0)
        cr    = pygame.Rect(cx, cy, cw, ch)

        pygame.draw.rect(surface, (30, 30, 50), cr, border_radius=12)
        pygame.draw.rect(surface, buff["color"], cr, 3, border_radius=12)

        if hover:
            g = pygame.Surface((cw, ch), pygame.SRCALPHA)
            g.fill((*buff["color"], 40))
            surface.blit(g, (cx, cy))

        pygame.draw.rect(surface, buff["color"],
                         pygame.Rect(cx, cy, cw, 8),
                         border_top_left_radius=12, border_top_right_radius=12)

        ns = fn.render(buff["name"], True, buff["color"])
        surface.blit(ns, (cx + cw // 2 - ns.get_width() // 2, cy + 30))

        pygame.draw.line(surface, buff["color"], (cx + 20, cy + 70), (cx + cw - 20, cy + 70), 1)

        for j, line in enumerate(buff["desc"].split("\n")):
            ds = fd.render(line, True, (200, 200, 200))
            surface.blit(ds, (cx + cw // 2 - ds.get_width() // 2, cy + 90 + j * 26))

        ns2 = fd.render(f"[ {i+1} ]", True, GRAY)
        surface.blit(ns2, (cx + cw // 2 - ns2.get_width() // 2, cy + ch - 35))

# ──────────────────────────────────────────
#  게임오버 화면
# ──────────────────────────────────────────
def draw_game_over(surface, wave):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))

    gt = get_font(80).render("GAME OVER", True, RED)
    surface.blit(gt, (WIDTH // 2 - gt.get_width() // 2, HEIGHT // 2 - 100))

    wt = get_font(32).render(f"도달한 웨이브: {wave}", True, WHITE)
    surface.blit(wt, (WIDTH // 2 - wt.get_width() // 2, HEIGHT // 2 + 10))

    ht = get_font(24).render("R: 다시 시작    ESC: 종료", True, GRAY)
    surface.blit(ht, (WIDTH // 2 - ht.get_width() // 2, HEIGHT // 2 + 70))

# ──────────────────────────────────────────
#  적 스폰
# ──────────────────────────────────────────
def spawn_wave_enemies(wave, zone_x):
    """웨이브 구역 적 스폰"""
    count   = 2 + wave
    enemies = []
    for _ in range(count):
        side = random.choice([-1, 1])
        x    = zone_x + side * random.randint(100, 400)
        x    = max(zone_x - 500, min(zone_x + 500, x))
        enemies.append(Enemy(x, 100))
    return enemies

def get_ground_y(world_x):
    """주어진 x 위치에서 가장 위쪽 발판의 top y를 반환. 없으면 HEIGHT+100"""
    best_y = HEIGHT + 100
    for plat in platforms:
        if plat.left <= world_x <= plat.right:
            if plat.top < best_y:
                best_y = plat.top
    return best_y

def is_safe_spawn(world_x, min_width=60):
    """스폰 위치 좌우 min_width 범위 안에 발판이 충분히 있는지 확인"""
    gy = get_ground_y(world_x)
    if gy >= HEIGHT + 100:
        return False  # 발판 자체가 없음

    # 좌우로 적 크기(36px) + 여유 공간만큼 발판이 있는지 확인
    left_ok  = get_ground_y(world_x - min_width) < HEIGHT + 100
    right_ok = get_ground_y(world_x + min_width) < HEIGHT + 100
    return left_ok and right_ok

def find_safe_spawn(candidates, min_width=60):
    """후보 x 좌표 중 안전한 위치 반환. 없으면 가장 가까운 발판 위치 탐색"""
    for x in candidates:
        if is_safe_spawn(x, min_width):
            return x, get_ground_y(x)

    # 후보 중 안전한 곳 없으면 발판 목록에서 직접 찾기
    for plat in platforms:
        cx = plat.centerx
        if is_safe_spawn(cx, min_width):
            return cx, plat.top
    return candidates[0], get_ground_y(candidates[0])  # 최후 fallback

# ──────────────────────────────────────────
#  스폰 예고 클래스
# ──────────────────────────────────────────
SPAWN_WARN_TIME = 90   # 예고 표시 시간 (프레임)

class SpawnWarning:
    def __init__(self, x, y, enemy_type, is_patrol=False):
        self.world_x    = x
        self.world_y    = y
        self.enemy_type = enemy_type
        self.is_patrol  = is_patrol
        self.timer      = 0
        self.done       = False

    def update(self):
        self.timer += 1
        if self.timer >= SPAWN_WARN_TIME:
            self.done = True

    def spawn_enemy(self):
        return Enemy(self.world_x, self.world_y, self.is_patrol, self.enemy_type)

    def draw(self, surface, cam):
        sx = cam.to_screen(self.world_x)
        if not (-60 < sx < WIDTH + 60):
            return
        # 깜빡임 (10프레임마다)
        if (self.timer // 10) % 2 == 0:
            rect = pygame.Rect(sx - 18, self.world_y, 36, 36)
            pygame.draw.rect(surface, (180, 0, 0), rect, border_radius=4)
            pygame.draw.rect(surface, RED, rect, 2, border_radius=4)
            ft = get_font(28)
            t  = ft.render("!", True, WHITE)
            surface.blit(t, (sx - t.get_width() // 2, self.world_y + 4))

def spawn_patrol_enemies(zone_x, next_zone_x):
    """이동 구간 중간에 출몰하는 적 1마리"""
    attempts = 0
    while attempts < 20:
        attempts += 1
        span = max(1, next_zone_x - 300 - (zone_x + 300))
        x    = zone_x + 300 + random.randint(0, span)
        if is_safe_spawn(x):
            gy = get_ground_y(x)
            return [Enemy(x, gy - 36, is_patrol=True)]
    return []

def spawn_wave_enemies(wave, zone_x):
    """웨이브 구역 적 스폰 예고 목록 반환"""
    count    = 2 + wave
    warnings = []
    # 후보 위치들
    candidates = [
        zone_x - 350, zone_x - 250, zone_x - 150,
        zone_x - 50,  zone_x + 50,  zone_x + 150,
        zone_x + 250, zone_x + 380,
    ]
    random.shuffle(candidates)

    used_xs = []
    for cx in candidates:
        if len(warnings) >= count:
            break
        # 이미 사용한 위치와 너무 가깝지 않은지 확인 (60px 이상 간격)
        too_close = any(abs(cx - ux) < 60 for ux in used_xs)
        if too_close:
            continue
        if is_safe_spawn(cx):
            gy = get_ground_y(cx)
            if wave >= 3 and random.random() < 0.2:
                etype = ENEMY_SHOOTER
            else:
                etype = random.choice([ENEMY_CHASER, ENEMY_WALKER])
            warnings.append(SpawnWarning(cx, gy - 36, etype))
            used_xs.append(cx)

    # 후보 중 안전한 곳이 부족하면 발판에서 직접 찾기
    if len(warnings) < count:
        for plat in platforms:
            if len(warnings) >= count:
                break
            cx = plat.centerx
            if abs(cx - zone_x) > 600:
                continue
            too_close = any(abs(cx - ux) < 60 for ux in used_xs)
            if too_close:
                continue
            if is_safe_spawn(cx):
                if wave >= 3 and random.random() < 0.2:
                    etype = ENEMY_SHOOTER
                else:
                    etype = random.choice([ENEMY_CHASER, ENEMY_WALKER])
                warnings.append(SpawnWarning(cx, plat.top - 36, etype))
                used_xs.append(cx)

    return warnings

# ──────────────────────────────────────────
#  플랫폼 그리기
# ──────────────────────────────────────────
def draw_platforms(surface, cam):
    for plat in platforms:
        sr = cam.to_screen_rect(plat)
        # sr.x 기준이 아닌 실제 화면 겹침 여부로 판단
        if sr.right > 0 and sr.left < WIDTH:
            pygame.draw.rect(surface, (60, 60, 80),    sr, border_radius=4)
            pygame.draw.rect(surface, (100, 100, 130), sr, 2, border_radius=4)

def draw_zone_marker(surface, cam, zone_x, wave_num, active):
    """웨이브 구역 표시선"""
    sx = cam.to_screen(zone_x)
    if -10 < sx < WIDTH + 10:
        color = RED if active else (80, 80, 80)
        pygame.draw.line(surface, color, (sx, 0), (sx, HEIGHT), 2)
        label = get_font(20).render(f"W{wave_num}", True, color)
        surface.blit(label, (sx + 4, 10))

# ──────────────────────────────────────────
#  메인
# ──────────────────────────────────────────
def main():
    player        = Player(100, 480)
    cam           = Camera()
    wave          = 0
    next_wave_i   = 0
    state         = STATE_PLAY
    buff_cards    = []
    hovered_card  = -1
    wave_banner   = None
    in_wave_zone  = False
    right_bound   = None
    all_enemies   = []
    spawn_warnings = []
    shake_timer   = 0      # 흔들림 지속 프레임
    shake_amount  = 0      # 흔들림 강도

    # 첫 구간 순찰 적 생성
    if WAVE_ZONES:
        all_enemies += spawn_patrol_enemies(0, WAVE_ZONES[0])
    for i in range(len(WAVE_ZONES) - 1):
        all_enemies += spawn_patrol_enemies(WAVE_ZONES[i], WAVE_ZONES[i + 1])

    while True:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()

        # ── 이벤트 ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()

                if event.key == pygame.K_r and state == STATE_GAME_OVER:
                    return main()

                if event.key == pygame.K_r and state == STATE_PLAY:
                    if not player.reloading and player.ammo < player.max_ammo:
                        player._start_reload(pygame.time.get_ticks())

                # ── P키 치트 — Wave 7 구역으로 순간이동 ──
                if event.key == pygame.K_p and state == STATE_PLAY:
                    target_i = len(WAVE_ZONES) - 1
                    target_x = WAVE_ZONES[target_i] - 200
                    player.rect.x  = target_x
                    player.rect.y  = 400
                    player.vx      = 0
                    player.vy      = 0
                    next_wave_i    = target_i
                    wave           = target_i   # wave 카운터도 맞춰줌
                    in_wave_zone   = False
                    cam.locked     = False
                    right_bound    = None
                    wave_banner    = None
                    spawn_warnings = []
                    all_enemies    = []
                    cam.x          = max(0, target_x - WIDTH * 0.4)

            if state == STATE_PLAY:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    player.try_shoot(mx, my, cam)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    player.try_block()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    player.try_block()

            elif state == STATE_BUFF_SELECT:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hovered_card >= 0:
                        player.apply_buff(buff_cards[hovered_card]["id"])
                        in_wave_zone   = False
                        cam.locked     = False
                        right_bound    = None
                        wave_banner    = None
                        state          = STATE_PLAY

                if event.type == pygame.KEYDOWN:
                    for i, key in enumerate([pygame.K_1, pygame.K_2, pygame.K_3]):
                        if event.key == key and i < len(buff_cards):
                            player.apply_buff(buff_cards[i]["id"])
                            in_wave_zone   = False
                            cam.locked     = False
                            right_bound    = None
                            wave_banner    = None
                            state          = STATE_PLAY

        # ── 호버 계산 ──
        if state == STATE_BUFF_SELECT:
            cw, ch  = 220, 260
            start_x = (WIDTH - (cw * 3 + 80)) // 2
            cy_base = HEIGHT // 2 - ch // 2
            hovered_card = -1
            for i in range(len(buff_cards)):
                cx   = start_x + i * (cw + 40)
                crct = pygame.Rect(cx, cy_base - 10, cw, ch + 10)
                if crct.collidepoint(mx, my):
                    hovered_card = i

        # ── 업데이트 ──
        if state == STATE_PLAY:
            player.handle_input(cam.x, right_bound)
            player.update(all_enemies)
            cam.update(player.rect.centerx)

            # 웨이브 구역 진입 감지
            if not in_wave_zone and next_wave_i < len(WAVE_ZONES):
                if player.rect.centerx >= WAVE_ZONES[next_wave_i]:
                    in_wave_zone   = True
                    cam.locked     = True
                    right_bound    = WAVE_ZONES[next_wave_i] + WIDTH // 2
                    wave          += 1
                    wave_banner    = WaveBanner(wave)
                    spawn_warnings = []
                    next_wave_i   += 1

            # 배너 업데이트 — 끝나면 스폰 예고 시작
            if wave_banner and not wave_banner.done:
                wave_banner.update()
                if wave_banner.done:
                    # 배너 끝 → 스폰 예고 생성
                    spawn_warnings = spawn_wave_enemies(
                        next_wave_i, WAVE_ZONES[next_wave_i - 1]
                    )

            # 스폰 예고 업데이트 — 완료되면 실제 적으로 전환
            still_warning = []
            for w in spawn_warnings:
                w.update()
                if w.done:
                    all_enemies.append(w.spawn_enemy())
                else:
                    still_warning.append(w)
            spawn_warnings = still_warning

            # 왕복 적 — 화면(카메라) 경계에서 반전
            cam_left  = int(cam.x)
            cam_right = int(cam.x) + WIDTH
            for e in all_enemies:
                if e.alive and e.type == ENEMY_WALKER:
                    if e.rect.left <= cam_left or e.rect.right >= cam_right:
                        e.direction *= -1
                        # 경계 밖으로 나간 경우 보정
                        e.rect.left  = max(e.rect.left,  cam_left)
                        e.rect.right = min(e.rect.right, cam_right)

            # 적 업데이트
            for e in all_enemies:
                if e.alive:
                    e.update(player.rect.centerx, player.rect.centery, all_enemies)

            # 총알 충돌
            for b in player.bullets:
                for e in all_enemies:
                    if e.alive and b.alive and b.get_world_rect().colliderect(e.rect):
                        e.take_damage(b.damage)
                        if b.poison:
                            e.poison_timer = 120
                        if b.cold:
                            e.slow_timer   = 120   # 2초 빙결
                        if b.dazzle:
                            e.stun_timer   = 40    # 0.67초 스턴
                        b.alive = False
                        if not e.alive:
                            player.on_kill(e.rect.centerx, e.rect.centery, player.bullets)

            # 접촉 데미지 + 블록 밀어내기
            for e in all_enemies:
                if e.alive and e.rect.colliderect(player.rect):
                    if player.blocking:
                        # 블록 — 해당 적과 모든 적을 3배 거리 밀어냄
                        for other in all_enemies:
                            if not other.alive:
                                continue
                            dx = other.rect.centerx - player.rect.centerx
                            dy = other.rect.centery - player.rect.centery
                            dist = math.hypot(dx, dy) or 1
                            push = 3.0
                            other.rect.x += int(dx / dist * dist * push)
                            other.rect.y += int(dy / dist * dist * push)
                    else:
                        if player.take_damage(10):
                            shake_timer  = 12
                            shake_amount = 6

            # 적 총알 처리
            for e in all_enemies:
                if not e.alive or e.type != ENEMY_SHOOTER:
                    continue
                for eb in e.enemy_bullets:
                    if not eb.alive:
                        continue
                    ebr = eb.get_world_rect()
                    # 블록으로 반사
                    if player.blocking and ebr.colliderect(player.rect):
                        eb.dx       = -eb.dx
                        eb.dy       = -abs(eb.dy) * 0.8
                        eb.reflected = True
                        continue
                    # 플레이어 피격
                    if not eb.reflected and ebr.colliderect(player.rect):
                        if player.take_damage(10):
                            shake_timer  = 12
                            shake_amount = 6
                        eb.alive = False
                    # 반사 총알이 적 맞추기
                    if eb.reflected:
                        for target in all_enemies:
                            if target.alive and ebr.colliderect(target.rect):
                                target.take_damage(eb.damage)
                                eb.alive = False
                                if not target.alive:
                                    player.on_kill(target.rect.centerx, target.rect.centery, player.bullets)
                                break

            all_enemies = [e for e in all_enemies if e.alive]

            if player.hp <= 0:
                state = STATE_GAME_OVER

            # 웨이브 구역 — 배너 끝나고 예고+적 모두 처치 시 클리어
            if in_wave_zone and wave_banner and wave_banner.done:
                wave_alive = [e for e in all_enemies if not e.is_patrol]
                if len(wave_alive) == 0 and len(spawn_warnings) == 0:
                    player.hp  = min(player.max_hp, player.hp + 10)
                    buff_cards = random.sample(ALL_BUFFS, 3)
                    state      = STATE_BUFF_SELECT

        # ── 그리기 ──
        # 버퍼에 먼저 그리고 흔들림 오프셋으로 화면에 blit
        buf = pygame.Surface((WIDTH, HEIGHT))
        buf.fill(DARK)
        draw_platforms(buf, cam)

        for i, zx in enumerate(WAVE_ZONES):
            draw_zone_marker(buf, cam, zx, i + 1, i == next_wave_i)

        for w in spawn_warnings:
            w.draw(buf, cam)

        for e in all_enemies:
            e.draw(buf, cam)

        player.draw(buf, cam)
        draw_hud(buf, player, wave)

        if wave_banner and not wave_banner.done:
            wave_banner.draw(buf)

        if state == STATE_BUFF_SELECT:
            draw_buff_select(buf, buff_cards, hovered_card)
        elif state == STATE_GAME_OVER:
            draw_game_over(buf, wave)

        # 흔들림 오프셋 계산
        if shake_timer > 0:
            shake_timer -= 1
            ox = random.randint(-shake_amount, shake_amount)
            oy = random.randint(-shake_amount, shake_amount)
        else:
            ox, oy = 0, 0

        screen.fill(DARK)
        screen.blit(buf, (ox, oy))

        pygame.display.flip()

if __name__ == "__main__":
    main()
