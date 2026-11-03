import type { ReactNode } from 'react';
import { Link } from 'react-router';

type BotaoPrimarioProps = {
    to: string;
    children: ReactNode;
    className?: string;
};

export default function BotaoPrimario({ to, children, className = '' }: BotaoPrimarioProps) {
    return (
        <Link
            to={to}
            className={`inline-block rounded-lg bg-button-pink px-[3.6rem] py-[1.4rem] text-center text-[1.6rem] font-semibold text-white shadow-[0_2px_8px_rgba(154,74,97,0.25)] transition-[transform,box-shadow] duration-300 hover:scale-[1.06] hover:shadow-[0_6px_20px_rgba(154,74,97,0.35)] ${className}`}
        >
            {children}
        </Link>
    );
}