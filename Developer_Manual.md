# QCraft Developer Manual

This document details the necessary steps to deploy and run the QCraft development environment.

## 1. Clone the Repository

```bash
git clone https://github.com/aandresb01/QCRAFT-Quantum-Collaborative-Interface-main.git
```

## 2. Project Deployment

The system consists of four main components that must run simultaneously.

### Django Backend (Authentication & User Management)

1. Navigate to the Django project folder.
2. Ensure **Python 3.10.11+** is installed.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:

   ```bash
   python manage.py runserver
   ```
5. The backend will be available at `http://localhost:8000`.

---

### Spring Boot Backend (WebSocket & Collaborative Editing)

1. Navigate to the Spring Boot project folder.
2. Ensure **Java (JDK 17+)** and **Maven** are installed.
3. Compile and run the server:

   ```bash
   cd quirkShareSpring/
   mvn spring-boot:run
   ```
4. This service will handle WebSockets for collaborative circuit editing.

---

### React Frontend - QCraft (Main Interface with Auth0)

1. Navigate to the project folder:

   ```bash
   cd UpdateQuirk/Auth0/
   ```

2. Ensure **Node.js** is installed.

3. Install dependencies:

   ```bash
   npm install
   ```

4. **Auth0 Configuration**:

   * Create a new *Single Page Application* in Auth0.
   * > ⚠️ Add `http://localhost:3000` to **Allowed Callback URLs**.
   * Create the configuration file at `UpdateQuirk/Auth0/src/auth_config.json` with the following content:

   ```json
   {
     "domain": "example.us.auth0.com",
     "clientId": "example",
     "audience": "https://example.us.auth0.com/api/v2/"
   }
   ```

   *(Domain and ClientID are in **Settings**; Audience is in **APIs**)*

5. Start the server:

   ```bash
   npm start
   ```

6. The main interface will be available at `http://localhost:3000`.

---

### React Frontend - Quirk (Circuit Visualization)

1. Navigate to the project folder:

   ```bash
   cd UpdateQuirk/Quirk/out
   ```
2. Install dependencies:

   ```bash
   npm install
   ```
3. Start the development server:

   ```bash
   npm run dev
   ```
4. **Important**:

   * Delete the `quirk.html` file.
   * Rename `quirk_util.html` -> `quirk.html`.
   * Refresh the page.
5. This environment allows real-time visualization of circuits.

---

## Final Note

> 📝 Once all four servers (Django, Spring, QCraft, Quirk) are running, the system is ready for collaborative real-time use.

---

## 3. Usage: Debug Mode

In the **My Circuits** section, an additional button appears next to the play button, represented by a bug icon 🐞. Clicking it opens the circuit in **DEBUG Mode**.

This mode enables additional tools for step-by-step circuit analysis:

* **Step Navigation**: Buttons **Previous Step** and **Next Step** are added at the top, allowing navigation through execution states.
* **Visual Tracking**: Step tracking is highlighted in gray, showing:

  * The results of each circuit column, in addition to the final outcome.
* **Dynamic Update**: The tracking state updates dynamically as you move forward or backward using the buttons.

### Usage Examples

* **CASE 1**: Results are already saved in the database; no need to run the circuit to view outcomes.

![VIDEO SAMPLE 1](./gifs/IDyaGuardado.gif)

* **CASE 2**: The circuit has been modified, so it must be executed to see the new results.

![VIDEO SAMPLE 2](./gifs/NuevoCircuito.gif)
