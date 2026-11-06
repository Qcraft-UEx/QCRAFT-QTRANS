package bb.back.quirkspring.util;

import java.util.Objects;

public class ModInit {
    private Integer x;
    private String element;
    private String mod;

    public ModInit(Integer x, String element, String mod) {
        this.x = x;
        this.element = element;
        this.mod = mod;
    }

    public Integer getX() {
        return x;
    }

    public void setX(Integer x) {
        this.x = x;
    }

    public String getElement() {
        return element;
    }

    public void setElement(String element) {
        this.element = element;
    }

    public String getMod() {
        return mod;
    }

    public void setMod(String mod) {
        this.mod = mod;

    }

    @Override
    public boolean equals(Object o) {
        if (!(o instanceof ModInit modInit)) return false;
        return Objects.equals(getX(), modInit.getX()) && Objects.equals(getElement(), modInit.getElement()) && Objects.equals(getMod(), modInit.getMod());
    }

    @Override
    public int hashCode() {
        return Objects.hash(getX(), getElement(), getMod());
    }

    @Override
    public String toString() {
        return "ModInit{" +
                "x=" + x +
                ", element='" + element + '\'' +
                ", mod='" + mod + '\'' +
                '}';
    }
}
