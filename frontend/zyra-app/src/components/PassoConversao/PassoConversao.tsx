import type { PassoConversao as PassoConversaoType } from '../../types/passoConversao';

type PassoConversaoProps = {
    passo: PassoConversaoType;
    numero: number;
};

export default function PassoConversao({ passo, numero }: PassoConversaoProps) {
    const par = numero % 2 === 0;
    const destaque = Boolean(passo.destaque);

    const fundoLi = destaque ? 'bg-card-dark-green' : par ? 'bg-card-green' : 'bg-card-light-green';

    const fundoNum = destaque
        ? 'bg-hover text-white shadow-[0_0_0_3px_#9a4a6140]'
        : par
          ? 'bg-card-light-yellow text-card-dark-green'
          : 'bg-card-dark-green text-text-light-yellow';

    const fundoIcone = destaque ? 'bg-hover' : par ? 'bg-card-dark-green/15' : 'bg-card-dark-green';
    const corIcone = destaque ? 'text-white' : par ? 'text-card-dark-green' : 'text-text-light-yellow';

    const corNome = destaque ? 'text-text-light-yellow' : 'text-title';
    const corDesc = destaque ? 'text-card-green' : 'text-text-dark';

    return (
        <li
            className={`flex items-center gap-[2.4rem] p-[2rem_3.2rem] transition-colors duration-200 hover:brightness-[1.04] ${fundoLi}`}
        >
            <span
                className={`z-[1] flex h-[3.8rem] w-[3.8rem] shrink-0 items-center justify-center rounded-full font-text text-[1.6rem] font-bold shadow-[0_2px_8px_rgba(0,0,0,0.15)] ${fundoNum}`}
            >
                {numero}
            </span>

            {passo.imagem ? (
                <img
                    src={passo.imagem}
                    alt={`Ícone de ${passo.nome}`}
                    className="h-[5.6rem] w-[5.6rem] shrink-0 rounded-[1.2rem] object-cover"
                />
            ) : (
                <div
                    className={`flex h-[5.6rem] w-[5.6rem] shrink-0 items-center justify-center rounded-[1.2rem] ${fundoIcone}`}
                >
                    <i className={`${passo.icone} text-[2.2rem] ${corIcone}`} aria-hidden="true" />
                </div>
            )}

            <div className="flex-1">
                <h3 className={`mb-[0.3rem] font-text text-[1.6rem] font-bold ${corNome}`}>{passo.nome}</h3>
                <p className={`font-text text-[1.3rem] leading-[1.5] ${corDesc}`}>{passo.desc}</p>
            </div>
        </li>
    );
}
