package bb.back.quirkspring.util;

import java.util.LinkedList;

public class MakerCircuit {
    private LinkedList<Mod> listMod;
    private String circut;
    private LinkedList<LinkedList <String>> matriz;

    public MakerCircuit(LinkedList<Mod> listMod) {
        this.listMod = listMod;
        this.circut = new String();
        this.matriz = new LinkedList<>();
    }

    /*
     *
     *
        Añadir los UUID
     *
     *
     */
    private void makeMod(){
        Mod mod = listMod.get(listMod.size() - 1);
        switch (mod.getMod()){
            case "createCircuit":
                LinkedList <String> colum = new LinkedList<>();
                for (int i =0; i<mod.getY(); i++){
                    colum.add("1");
                }
                colum.add(mod.getY(),mod.getElement());
                matriz.add( colum);
                break;
            default:
                break;
        }
    }
    private boolean esNumero(String str) {
        return str.matches("-?\\d+(\\.\\d+)?");
    }
    private void make () {
        this.circut = "";
        char comilla = '"';
        String initCircuit = "{"+comilla+"cols"+comilla+":[";
        this.circut = circut.concat(initCircuit);

        for (int i =0; i<matriz.size(); i++){
            // inicio columna
            String initColum = "[";
            // si no es la primera se mete la coma
            if(i!=0){
                initColum = ","+initColum;
            }
            // se crea la columan
            for (int e =0; e<matriz.get(i).size(); e++){
                // Si no es la primera se inserta coma
                String element = "";
                if(e!=0){
                    element = ",";
                }
                // si no es numero se le añaden la comillas
                if("1".equals(matriz.get(i).get(e))){
                    element = element+matriz.get(i).get(e);
                }else{
                    element = element+comilla+matriz.get(i).get(e)+comilla;
                }
                initColum = initColum + element;
            }

            initColum =initColum+ "]";
            this.circut = circut.concat(initColum);
        }

        String finalCircuit = "]}";
        this.circut = circut.concat(finalCircuit);

    }


    public String getCircut() {
        makeMod();
        make();
        return circut;
    }
    public void setCircuti(String circut) {
        this.circut = circut;
    }
    public LinkedList<Mod> getListMod() {
        return listMod;
    }
    public void setListMod(LinkedList<Mod> listMod) {
        this.listMod = listMod;
    }
}
