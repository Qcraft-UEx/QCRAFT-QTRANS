// import React, { Fragment } from "react";
// import { useAuth0 } from "@auth0/auth0-react";
// import Hero from "../components/Hero";
// import Content from "../components/Content";
// import "../Home.css";

// const Home = () => {
//   const { user, isAuthenticated } = useAuth0();

//   const handleCrearCircuito = () => {
//     let url = "http://localhost:4444/quirk.html";
//     if (isAuthenticated && user?.email) {
//       url += `?user=${encodeURIComponent(user.email)}`;
//     }
//     window.location.href = url;
//   };

//   return (
//     <Fragment>
//       <Hero />
//       <div className="centered-button">
//         <button onClick={handleCrearCircuito}>¡Crear circuito!</button>
//       </div>
//       <hr />
//       <Content />
//     </Fragment>
//   );
// };

// export default Home;


// import React, { Fragment } from "react";
// import { useAuth0 } from "@auth0/auth0-react";
// import Hero from "../components/Hero";
// import Content from "../components/Content";
// import "../Home.css";

// const Home = () => {
//   const { user, isAuthenticated } = useAuth0();

//   const handleCrearCircuito = async () => {
//     let url = "http://localhost:4444/quirk.html";
//     let urlParams = "";
//     let hashParams = "";

//     if (isAuthenticated && user?.email) {
//       urlParams = `?user=${encodeURIComponent(user.email)}`;

//       try {
//         const response = await fetch(`http://localhost:8000/circuitos/obtener_puertas_custom/?email=${encodeURIComponent(user.email)}`);
//         const data = await response.json();

//         if (data.custom_gates && data.custom_gates.length > 0) {
//           const circuitData = {
//             cols: [],
//             gates: data.custom_gates.map(g => ({
//               id: g.symbol,
//               name: g.name,
//               matrix: g.definition
//             }))
//           };
//           hashParams = `#circuit=${JSON.stringify(circuitData)}`;
//         }
//       } catch (error) {
//         console.error("Error al cargar puertas custom:", error);
//       }
//     }

//     window.location.href = url + urlParams + hashParams;
//   };


//   return (
//     <Fragment>
//       <Hero />
//       <div className="centered-button">
//         <button onClick={handleCrearCircuito}>¡Crear circuito!</button>
//       </div>
//       <hr />
//       <Content />
//     </Fragment>
//   );
// };

// export default Home;


import React, { Fragment } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import Hero from "../components/Hero";
import Content from "../components/Content";
import "../Home.css";

const Home = () => {
  const { user, isAuthenticated } = useAuth0();

  const handleCrearCircuito = async () => {
    let url = "http://localhost:4444/quirk.html";
    let urlParams = "";
    let hashParams = "";

    if (isAuthenticated && user?.email) {
      urlParams = `?user=${encodeURIComponent(user.email)}`;

      try {
        const response = await fetch(
          `http://localhost:8000/circuitos/obtener_puertas_custom/?email=${encodeURIComponent(user.email)}`
        );
        const data = await response.json();

        if (data.custom_gates && data.custom_gates.length > 0) {
          const gatesArray = data.custom_gates.map((g) => {
            const defStr = (g.definition || "").trim();
            if (defStr.startsWith("{{")) {
              return { id: g.symbol, name: g.name, matrix: defStr };
            }
            try {
              const parsed = JSON.parse(defStr);
              if (parsed && parsed.cols) {
                return { id: g.symbol, name: g.name, circuit: parsed };
              }
            } catch (_) {}
            return { id: g.symbol, name: g.name, matrix: defStr };
          });

          const circuitData = {
            cols: [],
            gates: gatesArray,
          };
          hashParams = `#circuit=${encodeURIComponent(JSON.stringify(circuitData))}`;
        }
      } catch (error) {
        console.error("Error al cargar puertas custom:", error);
      }
    }

    window.location.href = url + urlParams + hashParams;
  };

  return (
    <Fragment>
      <Hero />
      <div className="centered-button">
        <button onClick={handleCrearCircuito}>¡Crear circuito!</button>
      </div>
      <hr />
      <Content />
    </Fragment>
  );
};

export default Home;