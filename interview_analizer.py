from langchain_openai import ChatOpenAI
from openai import OpenAI

from langchain.schema import SystemMessage, HumanMessage
import streamlit as st
import os
from database import Database

# Initialize Database
db = Database()

st.set_page_config(page_title="Interview Analyzer", page_icon="🎙️")
st.title("🎙️ Interview Analyzer")
st.markdown("Upload a job interview recording to get a transcription and analysis.")

uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a", "mp4"])

if uploaded_file is not None:
    # Save file temporarily
    file_path = f"temp_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.info(f"File '{uploaded_file.name}' uploaded successfully. Processing...")
    
    try:
        # 1. Transcribe using OpenAI Whisper (via client)
        st.subheader("Transcription")
        with st.spinner("Transcribing..."):
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            with open(file_path, "rb") as audio_file:
                transcription_response = client.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file
                )
            transcription_text = transcription_response.text
        
        st.success("Transcription complete!")
        st.text_area("Transcript", transcription_text, height=300)
        
        # Save to DB
        interview_id = db.save_transcription(uploaded_file.name, transcription_text)
        
        # 2. Analyze using GPT
        st.subheader("Analysis")
        with st.spinner("Analyzing from the interviewee's perspective..."):
            chat_model = ChatOpenAI(model="gpt-4o", temperature=0.5)
            
            messages = [
                SystemMessage(content="You are an expert HR consultant. Analyze the following job interview transcript from the perspective of the interviewee. Highlight strengths, weaknesses, and potential improvements."),
                HumanMessage(content=f"Transcript:\n{transcription_text}")
            ]
            
            analysis_response = chat_model.invoke(messages)
            analysis_text = analysis_response.content
            
        st.success("Analysis complete!")
        st.markdown(analysis_text)
        
        # Update DB with analysis
        if interview_id:
            db.update_analysis(interview_id, analysis_text)
            st.info("Results saved to database.")
            
    except Exception as e:
        st.error(f"An error occurred: {e}")
        
    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
