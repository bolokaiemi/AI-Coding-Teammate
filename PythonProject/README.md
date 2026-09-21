# 🤖 AI Coding Teammate

AI Coding Teammate is an AI-powered development assistant designed to work alongside developers like a real programming teammate.

It helps developers analyze code, detect errors, understand bugs, receive correction suggestions, communicate through chat and voice, and share visual development context such as a screen, camera feed, images, or videos.

The project is especially designed for freelancers, independent developers, students, and remote developers who want an intelligent development partner while working on software projects.

---

## 🚀 Project Vision

Developers working alone do not always have another programmer available to review their code, discuss an error, or help debug a difficult problem.

AI Coding Teammate is designed to fill that gap.

Instead of functioning only as a traditional chatbot, the application is designed to act more like a collaborative development partner.

A developer can:

- Write or paste code
- Ask questions about the code
- Run code analysis
- Find programming errors
- Request code corrections
- Ask for explanations
- Share their screen
- Use their camera
- Upload images or videos
- Communicate using voice
- Manage development projects and files

The AI teammate can then analyze the available context and provide development assistance.

---

# ✨ Main Features

## 💻 Code Editor

The built-in code editor allows developers to write, edit, save, and analyze source code directly inside the workspace.

Planned and supported functionality includes:

- Code editing
- File selection
- Save project files
- Run code
- Send code for AI analysis
- Apply AI-generated corrections

---

## 🤖 AI Coding Assistant

The AI teammate communicates with the developer through an integrated chat interface.

Developers can ask the AI to:

- Explain code
- Find errors
- Correct code
- Review code
- Suggest improvements
- Explain programming concepts
- Assist with debugging
- Discuss project architecture

Quick actions are available for common development tasks such as:

- 💡 Explain Code
- 🐛 Find Error
- 🛠 Correct Code
- 🔍 Review Code

---

## 👁️ AI Visualizer

The AI Visualizer provides a dedicated area for understanding AI analysis.

The visualizer contains different views for:

### Analysis

Displays the AI's overall analysis of the selected code.

### Errors

Displays detected programming problems and possible causes.

### Code Flow

Provides a visual representation of how code moves through important operations.

### Correction

Displays the original code alongside the AI's suggested corrected version.

### Screen Analysis

Allows visual feedback when screen-sharing functionality is active.

---

## 🖥️ Screen Sharing

AI Coding Teammate is designed to allow developers to share their screen with the AI assistant.

The browser uses:

```javascript
navigator.mediaDevices.getDisplayMedia()
```

to request permission to capture the user's screen.

Captured visual information can then be processed and sent to the AI analysis system.

This allows the AI teammate to understand more than just manually pasted code.

---

## 📷 Camera Support

Camera sharing allows users to provide additional visual context.

The browser can access the camera using:

```javascript
navigator.mediaDevices.getUserMedia()
```

Camera access requires explicit browser permission from the user.

---

## 🖼️ Image and Video Upload

Users can upload images and videos for AI-assisted analysis.

Examples include:

- Screenshots of programming errors
- IDE screenshots
- Terminal output
- Application interfaces
- Development diagrams
- Recorded demonstrations

---

## 🎤 Voice Communication

AI Coding Teammate includes support for voice-based interaction.

The interface provides:

- Voice input
- Listening status
- Start/stop voice controls
- AI chat integration

This allows developers to communicate with their AI teammate without always typing.

---

# 🗂️ Project Management

The workspace contains a project panel for managing development files.

Supported interface features include:

- New file
- New folder
- Upload files
- Search project files
- Select project files
- View programming-language information
- AI project memory status

Example project files may include:

```text
main.py
app.py
requirements.txt
README.md
templates/
static/
```

---

# 📊 Dashboard

The dashboard provides an overview of the developer's activity.

It can display information such as:

- Projects
- Development sessions
- AI analyses
- AI sessions
- Recent projects
- Development tools

The dashboard also provides quick access to:

- Code Editor
- AI Visualizer
- Screen Sharing
- Camera
- Workspace

---

# ⚙️ Account Settings

Users can configure their AI Coding Teammate experience from the Settings page.

Settings include:

## Profile

- First name
- Last name
- Email address
- Developer role

## AI Teammate

Users can configure AI behavior such as:

- Balanced responses
- Concise responses
- Detailed responses
- Teaching / step-by-step responses
- Code explanation level
- Automatic code analysis
- Visual explanations

## Notifications

Notification preferences can include:

- Email notifications
- Analysis notifications
- Product updates

## Security

Security options include:

- Password reset
- Account protection information
- Account deletion controls

---

# 🔐 Authentication

The application includes authentication functionality for managing user accounts.

Authentication pages include:

```text
Login
Register
Forgot Password
Reset Password
```

Authentication is integrated with Flask and Jinja templates.

---

# ⚠️ Error Handling

Custom error pages are included for common application errors.

## 404 — Page Not Found

Displayed when a requested route or resource cannot be found.

## 500 — Server Error

Displayed when the Flask application encounters an unexpected server-side error.

The error pages maintain the same visual design as the rest of AI Coding Teammate.

---

# 🔒 Privacy and Legal Pages

The project includes:

```text
datenschutz.html
impressum.html
```

These provide the structure for German privacy and legal information.

Before production deployment, all legal placeholders must be replaced with the correct operator, hosting, service-provider, and business information.

---

# 🛠️ Technology Stack

## Backend

- Python
- Flask
- Flask Blueprints
- Flask-Login
- Jinja2
- SQLAlchemy
- SQLite / SQL database

## Frontend

- HTML5
- CSS3
- JavaScript
- Jinja2 Templates

## Real-Time Communication

The architecture can support technologies such as:

- WebSockets
- Flask-SocketIO

## AI / Multimodal Layer

The AI layer is designed to support:

- Large Language Models
- Code analysis models
- Multimodal AI models
- Image analysis
- Screen analysis
- Camera-frame analysis

---

# 📁 Project Structure

```text
ai-coding-teammate/
│
├── app.py
├── config.py
├── README.md
├── requirements.txt
├── .env
│
├── routes/
│   ├── __init__.py
│   ├── main_routes.py
│   ├── auth_routes.py
│   ├── dashboard_routes.py
│   ├── workspace_routes.py
│   ├── project_routes.py
│   └── api_routes.py
│
├── database/
│   ├── __init__.py
│   ├── database.py
│   └── models.py
│
├── services/
│   ├── __init__.py
│   ├── user_service.py
│   ├── project_service.py
│   ├── code_service.py
│   ├── chat_service.py
│   ├── analysis_service.py
│   ├── screen_service.py
│   ├── camera_service.py
│   └── file_service.py
│
├── ai/
│   ├── __init__.py
│   └── ...
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── forgot_password.html
│   ├── reset_password.html
│   ├── dashboard.html
│   ├── settings.html
│   ├── workspace.html
│   ├── datenschutz.html
│   ├── impressum.html
│   │
│   ├── workspace/
│   │   ├── project_panel.html
│   │   ├── code_editor.html
│   │   ├── visualizer.html
│   │   └── chat.html
│   │
│   └── errors/
│       ├── 404.html
│       └── 500.html
│
├── static/
│   ├── css/
│   │   ├── style.css
│   │   ├── dashboard.css
│   │   ├── settings.css
│   │   ├── workspace.css
│   │   ├── project_panel.css
│   │   ├── code-editor.css
│   │   ├── visualizer.css
│   │   ├── chat.css
│   │   ├── error.css
│   │   └── datenimpress.css
│   │
│   └── js/
│       ├── app.js
│       ├── dashboard.js
│       ├── websocket.js
│       ├── code-editor.js
│       ├── code-analysis.js
│       ├── visualizer.js
│       ├── chat.js
│       ├── screen-share.js
│       ├── camera.js
│       ├── image-video.js
│       ├── voice.js
│       └── project.js
│
└── tests/
    └── ...
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone <your-repository-url>
```

Move into the project directory:

```bash
cd ai-coding-teammate
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

---

# 📦 Install Dependencies

Install the dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

Depending on the AI and real-time features enabled in your version of the project, packages may include Flask, SQLAlchemy, Flask-Login, Flask-SocketIO, dotenv, Pillow, Transformers, and other AI dependencies.

The project's `requirements.txt` should remain the authoritative dependency list.

---

# 🔑 Environment Variables

Create a `.env` file in the project root.

Example:

```env
SECRET_KEY=replace-with-a-secure-secret-key
DATABASE_URL=sqlite:///ai_coding_teammate.db

# Add only the AI/API credentials actually used by your application.
AI_API_KEY=your-api-key
```

Never commit real API keys or passwords to GitHub.

Add `.env` to `.gitignore`:

```gitignore
.env
.venv/
venv/
__pycache__/
*.pyc
instance/
```

---

# ▶️ Running the Application

Depending on your Flask setup, start the application with:

```bash
python app.py
```

Or:

```bash
flask --app app run --debug
```

Then open:

```text
http://127.0.0.1:5000
```

---

# 🧠 How AI Analysis Works

A typical code-analysis workflow is:

```text
Developer
    │
    ▼
Code Editor
    │
    ▼
JavaScript
    │
    ▼
Flask Backend
    │
    ▼
Analysis Service
    │
    ▼
AI Layer
    │
    ▼
AI Response
    │
    ├── Explanation
    ├── Errors
    ├── Correction
    └── Suggestions
    │
    ▼
Visualizer + AI Chat
```

---

# 👁️ Multimodal Analysis Architecture

For screen or camera analysis, the frontend can capture visual frames.

```text
Camera / Screen
       │
       ▼
Browser Media API
       │
       ▼
Video Element
       │
       ▼
Hidden Canvas
       │
       ▼
Captured Frame
       │
       ▼
WebSocket / Backend
       │
       ▼
Multimodal AI Model
       │
       ▼
Analysis
       │
       ▼
AI Visualizer / Chat
```

This architecture allows the AI teammate to understand visual development context in addition to text and source code.

---

# 🔐 Security Considerations

AI Coding Teammate may process source code, files, prompts, screenshots, and other development information.

Production deployments should therefore implement appropriate security controls.

Important considerations include:

- Hash passwords securely
- Protect authenticated routes
- Validate uploaded files
- Restrict upload size
- Validate file names and paths
- Prevent directory traversal
- Protect forms against CSRF
- Use secure session cookies
- Use HTTPS in production
- Validate WebSocket connections
- Apply rate limiting where appropriate
- Protect API credentials
- Never expose `.env`
- Sanitize or safely render AI-generated content
- Avoid executing arbitrary AI-generated code directly on the host

---

# ⚠️ Code Execution Security

If AI Coding Teammate eventually executes user-provided code, that code should **not** be executed directly inside the main Flask application process.

A production implementation should use an isolated execution environment such as a sandbox or appropriately configured container with strict limits on:

- CPU
- Memory
- Execution time
- Network access
- Filesystem access
- Processes
- System calls

This separation helps protect the main application and server from unsafe or malicious code.

---

# 🔏 Privacy Considerations

Users should avoid sending secrets to AI services, including:

```text
Passwords
API keys
Private tokens
Database credentials
Credit-card information
Private encryption keys
Confidential customer information
```

Screen-sharing users should also check the visible screen before starting a capture to avoid unintentionally sharing sensitive information.

See the application's `Datenschutz` page for privacy information.

---

# 🧪 Testing

Tests are stored in:

```text
tests/
```

Run the test suite with:

```bash
pytest
```

Tests should cover important components such as:

- Authentication
- Database models
- Routes
- Project management
- File operations
- AI analysis services
- API endpoints
- Error handling

---

# 🗺️ Development Roadmap

Planned development areas include:

- [x] Flask application structure
- [x] Jinja template architecture
- [x] Authentication interface
- [x] Dashboard interface
- [x] Workspace interface
- [x] Project panel
- [x] Code editor interface
- [x] AI visualizer interface
- [x] AI chat interface
- [x] Settings interface
- [x] Custom 404 and 500 pages
- [x] Datenschutz and Impressum pages
- [ ] Complete database integration
- [ ] Complete project/file persistence
- [ ] Complete AI backend integration
- [ ] Real-time AI chat
- [ ] Code analysis pipeline
- [ ] AI correction workflow
- [ ] Secure code execution sandbox
- [ ] Screen-sharing analysis
- [ ] Camera analysis
- [ ] Image/video analysis
- [ ] Voice input
- [ ] Speech-to-speech communication
- [ ] Production security hardening
- [ ] Automated tests
- [ ] Production deployment

---

# 🎯 Target Users

AI Coding Teammate is intended for:

- Freelance developers
- Remote developers
- Independent developers
- Junior developers
- Programming students
- AI engineering students
- Developers learning new technologies
- Developers who want an AI development partner

---

# 💡 Example

Suppose a developer writes:

```python
def calculate_total(price, tax):
    total = price + taxes
    return total
```

The AI Coding Teammate can identify that:

```python
taxes
```

is undefined while the function parameter is:

```python
tax
```

It can suggest:

```python
def calculate_total(price, tax):
    total = price + tax
    return total
```

The AI can then explain **what was wrong, why it caused an error, and how the correction fixes it**.

This interaction represents the central idea behind AI Coding Teammate: not simply generating code, but working with the developer to understand and solve problems.

---

# 🤝 Project Philosophy

AI Coding Teammate is built around a simple idea:

> **Develop with AI, not just ask AI for code.**

The goal is to create an AI teammate that can see development context, communicate with the developer, analyze problems, explain errors, and collaborate throughout the development process.

---

# 📄 License

This work is proprietary and owned by **EBI Emmerich‑Adehor**. All rights reserved.

---

# 👨💻 Author

**EBI Emmerich‑Adehor**

Computer Science / AI Engineering

Project:

**AI Coding Teammate**

---

## 🚀 Status

AI Coding Teammate is currently under active development.

Features, architecture, AI integrations, and security controls may change as development continues.
