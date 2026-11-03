import type { Missao } from '../types/missao';

export const missoes: Missao[] = [
    {
        id: 'foto-transporte',
        icone: 'fa-solid fa-camera',
        nome: 'Foto no transporte',
        desc: 'Tire uma foto ou faça um vídeo usando transporte público e registre no app.',
        pontos: 15,
    },
    {
        id: 'checkin-estacao',
        icone: 'fa-solid fa-location-dot',
        nome: 'Check-in na estação',
        desc: 'Faça check-in ao embarcar em uma estação de metrô ou trem via GPS.',
        pontos: 15,
    },
    {
        id: 'sequencia-semanal',
        icone: 'fa-solid fa-fire',
        nome: 'Sequência semanal',
        desc: 'Use transporte público por 5 dias consecutivos e ganhe bônus de sequência.',
        pontos: 100,
    },
];
