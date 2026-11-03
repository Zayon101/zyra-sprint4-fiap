import type { Faq } from '../types/faq';

export const perguntasFrequentes: Faq[] = [
    {
        id: 1,
        pergunta: 'O que é a Soul Up?',
        resposta:
            'A SOUL é uma plataforma social inovadora onde cada interação gera Pontos Soul, sua moeda de impacto. Um ecossistema que combina fidelização, tecnologia blockchain dentro de um conceito de comunidades voltado para o impacto socioambiental positivo.',
    },
    {
        id: 2,
        pergunta: 'O que são os pontos Soul?',
        resposta:
            'Os Pontos Soul são um sistema de recompensas da Soul Up. Cada vez que você interage com a plataforma, como assistir anúncios ou realizar missões, você acumula pontos que podem ser convertidos em benefícios reais, como passagens de transporte público e Vale-Energia.',
    },
    {
        id: 3,
        pergunta: 'Quantos pontos preciso para uma passagem?',
        resposta:
            'São necessários 587 + 15% de pontos Soul para resgatar o valor de uma passagem completa, o equivalente a R$ 5,40. A taxa de conversão padrão é de 50 pontos para cada R$ 0,46. Mas cobramos uma taxa de 15% sobre o valor do resgate, que é convertida em pontos Soul, para cobrir custos operacionais e manter a sustentabilidade do programa.',
    },
    {
        id: 4,
        pergunta: 'Como funciona a conversão dos pontos em saldo de transporte?',
        resposta:
            'Ao converter seus Pontos Soul, o valor é creditado diretamente na sua conta de transporte por meio da RecargaPay, nossa parceira de recarga. Diferente de um bilhete com validade fixa, o saldo fica disponível na hora e é debitado automaticamente a cada viagem realizada.',
    },
    {
        id: 5,
        pergunta: 'O que é a RecargaPay e qual sua relação com a Zyra?',
        resposta:
            'A RecargaPay é a parceira que opera o sistema de saldo pré-pago já integrado à bilhetagem eletrônica de São Paulo. Ela garante que a recarga feita pelo aplicativo SoulUp seja processada de forma rápida e segura, sem que você precise lidar com outro sistema separado.',
    },
    {
        id: 6,
        pergunta: 'Quais missões e conquistas estão disponíveis na Zyra?',
        resposta:
            'Você pode ganhar pontos fazendo check-in de entrada e saída no transporte, tirando uma selfie durante o trajeto, mantendo uma sequência de dias utilizando transporte público, entre outras ações simples do dia a dia que incentivam o uso contínuo do transporte sustentável.',
    },
    {
        id: 7,
        pergunta: 'Como é calculado o CO₂ que eu evito ao usar transporte público?',
        resposta:
            'Cada viagem realizada é comparada com a emissão que o mesmo trajeto teria de carro solo, e a diferença é convertida em kg de CO₂ evitado. Esse valor fica acumulado no seu perfil e pode ser consultado e recompensado por conquistas.',
    },
];