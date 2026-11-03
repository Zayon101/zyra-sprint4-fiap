/** Exemplo de cliente para o Zyra React/Vite; não está conectado ao site existente.
 * Inicie servidor_web.py e execute o React em localhost:5173.
 * NÃO utilize este servidor sem autenticação em produção.
 */
const BASE = "http://127.0.0.1:8765/api";

export type Troca = {
  id: number;
  data: string;
  passagem: string;
  viagens: number;
  custo: number;
  valor: number;
};

export type Usuario = {
  id: number;
  nome: string;
  pontos: number;
  historico: Troca[];
};

export type ResumoZyra = {
  total_usuarios: number;
  total_pontos: number;
  valor_total_saldo_reais: number;
  total_trocas: number;
  total_viagens: number;
  valor_total_resgatado_reais: number;
};

async function requisitar<T>(rota: string, metodo = "GET", dados?: unknown): Promise<T> {
  const resposta = await fetch(BASE + rota, {
    method: metodo,
    headers: {
      Accept: "application/json",
      ...(metodo === "GET" ? {} : { "X-Zyra-Cliente": "painel-web" }),
      ...(dados === undefined ? {} : { "Content-Type": "application/json" }),
    },
    ...(dados === undefined ? {} : { body: JSON.stringify(dados) }),
  });
  const corpo: unknown = await resposta.json();
  if (!resposta.ok) {
    const erro = corpo as { erro?: string };
    throw new Error(erro.erro ?? `Erro HTTP ${resposta.status}`);
  }
  return corpo as T;
}

export const zyraApi = {
  listarUsuarios: () => requisitar<{ usuarios: Usuario[] }>("/usuarios"),
  buscarUsuario: (id: number) => requisitar<{ usuario: Usuario }>(`/usuarios/${id}`),
  criarUsuario: (nome: string) => requisitar<{ usuario: Usuario }>("/usuarios", "POST", { nome }),
  alterarNome: (id: number, nome: string) => requisitar<{ usuario: Usuario }>(`/usuarios/${id}`, "PATCH", { nome }),
  alterarSaldo: (id: number, pontos: number) => requisitar<{ usuario: Usuario }>(`/usuarios/${id}`, "PATCH", { pontos }),
  adicionarPontos: (id: number, quantidade: number) => requisitar<{ usuario: Usuario }>(`/usuarios/${id}/pontos`, "POST", { quantidade }),
  resgatarPassagem: (id: number, tipo: 1 | 2 | 3) => requisitar<{ usuario: Usuario }>(`/usuarios/${id}/resgates`, "POST", { tipo }),
  excluirUsuario: (id: number) => requisitar<{ excluido: boolean }>(`/usuarios/${id}`, "DELETE"),
  resumo: () => requisitar<ResumoZyra>("/resumo"),
  passagens: () => requisitar("/passagens"),
  clima: () => requisitar("/clima"),
};
