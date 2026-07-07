import streamlit as st
import asyncio
import edge_tts
import os
import hashlib

# ================= 1. 页面基本设置 =================
st.set_page_config(page_title="英语口语对练平台", page_icon="🎤", layout="centered")
st.title("🎤 英语口语对练平台")
st.markdown("用手机或电脑随时随地练习口语。")

# ================= 2. 核心数据 =================
# （这里只保留了两个 Topic 作为演示，你可以把之前完整的 dialogues_data 粘贴过来替换这一块）
dialogues_data = {
    "Topic 1: Good and Bad Behavior (良好与不良行为)": [
        {"A_en": "Hi! How are you doing today?", "A_zh": "(嗨！你今天过得怎么样？)",
         "B_en": "I am doing well, thank you. Let's talk about behavior.",
         "B_zh": "(我很好，谢谢。我们来聊聊行为举止吧。)"},
        {"A_en": "Sure. Have you noticed any bad behavior in public places recently?",
         "A_zh": "(好的。你最近有注意到公共场所的不良行为吗？)",
         "B_en": "Yes. Some people talk very loudly on the bus. It is annoying.",
         "B_zh": "(是的。有些人在公交车上说话很大声。这很烦人。)"},
        {"A_en": "I agree. Smoking in the elevator is also a bad behavior.",
         "A_zh": "(我同意。在电梯里抽烟也是不良行为。)",
         "B_en": "Exactly. Have you experienced any recent examples of good or bad manners?",
         "B_zh": "(没错。你最近经历过好习惯或坏习惯的例子吗？)"}
    ],
    "Topic 2: How you feel about your lives (对生活的感受)": [
        {"A_en": "Hi! How do you feel about your college life right now?", "A_zh": "(嗨！你现在觉得大学生活怎么样？)",
         "B_en": "I feel great. It is busy but very happy.", "B_zh": "(我觉得很好。虽然忙碌但很快乐。)"},
        {"A_en": "Let's talk about the future. What do you expect in the future?",
         "A_zh": "(我们聊聊未来吧。你对未来有什么期待？)",
         "B_en": "I expect to find a good job and travel around the world.",
         "B_zh": "(我期待找一份好工作，然后环游世界。)"}
    ]
}

# ================= 3. 状态管理 (记忆当前读到哪一句) =================
if 'current_round' not in st.session_state:
    st.session_state.current_round = 0
if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = list(dialogues_data.keys())[0]


# ================= 4. 语音生成与缓存引擎 =================
@st.cache_data(show_spinner=False)
def get_audio_file(text, voice):
    """生成音频并返回本地文件路径，利用 Streamlit 的缓存机制做到极速加载"""
    cache_dir = "voice_cache"
    os.makedirs(cache_dir, exist_ok=True)
    file_hash = hashlib.md5((voice + text).encode('utf-8')).hexdigest()
    file_path = os.path.join(cache_dir, f"{file_hash}.mp3")

    if not os.path.exists(file_path):
        async def generate():
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(file_path)

        asyncio.run(generate())

    return file_path


# ================= 5. 网页 UI 排版 =================
# 顶部选择区
st.sidebar.header("⚙️ 练习设置")
new_topic = st.sidebar.selectbox("选择要练习的稿件:", list(dialogues_data.keys()))

# 如果切换了话题，重置进度
if new_topic != st.session_state.selected_topic:
    st.session_state.selected_topic = new_topic
    st.session_state.current_round = 0
    st.rerun()

current_data = dialogues_data[st.session_state.selected_topic]
total_rounds = len(current_data)

st.progress((st.session_state.current_round) / total_rounds,
            text=f"练习进度: {st.session_state.current_round} / {total_rounds}")

if st.session_state.current_round < total_rounds:
    round_data = current_data[st.session_state.current_round]

    # --- A 角色 (电脑发音) ---
    st.info("👱‍♀️ **A (电脑):**")
    st.subheader(round_data["A_en"])
    st.write(round_data["A_zh"])

    # 获取音频并在网页上显示播放器 (开启自动播放)
    a_audio = get_audio_file(round_data["A_en"], "en-US-AriaNeural")
    st.audio(a_audio, format="audio/mp3", autoplay=True)

    st.divider()  # 分割线

    # --- B 角色 (用户台词) ---
    st.warning("🧑 **B (你的台词):**")
    st.subheader(round_data["B_en"])
    st.write(round_data["B_zh"])

    # 折叠面板：如果用户想听示范，点开即可播放男声
    with st.expander("🎤 点击听男声带读示范"):
        b_audio = get_audio_file(round_data["B_en"], "en-US-GuyNeural")
        st.audio(b_audio, format="audio/mp3")

else:
    st.success("🎉 太棒了！你已经完成了本稿件的全部练习。")
    if st.button("🔄 重新练习本篇"):
        st.session_state.current_round = 0
        st.rerun()

# ================= 6. 底部控制按钮 =================
st.write("")  # 占位空行
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("⬅️ 返回上一句", disabled=(st.session_state.current_round == 0), use_container_width=True):
        st.session_state.current_round -= 1
        st.rerun()

with col3:
    if st.button("进入下一句 ➔", disabled=(st.session_state.current_round >= total_rounds), type="primary",
                 use_container_width=True):
        st.session_state.current_round += 1
        st.rerun()