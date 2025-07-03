import pygame
import sys
import math
import random

# 初始化pygame
pygame.init()

# 游戏常量
SCREEN_WIDTH = 1200  # 增加宽度以容纳调试面板
SCREEN_HEIGHT = 800  # 增加高度
DEBUG_PANEL_WIDTH = 220  # 调试面板宽度
GAME_AREA_X = 0  # 游戏区域从0开始，调试面板独立显示
SKY_HEIGHT = 120  # 增加天空高度以放置UI
WATER_SURFACE_HEIGHT = SKY_HEIGHT  # 水面位置
UNDERWATER_HEIGHT = SCREEN_HEIGHT - WATER_SURFACE_HEIGHT  # 水下区域

# 颜色定义
SKY_BLUE = (135, 206, 235)
DARK_BLUE = (25, 25, 112)
WATER_BLUE = (0, 100, 200)
SHIP_GRAY = (128, 128, 128)
BOMB_GRAY = (80, 80, 80)
BOMB_METAL = (160, 160, 160)
EXPLOSION_ORANGE = (255, 165, 0)
EXPLOSION_RED = (255, 69, 0)
WHITE = (255, 255, 255)
SEA_FLOOR = (139, 69, 19)
SUBMARINE_GREEN = (34, 139, 34)
SUBMARINE_DARK = (0, 100, 0)

# 游戏设置
FPS = 60
SHIP_SPEED = 5
BOMB_SPEED = 3
BOMB_RADIUS = 8
EXPLOSION_DURATION = 30  # 爆炸持续帧数

# 爆炸半径设置
BOMB_EXPLOSION_RADIUS = 100      # 炸弹爆炸半径
SUBMARINE_EXPLOSION_RADIUS = 80  # 潜艇爆炸半径
HIGH_EXPLOSIVE_RADIUS = 200      # 高爆炸弹爆炸半径（2倍）

# 高爆炸弹设置
HIGH_EXPLOSIVE_COOLDOWN = 600    # 10秒生成一枚（60FPS * 10秒）
MAX_HIGH_EXPLOSIVES = 3          # 最大存储数量

# 驱逐舰生命系统
SHIP_MAX_LIVES = 3               # 驱逐舰生命值
INVINCIBILITY_TIME = 180         # 无敌时间（3秒 * 60FPS）

# 水层定义 - 确保潜艇不会太靠近水面
SHALLOW_WATER_START = WATER_SURFACE_HEIGHT + 40  # 增加安全距离
SHALLOW_WATER_END = WATER_SURFACE_HEIGHT + 200   # 调整浅水层范围
MIDDLE_WATER_START = SHALLOW_WATER_END  
MIDDLE_WATER_END = WATER_SURFACE_HEIGHT + 400    # 调整中水层范围
DEEP_WATER_START = MIDDLE_WATER_END
DEEP_WATER_END = SCREEN_HEIGHT - 50

# 潜艇类型配置
SUBMARINE_CONFIGS = {
    'scout': {  # 侦查潜艇
        'name': 'Scout Submarine',
        'name_cn': 'Reconnaissance Submarine',
        'speed_range': (1, 2),      # 速度范围
        'depth_range': (SHALLOW_WATER_START + 20, DEEP_WATER_END - 20),  # 增加边界安全距离
        'score': 100,               # 击沉得分
        'spawn_chance': 0.006,      # 每帧生成概率
        'width': 60,                # 宽度
        'height': 20,               # 高度
        'color': SUBMARINE_GREEN,
        'dark_color': SUBMARINE_DARK,
        'special': None
    },
    'minelayer': {  # 布雷潜艇
        'name': 'Minelayer Submarine',
        'name_cn': 'Minelayer Submarine',
        'speed_range': (0.8, 1.5),  # 稍慢一些
        'depth_range': (MIDDLE_WATER_START + 20, DEEP_WATER_END - 20),  # 只在中深水层，增加安全距离
        'score': 200,               # 更高分数
        'spawn_chance': 0.003,      # 较低生成概率
        'width': 80,                # 更大一些
        'height': 25,               # 更高一些
        'color': (139, 69, 19),     # 棕色
        'dark_color': (101, 67, 33),
        'special': 'minelayer',
        'mine_cooldown': 240        # 4秒发射一枚水雷
    },
    'missile': {  # 导弹潜艇
        'name': 'Missile Submarine',
        'name_cn': 'Missile Submarine',
        'speed_range': (0.6, 1.2),  # 更慢一些，专注攻击
        'depth_range': (DEEP_WATER_START + 20, DEEP_WATER_END - 20),  # 只在深水层，增加安全距离
        'score': 300,               # 最高分数
        'spawn_chance': 0.002,      # 最低生成概率
        'width': 90,                # 最大
        'height': 30,               # 最高
        'color': (70, 70, 70),      # 深灰色
        'dark_color': (40, 40, 40),
        'special': 'missile',
        'missile_cooldown': 300     # 5秒发射一枚导弹
    }
}

class Ship:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 60  # 变窄小一些
        self.height = 20  # 降低高度
        self.speed = SHIP_SPEED
        self.lives = SHIP_MAX_LIVES  # 生命值
        self.invincible_timer = 0    # 无敌计时器
        
    def move_left(self):
        if self.x > 0:  # 允许在整个游戏区域移动
            self.x -= self.speed
            
    def move_right(self):
        if self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
    
    def get_bomb_start_pos(self):
        # 炸弹从驱逐舰中心底部发射
        return (self.x + self.width // 2, self.y + self.height)
    
    def get_rect(self):
        # 返回驱逐舰的碰撞矩形
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_invincible(self):
        return self.invincible_timer > 0
    
    def take_damage(self, god_mode=False):
        if god_mode:  # 无敌模式下不受伤
            return False
        if not self.is_invincible() and self.lives > 0:
            self.lives -= 1
            self.invincible_timer = INVINCIBILITY_TIME
            print(f"💥 Ship hit! Lives remaining: {self.lives}")
            return True
        return False
    
    def update(self):
        # 更新无敌时间
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
    
    def draw(self, screen):
        # 绘制更小的驱逐舰形状
        # 如果在无敌状态，闪烁显示
        is_flashing = self.is_invincible() and (self.invincible_timer // 10) % 2 == 0
        
        if not is_flashing:
            # 主体
            pygame.draw.rect(screen, SHIP_GRAY, (self.x, self.y, self.width, self.height))
            # 驾驶台
            pygame.draw.rect(screen, SHIP_GRAY, (self.x + 15, self.y - 10, 30, 10))
            # 烟囱
            pygame.draw.rect(screen, SHIP_GRAY, (self.x + 25, self.y - 18, 8, 8))
            # 舰首细节
            pygame.draw.polygon(screen, SHIP_GRAY, [
                (self.x + self.width, self.y + 5),
                (self.x + self.width + 8, self.y + self.height // 2),
                (self.x + self.width, self.y + self.height - 5)
            ])

class Bomb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 12
        self.height = 20
        self.speed = BOMB_SPEED
        self.active = True
        
    def update(self):
        if self.active:
            self.y += self.speed
            # 如果炸弹到达海底，就爆炸
            if self.y >= SCREEN_HEIGHT - 20:
                self.active = False
                return 'seabed'  # 返回爆炸类型
        return False
    
    def get_rect(self):
        # 返回炸弹的碰撞矩形
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, 
                          self.width, self.height)
    
    def draw(self, screen):
        if self.active:
            # 绘制桶状深海炸弹
            bomb_rect = self.get_rect()
            
            # 主体 - 灰色圆柱形
            pygame.draw.rect(screen, BOMB_GRAY, bomb_rect)
            # 上下金属环
            pygame.draw.rect(screen, BOMB_METAL, 
                           (bomb_rect.x, bomb_rect.y, bomb_rect.width, 3))
            pygame.draw.rect(screen, BOMB_METAL, 
                           (bomb_rect.x, bomb_rect.y + bomb_rect.height - 3, bomb_rect.width, 3))
            # 中间金属环
            pygame.draw.rect(screen, BOMB_METAL, 
                           (bomb_rect.x, bomb_rect.y + bomb_rect.height//2 - 1, bomb_rect.width, 2))
            # 顶部引信
            pygame.draw.circle(screen, BOMB_METAL, 
                             (int(self.x), bomb_rect.y - 2), 3)

class HighExplosiveBomb(Bomb):
    def __init__(self, x, y):
        super().__init__(x, y)
        # 高爆炸弹更大
        self.width = 20   # 2倍碰撞体积
        self.height = 30
        
    def draw(self, screen):
        if self.active:
            # 绘制更大的高爆炸弹
            bomb_rect = self.get_rect()
            
            # 主体 - 红色标识高爆炸弹
            pygame.draw.rect(screen, (180, 50, 50), bomb_rect)
            # 上下金属环
            pygame.draw.rect(screen, BOMB_METAL, 
                           (bomb_rect.x, bomb_rect.y, bomb_rect.width, 4))
            pygame.draw.rect(screen, BOMB_METAL, 
                           (bomb_rect.x, bomb_rect.y + bomb_rect.height - 4, bomb_rect.width, 4))
            # 中间金属环
            pygame.draw.rect(screen, BOMB_METAL, 
                           (bomb_rect.x, bomb_rect.y + bomb_rect.height//2 - 2, bomb_rect.width, 4))
            # 顶部引信（更大）
            pygame.draw.circle(screen, (255, 100, 100), 
                             (int(self.x), bomb_rect.y - 3), 5)
            # 高爆标识
            pygame.draw.circle(screen, (255, 255, 0), 
                             (int(self.x), int(self.y)), 3)

class Mine:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 8  # 缩小到原来的2/3（从12改为8）
        self.speed = 1.5  # 上浮速度
        self.active = True
        self.surface_timer = 0  # 在水面的计时器
        self.is_on_surface = False
        
    def update(self):
        if self.active:
            if not self.is_on_surface:
                # 向上浮动
                self.y -= self.speed
                if self.y <= WATER_SURFACE_HEIGHT - 10:  # 浮到驱逐舰的水平线
                    self.is_on_surface = True
                    self.y = WATER_SURFACE_HEIGHT - 10   # 与驱逐舰在同一水平
                    print(f"⚠️ Mine surfaced at position: ({self.x}, {self.y})")
            else:
                # 在水面停留，增加横向漂移
                self.surface_timer += 1
                # 水雷在水面缓慢漂移
                self.x += 0.3 * (1 if self.x < SCREEN_WIDTH // 2 else -1)  # 向屏幕中心漂移
                
                # 延长停留时间到5秒，并检查边界
                if self.surface_timer >= 300:  # 5秒后消失
                    self.active = False
                    print(f"🌊 Mine disappeared from surface")
                elif self.x < -20 or self.x > SCREEN_WIDTH + 20:
                    self.active = False
                    print(f"🌊 Mine drifted off screen")
        
        return not self.active
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, 
                          self.radius * 2, self.radius * 2)
    
    def draw(self, screen):
        if self.active:
            # 水雷主体 - 黑色球形
            pygame.draw.circle(screen, (30, 30, 30), (int(self.x), int(self.y)), self.radius)
            # 触发器 - 红色小点
            for angle in range(0, 360, 60):
                spike_x = int(self.x + (self.radius - 2) * math.cos(math.radians(angle)))
                spike_y = int(self.y + (self.radius - 2) * math.sin(math.radians(angle)))
                pygame.draw.circle(screen, (200, 0, 0), (spike_x, spike_y), 2)
            
            # 如果在水面，增加警告效果
            if self.is_on_surface:
                warning_radius = self.radius + 5 + int(math.sin(self.surface_timer * 0.3) * 3)
                pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), warning_radius, 2)

class Submarine:
    def __init__(self, sub_type='scout'):
        self.type = sub_type
        self.config = SUBMARINE_CONFIGS[sub_type]
        
        # 随机生成位置和属性
        self.width = self.config['width']
        self.height = self.config['height']
        
        # 随机深度
        depth_min, depth_max = self.config['depth_range']
        if depth_min < WATER_SURFACE_HEIGHT:
            depth_min = WATER_SURFACE_HEIGHT + 50
        if depth_max > SCREEN_HEIGHT - 50:
            depth_max = SCREEN_HEIGHT - 50
        self.y = random.randint(int(depth_min), int(depth_max))
        
        # 随机从左右进入
        self.direction = random.choice([-1, 1])  # -1从左进入，1从右进入
        if self.direction == -1:  # 从左进入，向右移动
            self.x = -self.width  # 从屏幕左侧进入
            self.speed = random.uniform(*self.config['speed_range'])  # 正速度，向右
        else:  # 从右进入，向左移动
            self.x = SCREEN_WIDTH
            self.speed = -random.uniform(*self.config['speed_range'])  # 负速度，向左
        self.active = True
        
        # 布雷潜艇特殊功能
        self.mine_cooldown = 0
        self.mines_deployed = 0
        
        # 导弹潜艇特殊功能
        self.missile_cooldown = 0
        self.missiles_fired = 0
        
    def update(self):
        if self.active:
            self.x += self.speed
            # 如果潜艇离开屏幕，标记为非活跃
            if self.x < -self.width - 50 or self.x > SCREEN_WIDTH + 50:
                self.active = False
            
            # 布雷潜艇特殊行为
            if self.config.get('special') == 'minelayer':
                self.mine_cooldown += 1
            
            # 导弹潜艇特殊行为
            if self.config.get('special') == 'missile':
                self.missile_cooldown += 1
                
    def should_deploy_mine(self):
        """检查布雷潜艇是否应该发射水雷"""
        if self.config.get('special') == 'minelayer':
            mine_cooldown_config = self.config.get('mine_cooldown', 240)
            if self.mine_cooldown >= mine_cooldown_config and self.mines_deployed < 3:  # 最多发射3枚
                self.mine_cooldown = 0
                self.mines_deployed += 1
                return True
        return False
    
    def should_fire_missile(self):
        """检查导弹潜艇是否应该发射导弹"""
        if self.config.get('special') == 'missile':
            missile_cooldown_config = self.config.get('missile_cooldown', 300)
            if self.missile_cooldown >= missile_cooldown_config and self.missiles_fired < 2:  # 最多发射2枚
                self.missile_cooldown = 0
                self.missiles_fired += 1
                return True
        return False
    
    def get_mine_launch_pos(self):
        """获取水雷发射位置"""
        return (self.x + self.width // 2, self.y)
    
    def get_missile_launch_pos(self):
        """获取导弹发射位置"""
        return (self.x + self.width // 2, self.y - 5)
    
    def get_missile_direction(self):
        """获取导弹发射方向（基于潜艇移动方向）"""
        return 1 if self.speed > 0 else -1
    
    def get_rect(self):
        # 返回潜艇的碰撞矩形
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        if self.active:
            # 绘制潜艇
            sub_rect = self.get_rect()
            
            # 潜艇绘制（可选调试信息已移除）
            
            # 主体
            pygame.draw.ellipse(screen, self.config['color'], sub_rect)
            
            # 指挥塔
            tower_width = self.width // 4
            tower_height = self.height // 2
            tower_x = self.x + self.width // 2 - tower_width // 2
            tower_y = self.y - tower_height // 2
            pygame.draw.rect(screen, self.config['dark_color'], 
                           (tower_x, tower_y, tower_width, tower_height))
            
            # 潜望镜
            if self.direction == 1:  # 向右移动
                periscope_x = tower_x + tower_width
            else:  # 向左移动
                periscope_x = tower_x
            pygame.draw.line(screen, self.config['dark_color'], 
                           (periscope_x, tower_y), 
                           (periscope_x, tower_y - 8), 2)
            
            # 螺旋桨（在潜艇后方）
            if self.speed > 0:  # 向右移动，螺旋桨在左端（后方）
                prop_x = self.x
            else:  # 向左移动，螺旋桨在右端（后方）
                prop_x = self.x + self.width
            prop_y = self.y + self.height // 2
            pygame.draw.circle(screen, self.config['dark_color'], 
                             (int(prop_x), int(prop_y)), 4)
            
            # 布雷潜艇特殊标识
            if self.config.get('special') == 'minelayer':
                # 绘制水雷发射管
                launcher_x = self.x + self.width // 2
                launcher_y = self.y - 5
                pygame.draw.rect(screen, (100, 100, 100), 
                               (launcher_x - 3, launcher_y, 6, 8))
                # 绘制"M"标识
                pygame.draw.circle(screen, (255, 255, 0), 
                                 (int(self.x + self.width // 2), int(self.y + self.height // 2)), 8, 2)
            
            # 导弹潜艇特殊标识
            if self.config.get('special') == 'missile':
                # 绘制导弹发射管（垂直）
                launcher_x = self.x + self.width // 2
                launcher_y = self.y - 8
                pygame.draw.rect(screen, (80, 80, 80), 
                               (launcher_x - 4, launcher_y, 8, 12))
                # 绘制导弹舱门
                pygame.draw.rect(screen, (120, 120, 120), 
                               (launcher_x - 5, launcher_y - 2, 10, 3))
                # 绘制"⚡"标识
                pygame.draw.polygon(screen, (255, 0, 0), [
                    (int(self.x + self.width // 2 - 6), int(self.y + self.height // 2 - 4)),
                    (int(self.x + self.width // 2 + 2), int(self.y + self.height // 2 - 4)),
                    (int(self.x + self.width // 2 - 2), int(self.y + self.height // 2)),
                    (int(self.x + self.width // 2 + 6), int(self.y + self.height // 2)),
                    (int(self.x + self.width // 2 - 2), int(self.y + self.height // 2 + 4)),
                    (int(self.x + self.width // 2 + 2), int(self.y + self.height // 2 + 4))
                ])

class Explosion:
    def __init__(self, x, y, explosion_type='normal'):
        self.x = x
        self.y = y
        self.timer = 0
        self.max_timer = EXPLOSION_DURATION
        self.explosion_type = explosion_type
        self.has_triggered_chain = False  # 防止重复触发连环爆炸
        
        # 根据爆炸类型调整大小和伤害半径
        if explosion_type == 'submarine':
            self.max_radius = 80  # 击中潜艇的爆炸更大
            self.damage_radius = SUBMARINE_EXPLOSION_RADIUS
        elif explosion_type == 'high_explosive':
            self.max_radius = 120  # 高爆炸弹爆炸更大
            self.damage_radius = HIGH_EXPLOSIVE_RADIUS
        elif explosion_type == 'bomb' or explosion_type == 'seabed':
            self.max_radius = 60  # 普通炸弹爆炸
            self.damage_radius = BOMB_EXPLOSION_RADIUS
        else:
            self.max_radius = 60  # 普通爆炸
            self.damage_radius = BOMB_EXPLOSION_RADIUS
        
    def update(self):
        self.timer += 1
        return self.timer >= self.max_timer
    
    def draw(self, screen):
        if self.timer < self.max_timer:
            # 计算爆炸效果
            progress = self.timer / self.max_timer
            radius = int(self.max_radius * math.sin(progress * math.pi))
            
            # 绘制多层爆炸效果
            if radius > 0:
                # 外层红色
                pygame.draw.circle(screen, EXPLOSION_RED, (int(self.x), int(self.y)), radius)
                # 内层橙色
                if radius > 10:
                    pygame.draw.circle(screen, EXPLOSION_ORANGE, (int(self.x), int(self.y)), radius - 10)
                # 核心黄色
                if radius > 20:
                    pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), radius - 20)

class Missile:
    def __init__(self, x, y, direction):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.direction = direction  # 1为向右，-1为向左
        self.speed = 3.0  # 导弹速度
        self.active = True
        self.phase = 1  # 1为水平飞行，2为向上飞行
        self.horizontal_distance = 0
        self.target_horizontal_distance = 120  # 水平飞行距离
        self.turn_timer = 0
        self.max_turn_timer = 15  # 转向动画持续时间
        self.angle = 0 if direction == 1 else 180  # 初始角度
        self.surface_timer = 0  # 在水面的计时器
        self.is_on_surface = False
        
    def update(self):
        if self.active:
            if self.phase == 1:  # 水平飞行阶段
                self.x += self.speed * self.direction
                self.horizontal_distance += self.speed
                
                if self.horizontal_distance >= self.target_horizontal_distance:
                    self.phase = 2  # 转向阶段
                    print(f"🚀 Missile turning upward at ({self.x}, {self.y})")
                    
            elif self.phase == 2:  # 转向阶段
                # 平滑转向动画
                self.turn_timer += 1
                progress = min(self.turn_timer / self.max_turn_timer, 1.0)
                
                if self.direction == 1:  # 向右发射的导弹
                    self.angle = progress * -90  # 从0度转到-90度（向上）
                else:  # 向左发射的导弹
                    self.angle = 180 + progress * -90  # 从180度转到90度（向上）
                
                if progress >= 1.0:
                    self.phase = 3  # 垂直向上飞行
                    
            elif self.phase == 3:  # 垂直向上飞行阶段
                self.y -= self.speed
                
                # 检查是否冲出水面，在驱逐舰高度停留
                if self.y <= WATER_SURFACE_HEIGHT - 10 and not self.is_on_surface:
                    self.is_on_surface = True
                    print(f"🚀 Missile surfaced at position: ({self.x}, {self.y})")
                
                # 导弹继续向上飞行直到完全离开屏幕
                if self.y < -50:
                    self.active = False
                    print(f"💨 Missile disappeared into sky")
        
        return not self.active
    
    def get_rect(self):
        # 导弹的碰撞体积应该与绘制一致，窄长形状
        missile_length = 16
        missile_width = 6
        return pygame.Rect(self.x - missile_length//2, self.y - missile_width//2, 
                          missile_length, missile_width)
    
    def draw(self, screen):
        if self.active:
            # 根据角度计算导弹的绘制方向
            missile_length = 16
            missile_width = 6
            
            # 计算导弹头部和尾部位置
            angle_rad = math.radians(self.angle)
            dx = math.cos(angle_rad) * missile_length // 2
            dy = math.sin(angle_rad) * missile_length // 2
            
            head_x = int(self.x + dx)
            head_y = int(self.y + dy)
            tail_x = int(self.x - dx)
            tail_y = int(self.y - dy)
            
            # 绘制导弹主体
            pygame.draw.line(screen, (100, 100, 100), (tail_x, tail_y), (head_x, head_y), missile_width)
            
            # 绘制导弹头部（红色）
            pygame.draw.circle(screen, (200, 50, 50), (head_x, head_y), 4)
            
            # 绘制导弹尾部推进器（橙色）
            if self.phase >= 2:  # 转向后才显示推进器火焰
                flame_x = int(self.x - dx * 1.5)
                flame_y = int(self.y - dy * 1.5)
                pygame.draw.circle(screen, (255, 165, 0), (flame_x, flame_y), 3)
            
            # 导弹到达水面时去除圆形范围框，不绘制警告效果

class SubmarineHunterGame:
    def __init__(self):
        # 根据调试模式调整窗口宽度
        window_width = SCREEN_WIDTH + DEBUG_PANEL_WIDTH if True else SCREEN_WIDTH
        self.screen = pygame.display.set_mode((window_width, SCREEN_HEIGHT))
        pygame.display.set_caption("Submarine Hunter - 猎杀潜艇")
        self.clock = pygame.time.Clock()
        
        # 游戏对象 - 驱逐舰初始位置在游戏区域中央
        ship_start_x = SCREEN_WIDTH // 2 - 30
        self.ship = Ship(ship_start_x, WATER_SURFACE_HEIGHT - 25)
        self.bombs = []
        self.explosions = []
        self.submarines = []
        self.mines = []  # 水雷列表
        self.missiles = []  # 导弹列表
        
        # 游戏状态
        self.running = True
        self.bombs_fired = 0
        self.score = 0
        self.submarines_destroyed = 0
        self.debug_timer = 0  # 调试计时器
        
        # 高爆炸弹系统
        self.high_explosives = MAX_HIGH_EXPLOSIVES  # 开始时有满载高爆炸弹
        self.high_explosive_cooldown = 0            # 冷却计时器
        self.high_explosives_fired = 0              # 发射的高爆炸弹数量
        
        # 调试系统
        self.debug_mode = True  # 显示调试面板
        self.god_mode = False   # 无敌模式，默认关闭
        self.spawn_rates = {    # 可调整的生成概率
            'scout': 0.006,
            'minelayer': 0.003,
            'missile': 0.002
        }
        
        # 性能优化 - 减少调试输出
        self.verbose_logging = False  # 关闭详细调试输出
        
        # 游戏正式开始，潜艇将随机生成
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.fire_bomb()
                elif event.key == pygame.K_s:
                    self.fire_high_explosive()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                # 调试功能按键
                elif event.key == pygame.K_d:
                    self.debug_mode = not self.debug_mode
                elif event.key == pygame.K_g:
                    self.god_mode = not self.god_mode
                    print(f"🛡️ God mode: {'ON' if self.god_mode else 'OFF'}")
                # 潜艇生成概率调整
                elif event.key == pygame.K_1:
                    self.spawn_rates['scout'] = min(0.02, self.spawn_rates['scout'] + 0.001)
                    print(f"🔺 Scout spawn rate: {self.spawn_rates['scout']:.3f}")
                elif event.key == pygame.K_2:
                    self.spawn_rates['scout'] = max(0.001, self.spawn_rates['scout'] - 0.001)
                    print(f"🔻 Scout spawn rate: {self.spawn_rates['scout']:.3f}")
                elif event.key == pygame.K_3:
                    self.spawn_rates['minelayer'] = min(0.01, self.spawn_rates['minelayer'] + 0.001)
                    print(f"🔺 Minelayer spawn rate: {self.spawn_rates['minelayer']:.3f}")
                elif event.key == pygame.K_4:
                    self.spawn_rates['minelayer'] = max(0.001, self.spawn_rates['minelayer'] - 0.001)
                    print(f"🔻 Minelayer spawn rate: {self.spawn_rates['minelayer']:.3f}")
                elif event.key == pygame.K_5:
                    self.spawn_rates['missile'] = min(0.01, self.spawn_rates['missile'] + 0.001)
                    print(f"🔺 Missile sub spawn rate: {self.spawn_rates['missile']:.3f}")
                elif event.key == pygame.K_6:
                    self.spawn_rates['missile'] = max(0.001, self.spawn_rates['missile'] - 0.001)
                    print(f"🔻 Missile sub spawn rate: {self.spawn_rates['missile']:.3f}")
        
        # 持续按键检测
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.ship.move_left()
        if keys[pygame.K_RIGHT]:
            self.ship.move_right()
    
    def fire_bomb(self):
        # 从驱逐舰发射炸弹
        bomb_x, bomb_y = self.ship.get_bomb_start_pos()
        self.bombs.append(Bomb(bomb_x, bomb_y))
        self.bombs_fired += 1
        if self.verbose_logging:
            print(f"💣 Bomb fired! #{self.bombs_fired} at position: ({bomb_x}, {bomb_y})")
    
    def fire_high_explosive(self):
        # 发射高爆炸弹
        if self.high_explosives > 0:
            bomb_x, bomb_y = self.ship.get_bomb_start_pos()
            self.bombs.append(HighExplosiveBomb(bomb_x, bomb_y))
            self.high_explosives -= 1
            self.high_explosives_fired += 1
            if self.verbose_logging:
                print(f"💥 HIGH EXPLOSIVE fired! Stock: {self.high_explosives} remaining at position: ({bomb_x}, {bomb_y})")
        else:
            if self.verbose_logging:
                print("⚠️ No high explosives available! Wait for reload...")
    
    def spawn_submarines(self):
        # 随机生成潜艇 - 减少调试输出
        for sub_type, config in SUBMARINE_CONFIGS.items():
            spawn_chance = self.spawn_rates.get(sub_type, config['spawn_chance'])
            if random.random() < spawn_chance:
                new_sub = Submarine(sub_type)
                self.submarines.append(new_sub)
                if self.verbose_logging:
                    print(f"✅ New {config['name']} spawned at depth: {new_sub.y:.1f}")
    
    def chain_explosion(self, explosion_x, explosion_y, explosion_radius, explosion_type='chain'):
        """处理连环爆炸逻辑"""
        chain_count = 0
        submarines_hit = []
        
        # 检查爆炸范围内的潜艇
        for submarine in self.submarines[:]:  # 使用切片避免修改列表时的问题
            if submarine.active:
                sub_center_x = submarine.x + submarine.width // 2
                sub_center_y = submarine.y + submarine.height // 2
                distance = math.sqrt((sub_center_x - explosion_x)**2 + (sub_center_y - explosion_y)**2)
                
                if distance <= explosion_radius:
                    # 潜艇被炸毁
                    submarine.active = False
                    self.score += submarine.config['score']
                    self.submarines_destroyed += 1
                    submarines_hit.append(submarine)
                    
                    # 创建潜艇爆炸
                    self.explosions.append(Explosion(sub_center_x, sub_center_y, 'submarine'))
                    chain_count += 1
        
        # 输出连环爆炸信息（减少冗余输出）
        if chain_count > 0:
            if explosion_type == 'seabed':
                if chain_count == 1:
                    print(f"💥 Chain explosion! {submarines_hit[0].config['name']} destroyed! +{submarines_hit[0].config['score']} points")
                else:
                    print(f"🌟 MASSIVE seabed chain reaction! {chain_count} submarines destroyed!")
            elif explosion_type == 'high_explosive':
                print(f"🌟 MASSIVE chain explosion! {chain_count} submarines destroyed!")
            else:
                print(f"💥 Chain explosion! {submarines_hit[0].config['name']} destroyed! +{submarines_hit[0].config['score']} points")
            
            if chain_count > 1:
                print(f"🔗 Chain explosion triggered! {chain_count - 1} additional submarines destroyed!")
        
        # 触发连锁反应
        for submarine in submarines_hit:
            sub_center_x = submarine.x + submarine.width // 2
            sub_center_y = submarine.y + submarine.height // 2
            self.chain_explosion(sub_center_x, sub_center_y, SUBMARINE_EXPLOSION_RADIUS, 'chain')
        
        return chain_count
    
    def check_collisions(self):
        # 检查水雷与驱逐舰的碰撞（仅在水面时）
        for mine in self.mines[:]:
            if mine.active and mine.is_on_surface:
                mine_rect = mine.get_rect()
                ship_rect = self.ship.get_rect()
                
                # 添加调试信息
                if self.verbose_logging:
                    distance = math.sqrt((mine.x - self.ship.x)**2 + (mine.y - self.ship.y)**2)
                    print(f"💣 Mine check: mine({mine.x:.1f}, {mine.y:.1f}) ship({self.ship.x:.1f}, {self.ship.y:.1f}) distance: {distance:.1f}")
                
                if mine_rect.colliderect(ship_rect):
                    # 水雷击中驱逐舰
                    if self.ship.take_damage(self.god_mode):
                        print(f"💥 Mine hit ship! Lives: {self.ship.lives}")
                        # 创建爆炸效果
                        self.explosions.append(Explosion(mine.x, mine.y, 'bomb'))
                        mine.active = False
                        self.mines.remove(mine)
                        
                        # 检查游戏结束
                        if self.ship.lives <= 0:
                            print("💀 Game Over! Ship destroyed!")
                            self.running = False
                            return
        
        # 检查导弹与驱逐舰的碰撞（仅在水面时）
        for missile in self.missiles[:]:
            if missile.active and missile.is_on_surface:
                missile_rect = missile.get_rect()
                ship_rect = self.ship.get_rect()
                if missile_rect.colliderect(ship_rect):
                    # 导弹击中驱逐舰
                    if self.ship.take_damage(self.god_mode):
                        print(f"🚀 Missile hit ship! Lives: {self.ship.lives}")
                        # 创建爆炸效果
                        self.explosions.append(Explosion(missile.x, missile.y, 'bomb'))
                        missile.active = False
                        self.missiles.remove(missile)
                        
                        # 检查游戏结束
                        if self.ship.lives <= 0:
                            print("💀 Game Over! Ship destroyed by missile!")
                            self.running = False
                            return
        
        # 检查炸弹与导弹的碰撞
        for bomb in self.bombs[:]:
            if not bomb.active:
                continue
            
            bomb_rect = bomb.get_rect()
            for missile in self.missiles[:]:
                if missile.active:
                    missile_rect = missile.get_rect()
                    if bomb_rect.colliderect(missile_rect):
                        # 炸弹击中导弹，提前引爆
                        explosion_x = (bomb.x + missile.x) // 2
                        explosion_y = (bomb.y + missile.y) // 2
                        
                        # 判断是否为高爆炸弹
                        is_high_explosive = isinstance(bomb, HighExplosiveBomb)
                        explosion_type = 'high_explosive' if is_high_explosive else 'bomb'
                        explosion_radius = HIGH_EXPLOSIVE_RADIUS if is_high_explosive else BOMB_EXPLOSION_RADIUS
                        
                        # 创建爆炸效果
                        self.explosions.append(Explosion(explosion_x, explosion_y, explosion_type))
                        
                        # 移除炸弹和导弹
                        bomb.active = False
                        missile.active = False
                        self.bombs.remove(bomb)
                        self.missiles.remove(missile)
                        
                        print(f"💥 Bomb intercepted missile at ({explosion_x}, {explosion_y})")
                        
                        # 触发连环爆炸
                        chain_count = self.chain_explosion(explosion_x, explosion_y, explosion_radius)
                        if chain_count > 0:
                            print(f"🔗 Chain explosion triggered! {chain_count} submarines destroyed!")
                        break
        
        # 检查炸弹与水雷的碰撞
        for bomb in self.bombs[:]:
            if not bomb.active:
                continue
            
            bomb_rect = bomb.get_rect()
            for mine in self.mines[:]:
                if mine.active:
                    mine_rect = mine.get_rect()
                    if bomb_rect.colliderect(mine_rect):
                        # 炸弹击中水雷，提前引爆
                        explosion_x = (bomb.x + mine.x) // 2
                        explosion_y = (bomb.y + mine.y) // 2
                        
                        # 判断是否为高爆炸弹
                        is_high_explosive = isinstance(bomb, HighExplosiveBomb)
                        explosion_type = 'high_explosive' if is_high_explosive else 'bomb'
                        explosion_radius = HIGH_EXPLOSIVE_RADIUS if is_high_explosive else BOMB_EXPLOSION_RADIUS
                        
                        # 创建爆炸效果
                        self.explosions.append(Explosion(explosion_x, explosion_y, explosion_type))
                        
                        # 移除炸弹和水雷
                        bomb.active = False
                        mine.active = False
                        self.bombs.remove(bomb)
                        self.mines.remove(mine)
                        
                        print(f"💥 Bomb destroyed mine at ({explosion_x}, {explosion_y})")
                        
                        # 触发连环爆炸
                        chain_count = self.chain_explosion(explosion_x, explosion_y, explosion_radius)
                        if chain_count > 0:
                            print(f"🔗 Chain explosion triggered! {chain_count} submarines destroyed!")
                        break
        
        # 检查炸弹与潜艇的碰撞
        for bomb in self.bombs[:]:
            if not bomb.active:
                continue
                
            bomb_rect = bomb.get_rect()
            for submarine in self.submarines[:]:
                if not submarine.active:
                    continue
                    
                sub_rect = submarine.get_rect()
                if bomb_rect.colliderect(sub_rect):
                    # 碰撞！炸弹和潜艇都爆炸
                    explosion_x = (bomb.x + submarine.x + submarine.width // 2) // 2
                    explosion_y = (bomb.y + submarine.y + submarine.height // 2) // 2
                    
                    # 判断是否为高爆炸弹
                    is_high_explosive = isinstance(bomb, HighExplosiveBomb)
                    explosion_type = 'high_explosive' if is_high_explosive else 'bomb'
                    explosion_radius = HIGH_EXPLOSIVE_RADIUS if is_high_explosive else BOMB_EXPLOSION_RADIUS
                    
                    # 创建爆炸效果
                    self.explosions.append(Explosion(explosion_x, explosion_y, explosion_type))
                    
                    # 增加得分
                    points = submarine.config['score']
                    self.score += points
                    self.submarines_destroyed += 1
                    
                    # 移除炸弹和潜艇
                    bomb.active = False
                    submarine.active = False
                    self.bombs.remove(bomb)
                    self.submarines.remove(submarine)
                    
                    hit_message = "🔥 HIGH EXPLOSIVE HIT!" if is_high_explosive else "🎯 Direct hit!"
                    print(f"{hit_message} {submarine.config['name']} destroyed! +{points} points")
                    
                    # 立即触发连环爆炸
                    chain_count = self.chain_explosion(explosion_x, explosion_y, explosion_radius)
                    if chain_count > 0:
                        chain_message = f"🌟 MASSIVE chain explosion! {chain_count} submarines destroyed!" if is_high_explosive else f"🔗 Chain explosion triggered! {chain_count} additional submarines destroyed!"
                        print(chain_message)
                    
                    break
    
    def update(self):
        # 更新游戏对象
        self.ship.update()
        
        # 更新高爆炸弹冷却
        if self.high_explosive_cooldown > 0:
            self.high_explosive_cooldown -= 1
        elif self.high_explosives < MAX_HIGH_EXPLOSIVES:
            self.high_explosives += 1
            self.high_explosive_cooldown = HIGH_EXPLOSIVE_COOLDOWN
            if self.verbose_logging:
                print(f"🔋 High explosive reloaded! Stock: {self.high_explosives}/{MAX_HIGH_EXPLOSIVES}")
        
        # 生成新潜艇
        self.spawn_submarines()
        
        # 更新炸弹
        bombs_to_remove = []
        for i, bomb in enumerate(self.bombs):
            result = bomb.update()
            if result == 'seabed':
                # 海底爆炸
                explosion_type = 'high_explosive' if isinstance(bomb, HighExplosiveBomb) else 'normal'
                explosion_radius = HIGH_EXPLOSIVE_RADIUS if isinstance(bomb, HighExplosiveBomb) else BOMB_EXPLOSION_RADIUS
                self.explosions.append(Explosion(bomb.x, bomb.y, explosion_type))
                self.chain_explosion(bomb.x, bomb.y, explosion_radius, 'seabed')
                bombs_to_remove.append(i)
                if self.verbose_logging:
                    explosion_name = "HIGH EXPLOSIVE" if isinstance(bomb, HighExplosiveBomb) else "Bomb"
                    print(f"💣 {explosion_name} detonated on seabed! at: ({bomb.x}, {bomb.y})")
            elif not bomb.active:
                bombs_to_remove.append(i)
        
        # 性能优化：批量移除炸弹
        for i in reversed(bombs_to_remove):
            self.bombs.pop(i)
        
        # 更新潜艇
        submarines_to_remove = []
        for i, submarine in enumerate(self.submarines):
            submarine.update()
            if not submarine.active:
                submarines_to_remove.append(i)
                if self.verbose_logging:
                    print(f"🚫 Submarine removed (left screen): {submarine.config['name']}")
            else:
                # 布雷潜艇部署水雷
                if submarine.should_deploy_mine():
                    mine_x, mine_y = submarine.get_mine_launch_pos()
                    self.mines.append(Mine(mine_x, mine_y))
                    if self.verbose_logging:
                        print(f"💣 Minelayer deployed mine at ({mine_x}, {mine_y})")
                
                # 导弹潜艇发射导弹
                if submarine.should_fire_missile():
                    missile_x, missile_y = submarine.get_missile_launch_pos()
                    missile_direction = submarine.get_missile_direction()
                    self.missiles.append(Missile(missile_x, missile_y, missile_direction))
                    if self.verbose_logging:
                        print(f"🚀 Missile submarine fired at ({missile_x}, {missile_y}) direction: {missile_direction}")
        
        # 性能优化：批量移除潜艇
        for i in reversed(submarines_to_remove):
            self.submarines.pop(i)
        
        # 更新水雷
        mines_to_remove = []
        for i, mine in enumerate(self.mines):
            if mine.update():
                mines_to_remove.append(i)
        
        # 性能优化：批量移除水雷
        for i in reversed(mines_to_remove):
            self.mines.pop(i)
        
        # 更新导弹
        missiles_to_remove = []
        for i, missile in enumerate(self.missiles):
            if missile.update():
                missiles_to_remove.append(i)
        
        # 性能优化：批量移除导弹
        for i in reversed(missiles_to_remove):
            self.missiles.pop(i)
        
        # 更新爆炸效果
        explosions_to_remove = []
        for i, explosion in enumerate(self.explosions):
            if explosion.update():  # update()返回True表示爆炸结束
                explosions_to_remove.append(i)
        
        # 性能优化：批量移除爆炸效果
        for i in reversed(explosions_to_remove):
            self.explosions.pop(i)
        
        # 碰撞检测
        self.check_collisions()
        
        # 检查游戏结束
        if self.ship.lives <= 0:
            self.running = False
    
    def draw_background(self):
        # 绘制天空背景
        self.screen.fill(SKY_BLUE)
        
        # 如果调试模式开启，在右侧绘制调试面板背景
        if self.debug_mode:
            debug_panel_x = SCREEN_WIDTH
            pygame.draw.rect(self.screen, (40, 40, 40), 
                           (debug_panel_x, 0, DEBUG_PANEL_WIDTH, SCREEN_HEIGHT))
            # 绘制分隔线
            pygame.draw.line(self.screen, (100, 100, 100), 
                           (debug_panel_x, 0), (debug_panel_x, SCREEN_HEIGHT), 2)
        
        # 绘制水面线
        pygame.draw.line(self.screen, WATER_BLUE, (0, WATER_SURFACE_HEIGHT), 
                        (SCREEN_WIDTH, WATER_SURFACE_HEIGHT), 3)
        
        # 绘制水下区域
        pygame.draw.rect(self.screen, DARK_BLUE, 
                        (0, WATER_SURFACE_HEIGHT, SCREEN_WIDTH, UNDERWATER_HEIGHT))
        
        # 绘制海底
        pygame.draw.rect(self.screen, SEA_FLOOR, 
                        (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))
        
        # 绘制一些水波效果
        for i in range(0, SCREEN_WIDTH, 20):
            pygame.draw.arc(self.screen, WATER_BLUE, 
                          (i, WATER_SURFACE_HEIGHT - 5, 20, 10), 0, math.pi, 2)
    
    def draw_debug_panel(self):
        if not self.debug_mode:
            return
            
        font = pygame.font.Font(None, 24)
        font_small = pygame.font.Font(None, 18)
        debug_x = SCREEN_WIDTH + 10  # 调试面板位置
        y_offset = 10
        
        # 标题
        title = font.render("DEBUG PANEL", True, (255, 255, 255))
        self.screen.blit(title, (debug_x, y_offset))
        y_offset += 30
        
        # 无敌模式状态
        god_status = "ON" if self.god_mode else "OFF"
        god_color = (255, 100, 100) if self.god_mode else (100, 255, 100)
        god_text = font_small.render(f"God Mode: {god_status}", True, god_color)
        self.screen.blit(god_text, (debug_x, y_offset))
        y_offset += 25
        
        # 潜艇生成概率
        spawn_title = font_small.render("Spawn Rates:", True, (255, 255, 100))
        self.screen.blit(spawn_title, (debug_x, y_offset))
        y_offset += 20
        
        for sub_type, rate in self.spawn_rates.items():
            rate_text = font_small.render(f"{sub_type}: {rate:.3f}", True, (200, 200, 200))
            self.screen.blit(rate_text, (debug_x + 5, y_offset))
            y_offset += 18
        
        y_offset += 10
        
        # 控制说明
        controls = [
            "CONTROLS:",
            "D - Toggle Panel",
            "G - God Mode",
            "",
            "Scout Submarine:",
            "1 - Increase Rate",
            "2 - Decrease Rate",
            "",
            "Minelayer:",
            "3 - Increase Rate", 
            "4 - Decrease Rate",
            "",
            "Missile Sub:",
            "5 - Increase Rate",
            "6 - Decrease Rate"
        ]
        
        for control in controls:
            if control == "CONTROLS:":
                color = (255, 255, 100)
            elif control.endswith("Submarine:") or control.endswith("Minelayer:") or control.endswith("Sub:"):
                color = (100, 255, 100)
            elif control == "":
                y_offset += 8
                continue
            else:
                color = (180, 180, 180)
            
            control_text = font_small.render(control, True, color)
            self.screen.blit(control_text, (debug_x, y_offset))
            y_offset += 16
    
    def draw_ui(self):
        # 在天空区域绘制游戏信息
        font = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)
        
        # 左上角 - 生命值和得分
        lives_color = (255, 100, 100) if self.ship.lives <= 1 else (100, 255, 100)
        lives_text = font.render(f"Lives: {self.ship.lives}", True, lives_color)
        self.screen.blit(lives_text, (10, 10))
        
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 45))
        
        # 中上 - 弹药信息
        center_x = SCREEN_WIDTH // 2
        bombs_text = font_small.render(f"Bombs Fired: {self.bombs_fired}", True, WHITE)
        self.screen.blit(bombs_text, (center_x - 100, 10))
        
        he_text = font_small.render(f"High Explosives: {self.high_explosives}", True, WHITE)
        self.screen.blit(he_text, (center_x - 100, 35))
        
        subs_text = font_small.render(f"Submarines: {self.submarines_destroyed}", True, WHITE)
        self.screen.blit(subs_text, (center_x - 100, 60))
        
        # 右上角 - 威胁信息
        threat_x = SCREEN_WIDTH - 200
        if len(self.mines) > 0:
            mines_text = font_small.render(f"⚠️ Mines: {len(self.mines)}", True, (255, 255, 100))
            self.screen.blit(mines_text, (threat_x, 10))
        
        if len(self.missiles) > 0:
            missiles_text = font_small.render(f"🚀 Missiles: {len(self.missiles)}", True, (255, 100, 100))
            y_pos = 35 if len(self.mines) > 0 else 10
            self.screen.blit(missiles_text, (threat_x, y_pos))
        
        # 控制说明在天空底部
        control_y = SKY_HEIGHT - 45
        controls = ["← → Move | A Bomb | S High Explosive | ESC Exit"]
        for control in controls:
            text = font_small.render(control, True, (200, 200, 255))
            text_rect = text.get_rect()
            self.screen.blit(text, (SCREEN_WIDTH//2 - text_rect.width//2, control_y))
    
    def draw(self):
        self.draw_background()
        
        # 绘制游戏对象
        self.ship.draw(self.screen)
        
        for submarine in self.submarines:
            submarine.draw(self.screen)
        
        for bomb in self.bombs:
            bomb.draw(self.screen)
        
        for mine in self.mines:
            mine.draw(self.screen)
        
        for missile in self.missiles:
            missile.draw(self.screen)
        
        for explosion in self.explosions:
            explosion.draw(self.screen)
        
        self.draw_debug_panel()
        self.draw_ui()
        
        pygame.display.flip()
    
    def run(self):
        print("=== Submarine Hunter Game Started ===")
        print("Controls:")
        print("- Left/Right Arrow Keys: Move Destroyer")
        print("- A Key: Drop Depth Charge")
        print("- S Key: High Explosive Bomb")
        print("- D Key: Toggle Debug Panel")
        print("- G Key: God Mode")
        print("- ESC Key: Exit Game")
        print("=====================================")
        
        frame_count = 0
        while self.running:
            frame_count += 1
            
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
            # 性能监控 - 每5秒输出一次统计信息
            if frame_count % (FPS * 5) == 0 and self.verbose_logging:
                print(f"📊 Performance: {len(self.submarines)} subs, {len(self.bombs)} bombs, {len(self.explosions)} explosions")
        
        print(f"\n🎮 Game Over! Final Score: {self.score}")
        print(f"🎯 Submarines Destroyed: {self.submarines_destroyed}")
        print(f"💣 Bombs Fired: {self.bombs_fired}")
        print(f"💥 High Explosives Used: {self.high_explosives_fired}")
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SubmarineHunterGame()
    game.run() 