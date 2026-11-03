import { NavLink } from 'react-router';
import type { LinkNavegacao } from '../../types/navegacao';

type ColunaRodape = {
    titulo: string;
    links: LinkNavegacao[];
};

const COLUNAS_RODAPE: ColunaRodape[] = [
    {
        titulo: 'Projeto:',
        links: [
            { caminho: '/', rotulo: 'Início' },
            { caminho: '/sobre', rotulo: 'Sobre' },
            { caminho: '/missoes', rotulo: 'Missões' },
            { caminho: '/faq', rotulo: 'FAQ' },
        ],
    },
    {
        titulo: 'Equipe:',
        links: [
            { caminho: '/integrantes', rotulo: 'Integrantes' },
            { caminho: '/contato', rotulo: 'Contato' },
        ],
    },
];

export default function Rodape() {
    return (
        <footer className="mt-auto flex flex-col items-center gap-8 bg-footer px-6 py-10 text-center text-text-light-yellow mobile-lg:px-8 tablet:flex-row tablet:items-start tablet:justify-center tablet:gap-10 tablet:text-left desktop:justify-start desktop:gap-32 desktop:px-24">
            <img src="/img/zyra-inv.png" alt="Logo Zyra" className="h-[4rem] w-auto mobile-lg:h-[4.4rem] desktop:h-[5rem]" />

            <nav
                aria-label="Navegação do rodapé"
                className="flex flex-wrap justify-center gap-10 desktop:gap-24"
            >
                {COLUNAS_RODAPE.map((coluna) => (
                    <div key={coluna.titulo} className="flex min-w-[12rem] flex-col items-center gap-3 tablet:items-start">
                        <h2 className="text-[1.5rem] font-extrabold text-text-light-yellow">{coluna.titulo}</h2>
                        <ul className="flex flex-col items-center gap-2 tablet:items-start">
                            {coluna.links.map((link) => (
                                <li key={link.caminho}>
                                    <NavLink
                                        to={link.caminho}
                                        className="text-[1.2rem] font-normal text-text-light-yellow transition-colors duration-200 hover:text-hover"
                                    >
                                        {link.rotulo}
                                    </NavLink>
                                </li>
                            ))}
                        </ul>
                    </div>
                ))}
            </nav>
        </footer>
    );
}
