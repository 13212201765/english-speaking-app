import streamlit as st
import asyncio
import edge_tts
import os
import hashlib

# ================= 1. 页面基本设置 =================
st.set_page_config(page_title="英语口语对练平台", page_icon="🎤", layout="centered")
st.title("🎤 英语口语对练平台")
st.markdown("用手机或电脑随时随地练习口语。")

# ================= 2. 核心数据 (完整5个话题) =================
dialogues_data = {
    "Topic 1: Good and Bad Behavior (良好与不良行为)": [
        {"A_en": "Hi! How are you doing today?", "A_zh": "(嗨！你今天过得怎么样？)", "B_en": "I am doing well, thank you. Let's talk about behavior.", "B_zh": "(我很好，谢谢。我们来聊聊行为举止吧。)"},
        {"A_en": "Sure. Have you noticed any bad behavior in public places recently?", "A_zh": "(好的。你最近有注意到公共场所的不良行为吗？)", "B_en": "Yes. Some people talk very loudly on the bus. It is annoying.", "B_zh": "(是的。有些人在公交车上说话很大声。这很烦人。)"},
        {"A_en": "I agree. Smoking in the elevator is also a bad behavior.", "A_zh": "(我同意。在电梯里抽烟也是不良行为。)", "B_en": "Exactly. Have you experienced any recent examples of good or bad manners?", "B_zh": "(没错。你最近经历过好习惯或坏习惯的例子吗？)"},
        {"A_en": "Yesterday, I saw a young boy helping an old man cross the street.", "A_zh": "(昨天，我看到一个小男孩扶一位老人过马路。)", "B_en": "That is a great example of good manners! It warms my heart.", "B_zh": "(那是好习惯的绝佳榜样！让我心里暖暖的。)"},
        {"A_en": "But last week, someone threw trash on the floor in the library.", "A_zh": "(但是上周，有人在图书馆把垃圾扔在地上。)", "B_en": "That is terrible. We should always keep public places clean.", "B_zh": "(太糟糕了。我们应该始终保持公共场所的清洁。)"},
        {"A_en": "So, what are your attitudes toward bad behavior?", "A_zh": "(那么，你对不良行为的态度是什么？)", "B_en": "I think bad behavior shows a lack of respect for others.", "B_zh": "(我认为不良行为表现出对他人的不尊重。)"},
        {"A_en": "I totally agree. We must follow the rules in our society.", "A_zh": "(我完全同意。我们必须遵守社会规则。)", "B_en": "Yes. If everyone is polite, our society will be much better.", "B_zh": "(是的。如果每个人都有礼貌，我们的社会会好得多。)"},
        {"A_en": "Education is very important to stop bad behavior.", "A_zh": "(教育对于阻止不良行为非常重要。)", "B_en": "You are right. Parents and schools should teach children good manners.", "B_zh": "(你说得对。父母和学校应该教孩子们好习惯。)"},
        {"A_en": "We should also start with ourselves and be good citizens.", "A_zh": "(我们也应该从自己做起，做好公民。)", "B_en": "I couldn't agree more. Let's try our best.", "B_zh": "(我完全同意。我们尽力而为吧。)"},
        {"A_en": "Well, it was nice talking with you about this.", "A_zh": "(嗯，很高兴和你聊这个。)", "B_en": "Nice talking to you too. See you later!", "B_zh": "(也很高兴和你聊天。回见！)"}
    ],
    "Topic 2: How you feel about your lives (对生活的感受)": [
        {"A_en": "Hi! How do you feel about your college life right now?", "A_zh": "(嗨！你现在觉得大学生活怎么样？)", "B_en": "I feel great. It is busy but very happy.", "B_zh": "(我觉得很好。虽然忙碌但很快乐。)"},
        {"A_en": "Let's talk about the future. What do you expect in the future?", "A_zh": "(我们聊聊未来吧。你对未来有什么期待？)", "B_en": "I expect to find a good job and travel around the world.", "B_zh": "(我期待找一份好工作，然后环游世界。)"},
        {"A_en": "That is a wonderful dream. I expect to become a great teacher.", "A_zh": "(那是个美妙的梦想。我期待成为一名好老师。)", "B_en": "Teaching is a great job. What do you not expect in the future?", "B_zh": "(教书是份好工作。未来有什么是不期待的？)"},
        {"A_en": "I do not expect life to be perfectly easy. There will be difficulties.", "A_zh": "(我不指望生活一帆风顺。总会有困难的。)", "B_en": "I agree with you. I also do not expect to be super rich.", "B_zh": "(我同意。我也不指望自己变得超级有钱。)"},
        {"A_en": "Money is not everything. Being happy and healthy is more important.", "A_zh": "(钱不是万能的。快乐和健康更重要。)", "B_en": "That is a very mature attitude. Hardships make us stronger.", "B_zh": "(这是很成熟的态度。困难使我们更强大。)"},
        {"A_en": "Yes, we just need to face our problems bravely.", "A_zh": "(是的，我们只需要勇敢面对问题。)", "B_en": "Speaking of happiness, what are the best days of your lives?", "B_zh": "(说到幸福，你生命中最美好的日子是什么？)"},
        {"A_en": "I think our college days are the best days of our lives.", "A_zh": "(我认为我们的大学时光是生命中最美好的日子。)", "B_en": "Really? Why do you say that?", "B_zh": "(真的吗？为什么这么说？)"},
        {"A_en": "Because we have the time, energy, and freedom to learn new things.", "A_zh": "(因为我们有时间、精力和自由去学习新事物。)", "B_en": "I totally agree. We don't have too much pressure from work yet.", "B_zh": "(我完全同意。我们现在还没有太大的工作压力。)"},
        {"A_en": "So we should cherish every single day in our university.", "A_zh": "(所以我们应该珍惜在大学里的每一天。)", "B_en": "Yes, let's work hard and enjoy our youth!", "B_zh": "(是的，让我们努力学习，享受青春！)"},
        {"A_en": "Thank you for sharing your thoughts with me.", "A_zh": "(谢谢你和我分享你的想法。)", "B_en": "You are welcome. See you next time!", "B_zh": "(不客气。下次见！)"}
    ],
    "Topic 3: Leisure Time Activities (休闲时间活动)": [
        {"A_en": "Hello! The weather is so nice today, isn't it?", "A_zh": "(你好！今天天气真好，不是吗？)", "B_en": "Hi! Yes, it is a great day to relax.", "B_zh": "(嗨！是的，这是放松的好日子。)"},
        {"A_en": "So, what do you usually do in your free time?", "A_zh": "(那你空闲时间通常做什么？)", "B_en": "I usually read books and play badminton. What about you?", "B_zh": "(我通常看书和打羽毛球。你呢？)"},
        {"A_en": "I like watching movies and listening to music.", "A_zh": "(我喜欢看电影和听音乐。)", "B_en": "That sounds great. Relaxation is very important for our health.", "B_zh": "(听起来很棒。放松对我们的健康很重要。)"},
        {"A_en": "What would you do differently if you were given more time or money?", "A_zh": "(如果你有更多的时间或金钱，你会做些什么不同的事？)", "B_en": "If I had more money and time, I would travel to Paris.", "B_zh": "(如果我有更多的钱和时间，我会去巴黎旅行。)"},
        {"A_en": "Paris is beautiful! If I had the opportunity, I would learn the piano.", "A_zh": "(巴黎很美！如果有机会，我会学弹钢琴。)", "B_en": "Playing the piano is elegant. Why don't you do it now?", "B_zh": "(弹钢琴很优雅。你为什么现在不学呢？)"},
        {"A_en": "Because I don't have enough free time. College life is really busy!", "A_zh": "(因为我没有足够的空闲时间。大学生活真的很忙！)", "B_en": "I understand. We have too many classes every single day.", "B_zh": "(我明白。我们每天有太多的课。)"},
        {"A_en": "What are the benefits to society of giving people more free time?", "A_zh": "(如果给人们更多空闲时间，对社会有什么好处？)", "B_en": "If people have more holidays, they will be happier and less stressed.", "B_zh": "(如果人们有更多假期，他们会更快乐，压力也会更小。)"},
        {"A_en": "That makes sense. Happier people are usually more productive.", "A_zh": "(有道理。更快乐的人通常工作效率更高。)", "B_en": "Yes, and they will spend more money on traveling and shopping.", "B_zh": "(是的，而且他们会在旅游和购物上花更多钱。)"},
        {"A_en": "That is very good for the economy. It is a win-win situation.", "A_zh": "(这对经济非常好。这是一个双赢的局面。)", "B_en": "Exactly! I really hope we can get more holidays in the future.", "B_zh": "(完全正确！我真希望未来我们能有更多假期。)"},
        {"A_en": "Me too! Anyway, I have a class soon. Goodbye!", "A_zh": "(我也是！不管怎样，我马上要有课了。再见！)", "B_en": "Nice talking to you. See you later!", "B_zh": "(很高兴和你聊天。回见！)"}
    ],
    "Topic 4: Money and Happiness (金钱与幸福)": [
        {"A_en": "Hi! Let's discuss an interesting topic today.", "A_zh": "(嗨！我们今天来讨论一个有趣的话题吧。)", "B_en": "Sure! What are we going to talk about?", "B_zh": "(好啊！我们要聊什么？)"},
        {"A_en": "What are your opinions on the relationship between money and happiness?", "A_zh": "(你对金钱和幸福之间的关系有什么看法？)", "B_en": "I think money is important, but it cannot buy true happiness.", "B_zh": "(我认为钱很重要，但买不到真正的幸福。)"},
        {"A_en": "I completely agree. Money can buy a house, but not a warm home.", "A_zh": "(我完全同意。钱能买到房子，但买不到温暖的家。)", "B_en": "Exactly. Money can make life easier, but not always happier.", "B_zh": "(没错。钱能让生活更轻松，但不一定更快乐。)"},
        {"A_en": "So, what things do you think are more important than money?", "A_zh": "(那么，你认为什么东西比钱更重要？)", "B_en": "Health and family are definitely more important than money.", "B_zh": "(健康和家庭绝对比钱更重要。)"},
        {"A_en": "You are so right. Without good health, money means nothing.", "A_zh": "(你太对了。没有好身体，钱毫无意义。)", "B_en": "Also, true friendship is priceless and more important than wealth.", "B_zh": "(而且，真正的友谊是无价的，比财富更重要。)"},
        {"A_en": "Yes. Having good friends makes our life very colorful.", "A_zh": "(是的。有好朋友让我们的生活丰富多彩。)", "B_en": "Now, let's talk about the rich and the poor.", "B_zh": "(现在，我们来谈谈富人和穷人。)"},
        {"A_en": "What do you think the rich can do to support the poor?", "A_zh": "(你认为富人能做些什么来帮助穷人？)", "B_en": "The rich can donate money to build schools in poor areas.", "B_zh": "(富人可以捐钱在贫困地区建学校。)"},
        {"A_en": "That is a very good idea. Education can change their lives.", "A_zh": "(这是个好主意。教育能改变他们的生活。)", "B_en": "The rich can also provide more job opportunities for them.", "B_zh": "(富人也可以为他们提供更多就业机会。)"},
        {"A_en": "Yes, helping others is a great way to find real happiness.", "A_zh": "(是的，帮助他人是找到真正幸福的好方法。)", "B_en": "A society full of love and help is what we really need.", "B_zh": "(一个充满爱和帮助的社会正是我们需要的。)"},
        {"A_en": "I totally agree with you. It was a great chat.", "A_zh": "(我完全同意。这是次很棒的聊天。)", "B_en": "Thank you! Have a nice day!", "B_zh": "(谢谢！祝你今天愉快！)"}
    ],
    "Topic 5: Arts (艺术)": [
         {"A_en": "Good morning! Do you like arts?", "A_zh": "(早上好！你喜欢艺术吗？)", "B_en": "Good morning! Yes, I think art is very interesting and beautiful.", "B_zh": "(早上好！是的，我觉得艺术非常有趣且美丽。)"},
        {"A_en": "What areas of the arts do you enjoy the most?", "A_zh": "(你最喜欢哪个艺术领域？)", "B_en": "I really enjoy pop music and action movies. What about you?", "B_zh": "(我特别喜欢流行音乐和动作电影。你呢？)"},
        {"A_en": "I love traditional painting and photography.", "A_zh": "(我喜欢传统绘画和摄影。)", "B_en": "That sounds very elegant. They can capture beautiful moments.", "B_zh": "(听起来很优雅。它们能捕捉美丽的瞬间。)"},
        {"A_en": "Have you been to any exhibition or performance recently?", "A_zh": "(你最近去过什么展览或演出吗？)", "B_en": "Yes, I went to a music concert last month.", "B_zh": "(是的，我上个月去了一场音乐会。)"},
        {"A_en": "Wow! How was the concert?", "A_zh": "(哇！音乐会怎么样？)", "B_en": "The atmosphere was fantastic, and I felt very relaxed.", "B_zh": "(氛围太棒了，我觉得非常放松。)"},
        {"A_en": "That is wonderful. I went to a photography exhibition last weekend.", "A_zh": "(太棒了。我上周末去了一个摄影展。)", "B_en": "Did you see any beautiful pictures there?", "B_zh": "(你在那里看到漂亮的照片了吗？)"},
        {"A_en": "Yes, I saw many amazing photos of nature and animals.", "A_zh": "(是的，我看到了很多关于自然和动物的惊艳照片。)", "B_en": "So, what are your general attitudes toward arts?", "B_zh": "(那么，你对艺术的总体态度是什么？)"},
        {"A_en": "I think art is an essential part of our daily life.", "A_zh": "(我认为艺术是我们日常生活中必不可少的一部分。)", "B_en": "I completely agree. Art makes our world colorful and meaningful.", "B_zh": "(我完全同意。艺术让我们的世界变得多姿多彩且有意义。)"},
        {"A_en": "Art also helps us express our deep feelings and emotions.", "A_zh": "(艺术也帮助我们表达内心深处的感受和情感。)", "B_en": "Definitely. Life without art would be very boring.", "B_zh": "(绝对的。没有艺术的生活会非常无聊。)"},
        {"A_en": "Well, I need to go to the library now. See you!", "A_zh": "(好了，我现在得去图书馆了。再见！)", "B_en": "Okay, see you next time!", "B_zh": "(好的，下次见！)"}
    ]
}

# ================= 3. 状态管理 =================
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

st.progress((st.session_state.current_round) / total_rounds, text=f"练习进度: {st.session_state.current_round} / {total_rounds}")

if st.session_state.current_round < total_rounds:
    round_data = current_data[st.session_state.current_round]
    
    # --- A 角色 (电脑发音) ---
    st.info("👱‍♀️ **A (电脑):**")
    st.subheader(round_data["A_en"])
    st.write(round_data["A_zh"])
    
    # 获取音频并在网页上显示播放器 (开启自动播放)
    a_audio = get_audio_file(round_data["A_en"], "en-US-AriaNeural")
    st.audio(a_audio, format="audio/mp3", autoplay=True)
    
    st.divider() # 分割线
    
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
st.write("") # 占位空行
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("⬅️ 返回上一句", disabled=(st.session_state.current_round == 0), use_container_width=True):
        st.session_state.current_round -= 1
        st.rerun()

with col3:
    if st.button("进入下一句 ➔", disabled=(st.session_state.current_round >= total_rounds), type="primary", use_container_width=True):
        st.session_state.current_round += 1
        st.rerun()
