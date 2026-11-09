package padrao_database.sem;

public class UsuarioService {

    private final PostgresClient postgresClient;
    private final MongoDBClient mongoDBClient;

    public UsuarioService(PostgresClient postgresClient, MongoDBClient mongoDBClient) {
        this.postgresClient = postgresClient;
        this.mongoDBClient = mongoDBClient;
    }

    public void cadastrarUsuario(String nome) {

        System.out.println("Conectando aos Bancos de Dados...");

        postgresClient.conectar();
        try {
            postgresClient.inserirUsuario(nome);
        } finally {
            postgresClient.desconectar();
        }

        mongoDBClient.conectar();
        try {
            mongoDBClient.salvarDocumento("documentos-pessoais", "cpf.pdf");
        } finally {
            mongoDBClient.desconectar();
        }

    }



}
