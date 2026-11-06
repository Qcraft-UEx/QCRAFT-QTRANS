package bb.back.quirkspring.util;

import java.util.Objects;

public class Celda {

    private String label;
    private String uuid;

    public Celda(String label, String uuid) {
        this.label = label;
        this.uuid = uuid;
    }
    public Celda() {
        this.label = "";
        this.uuid = "";
    }

    public String getLabel() {
        return label;
    }

    public void setLabel(String label) {
        this.label = label;
    }

    public String getUuid() {
        return uuid;
    }

    public void setUuid(String uuid) {
        this.uuid = uuid;
    }

    @Override
    public boolean equals(Object o) {
        if (!(o instanceof Celda celda)) return false;
        return Objects.equals(getLabel(), celda.getLabel()) && Objects.equals(getUuid(), celda.getUuid());
    }

    @Override
    public int hashCode() {
        return Objects.hash(getLabel(), getUuid());
    }

    @Override
    public String toString() {
        return "Celda{" +
                "label='" + label + '\'' +
                ", uuid='" + uuid + '\'' +
                '}';
    }
}
