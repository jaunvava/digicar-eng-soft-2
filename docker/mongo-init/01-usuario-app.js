// Executado pelo container do MongoDB apenas na primeira inicializacao (volume vazio).
// Cria o usuario da aplicacao com acesso somente ao banco do DigiCar.
const banco = process.env.MONGO_DATABASE;

db.getSiblingDB(banco).createUser({
  user: process.env.MONGO_APP_USER,
  pwd: process.env.MONGO_APP_PASSWORD,
  roles: [{ role: "readWrite", db: banco }],
});
