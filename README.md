# crawloop
基于PlayWright实现对js渲染的动态网页进行抓取，包含网页源码、截图、网站入口、网页交互过程等，支持优先级任务调度。

crawloop 目前支持一下特性
- 原生浏览器环境，支持chrome、firefox，协程处理调度任务
- 完整DOM事件收集，自动化触发
- 全面分析收集，包括js文件，页面源码、网站截图、网站图标、标题、编码、cookies、重定向链等等
- 支持Host绑定，可自定义添加Referer
- 支持请求代理，支持爬虫结果主动回调



### 环境（Docker）
- Docker 18.03+
- Postgresl 9.x+
- Rabbitmq 3.8.x+
- Docker Compose 1.24+


## 架构

Crawloop的架构包括了一个主节点（Master Node）和多个工作节点（Worker Node），以及负责通信和数据储存的gRPC和Postgresql数据库。

![](http://static-docs.crawlab.cn/architecture.png)
(上图架构有所变化，Mongo改为Postgresl，Redis改为rabbitMq)

客户端应用向主节点请求数据，主节点通过Celery和Rabbitmq来执行任务派发调度以及负载均衡，工作节点收到任务之后，开始执行爬虫任务，并将任务结果通过gRPC回调给主节点，之后落库存储。


主节点是整个Crawlab架构的核心，属于Crawlab的中控系统。

主节点主要负责以下功能:
1. 周期性任务调度
2. 工作节点管理和通信
3. 对外API服务

主节点负责与客户端进行通信，并通过Celery将爬虫任务基于负载均衡算法异步派发给工作节点。

### 工作节点

工作节点的主要功能是执行爬虫任务和回调抓取数据与日志，并且通过gRPC跟主节点通信。通过增加工作节点数量，Crawloop可以做到横向扩展，不同的爬虫任务可以分配到不同的节点上执行。
