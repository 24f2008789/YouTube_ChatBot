const input_box  = document.getElementById("userinput");
const button = document.getElementById("sendBtn");
const chatWindow = document.querySelector(".chat-window");

let isProcessing = false;

button.addEventListener("click", user_message);
input_box.addEventListener("keypress", function(e){
    if (e.key === "Enter") user_message();
});

async function getVideoId() {
    return new Promise((resolve, reject) => {
        chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
            const url = new URL(tabs[0].url);
            const id = url.searchParams.get("v");
            resolve(id);
        });
    });
}

function user_message() {
    if (isProcessing) return;
    const text = input_box.value.trim();
    if (!text) return;

    show_message(text, "user");
    input_box.value = "";
    call_ai(text);
}

function show_message(msg, sender) {
    const div = document.createElement("div");
    div.classList.add(sender === "user" ? "user-msg" : "bot-msg");
    div.textContent = msg;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return div
}

async function call_ai(query){
    const video_id = await getVideoId();
    if (!video_id){
        show_message("Please open a YouTube video to use the assistant", "bot");
        userinput.disabled = true;
        sendBtn.disabled = true;
        return;
    }
    
    isProcessing = true;
    sendBtn.disabled = false;
    const inital_message = show_message("Thinking...", "bot");

    const data = {
        question: query,
        you_tube_id: video_id
    };

    try {
        const response = await fetch("http://localhost:5000/query",{
            method:"POST",
             headers: {
                "Content-Type": "application/json"
            },
            body:JSON.stringify(data)
        })
        
        const result = await response.json();
        
        // remove the "Thinking..."
        inital_message.textContent = result.message;

    } catch (err) {
        inital_message.textContent = "Error: " + err.message;
    }
    isProcessing = false;
    button.disabled = false;
}
