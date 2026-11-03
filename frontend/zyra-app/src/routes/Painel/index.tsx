import { useEffect, useState } from 'react';
import type { FormEvent, ReactNode } from 'react';
import CabecalhoPagina from '../../components/CabecalhoPagina/CabecalhoPagina';
import { zyraApi } from '../../services/zyraApi';
import type {
  CatalogoPassagens, ClimaZyra, ResumoZyra,
  TipoExportacao, UsuarioZyra,
} from '../../types/zyra';

type Secao = 'resumo' | 'usuarios' | 'passagens' | 'historico' | 'exportacao' | 'clima' | 'conexao';

const NAVEGACAO: Array<{ id: Secao; rotulo: string; icone: string; detalhe: string }> = [
  { id: 'resumo', rotulo: 'Visão geral', icone: 'fa-chart-pie', detalhe: 'Indicadores do sistema' },
  { id: 'usuarios', rotulo: 'Usuários', icone: 'fa-users', detalhe: 'Cadastrar e gerenciar' },
  { id: 'passagens', rotulo: 'Pontos e passagens', icone: 'fa-ticket', detalhe: 'Crédito e resgates' },
  { id: 'historico', rotulo: 'Histórico', icone: 'fa-clock-rotate-left', detalhe: 'Viagens resgatadas' },
  { id: 'exportacao', rotulo: 'Exportar JSON', icone: 'fa-file-export', detalhe: 'Relatórios e dados' },
  { id: 'clima', rotulo: 'Condições da viagem', icone: 'fa-cloud-sun', detalhe: 'Previsão do tempo' },
  { id: 'conexao', rotulo: 'Conexão SQL', icone: 'fa-database', detalhe: 'Estado do Oracle' },
];

const ESTILO_INPUT = 'w-full rounded-[1rem] border border-separator-light bg-white px-[1.4rem] py-[1.1rem] text-[1.5rem] text-text-dark outline-none transition focus:border-nav focus:ring-2 focus:ring-card-green';
const ESTILO_PRIMARIO = 'inline-flex min-h-[4.4rem] items-center justify-center gap-[0.9rem] rounded-[1.1rem] bg-nav px-[2rem] py-[1.1rem] text-[1.4rem] font-bold text-white transition hover:bg-card-dark-green focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-nav disabled:cursor-not-allowed disabled:opacity-50';
const ESTILO_SECUNDARIO = 'inline-flex min-h-[4.4rem] items-center justify-center gap-[0.9rem] rounded-[1.1rem] border border-nav px-[1.8rem] py-[1.1rem] text-[1.4rem] font-bold text-nav transition hover:bg-card-light-green disabled:cursor-not-allowed disabled:opacity-50';

const formatarReais = (valor: number) => new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor);
const formatarNumero = (valor: number) => new Intl.NumberFormat('pt-BR').format(valor);
const mensagemErro = (erro: unknown) => erro instanceof Error ? erro.message : 'Ocorreu um erro inesperado.';
const formatarData = (data: string) => {
  const valor = new Date(data);
  return Number.isNaN(valor.getTime()) ? data : valor.toLocaleString('pt-BR');
};
function inteiroValido(valor: string, minimo: number, maximo = 999_999_999_999): number {
  if (!/^\d+$/.test(valor.trim())) throw new Error('Informe um número inteiro válido.');
  const numero = Number(valor);
  if (!Number.isSafeInteger(numero) || numero < minimo || numero > maximo) {
    throw new Error(`Informe um valor inteiro entre ${formatarNumero(minimo)} e ${formatarNumero(maximo)}.`);
  }
  return numero;
}

function Bloco({ titulo, descricao, children, extra }: { titulo: string; descricao?: string; children: ReactNode; extra?: ReactNode }) {
  return (
    <section className="rounded-[2.4rem_0.9rem_2.4rem_0.9rem] border border-separator-light/65 bg-white px-[2rem] py-[2.4rem] shadow-[0_4px_24px_rgba(60,88,74,0.07)] mobile-lg:px-[2.8rem] tablet:p-[3rem]">
      <div className="mb-[2rem] flex flex-wrap items-start justify-between gap-[1.2rem]">
        <div><h3 className="font-title text-[2rem] font-bold text-title">{titulo}</h3>{descricao && <p className="mt-[0.5rem] text-[1.4rem] text-text-dark">{descricao}</p>}</div>
        {extra}
      </div>
      {children}
    </section>
  );
}

function Campo({ rotulo, children }: { rotulo: string; children: ReactNode }) {
  return <label className="flex flex-col gap-[0.7rem] text-[1.4rem] font-bold text-text-dark">{rotulo}{children}</label>;
}

function Vazio({ titulo, descricao }: { titulo: string; descricao: string }) {
  return <div className="rounded-[1.5rem] border border-dashed border-separator-light bg-card-light-yellow px-[2.4rem] py-[3rem] text-center"><p className="font-bold text-title">{titulo}</p><p className="mt-[0.5rem] text-[1.4rem]">{descricao}</p></div>;
}

function Indicador({ rotulo, valor, icone }: { rotulo: string; valor: string; icone: string }) {
  return <div className="rounded-[2.2rem_0.7rem_2.2rem_0.7rem] bg-card-light-green px-[2rem] py-[2.2rem]">
    <div className="mb-[1.2rem] flex items-center justify-between text-nav"><span className="text-[1.3rem] font-bold">{rotulo}</span><i className={`fa-solid ${icone} text-[1.9rem]`} aria-hidden="true" /></div>
    <p className="break-words font-title text-[2.5rem] font-bold text-title">{valor}</p>
  </div>;
}

export default function Painel() {
  const [secao, setSecao] = useState<Secao>('resumo');
  const [usuarios, setUsuarios] = useState<UsuarioZyra[]>([]);
  const [resumo, setResumo] = useState<ResumoZyra | null>(null);
  const [catalogo, setCatalogo] = useState<CatalogoPassagens | null>(null);
  const [clima, setClima] = useState<ClimaZyra | null>(null);
  const [oracle, setOracle] = useState<'conectado' | 'indisponivel' | 'desconhecido'>('desconhecido');
  const [idUsuario, setIdUsuario] = useState('');
  const [nomeCadastro, setNomeCadastro] = useState('');
  const [nomeAlterado, setNomeAlterado] = useState('');
  const [saldoAlterado, setSaldoAlterado] = useState('');
  const [quantidade, setQuantidade] = useState('100');
  const [tipoPassagem, setTipoPassagem] = useState('1');
  const [busca, setBusca] = useState('');
  const [tipoExportacao, setTipoExportacao] = useState<TipoExportacao>('usuarios');
  const [idExportacao, setIdExportacao] = useState('');
  const [erro, setErro] = useState('');
  const [sucesso, setSucesso] = useState('');
  const [ocupado, setOcupado] = useState(false);
  const [carregando, setCarregando] = useState(true);
  const [carregandoClima, setCarregandoClima] = useState(false);

  const selecionado = usuarios.find((usuario) => String(usuario.id) === idUsuario);
  const usuariosFiltrados = usuarios.filter((usuario) =>
    usuario.nome.toLocaleLowerCase('pt-BR').includes(busca.toLocaleLowerCase('pt-BR')) || String(usuario.id).includes(busca),
  );

  async function atualizarDados(): Promise<void> {
    const [lista, indicadores] = await Promise.all([zyraApi.usuarios(), zyraApi.resumo()]);
    setUsuarios(lista);
    setResumo(indicadores);
    setIdUsuario((anterior) => lista.some((usuario) => String(usuario.id) === anterior) ? anterior : String(lista[0]?.id ?? ''));
  }

  async function atualizarStatus(): Promise<void> {
    try {
      const estado = await zyraApi.status();
      setOracle(estado.oracle === 'conectado' ? 'conectado' : 'indisponivel');
    } catch {
      setOracle('desconhecido');
    }
  }

  useEffect(() => {
    let ativo = true;
    async function iniciar() {
      const [estado, passagens, dados] = await Promise.allSettled([
        zyraApi.status(), zyraApi.passagens(), Promise.all([zyraApi.usuarios(), zyraApi.resumo()]),
      ]);
      if (!ativo) return;
      if (estado.status === 'fulfilled') setOracle(estado.value.oracle === 'conectado' ? 'conectado' : 'indisponivel');
      if (passagens.status === 'fulfilled') setCatalogo(passagens.value);
      if (dados.status === 'fulfilled') {
        setUsuarios(dados.value[0]);
        setResumo(dados.value[1]);
        setIdUsuario(String(dados.value[0][0]?.id ?? ''));
      } else setErro(mensagemErro(dados.reason));
      setCarregando(false);
    }
    void iniciar();
    return () => { ativo = false; };
  }, []);

  function navegar(destino: Secao) {
    setSecao(destino);
    setErro('');
    setSucesso('');
    if (destino === 'clima' && !clima) void buscarClima();
    if (destino === 'conexao') void atualizarStatus();
  }

  async function executar(mensagem: string, acao: () => Promise<unknown>): Promise<void> {
    setOcupado(true);
    setErro('');
    setSucesso('');
    try {
      await acao();
      await atualizarDados();
      setSucesso(mensagem);
    } catch (falha) { setErro(mensagemErro(falha)); }
    finally { setOcupado(false); }
  }

  async function buscarClima(): Promise<void> {
    setCarregandoClima(true);
    setErro('');
    try { setClima(await zyraApi.clima()); }
    catch (falha) { setErro(mensagemErro(falha)); }
    finally { setCarregandoClima(false); }
  }

  function cadastro(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (nomeCadastro.trim().length < 3) { setErro('O nome deve ter pelo menos 3 caracteres.'); return; }
    void executar('Usuário cadastrado com bônus inicial de 500 pontos.', async () => {
      const criado = await zyraApi.criar(nomeCadastro.trim());
      setNomeCadastro('');
      setIdUsuario(String(criado.id));
    });
  }

  function alterarNome(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (!selecionado) return;
    const id = selecionado.id;
    void executar('Nome atualizado com sucesso.', async () => { await zyraApi.alterarNome(id, nomeAlterado.trim()); setNomeAlterado(''); });
  }

  function alterarSaldo(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (!selecionado) return;
    try {
      const pontos = inteiroValido(saldoAlterado, 0);
      const id = selecionado.id;
      void executar('Saldo atualizado com sucesso.', async () => { await zyraApi.alterarSaldo(id, pontos); setSaldoAlterado(''); });
    } catch (falha) { setErro(mensagemErro(falha)); }
  }

  function adicionarPontos(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (!selecionado) return;
    try {
      const pontos = inteiroValido(quantidade, 1);
      void executar(`${formatarNumero(pontos)} pontos adicionados com sucesso.`, () => zyraApi.adicionarPontos(selecionado.id, pontos));
    } catch (falha) { setErro(mensagemErro(falha)); }
  }

  function resgatar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (!selecionado) return;
    const passagem = catalogo?.passagens.find((item) => String(item.tipo) === tipoPassagem);
    if (!passagem) { setErro('Escolha uma passagem válida.'); return; }
    if (!window.confirm(`Resgatar ${passagem.nome} por ${formatarNumero(passagem.custo_pontos)} pontos para ${selecionado.nome}?`)) return;
    void executar('Passagem resgatada e registrada no histórico.', () => zyraApi.resgatar(selecionado.id, passagem.tipo));
  }

  function excluir(id: number, nome: string) {
    if (!window.confirm(`Excluir permanentemente ${nome} (ID ${id}) e todo o histórico de trocas?`)) return;
    void executar(`Cadastro de ${nome} excluído.`, () => zyraApi.excluir(id));
  }

  async function exportar(evento: FormEvent<HTMLFormElement>): Promise<void> {
    evento.preventDefault();
    setOcupado(true);
    setErro(''); setSucesso('');
    try {
      let documento: Record<string, unknown>;
      let referencia = '';
      if (tipoExportacao === 'usuarios') {
        const lista = await zyraApi.usuarios();
        documento = { tipo: 'usuarios', total: lista.length, usuarios: lista };
      } else if (tipoExportacao === 'resumo') {
        documento = { tipo: 'resumo', resumo: await zyraApi.resumo() };
      } else {
        const id = inteiroValido(idExportacao || idUsuario, 1);
        const usuario = await zyraApi.usuario(id);
        referencia = `_${id}`;
        documento = tipoExportacao === 'usuario'
          ? { tipo: 'usuario', usuario }
          : { tipo: 'historico', usuario: { id: usuario.id, nome: usuario.nome }, total_trocas: usuario.historico.length, trocas: usuario.historico };
      }
      documento.exportado_em = new Date().toISOString();
      const arquivo = new Blob([JSON.stringify(documento, null, 4) + '\n'], { type: 'application/json;charset=utf-8' });
      const url = URL.createObjectURL(arquivo);
      const link = document.createElement('a');
      link.href = url;
      link.download = `zyra_${tipoExportacao}${referencia}_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setSucesso('Consulta exportada para JSON com sucesso.');
    } catch (falha) { setErro(mensagemErro(falha)); }
    finally { setOcupado(false); }
  }

  const opcoesUsuarios = usuarios.map((usuario) => <option value={usuario.id} key={usuario.id}>{`#${usuario.id} — ${usuario.nome}`}</option>);
  const seletorUsuario = (
    <Campo rotulo="Usuário selecionado">
      <select className={ESTILO_INPUT} value={idUsuario} onChange={(evento) => { setIdUsuario(evento.target.value); setErro(''); setSucesso(''); }} disabled={!usuarios.length || ocupado}>
        {!usuarios.length && <option value="">Nenhum usuário cadastrado</option>}
        {opcoesUsuarios}
      </select>
    </Campo>
  );

  return (
    <main className="min-h-[70vh] pb-[8rem]">
      <div className="bg-card-light-green px-[1.6rem] pt-[4.8rem] pb-[4rem] tablet:pt-[6rem]">
        <CabecalhoPagina titulo="Painel Zyra" descricao="Gerencie seus usuários, pontos SoulUp e passagens em um só lugar." />
        <p className="mx-auto -mt-[2.5rem] max-w-[70rem] text-center text-[1.3rem] text-text-dark">Painel de demonstração da Sprint 4 · Dados sincronizados com o Python e Oracle</p>
      </div>

      <div className="mx-auto grid max-w-[138rem] gap-[2.6rem] px-[1.6rem] pt-[3.4rem] mobile-lg:px-[2.4rem] tablet:px-[4rem] desktop:grid-cols-[25rem_minmax(0,1fr)] desktop:gap-[3.5rem] desktop:px-[6rem]">
        <aside aria-label="Seções do painel" className="min-w-0">
          <nav className="flex gap-[0.8rem] overflow-x-auto pb-[1rem] desktop:sticky desktop:top-[11rem] desktop:flex-col desktop:overflow-visible">
            {NAVEGACAO.map(({ id, rotulo, icone, detalhe }) => (
              <button key={id} type="button" onClick={() => navegar(id)} aria-current={secao === id ? 'page' : undefined}
                className={`flex min-w-max items-center gap-[1.3rem] rounded-[1.3rem] px-[1.5rem] py-[1.3rem] text-left transition desktop:min-w-0 ${secao === id ? 'bg-nav text-white shadow-md' : 'bg-white text-nav hover:bg-card-light-green'}`}>
                <i className={`fa-solid ${icone} w-[2rem] text-center text-[1.7rem]`} aria-hidden="true" />
                <span><span className="block text-[1.4rem] font-bold">{rotulo}</span><span className={`hidden text-[1.2rem] desktop:block ${secao === id ? 'text-white/85' : 'text-text-dark'}`}>{detalhe}</span></span>
              </button>
            ))}
          </nav>
        </aside>

        <div className="min-w-0 space-y-[2.4rem]" aria-live="polite">
          <div className="flex flex-wrap items-center justify-between gap-[1.2rem] rounded-[1.5rem] bg-white px-[2rem] py-[1.5rem]">
            <div className="flex items-center gap-[0.9rem] text-[1.3rem] text-text-dark">
              <span className={`h-[0.9rem] w-[0.9rem] rounded-full ${oracle === 'conectado' ? 'bg-green-600' : 'bg-amber-500'}`} />
              Oracle: <strong>{oracle === 'conectado' ? 'conectado' : oracle === 'indisponivel' ? 'não preparado' : 'verificando'}</strong>
            </div>
            <button type="button" onClick={() => { void atualizarStatus(); void atualizarDados().then(() => setErro('')).catch((falha: unknown) => setErro(mensagemErro(falha))); }} disabled={ocupado} className="text-[1.3rem] font-bold text-nav underline underline-offset-4 hover:text-brand">Atualizar dados</button>
          </div>

          {erro && <div role="alert" className="rounded-[1.2rem] border border-red-300 bg-red-50 px-[2rem] py-[1.4rem] text-[1.4rem] text-red-800">{erro}</div>}
          {sucesso && <div role="status" className="rounded-[1.2rem] border border-green-300 bg-green-50 px-[2rem] py-[1.4rem] text-[1.4rem] text-green-900">{sucesso}</div>}
          {carregando && <p className="text-[1.4rem] text-text-dark">Carregando dados do Zyra...</p>}

          {secao === 'resumo' && <>
            <div className="grid gap-[1.4rem] mobile-lg:grid-cols-2 xl:grid-cols-3">
              <Indicador rotulo="Usuários cadastrados" valor={resumo ? formatarNumero(resumo.total_usuarios) : '—'} icone="fa-users" />
              <Indicador rotulo="Pontos em circulação" valor={resumo ? formatarNumero(resumo.total_pontos) : '—'} icone="fa-coins" />
              <Indicador rotulo="Trocas realizadas" valor={resumo ? formatarNumero(resumo.total_trocas) : '—'} icone="fa-ticket" />
              <Indicador rotulo="Viagens resgatadas" valor={resumo ? formatarNumero(resumo.total_viagens) : '—'} icone="fa-train-subway" />
              <Indicador rotulo="Saldo equivalente" valor={resumo ? formatarReais(resumo.valor_total_saldo_reais) : '—'} icone="fa-wallet" />
              <Indicador rotulo="Total resgatado" valor={resumo ? formatarReais(resumo.valor_total_resgatado_reais) : '—'} icone="fa-circle-check" />
            </div>
            <Bloco titulo="Como funciona o Zyra" descricao="Uma solução acadêmica para converter pontos SoulUp em passagens de transporte.">
              <div className="grid gap-[1.4rem] mobile-lg:grid-cols-3">
                <div className="rounded-[1.2rem] bg-card-light-yellow p-[1.8rem]"><p className="text-[1.3rem]">Bônus inicial</p><p className="font-title text-[2.2rem] font-bold text-brand">500 pontos</p></div>
                <div className="rounded-[1.2rem] bg-card-light-yellow p-[1.8rem]"><p className="text-[1.3rem]">Passagem unitária</p><p className="font-title text-[2.2rem] font-bold text-brand">587 pontos</p></div>
                <div className="rounded-[1.2rem] bg-card-light-yellow p-[1.8rem]"><p className="text-[1.3rem]">Valor simulado</p><p className="font-title text-[2.2rem] font-bold text-brand">R$ 5,40</p></div>
              </div>
              <p className="mt-[1.8rem] text-[1.3rem]">Os valores representam a simulação acadêmica do Zyra, não uma emissão oficial de bilhetes.</p>
            </Bloco>
          </>}

          {secao === 'usuarios' && <>
            <Bloco titulo="Cadastrar usuário" descricao="Novos usuários recebem automaticamente 500 pontos SoulUp.">
              <form onSubmit={cadastro} className="flex flex-col gap-[1.3rem] mobile-lg:flex-row mobile-lg:items-end">
                <div className="min-w-0 flex-1"><Campo rotulo="Nome completo"><input className={ESTILO_INPUT} type="text" required minLength={3} maxLength={120} value={nomeCadastro} onChange={(evento) => setNomeCadastro(evento.target.value)} placeholder="Digite o nome do usuário" /></Campo></div>
                <button type="submit" className={ESTILO_PRIMARIO} disabled={ocupado}><i className="fa-solid fa-user-plus" aria-hidden="true" /> Cadastrar</button>
              </form>
            </Bloco>
            <Bloco titulo="Usuários cadastrados" descricao="Consulte, selecione e exclua cadastros do Oracle." extra={<span className="rounded-full bg-card-light-green px-[1.4rem] py-[0.6rem] text-[1.3rem] font-bold text-nav">{usuarios.length} usuário(s)</span>}>
              <div className="mb-[1.8rem]"><Campo rotulo="Buscar por nome ou ID"><input className={ESTILO_INPUT} type="search" value={busca} onChange={(evento) => setBusca(evento.target.value)} placeholder="Buscar usuário..." /></Campo></div>
              {!usuariosFiltrados.length ? <Vazio titulo="Nenhum cadastro encontrado" descricao="Cadastre um usuário ou altere o termo da busca." /> :
              <div className="overflow-x-auto"><table className="w-full min-w-[48rem] text-left text-[1.4rem]">
                <thead><tr className="border-b border-separator-light text-nav"><th className="p-[1rem]">ID</th><th className="p-[1rem]">Nome</th><th className="p-[1rem]">Saldo</th><th className="p-[1rem]">Ações</th></tr></thead>
                <tbody>{usuariosFiltrados.map((usuario) => <tr key={usuario.id} className="border-b border-separator-light/60">
                  <td className="p-[1rem]">#{usuario.id}</td><td className="p-[1rem] font-bold">{usuario.nome}</td><td className="p-[1rem]">{formatarNumero(usuario.pontos)} pts</td>
                  <td className="whitespace-nowrap p-[1rem]"><button type="button" onClick={() => setIdUsuario(String(usuario.id))} className="mr-[1.3rem] font-bold text-nav underline underline-offset-4">Selecionar</button><button type="button" disabled={ocupado} onClick={() => excluir(usuario.id, usuario.nome)} className="font-bold text-brand underline underline-offset-4">Excluir</button></td>
                </tr>)}</tbody>
              </table></div>}
            </Bloco>
            <Bloco titulo="Alterar cadastro" descricao="Escolha um usuário para modificar o nome ou definir o saldo de pontos.">
              <div className="mb-[2rem]">{seletorUsuario}</div>
              {selecionado ? <div className="grid gap-[2rem] tablet:grid-cols-2">
                <form onSubmit={alterarNome} className="space-y-[1.2rem]"><Campo rotulo={`Novo nome de ${selecionado.nome}`}><input className={ESTILO_INPUT} value={nomeAlterado} onChange={(evento) => setNomeAlterado(evento.target.value)} minLength={3} maxLength={120} required placeholder={selecionado.nome} /></Campo><button className={ESTILO_SECUNDARIO} disabled={ocupado} type="submit">Salvar nome</button></form>
                <form onSubmit={alterarSaldo} className="space-y-[1.2rem]"><Campo rotulo={`Definir saldo (atual: ${formatarNumero(selecionado.pontos)})`}><input className={ESTILO_INPUT} type="number" min="0" max="999999999999" step="1" required value={saldoAlterado} onChange={(evento) => setSaldoAlterado(evento.target.value)} placeholder="Novo saldo de pontos" /></Campo><button className={ESTILO_SECUNDARIO} disabled={ocupado} type="submit">Salvar saldo</button></form>
              </div> : <Vazio titulo="Nenhum usuário selecionado" descricao="Cadastre alguém para alterar seus dados." />}
            </Bloco>
          </>}

          {secao === 'passagens' && <>
            <Bloco titulo="Gerenciar pontos e passagens" descricao="Créditos e resgates registrados no Oracle.">
              <div className="mb-[1.8rem]">{seletorUsuario}</div>
              {selecionado && <div className="rounded-[1.5rem] bg-card-light-green p-[2rem]"><p className="text-[1.3rem] font-bold text-nav">Saldo de {selecionado.nome}</p><p className="font-title text-[2.8rem] font-bold text-title">{formatarNumero(selecionado.pontos)} <span className="text-[1.5rem]">pontos</span></p></div>}
            </Bloco>
            <div className="grid gap-[2.4rem] xl:grid-cols-2">
              <Bloco titulo="Adicionar pontos"><form onSubmit={adicionarPontos} className="space-y-[1.7rem]"><Campo rotulo="Quantidade de pontos"><input className={ESTILO_INPUT} type="number" min="1" max="999999999999" step="1" required value={quantidade} onChange={(evento) => setQuantidade(evento.target.value)} /></Campo><button className={`${ESTILO_PRIMARIO} w-full`} disabled={!selecionado || ocupado} type="submit"><i className="fa-solid fa-plus" aria-hidden="true" /> Creditar pontos</button></form></Bloco>
              <Bloco titulo="Trocar por passagem"><form onSubmit={resgatar} className="space-y-[1.7rem]"><Campo rotulo="Tipo de passagem"><select value={tipoPassagem} className={ESTILO_INPUT} onChange={(evento) => setTipoPassagem(evento.target.value)}>{catalogo?.passagens.map((passagem) => <option key={passagem.tipo} value={passagem.tipo}>{passagem.nome} — {formatarNumero(passagem.custo_pontos)} pts</option>)}</select></Campo><button className={`${ESTILO_PRIMARIO} w-full`} disabled={!selecionado || ocupado || !catalogo} type="submit"><i className="fa-solid fa-ticket" aria-hidden="true" /> Resgatar passagem</button></form></Bloco>
            </div>
            <Bloco titulo="Passagens disponíveis" descricao="Tabela de conversão utilizada pelo sistema Python.">
              <div className="grid gap-[1.3rem] mobile-lg:grid-cols-3">{catalogo?.passagens.map((passagem) => <div key={passagem.tipo} className="rounded-[1.2rem] bg-card-light-yellow p-[1.7rem]"><p className="font-bold text-title">{passagem.nome}</p><p className="mt-[0.8rem] font-title text-[2rem] font-bold text-brand">{formatarNumero(passagem.custo_pontos)} pts</p><p className="text-[1.3rem]">{passagem.viagens} viagem(ns) · {formatarReais(passagem.viagens * (catalogo?.valor_passagem_reais ?? 0))}</p></div>)}</div>
            </Bloco>
          </>}

          {secao === 'historico' && <Bloco titulo="Histórico de trocas" descricao="Consulte as passagens resgatadas pelo usuário selecionado.">
            <div className="mb-[2rem]">{seletorUsuario}</div>
            {!selecionado?.historico.length ? <Vazio titulo="Nenhuma troca registrada" descricao="Os resgates aparecerão aqui após a primeira troca." /> : <div className="space-y-[1rem]">
              {selecionado.historico.map((troca) => <div key={troca.id} className="flex flex-wrap items-center justify-between gap-[1rem] rounded-[1.2rem] bg-card-light-green p-[1.6rem]"><div><p className="font-bold text-title">{troca.passagem}</p><p className="text-[1.3rem]">{formatarData(troca.data)} · {troca.viagens} viagem(ns) · ID #{troca.id}</p></div><div className="text-right"><p className="font-bold text-brand">−{formatarNumero(troca.custo)} pts</p><p className="text-[1.3rem]">{formatarReais(troca.valor)}</p></div></div>)}
            </div>}
          </Bloco>}

          {secao === 'exportacao' && <Bloco titulo="Exportação de consultas" descricao="Gere arquivos JSON a partir de consultas reais ao Oracle, sem alterar o banco.">
            <form onSubmit={(evento) => { void exportar(evento); }} className="space-y-[1.8rem]">
              <Campo rotulo="Dados que deseja exportar"><select className={ESTILO_INPUT} value={tipoExportacao} onChange={(evento) => setTipoExportacao(evento.target.value as TipoExportacao)}><option value="usuarios">Todos os usuários</option><option value="usuario">Usuário por ID</option><option value="historico">Histórico de um usuário</option><option value="resumo">Resumo geral</option></select></Campo>
              {(tipoExportacao === 'usuario' || tipoExportacao === 'historico') && <Campo rotulo="ID do usuário"><input className={ESTILO_INPUT} type="number" min="1" step="1" required placeholder="Digite o ID" value={idExportacao} onChange={(evento) => setIdExportacao(evento.target.value)} /></Campo>}
              <button className={ESTILO_PRIMARIO} type="submit" disabled={ocupado}><i className="fa-solid fa-file-arrow-down" aria-hidden="true" /> Exportar JSON</button>
            </form>
            <p className="mt-[2rem] text-[1.3rem]">O arquivo será baixado pelo navegador. O formato corresponde às exportações do menu do Python.</p>
          </Bloco>}

          {secao === 'clima' && <Bloco titulo="Condições para sua viagem" descricao="Dados meteorológicos públicos da Open-Meteo para São Paulo." extra={<button type="button" className={ESTILO_SECUNDARIO} disabled={carregandoClima} onClick={() => { void buscarClima(); }}>Atualizar</button>}>
            {carregandoClima && <p>Consultando previsão do tempo...</p>}
            {clima && <><div className="grid gap-[1.2rem] mobile-lg:grid-cols-2 tablet:grid-cols-4">
              <Indicador rotulo="Temperatura" valor={`${clima.atual.temperatura.toFixed(1)} °C`} icone="fa-temperature-half" />
              <Indicador rotulo="Sensação térmica" valor={clima.atual.sensacao_termica === null ? '—' : `${clima.atual.sensacao_termica.toFixed(1)} °C`} icone="fa-sun" />
              <Indicador rotulo="Umidade" valor={clima.atual.umidade === null ? '—' : `${clima.atual.umidade}%`} icone="fa-droplet" />
              <Indicador rotulo="Chuva atual" valor={`${clima.atual.precipitacao} mm`} icone="fa-cloud-rain" />
            </div><p className="my-[1.8rem] rounded-[1.2rem] bg-card-light-yellow p-[1.6rem] font-bold text-title">{clima.atual.descricao} · Vento: {clima.atual.vento ?? '—'} km/h</p><h4 className="mb-[1.2rem] font-title text-[1.8rem] font-bold">Previsão para os próximos dias</h4><div className="grid gap-[1.2rem] mobile-lg:grid-cols-3">{clima.previsao.map((dia) => <div key={dia.data} className="rounded-[1.2rem] bg-card-light-green p-[1.7rem]"><p className="font-bold text-title">{dia.data.split('-').reverse().join('/')}</p><p className="text-[1.3rem]">{dia.descricao}</p><p className="mt-[0.8rem] font-bold">{dia.minima.toFixed(0)}° / {dia.maxima.toFixed(0)}°</p><p className="text-[1.3rem]">Chance de chuva: {dia.probabilidade_chuva ?? '—'}%</p></div>)}</div></>}
            <p className="mt-[2rem] text-[1.2rem] text-text-dark">Fonte: Open-Meteo. Previsões sujeitas a atualização; a API do backend possui cache para evitar consultas excessivas.</p>
          </Bloco>}

          {secao === 'conexao' && <Bloco titulo="Conexão com o Oracle" descricao="Verifique se o servidor Python está pronto para consultar os dados.">
            <div className="mb-[2rem] rounded-[1.5rem] bg-card-light-green p-[2rem]"><p className="font-bold text-nav">Estado da conexão</p><p className="mt-[0.5rem] font-title text-[2.2rem] font-bold text-title">{oracle === 'conectado' ? 'Oracle preparado' : oracle === 'indisponivel' ? 'Oracle não preparado' : 'Servidor indisponível ou aguardando'}</p></div>
            <p className="mb-[1.5rem] text-[1.4rem]">A conexão SQL e a criação das tabelas são configuradas no terminal para não expor credenciais na interface web.</p>
            <ol className="list-decimal space-y-[0.8rem] pl-[2rem] text-[1.4rem]"><li>Execute <code className="rounded bg-card-light-yellow px-[0.6rem]">python main.py</code> na pasta do backend.</li><li>Escolha <strong>[7] Conectar SQL / preparar tabelas</strong> e informe as credenciais.</li><li>Verifique ou crie as tabelas e escolha <strong>[8] Abrir página web</strong>.</li><li>Volte ao painel e atualize o status.</li></ol>
            <button type="button" className={`${ESTILO_PRIMARIO} mt-[2rem]`} onClick={() => { void atualizarStatus(); }}>Verificar novamente</button>
          </Bloco>}
        </div>
      </div>
    </main>
  );
}
