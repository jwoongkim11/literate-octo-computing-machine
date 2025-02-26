import streamlit as st
import google.generativeai as genai
import PyPDF2
import io

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def initialize_gemini(api_key):
    genai.configure(api_key=api_key)
    
    # 사용 가능한 모델 목록 확인
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            st.write(f"사용 가능한 모델: {m.name}")
    
    # 정확한 모델 이름 사용
    model = genai.GenerativeModel('models/gemini-2.0-flash')
    return model

st.title("부동산 전문가 챗봇 🏠")

# API 키 입력
api_key = st.text_input("Google API 키를 입력하세요:", type="password")

# PDF 파일 업로드
pdf_file = st.file_uploader("PDF 파일을 업로드하세요", type=['pdf'])
pdf_text = ""

if pdf_file is not None:
    pdf_text = extract_text_from_pdf(pdf_file)
    st.success("PDF 파일이 성공적으로 업로드되었습니다!")

if api_key:
    try:
        model = initialize_gemini(api_key)
        
        # 초기 프롬프트 설정
        system_prompt = f"""
        당신은 부동산 전문가입니다. 다음 문서를 참고하여 사용자의 질문에 답변해주세요:
        {pdf_text}
        
        전문적이고 정확한 답변을 제공해주세요.
        """
        
        # 채팅 기록 초기화
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # 이전 대화 표시
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # 사용자 입력
        if prompt := st.chat_input("질문을 입력하세요"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Gemini 응답 생성
            full_prompt = system_prompt + "\n\n사용자: " + prompt
            response = model.generate_content(full_prompt)
            
            # 응답 표시
            with st.chat_message("assistant"):
                st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"오류가 발생했습니다: {str(e)}")
else:
    st.warning("API 키를 입력해주세요.")
