"""
RESTful API - 取证平台API接口
支持FastAPI，提供完整的REST API
"""
import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

# ==================== 数据模型 ====================

class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息")
    evidence_path: Optional[str] = Field(None, description="证据文件路径")
    history: Optional[List[Dict[str, str]]] = Field(None, description="对话历史")

class ChatResponse(BaseModel):
    """聊天响应"""
    response: str = Field(..., description="AI响应")
    task_type: Optional[str] = Field(None, description="检测到的任务类型")
    findings: Optional[List[str]] = Field(None, description="关键发现")
    artifacts: Optional[List[Dict[str, Any]]] = Field(None, description="提取的证据")

class AnalysisRequest(BaseModel):
    """分析请求"""
    evidence_path: str = Field(..., description="证据文件路径")
    question: str = Field(..., description="分析问题")
    depth: int = Field(3, description="分析深度 (1-5)")

class AnalysisResponse(BaseModel):
    """分析响应"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    question: str = Field(..., description="分析问题")
    evidence_path: str = Field(..., description="证据文件路径")
    plan: Optional[Dict[str, Any]] = Field(None, description="分析计划")
    findings: Optional[List[str]] = Field(None, description="关键发现")
    artifacts: Optional[List[Dict[str, Any]]] = Field(None, description="提取的证据")
    summary: Optional[str] = Field(None, description="分析总结")

class ToolInfo(BaseModel):
    """工具信息"""
    name: str
    category: str
    description: str
    available: bool
    install_command: str

class ToolStatusResponse(BaseModel):
    """工具状态响应"""
    total: int
    available: int
    tools: List[ToolInfo]

class ConfigRequest(BaseModel):
    """配置请求"""
    provider: Optional[str] = Field(None, description="LLM提供者")
    api_key: Optional[str] = Field(None, description="API密钥")
    base_url: Optional[str] = Field(None, description="API基础URL")
    model: Optional[str] = Field(None, description="模型名称")

class PluginInfo(BaseModel):
    """插件信息"""
    name: str
    version: str
    description: str
    author: str
    enabled: bool

# ==================== API应用 ====================

def create_api(agent=None) -> FastAPI:
    """创建API应用"""
    
    from agent.core import ForensicAgent
    from agent.tools.registry import registry
    
    app = FastAPI(
        title="取证AI平台 API",
        description="基于大模型的自动化取证平台 RESTful API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS配置
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 初始化Agent
    forensic_agent = agent or ForensicAgent()
    tool_registry = registry
    
    # 任务存储
    tasks: Dict[str, Dict[str, Any]] = {}
    
    # ==================== 根路由 ====================
    
    @app.get("/", tags=["根"])
    async def root():
        """API根路径"""
        return {
            "name": "取证AI平台 API",
            "version": "0.1.0",
            "docs": "/docs",
            "status": "running"
        }
    
    @app.get("/health", tags=["根"])
    async def health():
        """健康检查"""
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    
    # ==================== 聊天接口 ====================
    
    @app.post("/api/chat", response_model=ChatResponse, tags=["聊天"])
    async def chat(request: ChatRequest):
        """
        与AI取证助手对话
        
        - **message**: 用户消息
        - **evidence_path**: 可选的证据文件路径
        - **history**: 可选的对话历史
        """
        try:
            if request.evidence_path:
                # 执行取证分析
                result = await forensic_agent.analyze(request.message, request.evidence_path)
                return ChatResponse(
                    response=result.get("summary", "分析完成"),
                    task_type=result.get("plan", {}).get("task_type"),
                    findings=result.get("findings"),
                    artifacts=result.get("artifacts")
                )
            else:
                # 普通对话
                from agent.llm import LLMEngine
                llm = LLMEngine()
                
                system_prompt = "你是专业电子取证AI助手，用中文回答。"
                
                messages = [{"role": "system", "content": system_prompt}]
                if request.history:
                    messages.extend(request.history[-5:])
                messages.append({"role": "user", "content": request.message})
                
                response = await llm.chat(messages)
                return ChatResponse(response=response.content)
                
        except Exception as e:
            logger.error(f"聊天错误: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    # ==================== 分析接口 ====================
    
    @app.post("/api/analyze", response_model=AnalysisResponse, tags=["分析"])
    async def analyze(request: AnalysisRequest, background_tasks: BackgroundTasks):
        """
        提交取证分析任务
        
        - **evidence_path**: 证据文件路径
        - **question**: 分析问题
        - **depth**: 分析深度 (1-5)
        """
        import uuid
        
        task_id = str(uuid.uuid4())[:8]
        
        # 创建任务记录
        tasks[task_id] = {
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "request": request.dict()
        }
        
        # 后台执行分析
        background_tasks.add_task(
            _run_analysis,
            task_id,
            request.evidence_path,
            request.question,
            request.depth
        )
        
        return AnalysisResponse(
            task_id=task_id,
            status="pending",
            question=request.question,
            evidence_path=request.evidence_path
        )
    
    async def _run_analysis(task_id: str, evidence_path: str, question: str, depth: int):
        """后台执行分析"""
        try:
            tasks[task_id]["status"] = "running"
            
            result = await forensic_agent.analyze(question, evidence_path)
            
            tasks[task_id].update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "result": result
            })
            
        except Exception as e:
            tasks[task_id].update({
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.now().isoformat()
            })
    
    @app.get("/api/tasks/{task_id}", tags=["分析"])
    async def get_task(task_id: str):
        """获取分析任务状态"""
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail="任务未找到")
        return tasks[task_id]
    
    @app.get("/api/tasks", tags=["分析"])
    async def list_tasks():
        """列出所有任务"""
        return {"tasks": tasks}
    
    # ==================== 工具接口 ====================
    
    @app.get("/api/tools", response_model=ToolStatusResponse, tags=["工具"])
    async def get_tools():
        """获取所有工具状态"""
        status = tool_registry.check_all_tools()
        
        tools = []
        for tool in tool_registry.get_all_tools():
            tools.append(ToolInfo(
                name=tool.name,
                category=tool.category.value,
                description=tool.description,
                available=status.get(tool.name, False),
                install_command=tool.install_command
            ))
        
        available = sum(1 for v in status.values() if v)
        
        return ToolStatusResponse(
            total=len(tools),
            available=available,
            tools=tools
        )
    
    @app.get("/api/tools/{tool_name}", tags=["工具"])
    async def get_tool(tool_name: str):
        """获取指定工具信息"""
        tool = tool_registry.get_tool(tool_name)
        if not tool:
            raise HTTPException(status_code=404, detail="工具未找到")
        
        available = tool_registry.check_tool_available(tool_name)
        
        return {
            "name": tool.name,
            "category": tool.category.value,
            "description": tool.description,
            "available": available,
            "install_command": tool.install_command,
            "command_template": tool.command_template,
            "examples": tool.examples
        }
    
    @app.post("/api/tools/{tool_name}/execute", tags=["工具"])
    async def execute_tool(tool_name: str, evidence_path: str, args: str = ""):
        """执行指定工具"""
        from agent.tools.executor import executor
        
        tool = tool_registry.get_tool(tool_name)
        if not tool:
            raise HTTPException(status_code=404, detail="工具未找到")
        
        result = executor.execute_tool(tool_name, evidence_path, args)
        
        return {
            "tool": tool_name,
            "command": result.command,
            "success": result.success,
            "return_code": result.return_code,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_time": result.execution_time
        }
    
    # ==================== 配置接口 ====================
    
    @app.get("/api/config", tags=["配置"])
    async def get_config():
        """获取当前配置（隐藏敏感信息）"""
        config_path = "config/llm_config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 隐藏API密钥
            if "api_key" in config and config["api_key"]:
                config["api_key"] = config["api_key"][:8] + "..." + config["api_key"][-4:]
            
            return config
        
        return {"provider": "未配置", "model": "未配置"}
    
    @app.put("/api/config", tags=["配置"])
    async def update_config(request: ConfigRequest):
        """更新配置"""
        config_path = "config/llm_config.json"
        
        # 读取现有配置
        config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        
        # 更新配置
        if request.provider:
            config["provider"] = request.provider
        if request.api_key:
            config["api_key"] = request.api_key
        if request.base_url:
            config["base_url"] = request.base_url
        if request.model:
            config["model"] = request.model
        
        # 保存配置
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        return {"message": "配置已更新", "config": config}
    
    # ==================== 知识库接口 ====================
    
    @app.get("/api/knowledge/search", tags=["知识库"])
    async def search_knowledge(query: str, category: str = None, limit: int = 5):
        """搜索知识库"""
        from agent.knowledge_base import KnowledgeBase
        
        kb = KnowledgeBase()
        results = kb.search(query, top_k=limit)
        
        return {
            "query": query,
            "results": [
                {
                    "skill_id": r.skill_id,
                    "name": r.name,
                    "category": r.category,
                    "tags": r.tags,
                    "preview": r.content[:200] + "..."
                }
                for r in results
            ]
        }
    
    @app.get("/api/knowledge/categories", tags=["知识库"])
    async def get_categories():
        """获取知识库类别"""
        from agent.knowledge_base import KnowledgeBase
        
        kb = KnowledgeBase()
        categories = kb.get_all_categories()
        stats = kb.get_stats()
        
        return {
            "categories": categories,
            "stats": stats
        }
    
    # ==================== 插件接口 ====================
    
    @app.get("/api/plugins", tags=["插件"])
    async def list_plugins():
        """列出所有插件"""
        from plugins.manager import plugin_manager
        
        plugins = plugin_manager.list_plugins()
        return {"plugins": plugins}
    
    @app.post("/api/plugins/{plugin_name}/enable", tags=["插件"])
    async def enable_plugin(plugin_name: str):
        """启用插件"""
        from plugins.manager import plugin_manager
        
        result = plugin_manager.enable_plugin(plugin_name)
        return {"message": f"插件 {plugin_name} 已启用", "success": result}
    
    @app.post("/api/plugins/{plugin_name}/disable", tags=["插件"])
    async def disable_plugin(plugin_name: str):
        """禁用插件"""
        from plugins.manager import plugin_manager
        
        result = plugin_manager.disable_plugin(plugin_name)
        return {"message": f"插件 {plugin_name} 已禁用", "success": result}
    
    @app.post("/api/plugins/{plugin_name}/execute", tags=["插件"])
    async def execute_plugin(plugin_name: str, **kwargs):
        """执行插件"""
        from plugins.manager import plugin_manager
        
        result = plugin_manager.execute_plugin(plugin_name, **kwargs)
        return result
    
    # ==================== 报告接口 ====================
    
    @app.post("/api/reports/generate", tags=["报告"])
    async def generate_report(task_id: str, format: str = "markdown"):
        """生成分析报告"""
        if task_id not in tasks:
            raise HTTPException(status_code=404, detail="任务未找到")
        
        task = tasks[task_id]
        if task["status"] != "completed":
            raise HTTPException(status_code=400, detail="任务未完成")
        
        result = task.get("result", {})
        
        if format == "markdown":
            report = _generate_markdown_report(result)
            return {"format": "markdown", "content": report}
        elif format == "json":
            return {"format": "json", "content": result}
        else:
            raise HTTPException(status_code=400, detail="不支持的格式")
    
    def _generate_markdown_report(result: dict) -> str:
        """生成Markdown报告"""
        report = []
        report.append("# 取证分析报告\n")
        report.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if result.get("findings"):
            report.append("## 关键发现\n")
            for i, finding in enumerate(result["findings"], 1):
                report.append(f"{i}. {finding}")
            report.append("")
        
        if result.get("artifacts"):
            report.append("## 提取的证据\n")
            for artifact in result["artifacts"]:
                report.append(f"- **{artifact.get('type')}**: {artifact.get('value', artifact.get('name'))}")
            report.append("")
        
        if result.get("summary"):
            report.append("## 分析总结\n")
            report.append(result["summary"])
        
        return "\n".join(report)
    
    return app

# ==================== 启动入口 ====================

def main():
    """启动API服务"""
    import uvicorn
    
    app = create_api()
    
    print("=" * 50)
    print("  取证AI平台 API 服务")
    print("=" * 50)
    print(f"  API文档: http://localhost:8000/docs")
    print(f"  ReDoc:   http://localhost:8000/redoc")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
