# SecureChat User Guide

## Introduction

SecureChat is a web-based secure messaging application designed to provide end-to-end encrypted communication between users. Built with Flask and featuring real-time messaging through WebSockets, SecureChat ensures that messages are protected using RSA key pairs for encryption. The application includes user authentication, key management, and an interactive Attack Lab for demonstrating common security vulnerabilities and best practices.

Key security features include:
- RSA-based end-to-end encryption for messages
- Secure user authentication with session management
- Real-time messaging with WebSocket connections
- Built-in Attack Lab for educational security demonstrations

This guide will walk you through installing, configuring, and using SecureChat effectively.

## System Requirements

To run SecureChat, ensure your system meets the following requirements:

### Hardware Requirements
- A computer with at least 2GB RAM (4GB recommended)
- Sufficient storage space (minimum 100MB free space)

### Software Requirements
- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.6 or higher (Python 3.8+ recommended)
- **Package Manager**: pip (comes with Python installations)
- **Web Browser**: Modern browser with JavaScript enabled (Chrome, Firefox, Safari, or Edge)

### Optional Components
- **Database**: SQLite (included by default) or PostgreSQL for production use
- **Redis**: For session management and caching (optional)

## Installation Instructions

Follow these step-by-step instructions to install and set up SecureChat on your system.

1. **Download or Clone the Project**:
   - Download the SecureChat project files to your local machine, or clone the repository if available.

2. **Install Python Dependencies**:
   - Open a terminal or command prompt.
   - Navigate to the SecureChat project directory.
   - Run the following command to install required packages:
     ```
     pip install -r requirements.txt
     ```

3. **Initialize the Database**:
   - In the terminal, run the database initialization script:
     ```
     python scripts/init_db.py
     ```
   - This will create the necessary database tables and prepare SecureChat for use.

4. **Start the Application**:
   - Run the following command to start the SecureChat server:
     ```
     python backend/app.py
     ```
   - The application will start on `http://localhost:5000`.

5. **Access SecureChat**:
   - Open your web browser and navigate to `http://localhost:5000` to access the application.

## Configuration

SecureChat uses environment variables for configuration. For basic usage, the default settings should work. However, for production or custom setups, you may need to configure the following:

### Database Configuration
- By default, SecureChat uses SQLite with a local database file (`securechat.db`).
- To use a different database (e.g., PostgreSQL), set the `DATABASE_URL` environment variable in a `.env` file.

### Environment Setup
1. Create a file named `.env` in the project root directory.
2. Add the following variables as needed:
   ```
   SECRET_KEY=your_secret_key_here
   DATABASE_URL=sqlite:///securechat.db
   ```
3. The `SECRET_KEY` is used for Flask session security. Use a strong, random string in production.
4. Restart the application after making configuration changes.

## Usage Guide

### User Registration and Login

1. **Registration**:
   - Navigate to the registration page (`/register` or click "Register" on the main page).
   - Enter a unique username.
   - Click "Register" to create your account.
   - SecureChat will generate an RSA key pair for your account automatically.

2. **Login**:
   - Go to the login page (`/login` or click "Login" on the main page).
   - Enter your username.
   - Click "Login" to access your account.
   - Upon successful login, you'll be redirected to the main messaging interface.

### Key Management

SecureChat automatically generates and manages RSA key pairs for encryption. To view or manage your keys:

1. Navigate to the Key Management page (`/key-management`).
2. Here you can view your public and private keys.
3. Keys are used automatically for encrypting and decrypting messages.
4. **Important**: Never share your private key with anyone.

### Sending and Receiving Messages

1. **Access the Main Interface**:
   - After logging in, you'll see the main messaging dashboard.

2. **Send a Message**:
   - Select a recipient from the user list (if available).
   - Type your message in the input field.
   - Click "Send" to transmit the message.
   - Messages are encrypted end-to-end using RSA keys.

3. **Receive Messages**:
   - Incoming messages appear in real-time in the chat interface.
   - Messages are automatically decrypted for display.

4. **Real-time Communication**:
   - SecureChat uses WebSockets for instant message delivery.
   - No need to refresh the page; messages appear as they are sent.

### Using the Attack Lab

The Attack Lab is an educational feature demonstrating common security vulnerabilities:

1. Navigate to the Attack Lab page (`/attack-lab`).
2. Explore various security scenarios and demonstrations.
3. Learn about encryption, authentication, and secure communication practices.
4. Use this feature to understand potential security risks and best practices.

## Screenshots

Below are key screenshots of the SecureChat interface. (Note: Please insert actual screenshots here as they cannot be generated automatically.)

- **Login Page**: [Insert screenshot of login.html]
- **Registration Page**: [Insert screenshot of register.html]
- **Main Messaging Interface**: [Insert screenshot of index.html]
- **Key Management Page**: [Insert screenshot of key_management.html]
- **Attack Lab Page**: [Insert screenshot of attack_lab.html]

## Troubleshooting

### Common Issues and Solutions

1. **Application Won't Start**:
   - Ensure Python 3.x is installed and in your PATH.
   - Verify all dependencies are installed: `pip install -r requirements.txt`
   - Check for port conflicts (default port 5000).

2. **Database Errors**:
   - Run `python scripts/init_db.py` to reinitialize the database.
   - Ensure write permissions in the project directory.

3. **Login Issues**:
   - Verify your username is correct.
   - Clear browser cache and cookies.
   - Check browser console for JavaScript errors.

4. **Messages Not Sending**:
   - Ensure you're logged in.
   - Check your internet connection.
   - Verify the recipient exists and is online.

5. **Port Already in Use**:
   - Change the port in `backend/app.py` or kill the process using the port.
   - On Windows: `netstat -ano | findstr :5000` then `taskkill /PID <PID>`

6. **WebSocket Connection Issues**:
   - Ensure your firewall allows WebSocket connections.
   - Try a different browser.

If issues persist, check the terminal output for error messages and consult the project documentation.

## Security Notes

SecureChat is designed with security in mind, but user awareness is crucial:

- **Key Security**: Your RSA private key is stored securely but never share it. Loss of your private key means loss of access to encrypted messages.
- **Username Best Practices**: Use unique, non-guessable usernames. Avoid personal information.
- **Session Management**: Always log out when finished. Sessions expire automatically.
- **Network Security**: Use HTTPS in production environments.
- **Attack Lab**: Use the Attack Lab for learning, not for malicious activities.
- **Data Privacy**: Messages are encrypted, but be aware of local storage and backups.
- **Updates**: Keep SecureChat updated to benefit from security improvements.

For advanced security configurations or production deployment, consult with security professionals.

---

This concludes the SecureChat User Guide. For technical support or feature requests, refer to the project repository or contact the development team.