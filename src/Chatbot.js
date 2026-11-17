import { useState, useRef, useEffect } from "react";
import "./chat.css";

const USER_ID = "user_" + Math.random().toString(36).slice(2, 9);

export default function Chatbot() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [typing, setTyping] = useState(false);
  const chatEndRef = useRef(null);

  // Auto-scroll
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  // Greet when opened
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      sendAuto();
    }
  }, [isOpen]);

  const closeChat = () => {
    setMessages([]);
    setInput("");
    setIsOpen(false);
  };

  // 🔥 Auto greeting
  const sendAuto = async (text) => {
    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          user_id: USER_ID,
          message: text
        })
      });

      const data = await res.json();

      setMessages([
        { sender: "bot", text: data?.reply || "Hello!" }
      ]);

    } catch (err) {
      setMessages([
        { sender: "bot", text: "❌ Cannot connect to backend" }
      ]);
    }
  };

  // 🔥 Send message
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userText = input.trim();
    console.log("Sending:", userText);

    setMessages(prev => [
      ...prev,
      { sender: "user", text: userText }
    ]);

    setInput("");
    setTyping(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          user_id: USER_ID,
          message: userText
        })
      });

      const data = await res.json();
      console.log("Response:", data);

      setTyping(false);

      setMessages(prev => [
        ...prev,
        { sender: "bot", text: data?.reply || "⚠️ No response" }
      ]);

    } catch (err) {
      console.error(err);

      setTyping(false);

      setMessages(prev => [
        ...prev,
        { sender: "bot", text: "❌ Backend not reachable" }
      ]);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  return (
    <>
      {/* Toggle button */}
      <div className="chat-toggle" onClick={() => setIsOpen(o => !o)}>
        {isOpen ? "✖" : "💬"}
      </div>

      {isOpen && (
        <div className="chat-wrapper">

          {/* Header */}
          <div className="chat-header">
            <div className="chat-header-left">
              <div className="chat-header-avatar">🤖</div>
              <div className="chat-header-info">
                <span className="chat-header-name">VidhyaGhar AI</span>
                <span className="chat-header-status">
                  <span className="status-dot" />
                  Online
                </span>
              </div>
            </div>
            <button className="chat-header-close" onClick={closeChat}>
              ✖
            </button>
          </div>

          {/* Messages */}
          <div className="chat-box">
            {messages.map((msg, i) => (
              <div key={i} className={`message ${msg.sender}`}>
                {msg.text}
              </div>
            ))}

            {typing && (
              <div className="message bot">Typing...</div>
            )}

            <div ref={chatEndRef} />
          </div>

          {/* Input */}
          <div className="chat-input">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Ask something..."
            />
            <button onClick={sendMessage}>➤</button>
          </div>

        </div>
      )}
    </>
  );
}