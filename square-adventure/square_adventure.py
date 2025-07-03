import pygame
import sys
import random
import math
from typing import List, Tuple

# 初始化pygame
pygame.init()

# 设置中文字体支持
try:
    # 尝试加载中文字体
    font_path = "/System/Library/Fonts/PingFang.ttc"  # macOS中文字体
    pygame.font.Font(font_path, 24)
    FONT_PATH = font_path
except:
    try:
        # 备用字体
        font_path = "/System/Library/Fonts/Arial Unicode.ttf"
        pygame.font.Font(font_path, 24)
        FONT_PATH = font_path
    except:
        # 使用默认字体
        FONT_PATH = None

# 游戏常量
SCREEN_SIZE = 800  # 正方形窗口尺寸
MAP_SIZE = 600     # 地图尺寸（留出边界）
MAP_OFFSET = (SCREEN_SIZE - MAP_SIZE) // 2  # 地图居中偏移
GRID_SIZE = 30     # 网格大小

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
GREEN = (0, 200, 0)      # 绿色方块
BLUE = (0, 100, 255)     # 蓝色眼睛
RED = (255, 0, 0)        # 红色怪物
YELLOW = (255, 255, 0)   # 黄色圆点
WALL_COLOR = (0, 0, 0)   # 黑色墙体
PURPLE = (128, 0, 128)   # 紫色怪物
ORANGE = (255, 165, 0)   # 橙色怪物

# 玩家设置
PLAYER_SIZE = 28
PLAYER_SPEED = 4

# 怪物设置
MONSTER_SIZE = 26
MONSTER_SPEED = 1
MONSTER_COUNT = 3

# 游戏对象设置
WALL_COUNT = 25          # 增加墙体数量
COIN_COUNT = 15          # 初始金币数量
COIN_SIZE = 8            # 金币半径
COIN_SCORE = 10          # 每个金币得分

class Wall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = GRID_SIZE
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def draw(self, screen):
        pygame.draw.rect(screen, WALL_COLOR, self.get_rect())
        pygame.draw.rect(screen, WHITE, self.get_rect(), 2)

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = COIN_SIZE
        self.active = True
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, 
                          self.size * 2, self.size * 2)
    
    def draw(self, screen):
        if self.active:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, (255, 215, 0), (int(self.x), int(self.y)), self.size - 2)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.color = GREEN
    
    def move(self, dx, dy, walls):
        """移动玩家，但不能超出地图边界或穿过墙体"""
        new_x = self.x + dx
        new_y = self.y + dy
        
        # 创建新位置的矩形
        new_rect = pygame.Rect(new_x, new_y, self.size, self.size)
        
        # 检查边界
        if (MAP_OFFSET <= new_x <= MAP_OFFSET + MAP_SIZE - self.size and
            MAP_OFFSET <= new_y <= MAP_OFFSET + MAP_SIZE - self.size):
            
            # 检查是否与墙体碰撞
            can_move = True
            for wall in walls:
                if new_rect.colliderect(wall.get_rect()):
                    can_move = False
                    break
            
            if can_move:
                self.x = new_x
                self.y = new_y
    
    def get_rect(self):
        """获取玩家的矩形区域"""
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def draw(self, screen):
        """绘制玩家"""
        # 主体 - 绿色
        pygame.draw.rect(screen, self.color, self.get_rect())
        # 边框
        pygame.draw.rect(screen, WHITE, self.get_rect(), 2)
        # 蓝色眼睛
        eye_size = 4
        pygame.draw.circle(screen, BLUE, 
                         (int(self.x + self.size//3), int(self.y + self.size//3)), eye_size)
        pygame.draw.circle(screen, BLUE, 
                         (int(self.x + 2*self.size//3), int(self.y + self.size//3)), eye_size)

class Monster:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.size = MONSTER_SIZE
        self.speed = MONSTER_SPEED
        self.color = color
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])  # 随机初始方向
        self.move_timer = 0
        self.direction_change_interval = random.randint(60, 180)  # 1-3秒改变方向
    
    def update(self, walls):
        """更新怪物位置和AI"""
        self.move_timer += 1
        
        # 随机改变方向
        if self.move_timer >= self.direction_change_interval:
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            self.move_timer = 0
            self.direction_change_interval = random.randint(60, 180)
        
        # 尝试移动
        dx = self.direction[0] * self.speed
        dy = self.direction[1] * self.speed
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        # 创建新位置的矩形
        new_rect = pygame.Rect(new_x, new_y, self.size, self.size)
        
        # 检查边界和墙体碰撞
        if (MAP_OFFSET <= new_x <= MAP_OFFSET + MAP_SIZE - self.size and
            MAP_OFFSET <= new_y <= MAP_OFFSET + MAP_SIZE - self.size):
            
            # 检查是否与墙体碰撞
            can_move = True
            for wall in walls:
                if new_rect.colliderect(wall.get_rect()):
                    can_move = False
                    break
            
            if can_move:
                self.x = new_x
                self.y = new_y
            else:
                # 如果不能移动，随机选择新方向
                self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                self.move_timer = 0
        else:
            # 如果到达边界，随机选择新方向
            self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            self.move_timer = 0
    
    def get_rect(self):
        """获取怪物的矩形区域"""
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def draw(self, screen):
        """绘制怪物"""
        # 主体
        pygame.draw.rect(screen, self.color, self.get_rect())
        # 边框
        pygame.draw.rect(screen, WHITE, self.get_rect(), 2)
        # 白色眼睛
        eye_size = 3
        pygame.draw.circle(screen, WHITE, 
                         (int(self.x + self.size//3), int(self.y + self.size//3)), eye_size)
        pygame.draw.circle(screen, WHITE, 
                         (int(self.x + 2*self.size//3), int(self.y + self.size//3)), eye_size)
        # 黑色瞳孔
        pygame.draw.circle(screen, BLACK, 
                         (int(self.x + self.size//3), int(self.y + self.size//3)), eye_size-1)
        pygame.draw.circle(screen, BLACK, 
                         (int(self.x + 2*self.size//3), int(self.y + self.size//3)), eye_size-1)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        pygame.display.set_caption("方块冒险 - Square Adventure")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # 创建玩家，位置在地图中心
        center_x = MAP_OFFSET + MAP_SIZE // 2 - PLAYER_SIZE // 2
        center_y = MAP_OFFSET + MAP_SIZE // 2 - PLAYER_SIZE // 2
        self.player = Player(center_x, center_y)
        
        # 游戏状态
        self.keys_pressed = set()
        self.score = 0
        self.coins_collected = 0  # 收集的金币总数
        
        # 创建游戏对象
        self.walls = []
        self.coins = []
        self.monsters = []
        
        self.generate_walls()
        self.generate_coins()
        self.generate_monsters()
    
    def generate_walls(self):
        """生成随机墙体，避免死路"""
        self.walls = []
        grid_width = MAP_SIZE // GRID_SIZE
        grid_height = MAP_SIZE // GRID_SIZE
        
        # 创建一个网格来追踪墙体
        grid = [[False for _ in range(grid_width)] for _ in range(grid_height)]
        
        # 玩家初始位置的网格坐标
        player_grid_x = (self.player.x - MAP_OFFSET) // GRID_SIZE
        player_grid_y = (self.player.y - MAP_OFFSET) // GRID_SIZE
        
        # 生成墙体，但确保有路径
        attempts = 0
        while len(self.walls) < WALL_COUNT and attempts < 300:
            attempts += 1
            
            # 随机生成墙体位置
            grid_x = random.randint(0, grid_width - 1)
            grid_y = random.randint(0, grid_height - 1)
            
            # 避免在玩家初始位置附近生成墙体
            if abs(grid_x - player_grid_x) <= 1 and abs(grid_y - player_grid_y) <= 1:
                continue
            
            # 检查是否已经有墙体
            if grid[grid_y][grid_x]:
                continue
            
            # 临时放置墙体
            grid[grid_y][grid_x] = True
            
            # 简单检查：确保不会完全包围某个区域
            # 检查周围8个方向的墙体数量
            wall_count = 0
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = grid_x + dx, grid_y + dy
                    if 0 <= nx < grid_width and 0 <= ny < grid_height:
                        if grid[ny][nx]:
                            wall_count += 1
            
            # 如果周围墙体太多，跳过这个位置
            if wall_count >= 6:
                grid[grid_y][grid_x] = False
                continue
            
            # 创建墙体
            wall_x = MAP_OFFSET + grid_x * GRID_SIZE
            wall_y = MAP_OFFSET + grid_y * GRID_SIZE
            self.walls.append(Wall(wall_x, wall_y))
    
    def generate_coins(self):
        """生成随机金币"""
        self.coins = []
        attempts = 0
        while len(self.coins) < COIN_COUNT and attempts < 300:
            attempts += 1
            
            # 随机生成金币位置
            coin_x = random.randint(MAP_OFFSET + COIN_SIZE, MAP_OFFSET + MAP_SIZE - COIN_SIZE)
            coin_y = random.randint(MAP_OFFSET + COIN_SIZE, MAP_OFFSET + MAP_SIZE - COIN_SIZE)
            
            coin_rect = pygame.Rect(coin_x - COIN_SIZE, coin_y - COIN_SIZE, 
                                   COIN_SIZE * 2, COIN_SIZE * 2)
            
            # 检查是否与玩家初始位置重叠
            player_rect = self.player.get_rect()
            if coin_rect.colliderect(player_rect):
                continue
            
            # 检查是否与墙体重叠
            overlap = False
            for wall in self.walls:
                if coin_rect.colliderect(wall.get_rect()):
                    overlap = True
                    break
            
            if not overlap:
                # 检查是否与已存在的金币重叠
                coin_overlap = False
                for existing_coin in self.coins:
                    existing_rect = existing_coin.get_rect()
                    if coin_rect.colliderect(existing_rect):
                        coin_overlap = True
                        break
                
                if not coin_overlap:
                    self.coins.append(Coin(coin_x, coin_y))
    
    def generate_monsters(self):
        """生成怪物"""
        self.monsters = []
        monster_colors = [RED, PURPLE, ORANGE]
        
        attempts = 0
        while len(self.monsters) < MONSTER_COUNT and attempts < 100:
            attempts += 1
            
            # 随机生成怪物位置
            monster_x = random.randint(MAP_OFFSET, MAP_OFFSET + MAP_SIZE - MONSTER_SIZE)
            monster_y = random.randint(MAP_OFFSET, MAP_OFFSET + MAP_SIZE - MONSTER_SIZE)
            
            monster_rect = pygame.Rect(monster_x, monster_y, MONSTER_SIZE, MONSTER_SIZE)
            
            # 检查是否与玩家初始位置重叠
            player_rect = self.player.get_rect()
            if monster_rect.colliderect(player_rect):
                continue
            
            # 检查是否与墙体重叠
            overlap = False
            for wall in self.walls:
                if monster_rect.colliderect(wall.get_rect()):
                    overlap = True
                    break
            
            if not overlap:
                # 检查是否与已存在的怪物重叠
                monster_overlap = False
                for existing_monster in self.monsters:
                    existing_rect = existing_monster.get_rect()
                    if monster_rect.colliderect(existing_rect):
                        monster_overlap = True
                        break
                
                if not monster_overlap:
                    color = monster_colors[len(self.monsters) % len(monster_colors)]
                    self.monsters.append(Monster(monster_x, monster_y, color))
    
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    # 重置游戏
                    self.__init__()
                else:
                    self.keys_pressed.add(event.key)
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
    
    def update(self):
        """更新游戏状态"""
        # 处理玩家移动
        dx, dy = 0, 0
        
        if pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed:
            dx = -self.player.speed
        if pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed:
            dx = self.player.speed
        if pygame.K_UP in self.keys_pressed or pygame.K_w in self.keys_pressed:
            dy = -self.player.speed
        if pygame.K_DOWN in self.keys_pressed or pygame.K_s in self.keys_pressed:
            dy = self.player.speed
        
        # 移动玩家
        self.player.move(dx, dy, self.walls)
        
        # 更新怪物
        for monster in self.monsters:
            monster.update(self.walls)
        
        # 检查玩家与金币的碰撞
        player_rect = self.player.get_rect()
        for coin in self.coins:
            if coin.active and player_rect.colliderect(coin.get_rect()):
                coin.active = False
                self.score += COIN_SCORE
                self.coins_collected += 1
        
        # 检查怪物与金币的碰撞
        for monster in self.monsters:
            monster_rect = monster.get_rect()
            for coin in self.coins:
                if coin.active and monster_rect.colliderect(coin.get_rect()):
                    coin.active = False
        
        # 检查玩家与怪物的碰撞
        for monster in self.monsters:
            monster_rect = monster.get_rect()
            if player_rect.colliderect(monster_rect):
                # 玩家碰到怪物，减少1个金币的分数
                if self.coins_collected > 0:
                    self.score = max(0, self.score - COIN_SCORE)
                    self.coins_collected -= 1
                # 将怪物推开一点，避免连续碰撞
                monster.x += random.randint(-20, 20)
                monster.y += random.randint(-20, 20)
                monster.x = max(MAP_OFFSET, min(MAP_OFFSET + MAP_SIZE - MONSTER_SIZE, monster.x))
                monster.y = max(MAP_OFFSET, min(MAP_OFFSET + MAP_SIZE - MONSTER_SIZE, monster.y))
        
        # 检查是否需要重新生成金币
        if all(not coin.active for coin in self.coins):
            self.generate_coins()
    
    def draw_background(self):
        """绘制背景和地图"""
        # 清屏 - 深灰色背景
        self.screen.fill(DARK_GRAY)
        
        # 绘制地图边界
        map_rect = pygame.Rect(MAP_OFFSET, MAP_OFFSET, MAP_SIZE, MAP_SIZE)
        pygame.draw.rect(self.screen, WHITE, map_rect)  # 白色地图区域
        pygame.draw.rect(self.screen, BLACK, map_rect, 3)  # 黑色边框
        
        # 绘制网格线（淡化）
        for i in range(GRID_SIZE, MAP_SIZE, GRID_SIZE):
            # 垂直线
            pygame.draw.line(self.screen, (200, 200, 200), 
                           (MAP_OFFSET + i, MAP_OFFSET), 
                           (MAP_OFFSET + i, MAP_OFFSET + MAP_SIZE), 1)
            # 水平线
            pygame.draw.line(self.screen, (200, 200, 200), 
                           (MAP_OFFSET, MAP_OFFSET + i), 
                           (MAP_OFFSET + MAP_SIZE, MAP_OFFSET + i), 1)
    
    def get_font(self, size):
        """获取支持中文的字体"""
        if FONT_PATH:
            try:
                return pygame.font.Font(FONT_PATH, size)
            except:
                return pygame.font.Font(None, size)
        else:
            return pygame.font.Font(None, size)
    
    def draw_ui(self):
        """绘制用户界面"""
        font = self.get_font(36)
        font_small = self.get_font(24)
        
        # 标题
        title = font.render("方块冒险", True, WHITE)
        title_rect = title.get_rect()
        self.screen.blit(title, (SCREEN_SIZE//2 - title_rect.width//2, 20))
        
        # 分数
        score_text = font_small.render(f"分数: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))
        
        # 收集的金币数
        coins_text = font_small.render(f"收集金币: {self.coins_collected}", True, WHITE)
        self.screen.blit(coins_text, (20, 50))
        
        # 剩余金币数
        remaining_coins = sum(1 for coin in self.coins if coin.active)
        remaining_text = font_small.render(f"剩余金币: {remaining_coins}", True, WHITE)
        self.screen.blit(remaining_text, (20, 80))
        
        # 控制说明
        controls = [
            "方向键/WASD: 移动",
            "避开怪物方块",
            "R键: 重新开始",
            "ESC: 退出游戏"
        ]
        
        for i, text in enumerate(controls):
            control_text = font_small.render(text, True, WHITE)
            self.screen.blit(control_text, (20, SCREEN_SIZE - 110 + i * 25))
    
    def draw(self):
        """绘制所有游戏元素"""
        self.draw_background()
        
        # 绘制墙体
        for wall in self.walls:
            wall.draw(self.screen)
        
        # 绘制金币
        for coin in self.coins:
            coin.draw(self.screen)
        
        # 绘制怪物
        for monster in self.monsters:
            monster.draw(self.screen)
        
        # 绘制玩家
        self.player.draw(self.screen)
        
        # 绘制UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def run(self):
        """主游戏循环"""
        print("=== 方块冒险游戏开始 ===")
        print("控制说明:")
        print("- 方向键或WASD: 移动绿色方块")
        print("- 收集黄色金币获得分数")
        print("- 避开红色/紫色/橙色怪物方块")
        print("- 怪物会吃掉金币，碰到怪物会失去金币")
        print("- R键: 重新开始")
        print("- ESC键: 退出游戏")
        print("=============================")
        
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 