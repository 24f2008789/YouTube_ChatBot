from flask import Flask, request,jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi,NoTranscriptFound,TranscriptsDisabled
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
import os

load_dotenv()
hf_token = os.getenv("HUGGINGFACEHUB_ACCESS_TOKEN")
llm = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
    huggingfacehub_api_token=hf_token
)

model = ChatHuggingFace(llm=llm)


app = Flask(__name__)
CORS(app)

transcript_cache = {}
def get_transcript(video_id):
    if video_id in transcript_cache:
        return transcript_cache[video_id]
    try:
        ytt = YouTubeTranscriptApi()
        transcript_list = ytt.fetch(video_id, languages=['en'])  

        full_text = "".join(snip.text for snip in transcript_list.snippets)
        transcript_cache[video_id] = full_text
        return full_text
    
    except NoTranscriptFound:
        return None
    except TranscriptsDisabled:
        return None
    except:
        return None
    
def format_docs(retireve_docs):
    docs = "\n\n".join([doc.page_content for doc in retireve_docs])
    return docs

vector_store_cache = {}
def get_vector_store(video_id, transcript):
    if video_id in vector_store_cache:
        return vector_store_cache[video_id]
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.create_documents([transcript])

    embedding = HuggingFaceEmbeddings(model_name='sentence-transformers/all-mpnet-base-v2')
    vector_store = Chroma.from_documents(chunks,embedding)
    vector_store_cache[video_id] = vector_store
    return vector_store

@app.route("/query", methods=["POST"])
def main():
    data = request.get_json()
    question = data.get("question")
    video_id = data.get("you_tube_id")

    print("process started")
    # data sourcing from youtube video into text
    transcript = get_transcript(video_id)
    if (not transcript):
        return jsonify(message="No transcript for this video")
    

    vector_store = get_vector_store(video_id,transcript)
    print("vector_store got")


    # retriver 
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})


    prompt = PromptTemplate(
        template="""
    You are very helpful AI assisstant. Which help students to clear doubts form the given context.
    Explain user query in simple language.
    Answer ONLY from the provided transcript context.
    If the context is insufficient, just say you don't know.

    {context}
    Question: {question} 
    """,
    input_variables=["context","question"]
    )
    
    retrieve_docs = retriever.invoke(question)
    
    new_docs = format_docs(retrieve_docs)

    final_prompt = prompt.invoke({'context' : new_docs , 'question' : question})
    
    print("inside model invoke")
    answer = model.invoke(final_prompt)
    
    print("answer sned to javascript")

    return jsonify(message=answer.content)

if __name__ == "__main__":
    app.run(debug=True)

