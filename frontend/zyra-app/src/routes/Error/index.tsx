import { isRouteErrorResponse, useRouteError } from 'react-router';
import type { LinkNavegacao } from '../../types/navegacao';
import BotaoPrimario from '../../components/BotaoPrimario/BotaoPrimario';
import TituloErro from '../../components/TituloErro/TituloErro';
import LinksUteis from '../../components/LinksUteis/LinksUteis';

const LINKS_SUGERIDOS: LinkNavegacao[] = [
    { caminho: '/sobre', rotulo: 'Sobre' },
    { caminho: '/missoes', rotulo: 'Missões' },
    { caminho: '/faq', rotulo: 'FAQ' },
    { caminho: '/contato', rotulo: 'Contato' },
];

export default function Error() {
    const erro = useRouteError();
    const eNaoEncontrado = isRouteErrorResponse(erro) ? erro.status === 404 : true;

    const codigo = isRouteErrorResponse(erro) ? String(erro.status) : '404';
    const titulo = eNaoEncontrado ? 'Ops! Essa rota não existe.' : 'Ops! Algo saiu dos trilhos.';
    const descricao = eNaoEncontrado
        ? 'A página que você tentou acessar não foi encontrada. Ela pode ter mudado de endereço ou nunca ter existido.'
        : 'Algo inesperado aconteceu durante o carregamento desta página. Tente voltar para o início e navegar novamente.';

    return (
        <main>
            <section
                aria-label="Página não encontrada"
                className="mx-auto flex max-w-[1300px] flex-col items-center gap-[2.4rem] p-[6rem_2.4rem_6.4rem] text-center mobile-lg:gap-[2.8rem] mobile-lg:p-[7.2rem_3.2rem_7.2rem] tablet:p-[8rem_6.4rem] desktop:p-[9.6rem_6.4rem_8.8rem]"
            >
                <TituloErro codigo={codigo} />

                <div className="flex flex-col gap-[1.2rem] mobile-lg:gap-[1.6rem]">
                    <h1 className="font-title text-[2.2rem] font-black leading-[1.2] text-title mobile-lg:text-[2.6rem] tablet:text-subtitle">
                        {titulo}
                    </h1>
                    <p className="mx-auto max-w-[50rem] font-text text-[1.5rem] leading-[1.7] text-text-dark mobile-lg:text-[1.6rem] tablet:text-body">
                        {descricao}
                    </p>
                </div>

                <BotaoPrimario to="/" className="mobile-lg:px-[4.4rem]">
                    Voltar para o início
                </BotaoPrimario>

                <LinksUteis links={LINKS_SUGERIDOS} />
            </section>
        </main>
    );
}
