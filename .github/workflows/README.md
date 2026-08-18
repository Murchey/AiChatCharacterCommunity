# Release 工作流使用说明

## 自动打包角色包

当你推送一个以 `v` 开头的 tag 时，GitHub Actions 会自动：

1. 遍历 `Characters/` 目录下的所有游戏和角色
2. 为每个有 `Profile.json` 的角色创建单独的 zip 包
3. 生成 Release 并上传所有角色包

## 使用方法

### 1. 创建 Tag

```bash
# 创建一个 v 开头的 tag
git tag v1.0.0

# 推送 tag 到 GitHub
git push origin v1.0.0
```

或者创建带注释的 tag：

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### 2. 自动触发

推送 tag 后，GitHub Actions 会自动：

1. 检查 `Characters/` 下的所有角色目录
2. 找到所有包含 `Profile.json` 的角色文件夹
3. 为每个角色创建 zip 包（文件名为 `角色名.zip`）
4. 创建 GitHub Release 并上传所有 zip 文件

### 3. Release 内容

每个 Release 包含：

- **Release 标题**：`Character Release {tag名}`
- **Release 描述**：角色包列表和使用说明
- **附件**：所有角色的 zip 包（文件名为 `中文名（英文名）.zip`）

## 目录结构示例

```
Characters/
├── Arknights/
│   ├── 阿米娅（Amiya）/
│   │   ├── Profile.json
│   │   ├── Prompt.txt
│   │   └── moments/
│   └── 缄默德克萨斯（Texas the Omertosa）/
│       ├── Profile.json
│       └── ...
├── WutheringWaves/
│   └── 爱弥斯（Aemeath）/
│       └── ...
└── HonkaiStarRail/
    └── 银狼（Silver Wolf LV.999）/
        └── ...
```

生成的 zip 文件：

- `阿米娅（Amiya）.zip`
- `缄默德克萨斯（Texas the Omertosa）.zip`
- `爱弥斯（Aemeath）.zip`
- `银狼（Silver Wolf LV.999）.zip`

## 角色包结构

每个 zip 包内的结构：

```
角色名/
├── Profile.json         # 角色资料（必填）
├── Prompt.txt           # 角色提示词（可选）
├── ProfilePicture.jpg   # 角色头像（可选）
├── ProfileBackground.jpg # 角色背景图（可选）
└── moments/             # 朋友圈内容（可选）
    ├── moments.json
    └── files/
        ├── 01.jpg
        └── ...
```

## 注意事项

1. **只有包含 `Profile.json` 的角色目录才会被打包**
2. **zip 文件名使用中文名（英文名）格式**，与角色文件夹名一致
3. **GitHub Releases 支持上传带中文名的文件**
4. **建议使用 UTF-8 编码**的文本文件

## 手动触发（可选）

如果需要手动触发 release，可以修改 `.github/workflows/release.yml` 的触发条件：

```yaml
on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:  # 添加这一行，允许手动触发
```

## 调试

如果需要查看工作流的执行日志：

1. 进入 GitHub 仓库页面
2. 点击 `Actions` 标签
3. 选择对应的工作流运行
4. 查看每个步骤的详细日志

## 常见问题

### Q: 为什么某些角色没有被打包？

A: 只有包含 `Profile.json` 文件的角色目录才会被打包。检查角色目录是否包含这个文件。

### Q: zip 文件名中的中文字符会显示乱码吗？

A: GitHub Releases 支持上传带中文名的文件，下载后文件名会正确显示。

### Q: 如何修改 Release 的描述？

A: 编辑 `.github/workflows/release.yml` 中的 `release_notes.md` 生成逻辑。

### Q: 如何跳过某些角色？

A: 可以在工作流中添加过滤条件，例如只打包特定游戏或特定目录下的角色。
