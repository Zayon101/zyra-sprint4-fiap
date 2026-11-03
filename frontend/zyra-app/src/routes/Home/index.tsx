import HeroInicio from '../../components/HeroInicio/HeroInicio';
import SecaoDestaques from '../../components/SecaoDestaques/SecaoDestaques';
import Separador from '../../components/Separador/Separador';

export default function Home() {
    return (
        <main>
            <HeroInicio />
            <Separador />
            <SecaoDestaques />
        </main>
    );
}