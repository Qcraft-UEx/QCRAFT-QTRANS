package bb.back.quirkspring.util;

public class Gate {
    private String id;
    private String name;
    private String circuit;


    public Gate(String id, String circuit) {
        this.id = id;
        this.name = "";
        this.circuit = circuit;
    }
    public Gate(String id, String name, String circuit) {
        this.id = id;
        this.name = name;
        this.circuit = circuit;
    }

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getCircuit() {
        return circuit;
    }

    public void setCircuit(String circuit) {
        this.circuit = circuit;
    }
}
