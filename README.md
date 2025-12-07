**Authors:** Ali Asiri (202027780), Omar alshahrani (202040640)  
**Date:** December 7, 2025  
**Course:** ICS344 - Network Security  
**Institution:** King Fahd University of Petroleum and Minerals  

# SecureChat

## Project Description

SecureChat is a comprehensive web-based secure messaging application designed to demonstrate advanced cryptographic techniques and network security principles. This project implements a hybrid cryptography system combining symmetric (AES-256-GCM) and asymmetric (RSA-PSS/RSA-OAEP) encryption to ensure end-to-end confidentiality, integrity, and authentication of messages. Beyond being a functional messaging platform, SecureChat serves as an educational attack laboratory where users can simulate and study various security threats and their countermeasures. The application targets students, educators, and security professionals interested in practical cryptography and network security education.

## Author Information

**👥 Group Members**
- Member 1: Ali Asiri (202027780) — 4
- Member 2: Omar alshahrani (202040640) — 4

**Course Information**  
ICS344 - Network Security  
King Fahd University of Petroleum and Minerals  
December 2025

## Features

- **End-to-End Encryption**: Hybrid AES-256-GCM + RSA-PSS/RSA-OAEP for secure message transmission
- **Real-Time Messaging**: WebSocket-based instant communication with live updates
- **User Authentication**: Secure login and registration with password hashing
- **Key Management**: Automated generation and management of cryptographic keys
- **Attack Laboratory**: Interactive environment to simulate and study security attacks
- **Comprehensive Testing**: Extensive test suite covering cryptography and integration
- **Cross-Platform Support**: Web-based interface accessible from any modern browser

## Technology Stack

**Backend:**
- Flask 3.0.0 - Web framework
- Flask-SocketIO - Real-time communication
- Flask-SQLAlchemy - Database ORM

**Cryptography:**
- Python cryptography library - Core cryptographic operations

**Database:**
- PostgreSQL/SQLite - Data persistence

**Frontend:**
- HTML5 - Structure
- CSS3 - Styling
- JavaScript - Client-side logic

**Security:**
- bcrypt - Password hashing
- PBKDF2 - Key derivation

**Testing:**
- pytest - Test framework

## Security Highlights

- **Hybrid Cryptography**: Combines strengths of symmetric and asymmetric encryption
- **Message Integrity**: Ensures messages are not tampered with during transmission
- **Replay Attack Prevention**: Mechanisms to detect and prevent message replay
- **DoS Protection**: Built-in defenses against denial-of-service attacks
- **Attack Simulation**: Educational tools to demonstrate common security vulnerabilities
- **Comprehensive Logging**: Detailed security event logging for monitoring and analysis

## Documentation

- [User Guide](User_Guide.md) - Complete user manual and tutorials
- [Technical Report](SecureChat_Technical_Report.md) - Detailed technical documentation
- [Backend API Documentation](backend/api_routes.py) - API endpoint specifications

## Project Structure

```
SecureChat_Project/
├── .env.example
├── .gitignore
├── README.md
├── requirements-dev.txt
├── requirements.txt
├── SecureChat_Technical_Report.md
├── test_auth.py
├── User_Guide.md
├── backend/
│   ├── api_routes.py
│   ├── app.py
│   ├── attack_lab.py
│   ├── auth.py
│   ├── config.py
│   ├── crypto_engine.py
│   ├── database.py
│   ├── key_manager.py
│   ├── message_handler.py
│   ├── utils.py
│   └── websocket_handler.py
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   └── js/
│   │       └── app.js
│   └── templates/
│       ├── attack_lab.html
│       ├── index.html
│       ├── key_management.html
│       ├── login.html
│       └── register.html
├── scripts/
│   ├── init_db.py
│   └── test_auth.py
└── tests/
    ├── test_crypto.py
    └── test_integration.py
```

## Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, SQLite for development)

### Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd SecureChat_Project
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Configuration
1. Copy environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your configuration:
   ```
   SECRET_KEY=your-secret-key
   DATABASE_URL=postgresql://user:password@localhost/securechat
   # or for SQLite: DATABASE_URL=sqlite:///securechat.db
   ```

### Database Setup
1. Initialize the database:
   ```bash
   python scripts/init_db.py
   ```

### Running the Application
1. Start the server:
   ```bash
   python backend/app.py
   ```

2. Open your browser and navigate to `http://localhost:5000`

## Usage Examples

### Registration
1. Navigate to the registration page
2. Enter username and password
3. System generates cryptographic keys automatically

### Login
1. Enter credentials on login page
2. System authenticates and establishes secure session

### Sending Messages
1. Select recipient from user list
2. Type message in chat interface
3. Message is encrypted end-to-end before transmission

### Using Attack Lab
1. Access attack lab from main interface
2. Select attack type to simulate
3. Observe security mechanisms in action

### Key Management
1. Navigate to key management section
2. View current keys or generate new ones
3. Export/import keys as needed

## Development Information

### Setup for Developers
1. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

2. Run tests:
   ```bash
   pytest
   ```

### Testing
- Unit tests: `pytest tests/`
- Integration tests: `pytest tests/test_integration.py`
- Authentication tests: `python scripts/test_auth.py`

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

### License
This project is licensed under the MIT License - see the LICENSE file for details.
