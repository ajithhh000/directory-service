# 🏢 Employee Directory – Full DevOps CI/CD Pipeline

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0.3-black?logo=flask)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)
![Jenkins](https://img.shields.io/badge/Jenkins-CI%2FCD-red?logo=jenkins)
![AWS EC2](https://img.shields.io/badge/Deployed_on-AWS_EC2-orange?logo=amazon-aws)
![MySQL](https://img.shields.io/badge/MySQL-8.0-deepblue?logo=mysql)

A production-ready **Employee Directory** web app built with Flask and MySQL, containerized with Docker, and deployed via a fully automated **Jenkins CI/CD pipeline** on **AWS EC2**. Designed with core DevOps principles: infrastructure-as-code, health checks, idempotent deployments, and observability.

> 🔗 **Live Demo**: Deployed on AWS EC2 (IP redacted for security)  
> 💡 **Ideal for DevOps/portfolio showcases** – demonstrates end-to-end automation from Git push to running service.

---

## 🌟 Features

- ✅ **Full CRUD operations**: Add, view, update, and delete employees  
- 🔒 Secure configuration via environment variables  
- 🔄 **Automated CI/CD**: Jenkins pipeline triggered by GitHub webhook  
- 🐳 **Multi-container architecture**: Isolated Flask app + MySQL (with persistent volume)  
- 🩺 Built-in **health checks** (`/health` endpoint + Docker service dependencies)  
- 🧪 **Robust startup**: App retries DB connection with backoff on boot  
- 🎨 Modern, responsive UI with flash messages and confirmation dialogs  
- ☁️ One-click deployable on **AWS EC2**

![Employee Directory UI](screenshots/employee-directory-ui.png)

---

## 🛠️ Tech Stack

| Layer           | Technology                                     |
|-----------------|-----------------------------------------------|
| **Backend**     | Python 3.12, Flask 3.0.3                      |
| **Database**    | MySQL 8.0 (containerized, persistent volume)  |
| **Container**   | Docker, Docker Compose                        |
| **CI/CD**       | Jenkins (Declarative Pipeline as Code)        |
| **Cloud**       | AWS EC2 (Ubuntu 22.04 LTS)                    |
| **Dependencies**| `mysql-connector-python==9.1.0`, `Werkzeug`   |

---

## 🚀 Local Deployment

```bash
git clone https://github.com/ajithhh000/directory-service.git
cd directory-service
docker compose up --build -d
