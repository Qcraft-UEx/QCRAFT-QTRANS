import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { withAuthenticationRequired, useAuth0 } from "@auth0/auth0-react";
import { useUserEmail } from "../components/UserEmailContext";
import "../MisCircuitos.css";
import trashIcon from "../assets/trash-icon.png";
import editIcon from "../assets/edit-icon.png";

import {
  Button,
  Modal,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Label,
  Input,
} from "reactstrap";

const MisPuertas = () => {
  const { user } = useAuth0();
  const { setUserEmail, userEmail } = useUserEmail();
  const [puertas, setPuertas] = useState([]);
  const [loading, setLoading] = useState(true);

  // Estados para el modal de edición rápida
  const [modalEditar, setModalEditar] = useState(false);
  const [puertaEditando, setPuertaEditando] = useState(null);
  const [editName, setEditName] = useState("");
  const [editSymbol, setEditSymbol] = useState("");
  const [editDefinition, setEditDefinition] = useState("");

  const QUIRK_URL = "http://localhost:4444/quirk.html";
  const emailActivo = userEmail || (user && user.email);

  const fetchPuertas = useCallback(async () => {
    if (!emailActivo) return;
    setLoading(true);
    try {
      const response = await axios.get(
        `http://localhost:8000/circuitos/obtener_puertas_custom/?email=${encodeURIComponent(emailActivo)}`
      );
      setPuertas(response.data.custom_gates || []);
    } catch (error) {
      console.error("Error al obtener las puertas personalizadas:", error);
    } finally {
      setLoading(false);
    }
  }, [emailActivo]);

  useEffect(() => {
    if (user && user.email && !userEmail) {
      setUserEmail(user.email);
    }
    fetchPuertas();
  }, [user, userEmail, setUserEmail, fetchPuertas]);

  // Construye la URL de Quirk inyectando todas las puertas en 'gates'
  // y, opcionalmente, el circuito de una puerta seleccionada en 'cols'
  const construirUrlQuirk = (puertaSeleccionada = null) => {
    const gatesArray = puertas.map((p) => {
      const defStr = (p.definition || "").trim();
      if (defStr.startsWith("{{")) {
        return {
          id: p.symbol,
          name: p.name,
          matrix: defStr,
        };
      }
      try {
        const parsed = JSON.parse(defStr);
        return {
          id: p.symbol,
          name: p.name,
          circuit: parsed,
        };
      } catch (e) {
        return {
          id: p.symbol,
          name: p.name,
          matrix: defStr,
        };
      }
    });

    let colsIniciales = [];
    if (puertaSeleccionada) {
      const defSel = (puertaSeleccionada.definition || "").trim();
      if (defSel.startsWith("{") && !defSel.startsWith("{{")) {
        try {
          const parsedSel = JSON.parse(defSel);
          colsIniciales = parsedSel.cols || [];
        } catch (e) {
          colsIniciales = [[puertaSeleccionada.symbol]];
        }
      } else {
        colsIniciales = [[puertaSeleccionada.symbol]];
      }
    }

    const circuitPayload = {
      cols: colsIniciales,
      gates: gatesArray,
    };

    const encodedCircuit = encodeURIComponent(JSON.stringify(circuitPayload));
    return `${QUIRK_URL}?user=${encodeURIComponent(emailActivo)}#circuit=${encodedCircuit}`;
  };

  const abrirModalEditar = (puerta) => {
    setPuertaEditando(puerta);
    setEditName(puerta.name || "");
    setEditSymbol(puerta.symbol || "");
    setEditDefinition(puerta.definition || "");
    setModalEditar(true);
  };

  const handleGuardarEdicion = async () => {
    if (!puertaEditando) return;
    try {
      await axios.post("http://localhost:8000/circuitos/editar_puerta_custom/", {
        email: emailActivo,
        gate_id: puertaEditando.id,
        name: editName,
        symbol: editSymbol,
        definition: editDefinition,
      });
      setModalEditar(false);
      setPuertaEditando(null);
      fetchPuertas();
    } catch (error) {
      console.error("Error al editar la puerta:", error);
      alert("No se pudo guardar la edición. Comprueba que no exista otra puerta con el mismo nombre.");
    }
  };

  const handleAbrirEnQuirk = (puerta = null) => {
    const url = construirUrlQuirk(puerta);
    window.location.href = url;
  };

  const handleBorrarPuerta = async (puerta) => {
    if (!window.confirm(`¿Está seguro de que quiere borrar la puerta "${puerta.name}"?`)) {
      return;
    }
    try {
      await axios.delete(
        `http://localhost:8000/circuitos/borrar_puerta_custom/?email=${encodeURIComponent(emailActivo)}&gate_id=${encodeURIComponent(puerta.id)}`
      );
      setPuertas((prev) => prev.filter((p) => p.id !== puerta.id));
    } catch (error) {
      if (error.response && error.response.data && error.response.data.error) {
        alert(error.response.data.error);
      } else {
        console.error("Error al borrar la puerta:", error);
        alert("Error al eliminar la puerta.");
      }
    }
  };

  return (
    <div className="mis-circuitos-container">
      <div
        className="mis-circuitos-header"
        style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px" }}
      >
        <h2>Mis Puertas (Quirk)</h2>
        {emailActivo && (
          <button
            className="mis-circuitos-blue-button"
            onClick={() => handleAbrirEnQuirk(null)}
          >
            Abrir editor Quirk
          </button>
        )}
      </div>

      {loading ? (
        <p>Cargando puertas personalizadas...</p>
      ) : puertas.length === 0 ? (
        <p style={{ marginTop: "20px" }}>
          No tienes puertas personalizadas guardadas todavía. Créalas en Quirk y aparecerán aquí automáticamente.
        </p>
      ) : (
        <ul className="mis-circuitos-list">
          {puertas.map((puerta) => (
            <li key={puerta.id} className="mis-circuitos-circuito-container">
              <div className="mis-circuitos-circuito-header">
                <span className="mis-circuitos-circuito-name">
                  <h4>{puerta.name}</h4>
                </span>
                <span
                  style={{
                    backgroundColor: "#e9ecef",
                    padding: "4px 10px",
                    borderRadius: "4px",
                    fontWeight: "bold",
                    fontFamily: "monospace",
                  }}
                >
                  Símbolo: {puerta.symbol}
                </span>
              </div>

              {/* Representación visual de la puerta (diagrama de circuito o matriz) */}
              {puerta.diagram && (
                <div
                  style={{
                    margin: "12px 0",
                    padding: "12px",
                    backgroundColor: "#fff",
                    border: "1px solid #e0e0e0",
                    borderRadius: "6px",
                    textAlign: "center",
                    overflowX: "auto",
                  }}
                >
                  {puerta.diagram.type === "image" ? (
                    <img
                      src={puerta.diagram.data}
                      alt={`Diagrama de ${puerta.name}`}
                      style={{ maxHeight: "140px", maxWidth: "100%", height: "auto" }}
                    />
                  ) : (
                    <pre
                      style={{
                        display: "inline-block",
                        margin: 0,
                        padding: "8px 16px",
                        backgroundColor: "#f0f4ff",
                        border: "1px solid #c2d7ff",
                        borderRadius: "6px",
                        fontFamily: "monospace",
                        fontSize: "14px",
                        fontWeight: "bold",
                        color: "#174ea6",
                      }}
                    >
                      {puerta.diagram.data}
                    </pre>
                  )}
                </div>
              )}

              <div style={{ margin: "10px 0", textAlign: "left" }}>
                <small style={{ color: "#666", display: "block", marginBottom: "4px" }}>
                  Definición / Circuito:
                </small>
                <pre
                  style={{
                    backgroundColor: "#f8f9fa",
                    padding: "8px",
                    borderRadius: "4px",
                    fontSize: "12px",
                    maxHeight: "90px",
                    overflowY: "auto",
                    margin: 0,
                  }}
                >
                  {puerta.definition}
                </pre>
              </div>

              <div
                className="mis-circuitos-circuito-buttons"
                style={{ justifyContent: "space-between", marginTop: "12px" }}
              >
                <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                  {/* <button
                    className="mis-circuitos-blue-button"
                    onClick={() => abrirModalEditar(puerta)}
                    title="Editar nombre o definición"
                  >
                    Editar
                  </button> */}
                  <button
                    className="mis-circuitos-icon-button"
                    onClick={() => handleAbrirEnQuirk(puerta)}
                    title="Editar circuito en Quirk"
                  >
                    <img src={editIcon} alt="Editar en Quirk" className="icon-button" />
                  </button>
                </div>

                <div>
                  <button
                    className="mis-circuitos-icon-button"
                    onClick={() => handleBorrarPuerta(puerta)}
                    title="Borrar puerta"
                  >
                    <img src={trashIcon} alt="Borrar" className="icon-button" />
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}

      <Modal isOpen={modalEditar} toggle={() => setModalEditar(!modalEditar)} centered={true}>
        <ModalHeader toggle={() => setModalEditar(!modalEditar)}>
          Editar puerta personalizada
        </ModalHeader>
        <ModalBody>
          <div className="mb-3">
            <Label>Nombre de la puerta</Label>
            <Input
              type="text"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
            />
          </div>
          <div className="mb-3">
            <Label>Símbolo en Quirk</Label>
            <Input
              type="text"
              value={editSymbol}
              onChange={(e) => setEditSymbol(e.target.value)}
            />
          </div>
          <div className="mb-3">
            <Label>Definición (Matriz o JSON de circuito)</Label>
            <Input
              type="textarea"
              rows="4"
              value={editDefinition}
              onChange={(e) => setEditDefinition(e.target.value)}
            />
          </div>
        </ModalBody>
        <ModalFooter>
          <Button color="secondary" onClick={() => setModalEditar(false)}>
            Cancelar
          </Button>
          <Button color="primary" onClick={handleGuardarEdicion}>
            Guardar cambios
          </Button>
        </ModalFooter>
      </Modal>
    </div>
  );
};

export default withAuthenticationRequired(MisPuertas, {
  onRedirecting: () => <div>Cargando...</div>,
});