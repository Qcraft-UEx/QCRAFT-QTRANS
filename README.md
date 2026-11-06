<p align="center">
   <picture>
     <source media="(prefers-color-scheme: dark)" srcset="https://github.com/Qcraft-UEx/Qcraft/blob/main/docs/_images/qcraft_logo.png?raw=true" width="60%">
     <img src="https://github.com/Qcraft-UEx/Qcraft/blob/main/docs/_images/qcraft_logo.png?raw=true" width="60%" alt="QCRAFT Logo">
   </picture>
</p>

# QCRAFT Quantum Debugger 
![Python Versions](https://img.shields.io/badge/python-3.9%20|%203.10%20|%203.11%20|%203.12-blue.svg)  
![JavaScript](https://shields.io/badge/JavaScript-F7DF1E?logo=JavaScript&logoColor=000&style=flat-square)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/Qcraft-UEx/QCRAFT-Quantum-Collaborative-Interface/blob/main/LICENSE)

**QCRAFT Quantum Debugger**  is a tool for quantum circuit development designed for real-time collaboration and debug. It enables multiple users to **co-edit quantum circuits synchronously** through a shared visual interface. This functionality is built on a custom adaptation of the **Operational Transformation (OT)** model, tailored specifically for quantum circuits. And enables you to analyze circuit behavior step by step to verify logic using interactive **debug mode**.

## Documentation

- [📖 Manual de Desarrollador (Español)](./Manual_Desarrollador.md)
- [📖 Developer Manual (English)](./Developer_Manual.md)

## Key Features

- **Real-time collaborative editing of quantum circuits**  
  Users can co-design circuits in a shared Quirk-based interface. Edits are synchronized instantly using a WebSocket-based OT protocol adapted for quantum data structures.

- **Operational Transformation for Quantum Circuits**  
  Unlike traditional OT for text, our adaptation works with quantum circuit elements—each with semantic context such as qubit state, gate type, and spatial position (row/column).

- **WebSocket Synchronization Layer**  
  Ensures low-latency, bidirectional communication and full support for the OT model, allowing efficient and scalable collaborative workflows.

- **Dual-backend Architecture**  
  Combines Django for persistent user/session management with **Spring Boot** for optimized real-time collaboration services. This separation improves scalability, maintainability, and performance.

- **Cross-platform execution**  
  Collaborative designs can be translated and executed on IBM Quantum or AWS Braket, including visual results and cost estimation.

- **Deployment as Quantum Services**  
  Circuits can be deployed in Docker containers and exposed as web services for reproducible and accessible experimentation.

- **Interactive Debug Mode**  
  Visualize quantum circuit execution step-by-step. Inspect intermediate states, column-wise results, and final outcomes with dynamic visual tracking.


## Workflow Overview

1. **Collaborative Design**: Multiple users build circuits in real time via Quirk.
2. **Synchronization**: All changes are propagated using an OT model over WebSockets.
3. **Code Translation**: Circuits are translated to Qiskit or Braket code.
4. **Execution**: Users can launch executions on AWS or IBM devices.
5. **Result Visualization**: Real-time access to execution outcomes and performance metrics.
6. **Debugging**: Analyze circuit behavior step-by-step to verify logic using the interactive Debug Mode.

## Repository Structure

- `frontend/`: Visual interface (Quirk + collaborative extensions)
- `backend-django/`: User/session management, API, storage
- `backend-spring/`: Real-time synchronization server (WebSocket + OT engine)
- `docker/`: Deployment environment definitions
- `gifs/`: Demonstration assets and visual examples

## Demonstration

A demo video showing how to collaboratively design is available here:  
🔗 [https://youtu.be/demo-collaborative-editing](https://youtu.be/UCplUEtMYZ0)

### Debug Mode Preview

**Case 1: Viewing existing results**
![Debug Mode - Existing Results](./gifs/IDyaGuardado.gif)

**Case 2:  Analyzing modified circuits**
![Debug Mode - New Execution](./gifs/NuevoCircuito.gif)

## License

This project is licensed under the [MIT License](https://github.com/Qcraft-UEx/QCRAFT-Quantum-Collaborative-Interface/blob/main/LICENSE).
