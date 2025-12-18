# texaspoker

这是一个德州扑克游戏的技术架构雏形目录，基于“在线多人德州扑克系统”的分层设计，涵盖客户端、网关、业务服务与基础设施。当前仅包含架构文档与模块职责说明，便于后续落地实现。

## 目录结构
- `docs/ARCHITECTURE.md`：整体架构说明、交互关系与可扩展性要点。
- `modules/client/`：客户端职责说明。
- `modules/gateway/`：API Gateway 与 Realtime Gateway 说明。
- `modules/services/`：大厅匹配、牌桌管理、游戏逻辑、经济、数据/回放、聊天、防作弊、通知等核心服务说明。
- `infra/`：消息队列、存储缓存、监控可观测性等基础设施说明。

## 后续可扩展方向
- 在各模块目录内补充接口契约（OpenAPI/AsyncAPI）、序列图与状态机描述。
- 增加 CI/CD、部署模板（Terraform/Helm）、本地开发环境脚本。
- 引入协议与公共库示例（Protobuf/序列化、鉴权中间件、节流防刷）。
