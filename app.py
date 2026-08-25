import streamlit as st
from modules.gemini_client import analyze_content
from modules.audio_processor import analyze_audio
from modules.video_processor import analyze_video
from modules.url_processor import analyze_url
from utils.ui_helpers import inject_styles, stat_card, deck_card

st.set_page_config(page_title="LectureLens AI", page_icon="✦", layout="wide")
inject_styles()

defaults = {
    "study_pack": None,
    "source_content": None,
    "source_name": "",
    "page": "Dashboard",
    "flash_index": 0,
    "show_answer": False,
    "studied": 0,
    "quiz_done": False
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

with st.sidebar:
    st.markdown('<div class="brand"><span>✦</span> LECTURELENS AI</div>', unsafe_allow_html=True)
    st.caption("Your intelligent study workspace")
    pages = ["Dashboard", "Create Study Pack", "Flashcards", "Quiz", "Exam Prep", "Study Coach"]
    for page in pages:
        if st.button(("● " if st.session_state.page == page else "○ ") + page, use_container_width=True, key="nav_"+page):
            st.session_state.page = page
            st.rerun()
    st.divider()
    st.markdown("**AI Study Engine**")
    st.caption("Gemini-powered lecture understanding")
    if st.session_state.study_pack:
        if st.button("＋ New Lecture", use_container_width=True):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.rerun()

def topbar():
    left, right = st.columns([4,1])
    with left:
        st.markdown("**LectureLens AI**  ·  Personal Study Workspace")
    with right:
        st.markdown('<div style="text-align:right;color:#8d879a">✦ AI READY</div>', unsafe_allow_html=True)

def generate(source_mode, audio=None, video=None, url=""):
    with st.status("Building your study system...", expanded=True) as status:
        st.write("Understanding the source")
        if source_mode == "audio":
            if audio is None:
                raise ValueError("Please record or upload audio first.")
            content = analyze_audio(audio)
            source_name = getattr(audio, "name", "Lecture Audio")
        elif source_mode == "video":
            if video is None:
                raise ValueError("Please upload a video first.")
            content = analyze_video(video)
            source_name = getattr(video, "name", "Lecture Video")
        else:
            if not url.strip():
                raise ValueError("Please enter a YouTube URL.")
            content = analyze_url(url)
            source_name = url
        st.write("Creating notes, flashcards and exam prep")
        pack = analyze_content(content)
        status.update(label="Study pack ready", state="complete")
    st.session_state.study_pack = pack
    st.session_state.source_content = content
    st.session_state.source_name = source_name
    st.session_state.page = "Dashboard"
    st.session_state.flash_index = 0
    st.session_state.show_answer = False
    st.rerun()

topbar()
pack = st.session_state.study_pack

if st.session_state.page == "Dashboard":
    st.markdown('<div class="eyebrow">PERSONAL LEARNING DASHBOARD</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Learn smarter.<br><span style="color:#a879ff">Remember longer.</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-copy">Turn lectures, voice notes and study videos into structured notes, active-recall flashcards, quizzes and exam-ready revision plans.</div>', unsafe_allow_html=True)
    st.write("")
    if not pack:
        a,b,c = st.columns(3)
        with a: stat_card("0","Lectures Processed",True)
        with b: stat_card("0","Flashcards Created")
        with c: stat_card("0","Quiz Accuracy")
        st.write("")
        st.markdown('<div class="panel-purple"><div class="eyebrow">START LEARNING</div><h2>Turn your next lecture into a study system.</h2><p class="muted">Record audio, upload a file, upload video or paste a public YouTube study URL.</p></div>', unsafe_allow_html=True)
        if st.button("✨ Create your first study pack", type="primary", use_container_width=True):
            st.session_state.page = "Create Study Pack"
            st.rerun()
    else:
        cards = pack.get("flashcards", [])
        quiz = pack.get("quiz", [])
        c1,c2,c3,c4 = st.columns(4)
        with c1: stat_card("1","Lecture Processed",True)
        with c2: stat_card(str(len(cards)),"Flashcards Created")
        with c3: stat_card(str(len(pack.get("key_concepts",[]))),"Concepts Learned")
        with c4: stat_card(str(len(quiz)),"Quiz Questions")
        st.write("")
        left,right = st.columns([1.5,1])
        with left:
            st.markdown('<div class="panel"><div class="eyebrow">CURRENT LECTURE</div><h2>'+pack.get("title","Your Lecture")+'</h2><p class="muted">'+pack.get("subject","Study material")+' · '+pack.get("difficulty","Intermediate")+'</p></div>', unsafe_allow_html=True)
            st.write("")
            st.markdown("### Continue studying")
            x,y = st.columns(2)
            with x:
                deck_card("Flashcards", f"{len(cards)} cards ready", min(100, len(cards)*7))
                if st.button("Study cards →", use_container_width=True):
                    st.session_state.page = "Flashcards"; st.rerun()
            with y:
                deck_card("Exam Prep", f"{len(pack.get('exam_questions',[]))} questions", 65)
                if st.button("Prepare for exam →", use_container_width=True):
                    st.session_state.page = "Exam Prep"; st.rerun()
        with right:
            st.markdown('<div class="panel-purple"><div class="eyebrow">AI STUDY INSIGHT</div><h3>What to focus on</h3><p>'+ (pack.get("study_coach") or ["Review the key concepts and test yourself with the quiz."])[0] +'</p></div>', unsafe_allow_html=True)
            st.write("")
            st.markdown("### Quick revision")
            st.info(pack.get("tldr",""))

elif st.session_state.page == "Create Study Pack":
    st.markdown('<div class="eyebrow">CREATE</div><div class="hero-title" style="font-size:44px">Bring your lecture.</div>', unsafe_allow_html=True)
    st.markdown('<p class="hero-copy">Choose any source. LectureLens turns it into a complete study workspace.</p>', unsafe_allow_html=True)
    mode = st.radio("Source", ["🎙 Record", "📁 Upload Audio", "🎬 Upload Video", "🔗 YouTube"], horizontal=True)
    audio = video = None
    url = ""
    if mode == "🎙 Record":
        audio = st.audio_input("Record your lecture")
    elif mode == "📁 Upload Audio":
        audio = st.file_uploader("Drop your lecture audio", type=["wav","mp3","m4a","ogg","flac","aac"])
        if audio: st.audio(audio)
    elif mode == "🎬 Upload Video":
        video = st.file_uploader("Drop your lecture video", type=["mp4","mov","avi","webm"])
        if video: st.video(video)
    else:
        url = st.text_input("Public YouTube URL", placeholder="https://www.youtube.com/watch?v=...")
    st.write("")
    if st.button("✨ Generate Complete Study Pack", type="primary", use_container_width=True):
        try:
            source_mode = "audio" if mode in ["🎙 Record","📁 Upload Audio"] else "video" if mode == "🎬 Upload Video" else "youtube"
            generate(source_mode, audio, video, url)
        except Exception as exc:
            st.error(str(exc))

elif st.session_state.page == "Flashcards":
    if not pack:
        st.info("Create a study pack first.")
    else:
        cards = pack.get("flashcards", [])
        if not cards:
            st.info("No flashcards were generated.")
        else:
            idx = st.session_state.flash_index % len(cards)
            card = cards[idx]
            st.markdown('<div class="eyebrow">ACTIVE RECALL</div><div class="hero-title" style="font-size:44px">Flashcards</div>', unsafe_allow_html=True)
            st.caption(f"Card {idx+1} of {len(cards)} · {pack.get('title','Lecture')}")
            st.write("")
            st.markdown(f'<div class="flashcard"><div class="flashcard-label">QUESTION</div><div class="flashcard-q">{card.get("question","")}</div></div>', unsafe_allow_html=True)
            st.write("")
            if st.session_state.show_answer:
                st.markdown(f'<div class="panel-purple"><div class="eyebrow">ANSWER</div><p style="font-size:18px;line-height:1.7">{card.get("answer","")}</p></div>', unsafe_allow_html=True)
            else:
                if st.button("Reveal Answer", type="primary", use_container_width=True):
                    st.session_state.show_answer = True
                    st.rerun()
            a,b,c = st.columns(3)
            with a:
                if st.button("← Previous", use_container_width=True):
                    st.session_state.flash_index = (idx-1) % len(cards); st.session_state.show_answer=False; st.rerun()
            with b:
                if st.button("✓ Mark Studied", use_container_width=True):
                    st.session_state.studied += 1; st.session_state.flash_index=(idx+1)%len(cards); st.session_state.show_answer=False; st.rerun()
            with c:
                if st.button("Next →", use_container_width=True):
                    st.session_state.flash_index=(idx+1)%len(cards); st.session_state.show_answer=False; st.rerun()

elif st.session_state.page == "Quiz":
    if not pack:
        st.info("Create a study pack first.")
    else:
        quiz = pack.get("quiz", [])
        st.markdown('<div class="eyebrow">KNOWLEDGE CHECK</div><div class="hero-title" style="font-size:44px">Test yourself.</div>', unsafe_allow_html=True)
        answers = {}
        for i,q in enumerate(quiz):
            st.markdown(f"### {i+1}. {q.get('question','')}")
            answers[i] = st.radio("Choose one", q.get("options",[]), key=f"q_{i}")
        if quiz and st.button("Check my score", type="primary", use_container_width=True):
            score = sum(answers.get(i) == q.get("correct_answer") for i,q in enumerate(quiz))
            st.markdown(f'<div class="panel-purple"><h2>{score}/{len(quiz)} correct</h2><p>Accuracy: {round(score/len(quiz)*100)}%</p></div>', unsafe_allow_html=True)
            for i,q in enumerate(quiz):
                if answers.get(i) == q.get("correct_answer"):
                    st.success(f"Q{i+1}: Correct")
                else:
                    st.error(f"Q{i+1}: Correct answer — {q.get('correct_answer')}")
                if q.get("explanation"): st.info(q["explanation"])

elif st.session_state.page == "Exam Prep":
    if not pack:
        st.info("Create a study pack first.")
    else:
        st.markdown('<div class="eyebrow">EXAM MODE</div><div class="hero-title" style="font-size:44px">Prepare with purpose.</div>', unsafe_allow_html=True)
        for i,item in enumerate(pack.get("exam_questions",[])):
            with st.expander(f"{i+1}. {item.get('question','')}"):
                st.markdown("**Answer structure**")
                st.write(item.get("answer_outline",""))
        st.markdown("### Important points")
        for x in pack.get("important_points",[]): st.markdown("• "+x)
        st.markdown("### Common mistakes")
        for x in pack.get("common_mistakes",[]): st.warning(x)

elif st.session_state.page == "Study Coach":
    if not pack:
        st.info("Create a study pack first.")
    else:
        st.markdown('<div class="eyebrow">AI COACH</div><div class="hero-title" style="font-size:44px">Your next best move.</div>', unsafe_allow_html=True)
        for x in pack.get("study_coach",[]):
            st.markdown(f'<div class="panel-purple"><p style="font-size:17px">🧠 {x}</p></div>', unsafe_allow_html=True)
        st.markdown("### Revision plan")
        for i,x in enumerate(pack.get("revision_plan",[])):
            st.markdown(f'<div class="deck"><b>{i+1}</b>&nbsp;&nbsp;{x}</div>', unsafe_allow_html=True)
        st.markdown("### Detailed notes")
        for note in pack.get("detailed_notes",[]):
            with st.expander(note.get("heading","Section")):
                st.write(note.get("explanation",""))
                if note.get("example"): st.info(note["example"])
        if pack.get("definitions"):
            st.markdown("### Definitions")
            for x in pack["definitions"]:
                with st.expander(x.get("term","Term")):
                    st.write(x.get("definition",""))
        if pack.get("formulas"):
            st.markdown("### Formulas")
            for x in pack["formulas"]:
                st.markdown(f'<div class="panel"><h4>{x.get("name","")}</h4><h3>{x.get("formula","")}</h3><p class="muted">{x.get("meaning","")}</p></div>', unsafe_allow_html=True)
