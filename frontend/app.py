"""
Streamlit前端应用 - 初始表单 + 对话式乡村墙绘AI
"""

import streamlit as st
import requests
import os
import json
from typing import Optional, Dict

# 页面配置
st.set_page_config(
    page_title="乡村墙绘AI助手",
    page_icon="🏡",
    layout="wide"
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .chat-container {
        max-width: 900px;
        margin: 0 auto;
    }
    .message {
        padding: 12px 16px;
        margin-bottom: 12px;
        border-radius: 12px;
        line-height: 1.5;
        position: relative;
        animation: fadeIn 0.3s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .user-message {
        background-color: #E3F2FD;
        margin-left: 20%;
        text-align: right;
        border-bottom-right-radius: 4px;
    }
    .assistant-message {
        background-color: #F5F5F5;
        margin-right: 20%;
        border-bottom-left-radius: 4px;
    }
    .agent-tag {
        font-size: 0.75rem;
        color: #555;
        margin-bottom: 4px;
        font-style: italic;
    }
    .input-area {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 1rem;
        border-top: 1px solid #eee;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    }
    .input-area > div {
        max-width: 900px;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health() -> bool:
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def send_initial_form(village_data: dict) -> Optional[Dict]:
    """发送初始村落信息（作为 user_input 的 JSON 字符串）"""
    try:
        user_input_json = json.dumps(village_data, ensure_ascii=False)
        response = requests.post(
            f"{API_BASE_URL}/api/chat",
            json={"user_input": user_input_json},
            timeout=120
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ 提交失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"❌ 请求异常: {e}")
        return None


def send_chat_message(session_id: str, user_input: str) -> Optional[Dict]:
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/chat",
            json={"session_id": session_id, "user_input": user_input},
            timeout=120
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ 消息发送失败: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"❌ 网络错误: {e}")
        return None


def get_chat_history(session_id: str) -> Optional[Dict]:
    try:
        response = requests.get(f"{API_BASE_URL}/api/chat/{session_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("❌ 会话不存在或已过期")
            return None
    except Exception as e:
        st.error(f"❌ 获取历史失败: {e}")
        return None


def render_message(msg: Dict):
    role = msg["role"]
    content = msg["content"]
    agent_name = msg.get("agent_name", "")

    if role == "user":
        css_class = "user-message"
    else:
        css_class = "assistant-message"

    if agent_name and role != "user":
        st.markdown(f'<div class="agent-tag">[{agent_name}]</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="message {css_class}">{content}</div>',
        unsafe_allow_html=True
    )


def show_initial_form():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    st.info("📌 请先填写村落基本信息，系统将自动生成文化分析与墙绘方案。")

    with st.form("village_form"):
        name = st.text_input("村落名称 *", placeholder="例如：西递村")
        location = st.text_input("地理位置 *", placeholder="例如：安徽省黄山市黟县")
        industry = st.text_input("特色产业（可选）", placeholder="例如：茶叶、 tourism")
        history = st.text_area("历史故事（可选）", placeholder="简要描述村落历史")
        custom_info = st.text_area("其他信息（可选）", placeholder="如民俗、建筑特色等")

        submitted = st.form_submit_button("🚀 开始生成墙绘方案", use_container_width=True)

        if submitted:
            if not name.strip() or not location.strip():
                st.error("❌ 村落名称和地理位置为必填项！")
                return

            village_data = {
                "name": name.strip(),
                "location": location.strip(),
                "industry": industry.strip() or None,
                "history": history.strip() or None,
                "custom_info": custom_info.strip() or None
            }

            with st.spinner("🔄 正在提交村落信息并生成文化分析..."):
                resp = send_initial_form(village_data)
                if resp:
                    st.session_state.session_id = resp["session_id"]
                    st.session_state.messages = resp["messages"]
                    st.session_state.current_stage = resp["current_stage"]
                    st.session_state.is_completed = resp["is_completed"]
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def show_chat_interface():
    # 渲染消息历史
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            render_message(msg)
        st.markdown('</div>', unsafe_allow_html=True)

    # 输入框（固定底部）
    st.markdown('<div class="input-area">', unsafe_allow_html=True)
    with st.container():
        with st.form("chat_input_form", clear_on_submit=True):
            user_input = st.text_area(
                "你的回复",
                placeholder="例如：确认继续 / 修改文化元素 / 重新生成...",
                height=80,
                label_visibility="collapsed"
            )
            submitted = st.form_submit_button("发送", use_container_width=True)

            if submitted and user_input.strip():
                with st.spinner("🤖 AI 正在处理..."):
                    resp = send_chat_message(st.session_state.session_id, user_input.strip())
                    if resp:
                        st.session_state.messages = resp["messages"]
                        st.session_state.current_stage = resp["current_stage"]
                        st.session_state.is_completed = resp["is_completed"]
                        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def main():
    st.markdown('<div class="main-header">🏡 乡村墙绘AI助手</div>', unsafe_allow_html=True)

    # 初始化状态
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "is_completed" not in st.session_state:
        st.session_state.is_completed = False
    if "current_stage" not in st.session_state:
        st.session_state.current_stage = "initial"

    # 侧边栏
    with st.sidebar:
        st.markdown("### 📌 会话状态")
        st.write(f"**阶段**: `{st.session_state.current_stage}`")
        st.write(f"**完成**: `{'是' if st.session_state.is_completed else '否'}`")
        
        if check_api_health():
            st.success("✅ 后端服务正常")
        else:
            st.error("❌ 后端未连接")

        if st.button("🆕 新对话", use_container_width=True):
            st.session_state.session_id = None
            st.session_state.messages = []
            st.session_state.is_completed = False
            st.session_state.current_stage = "initial"
            st.rerun()

        # 调试：手动加载会话
        manual_id = st.text_input("🔍 加载会话ID")
        if st.button("加载") and manual_id:
            resp = get_chat_history(manual_id)
            if resp:
                st.session_state.session_id = manual_id
                st.session_state.messages = resp["messages"]
                st.session_state.current_stage = resp["current_stage"]
                st.session_state.is_completed = resp["is_completed"]
                st.rerun()

    # 主逻辑：判断是否处于初始阶段
    if not st.session_state.session_id or st.session_state.current_stage == "initial":
        show_initial_form()
    else:
        show_chat_interface()

    # 自动滚动到底部
    st.components.v1.html("""
        <script>
            const chatContainer = parent.document.querySelector('section.main');
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        </script>
    """, height=0)


if __name__ == "__main__":
    main()