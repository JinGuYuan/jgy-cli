#!/usr/bin/env python3
"""终端版合成大饺子 - 纯命令行实现"""
import random
import os
import sys
from typing import List, Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# 饺子类型
DUMPLINGS = [
    {"name": "素什锦", "emoji": "🥬", "level": 1, "color": "green"},
    {"name": "西红柿蛋", "emoji": "🍅", "level": 2, "color": "red"},
    {"name": "猪肉白菜", "emoji": "🥬", "level": 3, "color": "white"},
    {"name": "猪肉韭菜", "emoji": "🌿", "level": 4, "color": "green"},
    {"name": "猪肉香菇", "emoji": "🍄", "level": 5, "color": "yellow"},
    {"name": "三鲜", "emoji": "🦐", "level": 6, "color": "cyan"},
    {"name": "香辣牛肉", "emoji": "🌶️", "level": 7, "color": "red"},
    {"name": "孜然羊肉", "emoji": "🥩", "level": 8, "color": "magenta"},
    {"name": "青瓜鲜虾", "emoji": "🦐", "level": 9, "color": "blue"},
    {"name": "饺子王", "emoji": "👑", "level": 10, "color": "gold"},
]

class TerminalGame:
    def __init__(self):
        self.board: List[Optional[dict]] = [None] * 16  # 4x4 格子
        self.score = 0
        self.console = Console() if RICH_AVAILABLE else None
        self.next_dumpling = self._random_dumpling()
        
    def _random_dumpling(self) -> dict:
        """随机生成一个饺子，低级概率高"""
        weights = [40, 30, 20, 10]  # 1-4级概率
        level = random.choices([1, 2, 3, 4], weights=weights)[0]
        return DUMPLINGS[level - 1].copy()
    
    def _clear_screen(self):
        """清屏"""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def _draw_board(self):
        """绘制游戏板"""
        self._clear_screen()
        
        # 标题
        if self.console:
            self.console.print(Panel.fit(
                "🥟 合成大饺子 - 终端版\n"
                "相同饺子相邻会自动合成！",
                title="金谷园饺子馆",
                border_style="yellow"
            ))
        else:
            print("=" * 40)
            print("     🥟 合成大饺子 - 终端版")
            print("     金谷园饺子馆")
            print("=" * 40)
        
        # 分数和下一个
        next_info = f"下一个: {self.next_dumpling['emoji']} {self.next_dumpling['name']}"
        score_info = f"分数: {self.score}"
        
        if self.console:
            self.console.print(f"[cyan]{score_info}[/cyan]    [green]{next_info}[/green]")
            print()
        else:
            print(f"{score_info}    {next_info}")
            print()
        
        # 游戏板
        self._print_grid()
        
        # 操作提示
        print()
        if self.console:
            self.console.print("[dim]操作: 1-16选择位置, q退出[/dim]")
        else:
            print("操作: 1-16选择位置, q退出")
    
    def _print_grid(self):
        """打印格子"""
        if self.console:
            # 使用 rich 表格
            from rich.table import Table
            table = Table(show_header=False, box=box.ROUNDED)
            
            for i in range(4):
                row = []
                for j in range(4):
                    idx = i * 4 + j
                    cell = self.board[idx]
                    if cell:
                        content = f"{cell['emoji']}\n{cell['name']}"
                        row.append(content)
                    else:
                        row.append(f"[{idx+1}]")
                table.add_row(*row)
            
            self.console.print(table)
        else:
            # 纯文本版本
            print("+--------+--------+--------+--------+")
            for i in range(4):
                row = "|"
                for j in range(4):
                    idx = i * 4 + j
                    cell = self.board[idx]
                    if cell:
                        content = f" {cell['emoji']}{cell['name'][:4]} "
                    else:
                        content = f"  [{idx+1:2d}]  "
                    row += content + "|"
                print(row)
                print("+--------+--------+--------+--------+")
    
    def _place_dumpling(self, pos: int) -> bool:
        """放置饺子到指定位置"""
        if pos < 0 or pos >= 16:
            return False
        if self.board[pos] is not None:
            return False
        
        self.board[pos] = self.next_dumpling
        self.next_dumpling = self._random_dumpling()
        
        # 检查合成
        self._check_merge()
        
        return True
    
    def _check_merge(self):
        """检查相邻相同饺子并合成"""
        merged = True
        while merged:
            merged = False
            # 检查水平相邻
            for i in range(4):
                for j in range(3):
                    idx1 = i * 4 + j
                    idx2 = i * 4 + j + 1
                    if self._try_merge(idx1, idx2):
                        merged = True
            
            # 检查垂直相邻
            for i in range(3):
                for j in range(4):
                    idx1 = i * 4 + j
                    idx2 = (i + 1) * 4 + j
                    if self._try_merge(idx1, idx2):
                        merged = True
    
    def _try_merge(self, idx1: int, idx2: int) -> bool:
        """尝试合并两个位置的饺子"""
        d1 = self.board[idx1]
        d2 = self.board[idx2]
        
        if d1 and d2 and d1['level'] == d2['level'] and d1['level'] < 10:
            # 合成！
            new_level = d1['level'] + 1
            self.board[idx1] = DUMPLINGS[new_level - 1].copy()
            self.board[idx2] = None
            
            # 计分
            points = new_level * 10
            self.score += points
            
            # 显示合成信息
            if self.console:
                self.console.print(f"[yellow]✨ 合成 {self.board[idx1]['name']}! +{points}分[/yellow]")
            else:
                print(f"✨ 合成 {self.board[idx1]['name']}! +{points}分")
            
            return True
        return False
    
    def _is_game_over(self) -> bool:
        """检查游戏是否结束"""
        return None not in self.board
    
    def _show_game_over(self):
        """显示游戏结束"""
        if self.console:
            self.console.print(Panel.fit(
                f"🎉 游戏结束！\n\n"
                f"最终得分: [bold yellow]{self.score}[/bold yellow]\n\n"
                f"最高饺子: {self._get_highest_dumpling()}",
                title="金谷园饺子馆",
                border_style="red"
            ))
        else:
            print("\n" + "=" * 40)
            print("           🎉 游戏结束！")
            print(f"         最终得分: {self.score}")
            print(f"         最高饺子: {self._get_highest_dumpling()}")
            print("=" * 40)
    
    def _get_highest_dumpling(self) -> str:
        """获取最高级饺子"""
        max_level = 0
        max_name = "无"
        for cell in self.board:
            if cell and cell['level'] > max_level:
                max_level = cell['level']
                max_name = cell['name']
        return max_name
    
    def run(self):
        """主循环"""
        while True:
            self._draw_board()
            
            if self._is_game_over():
                self._show_game_over()
                input("\n按回车键退出...")
                break
            
            try:
                choice = input("\n选择位置 (1-16) 或 q 退出: ").strip().lower()
                
                if choice == 'q':
                    print("感谢游玩！")
                    break
                
                pos = int(choice) - 1
                if not self._place_dumpling(pos):
                    print("❌ 无效位置，请重试")
                    input("按回车继续...")
                    
            except ValueError:
                print("❌ 请输入数字 1-16 或 q")
                input("按回车继续...")


def main():
    """入口函数"""
    game = TerminalGame()
    game.run()


if __name__ == "__main__":
    main()
