# Agent

## 核心

1. 函数MECE
2. Claude：注意命名规范、伪代码
3. 记忆 → 搜索 → 行动
4. 流程DAG（有向无环图），让Claude对代码生成Mermaid （JS渲染图的语言）
5. 文本文件模态能跑就行、时间和成功率无所谓，反正该记的该想的都弄完了
   1. 记住有turbo time这个东西：大的而非小的整合

## 潜在阻尼

1. Nebula原生操作，为了后续兼容性和拓展性还是直接上吧，别集成llamaindex了，但思路是可以借鉴的 - 倒也不是不行，llamaindex支持太好了，有属性图和各种查询，关键是有知识提取，太方便了

   1. https://www.llamaindex.ai/blog/introducing-the-property-graph-index-a-powerful-new-way-to-build-knowledge-graphs-with-llms
   2. 让Claude来写

2. Nebula的连接，网络问题

   1. 无太大所谓

3. 传统RAG的方法，PageRank等重排序

   1. 直接抄作业

   2. https://x.com/VoidAsuka/status/1818322857925251409

      [NebulaGraph&AdventrureX.pdf](https://prod-files-secure.s3.us-west-2.amazonaws.com/9a646d1f-bcca-4f33-8efa-1cbee7c50761/e44e3e24-14a5-43ce-8264-481bbabbd008/NebulaGraphAdventrureX.pdf)

   3. 也可以先不管，能把vector search返回的不是chunk，而是图中的node，然后可以从这个node开始进行遍历，返回topk nodes以及它们邻接节点或n度节点的数据的。实现就行

4. 结构化输出、动作、序号啥的

   1. 参考ai搜索的prompt

5. metadata

   1. 翻笔记，从增加广谱召回率的角度考虑
   2. 不用加新东西了，跑起来再说

## 函数

> 所有@tool可以被用户动态绑定，记忆除外 也可以强制调用 mem和search还有todo都需要有引用

1. 增添@tool

​	def **判断**增删改记忆（input:记忆内容）：

​	‘’‘

​		需要操作记忆的时候，

​		[补充详尽的prompt] - 参考童姥

​		初始persona

​	’‘’

​	类似于analysis

​	core_memory -> JSON  (事实驱动)

​	common_memory  ->  prop Graph （事件驱动，时序性，时间绝对化）

2. def core_memory_handler()：**增、改**，直接基于童姥写的改，schema复杂一些就行

3. def memory_handler：增，强制改/删

​		时空		

​		//  先拿要操作的记忆做一个基于nGQL（2/3）的匹配，如果相关（有矛盾）就返回给agent更新

​		状态0:没有就记录

​		如果拿到了要删除记忆的状态，那就nGQL查或者text2或者直接向量，然后让模型和用户确认、删除

4. def memory_loader ：载入common_memory,  、RA、从Graph里load

   

5. @tool

   判断

   todolist的增、删。改：1. 事件本身内容上改；2. 大事件拆分子任务的小状态改动

   def todo检查器，**先判断**是否有todo的操作，同判断记忆

​	   def todo handler（增删改查todo，规划小todo）

​		def 检查子任务状态、协作方式（**待尝试**）和enum自身工具，然后给agent

​		

​		def todo 拆分 子任务	

​		结合个性特征、当前 - 详情参考笔记，来搞一个

​		根据对话中提取到的点提取出to do list , 事情内容 /(时间，人物，地点)。

​		拆分、判断：大事件的子人物步骤；

​		PaE :

​		状态：init->step1-> step2

7. @tool

​		def 简单搜索

​		搜索网络信息

8. @tool

​		def global 探索 - 抄

​		https://github.com/Yusuke710/nanoPerplexityAI/blob/main/nanoPerplexityAI.py

9. solid def 统一文件、文档解析+rag（HIL，全文、段落摘录？还没想好呢，先把flomorag做好吧）

​	对话中。直接用langchain/index自带的rag，效果说不定会很好，确实很适合

​	https://x.com/llama_index/status/1816195731826565586

​	收藏时，可以先语义切块成flomo，然后flomo_rag()

10. solid def flomo rag ，按照小本本上的来（保存的时候）



// def url爬虫，递归的，用户选择爬哪些

// solid def 裁剪（有个移动窗口）消息

11. def 内存管理器 + 内心独白

​	**放进去指令、人设、核心记忆/核心特征、根据会话作GraphRAG load一些上来 、TodoList(SystemMessage) **

​	global memory：关于用户的核心特征（LPA）用json，在turbotime的时候检查，其他事件、回忆都放到graph里，有时间作为	metadata的graph，颜色衰退、graphrag、当前工作任务状态

一定要有独白/思考过程？ ： 核心记忆、graphrag和大任务作为前置假设、推理思考、意图识别

12. @def 决策器：帮助用户更好地决策，

    查todo//

​		判断是交给人类的，只是提供分析、推理（传统cs50ai那一套、定性定量研究）等

13. def 并行调度器（当 tool>2 时，前后台、compiler异步并行）**（等待）**

​		这个巨他妈重要和科幻

14. def 处理不确定结果时（收到上一条消息，然后返回序列）

​		LangGraph的breakpoints：https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/breakpoints/

​		agent不确定时（HIL，自省知之、工作Log判断）：确定、选择、填空 - 还有主动追问（越前面人类越能偷懒）
