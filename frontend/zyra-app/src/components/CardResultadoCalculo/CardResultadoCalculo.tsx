type CardResultadoCalculoProps = {
    icone: string;
    label: string;
    valor: string | null;
    destaque?: boolean;
};

export default function CardResultadoCalculo({
    icone,
    label,
    valor,
    destaque = false,
}: CardResultadoCalculoProps) {
    const corTexto = destaque ? 'text-[#e8a0b4]' : 'text-card-green';
    const fundo = destaque
        ? 'border-[rgba(154,74,97,0.35)] bg-[rgba(154,74,97,0.2)]'
        : 'border-white/10 bg-[rgba(255,255,255,0.07)]';

    return (
        <div
            className={`flex min-w-[15rem] max-w-[22rem] flex-1 flex-col items-center gap-[0.8rem] rounded-[1.2rem_0.4rem_1.2rem_0.4rem] border p-[2rem_2.4rem] text-center ${fundo}`}
        >
            <i className={`${icone} text-[2.4rem] ${corTexto}`} aria-hidden="true" />
            <p className={`font-text text-[1.2rem] font-semibold uppercase tracking-[0.08em] ${corTexto}`}>
                {label}
            </p>
            <p className="font-title text-[2.8rem] font-black leading-none text-text-light-yellow">
                {valor ?? '—'}
            </p>
            <p className={`font-text text-[1.2rem] ${corTexto}`}>kg de CO₂</p>
        </div>
    );
}
