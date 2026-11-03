import { Link } from 'react-router';
import type { Missao } from '../../types/missao';

type CardMissaoProps = {
    missao: Missao;
};

export default function CardMissao({ missao }: CardMissaoProps) {
    return (
        <Link
            to={`/missoes/${missao.id}`}
            aria-label={`Ver detalhes da missão ${missao.nome}`}
            className="card-shape flex min-w-[18rem] max-w-[26rem] flex-1 flex-col items-center gap-[1.2rem] bg-card-green p-[3.2rem_2.4rem] text-center shadow-[0_2px_12px_rgba(60,88,74,0.1)] transition-[transform,box-shadow] duration-200 hover:scale-[1.06] hover:shadow-[0_8px_28px_rgba(60,88,74,0.2)]"
        >
            <i className={`${missao.icone} flex items-center justify-center text-[3rem] text-icon`} aria-hidden="true" />
            <h3 className="font-text text-[1.5rem] font-bold text-title">{missao.nome}</h3>
            <p className="font-text text-[1.4rem] leading-[1.5] text-text-dark">{missao.desc}</p>
            <p className="font-text text-[1.4rem] font-bold text-hover">+{missao.pontos} pts</p>
        </Link>
    );
}
