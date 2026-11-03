import TituloSecao from '../TituloSecao/TituloSecao';

type SecaoAppPrintProps = {
    ariaLabel?: string;
    titulo?: string;
};

export default function SecaoAppPrint({
    ariaLabel = 'Imagem do aplicativo com a funcionalidade',
    titulo = 'A funcionalidade no aplicativo',
}: SecaoAppPrintProps) {
    return (
        <section
            aria-label={ariaLabel}
            className="
                mx-auto flex w-full max-w-[1300px]
                flex-col items-center
                px-[1.6rem] pb-[5rem] pt-[1.6rem]

                tablet:px-[3.2rem] tablet:pb-[6rem]

                desktop:px-[6.4rem] desktop:pb-[8rem]
            "
        >
            <TituloSecao titulo={titulo} />

            <img
                src="/img/pontos-app.png"
                alt="Imagem do aplicativo SoulUp com a funcionalidade Zyra"
                className="
                    w-full max-w-[32rem]
                    rounded-[2rem]
                    shadow-[0_8px_32px_rgba(60,88,74,0.2)]

                    mobile-lg:rounded-[2.5rem]

                    desktop:rounded-[3rem]
                "
            />
        </section>
    );
}
