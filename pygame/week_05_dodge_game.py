import pygame
import random
import sys

# 1. 초기화 및 환경 설정
pygame.init()

def get_korean_font(size):
    candidates = ["malgungothic", "applegothic", "nanumgothic", "notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent() > 0: return font
    return pygame.font.SysFont(None, size)

WIDTH, HEIGHT = 1000, 600
FPS = 60

# 색상 정의
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
BLUE, RED = (50, 120, 220), (220, 50,  50)
PURPLE, YELLOW = (160, 32, 240), (240, 200, 0)
GRAY, CYAN, GREEN = (40, 40, 40), (0, 200, 255), (0, 255, 100)
BRIGHT_BLUE = (0, 100, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blink & Color: Master Edition")
clock = pygame.time.Clock()

# 폰트 미리 로드
FONT_MAIN = get_korean_font(30)
FONT_SMALL = get_korean_font(18)
FONT_BIG = get_korean_font(80)

# [개선] 4, 5단계 추가 및 난이도 일정 상승 (스폰 간격 감소 및 속도 증가)
LEVELS = [
    {"min_speed": 3, "max_speed": 5,  "spawn": 30, "label": "Lv.1"},
    {"min_speed": 5, "max_speed": 8,  "spawn": 22, "label": "Lv.2"},
    {"min_speed": 7, "max_speed": 11, "spawn": 16, "label": "Lv.3"},
    {"min_speed": 9, "max_speed": 14, "spawn": 12, "label": "Lv.4"},
    {"min_speed": 11, "max_speed": 17, "spawn": 9,  "label": "Lv.5 (FINAL)"},
]

PLAYER_W, PLAYER_H = 50, 30
ENEMY_W,  ENEMY_H  = 30, 30

def spawn_enemy(level_cfg):
    x = random.randint(0, WIDTH - ENEMY_W)
    rect = pygame.Rect(x, -ENEMY_H, ENEMY_W, ENEMY_H)
    rand_val = random.random()
    
    if rand_val < 0.005: # 0.5% 검은색
        return [rect, random.randint(LEVELS[0]["min_speed"], LEVELS[0]["max_speed"]), BLACK, "DANGER", False]
    elif rand_val < 0.105: # 10% 보라색
        return [rect, random.randint(level_cfg["min_speed"], level_cfg["max_speed"]), PURPLE, "DASH", False]
    else:
        return [rect, random.randint(level_cfg["min_speed"], level_cfg["max_speed"]), RED, "NORMAL", False]

def draw_hud(score, level_cfg, lives, dash_cooldown, win_timer=None):
    screen.blit(FONT_MAIN.render(f"Score: {score}", True, WHITE), (20, 20))
    screen.blit(FONT_MAIN.render(f"Level: {level_cfg['label']}", True, YELLOW), (20, 55))
    
    # 5단계 생존 타이머 표시
    if win_timer is not None:
        seconds_left = max(0, win_timer // FPS)
        timer_text = f"SURVIVE: {seconds_left}s"
        screen.blit(FONT_MAIN.render(timer_text, True, CYAN), (WIDTH//2 - 80, 20))

    l_val = max(lives, 0)
    screen.blit(FONT_MAIN.render(f"Lives: {'♥ ' * l_val}", True, RED), (WIDTH - 250, 20))
    
    d_msg = "DASH: READY" if dash_cooldown == 0 else f"DASH: {dash_cooldown/60:.1f}s"
    screen.blit(FONT_MAIN.render(d_msg, True, GREEN if dash_cooldown == 0 else WHITE), (WIDTH - 250, 55))

    pygame.draw.rect(screen, (80, 80, 80), (WIDTH - 250, 90, 200, 8))
    fill = (120 - dash_cooldown) / 120
    pygame.draw.rect(screen, CYAN, (WIDTH - 250, 90, int(200 * fill), 8))

def end_screen(title, color, score):
    screen.fill(GRAY)
    screen.blit(FONT_BIG.render(title, True, color), (WIDTH//2 - 200, HEIGHT//2 - 80))
    screen.blit(FONT_MAIN.render(f"Final Score: {score}", True, WHITE), (WIDTH//2 - 80, HEIGHT//2 + 20))
    screen.blit(FONT_MAIN.render("Press 'R' to Restart or 'Q' to Quit", True, WHITE), (WIDTH//2 - 220, HEIGHT//2 + 80))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r: return True
                if e.key == pygame.K_q: return False

def main():
    while True:
        player = pygame.Rect(WIDTH // 2 - PLAYER_W // 2, HEIGHT - 60, PLAYER_W, PLAYER_H)
        enemies = []
        score, lives = 0, 3
        spawn_timer = 0
        level_idx = 0
        invincible, dash_cooldown, dash_invinc = 0, 0, 0
        last_dir = 1
        
        # 승리 관련 변수
        win_condition_timer = 30 * FPS # 30초 (1800프레임)
        game_result = "OVER" # "OVER" 또는 "WIN"

        game_running = True
        while game_running:
            clock.tick(FPS)
            level_cfg = LEVELS[level_idx]

            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player.left > 0:
                player.x -= 8
                last_dir = -1
            if keys[pygame.K_RIGHT] and player.right < WIDTH:
                player.x += 8
                last_dir = 1
            
            if keys[pygame.K_SPACE] and dash_cooldown == 0:
                player.x += (PLAYER_W * 1.5) * last_dir
                player.left = max(0, min(player.left, WIDTH - PLAYER_W))
                dash_cooldown, dash_invinc = 120, 12
            
            if dash_cooldown > 0: dash_cooldown -= 1
            if dash_invinc > 0: dash_invinc -= 1
            if invincible > 0: invincible -= 1

            # 5단계 승리 타이머 감소
            if level_idx == len(LEVELS) - 1:
                win_condition_timer -= 1
                if win_condition_timer <= 0:
                    game_result = "WIN"
                    game_running = False

            spawn_timer += 1
            if spawn_timer >= level_cfg["spawn"]:
                spawn_timer = 0
                enemies.append(spawn_enemy(level_cfg))

            survived = []
            for e_data in enemies:
                rect, speed, color, e_type, has_dashed = e_data
                rect.y += speed
                
                if e_type == "DASH" and not has_dashed and 50 <= rect.y <= 150:
                    if random.random() < 0.2:
                        dist = 80 * (1 if rect.centerx < player.centerx else -1)
                        rect.x += dist
                        rect.left = max(0, min(rect.left, WIDTH - ENEMY_W))
                        e_data[4] = True 

                if rect.top < HEIGHT:
                    survived.append(e_data)
                else:
                    score += 1
            enemies = survived

            if invincible <= 0 and dash_invinc <= 0:
                for e_data in enemies:
                    if player.colliderect(e_data[0]):
                        damage = 2 if e_data[3] == "DANGER" else 1
                        lives -= damage
                        invincible = 90
                        if lives <= 0:
                            game_result = "OVER"
                            game_running = False
                        break

            # 난이도 업데이트 (점수 20점마다 레벨업, 최대 5레벨)
            new_level_idx = min(score // 20, len(LEVELS) - 1)
            if new_level_idx != level_idx:
                level_idx = new_level_idx
                spawn_timer = 0

            # 그리기
            screen.fill(GRAY)
            if not (invincible > 0 and (invincible // 5) % 2 == 0):
                pygame.draw.rect(screen, BLUE, player)

            for e_data in enemies:
                rect, _, color, e_type, _ = e_data
                pygame.draw.rect(screen, color, rect)
                if e_type == "DANGER":
                    txt = FONT_SMALL.render("Danger!", True, BRIGHT_BLUE)
                    screen.blit(txt, (rect.x - 10, rect.y - 20))

            # HUD 그리기 (5단계일 때만 타이머 전달)
            current_win_timer = win_condition_timer if level_idx == len(LEVELS) - 1 else None
            draw_hud(score, level_cfg, lives, dash_cooldown, current_win_timer)
            pygame.display.flip()

        # 결과 화면 출력
        if game_result == "WIN":
            if not end_screen("YOU WIN!", GREEN, score): break
        else:
            if not end_screen("GAME OVER", RED, score): break

    pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()