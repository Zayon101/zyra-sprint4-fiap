import BotaoPrimario from '../BotaoPrimario/BotaoPrimario';

export default function HeroInicio() {
    return (
        <section
            aria-label="Apresentação do projeto"
            className="
                mx-auto
                flex
                w-full
                max-w-[1300px]
                flex-col
                items-center
                gap-[3.2rem]
                px-[2rem]
                py-[4rem]

                mobile-lg:px-[3.2rem]
                mobile-lg:py-[4.8rem]

                tablet:gap-[4rem]
                tablet:px-[4.8rem]
                tablet:py-[5.6rem]

                desktop:flex-row
                desktop:items-center
                desktop:justify-between
                desktop:gap-[4.8rem]
                desktop:px-[6.4rem]
                desktop:py-[7.2rem]
            "
        >
            <div
                className="
                    flex
                    w-full
                    flex-col
                    items-center
                    text-center

                    desktop:w-[55%]
                    desktop:items-start
                    desktop:text-left
                "
            >
                <h1
                    className="
                        font-title
                        text-[2.8rem]
                        font-black
                        leading-[1.2]
                        text-title

                        mobile-lg:text-[3.2rem]

                        tablet:text-[3.6rem]

                        desktop:text-hero
                    "
                >
                    Transforme seus pontos{' '}
                    <span className="mx-[0.4rem] inline-flex align-middle">
                        <a
                            href="https://soulup.io"
                            target="_blank"
                            rel="noopener noreferrer"
                        >
                            <img
                                src="/img/soulup.jpg"
                                alt="SoulUP"
                                className="
                                    h-[2.6rem]
                                    w-auto
                                    rounded-xl
                                    transition-transform
                                    duration-200

                                    mobile-lg:h-[2.9rem]

                                    tablet:h-[3.1rem]

                                    desktop:h-[3.3rem]

                                    hover:scale-105
                                "
                            />
                        </a>
                    </span>{' '}
                    em passagem de trens e metrô!
                </h1>

                <p
                    className="
                        mt-[1.8rem]
                        mb-[3rem]
                        max-w-[52rem]
                        font-text
                        text-[1.6rem]
                        leading-[1.7]
                        text-text-dark

                        tablet:text-[1.7rem]

                        desktop:mb-[3.6rem]
                        desktop:text-body
                    "
                >
                    Com Zyra você pode converter seus pontos para viajar de uma
                    forma sustentável e simples. Conheça mais sobre o projeto e
                    como contribuir para um meio ambiente melhor!
                </p>

                <BotaoPrimario
                    to="/sobre"
                    className="
                        w-full
                        max-w-[24rem]

                        mobile-lg:w-auto
                    "
                >
                    Ver como funciona
                </BotaoPrimario>
            </div>

            <img
                src="/img/trem.jpg"
                alt="Desenho de um trem"
                className="
                    w-full
                    max-w-[42rem]
                    rounded-[2rem]
                    object-cover

                    tablet:max-w-[48rem]

                    desktop:w-[40%]
                    desktop:max-w-none
                    desktop:rounded-[3rem]
                "
            />
        </section>
    );
}