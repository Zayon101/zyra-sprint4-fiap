import { useNavigate, useParams } from 'react-router';
import { missoes } from '../../data/missoes';
import BotaoPrimario from '../../components/BotaoPrimario/BotaoPrimario';

export default function MissaoDetalhe() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();

    const missao = missoes.find((item) => item.id === id);

    if (!missao) {
        return (
            <main>
                <section
                    aria-label="Missão não encontrada"
                    className="
                        mx-auto flex w-full max-w-[1300px] flex-col items-center gap-[2rem]
                        px-[1.6rem] py-[6rem] text-center

                        tablet:px-[3.2rem] tablet:py-[7.2rem]

                        desktop:px-[6.4rem] desktop:py-[8.8rem]
                    "
                >
                    <h1 className="font-title text-[2.4rem] font-black leading-[1.2] text-title tablet:text-subtitle">
                        Missão não encontrada
                    </h1>
                    <p className="mx-auto max-w-[50rem] font-text text-[1.5rem] leading-[1.7] text-text-dark tablet:text-body">
                        A missão que você tentou acessar não existe ou foi removida.
                    </p>
                    <BotaoPrimario to="/missoes">Voltar para missões</BotaoPrimario>
                </section>
            </main>
        );
    }

    return (
        <main>
            <section
                aria-label={`Detalhes da missão ${missao.nome}`}
                className="
                    mx-auto flex w-full max-w-[80rem] flex-col items-center gap-[2rem]
                    px-[1.6rem] py-[6rem] text-center

                    tablet:px-[3.2rem] tablet:py-[7.2rem]

                    desktop:px-[6.4rem] desktop:py-[8.8rem]
                "
            >
                <button
                    type="button"
                    onClick={() => navigate(-1)}
                    className="self-start font-text text-[1.4rem] font-semibold text-nav underline-offset-4 transition-colors duration-200 hover:text-hover hover:underline"
                >
                    ← Voltar
                </button>

                <i className={`${missao.icone} text-[4.8rem] text-icon`} aria-hidden="true" />

                <h1 className="font-title text-[2.6rem] font-black leading-[1.2] text-title tablet:text-subtitle">
                    {missao.nome}
                </h1>

                <p className="mx-auto max-w-[60rem] font-text text-[1.5rem] leading-[1.7] text-text-dark tablet:text-body">
                    {missao.desc}
                </p>

                <p className="font-text text-[1.8rem] font-bold text-hover">
                    +{missao.pontos} pts ao completar essa missão
                </p>

                <BotaoPrimario to="/missoes">Ver todas as missões</BotaoPrimario>
            </section>
        </main>
    );
}
