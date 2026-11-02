"use strict";

const $ = (id) => document.getElementById(id);
let usuarioSelecionado = null;
let catalogoPassagens = [];

function informar(texto, tipo = "") {
  $("mensagem").textContent = texto;
  $("mensagem").className = `mensagem ${tipo}`;
}

async function api(caminho, metodo = "GET", dados = undefined) {
  const opcoes = { method: metodo, headers: { Accept: "application/json" } };
  if (metodo !== "GET") {
    opcoes.headers["X-Zyra-Cliente"] = "painel-web";
    if (dados !== undefined) {
      opcoes.headers["Content-Type"] = "application/json";
      opcoes.body = JSON.stringify(dados);
    }
  }
  const resposta = await fetch(`/api${caminho}`, opcoes);
  const corpo = await resposta.json();
  if (!resposta.ok) throw new Error(corpo.erro || `HTTP ${resposta.status}`);
  return corpo;
}

function celula(linha, texto) {
  const td = document.createElement("td");
  td.textContent = String(texto);
  linha.append(td);
  return td;
}

function desenharUsuarios(usuarios) {
  const corpo = $("usuarios");
  corpo.replaceChildren();
  if (!usuarios.length) {
    const linha = document.createElement("tr");
    const td = celula(linha, "Nenhum usuário cadastrado.");
    td.colSpan = 5;
    corpo.append(linha);
    return;
  }
  for (const usuario of usuarios) {
    const linha = document.createElement("tr");
    celula(linha, usuario.id);
    celula(linha, usuario.nome);
    celula(linha, usuario.pontos.toLocaleString("pt-BR"));
    celula(linha, usuario.historico.length);
    const td = document.createElement("td");
    const botao = document.createElement("button");
    botao.className = "escolher";
    botao.type = "button";
    botao.textContent = "Selecionar";
    botao.addEventListener("click", () => selecionar(usuario.id));
    td.append(botao);
    linha.append(td);
    corpo.append(linha);
  }
}

function desenharSelecionado(usuario) {
  $("painel-usuario").hidden = false;
  $("usuario-atual").textContent = `#${usuario.id} — ${usuario.nome}`;
  $("novo-nome").value = usuario.nome;
  const lista = $("historico");
  lista.replaceChildren();
  if (!usuario.historico.length) {
    const item = document.createElement("li");
    item.textContent = "Nenhuma troca realizada.";
    lista.append(item);
  }
  for (const troca of usuario.historico) {
    const item = document.createElement("li");
    item.textContent = `${troca.passagem} • ${troca.custo} pontos • ${troca.data}`;
    lista.append(item);
  }
}

async function selecionar(id) {
  try {
    const { usuario } = await api(`/usuarios/${id}`);
    usuarioSelecionado = id;
    desenharSelecionado(usuario);
    informar(`Usuário ${usuario.nome} selecionado.`);
    $("painel-usuario").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (erro) { informar(erro.message, "erro"); }
}

async function carregar() {
  try {
    const [lista, resumo, passagens] = await Promise.all([
      api("/usuarios"), api("/resumo"), api("/passagens"),
    ]);
    desenharUsuarios(lista.usuarios);
    $("total-usuarios").textContent = resumo.total_usuarios.toLocaleString("pt-BR");
    $("total-pontos").textContent = resumo.total_pontos.toLocaleString("pt-BR");
    $("total-viagens").textContent = resumo.total_viagens.toLocaleString("pt-BR");
    if (!catalogoPassagens.length) {
      catalogoPassagens = passagens.passagens;
      const select = $("tipo-passagem");
      select.replaceChildren();
      for (const passagem of catalogoPassagens) {
        const opcao = document.createElement("option");
        opcao.value = String(passagem.tipo);
        opcao.textContent = `${passagem.nome} — ${passagem.custo_pontos} pontos`;
        select.append(opcao);
      }
    }
    if (usuarioSelecionado !== null) {
      const usuario = lista.usuarios.find((u) => u.id === usuarioSelecionado);
      if (usuario) desenharSelecionado(usuario);
      else { usuarioSelecionado = null; $("painel-usuario").hidden = true; }
    }
    informar("Dados atualizados diretamente do Oracle.", "sucesso");
  } catch (erro) { informar(erro.message, "erro"); }
}

async function clima() {
  try {
    const { cidade, atual, previsao } = await api("/clima");
    const box = $("clima");
    box.replaceChildren();
    const temperatura = document.createElement("strong");
    temperatura.textContent = `${atual.temperatura.toLocaleString("pt-BR")} °C`;
    const descricao = document.createElement("span");
    descricao.textContent = `${cidade}: ${atual.descricao}`;
    const futuro = document.createElement("small");
    futuro.textContent = `Previsão: ${previsao.length} dia(s) • chuva agora: ${atual.precipitacao} mm`;
    box.append(temperatura, descricao, futuro);
  } catch (erro) { $("clima").textContent = `Clima indisponível: ${erro.message}`; }
}

function acaoFormulario(id, callback) {
  $(id).addEventListener("submit", async (evento) => {
    evento.preventDefault();
    try { await callback(); await carregar(); informar("Operação salva no Oracle!", "sucesso"); }
    catch (erro) { informar(erro.message, "erro"); }
  });
}

$("atualizar").addEventListener("click", carregar);
acaoFormulario("cadastro", async () => {
  await api("/usuarios", "POST", { nome: $("nome").value.trim() });
  $("cadastro").reset();
});
acaoFormulario("alterar-nome", async () => {
  await api(`/usuarios/${usuarioSelecionado}`, "PATCH", { nome: $("novo-nome").value.trim() });
});
acaoFormulario("adicionar-pontos", async () => {
  await api(`/usuarios/${usuarioSelecionado}/pontos`, "POST", { quantidade: Number($("quantidade").value) });
  $("adicionar-pontos").reset();
});
acaoFormulario("resgatar", async () => {
  await api(`/usuarios/${usuarioSelecionado}/resgates`, "POST", { tipo: Number($("tipo-passagem").value) });
});
$("excluir").addEventListener("click", async () => {
  if (usuarioSelecionado === null || !confirm("Excluir o cadastro e todo o histórico deste usuário?")) return;
  try {
    await api(`/usuarios/${usuarioSelecionado}`, "DELETE");
    usuarioSelecionado = null;
    $("painel-usuario").hidden = true;
    await carregar();
    informar("Usuário excluído do Oracle.", "sucesso");
  } catch (erro) { informar(erro.message, "erro"); }
});

carregar();
clima();
