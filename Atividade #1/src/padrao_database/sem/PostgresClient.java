package padrao_database.sem;

public class PostgresClient {

    private final String host;
    private final int porta;
    private final String database;

    public PostgresClient(String host, int porta, String database) {
        this.host = host;
        this.porta = porta;
        this.database = database;
    }

    public void conectar(){
        System.out.println("Conexao direta ao Postgres em: " + this.host + ":" + this.porta + "/" + database);
    }

    public void desconectar(){
        System.out.println("Desconectando do Postgres...");
    }

    public void inserirUsuario(String nome){
        System.out.println("[INSERT] Postgres executou: INSERT INTO users (nome) VALUES ('"+ nome +"')");
    }


}
