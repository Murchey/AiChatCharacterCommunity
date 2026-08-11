# AiChatCharacterCommunity
AiChat配套的角色卡仓库

## 如何添加角色（以 CharactersImport 为例）

角色包是一个 `.zip` 文件，App 内通过 **【我】→ 导入角色包** 导入。一个 zip 中可以包含多个角色，每个角色是一个独立的文件夹。

项目根目录的 `CharactersImport\Sample1` 就是一份可直接打包成 zip 的示例：

```
CharactersImport/
└── Sample1/
    └── 爱弥斯/                  # 角色文件夹（文件夹名即角色名，可任意命名）
        ├── Profile.json         # 角色资料（必填）
        ├── Prompt.txt           # 角色提示词 / 人设（强烈建议提供）
        └── ProfilePicture.jpg   # 角色头像（可选）
```

### 步骤

1. 在 `Sample1` 下新建一个文件夹，文件夹名即角色显示名（如 `爱弥斯`）；
2. 在文件夹内新建 `Profile.json`，填入角色资料；
3. （可选）新建 `Prompt.txt` 写入角色人设提示词；
4. （可选）放入头像图片 `ProfilePicture.jpg`（支持 jpg / jpeg / png / webp / gif / bmp，取第一个）；
5. 将整个 `Sample1` 文件夹压缩为 zip；
6. 在 App 中进入 **【我】→ 导入角色包**，选择该 zip 并勾选要导入的角色。

### Profile.json 字段说明

| 字段 | 说明 | 是否必填 |
| ---- | ---- | ---- |
| `name` | 角色名称（缺省时使用文件夹名） | 建议 |
| `location` | 所在地（映射到「地区」） | 可选 |
| `gender` | 性别 | 可选 |
| `signature` | 个性签名 | 可选 |
| `remark` | 备注 | 可选 |
| `description` | 角色简介 | 可选 |
| `personality` | 性格特征 | 可选 |
| `greeting` | 开场白 | 可选 |
| `user_relationship` | 与用户的关系 | 可选 |
| `tags` | 标签数组，如 `["鸣潮","电子幽灵"]` | 可选 |
| `avatar` | 内嵌头像（base64 字符串，存在时优先于图片文件） | 可选 |

`Sample1\爱弥斯\Profile.json` 示例：

```json
{
    "name": "爱弥斯",
    "location": "拉海洛·星炬学院",
    "gender": "女",
    "signature": "关注飞行雪绒喵~"
}
```

### Prompt.txt 说明

`Prompt.txt` 的内容就是角色的 `systemPrompt`，App 在每次对话前会把它与用户资料、时间、输出格式指令一起组装成 System Prompt。

参考 `Sample1\爱弥斯\Prompt.txt`：建议写清楚角色**基础身份**、**性格特征**、**说话风格**、**核心记忆与执念**、**注意事项**，让角色行为稳定、性格鲜明。

### 注意事项

- 文本文件建议使用 **UTF-8** 编码；程序对 GBK 乱码有兼容处理，但建议统一 UTF-8；
- zip 中**必须**包含至少一个带 `Profile.json` 的角色文件夹，否则会被过滤；
- 文件层级不要过深：`Sample1\角色A\Profile.json` 即可，不要把文件直接放在 zip 根目录。
