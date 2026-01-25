import os
import json
import yaml
import time
import re
import html
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

from src.api_manager import create_api_manager
from config import prompts as prompt_module

# ---------------------- Utility Functions ---------------------- #
@st.cache_resource(show_spinner=False)
def load_config():
    cfg_path = Path('config.yaml')
    if cfg_path.exists():
        with open(cfg_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}

@st.cache_resource(show_spinner=False)
def init_api_manager(api_key: str, base_url: str, model: str, temperature: float = 0.0):
    """初始化 APIManager，使用 dmxapi 调用 gpt-4.1-nano"""
    cfg = {
        'openai': {
            'api_key': api_key,
            'base_url': base_url,
            'model': model,
            'temperature': temperature,
            'response_format': {'type': 'json_object'}
        }
    }
    return create_api_manager(cfg, max_workers=3, max_retries=2, retry_delay=1.0)

load_dotenv(override=False)

# Collect major prompt variants we want to expose (可根据需要扩展)
EXPOSED_PROMPTS = [
    'LIGHT_PROMPT_ICL',
    'LIGHT_PROMPT_Vanilla',
    'LIGHT_PROMPT_A_COT',
    'RUNWAY_PROMPT_ICL',
    'RUNWAY_PROMPT_Vanilla',
    'RUNWAY_PROMPT_COT'
]

PROMPT_NAME_MAP = {name: getattr(prompt_module, name) for name in EXPOSED_PROMPTS if hasattr(prompt_module, name)}

# 示例 NOTAM（可后续补充完善）
PROMPT_EXAMPLES = {
    'LIGHT_PROMPT_ICL': 'A)KSMF E) SMF RWY 35L/16R ALS U/S) NNNN',
    'LIGHT_PROMPT_Vanilla': 'A)LEVT E) RWY04R/16L APCH LIGHTING SYSTEM DOWNGRADED TO 80 PER CENT )NNNN',
    'LIGHT_PROMPT_A_COT': 'A)EGLL E) RWY 09R/27L ALS REDUCED TO 420M DUE TO MAINTENANCE',
    'RUNWAY_PROMPT_ICL': 'A) ZBAA E) RWY 18L/36R CLOSED DUE TO MAINTENANCE.',
    'RUNWAY_PROMPT_Vanilla': 'A) EHAM E) RWY 09/27 TODA REDUCED BY 500M FOR CONSTRUCTION.',
    'RUNWAY_PROMPT_COT': 'A) YSSY E) RWY 16/34 OPENED AFTER MAINTENANCE. PPR REQUIRED FOR HEAVY ACFT.'
}

def get_prompt_by_key(key: str) -> str:
    return PROMPT_NAME_MAP.get(key, '')

# Highlight utilities with dynamic field awareness per prompt type and pastel colors.

# 定义每类 Prompt 常见字段（尽量覆盖 prompts.py 中的类型）
PROMPT_CATEGORY_FIELDS = {
    'LIGHT': ['airport','runway','lightcategory','light','ilscategory','discate','unavailable/downgrade','state','als','downgrade','distance','percentage'],
    'RUNWAY': ['airport','runway','status_type','ppr','aip','tora','toda','asda','lda','distance_chg','affect_region','flight_type'],
    'TAXIWAY': ['airport','taxiway','status_type','section','intersection_with'],
    'AIRPORT': ['airport','rest_type','affect_region','affect_actype','affect_alt','flight_type'],
    'AREA': ['area_type','area_summary','height_detail','fpl','atc'],
    'AIRWAY': ['airway_id','direction','altitude_restriction','navigation_aid'],
    'PROCEDURE': ['airport','procedure_name','status','phase'],
    'NAVIGATION': ['facility','navaid_type','status','frequency','channel'],
    'STAND': ['airport','stand','status','aircraft_type_limit'],
    'RVR': ['airport','runway','rvr','tendency','time'],
    'STANDARD': ['standard_type','status','scope'],
    'UNKNOWN': []
}

# 柔和配色（避免深色）
PASTEL_PALETTE = [
    '#FFE9C7', '#CDEFFD', '#E3F2D3', '#FDE2E4', '#FFF6B7', '#E4D8F8', '#D0F0F0', '#FFE5EC', '#E0F7FA', '#F9E0FF',
    '#D8F3DC', '#FFEDDE', '#E8EAF6', '#F1F8E9', '#FFF3E0'
]

STATUS_KEYWORDS = [
    r'U/S', r'UNSERVICEABLE', r'UNAVAILABLE', r'DOWNGRADED', r'REDUCED', r'NOT AVBL', r'NOT AVAILABLE',
    r'CLOSED', r'CLSD', r'OPEN', r'OPN'
]

def detect_prompt_category(prompt_key: str) -> str:
    key = prompt_key.upper()
    for cat in PROMPT_CATEGORY_FIELDS.keys():
        if key.startswith(cat):
            return cat
    return 'UNKNOWN'

def build_field_colors(record: dict, category: str) -> dict:
    ordered = PROMPT_CATEGORY_FIELDS.get(category, [])
    colors = {}
    palette_iter = iter(PASTEL_PALETTE)
    # 先为预定义字段分配
    for f in ordered:
        if f not in colors:
            try:
                colors[f] = next(palette_iter)
            except StopIteration:
                palette_iter = iter(PASTEL_PALETTE)
                colors[f] = next(palette_iter)
    # 再为记录中出现但未覆盖的字段分配
    for f in record.keys():
        if f not in colors:
            try:
                colors[f] = next(palette_iter)
            except StopIteration:
                palette_iter = iter(PASTEL_PALETTE)
                colors[f] = next(palette_iter)
    return colors

def _build_patterns(record: dict):
    patterns = []
    def add(field, value, regex=None):
        if value is None: return
        if isinstance(value, (int, float)): value = str(value)
        val = str(value).strip()
        if not val or len(val) > 80:  # 避免超长段落匹配导致整篇染色
            return
        pat = regex if regex else re.escape(val)
        patterns.append((field, pat, val))

    for key, value in record.items():
        add(key, value)

    # 状态关键词扩展
    for status_key in ['unavailable/downgrade','state','status_type','status']:
        if status_key in record:
            for kw in STATUS_KEYWORDS:
                patterns.append((status_key, kw, record.get(status_key)))

    # 跑道特例
    rw = record.get('runway')
    if isinstance(rw, str) and rw:
        patterns.append(('runway', rf'RWY\s*{re.escape(rw)}', rw))
        # 单向拆分（如 35L/16R）
        if '/' in rw:
            for part in rw.split('/'):
                part = part.strip()
                if part:
                    patterns.append(('runway', rf'RWY\s*{re.escape(part)}', part))
    return patterns

def highlight_notam(notam_text: str, record: dict, field_colors: dict) -> str:
    if not notam_text:
        return '<pre>(空)</pre>'
    text = notam_text
    patterns = _build_patterns(record)
    if not patterns:
        return f'<pre>{html.escape(text)}</pre>'

    matches = []
    for field, pat, original_val in patterns:
        try:
            for m in re.finditer(pat, text, re.IGNORECASE):
                matches.append({'start': m.start(), 'end': m.end(), 'field': field, 'value': original_val, 'matched': m.group(0)})
        except re.error:
            continue
    if not matches:
        return f'<pre>{html.escape(text)}</pre>'

    matches.sort(key=lambda x: (x['start'], -(x['end']-x['start'])))
    filtered, last_end = [], -1
    for m in matches:
        if m['start'] >= last_end:
            filtered.append(m)
            last_end = m['end']

    out_parts, cursor = [], 0
    for m in filtered:
        if m['start'] > cursor:
            out_parts.append(html.escape(text[cursor:m['start']]))
        color = field_colors.get(m['field'], '#EEE')
        tooltip = f"{m['field']}: {m['value']}".replace('"','&quot;')
        out_parts.append(
            f"<span style='background:{color};padding:2px 4px;border-radius:4px;margin:1px 0;display:inline-block;' title='{tooltip}'>{html.escape(text[m['start']:m['end']])}</span>"
        )
        cursor = m['end']
    if cursor < len(text):
        out_parts.append(html.escape(text[cursor:]))

    used_fields = {m['field'] for m in filtered}
    legend_html = '<div style="margin-bottom:6px;line-height:1.8;">' + ''.join(
        f"<span style='background:{field_colors.get(f,'#EEE')};padding:3px 6px;border-radius:6px;margin:0 6px 6px 0;font-size:12px;display:inline-block'>{f}</span>" for f in used_fields
    ) + '</div>'
    return legend_html + '<pre style="white-space:pre-wrap;line-height:1.5;background:#FAFAFA;padding:8px;border:1px solid #eee;border-radius:6px;">' + ''.join(out_parts) + '</pre>'

# ---------------------- Page Layout ---------------------- #
st.set_page_config(page_title='航行情报大模型 - NOTAM 解析', layout='wide')

st.title('🚀 航行情报大模型')
st.caption('🔍 用于解析和分类航空 NOTAM 信息的工具')

with st.sidebar:
    st.header('选择解析类型')
    prompt_key = st.selectbox('解析模型 Prompt', EXPOSED_PROMPTS, index=0)
    example_notam = st.text_area('示例 NOTAM', value=PROMPT_EXAMPLES.get(prompt_key, ''), height=90)
    show_prompt = st.checkbox('显示 / 编辑 Prompt', value=False)
    if show_prompt:
        st.text_area('Prompt 内容 (可编辑)', value=get_prompt_by_key(prompt_key), key='prompt_text', height=260)
    else:
        st.session_state['prompt_text'] = get_prompt_by_key(prompt_key)

    st.markdown('---')
    st.subheader('API 设置')
    
    # 预设配置
    PROVIDER_PRESETS = {
        'DMX API': {
            'url': 'https://www.dmxapi.com/v1',
            'model': 'gpt-4.1-nano',
            'key': 'sk-fC3kByDAMkAIcnEDmYvYzzComNjZ4PsJmPZMK2vKIxz6Q2QE' # 仅为示例
        },
        'Alibaba DashScope (Qwen)': {
            'url': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
            'model': 'qwen-plus',
            'key': ''
        },
        'DeepSeek Official': {
            'url': 'https://api.deepseek.com',
            'model': 'deepseek-chat',
            'key': ''
        },
        'Custom': {
            'url': '',
            'model': '',
            'key': ''
        }
    }

    def on_provider_change():
        p = st.session_state.selected_provider
        if p in PROVIDER_PRESETS and p != 'Custom':
            st.session_state.base_url_input = PROVIDER_PRESETS[p]['url']
            st.session_state.model_name_input = PROVIDER_PRESETS[p]['model']
            # 如果预设中有key（例如demo key），也可以填入，但通常建议用户自己填
            if PROVIDER_PRESETS[p]['key']:
                 st.session_state.api_key_input = PROVIDER_PRESETS[p]['key']

    st.selectbox('快速预设 (Provider)', list(PROVIDER_PRESETS.keys()), index=0, key='selected_provider', on_change=on_provider_change)
    
    # 给输入框添加 key 以便通过 callback 更新
    if 'base_url_input' not in st.session_state: st.session_state.base_url_input = PROVIDER_PRESETS['DMX API']['url']
    if 'model_name_input' not in st.session_state: st.session_state.model_name_input = PROVIDER_PRESETS['DMX API']['model']
    if 'api_key_input' not in st.session_state: st.session_state.api_key_input = PROVIDER_PRESETS['DMX API']['key']

    default_base_url = st.text_input('Base URL', key='base_url_input')
    default_api_key = st.text_input('API Key', type='password', help='API Key', key='api_key_input')
    model_name = st.text_input('模型名称', disabled=False, help='请输入实际调用的模型名称', key='model_name_input')
    
    temperature = st.slider('Temperature', 0.0, 1.2, 0.0, 0.1)
    clear_chat = st.button('🗑 清除历史对话')

# Session state for history
if 'history' not in st.session_state or clear_chat:
    st.session_state.history = []

# Input area (bottom-like)
user_input = st.chat_input('请输入您的 NOTAM 文本，或在左侧粘贴示例后发送...')

# Display existing history or welcome panel
if st.session_state.history:
    for item in st.session_state.history:
        with st.chat_message(item['role']):
            if item['role'] == 'assistant' and isinstance(item['content'], dict):
                st.json(item['content'])
            else:
                st.write(item['content'])
else:
    st.info('欢迎使用 NOTAM 解析助手！您可以先选择左侧 Prompt，然后在下方输入 NOTAM 文本。')

# ---------------------- Processing Logic ---------------------- #
if user_input:
    st.session_state.history.append({'role': 'user', 'content': user_input})
    with st.chat_message('assistant'):
        if not default_api_key:
            default_api_key = 'sk-fC3kByDAMkAIcnEDmYvYzzComNjZ4PsJmPZMK2vKIxz6Q2QE'
        
        status_placeholder = st.empty()
        start_time = time.time()
        try:
            # 使用用户输入的模型名称
            actual_model = model_name
            api_manager = init_api_manager(default_api_key, default_base_url, actual_model, temperature)
            prompt_text = st.session_state.get('prompt_text', get_prompt_by_key(prompt_key))

            # 单条调用
            req = [{
                'prompt': prompt_text,
                'input_text': user_input,
                'max_retries': 2,
                'original_index': 0,
                'round': 0
            }]
            status_placeholder.info('正在调用模型，请稍候...')
            results = api_manager.batch_call(req)
            elapsed = time.time() - start_time

            if results and results[0]['result'].get('success'):
                data = results[0]['result'].get('data')
                status_placeholder.success(f'解析完成 ✔ 用时 {elapsed:.2f}s')
                # 统一转为列表便于后续显示
                data_list = data if isinstance(data, list) else [data]

                col1, col2 = st.columns([1,2], gap="large")
                with col1:
                    st.markdown("**解析结果 JSON**", help="结构化字段，可复制")
                    st.json(data)
                with col2:
                    st.markdown("**高亮原文**", help="彩色标记字段与原文对应关系")
                    active_idx = 0
                    if len(data_list) > 1:
                        active_idx = st.number_input('选择高亮记录索引', min_value=0, max_value=len(data_list)-1, value=0, step=1)
                    record = data_list[active_idx] if data_list else {}
                    category = detect_prompt_category(prompt_key)
                    field_colors = build_field_colors(record if isinstance(record, dict) else {}, category)
                    highlighted_html = highlight_notam(user_input, record if isinstance(record, dict) else {}, field_colors)
                    st.markdown(highlighted_html, unsafe_allow_html=True)

                st.session_state.history.append({'role': 'assistant', 'content': data})
            else:
                err = results[0]['result'].get('error') if results else '未知错误'
                st.error(f'解析失败: {err}')
                st.session_state.history.append({'role': 'assistant', 'content': f'解析失败: {err}'})
        except Exception as e:
            st.error(f'调用异常: {e}')
            st.session_state.history.append({'role': 'assistant', 'content': f'异常: {e}'})

# ---------------------- Footer ---------------------- #
st.divider()
st.caption('© 2025 NOTAM Parsing Demo')
