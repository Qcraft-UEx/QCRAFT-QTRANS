package bb.back.quirkspring.util;


import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;

public class Circuit {
    private LinkedList<LinkedList<LinkedList<String>>> listaMatrices;
    private LinkedList<LinkedList<String>> matriz;

    private String circuito;

    private String codigo;

    private LinkedList<Mod> listMod;
    private LinkedList<String> listModInit;
    private LinkedList<LinkedList<String>> listModHistoryInit;
    private LinkedList<String> listGates;

    private LinkedList<String> circuitList;

    private ArrayList<WebSocketSession> sesions;

    private Integer columnaEmpty = -1;

    private Integer postListCircuit = -1;
    private Integer postMod = 0;
    private Integer postInit = -1;
    private Integer postGate = -1;
    private LinkedList<String> listTypeMods;

    /**
     * Constructor de la clase Circuit
     *
     * @param codigo identificador del circuito
     */
    public Circuit(String codigo) {
        listaMatrices = new LinkedList<>();
        this.codigo = codigo;
        circuito = "";
        listMod = new LinkedList<>();
        sesions = new ArrayList<>();
        matriz = new LinkedList<>();
        circuitList = new LinkedList<>();
        listModInit = new LinkedList<>();
        listGates = new LinkedList<>();
        listModHistoryInit = new LinkedList<>();
        listTypeMods = new LinkedList<>();
        listaMatrices.add(new LinkedList<>());
        this.circuitList.add("{\"cols\":[]}");
    }

    // ---------- Métodos públicos principales ----------

    /**
     * Agrega un módulo al circuito
     */
    public boolean addMod(Integer x, Integer y, String element, String mod) {
        try {
            Mod modNew = new Mod();
            modNew.setX(x);
            modNew.setY(y);
            modNew.setElement(element);
            modNew.setMod(mod);
            listMod.add(modNew);
            makeMod();


            listaMatrices.add(postMod + 1, clonarMatriz(matriz));

            postMod++;
            if ((listaMatrices.size() - 1) > postMod) {
                listaMatrices.subList(postMod + 1, listaMatrices.size()).clear();
            }

            if (listaMatrices.size() > 0 && listaMatrices.size() > postMod) {
                this.matriz = clonarMatriz(listaMatrices.get(postMod));
            }

            listTypeMods.add("mod");

            postListCircuit = listTypeMods.size() - 1;

            return true;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        }
    }

    public void addElementWithColumn(Mod mod) {
        if (matriz == null) {
            matriz = new LinkedList<>();
        }
        // Vemos si existe la columna
        if (matriz.size() > mod.getX()) {
            LinkedList<String> colum = new LinkedList<>();
            //LinkedList<String> columUUID = new LinkedList<>();
            for (int i = 0; i < mod.getY(); i++) {
                colum.add("1");
                //columUUID.add("1");
            }
            colum.add(mod.getY(), mod.getElement());
            // columUUID.add(mod.getY(), mod.getUuid());
            matriz.add(mod.getX(), colum);
        }
    }

    public void addElement(Mod mod) {
        if (matriz == null) {
            matriz = new LinkedList<>();
        }
        // Vemos si existe la columna
        if (matriz.size() > mod.getX()) {
            LinkedList<String> column = matriz.get(mod.getX());
            // si el tamaño es mayor o igual a la posición del insert
            // sino rellenamos e insertamos el elemento
            if (column.size() > mod.getY()) {
                // si hay un elemento esta con un valor  en ese caso desplazamos la columna
                // sino añadimos
                if (!matriz.get(mod.getX()).get(mod.getY()).equals("1")) {
                    matriz.set(mod.getX(), column);
                    LinkedList<String> colum = new LinkedList<>();
                    //LinkedList<String> columUUID = new LinkedList<>();
                    for (int i = 0; i < mod.getY(); i++) {
                        colum.add("1");
                        //columUUID.add("1");
                    }
                    colum.add(mod.getY(), mod.getElement());
                    // columUUID.add(mod.getY(), mod.getUuid());
                    matriz.add(mod.getX(), colum);
                } else {
                    matriz.get(mod.getX()).set(mod.getY(), mod.getElement());
                }
            } else {
                // si es
                for (int i = column.size(); i < mod.getY(); i++) {
                    matriz.get(mod.getX()).add("1");
                }
                matriz.get(mod.getX()).add(mod.getElement());
            }
        } else {
            LinkedList<String> colum = new LinkedList<>();
            // LinkedList<String> columUUID = new LinkedList<>();
            for (int i = 0; i < mod.getY(); i++) {
                colum.add("1");
                // columUUID.add("1");
            }
            colum.add(mod.getY(), mod.getElement());
            // columUUID.add(mod.getY(), mod.getUuid());
            if (matriz.size() == 0) {
                matriz.add(colum);
            } else {
                matriz.add(mod.getX(), colum);
            }
        }
    }

    public void removeElement(Mod mod) {
        // Si no hay matriz aún, no hay nada que eliminar
        if (matriz == null) {
            return;
        }

        int x = mod.getX();
        int y = mod.getY();

        // Validamos que exista la columna x
        if (x < 0 || x >= matriz.size()) {
            return;
        }

        LinkedList<String> column = matriz.get(x);

        // Validamos que exista la posición y
        if (y < 0 || y >= column.size()) {
            return;
        }

        // Eliminamos directamente el elemento (y su UUID)
        column.set(y, "1");

        // Recortamos todos los "1" al final de la columna
        while (!column.isEmpty() && "1".equals(column.getLast())) {
            column.removeLast();
        }

        LinkedList<String> columaVacia = new LinkedList<>();
        columaVacia.add("EMPTY");
        // Si tras recortar la columna queda vacía, la eliminamos por completo
        if (column.isEmpty() && matriz.size() - 1 > x) {
            matriz.set(x, columaVacia);
        }
        if (column.isEmpty() && matriz.size() - 1 == x) {
            matriz.removeLast();
        }


    }


    private void makeMod() {
        Mod mod = listMod.getLast();
        if (mod.getMod().equals("add")) {
            addElement(mod);
        } else if (mod.getMod().equals("addWithColumn")) {
            addElementWithColumn(mod);
        } else {
            removeElement(mod);
        }
    }

    /**
     * Envía el estado actual del circuito a todas las sesiones WebSocket
     */
    public void sendCircuit() {
        ObjectMapper objectMapper = new ObjectMapper();
        try {
            make();
            borrarEmpty();
            this.circuitList.add(this.circuito);
            System.out.println(this.circuito);
            ObjectNode message = objectMapper.createObjectNode();
            message.put("action", "reciveCircuit");
            message.put("circuit", circuito);
            for (WebSocketSession session : sesions) {
                if (session.isOpen()) {
                    session.sendMessage(new TextMessage(message.toString()));
                }
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Deshace la última acción del circuito
     */
    public void undoCircuit() {
        if (postListCircuit < 0) {
            return;
        }
        String mod = listTypeMods.get(postListCircuit);
        if (mod.equals("mod")) {
            postMod--;
            if (postMod >= 0 && listaMatrices.size() > postMod) {
                this.matriz = clonarMatriz(listaMatrices.get(postMod));
            }
        } else if (mod.equals("init")) {
            postInit--;
            if (postInit >= 0 && listModHistoryInit.size() > postInit) {
                this.listModInit = clonarLista(
                        listModHistoryInit.get(postInit)
                );
            } else {
                if (postInit < 0) {
                    this.listModInit = new LinkedList<>();
                }
            }
        } else if (mod.equals("gate")) {
            postGate--;
        }


        postListCircuit--;
        sendCircuit();
    }

    /**
     * Rehace una acción previamente deshecha
     */
    public void redoCircuit() {
        if (listTypeMods.size() > postListCircuit + 1) {
            postListCircuit++;

            String mod = listTypeMods.get(postListCircuit);
            if (mod.equals("mod")) {
                postMod++;
                if (postMod >= 0 && listaMatrices.size() > postMod) {
                    this.matriz = clonarMatriz(listaMatrices.get(postMod));
                }
            } else if (mod.equals("init")) {
                postInit++;
                if (postInit >= 0 && listModHistoryInit.size() > postInit) {
                    this.listModInit = clonarLista(
                            listModHistoryInit.get(postInit)
                    );
                }
            } else if (mod.equals("gate")) {
                postGate++;
            }


            sendCircuit();
        }
    }

    /**
     * Limpia el circuito actual
     */
    public void clear() {
        this.circuitList.add("{\"cols\":[]}");
        this.postListCircuit = this.postListCircuit + 1;
        this.matriz = new LinkedList<>();
        this.circuito = this.circuitList.getLast();
        try {
            ObjectMapper objectMapper = new ObjectMapper();
            ObjectNode message = objectMapper.createObjectNode();
            message.put("action", "reciveCircuit");
            message.put("circuit", circuito);
            for (WebSocketSession session : sesions) {
                if (session.isOpen()) {
                    session.sendMessage(new TextMessage(message.toString()));
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    /**
     * Agrega una compuerta lógica al circuito
     */
    public void addGate(String gate) {
        listGates.add(gate);
        postGate++;
        if ((listGates.size() - 1) > postGate) {
            listGates.subList(postGate + 1, listGates.size()).clear();
        }

        this.postGate++;
        listTypeMods.add("gate");

        postListCircuit = listTypeMods.size() - 1;
    }

    /**
     * Construye el string JSON para las compuertas lógicas
     */
    public String buildGateString() {
        if (postGate == -1) {
            return "";
        }
        if (this.listGates.size() == 0) {
            return "";
        }
        String sb = ",\"gates\":[";
        int count = 0;
        for (int i = 0; i < postGate; i++) {
            String gate = listGates.get(i);
            sb = sb.concat(gate);
            count++;
            if (count < this.listGates.size()) {
                sb = sb.concat(",");
            }
        }
        sb = sb.concat("]");
        return sb;
    }

    /**
     * Agrega o modifica la lista de inicialización de módulos
     */
    public boolean addModInit(Integer x, String element, String type) {
        insertModInt(x, element, type);
        if (listModHistoryInit.size() > 0) {
            listModHistoryInit.add(postInit + 1, this.listModInit);
        } else {
            listModHistoryInit.add(this.listModInit);
        }
        postInit++;
        if ((listModHistoryInit.size() - 1) > postInit) {
            listModHistoryInit.subList(postInit + 1, listModHistoryInit.size()).clear();
        }

        if (listModHistoryInit.size() > 0 && listModHistoryInit.size() > postInit) {
            this.listModInit = clonarLista(listModHistoryInit.get(postInit));
        }

        listTypeMods.add("init");

        postListCircuit = listTypeMods.size() - 1;
        return true;
    }

    public void insertModInt(Integer x, String element, String type) {
        if (type.equals("add")) {
            if (x >= listModInit.size()) {
                for (int i = listModInit.size(); i <= x; i++) {
                    if (x == i) {
                        if (element.equals("0") || element.equals("1")) {
                            listModInit.add(element);
                        } else {
                            listModInit.add("\"" + element + "\"");
                        }
                    } else {
                        listModInit.add("0");
                    }
                }
            } else {
                if (element.equals("0") || element.equals("1")) {
                    listModInit.set(x, element);
                } else {
                    listModInit.set(x, "\"" + element + "\"");
                }
            }
        } else if (type.equals("remove")) {
            listModInit.removeLast();
        } else if (type.equals("modify")) {
            if (element.equals("0") || element.equals("1")) {
                listModInit.set(x, element);
            } else {
                listModInit.set(x, "\"" + element + "\"");
            }
        }
    }

    /**
     * Construye el string JSON de la inicialización de módulos
     */
    public String buildModInitString() {
        boolean vacia = true;
        if (postInit == -1) {
            return "";
        }
        for (int i = 0; i < listModInit.size(); i++) {
            String key = listModInit.get(i);
            if (!key.equals("0")) {
                vacia = false;
            }
        }
        if (vacia) {
            listModInit.clear();
            return "";
        }

        StringBuilder sb = new StringBuilder();
        sb.append(",\"init\":[");
        int count = 0;
        for (int i = 0; i < listModInit.size(); i++) {
            String modInit = listModInit.get(i);
            sb.append(modInit);
            count++;
            if (count < this.listModInit.size()) {
                sb.append(",");
            }
        }
        sb.append("]");
        return sb.toString();
    }


    public void clearCircuit() {
        this.matriz = new LinkedList<>();
        listaMatrices.add(postMod + 1, clonarMatriz(matriz));
        this.postMod++;
        if ((listaMatrices.size() - 1) > postMod) {
            listaMatrices.subList(postMod + 1, listaMatrices.size()).clear();
        }

        if (listaMatrices.size() > 0 && listaMatrices.size() > postMod) {
            this.matriz = clonarMatriz(listaMatrices.get(postMod));
        }

        listTypeMods.add("mod");

        postListCircuit = listTypeMods.size() - 1;
        sendCircuit();
    }


    public void clearAll() {
        this.matriz = new LinkedList<>();
        listaMatrices.add(postMod + 1, clonarMatriz(matriz));
        this.postMod++;
        if ((listaMatrices.size() - 1) > postMod) {
            listaMatrices.subList(postMod + 1, listaMatrices.size()).clear();
        }

        if (listaMatrices.size() > 0 && listaMatrices.size() > postMod) {
            this.matriz = clonarMatriz(listaMatrices.get(postMod));
        }


        this.listModInit = new LinkedList<>();
        if (listModHistoryInit.size() > 0) {
            listModHistoryInit.add(postInit + 1, this.listModInit);
        } else {
            listModHistoryInit.add(this.listModInit);
        }
        postInit++;
        if ((listModHistoryInit.size() - 1) > postInit) {
            listModHistoryInit.subList(postInit + 1, listModHistoryInit.size()).clear();
        }

        if (listModHistoryInit.size() > 0 && listModHistoryInit.size() > postInit) {
            this.listModInit = clonarLista(listModHistoryInit.get(postInit));
        }

        listGates.add("");
        postGate++;
        if ((listGates.size() - 1) > postGate) {
            listGates.subList(postGate + 1, listGates.size()).clear();
        }

        listTypeMods.add("clearAll");

        postListCircuit = listTypeMods.size() - 1;
    }


    // ---------- Métodos auxiliares internos ----------

    private LinkedList<LinkedList<String>> clonarMatriz(LinkedList<LinkedList<String>> original) {
        LinkedList<LinkedList<String>> copia = new LinkedList<>();
        for (LinkedList<String> fila : original) {
            // Clonamos cada fila (sublista)
            LinkedList<String> copiaFila = new LinkedList<>(fila);
            copia.add(copiaFila);
        }
        return copia;
    }

    /**
     * Crea y devuelve una copia de la lista original.
     *
     * @param original la LinkedList<String> que se desea copiar
     * @return una nueva LinkedList<String> con los mismos elementos que original
     */
    public LinkedList<String> clonarLista(LinkedList<String> original) {
        // El constructor de LinkedList que recibe otra Collection hace automáticamente
        // una copia superficial de los elementos. Con Strings, esto es suficiente.
        return new LinkedList<>(original);
    }


    private void make() {
        this.circuito = "";
        char comilla = '"';
        String initCircuit = "{" + comilla + "cols" + comilla + ":[";
        this.circuito = this.circuito.concat(initCircuit);

        for (int i = 0; i < matriz.size(); i++) {
            // inicio columna
            String initColum = "[";
            // si no es la primera se mete la coma
            if (i != 0) {
                initColum = "," + initColum;
            }
            if (!matriz.get(i).get(0).equals("EMPTY")) {
                // se crea la columan
                for (int e = 0; e < matriz.get(i).size(); e++) {
                    // Si no es la primera se inserta coma
                    String element = "";
                    if (e != 0) {
                        element = ",";
                    }
                    String valor = matriz.get(i).get(e);
                    if ("1".equals(valor)) {
                        element += valor; // Inserta 1 sin comillas
                    } else {
                        element += comilla + valor + comilla; // Todo lo demás con comillas
                    }
                    initColum = initColum + element;
                }
            }

            initColum = initColum + "]";
            this.circuito = this.circuito.concat(initColum);
        }

        String finalCircuit = "]";
        this.circuito = this.circuito.concat(finalCircuit);
        this.circuito = this.circuito.concat( buildGateString() + buildModInitString()+"}");

    }

    private void borrarEmpty() {
        for (int i = 0; i < matriz.size(); i++) {
            if (matriz.get(i).get(0).equals("EMPTY")) {
                matriz.remove(i);
            }
        }
    }

    // ---------- Getters y Setters ----------

    public boolean addSession(WebSocketSession session) {
        return sesions.add(session);
    }

    public ArrayList<WebSocketSession> getSesions() {
        return sesions;
    }

    public void setSesions(ArrayList<WebSocketSession> sesions) {
        this.sesions = sesions;
    }

    public String getCircuito() {
        return circuito;
    }

    public void setCircuito(String circuito) {
        this.circuito = circuito;
    }

    public String getCodigo() {
        return codigo;
    }

    public void setCodigo(String codigo) {
        this.codigo = codigo;
    }

    public LinkedList<Mod> getListMod() {
        return listMod;
    }

    public void setListMod(LinkedList<Mod> listMod) {
        this.listMod = listMod;
    }

    public LinkedList<LinkedList<String>> getMatriz() {
        return matriz;
    }

    public void setMatriz(LinkedList<LinkedList<String>> matriz) {
        this.matriz = matriz;
    }

    public LinkedList<String> getCircuitList() {
        return circuitList;
    }

    public void setCircuitList(LinkedList<String> circuitList) {
        this.circuitList = circuitList;
    }

    public Integer getColumnaEmpty() {
        return columnaEmpty;
    }

    public void setColumnaEmpty(Integer columnaEmpty) {
        this.columnaEmpty = columnaEmpty;
    }

    public LinkedList<String> getListModInit() {
        return listModInit;
    }

    public void setListModInit(LinkedList<String> listModInit) {
        this.listModInit = listModInit;
    }

    public LinkedList<String> getListGates() {
        return listGates;
    }

    public void setListGates(LinkedList<String> listGates) {
        this.listGates = listGates;
    }

    public Integer getPostListCircuit() {
        return postListCircuit;
    }

    public void setPostListCircuit(Integer postListCircuit) {
        this.postListCircuit = postListCircuit;
    }

    @Override
    public String toString() {
        return "Circuit{" +
                "matriz=" + matriz +
                ", circuito='" + circuito + '\'' +
                ", codigo='" + codigo + '\'' +
                ", listMod=" + listMod +
                ", circuitList=" + circuitList +
                ", sesions=" + sesions +
                ", columnaEmpty=" + columnaEmpty +
                ", listaGates=" + listGates +
                ", postListCircuit=" + postListCircuit +
                '}';
    }
}