# GitHub Actions Release 工作流

## 概述

本工作流会在 **push 到 main 分支且 Characters 目录有变化时** 自动触发，为每个角色创建单独的 zip 包并上传到 GitHub Release。**文件名会自动从拼音重命名为中文**。

## 工作流程

```
┌─────────────────────────────────────────────────────────────┐
│ 1. push 到 main 分支                                        │
│    （Characters/ 目录有变化）                                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Build Job                                                │
│    - 扫描 Characters/ 目录                                   │
│    - 为每个角色创建 zip 包（文件名使用拼音）                   │
│    - 上传到 GitHub Artifacts                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Release Job                                              │
│    - 下载 Artifacts                                          │
│    - 创建 GitHub Release                                     │
│    - 通过 GitHub API 将文件名重命名为中文                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 最终结果                                                 │
│    Release 中的文件名：阿米娅（Amiya）.zip                    │
└─────────────────────────────────────────────────────────────┘
```

## 快速开始

### 自动触发

当您 push 到 main 分支且 Characters 目录有变化时，工作流会自动触发：

```bash
# 修改角色内容后
git add Characters/
git commit -m "Update character"
git push origin main
```

### 手动触发

也可以在 GitHub 仓库的 Actions 页面手动触发：

1. 进入 GitHub 仓库的 Actions 页面
2. 选择 "Release Character Packages" 工作流
3. 点击 "Run workflow"

### 生成的文件

**打包时（拼音文件名）**：
- `AYuanAnJieLiNa_AngelinatheOathkeeper.zip`
- `AMiYa_Amiya.zip`
- `JianMoDeKeSaSi_TexastheOmertosa.zip`

**发布后（中文文件名）**：
- `予愿安洁莉娜（Angelina the Oathkeeper）.zip`
- `阿米娅（Amiya）.zip`
- `缄默德克萨斯（Texas the Omertosa）.zip`

## 工作流配置

工作流文件位置：`.github/workflows/release.yml`

### 触发条件

```yaml
on:
  push:
    branches:
      - main  # push 到 main 分支时触发
    paths:
      - 'Characters/**'  # 只有 Characters 目录下的文件变化才触发
  workflow_dispatch:  # 允许手动触发
```

### 包含条件

只有满足以下条件的角色目录才会被打包：

1. 位于 `Characters/{游戏名}/` 目录下
2. 包含 `Profile.json` 文件

### 打包逻辑

- 每个角色单独打包成一个 zip 文件
- zip 文件名使用驼峰拼音（如 `AMiYa_Amiya.zip`）
- zip 包内保留中文原名（如 `阿米娅（Amiya）/Profile.json`）
- 发布后通过 GitHub API 重命名为中文

## Release 描述

自动生成的 Release 描述包含：

- 角色包列表（拼音文件名）
- 使用方法
- 注意事项

## 常见问题

### Q: 为什么某些角色没有被打包？

A: 只有包含 `Profile.json` 的角色目录才会被打包。请检查角色目录是否包含此文件。

### Q: 文件名为什么会从拼音变成中文？

A: GitHub Actions 打包时不支持中文文件名，所以先使用拼音。发布后通过 GitHub API 自动重命名为中文。

### Q: 如何修改 Release 的描述？

A: 编辑工作流文件中的 `release_notes.md` 生成逻辑。

### Q: 如何跳过某些角色？

A: 可以在工作流中添加过滤条件，例如：

```yaml
# 只打包特定游戏
for game_dir in Characters/Arknights/; do
  # ...
done

# 或排除特定角色
if [[ "$char_name" != "测试角色"* ]]; then
  # ...
fi
```

### Q: 如何手动触发工作流？

A: 工作流已配置 `workflow_dispatch` 触发器，可以在 GitHub 仓库的 Actions 页面手动运行。

## 文件结构

```
.github/
├── workflows/
│   ├── release.yml          # 主工作流
│   └── README.md            # 工作流说明
└── scripts/
    └── to_camel.py          # 拼音转换脚本
```

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
