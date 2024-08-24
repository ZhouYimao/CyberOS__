# 目标实现

## 文件位置+实现功能

```/data/schema/config.json``` 对用户信息的读取和修改

```/data/schema/todo.json``` 对行程信息的读取和修改

```/io/loader.py``` 载入 message 、图片、语音等等

```React_agent.py``` 动态绑定导入的数据库，更新对话数量(THREAD_ID) ，在thread内创建消息

1. 登录: 短信验证 Google Github …

2. 获得可以唯一标识用户的数据: 手机号 google id / github id

3. 利用上述方式创建一个用户列表: 自己创建一个uuid给用户

   数据库示例：

    | Id | telephone_num | github_id | google_id | uuid        |
    |---|---------------|-----------|-----------|-------------|
    | 1 | 1111112       | null      | null      | 199-484-163 |
    | 2 | null          | 0058      | null      | 179-444-187 |
    | 3 | 118181        | 11191     | null      | 166-151-849 |

4. 登陆之后生成一个JWT的加密信息 包含{ 用户uuid 姓名}

5. 用户保存这个信息,前端发送请求时带上JWT的token

eg :用户发送请求后端message
{在thread内创建消息 POST https://api.emagen.cn/v1/threads/{thread_id}/messages }

数据库中存有thread_id -> user uuid 的关联表

后端解析JWT 获取用户uuid

判断uuid ?= 数据库中对应的uuid，若不是则403

若是，则继续请求

由于现在申请上述认证方式需要一些企业信息之类的，现在先用Jaccount做认证

即前端呈现为一个界面，上面有一个按钮，按下按钮后跳转jaccount登录，登录成功后返回到另一个页面，后端将得到学生学号，姓名这些unique的数据，用来第三步的创建过程

1. 为给定的聊天对话创建模型响应(在thread之外) 。

(1) url：```post https://api.emagen.cn/v1/chat/completions```

JWT、+用户输入信息+agent回复信息+metadata

(2) GPT中该部分相应post请求发送实例：

```
curl https://api.openai.com/v1/chat/completions \

-H "Content-Type: application/json" \

-H "Authorization: Bearer $OPENAI_API_KEY" \

-d 
'{
    "model": "gpt-4o",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Hello!"
        }
    ]
}'
```

(3) GPT 中该 API 执行完成的返回结果
```
{
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": 1677652288,
    "model": "gpt-4o-mini",
    "system_fingerprint": "fp_44709d6fcb",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "\n\nHello there, how may I assist you
                today?",
            },
            "logprobs": null,
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 9,
        "completion_tokens": 12,
        "total_tokens": 21
    }
}
```

2. 上传各种文件

直接在路径末尾加一个表示文件格式的路径参数

(1) Create upload

```POST https://api.emagen.cn/v1/uploads```

请求体包含 THREAD_ID 和 JWT

请求示例:

```
curl https://api.openai.com/v1/uploads \

-H "Authorization: Bearer $OPENAI_API_KEY" \

-d
'{
    "purpose": "fine-tune",
    "filename": "training_examples.jsonl",
    "bytes": 2147483648,
    "mime_type": "text/jsonl"
}'
```

Response 示例 (用户那里存一份 upload_id，后端那里也存 user_id 和 upload_id 并把他俩进行绑定，之后能用来校验

```
{
    "id": "upload_abc123",
    "object": "upload",
    "bytes": 2147483648,
    "created_at": 1719184911,
    "filename": "training_examples.jsonl",
    "purpose": "fine-tune",
    "status": "pending",
    "expires_at": 1719127296
}
```

(2) Add upload part

```POST https:// api.emagen.cn /v1/uploads/{upload_id}/parts```

请求体包含 THREAD_ID 和 JWT，路径参数中的 upload_id 是每个上传部分都会有的

请求示例

```
curl https://api.openai.com/v1/uploads/upload_abc123/parts

-H "Authorization: Bearer $OPENAI_API_KEY"\

-F data="aHR0cHM6Ly9hcGkub3BlbmFpLmNvbS92MS91cGxvYWRz..."
```

Response示例

```
{
    "id": "part_def456",
    "object": "upload.part",
    "created_at": 1719185911,  # 创建时间
    "upload_id": "upload_abc123"  # 上传文件的id
}
```

(3) Complete upload

```POST https:// api.emagen.cn /v1/uploads/{upload_id}/complete```

请求体包含 THREAD_ID 和 JWT，该 api 是确认是否上传完成

```
curl https://api.openai.com/v1/uploads/upload_abc123/complete

-d
'{
    "part_ids": ["part_def456", "part_ghi789"]
}'

{
    "id": "upload_abc123",
    "object": "upload",
    "bytes": 2147483648,
    "created_at": 1719184911,
    "filename": "training_examples.jsonl",
    "purpose": "fine-tune",
    "status": "completed",
    "expires_at": 1719127296,
    "file": {
        "id": "file-xyz321",
        "object": "file",
        "bytes": 2147483648,
        "created_at": 1719186911,
        "filename": "training_examples.jsonl",
        "purpose": "fine-tune"
    }
}
```

(4) Cancel upload

```POST https:// api.emagen.cn /v1/uploads/{upload_id}/cancel```
```
curl https://api.openai.com/v1/uploads/upload_abc123/cancel

{
    "id": "upload_abc123",
    "object": "upload",
    "bytes": 2147483648,
    "created_at": 1719184911,
    "filename": "training_examples.jsonl",
    "purpose": "fine-tune",
    "status": "cancelled",
    "expires_at": 1719127296
}
```

3. 创建、检索、删除 thread

(1) 创建 thread

```POST https://api.emagen.cn/v1/threads```

JWT

请求示例：

```
curl https://api.openai.com/v1/threads \

-H "Content-Type: application/json" \

-H "Authorization: Bearer $OPENAI_API_KEY" \

-H "OpenAI-Beta: assistants=v2" \

-d ''
```
response 示例 数据库那里存一份 thread_id 和 user_id，方便之后进行校验
```
{
    "id": "thread_abc123",
    "object": "thread",
    "created_at": 1699012949,
    "metadata": {},
    "tool_resources": {}
}
```

(2) 检索线程

```GET https:// api.emagen.cn /v1/threads/{THREAD_ID}```

JWT

该功能是为了获得 thread 对象，即与该 thread 有关的信息

请求示例
```
curl
https://api.openai.com/v1/threads/thread_abc123 \

-H
"Content-Type: application/json" \

-H
"Authorization: Bearer $OPENAI_API_KEY" \

-H
"OpenAI-Beta: assistants=v2"
```

response示例
```
{
    "id": "thread_abc123",
    "object": "thread",
    "created_at": 1699014083,
    "metadata": {},
    "tool_resources": {
        "code_interpreter": {
            "file_ids": []
        }
    }
}
```

(3) 删除 thread

```DELETE https://api.emagen.cn/v1/threads/{thread_id}```

JWT

请求示例
```
curl https://api.openai.com/v1/threads/thread_abc123 \

-H "Content-Type: application/json" \

-H "Authorization: Bearer $OPENAI_API_KEY" \

-H "OpenAI-Beta: assistants=v2" \

-X DELETE
```
response 示例
```
{
    "id": "thread_abc123",
    "object": "thread.deleted",
    "deleted": true
}
```
4. Message

(1) 在 thread 内创建消息

```POST https://api.emagen.cn/v1/threads/{thread_id}/messages```

数据库也存一份 thread_id
-> user.uuid

(2) 列出消息

```GET https:// api.emagen.cn /v1/threads/{thread_id}/messages```

请求体参数包含 USER_ID，还可选填起始时间截止时间、消息的数量等等

(3) 检索和删除某一条特定的消息

```
GET https://api.emagen.cn/v1/threads/{thread_id}/messages/{message_id}

DELETE https://api.emagen.cn/v1/threads/{thread_id}/messages/{message_id}
```
5. 用户信息和 todo

(1) 获取
```
GET https:// api.emagen.cn /v1/memory/config

GET https:// api.emagen.cn /v1/memory/todo
```
Memgpt 的应该是 https://memgpt.ai/api/agent/{agent_id}/memory

问 GPT 说上面的 GET 是即时记忆，下面的是存档记忆

(2) 更新
```
POST https://api.emagen.cn/v1/memory/config
DELETE https://api.emagen.cn/v1/memory/config

POST https://api.emagen.cn/v1/memory/todo
DELETE  https://api.emagen.cn/v1/memory/todo
```















 





 





 