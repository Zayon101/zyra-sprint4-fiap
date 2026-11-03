import { passosConversao } from '../../data/passosConversao';
import PassoConversao from '../PassoConversao/PassoConversao';

export default function ComoFazer() {
    return (
        <div className="card-shape-alt mx-auto max-w-[70rem] overflow-hidden bg-card-dark-green shadow-[0_4px_24px_rgba(60,88,74,0.18)]">
            <div className="flex items-center gap-[1rem] border-b border-white/10 p-[2rem_3.2rem]">
                <p className="font-text text-[1.8rem] font-bold text-text-light-yellow">Como fazer?</p>
            </div>

            <ul className="relative">
                {passosConversao.map((passo, indice) => (
                    <PassoConversao key={passo.id} passo={passo} numero={indice + 1} />
                ))}
            </ul>
        </div>
    );
}
