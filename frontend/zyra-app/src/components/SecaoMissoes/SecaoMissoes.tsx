import { missoes } from '../../data/missoes';
import CardMissao from '../CardMissao/CardMissao';
import TituloSecao from '../TituloSecao/TituloSecao';

export default function SecaoMissoes() {
    return (
        <section
            aria-label="Missões adicionadas"
            className="
                mx-auto w-full max-w-[1300px]
                px-[1.6rem] pb-[5rem]

                tablet:px-[3.2rem] tablet:pb-[6rem]

                desktop:px-[6.4rem] desktop:pb-[8rem]
            "
        >
            <TituloSecao titulo="Missões adicionadas" />

            <p
                className="
                    mx-auto mb-[2.4rem]
                    w-full max-w-[70rem]
                    text-center
                    font-text
                    text-[1.5rem]
                    leading-[1.7]
                    text-text-dark

                    tablet:mb-[3.2rem]
                    tablet:text-[1.6rem]

                    desktop:text-body
                "
            >
                Na SoulUp já existem missões, porém queremos adicionar novas
                missões que incentivem o uso do transporte público.
            </p>

            <div
                className="
                    flex flex-col
                    items-center
                    justify-center
                    gap-[2rem]

                    tablet:gap-[2.4rem]

                    desktop:flex-row
                    desktop:flex-wrap
                    desktop:items-stretch
                    desktop:gap-[2.8rem]
                "
            >
                {missoes.map((missao) => (
                    <CardMissao key={missao.id} missao={missao} />
                ))}
            </div>
        </section>
    );
}
