import CalculadoraImpacto from '../CalculadoraImpacto/CalculadoraImpacto';
import TituloSecao from '../TituloSecao/TituloSecao';

export default function SecaoCalculadora() {
return (
    <section
        aria-label="Calculadora de impacto ambiental"
        className="
            mx-auto w-full max-w-[1300px]
            px-[1.6rem] pb-[5rem]

            tablet:px-[3.2rem] tablet:pb-[6rem]

            desktop:px-[6.4rem] desktop:pb-[8rem]
        "
    >
        <TituloSecao titulo="Calculadora de Impacto Ambiental" />

        <CalculadoraImpacto />
    </section>
);

}
