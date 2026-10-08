# 🎬 AniMaze

### Anime discovery & streaming website

**AniMaze** is a full-stack anime website where users can discover anime, search for their favorite shows, view details, and stream episodes with subtitles and SUB/DUB support.

🌐 **Live Website:** https://ani-maze.vercel.app  
💻 **Source Code:** https://github.com/kaustuk.lol/AniMaze

> ⚠️ The original website was working when it was deployed. Some streaming features may not work now because the project depends on third-party APIs and streaming services that can change over time.

---

## ✨ Features

- 🔥 Trending anime
- 🔎 Search for anime
- 📖 Anime details and information
- 🎬 Episode listing
- ▶️ Online video streaming
- 🎙️ SUB / DUB support
- 📝 Subtitle support
- ⏭️ Next episode navigation
- 🎯 Recommended anime
- 📱 Responsive design
- ⚡ Fast API requests using asynchronous Python

---

## 🛠️ Tech Stack

### Frontend
- HTML
- CSS
- JavaScript
- Tailwind CSS

### Backend
- Python
- FastAPI
- Jinja2

### APIs
- AniList GraphQL API
- Consumet API

### Video
- HLS.js
- Plyr

### Deployment
- Vercel

---

## 🧩 How It Works

AniMaze connects different services to create the complete experience.

```text
                AniMaze
                   │
          ┌────────┴────────┐
          │                 │
      AniList            Consumet
          │                 │
   Anime information    Episodes
   Ratings              Streaming
   Genres               Sources
          │                 │
          └────────┬────────┘
                   │
                FastAPI
                   │
                   ▼
              AniMaze UI
                   │
                   ▼
             HLS Video Player
```

---

## 🎥 Streaming

One of the main parts of AniMaze is its video player.

The website gets the available episode source and sends it to an HLS-based player.

It supports:

- Video playback
- Subtitles
- SUB/DUB switching
- Episode switching
- Next episode navigation

---

## ⚡ What I Learned

Building AniMaze helped me understand how real web applications work.

I learned about:

- Building APIs with FastAPI
- Connecting multiple APIs together
- Using GraphQL
- Making asynchronous requests
- Working with video streams
- Handling subtitles
- Creating dynamic web pages
- Deploying a backend on Vercel
- Handling problems caused by third-party APIs

---

## 🏗️ Project Structure

```text
AniMaze/
│
├── main.py              # FastAPI backend
│
├── utils/
│   └── api.py           # API functions
│
├── templates/           # Website pages
│
├── static/              # CSS, JavaScript & assets
│
├── requirements.txt     # Python dependencies
│
├── vercel.json          # Vercel configuration
│
└── Dockerfile
```

---

## 💡 Why I Built It

I wanted to build something more than a simple frontend project.

Instead of only displaying information from an API, I wanted to understand how a complete application works:

```text
Frontend
   ↓
Backend
   ↓
APIs
   ↓
Data Processing
   ↓
Video Streaming
   ↓
User
```

AniMaze was one of my projects that helped me learn how different parts of web development work together.

---

## 🚀 Future Improvements

If I continue working on AniMaze, I would like to add:

- 👤 User accounts
- ❤️ Watchlist
- 📺 Watch history
- 🔖 Continue Watching
- ⭐ Favorites
- 🤖 Better recommendations
- ⚡ Caching for faster loading
- 🧪 Automated testing
- 📱 Better mobile experience

---

## 👨‍💻 Developer

**kaustuk.lol**

Built with ❤️, Python, JavaScript and a lot of debugging.

⭐ If you like the project, consider giving it a star!

---

### 📌 Note

AniMaze is an educational project. It does not host anime content itself and relies on external services for anime information and streaming data.
