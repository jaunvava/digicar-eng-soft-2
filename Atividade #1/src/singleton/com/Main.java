package singleton.com;

public class Main {

    public static void main(String[] args) {

        Configuracao config1 = Configuracao.getInstance();
        Configuracao config2 = Configuracao.getInstance();

        config1.setTema("escuro");

        System.out.println("Tema da config1: " + config1);
        System.out.println("Tema da config2: " + config2);
        System.out.println("Mesma instancia? " + (config1 == config2));

    }

}
