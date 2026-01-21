import time
import json
import uuid
import os
from typing import Dict, Any, Optional, List, Callable
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from dataclasses import dataclass
from enum import Enum
from src.utils import get_logger
from src.utils import extract_json_from_text
import poml  # 在全局导入poml

# Use a new logger
logger = get_logger('api_manager')

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

@dataclass
class APITask:
    """API call task"""
    id: str
    # Traditional mode fields
    prompt: Optional[str] = None
    input_text: Optional[str] = None
    # POML mode fields
    mode: str = "traditional"  # "traditional" or "poml"
    poml_file: Optional[str] = None
    # Common fields
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None
    max_retries: int = 3

class APIClient:
    """Simplified API client"""
    
    def __init__(self, 
                 api_key: str,
                 base_url: str = "https://api.openai.com/v1",
                 model: str = "gpt-3.5-turbo",
                 timeout: int = 30,
                 max_tokens: int = 8192,
                 temperature: float = 0,
                 response_format: Optional[Dict[str, str]] = None,
                 extra_body: Optional[Dict[str, Any]] = None,  # Add extra_body parameter
                 extra_params: Optional[Dict[str, Any]] = None):  # Add extra_params for API parameters
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.response_format = response_format or {}
        self.extra_body = extra_body or {}  # Store extra_body parameter
        self.extra_params = extra_params or {}  # Store extra_params (for qwen API etc.)
        self.logger = get_logger('APIClient')
    
    
    
    def call_api(self, prompt: str = None, input_text: str = None,
                 mode: str = "traditional", poml_file: str = None) -> Dict[str, Any]:
        """Single API call (optimized) - supports both traditional and POML modes"""

        try:
            if mode == "poml" and poml_file:
                context = {'notam_text': input_text}
                with open(poml_file, 'r', encoding='utf-8') as f:
                    poml_content = f.read()
                
                try:
                    params = poml.poml(poml_content, context=context, format="openai_chat")
                except Exception as e:
                    self.logger.error(f"Exception in poml.poml: {str(e)}")
                    params = {
                        "messages": [
                            {"role": "system", "content": "Process NOTAM information and return results in JSON format."},
                            {"role": "user", "content": input_text}
                        ]
                    }
                
                # 添加必要的参数
                params.update({
                    "model": self.model,
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature
                })
            else:
                # Traditional mode
                messages = [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": input_text}
                ]
                
                params = {
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": self.max_tokens,
                    "temperature": self.temperature
                }
            
            # 添加response_format和extra_body
            if self.response_format:
                params["response_format"] = self.response_format

            if self.extra_body:
                params["extra_body"] = self.extra_body

            # 检查params是否有必要的字段
            if "messages" not in params:
                self.logger.error("Missing 'messages' in params, adding default")
                params["messages"] = [
                    {"role": "system", "content": "Process NOTAM text and return results."},
                    {"role": "user", "content": input_text if input_text else "Please provide NOTAM information."}
                ]
            
            # 详细检查消息内容
            for i, msg in enumerate(params.get("messages", [])):
                if not isinstance(msg, dict):
                    self.logger.error(f"Message at index {i} is not a dict: {type(msg)}")
                    params["messages"][i] = {"role": "user", "content": str(msg)}
                elif "role" not in msg or "content" not in msg:
                    self.logger.error(f"Message at index {i} missing required fields: {msg}")
                    params["messages"][i] = {"role": "user", "content": str(msg)}
                elif msg.get("content") is None:
                    self.logger.error(f"Message at index {i} has None content")
                    params["messages"][i]["content"] = ""
            
            # 直接调用API，添加异常捕获来定位JSON错误
            try:
                # 尝试使用更安全的调用方式
                try:
                    # 明确列出需要的参数而不是使用**params
                    messages = params.get("messages", [])
                    model = params.get("model", self.model)
                    max_tokens = params.get("max_tokens", self.max_tokens)
                    temperature = params.get("temperature", self.temperature)
                    response_format = params.get("response_format", {"type": "json_object"})
                    
                    # 添加参数到API调用
                    api_params = {
                        "model": model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                        "response_format": response_format
                    }
                    
                    # 添加extra_body参数(包括enable_thinking)
                    if self.extra_body:
                        api_params['extra_body'] = self.extra_body
                    
                    response = self.client.chat.completions.create(**api_params)
                except Exception as e:
                    self.logger.error(f"分离参数调用失败: {e}, 尝试原始调用")
                    # 确保在原始调用中也添加extra_body参数
                    if self.extra_body:
                        params['extra_body'] = self.extra_body
                    
                    response = self.client.chat.completions.create(**params)
            except TypeError as e:
                # 可能是JSON相关错误
                self.logger.error(f"TypeError in API call: {e}")
                if "must be str, bytes or bytearray, not NoneType" in str(e):
                    # 在这里特别处理None值的情况
                    self.logger.error("JSON None value error detected")
                    # 尝试修复
                    try:
                        if "messages" in params:
                            for i, msg in enumerate(params["messages"]):
                                if msg.get("content") is None:
                                    params["messages"][i]["content"] = ""
                        response = self.client.chat.completions.create(**params)
                    except Exception as e2:
                        self.logger.error(f"Failed to recover from JSON error: {e2}")
                        raise e
                else:
                    raise e
            # 调试输出完整的响应结构
            # 处理DMX API的特殊情况：有时JSON在refusal字段而不是content字段
            message = response.choices[0].message
            content = message.content
            
            # 如果content为None，检查refusal字段
            if content is None and hasattr(message, 'refusal') and message.refusal:
                content = message.refusal
                
                # 检查是否为自然语言解释而非JSON
                if content and (content.startswith("I'm sorry") or 
                                content.startswith("Sorry") or 
                                "does not specify" in content or
                                "no relevant" in content):
                    self.logger.info("模型返回了解释而非JSON数据，返回空数组")
                    # 对于不包含所需信息的NOTAM，返回空数组作为有效的JSON响应
                    content = "[]"
            
            data_to_return = content
            
            # 仅当需要json时才尝试解析
            if self.response_format.get('type') == 'json_object' and content:
                try:
                    # 检查是否已经是字符串形式的JSON格式，如果不是则尝试提取
                    if content.strip().startswith('[') or content.strip().startswith('{'):
                        data_to_return = json.loads(content)
                    else:
                        # 尝试从文本中提取JSON
                        extracted = extract_json_from_text(content)
                        if extracted:
                            data_to_return = extracted
                        else:
                            # 如果无法提取JSON，返回空数组
                            data_to_return = []
                            self.logger.warning("无法提取JSON，返回空数组")
                    
                    # 对于NOTAM处理，确保结果始终是数组
                    if isinstance(data_to_return, dict):
                        data_to_return = [data_to_return]
                        
                except json.JSONDecodeError as e:
                    self.logger.warning(f"JSON parsing failed, attempting extract_json_from_text: {e}")
                    extracted_json = extract_json_from_text(content)
                    if extracted_json is not None:
                        data_to_return = extracted_json
                    else:
                        self.logger.error("All JSON parsing methods failed")
                        return {
                            'success': False,
                            'error': f'JSON parsing failed: {e}',
                            'raw_response': content
                        }

            # 统一的成功返回结构
            # 如果是数组且只有一个元素，则直接使用该元素而不是数组
            if isinstance(data_to_return, list) and len(data_to_return) == 1:
                parse_data = data_to_return[0]
            else:
                parse_data = data_to_return
                
            result = {
                'success': True,
                'data': parse_data,  # 使用处理后的数据
                'raw_response': content,
                'usage': response.usage.dict() if response.usage else None
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"API call failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'raw_response': None
            }

class APIManager:
    """API Manager - Concurrent calls and error handling"""
    
    def __init__(self, 
                 max_workers: int = 5,
                 max_retries: int = 3,
                 retry_delay: float = 1.0,
                 rate_limit: Optional[float] = None):
        self.max_workers = max_workers
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit = rate_limit
        
        self.clients: Dict[str, APIClient] = {}
        self.default_client: Optional[APIClient] = None
        
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'retry_requests': 0,
            'total_tokens': 0
        }
        
        self._last_request_time = 0
        self._lock = threading.Lock()
        self.logger = get_logger('APIManager')
    
    def register_client(self, name: str, client: APIClient, is_default: bool = False):
        """Register a client"""
        self.clients[name] = client
        if is_default or not self.default_client:
            self.default_client = client
        self.logger.info(f"Registered API client: {name} (default: {is_default})")
    
    def setup_clients(self, config: Dict[str, Any]):
        """Set up clients from configuration"""
        self.logger.info(f"Starting to set up API clients, number of configurations: {len(config)}")
        
        for provider, provider_config in config.items():
            if not provider_config.get('api_key'):
                self.logger.warning(f"Skipping {provider}: Missing API key")
                continue
            
            try:
                # Handle provider-specific defaults here
                if provider == 'deepseek':
                    use_json = provider_config.get('use_json_format', True)
                    response_format = {'type': 'json_object'} if use_json else {}
                    
                    client = APIClient(
                        api_key=provider_config['api_key'],
                        base_url="https://api.deepseek.com",
                        model="deepseek-chat",
                        response_format=response_format,
                        **{k: v for k, v in provider_config.items() if k not in ['api_key', 'use_json_format']}
                    )
                elif provider == 'openai':
                    # 避免 base_url 重复传入：手动拆出关键字段，其余作为扩展参数
                    self.logger.debug(f"Setting up openai client with keys: {list(provider_config.keys())}")
                    client = APIClient(
                        api_key=provider_config['api_key'],
                        base_url=provider_config.get('base_url', 'https://api.openai.com/v1'),
                        model=provider_config.get('model', 'gpt-4o-mini'),
                        timeout=provider_config.get('timeout', 30),
                        max_tokens=provider_config.get('max_tokens', 8192),
                        temperature=provider_config.get('temperature', 0),
                        response_format=provider_config.get('response_format', {'type': 'json_object'}),
                        extra_body=provider_config.get('extra_body', {}),
                        **{k: v for k, v in provider_config.items() if k not in ['api_key','base_url','model','timeout','max_tokens','temperature','response_format','extra_body']}
                    )
                elif provider == 'qdd':
                    use_json = provider_config.get('use_json_format', True)
                    response_format = {'type': 'json_schema'} if use_json else {}
                    
                    client = APIClient(
                        api_key=provider_config['api_key'],
                        base_url=provider_config.get('base_url', "https://api2.aigcbest.top/v1"),
                        model=provider_config.get('model', "@cf/meta/llama-3.1-8b-instruct"),
                        response_format=response_format,
                        **{k: v for k, v in provider_config.items() if k not in ['api_key', 'use_json_format', 'base_url', 'model']}
                    )
                elif provider == 'qwen':
                    # 特别为千问API添加特定处理，通过extra_body传递enable_thinking参数
                    client = APIClient(
                        api_key=provider_config['api_key'],
                        base_url=provider_config.get('base_url', "https://dashscope.aliyuncs.com/compatible-mode/v1"),
                        model=provider_config.get('model', "qwen3-8b"),
                        response_format=provider_config.get('response_format', {'type': 'json_object'}),
                        extra_body=provider_config.get('extra_body', {'enable_thinking': False}),  # 默认禁用enable_thinking
                        **{k: v for k, v in provider_config.items() if k not in ['api_key', 'base_url', 'model', 'response_format', 'extra_body']}
                    )
                else:
                    client = APIClient(**provider_config)
                
                self.register_client(provider, client, is_default=(provider == 'deepseek'))
                self.logger.info(f"✅ Successfully set up {provider} client")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to set up {provider} client: {e}")
    
    def single_call(self, 
                    prompt: str, 
                    input_text: str,
                    client_name: Optional[str] = None) -> Dict[str, Any]:
        """Single API call"""
        client = self._get_client(client_name)
        if not client:
            self.logger.error("No available API client")
            return {'success': False, 'error': 'No available client'}
        
        self.stats['total_requests'] += 1
        
        result = self._call_with_retry(client, prompt, input_text)
        
        if result.get('success'):
            self.stats['successful_requests'] += 1
            if result.get('usage'):
                self.stats['total_tokens'] += result['usage'].get('total_tokens', 0)
        else:
            self.stats['failed_requests'] += 1
            self.logger.warning(f"Single API call failed: {result.get('error')}")
        
        return result
    
    def batch_call(self, 
                   requests: List[Dict[str, Any]],
                   progress_callback: Optional[Callable] = None,
                   client_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Batch API calls"""
        if not requests:
            self.logger.warning("Batch call requests are empty")
            return []
        
        self.logger.info(f"Starting batch API calls, number of tasks: {len(requests)}")
        
        tasks = []
        for i, req in enumerate(requests):
            if req.get('mode') == 'poml':
                # POML mode task
                task = APITask(
                    id=str(uuid.uuid4()),
                    mode='poml',
                    poml_file=req['poml_file'],
                    input_text=req['input_text'],
                    prompt=req.get('prompt', 'Please respond in JSON format.'),  # For response_format: json_object
                    max_retries=req.get('max_retries', self.max_retries)
                )
            else:
                # Traditional mode task
                task = APITask(
                    id=str(uuid.uuid4()),
                    mode='traditional',
                    prompt=req['prompt'],
                    input_text=req['input_text'],
                    max_retries=req.get('max_retries', self.max_retries)
                )
            tasks.append(task)
        
        results = self._execute_batch_parallel(tasks, progress_callback, client_name)
        
        # Summarize batch call results
        success_count = sum(1 for r in results if r['result'].get('success'))
        self.logger.info(f"Batch API calls completed: {success_count}/{len(results)} succeeded")
        
        return results
    
    def _execute_batch_parallel(self, 
                              tasks: List[APITask],
                              progress_callback: Optional[Callable],
                              client_name: Optional[str]) -> List[Dict[str, Any]]:
        """Execute batch tasks concurrently"""
        results = [None] * len(tasks)
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_index = {
                executor.submit(self._execute_task, task, client_name): i
                for i, task in enumerate(tasks)
            }
            
            completed_count = 0
            total_tasks = len(tasks)

            for future in as_completed(future_to_index):
                index = future_to_index[future]
                task = tasks[index]
                
                try:
                    result = future.result()
                    results[index] = {'task_id': task.id, 'index': index, 'result': result}
                except Exception as e:
                    self.logger.error(f"Task execution exception: {task.id}: {e}")
                    results[index] = {
                        'task_id': task.id, 
                        'index': index, 
                        'result': {'success': False, 'error': str(e)}
                    }
                finally:
                    completed_count += 1
                    if progress_callback:
                        progress_callback(completed_count, total_tasks)
                    
                    # Log progress every 10 tasks or when all tasks are completed
                    if completed_count % 10 == 0 or completed_count == total_tasks:
                        self.logger.info(f"Batch task progress: {completed_count}/{total_tasks}")
        
        return results
    
    def _execute_task(self, task: APITask, client_name: Optional[str]) -> Dict[str, Any]:
        """Execute a single task (with retries)"""
        task.status = TaskStatus.RUNNING
        client = self._get_client(client_name)
        
        if not client:
            task.status = TaskStatus.FAILED
            task.error = 'No available client'
            self.logger.error(f"[Task {task.id}] Failed: No available client")
            return {'success': False, 'error': task.error}
        
        self.stats['total_requests'] += 1
        
        # 执行任务并记录时间
        start_time = time.time()
        if task.mode == 'poml':
            result = self._call_with_retry_poml(client, task.poml_file, task.input_text, task.max_retries, task.id)
        else:
            result = self._call_with_retry(client, task.prompt, task.input_text, task.max_retries)
        execution_time = time.time() - start_time
        
        # 记录详细的结果
        task.status = TaskStatus.SUCCESS if result.get('success') else TaskStatus.FAILED
        task.result = result
        if not result.get('success'):
            task.error = result.get('error')
            self.logger.error(f"[Task {task.id}] Failed after {execution_time:.2f}s, error: {task.error}")
        else:
            token_usage = result.get('usage', {}).get('total_tokens', 0)
            self.logger.info(f"[Task {task.id}] Completed successfully in {execution_time:.2f}s, tokens: {token_usage}")
            
        return result
    
    def _call_with_retry_poml(self, client: APIClient, poml_file: str, 
                            input_text: str, max_retries: Optional[int] = None, task_id: str = 'unknown') -> Dict[str, Any]:
        """API call with retries for POML mode - with detailed logging"""
        effective_max_retries = max_retries if max_retries is not None else self.max_retries
        last_result = {}

        for attempt in range(effective_max_retries + 1):
            # 捕获可能的JSON错误
            try:
                last_result = client.call_api(mode="poml", poml_file=poml_file, input_text=input_text)
            except Exception as e:
                self.logger.error(f"[Task {task_id}] Exception in POML call: {str(e)}")
                if "must be str, bytes or bytearray, not NoneType" in str(e):
                    self.logger.error(f"[Task {task_id}] JSON None value error detected - this might be a problem with POML parameters")
                last_result = {'success': False, 'error': str(e)}
            
            if last_result.get('success'):
                if attempt > 0:
                    self.logger.info(f"[Task {task_id}] POML retry succeeded, attempts: {attempt + 1}")
                return last_result
            
            if attempt < effective_max_retries:
                self.stats['retry_requests'] += 1
                wait_time = self.retry_delay * (2 ** attempt)
                self.logger.warning(
                    f"[Task {task_id}] POML call failed, retrying in {wait_time:.2f}s ({attempt + 1}/{effective_max_retries}). "
                    f"Error: {last_result.get('error')}"
                )
                time.sleep(wait_time)
        
        self.logger.error(f"[Task {task_id}] All POML retries failed, final error: {last_result.get('error')}")
        return last_result
        
    def _call_with_retry(self, 
                       client: APIClient, 
                       prompt: str, 
                       input_text: str,
                       max_retries: Optional[int] = None,
                       task_id: str = 'unknown') -> Dict[str, Any]:
        """API call with retries (optimized)"""
        effective_max_retries = max_retries if max_retries is not None else self.max_retries
        last_result = {}

        for attempt in range(effective_max_retries + 1):

            last_result = client.call_api(prompt, input_text)
            
            if last_result.get('success'):
                if attempt > 0:
                    self.logger.info(f"Retry succeeded, attempts: {attempt + 1}")
                return last_result
            
            if attempt < effective_max_retries:
                self.stats['retry_requests'] += 1
                wait_time = self.retry_delay * (2 ** attempt)
                self.logger.warning(
                    f"Call failed, retrying in {wait_time:.2f}s ({attempt + 1}/{effective_max_retries}). "
                    f"Error: {last_result.get('error')}"
                )
                time.sleep(wait_time)
        
        self.logger.error(f"All retries failed, final error: {last_result.get('error')}")
        return last_result # Return the last failed attempt
    
    def _get_client(self, client_name: Optional[str] = None) -> Optional[APIClient]:
        """Get a client"""
        if client_name and client_name in self.clients:
            return self.clients[client_name]
        return self.default_client
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        total = self.stats['total_requests']
        success_rate = (self.stats['successful_requests'] / total) if total > 0 else 0
        
        default_client_name = next(
            (name for name, client in self.clients.items() if client == self.default_client), 
            None
        )

        stats = {
            **self.stats,
            'success_rate': f"{success_rate:.2%}",
            'clients': list(self.clients.keys()),
            'default_client': default_client_name
        }
        
        return stats

# Convenience factory function
def create_api_manager(config: Dict[str, Any], **kwargs) -> APIManager:
    """Create and set up an API manager"""
    logger = get_logger('api_manager_factory')
    logger.info("Creating API manager")
    
    manager = APIManager(**kwargs)
    manager.setup_clients(config)
    
    logger.info(f"API manager created, number of clients: {len(manager.clients)}")
    return manager