import React, { useState } from "react";
import "../styles/ChatBox.css";

function ChatBox() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [promptCount, setPromptCount] = useState(0);  // Track prompts sent

  const MAX_PROMPTS = 5;

  const sendQuestion = async () => {
    if (!question.trim() || promptCount >= MAX_PROMPTS) return;

    const userMsg = { role: "user", text: question };
    setMessages((prev) => [...prev, userMsg]);
    setQuestion("");
    setLoading(true);
    setPromptCount((count) => count + 1);

    try {
      const res = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
      });

      const data = await res.json();

      const botMsg = { role: "bot", text: data.answer };
      setMessages((prev) => [...prev, botMsg]);

      if (data.note) {
        setMessages((prev) => [...prev, { role: "note", text: data.note }]);
      }
    } catch (err) {
      setMessages((prev) => [...prev, { role: "error", text: "Error contacting backend" }]);
    } finally {
      setLoading(false);
    }
  };

  // Filter messages to show only last 3 user prompts, but all other roles
  const displayedMessages = messages.filter((msg, idx) => {
    if (msg.role !== "user") return true;
    // Get all user messages indexes
    const userMessages = messages.filter(m => m.role === "user");
    const lastThreeUserMessages = userMessages.slice(-3);
    return lastThreeUserMessages.includes(msg);
  });

  return (
    <div className="chat-container">
      <div className="messages">
        {displayedMessages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {msg.text}
          </div>
        ))}
        {loading && <div className="message bot">...</div>}
      </div>
      <div className="input-box">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={promptCount >= MAX_PROMPTS ? "Max 5 prompts reached" : "Ask something..."}
          onKeyPress={(e) => e.key === "Enter" && sendQuestion()}
          disabled={promptCount >= MAX_PROMPTS}
        />
        <button onClick={sendQuestion} disabled={promptCount >= MAX_PROMPTS}>
          Send
        </button>
      </div>
    </div>
  );
}

export default ChatBox;
