import HeroSobre from '../../components/HeroSobre/HeroSobre';
import SecaoAppPrint from '../../components/SecaoAppPrint/SecaoAppPrint';
import SecaoDetalhes from '../../components/SecaoDetalhes/SecaoDetalhes';
import SecaoPassos from '../../components/SecaoPassos/SecaoPassos';
import Separador from '../../components/Separador/Separador';

export default function Sobre() {
    return (
        <main>
            <HeroSobre />
            <Separador />
            <SecaoDetalhes />
            <Separador />
            <SecaoPassos />
            <Separador />
            <SecaoAppPrint />
        </main>
    );
}