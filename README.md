# 金谷园饺子馆 CLI

🥟 命令行查询工具 - 快速查看菜单、价格、推荐菜品，还能玩等位小游戏！

## 安装

```bash
pip install jinguyuan
```

安装完成后，按提示配置环境变量即可使用。

## 使用方法

```bash
# 查看餐厅信息
jinguyuan info

# 显示完整菜单
jinguyuan menu

# 按类别查看
jinguyuan menu --category 猪

# 查询价格
jinguyuan price 香菇

# 获取推荐
jinguyuan recommend --type first_time --people 3

# 按标签浏览
jinguyuan tags

# 玩等位小游戏
jinguyuan game
```

## 命令列表

| 命令 | 说明 | 示例 |
|------|------|------|
| `info` | 餐厅基本信息 | `jinguyuan info` |
| `menu` | 完整菜单 | `jinguyuan menu -c 鲜` |
| `price` | 查询价格 | `jinguyuan price 虾` |
| `recommend` | 智能推荐 | `jinguyuan recommend -t seafood -p 4` |
| `tags` | 标签分类 | `jinguyuan tags` |
| `game` | 等位小游戏 | `jinguyuan game` |

## 推荐类型

- `first_time` - 首次来店推荐
- `seafood` - 海鲜爱好者
- `spicy` - 嗜辣推荐
- `light` - 清淡健康
- `meat` - 肉食主义

## 开发

```bash
# 本地安装测试
pip install -e .

# 运行
jinguyuan menu
```