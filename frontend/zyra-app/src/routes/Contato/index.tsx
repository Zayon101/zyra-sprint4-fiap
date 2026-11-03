import CabecalhoPagina from '../../components/CabecalhoPagina/CabecalhoPagina';
import FormularioContato from '../../components/FormularioContato/FormularioContato';

export default function Contato() {
    return (
        <main>
            <section aria-label="Fale conosco" className="mx-auto max-w-[1300px] p-[3.2rem_1.6rem_5.2rem] mobile-lg:p-[4.8rem_2.4rem_6.4rem] tablet:p-[5.6rem_4rem_7.2rem] desktop:p-[6.4rem_6.4rem_8rem]">
                <CabecalhoPagina
                    titulo="Contato:"
                    descricao="Entre em contato conosco preenchendo o formulário abaixo:"
                />
                <FormularioContato />
            </section>
        </main>
    );
}
