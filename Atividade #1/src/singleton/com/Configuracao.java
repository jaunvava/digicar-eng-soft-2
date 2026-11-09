package singleton.com;

public class Configuracao {

    // A unica instancia e criada quando a classe e carregada.
    private static final Configuracao INSTANCIA = new Configuracao();

    private String tema = "claro";

    private Configuracao(){}

    public static Configuracao getInstance() {

        return INSTANCIA;
    }

    public String getTema() {
        return tema;
    }

    public void setTema(String tema) {
        this.tema = tema;
    }

    @Override
    public String toString() {
        return this.tema;
    }
}
