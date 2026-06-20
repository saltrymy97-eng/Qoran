const { useState, useRef, useEffect } = React;

function App() {
    const [messages, setMessages] = useState([
        { role: 'bot', content: 'مرحباً بك في المساعد الذكي لجامعة القرآن الكريم - فرع غيل باوزير. تفضل بطرح استفسارك.' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const chatRef = useRef(null);

    useEffect(() => {
        if (chatRef.current) {
            chatRef.current.scrollTop = chatRef.current.scrollHeight;
        }
    }, [messages]);

    const sendMessage = async (text) => {
        if (!text || !text.trim() || loading) return;
        const q = text.trim();
        setMessages(prev => [...prev, { role: 'user', content: q }]);
        setInput('');
        setLoading(true);

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: q })
            });
            const data = await res.json();
            setMessages(prev => [...prev, { role: 'bot', content: data.reply || 'عذراً، حدث خطأ.' }]);
        } catch (e) {
            setMessages(prev => [...prev, { role: 'bot', content: '⚠️ خطأ في الاتصال بالخادم.' }]);
        }
        setLoading(false);
    };

    const quickActions = [
        { icon: '📅', label: 'الجداول', question: 'أريد الاستفسار عن جداول المحاضرات' },
        { icon: '📝', label: 'الامتحانات', question: 'ما هي مواعيد وترتيبات الامتحانات؟' },
        { icon: '📞', label: 'التواصل', question: 'كيف يمكنني التواصل مع إدارة الفرع؟' },
        { icon: '🎓', label: 'التخصصات', question: 'ما هي التخصصات الأكاديمية المتاحة؟' }
    ];

    return (
        <div className="container">
            <div className="basmala">بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ</div>
            <div className="uni-title">🕌 جامعة القرآن الكريم<br/>والعلوم الإسلامية</div>
            <div className="branch-title">✦ فرع غيل باوزير - حضرموت ✦</div>

            <div className="btn-row">
                {quickActions.map((action, i) => (
                    <button key={i} className="btn" onClick={() => sendMessage(action.question)}>
                        {action.icon} {action.label}
                    </button>
                ))}
            </div>

            <div className="quran-verse">﴿وَقُل رَّبِّ زِدْنِي عِلْمًا﴾</div>

            <div className="chat-box" ref={chatRef}>
                {messages.map((msg, i) => (
                    <div key={i} className={`chat-msg ${msg.role === 'user' ? 'user-msg' : 'bot-msg'}`}>
                        {msg.role === 'user' ? '🧑‍🎓 ' : '🤖 '}
                        {msg.content}
                    </div>
                ))}
                {loading && <div className="chat-msg bot-msg">⏳ جاري الرد...</div>}
            </div>

            <div className="input-row">
                <input
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage(input)}
                    placeholder="✍️ اكتب سؤالك هنا..."
                    disabled={loading}
                />
                <button className="send-btn" onClick={() => sendMessage(input)} disabled={loading}>
                    ➤
                </button>
            </div>

            <div className="footer">المطور: سالم التريمي</div>
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('root'));
