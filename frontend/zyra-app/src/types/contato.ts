export type DadosContato = {
    nome: string;
    sobrenome: string;
    email: string;
    telefone: string;
    mensagem: string;
};

export type StatusEnvio = 'sucesso' | 'erro' | null;
