/** Tipos da API HTTP local fornecida pelo backend Python. */
export interface Troca {
  id: number;
  data: string;
  passagem: string;
  viagens: number;
  custo: number;
  valor: number;
}

export interface UsuarioZyra {
  id: number;
  nome: string;
  pontos: number;
  historico: Troca[];
}

export interface ResumoZyra {
  total_usuarios: number;
  total_pontos: number;
  valor_total_saldo_reais: number;
  total_trocas: number;
  total_viagens: number;
  valor_total_resgatado_reais: number;
}

export interface PassagemZyra {
  tipo: number;
  nome: string;
  viagens: number;
  custo_pontos: number;
}

export interface CatalogoPassagens {
  pontos_por_passagem: number;
  valor_passagem_reais: number;
  passagens: PassagemZyra[];
}

export interface ClimaZyra {
  cidade: string;
  atual: {
    horario: string;
    temperatura: number;
    sensacao_termica: number | null;
    umidade: number | null;
    precipitacao: number;
    vento: number | null;
    descricao: string;
    codigo_tempo: number;
  };
  previsao: Array<{
    data: string;
    maxima: number;
    minima: number;
    probabilidade_chuva: number | null;
    precipitacao: number | null;
    descricao: string;
    codigo_tempo: number;
  }>;
}

export type TipoExportacao = 'usuarios' | 'usuario' | 'historico' | 'resumo';
