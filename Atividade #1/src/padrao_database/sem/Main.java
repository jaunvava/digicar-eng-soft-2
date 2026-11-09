package padrao_database.sem;

public class Main {

    public static void main() {

        PostgresClient postgresClient = new PostgresClient("localhost", 5432, "users_db");
        MongoDBClient mongoDBClient = new MongoDBClient("localhost", 27017, "users_doc");

        UsuarioService usuarioService = new UsuarioService(postgresClient, mongoDBClient);

        usuarioService.cadastrarUsuario("Erlon");

    }

}
