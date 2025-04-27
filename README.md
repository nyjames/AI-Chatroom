# AI - Chat Room
 
# 💬 Flask Chat App with OpenAI Integration

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Flask-2.2-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)
![OpenAI](https://img.shields.io/badge/OpenAI-API-blueviolet)

This is a real-time chat application built with Flask and Flask-SocketIO. It supports user authentication, multiple chat rooms, message persistence with SQLite, and includes an AI chatbot powered by OpenAI's GPT-3.5.

---

## Features

- **GPT Integration** — Ask the bot anything by mentioning `@bot` in a chat.
- **User Authentication** — Register, log in, and log out securely.
- **Real-Time Messaging** — Powered by WebSockets using Flask-SocketIO.
- **Chat History** — Stores messages per room in a SQLite database.
- **Multiple Rooms** — Chat in different rooms by switching via query params.
- **Dynamic User Lists** — Shows active users per room in real time.

---

## App Flow

1. Users register or log in.

2. After logging in, users are directed to the default lobby (index.html) that asks for Chatroom ID.

3. Messages are stored and broadcast live to everyone in the room.

4. If a message starts with `@bot`, it triggers a call to OpenAI and replies back with AI-generated content.

---

1. **Clone the repo**:
    ```bash
    git clone hhttps://github.com/nyjames/AI-Chatroom.git

    cd AI-Chatroom
    ```

2. **Create virtual environment & install dependencies**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. **Set your environment variables**:
    Create a `.env` file in the root with the following:

    ```
    OPENAI_API_KEY=sk-...
    ```
    Where you can insert your OpenAI API Key.

4. **Run the app**:
    ```
    flask run
    ```
    or

    ```
    python app.py
    ```
---

## GPT Integration

The app uses OpenAI's GPT-3.5 to respond to messages that begin with `@bot`.  
Make sure you have a valid API key and proper billing set up at [OpenAI Platform](https://platform.openai.com/).

---

## License

MIT License.

---

## Contributing

Pull requests are welcome! For major changes, open an issue first to discuss what you'd like to change.

---
