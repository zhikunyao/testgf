import pygame
import random
import logging
import sys
from enum import Enum
from typing import List, Tuple, Set
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('match_three_game.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GameState(Enum):
    PLAYING = 1
    FALLING = 2
    GAME_OVER = 3

class Color(Enum):
    RED = (180, 60, 60)        # 柔和的红色
    GREEN = (60, 180, 60)      # 柔和的绿色
    BLUE = (60, 60, 180)       # 柔和的蓝色
    ORANGE = (255, 165, 80)    # 柔和的橙色 (替换原黄色)
    PINK = (255, 182, 193)     # 柔和的粉色 (替换原紫色)
    GOLD = (255, 215, 0)       # 黄金色块 - 特殊奖励色块
    DIAMOND = (185, 242, 255)  # 钻石色块 - 超级奖励色块（冰蓝钻石色）
    COLORFUL = (255, 128, 255) # 彩色万能色块 - 可与任何色块消除（粉紫色基调）
    PEARL = (248, 248, 255)    # 珍珠色块 - 终极奖励色块（珍珠白）
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)

class MatchThreeGame:
    def __init__(self):
        pygame.init()
        
        # 游戏配置
        self.GRID_SIZE = 10
        self.CELL_SIZE = 60
        self.GRID_MARGIN = 5
        self.COLORS = [Color.RED, Color.GREEN, Color.BLUE, Color.ORANGE, Color.PINK]
        
        # 窗口设置
        self.WINDOW_WIDTH = self.GRID_SIZE * (self.CELL_SIZE + self.GRID_MARGIN) + self.GRID_MARGIN
        self.SCORE_HEIGHT = 80  # 上方计分区域高度
        self.TOOL_HEIGHT = 100  # 下方道具区域高度
        self.WINDOW_HEIGHT = self.WINDOW_WIDTH + self.SCORE_HEIGHT + self.TOOL_HEIGHT
        
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("三消游戏")
        
        # 游戏状态
        self.state = GameState.PLAYING
        self.grid = [[None for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]
        self.selected_cells = set()
        self.score = 0
        self.eliminated_count = 0
        
        # 动画相关
        self.falling_cells = []
        self.elimination_effects = []
        self.fall_speed = 2
        
        # 黄金色块闪光动画
        self.gold_animation_timer = 0
        self.gold_glow_intensity = 0
        
        # 钻石色块闪光动画
        self.diamond_animation_timer = 0
        self.diamond_glow_intensity = 0
        
        # 彩色色块闪光动画
        self.colorful_animation_timer = 0
        self.colorful_glow_intensity = 0
        
        # 珍珠色块闪光动画
        self.pearl_animation_timer = 0
        self.pearl_glow_intensity = 0
        
        # 道具系统
        self.hammer_count = 3  # 锤子道具数量
        self.is_hammer_mode = False  # 是否处于锤子使用模式
        self.hammer_cursor = None  # 锤子鼠标指针
        
        # 字体设置 - 尝试使用系统中文字体
        try:
            # 尝试使用系统中文字体
            self.font = pygame.font.Font("/System/Library/Fonts/Arial Unicode MS.ttf", 28)
        except:
            try:
                # 备选字体
                self.font = pygame.font.Font("/System/Library/Fonts/Helvetica.ttc", 28)
            except:
                # 最后使用默认字体
                self.font = pygame.font.Font(None, 36)
        
        # 初始化游戏网格
        self.generate_grid()
        
        # 设置自定义鼠标指针
        self.create_finger_cursor()
        self.create_hammer_cursor()
        
        logger.info("游戏初始化完成")
    
    def create_finger_cursor(self):
        """创建自定义大尺寸鼠标指针"""
        # 创建一个比普通鼠标稍大的指针图案 (28x36像素)
        cursor_size = (28, 36)
        cursor_surface = pygame.Surface(cursor_size, pygame.SRCALPHA)
        
        # 定义颜色
        white = (255, 255, 255)
        black = (0, 0, 0)
        gray = (128, 128, 128)
        
        # 定义箭头指针的坐标点 (放大版本)
        arrow_points = [
            (2, 2),   # 箭头顶点
            (2, 26),  # 左侧底部
            (8, 20),  # 左侧缺口
            (14, 26), # 中心底部
            (20, 20), # 右侧缺口
            (14, 14), # 右侧中间
            (20, 8),  # 右侧顶部
            (2, 2)    # 回到起点
        ]
        
        # 绘制黑色阴影 (偏移1像素)
        shadow_points = [(x+1, y+1) for x, y in arrow_points]
        pygame.draw.polygon(cursor_surface, black, shadow_points)
        
        # 绘制灰色边框
        pygame.draw.polygon(cursor_surface, gray, arrow_points, 2)
        
        # 绘制白色主体
        pygame.draw.polygon(cursor_surface, white, arrow_points)
        
        # 添加细节高光
        highlight_points = [
            (4, 4),   # 高光顶点
            (4, 22),  # 高光左侧
            (7, 18),  # 高光缺口
            (12, 22), # 高光中心
            (16, 18), # 高光右侧
            (12, 12), # 高光中间
            (16, 8),  # 高光右上
            (4, 4)    # 回到起点
        ]
        pygame.draw.polygon(cursor_surface, (245, 245, 245), highlight_points)
        
        # 绘制黑色轮廓
        pygame.draw.polygon(cursor_surface, black, arrow_points, 1)
        
        # 转换为pygame鼠标指针格式
        # 热点位置设置在箭头顶点
        hotspot = (2, 2)  
        
        # 创建鼠标掩码
        mask = pygame.mask.from_surface(cursor_surface)
        cursor_data = pygame.cursors.Cursor(hotspot, cursor_surface)
        
        # 设置自定义鼠标指针
        pygame.mouse.set_cursor(cursor_data)
        
        logger.info("已设置自定义大尺寸鼠标指针")
    
    def create_hammer_cursor(self):
        """创建锤子鼠标指针"""
        # 创建锤子图案 (32x32像素)
        cursor_size = (32, 32)
        hammer_surface = pygame.Surface(cursor_size, pygame.SRCALPHA)
        
        # 定义颜色
        brown = (139, 69, 19)      # 锤柄棕色
        dark_brown = (101, 50, 14) # 锤柄阴影
        silver = (192, 192, 192)   # 锤头银色
        dark_silver = (128, 128, 128) # 锤头阴影
        
        # 绘制锤柄 (竖直的矩形)
        handle_rect = pygame.Rect(13, 16, 6, 14)  # 竖直的柄，连接锤头底部
        pygame.draw.rect(hammer_surface, brown, handle_rect)
        pygame.draw.rect(hammer_surface, dark_brown, handle_rect, 1)
        
        # 绘制锤头主体
        hammer_head = pygame.Rect(8, 6, 16, 10)
        pygame.draw.rect(hammer_surface, silver, hammer_head)
        pygame.draw.rect(hammer_surface, dark_silver, hammer_head, 2)
        
        # 绘制锤头细节
        # 锤头顶部高光
        top_highlight = pygame.Rect(10, 7, 12, 2)
        pygame.draw.rect(hammer_surface, (220, 220, 220), top_highlight)
        
        # 锤头侧面阴影
        side_shadow = pygame.Rect(22, 8, 2, 6)
        pygame.draw.rect(hammer_surface, (100, 100, 100), side_shadow)
        
        # 保存锤子指针数据
        hotspot = (8, 6)  # 热点位置设置在锤头左上角
        self.hammer_cursor = pygame.cursors.Cursor(hotspot, hammer_surface)
        
        logger.info("已创建锤子鼠标指针")
    
    def generate_grid(self):
        """生成随机的10x10色块网格"""
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                self.grid[row][col] = random.choice(self.COLORS)
        logger.info("生成了新的游戏网格")
    
    def get_cell_at_pos(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """根据鼠标位置获取网格坐标"""
        x, y = pos
        # 网格开始位置需要考虑上方计分区域
        grid_start_y = self.SCORE_HEIGHT
        
        if x < self.GRID_MARGIN or y < grid_start_y + self.GRID_MARGIN:
            return None, None
        
        col = (x - self.GRID_MARGIN) // (self.CELL_SIZE + self.GRID_MARGIN)
        row = (y - grid_start_y - self.GRID_MARGIN) // (self.CELL_SIZE + self.GRID_MARGIN)
        
        if 0 <= row < self.GRID_SIZE and 0 <= col < self.GRID_SIZE:
            return row, col
        return None, None
    
    def get_cell_rect(self, row: int, col: int) -> pygame.Rect:
        """获取网格单元的矩形区域"""
        x = col * (self.CELL_SIZE + self.GRID_MARGIN) + self.GRID_MARGIN
        y = row * (self.CELL_SIZE + self.GRID_MARGIN) + self.GRID_MARGIN + self.SCORE_HEIGHT
        return pygame.Rect(x, y, self.CELL_SIZE, self.CELL_SIZE)
    
    def find_connected_cells(self, start_row: int, start_col: int) -> Set[Tuple[int, int]]:
        """找到与起始位置连接的同色块（彩色色块有特殊处理）"""
        if self.grid[start_row][start_col] is None:
            return set()
        
        start_color = self.grid[start_row][start_col]
        connected = set()
        to_check = [(start_row, start_col)]
        
        # 如果起始是彩色色块，使用特殊逻辑
        if start_color == Color.COLORFUL:
            return self.find_colorful_connected_cells(start_row, start_col)
        
        while to_check:
            row, col = to_check.pop()
            if (row, col) in connected:
                continue
            
            if (0 <= row < self.GRID_SIZE and 0 <= col < self.GRID_SIZE and 
                self.grid[row][col] is not None):
                
                current_color = self.grid[row][col]
                
                # 普通色块连接逻辑：相同颜色或包含彩色色块
                can_connect = (
                    current_color == start_color or  # 相同颜色
                    current_color == Color.COLORFUL   # 当前是彩色色块
                )
                
                if can_connect:
                    connected.add((row, col))
                    
                    # 检查四个方向
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        new_row, new_col = row + dr, col + dc
                        if (new_row, new_col) not in connected:
                            to_check.append((new_row, new_col))
        
        return connected
    
    def find_colorful_connected_cells(self, start_row: int, start_col: int) -> Set[Tuple[int, int]]:
        """找到彩色色块的连接组合（只连接直接相邻的同色块）"""
        connected = {(start_row, start_col)}  # 包含彩色色块本身
        
        # 检查四个方向的直接相邻色块
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_row, new_col = start_row + dr, start_col + dc
            if (0 <= new_row < self.GRID_SIZE and 0 <= new_col < self.GRID_SIZE and 
                self.grid[new_row][new_col] is not None):
                
                adjacent_color = self.grid[new_row][new_col]
                
                # 收集相邻的同色块组
                same_color_group = self.find_same_color_group(new_row, new_col, adjacent_color)
                connected.update(same_color_group)
        
        return connected
    
    def find_same_color_group(self, start_row: int, start_col: int, target_color) -> Set[Tuple[int, int]]:
        """找到指定颜色的连接组"""
        if target_color == Color.COLORFUL:
            return {(start_row, start_col)}  # 彩色色块不再递归连接
        
        connected = set()
        to_check = [(start_row, start_col)]
        
        while to_check:
            row, col = to_check.pop()
            if (row, col) in connected:
                continue
            
            if (0 <= row < self.GRID_SIZE and 0 <= col < self.GRID_SIZE and 
                self.grid[row][col] == target_color):
                
                connected.add((row, col))
                
                # 检查四个方向
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    new_row, new_col = row + dr, col + dc
                    if (new_row, new_col) not in connected:
                        to_check.append((new_row, new_col))
        
        return connected
    
    def handle_click(self, pos: Tuple[int, int]):
        """处理鼠标点击"""
        if self.state != GameState.PLAYING:
            return
        
        # 检查是否点击道具区域
        if self.handle_tool_click(pos):
            return
        
        row, col = self.get_cell_at_pos(pos)
        if row is None or col is None:
            return
        
        logger.info(f"点击坐标: ({row}, {col})")
        
        # 如果处于锤子模式，直接消除单个色块
        if self.is_hammer_mode:
            self.use_hammer(row, col)
            return
        
        # 找到连接的同色块
        connected = self.find_connected_cells(row, col)
        
        if len(connected) >= 2:
            # 可以消除
            self.eliminate_cells(connected)
            logger.info(f"消除坐标: {list(connected)}")
            self.selected_cells.clear()
        else:
            # 更新选中状态
            if (row, col) in self.selected_cells:
                self.selected_cells.remove((row, col))
            else:
                self.selected_cells.add((row, col))
    
    def handle_tool_click(self, pos: Tuple[int, int]) -> bool:
        """处理道具区域点击，返回是否点击了道具"""
        x, y = pos
        tool_area_start_y = self.SCORE_HEIGHT + self.GRID_SIZE * (self.CELL_SIZE + self.GRID_MARGIN) + self.GRID_MARGIN
        
        # 作弊功能：锤子模式下点击Score文字重置锤子数量
        if self.is_hammer_mode and y < self.SCORE_HEIGHT:
            # Score文字的大致位置 (根据draw_ui中的位置)
            score_rect = pygame.Rect(10, 10, 100, 30)  # Score文字区域
            if score_rect.collidepoint(x, y):
                self.hammer_count = 99
                logger.info("🎉 作弊功能激活！锤子数量重置为99个")
                return True
        
        # 检查是否在道具区域内
        if y < tool_area_start_y or y > tool_area_start_y + self.TOOL_HEIGHT:
            return False
        
        # 锤子道具的位置 (左侧)
        hammer_rect = pygame.Rect(20, tool_area_start_y + 20, 60, 60)
        if hammer_rect.collidepoint(x, y) and self.hammer_count > 0:
            self.toggle_hammer_mode()
            return True
        
        return False
    
    def toggle_hammer_mode(self):
        """切换锤子模式"""
        if self.is_hammer_mode:
            # 取消锤子模式
            self.is_hammer_mode = False
            self.create_finger_cursor()  # 恢复普通鼠标
            logger.info("取消锤子模式")
        else:
            # 进入锤子模式
            self.is_hammer_mode = True
            pygame.mouse.set_cursor(self.hammer_cursor)  # 设置锤子鼠标
            logger.info("进入锤子模式")
    
    def use_hammer(self, row: int, col: int):
        """使用锤子消除单个色块"""
        if self.grid[row][col] is None:
            return
        
        # 消除单个色块
        eliminated_color = self.grid[row][col]
        self.grid[row][col] = None
        
        # 添加消除效果
        rect = self.get_cell_rect(row, col)
        self.elimination_effects.append({
            'rect': rect,
            'timer': 30,
            'color': eliminated_color
        })
        
        # 更新分数
        points = 50  # 锤子消除获得50分
        self.score += points
        self.eliminated_count += 1
        
        # 减少锤子数量
        self.hammer_count -= 1
        
        # 退出锤子模式
        self.is_hammer_mode = False
        self.create_finger_cursor()  # 恢复普通鼠标
        
        logger.info(f"🔨 使用锤子消除坐标 ({row}, {col}) 的 {eliminated_color.name} 色块，获得 {points} 分，剩余锤子: {self.hammer_count}")
        
        # 开始掉落动画
        self.start_falling_animation()
    
    def eliminate_cells(self, cells: Set[Tuple[int, int]]):
        """消除指定的色块"""
        eliminated_color = None
        is_gold_elimination = False
        is_diamond_elimination = False
        is_colorful_elimination = False
        is_pearl_elimination = False
        
        # 添加消除效果
        for row, col in cells:
            if eliminated_color is None:
                eliminated_color = self.grid[row][col]
            
            # 检查是否是特殊色块
            if self.grid[row][col] == Color.GOLD:
                is_gold_elimination = True
            elif self.grid[row][col] == Color.DIAMOND:
                is_diamond_elimination = True
            elif self.grid[row][col] == Color.COLORFUL:
                is_colorful_elimination = True
            elif self.grid[row][col] == Color.PEARL:
                is_pearl_elimination = True
            
            # 添加消除效果动画
            rect = self.get_cell_rect(row, col)
            self.elimination_effects.append({
                'rect': rect,
                'timer': 30,  # 效果持续帧数
                'color': eliminated_color
            })
            
            # 清除色块
            self.grid[row][col] = None
        
        # 更新分数和统计
        if is_pearl_elimination and eliminated_color == Color.PEARL:
            # 珍珠色块消除，给予终极奖励
            points = len(cells) * 15000
            logger.info(f"🐚 消除了 {len(cells)} 个珍珠色块，获得 {points} 分！！！！")
        elif is_colorful_elimination and eliminated_color == Color.COLORFUL:
            # 彩色色块消除，给予特殊奖励
            points = len(cells) * 5000  # 彩色色块本身的价值
            logger.info(f"🌈 消除了 {len(cells)} 个彩色色块，获得 {points} 分！！")
        elif is_diamond_elimination and eliminated_color == Color.DIAMOND:
            # 钻石色块消除，给予超级奖励
            points = len(cells) * 10000
            logger.info(f"💎 消除了 {len(cells)} 个钻石色块，获得 {points} 分！！！")
        elif is_gold_elimination and eliminated_color == Color.GOLD:
            # 黄金色块消除，给予特殊奖励
            points = len(cells) * 1000
            logger.info(f"🌟 消除了 {len(cells)} 个黄金色块，获得 {points} 分！")
        else:
            # 普通色块消除
            points = len(cells) * 10
            logger.info(f"消除了 {len(cells)} 个 {eliminated_color.name} 色块，获得 {points} 分")
        
        self.score += points
        self.eliminated_count += len(cells)
        
        # 生成特殊色块的逻辑
        if is_colorful_elimination:
            # 彩色色块消除后生成珍珠色块
            self.generate_pearl_block_near(cells)
        elif is_diamond_elimination and len(cells) >= 3:
            # 3个或以上钻石消除后生成彩色色块
            self.generate_colorful_block_near(cells)
            logger.info(f"✨ 特殊触发：{len(cells)}个钻石连消，生成彩色万能色块！")
        elif is_gold_elimination:
            # 黄金色块消除后生成钻石色块
            self.generate_diamond_block_near(cells)
        elif not (is_diamond_elimination or is_pearl_elimination):
            # 普通色块消除后生成黄金色块（钻石单独消除和珍珠消除后不生成新色块）
            self.generate_gold_block_near(cells)
        
        # 开始掉落动画
        self.start_falling_animation()
    
    def generate_gold_block_near(self, eliminated_cells: Set[Tuple[int, int]]):
        """在消除区域附近生成黄金色块"""
        if not eliminated_cells:
            return
        
        # 收集消除区域附近的候选位置
        candidate_positions = set()
        
        for row, col in eliminated_cells:
            # 检查周围8个方向的位置
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue  # 跳过中心位置
                    
                    new_row, new_col = row + dr, col + dc
                    if (0 <= new_row < self.GRID_SIZE and 
                        0 <= new_col < self.GRID_SIZE and
                        (new_row, new_col) not in eliminated_cells):
                        candidate_positions.add((new_row, new_col))
        
        # 过滤掉已经是特殊色块的位置
        valid_positions = []
        for row, col in candidate_positions:
            if (self.grid[row][col] != Color.GOLD and 
                self.grid[row][col] != Color.DIAMOND and
                self.grid[row][col] != Color.COLORFUL and
                self.grid[row][col] != Color.PEARL):
                valid_positions.append((row, col))
        
        # 如果有有效位置，随机选择一个生成黄金色块
        if valid_positions:
            target_row, target_col = random.choice(valid_positions)
            old_color = self.grid[target_row][target_col]
            self.grid[target_row][target_col] = Color.GOLD
            logger.info(f"✨ 在位置 ({target_row}, {target_col}) 生成黄金色块 (原色块: {old_color.name if old_color else 'None'})")
        else:
            logger.info("⚠️ 没有合适的位置生成黄金色块（附近都是特殊色块）")
    
    def generate_diamond_block_near(self, eliminated_cells: Set[Tuple[int, int]]):
        """在消除区域附近生成钻石色块"""
        if not eliminated_cells:
            return
        
        # 收集消除区域附近的候选位置
        candidate_positions = set()
        
        for row, col in eliminated_cells:
            # 检查周围8个方向的位置
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue  # 跳过中心位置
                    
                    new_row, new_col = row + dr, col + dc
                    if (0 <= new_row < self.GRID_SIZE and 
                        0 <= new_col < self.GRID_SIZE and
                        (new_row, new_col) not in eliminated_cells):
                        candidate_positions.add((new_row, new_col))
        
        # 过滤掉已经是特殊色块的位置
        valid_positions = []
        for row, col in candidate_positions:
            if (self.grid[row][col] != Color.GOLD and 
                self.grid[row][col] != Color.DIAMOND and
                self.grid[row][col] != Color.COLORFUL and
                self.grid[row][col] != Color.PEARL):
                valid_positions.append((row, col))
        
        # 如果有有效位置，随机选择一个生成钻石色块
        if valid_positions:
            target_row, target_col = random.choice(valid_positions)
            old_color = self.grid[target_row][target_col]
            self.grid[target_row][target_col] = Color.DIAMOND
            logger.info(f"💎 在位置 ({target_row}, {target_col}) 生成钻石色块 (原色块: {old_color.name if old_color else 'None'})")
        else:
            logger.info("⚠️ 没有合适的位置生成钻石色块（附近都是特殊色块）")
    
    def generate_colorful_block_near(self, eliminated_cells: Set[Tuple[int, int]]):
        """在消除区域附近生成彩色万能色块"""
        if not eliminated_cells:
            return
        
        # 收集消除区域附近的候选位置
        candidate_positions = set()
        
        for row, col in eliminated_cells:
            # 检查周围8个方向的位置
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue  # 跳过中心位置
                    
                    new_row, new_col = row + dr, col + dc
                    if (0 <= new_row < self.GRID_SIZE and 
                        0 <= new_col < self.GRID_SIZE and
                        (new_row, new_col) not in eliminated_cells):
                        candidate_positions.add((new_row, new_col))
        
        # 过滤掉已经是特殊色块的位置
        valid_positions = []
        for row, col in candidate_positions:
            if (self.grid[row][col] != Color.GOLD and 
                self.grid[row][col] != Color.DIAMOND and
                self.grid[row][col] != Color.COLORFUL and
                self.grid[row][col] != Color.PEARL):
                valid_positions.append((row, col))
        
        # 如果有有效位置，随机选择一个生成彩色色块
        if valid_positions:
            target_row, target_col = random.choice(valid_positions)
            old_color = self.grid[target_row][target_col]
            self.grid[target_row][target_col] = Color.COLORFUL
            logger.info(f"🌈 在位置 ({target_row}, {target_col}) 生成彩色万能色块 (原色块: {old_color.name if old_color else 'None'})")
        else:
            logger.info("⚠️ 没有合适的位置生成彩色色块（附近都是特殊色块）")
    
    def generate_pearl_block_near(self, eliminated_cells: Set[Tuple[int, int]]):
        """在消除区域附近生成珍珠色块"""
        if not eliminated_cells:
            return
        
        # 收集消除区域附近的候选位置
        candidate_positions = set()
        
        for row, col in eliminated_cells:
            # 检查周围8个方向的位置
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue  # 跳过中心位置
                    
                    new_row, new_col = row + dr, col + dc
                    if (0 <= new_row < self.GRID_SIZE and 
                        0 <= new_col < self.GRID_SIZE and
                        (new_row, new_col) not in eliminated_cells):
                        candidate_positions.add((new_row, new_col))
        
        # 过滤掉已经是特殊色块的位置
        valid_positions = []
        for row, col in candidate_positions:
            if (self.grid[row][col] != Color.GOLD and 
                self.grid[row][col] != Color.DIAMOND and
                self.grid[row][col] != Color.COLORFUL and
                self.grid[row][col] != Color.PEARL):
                valid_positions.append((row, col))
        
        # 如果有有效位置，随机选择一个生成珍珠色块
        if valid_positions:
            target_row, target_col = random.choice(valid_positions)
            old_color = self.grid[target_row][target_col]
            self.grid[target_row][target_col] = Color.PEARL
            logger.info(f"🐚 在位置 ({target_row}, {target_col}) 生成珍珠色块 (原色块: {old_color.name if old_color else 'None'})")
        else:
            logger.info("⚠️ 没有合适的位置生成珍珠色块（附近都是特殊色块）")
    
    def start_falling_animation(self):
        """开始掉落动画"""
        self.state = GameState.FALLING
        self.falling_cells = []
        
        # 为每列处理掉落
        for col in range(self.GRID_SIZE):
            # 收集非空色块
            non_empty = []
            empty_count = 0
            
            for row in range(self.GRID_SIZE - 1, -1, -1):  # 从底部向上
                if self.grid[row][col] is not None:
                    non_empty.append(self.grid[row][col])
                else:
                    empty_count += 1
                self.grid[row][col] = None
            
            # 重新放置现有色块
            for i, color in enumerate(non_empty):
                target_row = self.GRID_SIZE - 1 - i
                self.grid[target_row][col] = color
            
            # 默认自动填充新色块，从上方掉落新色块填满网格
            if empty_count > 0:
                for i in range(empty_count):
                    new_row = empty_count - 1 - i
                    self.grid[new_row][col] = random.choice(self.COLORS)
                    logger.info(f"在位置 ({new_row}, {col}) 生成新色块: {self.grid[new_row][col].name}")
        
        # 模拟掉落完成
        pygame.time.set_timer(pygame.USEREVENT + 1, 500)  # 500ms后完成掉落
    
    def update_elimination_effects(self):
        """更新消除效果"""
        self.elimination_effects = [
            effect for effect in self.elimination_effects
            if self.update_single_effect(effect)
        ]
    
    def update_gold_animation(self):
        """更新黄金色块动画效果"""
        import math
        self.gold_animation_timer += 1
        # 使用sin函数创建周期性闪烁效果，周期约为60帧(1秒)
        self.gold_glow_intensity = (math.sin(self.gold_animation_timer * 0.1) + 1) * 0.5  # 0-1之间
    
    def update_diamond_animation(self):
        """更新钻石色块动画效果"""
        import math
        self.diamond_animation_timer += 1
        # 钻石使用更快的闪烁频率，创造更炫目的效果
        self.diamond_glow_intensity = (math.sin(self.diamond_animation_timer * 0.15) + 1) * 0.5  # 0-1之间，比黄金更快
    
    def update_colorful_animation(self):
        """更新彩色色块动画效果"""
        import math
        self.colorful_animation_timer += 1
        # 彩色使用彩虹变化效果，更加炫目
        self.colorful_glow_intensity = (math.sin(self.colorful_animation_timer * 0.2) + 1) * 0.5  # 0-1之间，最快频率
    
    def update_pearl_animation(self):
        """更新珍珠色块动画效果"""
        import math
        self.pearl_animation_timer += 1
        # 珍珠使用优雅的脉动效果
        self.pearl_glow_intensity = (math.sin(self.pearl_animation_timer * 0.08) + 1) * 0.5  # 0-1之间，最慢优雅
    
    def update_single_effect(self, effect: dict) -> bool:
        """更新单个消除效果，返回是否继续"""
        effect['timer'] -= 1
        return effect['timer'] > 0
    
    def draw_elimination_effect(self, effect: dict):
        """绘制消除效果"""
        alpha = int(255 * (effect['timer'] / 30))
        size_factor = 1 + (30 - effect['timer']) / 30 * 0.5
        
        rect = effect['rect']
        new_size = int(rect.width * size_factor)
        new_rect = pygame.Rect(
            rect.centerx - new_size // 2,
            rect.centery - new_size // 2,
            new_size,
            new_size
        )
        
        # 创建带透明度的表面
        temp_surface = pygame.Surface((new_size, new_size), pygame.SRCALPHA)
        color_with_alpha = (*effect['color'].value, alpha)
        pygame.draw.rect(temp_surface, color_with_alpha, (0, 0, new_size, new_size))
        
        self.screen.blit(temp_surface, new_rect)
    
    def draw_gold_effects(self, rect):
        """绘制黄金色块的动态闪光效果"""
        import math
        
        # 计算当前闪光强度 (0.3-1.0之间变化)
        glow_alpha = int(255 * (0.3 + 0.7 * self.gold_glow_intensity))
        
        # 第一层：外部光晕效果
        glow_size = int(8 + 6 * self.gold_glow_intensity)  # 8-14像素的光晕
        outer_rect = pygame.Rect(
            rect.x - glow_size // 2, 
            rect.y - glow_size // 2, 
            rect.width + glow_size, 
            rect.height + glow_size
        )
        glow_surface = pygame.Surface((outer_rect.width, outer_rect.height), pygame.SRCALPHA)
        glow_color = (255, 215, 0, max(50, glow_alpha // 4))  # 半透明黄金色光晕
        pygame.draw.rect(glow_surface, glow_color, (0, 0, outer_rect.width, outer_rect.height))
        self.screen.blit(glow_surface, outer_rect)
        
        # 第二层：动态闪烁的白色边框
        border_alpha = max(180, glow_alpha)
        border_color = (255, 255, 255, border_alpha)
        border_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(border_surface, border_color, (0, 0, rect.width, rect.height), 4)
        self.screen.blit(border_surface, rect)
        
        # 第三层：内部动态高光
        inner_size = max(8, int(16 * self.gold_glow_intensity))  # 动态大小的内部高光
        inner_rect = pygame.Rect(
            rect.x + (rect.width - inner_size) // 2,
            rect.y + (rect.height - inner_size) // 2,
            inner_size,
            inner_size
        )
        inner_surface = pygame.Surface((inner_size, inner_size), pygame.SRCALPHA)
        inner_alpha = max(100, int(200 * self.gold_glow_intensity))
        inner_color = (255, 255, 200, inner_alpha)
        pygame.draw.ellipse(inner_surface, inner_color, (0, 0, inner_size, inner_size))
        self.screen.blit(inner_surface, inner_rect)
        
        # 第四层：闪烁的角落星光效果
        if self.gold_glow_intensity > 0.8:  # 只在高强度时显示
            star_points = [
                (rect.x + 5, rect.y + 5),           # 左上
                (rect.x + rect.width - 5, rect.y + 5),    # 右上
                (rect.x + 5, rect.y + rect.height - 5),   # 左下
                (rect.x + rect.width - 5, rect.y + rect.height - 5)  # 右下
            ]
            
            for point in star_points:
                star_surface = pygame.Surface((8, 8), pygame.SRCALPHA)
                star_alpha = int(255 * (self.gold_glow_intensity - 0.8) * 5)  # 只在峰值时显示
                pygame.draw.circle(star_surface, (255, 255, 255, star_alpha), (4, 4), 3)
                self.screen.blit(star_surface, (point[0] - 4, point[1] - 4))
    
    def draw_diamond_effects(self, rect):
        """绘制钻石色块的超华丽动态效果"""
        import math
        
        # 计算当前闪光强度 (0.2-1.0之间变化，比黄金更强)
        glow_alpha = int(255 * (0.2 + 0.8 * self.diamond_glow_intensity))
        
        # 第一层：多重外部光晕效果
        for i in range(3):  # 三层光晕
            glow_size = int(12 + 8 * self.diamond_glow_intensity + i * 4)  # 更大的光晕
            outer_rect = pygame.Rect(
                rect.x - glow_size // 2, 
                rect.y - glow_size // 2, 
                rect.width + glow_size, 
                rect.height + glow_size
            )
            glow_surface = pygame.Surface((outer_rect.width, outer_rect.height), pygame.SRCALPHA)
            # 冰蓝色光晕，透明度递减
            alpha = max(30, glow_alpha // (4 + i * 2))
            glow_color = (185, 242, 255, alpha)
            pygame.draw.rect(glow_surface, glow_color, (0, 0, outer_rect.width, outer_rect.height))
            self.screen.blit(glow_surface, outer_rect)
        
        # 第二层：彩虹色动态边框
        border_colors = [
            (255, 255, 255),  # 白色
            (185, 242, 255),  # 冰蓝
            (200, 200, 255),  # 淡紫
            (255, 200, 255),  # 粉色
        ]
        for i, color in enumerate(border_colors):
            alpha = max(150, int(glow_alpha * (1 - i * 0.1)))
            border_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            border_color = (*color, alpha)
            pygame.draw.rect(border_surface, border_color, (0, 0, rect.width, rect.height), 2 + i)
            self.screen.blit(border_surface, rect)
        
        # 第三层：动态钻石切面效果
        center_x, center_y = rect.centerx, rect.centery
        diamond_size = int(20 + 15 * self.diamond_glow_intensity)
        
        # 钻石形状的多个切面
        for angle in [0, 45, 90, 135]:  # 四个切面
            radians = math.radians(angle + self.diamond_animation_timer * 2)  # 慢速旋转
            offset_x = int(math.cos(radians) * diamond_size // 4)
            offset_y = int(math.sin(radians) * diamond_size // 4)
            
            facet_surface = pygame.Surface((diamond_size, diamond_size), pygame.SRCALPHA)
            facet_alpha = max(80, int(180 * self.diamond_glow_intensity))
            facet_color = (255, 255, 255, facet_alpha)
            pygame.draw.ellipse(facet_surface, facet_color, (0, 0, diamond_size, diamond_size))
            
            self.screen.blit(facet_surface, 
                           (center_x - diamond_size // 2 + offset_x, 
                            center_y - diamond_size // 2 + offset_y))
        
        # 第四层：超级星光爆发效果
        if self.diamond_glow_intensity > 0.7:  # 更频繁的星光
            # 8个方向的星光射线
            for angle in range(0, 360, 45):
                radians = math.radians(angle)
                length = int(25 + 10 * self.diamond_glow_intensity)
                end_x = center_x + int(math.cos(radians) * length)
                end_y = center_y + int(math.sin(radians) * length)
                
                star_alpha = int(255 * (self.diamond_glow_intensity - 0.7) * 3.33)
                for thickness in range(1, 4):
                    line_surface = pygame.Surface((rect.width * 2, rect.height * 2), pygame.SRCALPHA)
                    line_alpha = star_alpha // thickness
                    pygame.draw.line(line_surface, (255, 255, 255, line_alpha), 
                                   (rect.width, rect.height), 
                                   (end_x - rect.x + rect.width, end_y - rect.y + rect.height), 
                                   thickness)
                    self.screen.blit(line_surface, (rect.x - rect.width, rect.y - rect.height))
        
        # 第五层：中心爆发光点（最高强度时）
        if self.diamond_glow_intensity > 0.9:  # 只在最高强度时
            burst_size = int(30 * (self.diamond_glow_intensity - 0.9) * 10)
            burst_surface = pygame.Surface((burst_size, burst_size), pygame.SRCALPHA)
            burst_alpha = int(255 * (self.diamond_glow_intensity - 0.9) * 10)
            pygame.draw.circle(burst_surface, (255, 255, 255, burst_alpha), 
                             (burst_size // 2, burst_size // 2), burst_size // 2)
            self.screen.blit(burst_surface, 
                           (center_x - burst_size // 2, center_y - burst_size // 2))
    
    def draw_colorful_effects(self, rect):
        """绘制彩色万能色块的彩虹动态效果"""
        import math
        
        # 计算当前闪光强度 (0.3-1.0之间变化)
        glow_alpha = int(255 * (0.3 + 0.7 * self.colorful_glow_intensity))
        
        # 第一层：彩虹光晕效果
        rainbow_colors = [
            (255, 0, 0),    # 红
            (255, 127, 0),  # 橙
            (255, 255, 0),  # 黄
            (0, 255, 0),    # 绿
            (0, 0, 255),    # 蓝
            (75, 0, 130),   # 靛
            (148, 0, 211),  # 紫
        ]
        
        for i, color in enumerate(rainbow_colors):
            angle_offset = (self.colorful_animation_timer + i * 15) % 360
            glow_size = int(10 + 8 * self.colorful_glow_intensity + i * 2)
            
            outer_rect = pygame.Rect(
                rect.x - glow_size // 2, 
                rect.y - glow_size // 2, 
                rect.width + glow_size, 
                rect.height + glow_size
            )
            
            glow_surface = pygame.Surface((outer_rect.width, outer_rect.height), pygame.SRCALPHA)
            alpha = max(20, glow_alpha // (4 + i))
            glow_color = (*color, alpha)
            pygame.draw.rect(glow_surface, glow_color, (0, 0, outer_rect.width, outer_rect.height))
            self.screen.blit(glow_surface, outer_rect)
        
        # 第二层：旋转彩虹边框
        for i in range(4):
            border_thickness = 3 - i
            color_index = (self.colorful_animation_timer // 10 + i) % len(rainbow_colors)
            border_color = rainbow_colors[color_index]
            border_alpha = max(150, int(glow_alpha * (1 - i * 0.1)))
            
            border_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(border_surface, (*border_color, border_alpha), 
                           (0, 0, rect.width, rect.height), border_thickness)
            self.screen.blit(border_surface, rect)
        
        # 第三层：中心彩虹漩涡
        center_x, center_y = rect.centerx, rect.centery
        spiral_size = int(15 + 10 * self.colorful_glow_intensity)
        
        for angle in range(0, 360, 45):
            color_index = (angle // 45 + self.colorful_animation_timer // 5) % len(rainbow_colors)
            spiral_color = rainbow_colors[color_index]
            
            radians = math.radians(angle + self.colorful_animation_timer * 3)
            offset_x = int(math.cos(radians) * spiral_size // 3)
            offset_y = int(math.sin(radians) * spiral_size // 3)
            
            spiral_surface = pygame.Surface((spiral_size, spiral_size), pygame.SRCALPHA)
            spiral_alpha = max(100, int(180 * self.colorful_glow_intensity))
            pygame.draw.circle(spiral_surface, (*spiral_color, spiral_alpha), 
                             (spiral_size // 2, spiral_size // 2), spiral_size // 4)
            
            self.screen.blit(spiral_surface, 
                           (center_x - spiral_size // 2 + offset_x, 
                            center_y - spiral_size // 2 + offset_y))
    
    def draw_pearl_effects(self, rect):
        """绘制珍珠色块的优雅光泽效果"""
        import math
        
        # 计算当前闪光强度 (0.4-1.0之间变化，更稳定)
        glow_alpha = int(255 * (0.4 + 0.6 * self.pearl_glow_intensity))
        
        # 第一层：珍珠光泽外晕
        for i in range(5):  # 五层渐变光晕
            glow_size = int(6 + 4 * self.pearl_glow_intensity + i * 2)
            outer_rect = pygame.Rect(
                rect.x - glow_size // 2, 
                rect.y - glow_size // 2, 
                rect.width + glow_size, 
                rect.height + glow_size
            )
            
            glow_surface = pygame.Surface((outer_rect.width, outer_rect.height), pygame.SRCALPHA)
            # 珍珠白到淡蓝的渐变
            pearl_colors = [(248, 248, 255), (240, 248, 255), (230, 240, 255), (220, 230, 255), (210, 220, 255)]
            alpha = max(15, glow_alpha // (3 + i * 2))
            glow_color = (*pearl_colors[i % len(pearl_colors)], alpha)
            pygame.draw.ellipse(glow_surface, glow_color, (0, 0, outer_rect.width, outer_rect.height))
            self.screen.blit(glow_surface, outer_rect)
        
        # 第二层：珍珠质感边框
        for thickness in range(1, 4):
            border_alpha = max(180, int(glow_alpha * (1 - thickness * 0.1)))
            border_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            border_color = (255, 255, 255, border_alpha)
            pygame.draw.rect(border_surface, border_color, (0, 0, rect.width, rect.height), thickness)
            self.screen.blit(border_surface, rect)
        
        # 第三层：珍珠光泽移动高光
        center_x, center_y = rect.centerx, rect.centery
        highlight_angle = self.pearl_animation_timer * 2  # 缓慢移动
        
        for i in range(3):  # 三道高光
            angle = highlight_angle + i * 120
            radians = math.radians(angle)
            highlight_size = int(12 + 8 * self.pearl_glow_intensity)
            
            offset_x = int(math.cos(radians) * highlight_size // 4)
            offset_y = int(math.sin(radians) * highlight_size // 4)
            
            highlight_surface = pygame.Surface((highlight_size, highlight_size), pygame.SRCALPHA)
            highlight_alpha = max(120, int(200 * self.pearl_glow_intensity))
            highlight_color = (255, 255, 255, highlight_alpha)
            pygame.draw.ellipse(highlight_surface, highlight_color, 
                              (0, 0, highlight_size, highlight_size))
            
            self.screen.blit(highlight_surface, 
                           (center_x - highlight_size // 2 + offset_x, 
                            center_y - highlight_size // 2 + offset_y))
        
        # 第四层：珍珠图案 - 简化的同心圆
        pattern_colors = [(255, 255, 255), (248, 248, 255), (240, 248, 255)]
        for i, color in enumerate(pattern_colors):
            pattern_size = int(rect.width - 10 - i * 6)
            if pattern_size > 0:
                pattern_surface = pygame.Surface((pattern_size, pattern_size), pygame.SRCALPHA)
                pattern_alpha = max(80, int(150 * self.pearl_glow_intensity))
                pygame.draw.ellipse(pattern_surface, (*color, pattern_alpha), 
                                  (0, 0, pattern_size, pattern_size), 2)
                
                self.screen.blit(pattern_surface, 
                               (center_x - pattern_size // 2, 
                                center_y - pattern_size // 2))
    
    def draw_rounded_3d_block(self, rect, color):
        """绘制立体圆角色块"""
        # 圆角半径
        corner_radius = 8
        
        # 立体效果的高光和阴影颜色
        base_color = color.value
        highlight_color = tuple(min(255, c + 40) for c in base_color)  # 更亮的高光
        shadow_color = tuple(max(0, c - 30) for c in base_color)       # 更暗的阴影
        
        # 绘制阴影 (右下偏移)
        shadow_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width, rect.height)
        pygame.draw.rect(self.screen, shadow_color, shadow_rect, border_radius=corner_radius)
        
        # 绘制主体色块
        pygame.draw.rect(self.screen, base_color, rect, border_radius=corner_radius)
        
        # 绘制高光 (左上角)
        highlight_rect = pygame.Rect(rect.x + 3, rect.y + 3, rect.width - 12, rect.height - 12)
        highlight_surface = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surface, (*highlight_color, 120), (0, 0, highlight_rect.width, highlight_rect.height), border_radius=corner_radius-2)
        self.screen.blit(highlight_surface, highlight_rect)
        
        # 绘制顶部高光条
        top_highlight = pygame.Rect(rect.x + 6, rect.y + 6, rect.width - 12, 8)
        top_surface = pygame.Surface((top_highlight.width, top_highlight.height), pygame.SRCALPHA)
        pygame.draw.rect(top_surface, (*highlight_color, 80), (0, 0, top_highlight.width, top_highlight.height), border_radius=corner_radius-3)
        self.screen.blit(top_surface, top_highlight)
        
        # 绘制左侧高光条
        left_highlight = pygame.Rect(rect.x + 6, rect.y + 6, 8, rect.height - 12)
        left_surface = pygame.Surface((left_highlight.width, left_highlight.height), pygame.SRCALPHA)
        pygame.draw.rect(left_surface, (*highlight_color, 60), (0, 0, left_highlight.width, left_highlight.height), border_radius=corner_radius-3)
        self.screen.blit(left_surface, left_highlight)
    
    def draw(self):
        """绘制游戏画面"""
        self.screen.fill(Color.WHITE.value)
        
        # 绘制网格
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                rect = self.get_cell_rect(row, col)
                
                # 绘制背景
                if self.grid[row][col] is None:
                    pygame.draw.rect(self.screen, Color.BLACK.value, rect)
                else:
                    # 普通色块使用立体圆角效果，特殊色块保持原有绘制
                    if self.grid[row][col] in [Color.RED, Color.GREEN, Color.BLUE, Color.ORANGE, Color.PINK]:
                        self.draw_rounded_3d_block(rect, self.grid[row][col])
                    else:
                        pygame.draw.rect(self.screen, self.grid[row][col].value, rect)
                    
                    # 特殊色块动态效果
                    if self.grid[row][col] == Color.GOLD:
                        self.draw_gold_effects(rect)
                    elif self.grid[row][col] == Color.DIAMOND:
                        self.draw_diamond_effects(rect)
                    elif self.grid[row][col] == Color.COLORFUL:
                        self.draw_colorful_effects(rect)
                    elif self.grid[row][col] == Color.PEARL:
                        self.draw_pearl_effects(rect)
                
                # 绘制边框
                pygame.draw.rect(self.screen, Color.GRAY.value, rect, 2)
                
                # 绘制选中状态
                if (row, col) in self.selected_cells:
                    pygame.draw.rect(self.screen, Color.WHITE.value, rect, 4)
        
        # 绘制消除效果
        for effect in self.elimination_effects:
            self.draw_elimination_effect(effect)
        
        # 绘制UI信息
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_ui(self):
        """绘制UI信息"""
        # 上方计分区域
        score_y = 10
        
        # 分数 - 限制最大显示为9999999
        display_score = min(self.score, 9999999)
        score_suffix = "+" if self.score > 9999999 else ""
        score_text = self.font.render(f"Score: {display_score}{score_suffix}", True, Color.BLACK.value)
        self.screen.blit(score_text, (10, score_y))
        
        # 消除数量
        count_text = self.font.render(f"Eliminated: {self.eliminated_count}", True, Color.BLACK.value)
        self.screen.blit(count_text, (250, score_y))
        
        # 游戏状态
        if self.state == GameState.FALLING:
            status_text = self.font.render("Falling...", True, Color.BLACK.value)
            self.screen.blit(status_text, (450, score_y))
        
        # 下方道具区域
        self.draw_tools()
    
    def draw_tools(self):
        """绘制道具区域"""
        tool_area_start_y = self.SCORE_HEIGHT + self.GRID_SIZE * (self.CELL_SIZE + self.GRID_MARGIN) + self.GRID_MARGIN
        
        # 绘制道具区域背景
        tool_rect = pygame.Rect(0, tool_area_start_y, self.WINDOW_WIDTH, self.TOOL_HEIGHT)
        pygame.draw.rect(self.screen, (240, 240, 240), tool_rect)  # 浅灰色背景
        pygame.draw.rect(self.screen, Color.GRAY.value, tool_rect, 2)  # 边框
        
        # 道具标题
        title_text = self.font.render("Tools:", True, Color.BLACK.value)
        self.screen.blit(title_text, (10, tool_area_start_y + 5))
        
        # 锤子道具
        hammer_rect = pygame.Rect(20, tool_area_start_y + 30, 60, 60)
        
        # 锤子背景色（根据状态变化）
        if self.is_hammer_mode:
            hammer_bg_color = (255, 200, 200)  # 选中状态：淡红色
        elif self.hammer_count > 0:
            hammer_bg_color = (200, 255, 200)  # 可用状态：淡绿色
        else:
            hammer_bg_color = (200, 200, 200)  # 不可用状态：灰色
        
        pygame.draw.rect(self.screen, hammer_bg_color, hammer_rect)
        pygame.draw.rect(self.screen, Color.BLACK.value, hammer_rect, 2)
        
        # 绘制锤子图标
        self.draw_hammer_icon(hammer_rect)
        
        # 锤子数量文本 - 调整位置避免溢出
        count_text = self.font.render(f"x{self.hammer_count}", True, Color.BLACK.value)
        self.screen.blit(count_text, (hammer_rect.x + 65, hammer_rect.y + 10))
        
        # 锤子说明 - 调整位置
        desc_text = pygame.font.Font(None, 18).render("Hammer", True, Color.BLACK.value)
        self.screen.blit(desc_text, (hammer_rect.x + 65, hammer_rect.y + 30))
    
    def draw_hammer_icon(self, rect):
        """在指定矩形内绘制锤子图标"""
        # 计算锤子图标的位置和大小
        icon_size = min(rect.width - 10, rect.height - 10)
        icon_x = rect.centerx - icon_size // 2
        icon_y = rect.centery - icon_size // 2
        
        # 定义颜色
        brown = (139, 69, 19)      # 锤柄棕色
        dark_brown = (101, 50, 14) # 锤柄阴影
        silver = (192, 192, 192)   # 锤头银色
        dark_silver = (128, 128, 128) # 锤头阴影
        
        # 缩放比例
        scale = icon_size / 32
        
        # 绘制锤柄 (竖直)
        handle_rect = pygame.Rect(
            icon_x + int(13 * scale), 
            icon_y + int(16 * scale), 
            int(6 * scale), 
            int(14 * scale)
        )
        pygame.draw.rect(self.screen, brown, handle_rect)
        pygame.draw.rect(self.screen, dark_brown, handle_rect, 1)
        
        # 绘制锤头
        hammer_head = pygame.Rect(
            icon_x + int(8 * scale), 
            icon_y + int(6 * scale), 
            int(16 * scale), 
            int(10 * scale)
        )
        pygame.draw.rect(self.screen, silver, hammer_head)
        pygame.draw.rect(self.screen, dark_silver, hammer_head, 2)
        
        # 锤头高光
        highlight = pygame.Rect(
            icon_x + int(10 * scale), 
            icon_y + int(7 * scale), 
            int(12 * scale), 
            int(2 * scale)
        )
        pygame.draw.rect(self.screen, (220, 220, 220), highlight)
    
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    self.handle_click(event.pos)
            
            elif event.type == pygame.USEREVENT + 1:
                # 掉落动画完成
                self.state = GameState.PLAYING
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # 取消定时器
                logger.info("掉落动画完成")
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # 重置游戏
                    self.reset_game()
        
        return True
    
    def reset_game(self):
        """重置游戏"""
        self.generate_grid()
        self.selected_cells.clear()
        self.score = 0
        self.eliminated_count = 0
        self.state = GameState.PLAYING
        self.elimination_effects.clear()
        self.gold_animation_timer = 0       # 重置黄金动画计时器
        self.gold_glow_intensity = 0
        self.diamond_animation_timer = 0    # 重置钻石动画计时器
        self.diamond_glow_intensity = 0
        self.colorful_animation_timer = 0   # 重置彩色动画计时器
        self.colorful_glow_intensity = 0
        self.pearl_animation_timer = 0      # 重置珍珠动画计时器
        self.pearl_glow_intensity = 0
        
        # 重置道具状态
        self.hammer_count = 3
        self.is_hammer_mode = False
        self.create_finger_cursor()  # 恢复普通鼠标
        
        logger.info("游戏重置")
    
    def run(self):
        """游戏主循环"""
        clock = pygame.time.Clock()
        running = True
        
        logger.info("游戏开始")
        
        while running:
            running = self.handle_events()
            self.update_elimination_effects()
            self.update_gold_animation()     # 更新黄金色块动画
            self.update_diamond_animation()  # 更新钻石色块动画
            self.update_colorful_animation() # 更新彩色色块动画
            self.update_pearl_animation()    # 更新珍珠色块动画
            self.draw()
            clock.tick(60)  # 60 FPS
        
        logger.info("游戏结束")
        pygame.quit()
        sys.exit()

def main():
    """主函数"""
    try:
        game = MatchThreeGame()
        game.run()
    except Exception as e:
        logger.error(f"游戏运行错误: {e}")
        pygame.quit()
        sys.exit(1)

if __name__ == "__main__":
    main() 