# 🛡️ Ephemera: Volatile Tactical Communication System

## 📌 Overview
**Ephemera** is a highly secure, "Zero-Trace" tactical communication system designed to prevent data compromise on captured devices. By eliminating persistent storage (HDD/SSD), the system ensures that all communications and executions occur exclusively in RAM. Once the session ends or power is lost, all digital footprints are instantly and irretrievably destroyed.

## 🚀 Key Features
* **Zero-Trace Architecture:** Utilizes an in-memory **Redis** database to guarantee absolute data volatility and eliminate digital remnants.
* **Advanced Encryption Engine:** Implements **AES-Fernet (256-bit)** encryption. It uses 128 bits for data confidentiality (CBC mode) and 128 bits for data integrity (HMAC signature).
* **Secure Offline Authentication:** Enforces multi-factor authentication (2FA) via Time-Based One-Time Passwords (TOTP) and offline QR code generation.
* **Segmented Operational Roles:** Strict access control that distinguishes between Tactical Units (*Unitate Tactică*) and Command Centers (*Centru de Comandă*).
* **Real-Time NLP Analysis:** Built-in Natural Language Processing to analyze text in real-time and trigger instant visual operational alerts.

## 🛠️ Technologies & Stack
* **Core Language:** Python
* **Database:** Redis (configured for strict In-Memory execution)
* **Networking:** TCP/IPv4 Protocol Stack
* **Security & Cryptography:** AES-256, HMAC, TOTP

## ⚙️ Architecture & Workflow
1. **Authentication:** Users authenticate through a mandatory, secure 2FA TOTP mechanism.
2. **Encrypted Flow:** Data is transmitted over a TCP/IPv4 connection, encrypted end-to-end.
3. **Volatile Processing:** Messages and session data are temporarily held in RAM via Redis.
4. **RAM Cleanup:** Upon manual termination or power interruption, the system completely flushes the memory.
