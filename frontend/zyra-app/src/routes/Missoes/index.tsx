import HeroMissoes from '../../components/HeroMissoes/HeroMissoes';
import SecaoAppPrint from '../../components/SecaoAppPrint/SecaoAppPrint';
import SecaoCalculadora from '../../components/SecaoCalculadora/SecaoCalculadora';
import SecaoConquistas from '../../components/SecaoConquistas/SecaoConquistas';
import SecaoMissoes from '../../components/SecaoMissoes/SecaoMissoes';
import Separador from '../../components/Separador/Separador';

export default function Missoes() {
    return (
        <main>
            <HeroMissoes />
            <Separador />
            <SecaoMissoes />
            <Separador />
            <SecaoConquistas />
            <Separador />
            <SecaoCalculadora />
            <Separador />
            <SecaoAppPrint
                ariaLabel="Imagem do aplicativo com as missões"
                titulo="As missões no aplicativo"
            />
        </main>
    );
}