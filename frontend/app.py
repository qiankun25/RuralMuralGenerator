"""
Streamlit前端应用 - 单页面渐进式交互
"""

import streamlit as st
import requests
import time
import os
from PIL import Image
from datetime import datetime
from typing import Optional, Dict

# 页面配置
st.set_page_config(
    page_title="乡村墙绘AI生成系统",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API配置
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #3498DB;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #D5F4E6;
        border-left: 5px solid #27AE60;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #EBF5FB;
        border-left: 5px solid #3498DB;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        background-color: #FEF5E7;
        border-left: 5px solid #F39C12;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# 初始化session_state
def init_session_state():
    """初始化会话状态"""
    if 'workflow_stage' not in st.session_state:
        st.session_state.workflow_stage = 'input'  # input -> analysis -> design -> generation -> complete
    
    if 'village_info' not in st.session_state:
        st.session_state.village_info = {}
    
    if 'culture_analysis' not in st.session_state:
        st.session_state.culture_analysis = None
    
    if 'design_options' not in st.session_state:
        st.session_state.design_options = None
    
    if 'selected_design' not in st.session_state:
        st.session_state.selected_design = None
    
    if 'selected_design_index' not in st.session_state:
        st.session_state.selected_design_index = None
    
    if 'image_task_id' not in st.session_state:
        st.session_state.image_task_id = None
    
    if 'generated_image' not in st.session_state:
        st.session_state.generated_image = None


def check_api_health() -> bool:
    """检查后端API健康状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def call_analyze_api(village_info: Dict) -> Optional[Dict]:
    """调用文化分析API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/analyze",
            json={"village_info": village_info},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API调用失败: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"API调用异常: {e}")
        return None


def call_design_api(culture_analysis: str, user_preference: str = "") -> Optional[Dict]:
    """调用设计方案生成API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/design",
            json={
                "culture_analysis": culture_analysis,
                "user_preference": user_preference
            },
            timeout=90
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API调用失败: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"API调用异常: {e}")
        return None


def call_generate_image_api(design_option: str, style_preference: str = "traditional") -> Optional[str]:
    """调用图像生成API（异步）"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/generate-image",
            json={
                "design_option": design_option,
                "style_preference": style_preference
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            return result.get('task_id')
        else:
            st.error(f"API调用失败: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"API调用异常: {e}")
        return None


def check_task_status(task_id: str) -> Optional[Dict]:
    """查询任务状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/task/{task_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"查询任务状态失败: {e}")
        return None


def render_progress_indicator():
    """渲染进度指示器"""
    stages = {
        'input': ('📝 输入信息', 0),
        'analysis': ('🔍 文化分析', 25),
        'design': ('🎨 设计方案', 50),
        'generation': ('🖼️ 图像生成', 75),
        'complete': ('✅ 完成', 100)
    }
    
    current_stage = st.session_state.workflow_stage
    _, progress = stages[current_stage]
    
    st.progress(progress / 100)
    
    cols = st.columns(5)
    for i, (stage_key, (stage_name, _)) in enumerate(stages.items()):
        with cols[i]:
            if stage_key == current_stage:
                st.markdown(f"**⏳ {stage_name}**")
            elif stages[stage_key][1] < stages[current_stage][1]:
                st.markdown(f"✅ {stage_name}")
            else:
                st.markdown(f"⏸️ {stage_name}")


def render_input_stage():
    """渲染输入阶段"""
    st.markdown('<div class="step-header">📝 步骤1：输入乡村信息</div>', unsafe_allow_html=True)
    
    with st.form("village_info_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            village_name = st.text_input(
                "🏘️ 乡村名称 *",
                placeholder="例如：西递村",
                help="请输入您要设计墙绘的乡村名称"
            )
            
            location = st.text_input(
                "📍 地理位置 *",
                placeholder="例如：安徽省黄山市",
                help="请输入乡村所在的省市县"
            )
        
        with col2:
            industry = st.text_input(
                "🏭 特色产业",
                placeholder="例如：旅游、茶叶种植",
                help="请输入乡村的主要产业或特色"
            )
            
            style_pref = st.selectbox(
                "🎨 设计风格偏好",
                options=["传统文化风格", "现代简约风格", "文化叙事风格"],
                help="选择您偏好的墙绘设计风格"
            )
        
        history = st.text_area(
            "📖 历史故事或文化特色",
            placeholder="请描述该乡村的历史背景、文化特色、民俗活动等...",
            height=150,
            help="详细的文化信息将帮助AI生成更准确的设计方案"
        )
        
        custom_info = st.text_area(
            "💡 其他要求（可选）",
            placeholder="例如：希望突出某个特定元素、色彩偏好等...",
            height=100
        )
        
        submitted = st.form_submit_button("🚀 开始生成", use_container_width=True)
        
        if submitted:
            if not village_name or not location:
                st.error("❌ 请填写必填项：乡村名称和地理位置")
            else:
                # 保存村落信息
                st.session_state.village_info = {
                    "name": village_name,
                    "location": location,
                    "industry": industry,
                    "history": history,
                    "custom_info": custom_info,
                    "style_preference": style_pref
                }
                
                # 进入分析阶段
                st.session_state.workflow_stage = 'analysis'
                st.rerun()


def render_analysis_stage():
    """渲染文化分析阶段"""
    st.markdown('<div class="step-header">🔍 步骤2：文化分析结果</div>', unsafe_allow_html=True)
    
    # 显示用户输入的信息（可折叠）
    with st.expander("📋 查看输入的乡村信息", expanded=False):
        st.write(f"**乡村名称**: {st.session_state.village_info.get('name')}")
        st.write(f"**地理位置**: {st.session_state.village_info.get('location')}")
        st.write(f"**特色产业**: {st.session_state.village_info.get('industry', '未填写')}")
        st.write(f"**历史故事**: {st.session_state.village_info.get('history', '未填写')}")
    
    # 如果还没有分析结果，调用API
    if st.session_state.culture_analysis is None:
        with st.spinner("🤖 文化分析智能体正在工作，请稍候..."):
            result = call_analyze_api(st.session_state.village_info)
            
            if result and result.get('status') == 'success':
                st.session_state.culture_analysis = result.get('culture_analysis')
                st.rerun()
            else:
                st.error("❌ 文化分析失败，请重试")
                if st.button("🔄 返回重新输入"):
                    st.session_state.workflow_stage = 'input'
                    st.session_state.culture_analysis = None
                    st.rerun()
                return
    
    # 显示分析结果
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.markdown("### ✅ 文化分析完成")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(st.session_state.culture_analysis)
    
    # 操作按钮
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("✅ 继续生成设计方案", use_container_width=True, type="primary"):
            st.session_state.workflow_stage = 'design'
            st.rerun()
    
    with col2:
        if st.button("🔄 重新分析", use_container_width=True):
            st.session_state.culture_analysis = None
            st.rerun()
    
    with col3:
        if st.button("⬅️ 返回", use_container_width=True):
            st.session_state.workflow_stage = 'input'
            st.session_state.culture_analysis = None
            st.rerun()


def render_design_stage():
    """渲染设计方案阶段"""
    st.markdown('<div class="step-header">🎨 步骤3：选择设计方案</div>', unsafe_allow_html=True)

    # 如果还没有设计方案，调用API
    if st.session_state.design_options is None:
        # 可选：用户偏好输入
        user_preference = st.text_input(
            "💭 设计偏好（可选）",
            placeholder="例如：希望更突出木雕元素、色彩更明快等...",
            help="您可以提出具体的设计要求"
        )

        if st.button("🎨 生成设计方案", use_container_width=True, type="primary"):
            with st.spinner("🤖 创意设计智能体正在工作，请稍候..."):
                result = call_design_api(
                    st.session_state.culture_analysis,
                    user_preference
                )

                if result and result.get('status') == 'success':
                    st.session_state.design_options = result.get('design_options')
                    st.rerun()
                else:
                    st.error("❌ 设计方案生成失败，请重试")
                    return

        # 返回按钮
        if st.button("⬅️ 返回文化分析", use_container_width=True):
            st.session_state.workflow_stage = 'analysis'
            st.rerun()

        return

    # 显示设计方案
    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.markdown("### ✅ 设计方案已生成")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(st.session_state.design_options)

    # 方案选择
    st.markdown("---")
    st.markdown("### 📌 请选择一个设计方案")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✅ 选择方案A", use_container_width=True, type="primary"):
            st.session_state.selected_design_index = 0
            st.session_state.selected_design = "方案A"
            st.session_state.workflow_stage = 'generation'
            st.rerun()

    with col2:
        if st.button("✅ 选择方案B", use_container_width=True, type="primary"):
            st.session_state.selected_design_index = 1
            st.session_state.selected_design = "方案B"
            st.session_state.workflow_stage = 'generation'
            st.rerun()

    with col3:
        if st.button("✅ 选择方案C", use_container_width=True, type="primary"):
            st.session_state.selected_design_index = 2
            st.session_state.selected_design = "方案C"
            st.session_state.workflow_stage = 'generation'
            st.rerun()

    st.markdown("---")

    # 其他操作
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 重新生成方案", use_container_width=True):
            st.session_state.design_options = None
            st.rerun()

    with col2:
        if st.button("⬅️ 返回文化分析", use_container_width=True):
            st.session_state.workflow_stage = 'analysis'
            st.rerun()


def render_generation_stage():
    """渲染图像生成阶段"""
    st.markdown('<div class="step-header">🖼️ 步骤4：生成墙绘图像</div>', unsafe_allow_html=True)

    # 显示选择的方案
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown(f"**已选择**: {st.session_state.selected_design}")
    st.markdown('</div>', unsafe_allow_html=True)

    # 如果还没有创建任务，创建图像生成任务
    if st.session_state.image_task_id is None:
        # 风格选择
        style_mapping = {
            "传统文化风格": "traditional",
            "现代简约风格": "modern",
            "文化叙事风格": "narrative"
        }

        style_preference = style_mapping.get(
            st.session_state.village_info.get('style_preference', '传统文化风格'),
            'traditional'
        )

        with st.spinner("🤖 正在创建图像生成任务..."):
            # 提取选定方案的内容
            design_text = st.session_state.design_options

            task_id = call_generate_image_api(design_text, style_preference)

            if task_id:
                st.session_state.image_task_id = task_id
                st.rerun()
            else:
                st.error("❌ 创建图像生成任务失败")
                if st.button("⬅️ 返回选择方案"):
                    st.session_state.workflow_stage = 'design'
                    st.rerun()
                return

    # 轮询任务状态
    task_id = st.session_state.image_task_id

    # 创建占位符
    status_placeholder = st.empty()
    progress_placeholder = st.empty()

    # 轮询任务状态
    max_attempts = 60  # 最多轮询60次（约2分钟）
    attempt = 0

    while attempt < max_attempts:
        task_status = check_task_status(task_id)

        if task_status:
            status = task_status.get('status')
            progress = task_status.get('progress', 0)

            # 更新进度显示
            status_placeholder.info(f"🖼️ 图像生成中... 状态: {status}")
            progress_placeholder.progress(progress / 100)

            if status == 'completed':
                # 任务完成
                result = task_status.get('result')
                st.session_state.generated_image = result
                st.session_state.workflow_stage = 'complete'
                st.rerun()
                break

            elif status == 'failed':
                # 任务失败
                error = task_status.get('error', '未知错误')
                st.error(f"❌ 图像生成失败: {error}")

                if st.button("🔄 重新生成"):
                    st.session_state.image_task_id = None
                    st.rerun()

                if st.button("⬅️ 返回选择方案"):
                    st.session_state.workflow_stage = 'design'
                    st.session_state.image_task_id = None
                    st.rerun()

                break

            else:
                # 继续等待
                time.sleep(2)
                attempt += 1
        else:
            st.error("❌ 无法查询任务状态")
            break

    if attempt >= max_attempts:
        st.warning("⚠️ 图像生成超时，请稍后查看或重新生成")


def render_complete_stage():
    """渲染完成阶段"""
    st.markdown('<div class="step-header">✅ 步骤5：生成完成</div>', unsafe_allow_html=True)

    st.balloons()

    st.markdown('<div class="success-box">', unsafe_allow_html=True)
    st.markdown("### 🎉 墙绘设计已完成！")
    st.markdown('</div>', unsafe_allow_html=True)

    # 显示生成的图像
    if st.session_state.generated_image:
        result = st.session_state.generated_image
        images = result.get('images', [])

        if images:
            st.markdown("### 🖼️ 生成的墙绘图像")

            for i, img_info in enumerate(images):
                local_path = img_info.get('local_path')

                if local_path and os.path.exists(local_path):
                    try:
                        image = Image.open(local_path)
                        st.image(image, caption=f"墙绘设计图 {i+1}", use_column_width=True)

                        # 下载按钮
                        with open(local_path, 'rb') as f:
                            st.download_button(
                                label=f"💾 下载图像 {i+1}",
                                data=f,
                                file_name=f"mural_design_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                                mime="image/png",
                                use_container_width=True
                            )
                    except Exception as e:
                        st.error(f"无法加载图像: {e}")
                else:
                    st.warning("图像文件不存在")

            # 显示是否为Mock图像
            if result.get('is_mock'):
                st.markdown('<div class="warning-box">', unsafe_allow_html=True)
                st.markdown("⚠️ **注意**: 这是演示图像。要生成真实图像，请配置通义万相API密钥。")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("未找到生成的图像")

    # 显示完整报告
    with st.expander("📄 查看完整设计报告", expanded=False):
        st.markdown("### 文化分析报告")
        st.markdown(st.session_state.culture_analysis)

        st.markdown("---")
        st.markdown("### 设计方案")
        st.markdown(st.session_state.design_options)

    # 操作按钮
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 重新生成图像", use_container_width=True):
            st.session_state.workflow_stage = 'generation'
            st.session_state.image_task_id = None
            st.session_state.generated_image = None
            st.rerun()

    with col2:
        if st.button("🎨 选择其他方案", use_container_width=True):
            st.session_state.workflow_stage = 'design'
            st.session_state.image_task_id = None
            st.session_state.generated_image = None
            st.rerun()

    with col3:
        if st.button("🆕 开始新项目", use_container_width=True):
            # 重置所有状态
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


def main():
    """主函数"""
    # 初始化session state
    init_session_state()

    # 标题
    st.markdown('<div class="main-header">🏡 乡村墙绘AI生成系统</div>', unsafe_allow_html=True)

    # 侧边栏
    with st.sidebar:
        st.markdown("### ⚙️ 系统配置")

        # API健康检查
        if check_api_health():
            st.success("✅ 后端服务正常")
        else:
            st.error("❌ 后端服务未连接")
            st.info(f"请确保后端服务运行在: {API_BASE_URL}")

        st.markdown("---")

        st.markdown("### 📖 使用说明")
        st.markdown("""
        1. **输入信息**: 填写乡村的基本信息
        2. **文化分析**: AI分析乡村文化特色
        3. **设计方案**: 生成3个备选设计方案
        4. **图像生成**: 根据选定方案生成墙绘图像
        5. **下载结果**: 下载图像和完整报告
        """)

        st.markdown("---")

        st.markdown("### 🤖 智能体说明")
        st.markdown("""
        - **文化分析Agent**: 使用ChromaDB检索和LLM分析
        - **创意设计Agent**: 基于文化分析生成设计方案
        - **图像生成Agent**: 调用通义万相生成图像
        """)

        st.markdown("---")

        st.markdown("### ℹ️ 关于")
        st.markdown("""
        **版本**: 1.0.0
        **技术栈**: CrewAI + LangChain + ChromaDB
        **LLM**: 通义千问
        **图像生成**: 通义万相
        """)

    # 进度指示器
    render_progress_indicator()

    st.markdown("---")

    # 根据工作流阶段渲染不同内容
    if st.session_state.workflow_stage == 'input':
        render_input_stage()

    elif st.session_state.workflow_stage == 'analysis':
        render_analysis_stage()

    elif st.session_state.workflow_stage == 'design':
        render_design_stage()

    elif st.session_state.workflow_stage == 'generation':
        render_generation_stage()

    elif st.session_state.workflow_stage == 'complete':
        render_complete_stage()


if __name__ == "__main__":
    main()


