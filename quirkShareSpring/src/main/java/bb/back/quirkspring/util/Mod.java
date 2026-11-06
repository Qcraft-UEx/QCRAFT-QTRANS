package bb.back.quirkspring.util;

import java.util.Objects;

public class Mod {
    private Integer x;
    private Integer y;
    private String element;
    private String mod;

    public Mod(Integer x, Integer y, String element, String mod) {
        this.x = x;
        this.y = y;
        this.element = element;
        this.mod = mod;
    }

    public Mod(){

    }

    public Integer getX() {
        return x;
    }

    public void setX(Integer x) {
        this.x = x;
    }

    public Integer getY() {
        return y;
    }

    public void setY(Integer y) {
        this.y = y;
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
        if (!(o instanceof Mod mod1)) return false;
        return Objects.equals(getX(), mod1.getX()) && Objects.equals(getY(), mod1.getY()) && Objects.equals(getElement(), mod1.getElement())  && Objects.equals(getMod(), mod1.getMod());
    }

    @Override
    public int hashCode() {
        return Objects.hash(getX(), getY(), getElement(), getMod());
    }

    @Override
    public String toString() {
        return "Mod{" +
                "x=" + x +
                ", y=" + y +
                ", element='" + element + '\'' +
                ", mod='" + mod + '\'' +
                '}';
    }
}
