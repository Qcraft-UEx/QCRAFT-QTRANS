/**
 * Copyright 2017 Google Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import {notifyAboutRecoveryFromUnexpectedError} from "../fallback.js"
import {CircuitDefinition} from "../circuit/CircuitDefinition.js"
import {CircuitStats} from "../circuit/CircuitStats.js"
import {Config} from "../Config.js"
import {Format} from "../base/Format.js"
import {HistoryPusher} from "../browser/HistoryPusher.js"
import {Matrix} from "../math/Matrix.js"
import {fromJsonText_CircuitDefinition, Serializer} from "../circuit/Serializer.js"
import { takeScreenshotOfCanvas } from "../fallback.js";

// --- GESTIÓN DE USUARIO Y PUERTAS CUSTOM ---
window.userEmail = null;

function extraerUsuarioDeUrl() {
    const urlString = window.location.href;
    const userMatch = urlString.match(/[?&]user=([^&#]+)/);
    
    if (userMatch && userMatch[1]) {
        window.userEmail = decodeURIComponent(userMatch[1]);
        cargarPuertasUsuario(window.userEmail);
    }
}

extraerUsuarioDeUrl();

function cargarPuertasUsuario(email) {
    fetch(`http://localhost:8000/circuitos/obtener_puertas_custom/?email=${encodeURIComponent(email)}`)
        .then(res => res.json())
        .then(data => {
            if (data.custom_gates && data.custom_gates.length > 0) {
                inyectarPuertasEnCircuito(data.custom_gates);
            }
        })
        .catch(err => console.error("Error al cargar puertas del usuario:", err));
}

function inyectarPuertasEnCircuito(puertasBD) {
    window.customGatesBD = puertasBD;
    
    let hash = window.location.hash;
    let jsonText = "{}";
    
    if (hash.includes("circuit=")) {
        const start = hash.indexOf('circuit=') + 8;
        let end = hash.indexOf('&', start);
        if (end === -1) end = hash.length;
        jsonText = decodeURIComponent(hash.substring(start, end));
    }
    
    try {
        let circuito = JSON.parse(jsonText);
        if (!circuito.gates) circuito.gates = []; // Asegúrate de que aquí pone .gates y no .{gates
        
        let huboCambios = false;
        puertasBD.forEach(puertaBD => {
            let existe = circuito.gates.some(g => (typeof g === 'string' ? g === puertaBD.symbol : g.id === puertaBD.symbol));
            if (!existe) {
                let def = (puertaBD.definition || "").trim();
                
                // Si la definición es un JSON de columnas/matriz pero viene sin dobles llaves
                if (def.startsWith("{") || def.startsWith("[")) {
                    try {
                        let parsed = JSON.parse(def);
                        if (parsed.cols) {
                            // Si es un circuito con 'cols', asígnalo a 'circuit' en lugar de 'matrix'
                            circuito.gates.push({
                                id: puertaBD.symbol,
                                name: puertaBD.name || puertaBD.symbol,
                                circuit: parsed
                            });
                        } else {
                            // Si es una matriz pura, envuélvela en el formato que espera Quirk con dobles llaves si es necesario
                            circuito.gates.push({
                                id: puertaBD.symbol,
                                name: puertaBD.name || puertaBD.symbol,
                                matrix: "{{" + def.replace(/^\{|\}$/g, '') + "}}"
                            });
                        }
                        huboCambios = true;
                    } catch (_) {
                        // Fallback si falla el parseo
                        circuito.gates.push({
                            id: puertaBD.symbol,
                            name: puertaBD.name || puertaBD.symbol,
                            matrix: "{{" + def + "}}"
                        });
                        huboCambios = true;
                    }
                } else if (def.startsWith("{{")) {
                    circuito.gates.push({
                        id: puertaBD.symbol,
                        name: puertaBD.name || puertaBD.symbol,
                        matrix: def
                    });
                    huboCambios = true;
                } else {
                    circuito.gates.push(puertaBD.symbol);
                    huboCambios = true;
                }
            }
        });
        
        if (huboCambios) {
            const nuevoHash = "#circuit=" + encodeURIComponent(JSON.stringify(circuito));
            window.location.hash = nuevoHash;
            window.dispatchEvent(new Event('popstate'));
        }
    } catch(e) {
        console.error("Error al inyectar puertas custom en el circuito:", e);
    }
}

function urlWithCircuitHash(jsonText) {
    if (jsonText.indexOf('%') !== -1 || jsonText.indexOf('&') !== -1) {
        jsonText = encodeURIComponent(jsonText);
    }
    return "#" + Config.URL_CIRCUIT_PARAM_KEY + "=" + jsonText;
}

/**
 * @param {!Revision} revision
 */
function initUrlCircuitSync(revision) {
    const getHashParameters = () => {
        let hashText = document.location.hash.substr(1);
        let paramsMap = new Map();
        if (hashText !== "") {
            for (let keyVal of hashText.split("&")) {
                let eq = keyVal.indexOf("=");
                if (eq === -1) {
                    continue;
                }
                let key = keyVal.substring(0, eq);
                let val = decodeURIComponent(keyVal.substring(eq + 1));
                paramsMap.set(key, val);
            }
        }
        return paramsMap;
    };

    const historyPusher = new HistoryPusher();
    const loadCircuitFromUrl = () => {
        try {
            historyPusher.currentStateIsMemorableButUnknown();
            let params = getHashParameters();
            if (!params.has(Config.URL_CIRCUIT_PARAM_KEY)) {
                let def = document.DEFAULT_CIRCUIT || JSON.stringify(Serializer.toJson(CircuitDefinition.EMPTY));
                params.set(Config.URL_CIRCUIT_PARAM_KEY, def);
            }

            let jsonText = params.get(Config.URL_CIRCUIT_PARAM_KEY);
            historyPusher.currentStateIsMemorableAndEqualTo(jsonText);
            let circuitDef = fromJsonText_CircuitDefinition(jsonText);
            let cleanedJson = JSON.stringify(Serializer.toJson(circuitDef));
            revision.clear(cleanedJson);
            if (circuitDef.isEmpty() && params.size === 1) {
                historyPusher.currentStateIsNotMemorable();
            } else {
                let urlHash = urlWithCircuitHash(jsonText);
                historyPusher.stateChange(jsonText, urlHash);
            }
        } catch (ex) {
            notifyAboutRecoveryFromUnexpectedError(
                "Defaulted to an empty circuit. Failed to understand circuit from URL.",
                {document_location_hash: document.location.hash},
                ex);
        }
    };

    window.addEventListener('popstate', loadCircuitFromUrl);
    loadCircuitFromUrl();

    revision.latestActiveCommit().whenDifferent().skip(1).subscribe(jsonText => {
        historyPusher.stateChange(jsonText, urlWithCircuitHash(jsonText));
    });
}

// function obtenerURL() {
//     let url = window.location.href;
//     url = url.replace(/([?&])user=[^&#]+&?/, '$1').replace(/[?&]$/, '');
    
//     const index = url.indexOf("&cadena=");
//     if (index !== -1) {
//         url = url.substring(0, index);
//     }
//     url = decodeURIComponent(url);
//     return url;
// }


function obtenerURL() {
    let url = window.location.href;
    url = url.replace(/([?&])user=([^&#]+)&?/, '$1').replace(/[?&]$/, '');
    
    const index = url.indexOf("&cadena=");
    if (index !== -1) {
        url = url.substring(0, index);
    }
    url = decodeURIComponent(url);
    return url;
}

// Función auxiliar para limpiar y asegurar que el circuito no guarde basura en formato cols plano desestructurado
function obtenerCadenaCircuitoLimpia() {
    let hash = window.location.hash;
    if (hash.includes("circuit=")) {
        const start = hash.indexOf('circuit=') + 8;
        let end = hash.indexOf('&', start);
        if (end === -1) end = hash.length;
        let jsonText = decodeURIComponent(hash.substring(start, end));
        console.log("JSON que se va a enviar a Django:", jsonText);
        try {
            let parsed = JSON.parse(jsonText);
            return JSON.stringify(parsed);
        } catch (e) {
            return jsonText;
        }
    }
    return window.cadenaCircuito || "";
}

window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'get url') {
        const urlQuirk = obtenerURL();
        enviarURLADjango(urlQuirk);
    }
    else if (event.data && event.data.type === 'edit circuit') {
        const urlQuirk = obtenerURL();
        let urlGlobalQuirk = window.urlAntesDeCadena;
        if (urlGlobalQuirk) {
            urlGlobalQuirk = decodeURIComponent(urlGlobalQuirk);
        }
        
        // Usamos la función de limpieza para capturar la cadena correcta del circuito con sus cols/gates bien formados
        let cadenaCircuito = obtenerCadenaCircuitoLimpia();
        
        if (urlQuirk === urlGlobalQuirk) {
            window.location.href = `http://localhost:3000/mis-circuitos`;
        } else {
            enviarURLADjangoEditada(urlQuirk, cadenaCircuito);            
        }
    }    
});


window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'get url') {
        const urlQuirk = obtenerURL();
        enviarURLADjango(urlQuirk);
    }
    else if (event.data && event.data.type === 'edit circuit') {
        const urlQuirk = obtenerURL();
        let urlGlobalQuirk = window.urlAntesDeCadena;
        urlGlobalQuirk = decodeURIComponent(urlGlobalQuirk);
        
        if (urlQuirk === urlGlobalQuirk) {
            window.location.href = `http://localhost:3000/mis-circuitos`;
        } else {
            let cadenaCircuito = window.cadenaCircuito;
            enviarURLADjangoEditada(urlQuirk, cadenaCircuito);            
        }
    }    
});

function obtenerSimbolosPuertasActivas(url) {
    const start = url.indexOf('circuit=');
    if (start === -1) return [];
    let end = url.indexOf('&', start);
    const rawParam = end === -1 ? url.substring(start + 8) : url.substring(start + 8, end);
    try {
        const circuito = JSON.parse(decodeURIComponent(rawParam));
        const usados = new Set();
        (circuito.cols || []).forEach(col => {
            (col || []).forEach(celda => {
                if (typeof celda === 'string' && celda.startsWith('~')) {
                    usados.add(celda.split(':')[0]);
                }
            });
        });
        return Array.from(usados);
    } catch (e) {
        return [];
    }
}

function obtenerMatrizCircuito(urlQuirk) {
    try {
        const start = urlQuirk.indexOf('circuit=');
        if (start === -1) return null;
        let end = urlQuirk.indexOf('&', start);
        const rawJson = end === -1 ? urlQuirk.substring(start + 8) : urlQuirk.substring(start + 8, end);
        const circuitDef = fromJsonText_CircuitDefinition(decodeURIComponent(rawJson));
        const n = circuitDef.numWires;
        if (n > 6) return null;

        const dim = 1 << n;
        const buf = new Float32Array(dim * dim * 2);

        for (let col = 0; col < dim; col++) {
            const initStates = new Map();
            for (let w = 0; w < n; w++) {
                if ((col >> w) & 1) {
                    initStates.set(w, "1");
                }
            }
            const stats = CircuitStats.fromCircuitAtTime(circuitDef.withInitialStates(initStates), 0);
            const stateBuf = stats.finalState.rawBuffer();
            for (let row = 0; row < dim; row++) {
                const dstIdx = (row * dim + col) * 2;
                const srcIdx = row * 2;
                buf[dstIdx] = stateBuf[srcIdx];
                buf[dstIdx + 1] = stateBuf[srcIdx + 1];
            }
        }
        return new Matrix(dim, dim, buf).toString(new Format(false, 0, 7, ","));
    } catch (e) {
        console.warn("No se pudo calcular la matriz del circuito:", e);
        return null;
    }
}

function enviarURLADjangoEditada(urlQuirk, cadenaCircuito) {
    let canvas = document.getElementById("drawCanvas");
    let canvasDataURL = canvas.toDataURL("image/png");

    var data = JSON.stringify({
        urlQuirk: urlQuirk, 
        cadenaCircuito: cadenaCircuito, 
        screenshotUrl: canvasDataURL,
        email: window.userEmail,
        customGates: obtenerSimbolosPuertasActivas(urlQuirk),
        matrix: obtenerMatrizCircuito(urlQuirk)
    });

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://localhost:8000/actualizar_url_circuito/", true);
    xhr.setRequestHeader("Content-Type", "application/json"); 
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.url) {
                    window.location.href = `http://localhost:3000/mis-circuitos`;
                } else {
                    alert("Error al actualizar la URL en el servidor.");
                }
            } else {
                alert("Error en la solicitud al servidor.");
            }
        }
    };
    xhr.onerror = function() {
        alert("Error de red al enviar la solicitud al servidor.");
    };
    xhr.send(data);
}

function enviarURLADjango(urlQuirk) {
    let canvas = document.getElementById("drawCanvas");
    let canvasDataURL = canvas.toDataURL("image/png");

    var data = JSON.stringify({
        urlQuirk: urlQuirk, 
        screenshotUrl: canvasDataURL,
        email: window.userEmail,
        customGates: obtenerSimbolosPuertasActivas(urlQuirk),
        matrix: obtenerMatrizCircuito(urlQuirk)
    });

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "http://localhost:8000/recibir_url_quirk/", true);
    xhr.setRequestHeader("Content-Type", "application/json"); 
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.url && response.cadena) {
                    enviarIDAReact(response.cadena);
                }
            }
        }
    };
    xhr.send(data);
}

function enviarIDAReact(cadena) {
    window.location.href = `http://localhost:3000/receptor-datos?id=${cadena}`;
}

export {initUrlCircuitSync}