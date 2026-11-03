import { conquistas } from '../../data/conquistas';
import CardConquista from '../CardConquista/CardConquista';
import TituloSecao from '../TituloSecao/TituloSecao';

export default function SecaoConquistas() {
 return (
    <section
        aria-label="Conquistas"
        className="
            mx-auto w-full max-w-[1300px]
            px-[1.6rem] pb-[5rem]

            tablet:px-[3.2rem] tablet:pb-[6rem]

            desktop:px-[6.4rem] desktop:pb-[8rem]
        "
    >
        <TituloSecao titulo="Novas conquistas" />

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
            Ainda não existe um sistema de conquistas na SoulUp, portanto vamos
            implementá-lo para que recompense os usuários por suas ações
            sustentáveis.
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
            {conquistas.map((conquista) => (
                <CardConquista
                    key={conquista.id}
                    conquista={conquista}
                />
            ))}
        </div>
    </section>
);

}
