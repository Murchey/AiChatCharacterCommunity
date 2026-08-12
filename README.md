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
        ├── ProfilePicture.jpg   # 角色头像（可选）
        ├── ProfileBackground.jpg# 角色详情页背景图（可选）
        └── moments/             # 朋友圈内容（可选，结构见「moments 文件夹说明」）
            ├── moments.json     # 朋友圈记录
            └── files/           # 朋友圈图片
                ├── 01.jpg
                └── ...
```

### 步骤

1. 在 `Sample1` 下新建一个文件夹，文件夹名即角色显示名（如 `爱弥斯`）；
2. 在文件夹内新建 `Profile.json`，填入角色资料；
3. （可选）新建 `Prompt.txt` 写入角色人设提示词；
4. （可选）放入头像图片 `ProfilePicture.jpg`（支持 jpg / jpeg / png / webp / gif / bmp，缺省时取角色目录内第一个图片文件）；
5. （可选）放入背景图 `ProfileBackground.jpg`（角色详情页封面背景图，缺省时详情页显示默认渐变）；
6. （可选）新建 `moments` 文件夹写入角色的朋友圈内容（格式见「moments 文件夹说明」）；
7. 将整个 `Sample1` 文件夹压缩为 zip；
8. 在 App 中进入 **【我】→ 导入角色包**，选择该 zip 并勾选要导入的角色。

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
| `background` | 内嵌背景图（base64 字符串，存在时优先于 `ProfileBackground.jpg`） | 可选 |

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

### moments 文件夹说明（朋友圈）

角色包中可选的 `moments` 文件夹用于承载角色的**朋友圈内容**，结构与聊天记录导出包类似：`moments.json` 记录动态（文案 / 点赞 / 评论），`files/` 目录存放动态引用的图片。

```
moments/
├── moments.json   # 朋友圈记录（必填）
└── files/         # 朋友圈图片（由 images 相对路径引用）
    ├── 01.jpg
    └── ...
```

`moments.json` 根对象包含 `character_name`（角色名）与 `moments` 数组，数组内按时间倒序（新在前）排列各条动态：

| 字段 | 说明 |
| ---- | ---- |
| `character_name` | 角色名（根对象） |
| `moments` | 动态数组（根对象） |
| `id` | 动态唯一标识（可选，缺省自动生成） |
| `content` | 朋友圈正文文案 |
| `images` | 图片相对路径数组，如 `["files/01.jpg"]`，对应 `files/` 目录下的图片文件（可选） |
| `likes` | 点赞昵称数组，如 `["千咲","琳奈"]`（可选） |
| `comments` | 评论数组，每条为 `{"sender":"昵称","content":"评论内容"}`（可选） |
| `created_at` | 发布时间（ISO 8601 字符串，可选） |

`Sample1\爱弥斯\moments\moments.json` 示例：

```json
{
    "character_name": "爱弥斯",
    "moments": [
        {
            "id": "m1",
            "content": "这小手机怎么这么好玩~睡觉耽误玩手机，玩手机耽误睡觉。",
            "images": ["files/01.jpg"],
            "likes": ["千咲", "琳奈", "漂泊者"],
            "comments": [
                { "sender": "爱弥斯她老冯", "content": "不许玩了，快睡觉" },
                { "sender": "琳奈", "content": "姐们你太坑了" }
            ],
            "created_at": "2026-08-11T23:00:00.000"
        },
        {
            "id": "m2",
            "content": "老爹老妈的合影~还有老妈和我的合影~",
            "images": ["files/02.jpg", "files/03.jpg"],
            "likes": ["漂泊者", "千咲", "莫宁", "琳奈", "西格莉卡"],
            "comments": [
                { "sender": "莫宁", "content": "漂泊者这身很漂亮" }
            ],
            "created_at": "2026-08-05T22:30:00.000"
        }
    ]
}
```

- 图片文件支持 jpg / jpeg / png / webp / gif / bmp，放在 `files/` 目录下，由 `images` 字段以 `files/xxx.jpg` 的相对路径引用；单条动态最多展示 **9 张**（超出部分截断），1 张为大图、多张按 3 列网格排列（对齐微信朋友圈）；
- 没有 `moments` 文件夹时角色无朋友圈内容，详情页朋友圈区域显示空态；
- 文本文件建议使用 UTF-8 编码（与角色包其他文件一致）。

### 注意事项

- 文本文件建议使用 **UTF-8** 编码；程序对 GBK 乱码有兼容处理，但建议统一 UTF-8；
- zip 中**必须**包含至少一个带 `Profile.json` 的角色文件夹，否则会被过滤；
- 文件层级不要过深：`Sample1\角色A\Profile.json` 即可，不要把文件直接放在 zip 根目录。