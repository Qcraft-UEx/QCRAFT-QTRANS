import React, { useState, useEffect } from "react";
import axios from "axios";
import { withAuthenticationRequired, useAuth0 } from "@auth0/auth0-react";
import { useUserEmail } from "../components/UserEmailContext";
import { useHistory } from "react-router-dom";
import "../MisCircuitos.css";
import awsIcon from "../assets/aws-icon.png";
import ibmIcon from "../assets/ibm-icon.png";
import trashIcon from "../assets/trash-icon.png";
import playIcon from "../assets/play-icon.png";
import debugIcon from "../assets/debug-icon.png";
import editIcon from "../assets/edit-icon.png";
import searchIcon from "../assets/search-icon.png";
import LoadingOverlay from "../components/LoadingOverlay";
import LoadingOverlayS from "../components/LoadingOverlayS";
import braketIcon from "../assets/braket-icon.png";
import qiskitIcon from "../assets/qiskit-icon.png";
import qasmIcon2 from "../assets/openqasm2-icon.png";
import qasmIcon3 from "../assets/openqasm3-icon.png";

import {
  Button,
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Label,
  Input,
} from "reactstrap";

const MisCircuitos = () => {
  const { user } = useAuth0();
  const { setUserEmail, userEmail } = useUserEmail();
  const [circuitos, setCircuitos] = useState([]);
  const [translatedCircuito, setTranslatedCircuito] = useState(null);
  
  const [awsCode, setAwsCode] = useState(null);
  const [ibmCode, setIbmCode] = useState(null);
  const [qasm2Code, setQasm2Code] = useState(null);
  const [qasm3Code, setQasm3Code] = useState(null);
  
  const [isTranslating, setIsTranslating] = useState(false);
  const [editingCircuito, setEditingCircuito] = useState(null);
  const [editedNombre, setEditedNombre] = useState("");
  const [selectedCircuitoId, setSelectedCircuitoId] = useState(null);
  
  const [selectedShotsIBM, setSelectedShotsIBM] = useState("");
  const [selectedShotsAWS, setSelectedShotsAWS] = useState("");
  const [selectedShotsQASM, setSelectedShotsQASM] = useState("");
  
  const [selectedMaquinaIBM, setSelectedMaquinaIBM] = useState("");
  const [selectedMaquinaAWS, setSelectedMaquinaAWS] = useState("");
  const [selectedMaquinaQASM, setSelectedMaquinaQASM] = useState("");
  
  const [codigocolumnaAWS, setCodigocolumnaAWS] = useState(null); 
  const [receivedUrl, setReceivedUrl] = useState(null);
  const [selectedCircuitoUrl, setSelectedCircuitoUrl] = useState("");
  const [isEditingName, setIsEditingName] = useState(false); 
  const [isEditingOrEjecting, setEditingOrEjecting] = useState(false);
  const [precioTarea, setPrecioTarea] = useState(0);
  const [precioShot, setPrecioShot] = useState(0);
  const [costoTotal, setCostoTotal] = useState(0);
  const [mensaje, setMensaje] = useState("");
  const [ejecucionEnCurso, setEjecucionEnCurso] = useState(null);
  const [ejecucionCompletada, setEjecucionCompletada] = useState(null);
  const [isExecutingS, setIsExecutingS] = useState(false); 
  const [isExecutingE, setIsExecutingE] = useState(false); 
  const [noEjecucion, setNoEjecucion] = useState(null);
  const [nombreCircuito, setNombreCircuito] = useState(null);

  const precios = {
    local: { tarea: 0, shot: 0 },
    sv1: { minuto: 0.075 },
    dm1: { minuto: 0.075 },
    tn1: { minuto: 0.275 },
    ionq: { tarea: 0.3, shot: 0.01 },
    "ionq Aria 1": { tarea: 0.3, shot: 0.03 },
    "ionq Aria 2": { tarea: 0.3, shot: 0.03 },
    "ionq Forte": { tarea: 0.3, shot: 0.01 },
    rigetti: { tarea: 0.3, shot: 0.00035 },
    "oqc lucy": { tarea: 0.3, shot: 0.00035 },
    "quera aquila": { tarea: 0.3, shot: 0.01 },
    garnet: { tarea: 0.3, shot: 0.00145 },
  };

  const [selectedProvider, setSelectedProvider] = useState(null);

  const handleProviderClick = (provider) => {
    setSelectedProvider(provider);
    setEjecucionCompletada(null);
    setEjecucionEnCurso("NO NULO");
    setNoEjecucion("NO NULO");
    setSelectedMaquinaAWS("");
    setSelectedMaquinaIBM("");
    setSelectedMaquinaQASM("");
    setSelectedShotsAWS("");
    setSelectedShotsIBM("");
    setSelectedShotsQASM("");
  };

  useEffect(() => {
    const maquina = precios[selectedMaquinaAWS];
    if (selectedMaquinaAWS === "local") {
      setMensaje("La ejecución es gratis y se ejecuta de forma inmediata.");
      setPrecioTarea(0);
      setPrecioShot(0);
    } else if (maquina && maquina.minuto) {
      setMensaje(`Tarifa por minuto: ${maquina.minuto} USD`);
      setPrecioTarea(0);
      setPrecioShot(0);
    } else if (maquina) {
      setMensaje("");
      setPrecioTarea(maquina.tarea || 0);
      setPrecioShot(maquina.shot || 0);
    } else {
      setMensaje("");
      setPrecioTarea(0);
      setPrecioShot(0);
    }
    // eslint-disable-next-line
  }, [selectedMaquinaAWS]);

  useEffect(() => {
    const total = precioTarea + precioShot * selectedShotsAWS;
    setCostoTotal(total);
  }, [selectedShotsAWS, precioTarea, precioShot]);

  useEffect(() => {
    console.log("Circuito ejecutado:", codigocolumnaAWS);
  }, [codigocolumnaAWS]);

  useEffect(() => {
    const fetchCircuitos = async () => {
      try {
        if (user && user.email) {
          setUserEmail(user.email);
          const response = await axios.get(
            `http://localhost:8000/obtener_url_y_nombre_por_email/?email=${userEmail}`
          );
          setCircuitos(response.data.circuitos);
        }
      } catch (error) {
        console.error("Error al obtener los circuitos:", error);
      }
    };
    fetchCircuitos();
    // eslint-disable-next-line
  }, [userEmail, user, ejecucionCompletada, ejecucionEnCurso]);

  const handleTranslate = async (url, nombre, url_desplegada) => {
    setEditingOrEjecting(true);
    setReceivedUrl(url_desplegada);
    try {
      setIsTranslating(true);
      setSelectedCircuitoUrl(url); 

      // 1. AWS
      const awsResponse = await axios.post("http://localhost:8000/api/translate/", { url: url, ecosystem: "braket" });
      if (awsResponse.data.code) setAwsCode(awsResponse.data.code);

      // 2. IBM
      const ibmResponse = await axios.post("http://localhost:8000/api/translate/", { url: url, ecosystem: "qiskit" });
      if (ibmResponse.data.code) setIbmCode(ibmResponse.data.code);

      // 3. OpenQASM 2
      const qasm2Response = await axios.post("http://localhost:8000/api/translate/", { url: url, ecosystem: "qasm2" });
      if (qasm2Response.data.code) setQasm2Code(qasm2Response.data.code);

      // 4. OpenQASM 3
      const qasm3Response = await axios.post("http://localhost:8000/api/translate/", { url: url, ecosystem: "qasm3" });
      if (qasm3Response.data.code) setQasm3Code(qasm3Response.data.code);

      setTranslatedCircuito({ url, nombre });
    } catch (error) {
      console.error("Error translating:", error);
      alert("Error al traducir el circuito. Comprueba la consola.");
    } finally {
      setIsTranslating(false);
      setEditingOrEjecting(false);
    }
  };

  const handleSendUrl = async (url) => {
    setIsExecutingS(true);
    try {
      const response = await axios.post(
        "http://localhost:8000/lanzar_servicio/",
        { url: url, id: selectedCircuitoId }
      );
      setReceivedUrl(response.data.service_url);
    } catch (error) {
      console.error("Error al enviar la URL:", error);
    } finally {
      setIsExecutingS(false);
    }
  };

  const ejecutarTraduccion = async (codigoTraducido, plataforma, shots, maquina) => {
    setIsExecutingE(true); 
    try {
      if (maquina === "") {
        alert("Por favor, selecciona una máquina válida.");
        setIsExecutingE(false);
        return;
      }
      if (shots === "" || parseInt(shots) < 100 || parseInt(shots) > 10000) {
        alert("El número de shots debe estar entre 100 y 10000.");
        setIsExecutingE(false);
        return;
      }
      
      const response = await axios.post(
        "http://localhost:8000/ejecutar_circuito/",
        {
          email: userEmail,
          codigo_traducido: codigoTraducido,
          circuito_id: selectedCircuitoId,
          plataforma: plataforma,
          shots: shots,
          maquina: maquina,
        }
      );

      setCodigocolumnaAWS(response.data.circuito);
      setEjecucionEnCurso(response.data.circuito);
      if (response.data.circuito === "ERROR" || response.data.circuito === "CREDENCIALES") {
        setNoEjecucion(response.data.circuito);
      } else {
        setEjecucionCompletada(response.data.circuito);
      }
    } catch (error) {
      console.error("Error al ejecutar traducción:", error);
    } finally {
      setIsExecutingE(false);
    }
  };

  const handleEjecutarAwsClick = () => {
    setEjecucionEnCurso("NO NULO");
    setNoEjecucion("NO NULO");
    setEjecucionCompletada(null);
    ejecutarTraduccion(awsCode, "AWS", selectedShotsAWS, selectedMaquinaAWS);
  };

  const handleEjecutarIbmClick = () => {
    setEjecucionEnCurso("NO NULO");
    setNoEjecucion("NO NULO");
    setEjecucionCompletada(null);
    ejecutarTraduccion(ibmCode, "IBM", selectedShotsIBM, selectedMaquinaIBM);
  };

  const handleEjecutarQasm2Click = () => {
    setEjecucionEnCurso("NO NULO");
    setNoEjecucion("NO NULO");
    setEjecucionCompletada(null);
    ejecutarTraduccion(qasm2Code, "QASM2", selectedShotsQASM, selectedMaquinaQASM);
  };

  const handleEjecutarQasm3Click = () => {
    setEjecucionEnCurso("NO NULO");
    setNoEjecucion("NO NULO");
    setEjecucionCompletada(null);
    ejecutarTraduccion(qasm3Code, "QASM3", selectedShotsQASM, selectedMaquinaQASM);
  };

  const handleBack = () => {
    setTranslatedCircuito(null);
    setEjecucionEnCurso("NO NULO");
    setNoEjecucion("NO NULO");
    setSelectedProvider(null);
    setSelectedMaquinaAWS("");
    setSelectedMaquinaIBM("");
    setSelectedMaquinaQASM(""); 
    setSelectedShotsAWS("");
    setSelectedShotsIBM("");
    setSelectedShotsQASM(""); 
    setEjecucionCompletada(null);
    setNombreCircuito(null);
  };

  const handleEditNombre = async (circuitoId, nuevoNombre) => {
    try {
      const response = await axios.post(
        "http://localhost:8000/actualizar_nombre_circuito/",
        { link_id: circuitoId, nuevo_nombre: nuevoNombre }
      );
      const { link_id } = response.data;
      setCircuitos(
        circuitos.map((circuito) => {
          if (circuito.id === link_id) return { ...circuito, nombre: nuevoNombre };
          return circuito;
        })
      );
      setEditingCircuito(null);
      setEditedNombre("");
      setIsEditingName(false);
      setEditingOrEjecting(false);
    } catch (error) {
      console.error("Error al actualizar el nombre:", error);
    }
  };

  const handleDeleteClick = (id) => {
    if (window.confirm("¿Está seguro de que quiere borrar el circuito y todos los resultados del mismo?")) {
      handleDeleteCircuito(id);
    }
  };

  const handleDeleteCircuito = async (id) => {
    try {
      await axios.post("http://localhost:8000/circuitos/borrar_circuito/", {
        email: user.email,
        link_id: id,
      });
    } catch (error) {
      console.error(error);
    }
  };

  const handleEditClick = (circuito) => {
    setEditingCircuito(circuito);
    setEditedNombre(circuito.nombre || "");
    setIsEditingName(true);
    setEditingOrEjecting(true);
  };

  const handleNombreChange = (event) => setEditedNombre(event.target.value);

  const handleEditCode = (circuito) => {
    const urlQuirk = `${circuito.url}&cadena=${circuito.cadena}&cod=${circuito.id}`;
    window.location.href = urlQuirk;
  };

  const handleDebugClick = (url, id) => {
    const [baseUrl, hash] = url.split("#");
    const separator = baseUrl.includes("?") ? "&" : "?";
    const newUrl = `${baseUrl}${separator}debug=true&id=${id}${hash ? "#" + hash : ""}`;
    window.location.href = newUrl;
  };

  const [modal, setModal] = useState(false);
  const [idCircuitoCompartir, setIdCircuitoCompartir] = useState(0);
  const [email, setEmail] = useState("");

  const toggle = () => setModal(!modal);

  const seleccionarIdCompartir = (id) => {
    setIdCircuitoCompartir(id);
    toggle();
  };

  const comparitrCircuito = () => {
    fetch("http://localhost:8000/guardar_info/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: email, link_id: idCircuitoCompartir }),
    })
      .then((response) => response.json())
      .then((data) => console.log(data))
      .catch((error) => console.error("Error:", error));
    setIdCircuitoCompartir(0);
    setEmail("");
    toggle();
  };

  return (
    <>
      <div className="mis-circuitos-container">
        <div className="mis-circuitos-header">
          <h2>Circuitos creados</h2>
        </div>
        {translatedCircuito ? (
          <div>
            <div className="mis-circuitos-circuito-header">
              <h3>{nombreCircuito}</h3>
            </div>
            
            {/* NUEVA CUADRÍCULA 2x2 PARA LOS BOTONES */}
            <div 
              className="mis-circuitos-button-container" 
              style={{ 
                display: 'grid', 
                gridTemplateColumns: '1fr 1fr', 
                gap: '20px', 
                maxWidth: '600px', 
                margin: '0 auto',
                paddingBottom: '30px'
              }}
            >
              <button
                onClick={() => handleProviderClick("AWS")}
                style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff', border: '1px solid #ddd', borderRadius: '8px', padding: '20px', cursor: 'pointer', height: '160px', transition: '0.3s' }}
              >
                <img src={braketIcon} alt="Amazon Braket Logo" style={{ maxHeight: '70px', maxWidth: '100%', objectFit: 'contain', marginBottom: '15px' }} />
                <span style={{ fontWeight: 'bold', fontSize: '16px', color: '#333' }}>Amazon Braket</span>
              </button>
              
              <button
                onClick={() => handleProviderClick("IBM")}
                style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff', border: '1px solid #ddd', borderRadius: '8px', padding: '20px', cursor: 'pointer', height: '160px', transition: '0.3s' }}
              >
                <img src={qiskitIcon} alt="Qiskit Logo" style={{ maxHeight: '70px', maxWidth: '100%', objectFit: 'contain', marginBottom: '15px' }} />
                <span style={{ fontWeight: 'bold', fontSize: '16px', color: '#333' }}>Qiskit</span>
              </button>
              
              <button
                onClick={() => handleProviderClick("QASM2")}
                style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff', border: '1px solid #ddd', borderRadius: '8px', padding: '20px', cursor: 'pointer', height: '160px', transition: '0.3s' }}
              >
                <img src={qasmIcon2} alt="OpenQASM 2 Logo" style={{ maxHeight: '70px', maxWidth: '100%', objectFit: 'contain', marginBottom: '15px' }} />
                <span style={{ fontWeight: 'bold', fontSize: '16px', color: '#333' }}>OpenQASM 2</span>
              </button>
              
              <button
                onClick={() => handleProviderClick("QASM3")}
                style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', backgroundColor: '#fff', border: '1px solid #ddd', borderRadius: '8px', padding: '20px', cursor: 'pointer', height: '160px', transition: '0.3s' }}
              >
                <img src={qasmIcon3} alt="OpenQASM 3 Logo" style={{ maxHeight: '70px', maxWidth: '100%', objectFit: 'contain', marginBottom: '15px' }} />
                <span style={{ fontWeight: 'bold', fontSize: '16px', color: '#333' }}>OpenQASM 3</span>
              </button>
            </div>
            {/* FIN DE LA CUADRÍCULA */}

            <div className="mis-circuitos-code-container">
              {selectedProvider === "AWS" && (
                <div className="mis-circuitos-quadrant">
                  <h4>Código AWS:</h4>
                  <pre>{awsCode}</pre>
                  <label htmlFor="selectMaquinaAWS">Seleccionar máquina: </label>
                  <select id="selectMaquinaAWS" value={selectedMaquinaAWS} onChange={(e) => setSelectedMaquinaAWS(e.target.value)}>
                    <option value="">Seleccione una</option>
                    <option value="local">local</option>
                    <option value="sv1">sv1</option>
                    <option value="tn1">tn1</option>
                    <option value="dm1">dm1</option>
                    <option value="ionq">ionq</option>
                    <option value="ionq Aria 1">ionq Aria 1</option>
                    <option value="ionq Aria 2">ionq Aria 2</option>
                    <option value="ionq Forte">ionq Forte</option>
                    <option value="rigetti">rigetti</option>
                    <option value="oqc lucy">oqc lucy</option>
                    <option value="quera aquila">quera aquila</option>
                    <option value="garnet">garnet</option>
                  </select>
                  <div className="mis-circuitos-message">
                    {mensaje ? <p>{mensaje}</p> : <><p>Precio por tarea: {precioTarea} USD</p><p>Precio por shot: {precioShot} USD</p></>}
                  </div>
                  <input type="number" value={selectedShotsAWS} onChange={(e) => setSelectedShotsAWS(Number(e.target.value))} placeholder="Número de shots" />
                  {selectedMaquinaAWS && !["local", "sv1", "dm1", "tn1"].includes(selectedMaquinaAWS) && (
                    <div className="mis-circuitos-cost-info"><p>Costo total: {costoTotal.toFixed(2)} USD</p></div>
                  )}
                  <button onClick={handleEjecutarAwsClick}>Ejecutar AWS</button>
                  {!ejecucionEnCurso && (
                    <p>
                      Su ejecución está en curso, puede comprobar el estado de
                      la misma en la pestaña{" "}
                      <a href="http://localhost:3000/resultados">Resultados</a>.
                    </p>
                  )}
                  {ejecucionCompletada && (
                    <p>
                      Su ejecución ha sido completada. Puede ver los resultados
                      en la pestaña{" "}
                      <a href="http://localhost:3000/resultados">Resultados</a>.
                    </p>
                  )}
                  {noEjecucion === "ERROR" && (
                    <p>
                      La máquina seleccionada no está disponible. Por favor,
                      inténtelo de nuevo más tarde.
                    </p>
                  )}
                  {noEjecucion === "CREDENCIALES" && (
                    <p>
                      Las credenciales de AWS no están configuradas. Por favor,
                      configure las credenciales de AWS en su perfil.
                    </p>
                  )}
                  {isExecutingE && <LoadingOverlay />}
                </div>
              )}

              {selectedProvider === "IBM" && (
                <div className="mis-circuitos-quadrant">
                  <h4>Código IBM:</h4>
                  <pre>{ibmCode}</pre>
                  <label htmlFor="selectMaquinaIBM">Seleccionar máquina: </label>
                  <select id="selectMaquinaIBM" value={selectedMaquinaIBM} onChange={(e) => setSelectedMaquinaIBM(e.target.value)}>
                    <option value="">Seleccione una</option>
                    <option value="local">local</option>
                    <option value="ibmq_qasm_simulator">ibmq_qasm_simulator</option>
                    <option value="simulator_statevector">simulator_statevector</option>
                    <option value="simulator_extended_stabilizer">simulator_extended_stabilizer</option>
                    <option value="simulator_stabilizer">simulator_stabilizer</option>
                    <option value="simulator_mps">simulator_mps</option>
                    <option value="ibm_kyoto">ibm_kyoto</option>
                    <option value="ibm_osaka">ibm_osaka</option>
                    <option value="ibm_brisbane">ibm_brisbane</option>
                    <option value="ibm_sherbrooke">ibm_shebrooke</option>
                  </select>
                  <input type="number" value={selectedShotsIBM} onChange={(e) => setSelectedShotsIBM(e.target.value)} placeholder="Número de shots" />
                  <button onClick={handleEjecutarIbmClick}>Ejecutar IBM</button>
                  {!ejecucionEnCurso && (
                    <p>
                      Su ejecución está en curso, puede comprobar el estado de
                      la misma en la pestaña{" "}
                      <a href="http://localhost:3000/resultados">Resultados</a>.
                    </p>
                  )}
                  {ejecucionCompletada && (
                    <p>
                      Su ejecución ha sido completada. Puede ver los resultados
                      en la pestaña{" "}
                      <a href="http://localhost:3000/resultados">Resultados</a>.
                    </p>
                  )}
                  {noEjecucion === "ERROR" && (
                    <p>
                      La máquina seleccionada no está disponible. Por favor,
                      inténtelo de nuevo más tarde.
                    </p>
                  )}
                  {noEjecucion === "CREDENCIALES" && (
                    <p>
                      Las credenciales de IBM no están configuradas. Por favor,
                      configure las credenciales de IBM en su perfil.
                    </p>
                  )}
                  {isExecutingE && <LoadingOverlay />}
                </div>
              )}
              
              {selectedProvider === "QASM2" && (
                <div className="mis-circuitos-quadrant">
                  <h4>Código OpenQASM 2:</h4>
                  <pre>{qasm2Code}</pre>
                  <label htmlFor="selectMaquinaQASM2">Seleccionar máquina: </label>
                  <select id="selectMaquinaQASM2" value={selectedMaquinaQASM} onChange={(e) => setSelectedMaquinaQASM(e.target.value)}>
                    <option value="">Seleccione una</option>
                    <option value="local">local</option>
                  </select>
                  <input type="number" value={selectedShotsQASM} onChange={(e) => setSelectedShotsQASM(e.target.value)} placeholder="Número de shots" />
                  <button onClick={handleEjecutarQasm2Click}>Ejecutar QASM 2</button>
                  {!ejecucionEnCurso && (
                    <p>
                      Su ejecución está en curso, puede comprobar el estado de
                      la misma en la pestaña{" "}
                      <a href="http://localhost:3000/resultados">Resultados</a>.
                    </p>
                  )}
                  {ejecucionCompletada && (
                    <p>
                      Su ejecución ha sido completada. Puede ver los resultados
                      en la pestaña{" "}
                      <a href="http://localhost:3000/resultados">Resultados</a>.
                    </p>
                  )}
                  {isExecutingE && <LoadingOverlay />}
                </div>
              )}
              
              {selectedProvider === "QASM3" && (
                <div className="mis-circuitos-quadrant">
                  <h4>Código OpenQASM 3:</h4>
                  <pre>{qasm3Code}</pre>
                  <label htmlFor="selectMaquinaQASM3">Seleccionar máquina: </label>
                  <select id="selectMaquinaQASM3" value={selectedMaquinaQASM} onChange={(e) => setSelectedMaquinaQASM(e.target.value)}>
                    <option value="">Seleccione una</option>
                    <option value="local">local</option>
                  </select>
                  <input type="number" value={selectedShotsQASM} onChange={(e) => setSelectedShotsQASM(e.target.value)} placeholder="Número de shots" />
                  <button onClick={handleEjecutarQasm3Click}>Ejecutar QASM 3</button>
                  {!ejecucionEnCurso && (
                    <p>
                      Su ejecución está en curso, puede comprobar el estado de
                      la misma en la pestaña{" "}
                      <a href="http://localhost:3000/resultados">Resultados</a>.
                    </p>
                  )}
                  {ejecucionCompletada && (
                    <p>
                      Su ejecución ha sido completada. Puede ver los resultados
                      en la pestaña{" "}
                      <a href="http://localhost:3000/resultados">Resultados</a>.
                    </p>
                  )}
                  {isExecutingE && <LoadingOverlay />}
                </div>
              )}

            </div>
            {!receivedUrl && <p><button onClick={() => handleSendUrl(selectedCircuitoUrl)}>Crear servicio</button></p>}
            {receivedUrl && <p>El servicio ha sido creado correctamente. Puede acceder a él en la siguiente URL: <a href={receivedUrl}>{receivedUrl}</a></p>}
            {isExecutingS && <LoadingOverlayS />}
            <p><button onClick={handleBack}>Volver</button></p>
          </div>
        ) : (
          <ul className="mis-circuitos-list">
            {circuitos.map((circuito, index) => (
              <li key={index} className="mis-circuitos-circuito-container">
                <div className="mis-circuitos-circuito-header">
                  {editingCircuito === circuito ? (
                    <>
                      <input type="text" value={editedNombre} onChange={handleNombreChange} />
                      <button className="mis-circuitos-blue-button" onClick={() => handleEditNombre(circuito.id, editedNombre)}>Guardar cambios</button>
                    </>
                  ) : (
                    <>
                      <span className="mis-circuitos-circuito-name">
                        <h4>{circuito.nombre ? circuito.nombre : `Circuito ${circuito.id}`}</h4>
                      </span>
                      <span>
                        <button className="mis-circuitos-blue-button" onClick={() => seleccionarIdCompartir(circuito.id)}>Compartir</button>
                      </span>
                      <button disabled={isEditingOrEjecting} className="mis-circuitos-blue-button" onClick={() => handleEditClick(circuito)}>Cambiar nombre</button>
                    </>
                  )}
                </div>
                {circuito.screenshot_url && (
                  <div>
                    <h5>Imagen del circuito:</h5>
                    <img src={circuito.screenshot_url} alt="Screenshot del circuito" className="img-circuito" />
                  </div>
                )}
                <div className="mis-circuitos-circuito-buttons">
                  <div className="mis-circuitos-circuito-buttons-left">
                    <button disabled={isEditingName || isEditingOrEjecting} className="mis-circuitos-icon-button" onClick={() => window.open(circuito.url, "_blank")}>
                      <img src={searchIcon} alt="Ver" title="Ver circuito (Quirk)" className="icon-button" />
                    </button>
                    <button disabled={isEditingName || isEditingOrEjecting} className="mis-circuitos-icon-button" onClick={() => handleEditCode(circuito)}>
                      <img src={editIcon} alt="Editar" title="Editar circuito (Quirk)" className="icon-button" />
                    </button>
                  </div>
                  <div className="mis-circuitos-circuito-buttons-middle">
                    <button disabled={isTranslating || isEditingName || isEditingOrEjecting} className="mis-circuitos-icon-button" onClick={() => {
                        setSelectedCircuitoId(circuito.id);
                        setNombreCircuito(circuito.nombre ? circuito.nombre : `Circuito ${circuito.id}`);
                        handleTranslate(circuito.url, circuito.nombre, circuito.url_desplegada);
                      }}>
                      <img src={playIcon} alt="Ejecutar" title="Ejecutar circuito" className="icon-button" />
                    </button>
                    <button disabled={isEditingName || isEditingOrEjecting} className="mis-circuitos-icon-button" onClick={() => handleDebugClick(circuito.url, circuito.id)}>
                      <img src={debugIcon} alt="Debug" title="Ver errores" className="icon-button" />
                    </button>
                  </div>
                  <div className="mis-circuitos-circuito-buttons-right">
                    <button disabled={isEditingName || isEditingOrEjecting} className="mis-circuitos-icon-button" onClick={() => handleDeleteClick(circuito.id)}>
                      <img src={trashIcon} alt="Borrar" title="Borrar circuito" className="icon-button" />
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
        <Modal isOpen={modal} toggle={toggle} centered={true}>
          <ModalHeader>Compartir circuito</ModalHeader>
          <ModalBody><Label>Email</Label><Input placeholder="example@example.com" type="email" value={email} onChange={(e) => setEmail(e.target.value)} /></ModalBody>
          <ModalFooter>
            <div className="buttons-modal">
              <div className="centrador"><Button color="danger" onClick={toggle}>Cancelar</Button></div>
              <div className="centrador"><Button color="success" onClick={comparitrCircuito}>Añadir</Button></div>
            </div>
          </ModalFooter>
        </Modal>
      </div>
    </>
  );
};

export default withAuthenticationRequired(MisCircuitos, {
  onRedirecting: () => <div>Cargando...</div>,
});