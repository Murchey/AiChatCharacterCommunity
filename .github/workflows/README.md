# GitHub Actions Release 工作流

## 概述

**每次 push 到 main 分支时**，自动同时生成两种打包模式：
- **按游戏分类**：每个游戏一个 zip，包含该游戏下的所有角色
- **按角色分类**：每个角色一个 zip

两种打包结果放在同一个 Release 中。

## 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│ 1. push 到 main 分支                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. 并行打包                                                 │
│    ┌─────────────────────┐  ┌─────────────────────┐         │
│    │ Build Game          │  │ Build Single        │         │
│    │ 按游戏分类打包       │  │ 按角色分类打包       │         │
│    └─────────────────────┘  └─────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Release Job                                              │
│    - 合并两种打包结果                                         │
│    - 创建 GitHub Release                                     │
│    - 通过 GitHub API 将文件名重命名为中文                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 最终结果                                                 │
│    Release 中包含：                                          │
│    - Arknights.zip（按游戏分类）                             │
│    - 阿米娅（Amiya）.zip（按角色分类）                       │
│    - 缄默德克萨斯（Texas the Omertosa）.zip（按角色分类）    │
│    - ...                                                    │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 自动触发

每次 push 到 main 分支时自动触发：

```bash
git add Characters/
git commit -m "Update character"
git push origin main
```

### 手动触发

也可以在 GitHub 仓库的 Actions 页面手动触发：

1. 进入 GitHub 仓库的 Actions 页面
2. 选择 "Release Character Packages" 工作流
3. 点击 "Run workflow"

## 生成的文件

### 按游戏分类

- `Arknights.zip` - 包含所有明日方舟角色
- `WutheringWaves.zip` - 包含所有鸣潮角色
- `HonkaiStarRail.zip` - 包含所有星铁角色
- `ArknightsEndfield.zip` - 包含所有终末地角色
- `VTuber.zip` - 包含所有 VTuber 角色

### 按角色分类

- `阿米娅（Amiya）.zip`
- `缄默德克萨斯（Texas the Omertosa）.zip`
- `予愿安洁莉娜（Angelina the Oathkeeper）.zip`
- `爱弥斯（Aemeath）.zip`
- ...

## 工作流配置

### 触发条件

```yaml
on:
  push:
    branches:
      - main  # push 到 main 分支时触发
  workflow_dispatch:  # 允许手动触发
```

### 打包规则

- 只有包含 `Profile.json` 的角色目录才会被打包
- 两种打包模式并行执行，提高效率
- 所有结果放在同一个 Release 中

## 文件名转换

| 中文名 | 拼音文件名（打包时） | 中文文件名（发布后） |
|--------|---------------------|---------------------|
| 予愿安洁莉娜（Angelina the Oathkeeper） | YuYuanAnJieLiNa_AngelinatheOathkeeper.zip | 予愿安洁莉娜（Angelina the Oathkeeper）.zip |
| 阿米娅（Amiya） | AMiYa_Amiya.zip | 阿米娅（Amiya）.zip |
| Arknights | Arknights.zip | Arknights.zip |

## 文件结构

```
.github/
├── workflows/
│   ├── release.yml          # 主工作流
│   └── README.md            # 工作流说明
└── scripts/
    └── to_camel.py          # 拼音转换脚本
```

## 调试

如果重命名没有生效，请检查 GitHub Actions 的运行日志：

1. 进入 GitHub 仓库的 Actions 页面
2. 点击最近一次运行的工作流
3. 展开 `Rename release assets to Chinese` 步骤
4. 查看输出信息

## 注意事项

1. **UTF-8 编码**：所有文本文件建议使用 UTF-8 编码
2. **文件层级**：zip 包内的文件层级不要过深
3. **Profile.json**：这是角色包的必需文件
4. **中文文件名**：GitHub Actions 打包时不支持中文，但发布后会自动重命名

## 相关文档

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [GitHub Releases 文档](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [softprops/action-gh-release](https://github.com/softprops/action-gh-release)
- [GitHub API - Update a release asset](https://docs.github.com/en/rest/releases/assets#update-a-release-asset)
