export default function HeroSobre() {
return (
    <section
        aria-label="Apresentação da funcionalidade"
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
            Como funciona a conversão de pontos?
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
            A Zyra conecta diretamente os pontos Soul ao sistema saldo de
            transporte público RecargaPay. Com poucos passos, você converte
            seu engajamento sustentável em um saldo válido para ser recarregado
            em seu bilhete único, permitindo que você viaje de forma prática
            e eficiente.
        </p>
    </section>
);
}
