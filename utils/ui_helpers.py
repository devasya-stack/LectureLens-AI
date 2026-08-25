import streamlit as st

def inject_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    *{font-family:Inter,sans-serif}
    .stApp{background:#09070e;color:#f6f2ff}
    .block-container{max-width:1420px;padding:1.1rem 2rem 4rem}
    [data-testid="stSidebar"]{background:#0c0a12;border-right:1px solid #24202e}
    [data-testid="stSidebar"] .block-container{padding:1.5rem 1rem}
    .side-brand{display:flex;align-items:center;gap:12px;margin:5px 0 32px}
    .brand-mark{width:34px;height:34px;border-radius:11px;background:linear-gradient(135deg,#754cff,#b07cff);display:flex;align-items:center;justify-content:center;font-weight:800}
    .brand-name{font-size:18px;font-weight:800}.brand-ai{font-size:8px;letter-spacing:2px;color:#8f879e;margin-top:2px}
    .side-section{font-size:10px;letter-spacing:2px;color:#6f687c;font-weight:800;margin:18px 8px 8px}
    .side-bottom{color:#a48bd1;font-size:12px;margin-top:60px}.side-bottom span{color:#777080;font-size:10px}
    .top-title{font-size:18px;font-weight:700;padding:8px 0}
    .fake-search{background:#11101a;border:1px solid #292432;border-radius:12px;padding:10px 16px;color:#777181}
    .profile{background:#11101a;border:1px solid #292432;border-radius:12px;padding:10px;text-align:center;color:#aaa2b3}
    .eyebrow{font-size:10px;letter-spacing:2px;font-weight:800;color:#9f70ff;text-transform:uppercase}
    .welcome{padding:35px 0 25px}.welcome h1{font-size:55px;line-height:1.03;letter-spacing:-3px;margin:10px 0}.welcome h1 span{color:#a876ff}
    .welcome p,.page-copy{max-width:700px;color:#91899d;line-height:1.7;font-size:15px}
    .stat{background:linear-gradient(145deg,#15111d,#100d16);border:1px solid #292332;border-radius:18px;padding:19px;min-height:105px}
    .stat-number{font-size:28px;font-weight:800}.stat-accent{color:#b487ff}.stat-label{color:#81798d;font-size:10px;text-transform:uppercase;letter-spacing:1.5px;margin-top:7px}
    .feature-panel,.lesson-card,.coach-card,.big-card,.answer-card,.score-card{background:linear-gradient(145deg,#171220,#100d16);border:1px solid #30253d;border-radius:24px;padding:28px}
    .feature-panel{display:flex;gap:22px;align-items:center;background:radial-gradient(circle at 85% 10%,rgba(148,83,255,.22),transparent 35%),#14101b}
    .feature-icon{font-size:35px;color:#a56fff}.feature-panel p{color:#8f879a}
    .lesson-top{display:flex;justify-content:space-between}.pill{background:#24163b;color:#b98cff;border-radius:99px;padding:6px 10px;font-size:9px;font-weight:800;letter-spacing:1px}
    .muted{color:#81798d}.lesson-card h2{font-size:26px;margin:22px 0 5px}.lesson-card p{color:#8d8597}
    .lesson-progress,.progress{height:6px;background:#292332;border-radius:10px;overflow:hidden;margin-top:22px}.lesson-progress div,.progress div{height:100%;background:linear-gradient(90deg,#754cff,#b77cff)}
    .lesson-footer{display:flex;justify-content:space-between;color:#777080;font-size:11px;margin-top:8px}
    .deck{background:#12101a;border:1px solid #292432;border-radius:18px;padding:18px;min-height:120px}.deck-title{font-weight:700;font-size:16px}.deck-meta{font-size:12px;color:#80798b;margin-top:7px}
    .coach-card{min-height:290px;background:radial-gradient(circle at 75% 35%,rgba(145,75,255,.25),transparent 34%),#120f19}.coach-card h2{margin-top:10px}.coach-card p{color:#8f8799;line-height:1.6}
    .orb{margin:20px auto;width:82px;height:82px;border-radius:50%;background:radial-gradient(circle,#b47cff,#5a20a1 45%,#180c29 72%);display:flex;align-items:center;justify-content:center;font-size:30px;box-shadow:0 0 45px rgba(157,89,255,.45)}
    .big-card{min-height:330px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;margin-top:15px;background:radial-gradient(circle at 50% 0%,rgba(147,83,255,.20),transparent 45%),#14101b}
    .card-label{font-size:10px;letter-spacing:2px;color:#9f70ff;font-weight:800}.question{font-size:29px;font-weight:700;max-width:800px;line-height:1.3;margin-top:22px}
    .answer-card{margin:15px 0;line-height:1.7;color:#bcb4c8}.score-card{text-align:center;margin:20px 0}.score{font-size:60px;font-weight:800;color:#b487ff}.score-card p{color:#898191}
    .coach-line{background:#15111d;border:1px solid #292332;border-radius:15px;padding:18px;margin:10px 0;color:#c9c1d0}
    .plan{display:flex;gap:18px;align-items:center;background:#12101a;border:1px solid #292432;border-radius:15px;padding:18px;margin:8px 0}
    div[data-baseweb="tab-list"]{background:#11101a;padding:6px;border-radius:15px}
    div[data-testid="stExpander"]{background:#11101a;border:1px solid #292432;border-radius:14px}
    div[data-testid="stFileUploader"]{background:#100d17;border:1px dashed #4a3960;border-radius:18px}
    .stButton>button{border-radius:11px;min-height:43px;font-weight:650;border-color:#2b2534}
    button[kind="primary"]{background:linear-gradient(100deg,#7449ff,#a36dff)!important;border:none!important;color:white!important;box-shadow:0 10px 30px rgba(116,73,255,.25)}
    </style>
    """,unsafe_allow_html=True)

def stat_card(number,label,accent=False):
    cls="stat-number stat-accent" if accent else "stat-number"
    st.markdown(f'<div class="stat"><div class="{cls}">{number}</div><div class="stat-label">{label}</div></div>',unsafe_allow_html=True)

def deck_card(title,meta,progress=0):
    st.markdown(f'<div class="deck"><div class="deck-title">{title}</div><div class="deck-meta">{meta}</div><div class="progress"><div style="width:{max(0,min(100,progress))}%"></div></div></div>',unsafe_allow_html=True)
