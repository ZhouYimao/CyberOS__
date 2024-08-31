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
   
| Id  | telephone_num | github_id | google_id | uuid         |
|-----|---------------|-----------|-----------|--------------|
| 1   | 1111112       | null      | null      | 199-484-163  |
| 2   | null          | 0058      | null      | 179-444-187  |
| 3   | 11818         | 11191     | null      | 166-151-849  |

4. 登陆之后生成一个JWT的加密信息 包含{ 用户uuid 姓名}

5. 用户保存这个信息,前端发送请求时带上JWT的token

eg :用户发送请求后端message
{在thread内创建消息 POST https:// api.emagen.cn /v1/threads/{thread_id}/messages }

数据库中存有 thread_id -> user uuid 的关联表

后端解析 JWT 获取用户 uuid

判断 uuid ?= 数据库中对应的 uuid，若不是则 403

若是，则继续请求

由于现在申请上述认证方式需要一些企业信息之类的，现在先用 jAccount 做认证

即前端呈现为一个界面，上面有一个按钮，按下按钮后跳转 jAccount 登录，登录成功后返回到另一个页面，后端将得到学生学号，姓名这些unique的数据，用来第三步的创建过程

1. 为给定的聊天对话创建模型响应 (在 thread 之外) 。

(1) url: ```POST https://api.emagen.cn/v1/chat/completions```

JWT + 用户输入信息 + agent 回复信息 + metadata

(2) 该部分相应 POST 请求发送实例：

```
curl https://api.emagen.cn/v1/chat/completions \

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

(3) 该 API 执行完成的返回结果

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
                "content": "\n\nHello there, how may I assist you today?"
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

2. 分步上传大文件

直接在路径末尾加一个表示文件格式的路径参数

(1) Create upload

```POST https://api.emagen.cn/v1/uploads```

请求体包含 THREAD_ID 和 JWT

请求示例:

```
curl https://api.emagen.cn/v1/uploads \

-H "Authorization: Bearer $OPENAI_API_KEY" \

-d
'{
    "purpose": "fine-tune",
    "filename": "training_examples.jsonl",
    "bytes": 2147483648,
    "mime_type": "text/jsonl"
}'
```

Response 示例 (用户那里存一份 upload_id, 后端那里也存 user_id 和 upload_id 并把他俩进行绑定，之后能用来校验

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

```POST https://api.emagen.cn/v1/uploads/{upload_id}/parts```

请求体包含 THREAD_ID 和 JWT, 路径参数中的 upload_id 是每个上传部分都会有的

请求示例

```
curl https://api.emagen.cn/v1/uploads/upload_abc123/parts

-H "Authorization: Bearer $OPENAI_API_KEY"\

-H "Content-Type: multipart/form-data"

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

```POST https://api.emagen.cn/v1/uploads/{upload_id}/complete```

请求体包含 THREAD_ID 和 JWT, 该 api 是确认是否上传完成

```
curl https://api.emagen.cn/v1/uploads/upload_abc123/complete

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
curl https://api.emagen.cn/v1/uploads/upload_abc123/cancel

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

3. 直接上传较小文件
（1）上传文件
上传笔记

```POST https://api.emagen.cn/v1/files/markdowns```

JWT
请求示例：

```
curl -X POST https://api.yourdomain.com/v1/files/markdowns \
  -H "Content-Type: multipart/form-data" \
  -H "Authorization: Bearer $YOUR_API_KEY" \
  -F purpose="user-uploaded-markdown" \
  -F "file=@path/to/your/markdown_file.md"
```

response示例

```
{
  "id": "file_123456789",
  "object": "file",
  "bytes": 2048,
  "created_at": 1713226573,
  "filename": "markdown_file.md",
  "purpose": "user-uploaded-markdown"
}
```

上传其他文件

```POST https://api.emagen.cn/v1/files/{file_format}```

JWT
请求示例：

```
curl -X POST https://api.yourdomain.com/v1/files/pdf \
  -H "Content-Type: multipart/form-data" \
  -H "Authorization: Bearer $YOUR_API_KEY" \
  -F purpose="user-uploaded-document" \
  -F "file=@path/to/your/document.pdf"

```

response示例

```
{
  "id": "file_987654321",
  "object": "file",
  "bytes": 4096,
  "created_at": 1713226590,
  "filename": "document.pdf",
  "purpose": "user-uploaded-document"
}

```


（2）列出上传过的文件
```GET https://api.emagen.cn/v1/files```

JWT
请求示例：

```
curl https://api.emagen.cn/v1/files \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

response示例：

```
{
  "data": [
    {
      "id": "file-abc123",
      "object": "file",
      "bytes": 175,
      "created_at": 1613677385,
      "filename": "salesOverview.pdf",
      "purpose": "assistants",
    },
    {
      "id": "file-abc123",
      "object": "file",
      "bytes": 140,
      "created_at": 1613779121,
      "filename": "puppy.jsonl",
      "purpose": "fine-tune",
    }
  ],
  "object": "list"
}
```

（3）检索特定文件的信息
```GET https://api.emagen.cn/v1/files/{file_id}```

请求示例：

```
curl https://api.emagen.cn/v1/files/file-abc123 \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

response示例：

```
{
  "id": "file-abc123",
  "object": "file",
  "bytes": 120000,
  "created_at": 1677610602,
  "filename": "mydata.jsonl",
  "purpose": "fine-tune",
}
```

（4）删除文件
```DELETE https://api.emagen.cn/v1/files/{file_id}```

请求示例：

```
curl https://api.emagen.cn/v1/files/file-abc123 \
  -X DELETE \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

response示例：

```
{
  "id": "file-abc123",
  "object": "file",
  "deleted": true
}
```

4. 创建、检索、删除 thread

(1) 创建 thread

```POST https://api.emagen.cn/v1/threads```

JWT

请求示例：

```
curl https://api.emagen.cn/v1/threads \

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

```GET https://api.emagen.cn/v1/threads/{THREAD_ID}```

JWT

该功能是为了获得 thread 对象，即与该 thread 有关的信息

请求示例

```
curl https://api.emagen.cn/v1/threads/thread_abc123 \

-H "Content-Type: application/json" \

-H "Authorization: Bearer $OPENAI_API_KEY" \

-H "OpenAI-Beta: assistants=v2"
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

```DELETE https://api.emagen.cn/v1/threads/{THREAD_ID}```

JWT

请求示例

```
curl https://api.emagen.cn/v1/threads/thread_abc123 \

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

5. Message

(1) 在 thread 内创建消息

```POST https://api.emagen.cn/v1/threads/{THREAD_ID}/messages```

数据库也存一份 thread_id
-> user.uuid
请求示例

```
curl https://api.emagen.cn/v1/threads/thread_abc123/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
      "role": "user",
      "content": "How does AI work? Explain it in simple terms."
    }'
```

```
reaponse示例：
{
  "id": "msg_abc123",
  "object": "thread.message",
  "created_at": 1713226573,
  "assistant_id": null,
  "thread_id": "thread_abc123",
  "run_id": null,
  "role": "user",
  "content": [
    {
      "type": "text",
      "text": {
        "value": "How does AI work? Explain it in simple terms.",
        "annotations": []
      }
    }
  ],
  "attachments": [],
  "metadata": {}
}
```


(2) 列出消息

```GET https://api.emagen.cn/v1/threads/{THREAD_ID}/messages```

请求体参数包含 USER_ID，还可选填起始时间截止时间、消息的数量等等
请求示例：

```
curl https://api.emagen.cn/v1/threads/thread_abc123/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" 
```

reaponse示例：

```
{
  "object": "list",
  "data": [
    {
      "id": "msg_abc123",
      "object": "thread.message",
      "created_at": 1699016383,
      "assistant_id": null,
      "thread_id": "thread_abc123",
      "run_id": null,
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": {
            "value": "How does AI work? Explain it in simple terms.",
            "annotations": []
          }
        }
      ],
      "attachments": [],
      "metadata": {}
    },
    {
      "id": "msg_abc456",
      "object": "thread.message",
      "created_at": 1699016383,
      "assistant_id": null,
      "thread_id": "thread_abc123",
      "run_id": null,
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": {
            "value": "Hello, what is AI?",
            "annotations": []
          }
        }
      ],
      "attachments": [],
      "metadata": {}
    }
  ],
  "first_id": "msg_abc123",
  "last_id": "msg_abc456",
  "has_more": false
}
```

(3) 检索和删除某一条特定的消息

```GET https://api.emagen.cn/v1/threads/{THREAD_ID}/messages/{MESSAGE_ID}```

请求示例：

```
curl https://api.api.emagen.cn/v1/threads/thread_abc123/messages/msg_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" 
```

response示例：

```
{
  "id": "msg_abc123",
  "object": "thread.message",
  "created_at": 1699017614,
  "assistant_id": null,
  "thread_id": "thread_abc123",
  "run_id": null,
  "role": "user",
  "content": [
    {
      "type": "text",
      "text": {
        "value": "How does AI work? Explain it in simple terms.",
        "annotations": []
      }
    }
  ],
  "attachments": [],
  "metadata": {}
}
```

```DELETE https://api.emagen.cn/v1/threads/{THREAD_ID}/messages/{MESSAGE_ID}```

请求示例：

```
curl -X DELETE https://api.emagen.cn/v1/threads/thread_abc123/messages/msg_abc123 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" 
```

response示例：

```
{
  "id": "msg_abc123",
  "object": "thread.message.deleted",
  "deleted": true
}
```


5. 用户信息和 todo

(1) 获取

```
GET https://api.emagen.cn/v1/memory/config

GET https://api.emagen.cn/v1/memory/todo
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















 





 





 