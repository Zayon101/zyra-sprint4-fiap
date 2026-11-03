import type { PassoConversao } from '../types/passoConversao';

export const passosConversao: PassoConversao[] = [
    {
        id: 'soul-up',
        nome: 'Soul Up',
        desc: 'Cadastre-se na SoulUp.',
        imagem: '/img/icon-soulup.png',
    },
    {
        id: 'pontos-soul',
        nome: 'Pontos Soul',
        desc: 'Acumule pontos Soul cumprindo missões, conquistas, convidando amigos e muito mais.',
        icone: 'fa-solid fa-coins',
    },
    {
        id: 'comprar-saldo',
        nome: 'Comprar Saldo',
        desc: 'Use a funcionalidade Zyra para converter seus pontos em saldo para transporte público com RecargaPay.',
        icone: 'fa-solid fa-mobile-screen-button',
        destaque: true,
    },
    {
        id: 'recarga-pay',
        nome: 'RecargaPay',
        desc: 'No aplicativo RecargaPay, você pode consultar seu saldo para utilizar em transporte público com seu bilhete único.',
        icone: 'fa-regular fa-credit-card',
    },
    {
        id: 'viagem',
        nome: 'Viagem',
        desc: 'Apresente seu bilhete único na catraca e viaje com tranquilidade por metrôs, trens e ônibus municipais e muito mais.',
        icone: 'fa-solid fa-train-subway',
    },
];
