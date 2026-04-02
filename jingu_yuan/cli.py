#!/usr/bin/env python3
"""金谷园饺子馆 CLI"""
import json
import os
import webbrowser
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

console = Console()

# 获取数据目录
DATA_DIR = Path(__file__).parent / "data"
GAME_DIR = Path(__file__).parent / "game"
MENU_FILE = DATA_DIR / "menu.json"


def load_menu():
    """加载菜单数据"""
    with open(MENU_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


@click.group(context_settings=dict(help_option_names=['-h', '--help']))
@click.version_option(version="0.1.3")
def cli():
    """🥟 金谷园饺子馆 - 命令行查询工具
    
    快速查询菜单、价格、推荐菜品，还能玩等位小游戏！
    
    示例:
        jgy menu           # 显示完整菜单
        jgy price 香菇     # 查询价格
        jgy recommend      # 获取推荐
        jgy game           # 玩合成大饺子
    """
    pass


@cli.command()
def info():
    """显示餐厅基本信息"""
    menu = load_menu()
    restaurant = menu["restaurant"]
    
    console.print(Panel.fit(
        f"[bold cyan]{restaurant['name']}[/bold cyan]\n"
        f"[dim]{restaurant['slogan']}[/dim]\n\n"
        f"🕐 营业时间: {restaurant['hours']}\n"
        f"📍 地址: {restaurant['address']}\n"
        f"📞 电话: {restaurant['phone']}",
        title="🥟 欢迎光临",
        border_style="green"
    ))


@cli.command()
@click.option("--category", "-c", help="按类别筛选 (鲜/猪/牛/羊/素)")
@click.option("--price", "-p", is_flag=True, help="按价格排序")
def menu(category: Optional[str], price: bool):
    """显示完整菜单"""
    menu_data = load_menu()
    
    console.print(f"\n[bold cyan]🥟 {menu_data['restaurant']['name']} - 菜单[/bold cyan]\n")
    
    for cat in menu_data["categories"]:
        if category and cat["name"] != category:
            continue
            
        table = Table(
            title=f"[bold]{cat['name']}类[/bold]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold magenta"
        )
        table.add_column("编号", style="dim", width=4)
        table.add_column("品名", style="cyan")
        table.add_column("价格", justify="right", style="green")
        table.add_column("标签", style="yellow")
        
        items = cat["items"]
        if price:
            items = sorted(items, key=lambda x: x["price"])
            
        for item in items:
            tags = " ".join([f"[#{tag}]" for tag in item["tags"]]) if item["tags"] else ""
            table.add_row(
                item["id"],
                item["name"],
                f"¥{item['price']}/{item['unit']}",
                tags
            )
        
        console.print(table)
        console.print()


@cli.command()
@click.argument("keyword")
def price(keyword: str):
    """查询具体菜品价格
    
    示例: jgy price 香菇
    """
    menu_data = load_menu()
    results = []
    
    for cat in menu_data["categories"]:
        for item in cat["items"]:
            if keyword.lower() in item["name"].lower():
                results.append({**item, "category": cat["name"]})
    
    if not results:
        console.print(f"[red]❌ 未找到包含 '{keyword}' 的菜品[/red]")
        console.print("[dim]试试: 猪肉、牛肉、虾、素...[/dim]")
        return
    
    table = Table(title=f"🔍 '{keyword}' 的搜索结果", box=box.ROUNDED)
    table.add_column("品名", style="cyan")
    table.add_column("类别", style="blue")
    table.add_column("价格", style="green", justify="right")
    
    for item in results:
        table.add_row(item["name"], f"{item['category']}类", f"¥{item['price']}/{item['unit']}")
    
    console.print(table)


@cli.command()
@click.option("--type", "-t", 
              type=click.Choice(["first_time", "seafood", "spicy", "light", "meat"]),
              default="first_time",
              help="推荐类型")
@click.option("--people", "-p", default=2, help="用餐人数")
def recommend(type: str, people: int):
    """获取推荐菜品
    
    类型: first_time(首次), seafood(海鲜), spicy(辣味), light(清淡), meat(肉食)
    """
    menu_data = load_menu()
    
    type_names = {
        "first_time": "🌟 首次来店推荐",
        "seafood": "🦐 海鲜爱好者",
        "spicy": "🌶️ 嗜辣推荐",
        "light": "🥗 清淡健康",
        "meat": "🥩 肉食主义"
    }
    
    rec_key = type if type != "seafood" else "seafood_lover"
    recs = menu_data["recommendations"].get(rec_key, [])
    
    # 根据人数调整数量
    count = min(people + 2, len(recs))
    selected = recs[:count]
    
    console.print(f"\n[bold cyan]{type_names.get(type, '推荐')}[/bold cyan]")
    console.print(f"[dim]用餐人数: {people}人[/dim]\n")
    
    # 查找完整信息
    for name in selected:
        for cat in menu_data["categories"]:
            for item in cat["items"]:
                if item["name"] == name:
                    tags = " ".join([f"[#{t}]" for t in item["tags"]])
                    console.print(
                        f"  [green]●[/green] [bold]{item['name']}[/bold] "
                        f"[dim]({cat['name']}类)[/dim] "
                        f"[yellow]¥{item['price']}/{item['unit']}[/yellow] {tags}"
                    )
                    break
    
    # 建议点单量
    total = count * 15  # 假设每样15元
    console.print(f"\n[dim]💡 建议点 {count} 种口味，约 {count*2} 两/人，预估 ¥{total} 起[/dim]")


@cli.command()
def game():
    """启动等位小游戏 - 合成大饺子（终端版）"""
    from .terminal_game import main as game_main
    game_main()


@cli.command()
def tags():
    """按标签浏览菜品"""
    menu_data = load_menu()
    
    # 收集所有标签
    all_tags = {}
    for cat in menu_data["categories"]:
        for item in cat["items"]:
            for tag in item["tags"]:
                if tag not in all_tags:
                    all_tags[tag] = []
                all_tags[tag].append(item["name"])
    
    console.print("\n[bold cyan]🏷️ 标签分类[/bold cyan]\n")
    
    for tag, items in sorted(all_tags.items(), key=lambda x: -len(x[1])):
        console.print(f"[bold yellow]#{tag}[/bold yellow] ({len(items)}款)")
        console.print(f"  {', '.join(items[:5])}{'...' if len(items) > 5 else ''}")
        console.print()


def main():
    """入口点"""
    cli()


if __name__ == "__main__":
    main()