import { useEffect, useState } from 'react';
import { NavLink } from 'react-router';
import type { LinkNavegacao } from '../../types/navegacao';

const LINKS_NAVEGACAO: LinkNavegacao[] = [
    { caminho: '/', rotulo: 'Início' },
    { caminho: '/sobre', rotulo: 'Sobre' },
    { caminho: '/missoes', rotulo: 'Missões' },
    { caminho: '/integrantes', rotulo: 'Integrantes' },
    { caminho: '/faq', rotulo: 'FAQ' },
    { caminho: '/contato', rotulo: 'Contato' },
    { caminho: '/painel', rotulo: 'Painel Zyra' },
];

export default function Cabecalho() {
    const [menuAberto, setMenuAberto] = useState(false);

    useEffect(() => {
        if (!menuAberto) {
            return;
        }

        function fecharComEsc(evento: KeyboardEvent) {
            if (evento.key === 'Escape') {
                setMenuAberto(false);
            }
        }

        window.addEventListener('keydown', fecharComEsc);
        return () => window.removeEventListener('keydown', fecharComEsc);
    }, [menuAberto]);

    function alternarMenu() {
        setMenuAberto((atual) => !atual);
    }

    return (
        <header className="sticky top-0 z-50 flex items-center justify-between border-b border-separator-light bg-bg px-6 py-[1.8rem] mobile-lg:px-8 tablet:px-12 desktop:justify-around desktop:px-24">
            <NavLink to="/" onClick={() => setMenuAberto(false)}>
                <img
                    src="/img/zyra.png"
                    alt="Logo Zyra"
                    className="h-[3.4rem] w-auto mobile-lg:h-[3.8rem] tablet:h-[4.2rem] desktop:h-[5rem]"
                />
            </NavLink>

            {/* Botão hambúrguer */}
            <button
                type="button"
                onClick={alternarMenu}
                aria-label={menuAberto ? 'Fechar menu de navegação' : 'Abrir menu de navegação'}
                aria-expanded={menuAberto}
                aria-controls="menu-principal"
                className="z-50 flex h-[2rem] w-[2.8rem] flex-col justify-between max-[480px]:h-[1.8rem] max-[480px]:w-[2.4rem] desktop:hidden"
            >
                <span
                    className={`block h-[2px] w-full rounded-full bg-nav transition-transform duration-300 ${
                        menuAberto ? 'translate-y-[9px] rotate-45 max-[480px]:translate-y-[8px]' : ''
                    }`}
                />
                <span
                    className={`block h-[2px] w-full rounded-full bg-nav transition-all duration-200 ${
                        menuAberto ? 'scale-x-0 opacity-0' : ''
                    }`}
                />
                <span
                    className={`block h-[2px] w-full rounded-full bg-nav transition-transform duration-300 ${
                        menuAberto ? '-translate-y-[9px] -rotate-45 max-[480px]:-translate-y-[8px]' : ''
                    }`}
                />
            </button>

            <nav
                id="menu-principal"
                aria-label="Navegação principal"
                className={`absolute left-0 top-full w-full overflow-hidden border-b border-separator-light bg-bg shadow-lg transition-[max-height,opacity] duration-300 ${
                    menuAberto ? 'max-h-[40rem] opacity-100' : 'pointer-events-none max-h-0 opacity-0'
                } desktop:static desktop:max-h-none desktop:w-auto desktop:overflow-visible desktop:border-none desktop:opacity-100 desktop:shadow-none desktop:pointer-events-auto`}
            >
                <ul className="flex flex-col desktop:flex-row desktop:items-center desktop:gap-10">
                    {LINKS_NAVEGACAO.map((link) => (
                        <li
                            key={link.caminho}
                            className="w-full border-b border-separator-light last:border-b-0 desktop:w-auto desktop:border-none"
                        >
                            <NavLink
                                to={link.caminho}
                                end={link.caminho === '/'}
                                onClick={() => setMenuAberto(false)}
                                className={({ isActive }) =>
                                    `relative block px-6 py-[1.4rem] text-[1.6rem] text-nav transition-colors duration-200 desktop:inline-block desktop:w-auto desktop:px-0 desktop:pb-[0.7rem] desktop:after:absolute desktop:after:bottom-0 desktop:after:left-0 desktop:after:h-[2px] desktop:after:w-full desktop:after:origin-left desktop:after:scale-y-0 desktop:after:bg-hover desktop:after:opacity-0 desktop:after:transition-all desktop:after:duration-200 desktop:hover:after:scale-y-100 desktop:hover:after:opacity-100 ${
                                        isActive
                                            ? 'font-bold text-hover desktop:font-normal desktop:text-nav desktop:after:scale-y-100 desktop:after:opacity-100'
                                            : ''
                                    }`
                                }
                            >
                                {link.rotulo}
                            </NavLink>
                        </li>
                    ))}
                </ul>
            </nav>
        </header>
    );
}