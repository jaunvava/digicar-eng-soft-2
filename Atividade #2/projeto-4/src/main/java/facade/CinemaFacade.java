package facade;

import subSistema.Reprodutor;
import subSistema.SistemaSom;

public class CinemaFacade {

    private Projetor projetor = new Projetor();
    private SistemaSom sistemaDeSom = new SistemaSom();
    private Reprodutor reprodutor = new Reprodutor();


    public void assistirFilme() {
        projetor.ligar();
        sistemaDeSom.ligar();
        reprodutor.reproduzir();
    }

}
