CREATE TABLE IF NOT EXISTS cliente (
    id_cliente SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    telefone VARCHAR(15) NOT NULL
);

CREATE TABLE IF NOT EXISTS tipo_evento (
    id_tipo SERIAL PRIMARY KEY,
    designacao VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS administrador (
    id_admin SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS pedido (
    id_pedido SERIAL PRIMARY KEY,
    codigo_consulta VARCHAR(8) UNIQUE NOT NULL,
    data_sessao DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fim TIME NOT NULL,
    localizacao VARCHAR(200) NOT NULL,
    duracao  INT NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'pendente',
    observacoes TEXT,
    id_cliente INT NOT NULL REFERENCES cliente(id_cliente) ON DELETE CASCADE,
    id_tipo INT NOT NULL REFERENCES tipo_evento(id_tipo),
    CONSTRAINT chk_hora CHECK (hora_inicio < hora_fim)
);
