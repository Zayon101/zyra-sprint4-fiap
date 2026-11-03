import { integrantes } from '../../data/integrantes';
import CardMembro from '../../components/CardMembro/CardMembro';
import CabecalhoPagina from '../../components/CabecalhoPagina/CabecalhoPagina';

export default function Integrantes() {
    return (
        <main>
            <section aria-label="Integrantes da equipe" className="mx-auto max-w-[1300px] p-[2.4rem_1.6rem_5.2rem] tablet:p-[6.4rem_6.4rem_8rem]">
                <CabecalhoPagina titulo="Integrantes:" />

                <div className="flex flex-wrap items-stretch justify-center gap-[1.6rem] tablet:gap-[2.8rem]">
                    {integrantes.map((integrante) => (
                        <CardMembro key={integrante.id} integrante={integrante} />
                    ))}
                </div>
            </section>
        </main>
    );
}