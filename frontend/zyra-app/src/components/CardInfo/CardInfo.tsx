import type { DetalheConversao } from '../../types/detalheConversao';

type CardInfoProps = {
    detalhe: DetalheConversao;
};

export default function CardInfo({ detalhe }: CardInfoProps) {
    return (
        <article className="card-shape flex min-w-[18rem] max-w-[26rem] flex-1 flex-col items-center gap-[1.2rem] bg-card-green p-[3.2rem_2.4rem] text-center shadow-[0_2px_12px_rgba(60,88,74,0.1)] transition-[transform,box-shadow] duration-200 hover:scale-105 hover:shadow-[0_8px_28px_rgba(60,88,74,0.2)]">
            <i className={`${detalhe.icone} text-[2.8rem] text-icon`} aria-hidden="true" />
            <p className="font-text text-[1.5rem] font-bold text-title">{detalhe.titulo}</p>
            <p className="font-title text-[2.2rem] font-black leading-[1.1] text-title">{detalhe.valor}</p>
            <p className="font-text text-[1.4rem] text-text-dark">{detalhe.desc}</p>
        </article>
    );
}
