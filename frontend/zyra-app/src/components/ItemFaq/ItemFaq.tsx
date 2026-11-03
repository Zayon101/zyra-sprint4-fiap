import type { Faq } from '../../types/faq';

type ItemFaqProps = {
    item: Faq;
    aberto: boolean;
    aoAlternar: (id: number) => void;
};

export default function ItemFaq({
    item,
    aberto,
    aoAlternar,
}: ItemFaqProps) {
    const idResposta = `faq-resposta-${item.id}`;

    return (
        <div
            className={`
                w-full
                overflow-hidden
                transition-[border-radius]
                duration-300

                ${
                    aberto
                        ? 'rounded-[1.6rem] tablet:rounded-[2rem]'
                        : 'rounded-[2.4rem] mobile-lg:rounded-[3rem] tablet:rounded-[4rem]'
                }
            `}
        >
            <button
                type="button"
                onClick={() => aoAlternar(item.id)}
                aria-expanded={aberto}
                aria-controls={idResposta}
                className={`
                    flex
                    w-full
                    items-center
                    justify-between
                    gap-[1.2rem]
                    px-[1.8rem]
                    py-[1.6rem]
                    text-left
                    font-text
                    text-[1.4rem]
                    font-semibold
                    leading-[1.5]
                    text-title
                    transition-colors
                    duration-200

                    mobile-lg:gap-[1.4rem]
                    mobile-lg:px-[2.2rem]
                    mobile-lg:py-[1.7rem]
                    mobile-lg:text-[1.5rem]

                    tablet:gap-[1.6rem]
                    tablet:px-[2.8rem]
                    tablet:py-[1.8rem]
                    tablet:text-[1.6rem]

                    ${
                        aberto
                            ? 'rounded-none bg-card-light-green'
                            : 'bg-card-green hover:bg-card-dark-green hover:text-text-light-yellow'
                    }
                `}
            >
                <span className="min-w-0">
                    {item.pergunta}
                </span>

                <span
                    aria-hidden="true"
                    className={`
                        flex
                        h-[2.8rem]
                        w-[2.8rem]
                        shrink-0
                        items-center
                        justify-center
                        rounded-full
                        text-[1.6rem]
                        font-light
                        leading-none
                        transition-colors
                        duration-200

                        mobile-lg:h-[3rem]
                        mobile-lg:w-[3rem]

                        tablet:h-[3.2rem]
                        tablet:w-[3.2rem]
                        tablet:text-[1.8rem]

                        ${
                            aberto
                                ? 'bg-card-dark-green text-text-light-yellow'
                                : 'bg-bg text-title'
                        }
                    `}
                >
                    {aberto ? 'x' : '+'}
                </span>
            </button>

            <div
                id={idResposta}
                role="region"
                className={`
                    overflow-hidden
                    bg-card-light-green
                    transition-[max-height,padding]
                    duration-[400ms]

                    ${
                        aberto
                            ? `
                                max-h-[50rem]
                                px-[1.8rem]
                                pt-[1.6rem]
                                pb-[2rem]

                                mobile-lg:px-[2.2rem]

                                tablet:px-[2.8rem]
                                tablet:pt-[2rem]
                                tablet:pb-[2.4rem]
                            `
                            : `
                                max-h-0
                                px-[1.8rem]
                                py-0

                                mobile-lg:px-[2.2rem]

                                tablet:px-[2.8rem]
                            `
                    }
                `}
            >
                <p
                    className="
                        font-text
                        text-[1.4rem]
                        leading-[1.7]
                        text-text-dark

                        mobile-lg:text-[1.45rem]

                        tablet:text-[1.5rem]
                    "
                >
                    {item.resposta}
                </p>
            </div>
        </div>
    );
}