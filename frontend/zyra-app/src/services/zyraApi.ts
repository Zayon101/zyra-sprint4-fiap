import type { CatalogoPassagens, ClimaZyra, ResumoZyra, UsuarioZyra } from '../types/zyra';

/** Em desenvolvimento o Vite encaminha /api ao Python; no build, ambos usam a mesma origem. */
export class ErroZyra extends Error {
  readonly status: number;

  constructor(mensagem: string, status = 0) {
    super(mensagem);
    this.name = 'ErroZyra';
    this.status = status;
  }
}

async function requisicao<T>(rota: string, metodo = 'GET', corpo?: object): Promise<T> {
  let resposta: Response;
  try {
    resposta = await fetch(`/api${rota}`, {
      method: metodo,
      headers: {
        'X-Zyra-Cliente': 'painel-web',
        ...(corpo ? { 'Content-Type': 'application/json' } : {}),
      },
      ...(corpo ? { body: JSON.stringify(corpo) } : {}),
    });
  } catch {
    throw new ErroZyra('Não foi possível alcançar o Python. Abra o Zyra pelo main.py e escolha [8] Abrir página web.');
  }

  const dados: unknown = await resposta.json().catch(() => null);
  if (!resposta.ok) {
    const mensagem = dados !== null && typeof dados === 'object' && 'erro' in dados
      && typeof dados.erro === 'string'
      ? dados.erro : `Falha na requisição (HTTP ${resposta.status}).`;
    throw new ErroZyra(mensagem, resposta.status);
  }
  if (dados === null) {
    throw new ErroZyra('O servidor retornou uma resposta inesperada.');
  }
  return dados as T;
}

export const zyraApi = {
  status: () => requisicao<{ status: string; servico: string; oracle: string }>('/status'),
  passagens: () => requisicao<CatalogoPassagens>('/passagens'),
  usuarios: async () => (await requisicao<{ usuarios: UsuarioZyra[] }>('/usuarios')).usuarios,
  usuario: async (id: number) => (await requisicao<{ usuario: UsuarioZyra }>(`/usuarios/${id}`)).usuario,
  resumo: () => requisicao<ResumoZyra>('/resumo'),
  criar: async (nome: string) => (await requisicao<{ usuario: UsuarioZyra }>('/usuarios', 'POST', { nome })).usuario,
  alterarNome: async (id: number, nome: string) => (await requisicao<{ usuario: UsuarioZyra }>(`/usuarios/${id}`, 'PATCH', { nome })).usuario,
  alterarSaldo: async (id: number, pontos: number) => (await requisicao<{ usuario: UsuarioZyra }>(`/usuarios/${id}`, 'PATCH', { pontos })).usuario,
  excluir: (id: number) => requisicao<{ excluido: boolean; id: number }>(`/usuarios/${id}`, 'DELETE'),
  adicionarPontos: async (id: number, quantidade: number) => (await requisicao<{ usuario: UsuarioZyra }>(`/usuarios/${id}/pontos`, 'POST', { quantidade })).usuario,
  resgatar: async (id: number, tipo: number) => (await requisicao<{ usuario: UsuarioZyra }>(`/usuarios/${id}/resgates`, 'POST', { tipo })).usuario,
  clima: () => requisicao<ClimaZyra>('/clima'),
};
