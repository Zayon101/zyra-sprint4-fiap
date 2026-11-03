type CabecalhoPaginaProps = {
    titulo: string;
    descricao?: string;
};

export default function CabecalhoPagina({ titulo, descricao }: CabecalhoPaginaProps) {
    return (
        <div className={`text-center ${descricao ? 'mb-[4rem]' : 'mb-[5.2rem]'}`}>
            <h1 className="mb-[1.2rem] font-title text-subtitle font-bold text-title">{titulo}</h1>
            <div className="mx-auto h-[0.2rem] w-[8rem] bg-separator-dark" aria-hidden="true" />
            {descricao && (
                <p className="mx-auto mt-[2rem] max-w-[70rem] font-text text-body leading-[1.7] text-text-dark">
                    {descricao}
                </p>
            )}
        </div>
    );
}
