import { detalhesConversao } from '../../data/detalhesConversao';
import CardInfo from '../CardInfo/CardInfo';
import TituloSecao from '../TituloSecao/TituloSecao';

export default function SecaoDetalhes() {
return (
        <section
            aria-label="Informações sobre a conversão"
            className="
                mx-auto w-full max-w-[1300px]
                px-[1.6rem] pb-[5rem]

                tablet:px-[3.2rem] tablet:pb-[6rem]

                desktop:px-[6.4rem] desktop:pb-[8rem]
            "
        >
            <TituloSecao titulo="Detalhes da conversão" />

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
                {detalhesConversao.map((detalhe) => (
                    <CardInfo key={detalhe.id} detalhe={detalhe} />
                ))}
            </div>
        </section>
    );
}