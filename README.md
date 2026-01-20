# YouTube Chatbot Chrome Extension

A Chrome Extension that allows users to query YouTube videos using natural language. The extension extracts the video transcript and uses an LLM with RAG (Retrieval Augmented Generation) to provide accurate answers based on the actual video content.

## Features

 - Ask questions about any YouTube video
 - Summarizes the video automatically
 - Retrieves relevant transcript chunks using RAG
 - Uses Large Language Model (LLM) for responses
 - Works directly inside YouTube as a floating UI
 - No need to manually copy video links or text

## Architecture Overview

The system consists of 2 main components:

### 1. Chrome Extension (Frontend)

 - Built with JavaScript + HTML + CSS
 - Injects a UI on YouTube pages
 - Extracts the videoId from the current URL
 - Sends user queries to the backend
 - Displays model responses in chat format

### 2. Backend Server

 - Fetches YouTube transcript based on videoId
 - Splits transcript into chunks for retrieval
 - Applies RAG (Retrieval Augmented Generation) pipeline:
 - Retrieve relevant transcript chunks
 - Augment the LLM prompt with retrieved context
 - Generate final answer using the LLM
 - Runs an LLM locally or via API (HuggingFace, etc.)

## Tech Stack

**Frontend:** JavaScript, Chrome Extensions API  
**Backend:** Flask / Python (LLM server)  
**ML:** RAG Pipeline + LLM ( Local Model)  
**Data Source:** YouTube Transcript
