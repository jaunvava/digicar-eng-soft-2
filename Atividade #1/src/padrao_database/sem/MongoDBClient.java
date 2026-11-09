package padrao_database.sem;

public class MongoDBClient {

    private final String host;
    private final int porta;
    private final String database;

    public MongoDBClient(String host, int porta, String database) {
        this.host = host;
        this.porta = porta;
        this.database = database;
    }

    public void conectar(){
        System.out.println("Conexao direta ao MongoDB em: " + this.host + ":" + this.porta + "/" + database);
    }

    public void desconectar(){
        System.out.println("Desconectando do MongoDB...");
    }

    public void salvarDocumento(String colecao, String documento){
        System.out.println("MongoDB salvou: " + documento + " em "+ colecao );
    }

}
