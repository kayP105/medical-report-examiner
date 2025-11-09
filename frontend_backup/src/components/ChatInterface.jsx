import React, { useState } from 'react';
import axios from 'axios';
import { FiSend } from 'react-icons/fi';

const ChatInterface = ({ reportContext }) => {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        'Hi! I can answer questions about your medical report. Try asking: "Is my cholesterol normal?" or "What does LDL mean?"'
    }
  ]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/chat', {
        question: userMessage.content,
        report_context: reportContext || ""  // Ensure it's never undefined
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.answer
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMsg = error.response?.data?.detail || 'Sorry, I encountered an error. Please try again.';
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: errorMsg }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const onKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={`message ${m.role}`}>
            <div className="message-content">{m.content}</div>
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="message-content">
              <span className="typing">
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
              </span>
            </div>
          </div>
        )}
      </div>

      <div className="chat-input-container">
        <input
          className="chat-input"
          placeholder="Ask about your report…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          disabled={loading}
        />

        <button
          className="chat-button"
          onClick={handleSend}
          disabled={loading || !input.trim()}
          aria-label="Send message"
          title="Send"
        >
          <FiSend />
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;


