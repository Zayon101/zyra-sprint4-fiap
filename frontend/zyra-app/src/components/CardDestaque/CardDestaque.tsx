import type { Destaque } from '../../types/destaque';

type CardDestaqueProps = {
    destaque: Destaque;
};

export default function CardDestaque({ destaque }: CardDestaqueProps) {
    return (
        <article
            className="
                flex
                w-full
                flex-col
                items-center
                gap-[1.6rem]
                rounded-[4rem_1rem_4rem_1rem]
                bg-card-green
                px-[2.4rem]
                py-[3.2rem]
                text-center
                shadow-[0_2px_12px_rgba(60,88,74,0.1)]
                transition-[transform,box-shadow]
                duration-200

                mobile-lg:px-[2.8rem]

                tablet:gap-[2rem]
                tablet:rounded-[5rem_1rem_5rem_1rem]
                tablet:pt-[3.6rem]
                tablet:pb-[3.2rem]

                desktop:rounded-[6rem_1rem_6rem_1rem]
                desktop:pt-[4rem]

                hover:scale-[1.03]
                hover:shadow-[0_8px_28px_rgba(60,88,74,0.2)]

                desktop:hover:scale-[1.06]
            "
        >
            <i
                className={`
                    ${destaque.icone}
                    flex
                    items-center
                    justify-center
                    text-[2.8rem]
                    text-icon

                    tablet:text-[3rem]
                `}
                aria-hidden="true"
            />

            <h3
                className="
                    text-[1.6rem]
                    font-semibold
                    text-title

                    tablet:text-[1.7rem]
                "
            >
                {destaque.titulo}
            </h3>

            <p
                className="
                    text-[1.4rem]
                    leading-[1.6]
                    text-title

                    tablet:text-[1.5rem]
                "
            >
                {destaque.texto}
            </p>
        </article>
    );
}