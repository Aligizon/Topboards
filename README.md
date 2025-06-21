# 🚀 Topboards

Topboards is a web application developed on **Flask**, using **PostgreSQL** and **Docker** for containerization.

## 📌 Features
✅ Product and order management
✅ User authorization and authentication
✅ Admin panel for store management
✅ Uploading and storing product images
✅ Flexible system of user roles and rights

---

## 🛠️ Technologies

- **Backend**: Flask, SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: JavaScript, Jinja2, Bootstrap, Slick Slider
- **Containerization**: Docker, Docker Compose
- **Deployment**: GitHub

---

## 🚀 Deployment with Docker

### 🔹 1. Clone gihub repo
```bash
git clone https://github.com/Aligizon/Topboards.git
cd Topboards
```

### 🔹 2. Run docker-compose
```bash
docker-compose up --build -d
```

### 🔹 2. Update to the Initial migration
```bash
docker exec -it <flask_container_name> bash
flask --app website/main.py db upgrate
```

### 🔹 3. Stop containers
```bash
docker-compose down
```

---

## ⚙️ Environment variables

```
POSTGRES_USER=topboards
POSTGRES_PASSWORD=my_topboards_16
POSTGRES_DB=database
SECRET_KEY=your_secret_key
```

---

## 👨‍💻 Author
**Aligizon**  
📧 Email: arseniy.akopov@gmail.com  
🔗 GitHub: [github.com/Aligizon](https://github.com/Aligizon)

---

## ⭐ Support the project
If you like this project, put ⭐ in the repository!

