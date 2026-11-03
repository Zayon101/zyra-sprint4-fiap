export default function HeroMissoes() {
    return (
        <section
            aria-label="Apresentação das missões e conquistas"
            className="
            mx-auto w-full max-w-[1300px]
            px-[1.6rem] py-[4rem]

            tablet:px-[3.2rem] tablet:py-[5rem]

            desktop:px-[6.4rem] desktop:py-[7.2rem]
        "
        >
            <h1
                className="
                mb-[1.6rem]
                font-title
                text-[2.8rem]
                font-black
                leading-[1.2]
                text-title

                tablet:text-[3.6rem]

                desktop:text-hero
            "
            >
                Missões e conquistas
            </h1>

            <p
                className="
                w-full max-w-[70rem]
                font-text
                text-[1.5rem]
                leading-[1.7]
                text-text-dark

                tablet:text-[1.6rem]

                desktop:text-body
            "
            >
                Para incentivar o uso do transporte público e aumentar o
                engajamento na plataforma, a Zyra adiciona novas missões e
                conquistas na SoulUp. Onde cada ação sustentável vira pontos Soul,
                e pontos Soul viram passagens de metrô. Também será implementada
                uma calculadora que compara o impacto ambiental de cada viagem
                entre transporte público e carro.
            </p>
        </section>
    );
}
