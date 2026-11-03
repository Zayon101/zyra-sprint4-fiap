import type { LinkNavegacao } from '../../types/navegacao';
import LinkSeta from '../LinkSeta/LinkSeta';

type LinksUteisProps = {
    titulo?: string;
    links: LinkNavegacao[];
};

export default function LinksUteis({ titulo = 'Ou explore:', links }: LinksUteisProps) {
    return (
        <div className="flex flex-col items-center gap-[1.2rem] tablet:gap-[1.6rem]">
            <p className="font-text text-[1.3rem] font-semibold text-text-dark tablet:text-[1.4rem]">{titulo}</p>
            <ul className="flex flex-col items-center gap-[1rem] mobile-lg:flex-row mobile-lg:flex-wrap mobile-lg:justify-center mobile-lg:gap-x-[2.4rem] mobile-lg:gap-y-[1.2rem]">
                {links.map((link) => (
                    <li key={link.caminho}>
                        <LinkSeta to={link.caminho}>{link.rotulo}</LinkSeta>
                    </li>
                ))}
            </ul>
        </div>
    );
}
