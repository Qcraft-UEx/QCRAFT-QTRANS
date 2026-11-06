# Manual de Desarrollador QCraft

Este documento detalla los pasos necesarios para desplegar y ejecutar el entorno de desarrollo de QCraft.

## 1. Clonar el repositorio

```bash
git clone https://github.com/aandresb01/QCRAFT-Quantum-Collaborative-Interface-main.git
```

## 2. Despliegue del Proyecto

El sistema consta de cuatro componentes principales que deben ejecutarse simultáneamente.

### Backend Django (Autenticación y Gestión de Usuarios)

1.  Navega a la carpeta del proyecto Django.
2.  Asegúrate de tener **Python 3.10.11+** instalado.
3.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Inicia el servidor:
    ```bash
    python manage.py runserver
    ```
5.  El backend estará disponible en `http://localhost:8000`.

---

### Backend Spring Boot (WebSocket y Edición Colaborativa)

1.  Navega a la carpeta del proyecto Spring Boot.
2.  Asegúrate de tener **Java (JDK 17+)** y **Maven** instalados.
3.  Compila y ejecuta el servidor:
    ```bash
    cd quirkShareSpring/
    mvn spring-boot:run
    ```
4.  Este servicio manejará los WebSockets para la edición colaborativa de circuitos.

---

### Frontend React - QCraft (Interfaz Principal con Auth0)

1.  Navega a la carpeta del proyecto:
    ```bash
    cd UpdateQuirk/Auth0/
    ```
2.  Asegúrate de tener **Node.js** instalado.
3.  Instala las dependencias:
    ```bash
    npm install
    ```
4.  **Configuración de Auth0**:
    *   Crea una nueva *Single Page Application* en Auth0.
    *   > ⚠️
        > En la configuración de Auth0, añade `http://localhost:3000` en **Allowed Callback URLs**.
    *   Crea el archivo de configuración en `UpdateQuirk\Auth0\src\auth_config.json` con el siguiente contenido:

    ```json
    {
      "domain": "example.us.auth0.com",
      "clientId": "example",
      "audience": "https://example.us.auth0.com/api/v2/"
    }
    ```
    *(Domain y ClientID están en **Settings**; Audience está en **APIs**)*

5.  Inicia el servidor:
    ```bash
    npm start
    ```
6.  La interfaz principal estará disponible en `http://localhost:3000`.

---

### Frontend React - Quirk (Visualización de Circuitos)

1.  Navega a la carpeta del proyecto:
    ```bash
    cd UpdateQuirk/Quirk/out
    ```
2.  Instala las dependencias:
    ```bash
    npm install
    ```
3.  Inicia el servidor de desarrollo:
    ```bash
    npm run dev
    ```
4.  **Importante**:
    *   Borra el archivo `quirk.html`.
    *   Renombra el archivo `quirk_util.html` -> `quirk.html`.
    *   Actualiza la página.
5.  Este entorno permite la visualización en tiempo real de los circuitos.

---

## Nota Final

> 📝
> Una vez que los cuatro servidores (Django, Spring, QCraft, Quirk) estén levantados, el sistema estará listo para usarse de forma colaborativa y en tiempo real.

---

## 3. Modo de Uso: Debug

En la sección **Mis Circuitos**, se muestra un botón adicional junto al botón de reproducción, identificado con un ícono de insecto 🐞. Al pulsarlo, se abrirá el circuito en **Modo DEBUG**.

Este modo habilita herramientas adicionales para el análisis paso a paso del circuito:

*   **Navegación paso a paso**: En la parte superior se añaden los botones **Previous Step** y **Next Step**, que permiten desplazarse entre los distintos estados de ejecución.
*   **Seguimiento visual**: Se activa un seguimiento visual de pasos en color gris, mostrando:
    *   Los resultados de cada columna del circuito, además del resultado final del circuito completo.
*   **Actualización dinámica**: El estado del seguimiento se actualiza dinámicamente al avanzar o retroceder entre pasos mediante los botones correspondientes.

### Ejemplos de uso

*   **CASO 1**: Los resultados ya están en la Base de Datos guardados, por lo que no es necesario ejecutar el circuito para ver los resultados.

![VIDEO MUESTRA 1](./gifs/IDyaGuardado.gif)

*   **CASO 2**: El circuito ha sido modificado, por lo que es necesario ejecutar el circuito para ver los resultados nuevos.

![VIDEO MUESTRA 2](./gifs/NuevoCircuito.gif)
