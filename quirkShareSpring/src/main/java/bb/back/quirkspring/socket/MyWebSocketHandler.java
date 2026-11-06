package bb.back.quirkspring.socket;
import bb.back.quirkspring.util.Circuit;
import bb.back.quirkspring.util.CodeGenerator;
import bb.back.quirkspring.util.Gate;
import bb.back.quirkspring.util.ModInit;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;


import java.io.IOException;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class MyWebSocketHandler extends TextWebSocketHandler {

    private ObjectMapper objectMapper = new ObjectMapper();

    private Map<String, Circuit> mapCircuit = new HashMap<>();

    public MyWebSocketHandler() {
        mapCircuit = new HashMap<>();
    }


    @Override
    public synchronized void afterConnectionEstablished(WebSocketSession session) throws Exception {
        ObjectNode message = objectMapper.createObjectNode();
        message.put("action", "connect");
        session.sendMessage(new TextMessage(message.toString()));
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws Exception {
        String payload = message.getPayload();
        try{
            System.out.println(message.getPayload().toString());
            JsonNode jsonNode = objectMapper.readTree(payload);
            String messageType = jsonNode.get("action").asText();
            switch(messageType){
                case "enterCircuit":
                    enterCircuit(session, jsonNode);
                    break;
                case "sendCircuit":
                    modCircuit(session, jsonNode);
                    break;
                case "createCircuit":
                    createCircuit(session);
                    break;
                case "undoCircuit":
                    undoCircuit(session, jsonNode);
                    break;
                case "redoCircuit":
                    redoCircuit(session, jsonNode);
                    break;
                case "clearCircuit":
                    clearCircuit(session, jsonNode);
                    break;
                case "sendInit":
                    sendInit(session, jsonNode);
                    break;
                case "sendGate":
                    sendGate(session, jsonNode);
                    break;
                default:
                    break;
            }
        }catch (JsonProcessingException e){
            e.printStackTrace();
        }
    }


    public void createCircuit(WebSocketSession session) throws JsonProcessingException {
        String codigo = CodeGenerator.generateCode();
        Circuit circuit = new Circuit(codigo);
        mapCircuit.put(codigo, circuit);
        circuit.addSession(session);
        System.out.println("Circuit creado " + codigo);
        ObjectMapper objectMapper = new ObjectMapper();
        ObjectNode message = objectMapper.createObjectNode();
        message.put("action", "createCircuit");
        message.put("cod", codigo);
        try {
            session.sendMessage(new TextMessage(message.toString()));
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }



    public void enterCircuit(WebSocketSession session, JsonNode jsonNode) throws JsonProcessingException {
        String codigo = jsonNode.get("cod").asText();
        if(!mapCircuit.containsKey(codigo)){
            Circuit circuit = new Circuit(codigo);
            mapCircuit.put(codigo, circuit);
            circuit = mapCircuit.get(codigo);
            circuit.addSession(session);
            //System.out.println("Session añadida a circuit " + codigo);
            ObjectMapper objectMapper = new ObjectMapper();
            ObjectNode message = objectMapper.createObjectNode();
            message.put("action", "createCircuit");
            message.put("cod", codigo);
            message.put("circuit", circuit.getCircuito());
            try {
                session.sendMessage(new TextMessage(message.toString()));
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }else{
            Circuit circuit = mapCircuit.get(codigo);
            circuit.addSession(session);
            //System.out.println("Session añadida a circuit " + codigo);
            ObjectMapper objectMapper = new ObjectMapper();
            ObjectNode message = objectMapper.createObjectNode();
            message.put("action", "enterCircuit");
            message.put("cod", codigo);
            message.put("circuit", circuit.getCircuito());
            try {
                session.sendMessage(new TextMessage(message.toString()));
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }
    }

    public void undoCircuit(WebSocketSession session, JsonNode jsonNode) throws JsonProcessingException {
        String cod = jsonNode.get("cod").asText();
        Circuit circuit = mapCircuit.get(cod);
        if(circuit != null){
            circuit.undoCircuit();
        }
    }

    public void redoCircuit(WebSocketSession session, JsonNode jsonNode) throws JsonProcessingException {
        String cod = jsonNode.get("cod").asText();
        Circuit circuit = mapCircuit.get(cod);
        if(circuit != null){
            circuit.redoCircuit();
        }
    }
public void clearCircuit(WebSocketSession session, JsonNode jsonNode) throws JsonProcessingException {
        String cod = jsonNode.get("cod").asText();
        Circuit circuit = mapCircuit.get(cod);
        if(circuit != null){
            circuit.clearCircuit();
        }
}


    public void modCircuit(WebSocketSession session, JsonNode jsonNode) {
        try{
            ObjectMapper mapper = new ObjectMapper();
            String cod = jsonNode.get("cod").asText();
            JsonNode updateCircuit = jsonNode.get("updateCircuit");
            Circuit circuit = mapCircuit.get(cod);
            if(circuit != null){
                /*
                if (updateCircuit != null && jsonNode.has("gates")) {
                    JsonNode gatesArray = jsonNode.get("gates");

                    if (gatesArray.isArray()) {
                        for (JsonNode gateNode : gatesArray) {
                            String id = gateNode.path("id").asText(); // null si no existe
                            String name = gateNode.path("name").asText(null); // null si no existe

                            String circuitGate = gateNode.get("circuit").toString();

                            Gate gate;
                            if (name != null && !name.isEmpty()) {
                                gate = new Gate(id, name, circuitGate);
                            } else {
                                gate = new Gate(id, circuitGate);
                            }

                            circuit.addGate(gate);
                        }
                    }
                }
                 */

                boolean check = circuit.addMod(updateCircuit.get("x").asInt(), updateCircuit.get("y").asInt(),updateCircuit.get("element").asText(), updateCircuit.get("mod").asText());
                if(check){
                    //circuit.addTypeMod("mod");
                    circuit.sendCircuit();
                }
            }
        } catch (Exception e) {
            throw new RuntimeException(e);
        }

    }

    public void sendInit(WebSocketSession session, JsonNode jsonNode) throws JsonProcessingException {
        String cod = jsonNode.get("cod").asText();
        Circuit circuit = mapCircuit.get(cod);
        if(circuit != null){
            JsonNode updateInit = jsonNode.get("updateInit");
            Integer x = updateInit.path("x").asInt();
            String element = updateInit.path("element").asText(null);
            String mod = updateInit.path("mod").asText(null);
             circuit.addModInit(x, element, mod);
            //circuit.addTypeMod("init");
             circuit.sendCircuit();
        }
    }

    public void sendGate(WebSocketSession session, JsonNode jsonNode) throws JsonProcessingException {
        String cod = jsonNode.get("cod").asText();
        String gate = jsonNode.get("gate").toString();
        if(mapCircuit.containsKey(cod)){
            Circuit circuit = mapCircuit.get(cod);
            circuit.addGate(gate);
            //circuit.addTypeMod("gate");
            circuit.sendCircuit();
        }
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) throws Exception {
        System.out.println("afterConnectionClosed");
        for (Circuit circuit : mapCircuit.values()) {
            if(circuit != null){
                if(circuit.getSesions().contains(session)){
                    session.close();
                    circuit.getSesions().remove(session);
                }
                if(circuit.getSesions().size() == 0){
                    mapCircuit.remove(circuit.getCodigo());
                }
            }
        }
    }

}
