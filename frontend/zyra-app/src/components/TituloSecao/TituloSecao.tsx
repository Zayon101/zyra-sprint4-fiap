type TituloSecaoProps = {
    titulo: string;
    nivel?: 'h1' | 'h2';
};

export default function TituloSecao({ titulo, nivel = 'h2' }: TituloSecaoProps) {
    const Titulo = nivel;

    return (
        <>
            <Titulo className="mb-[1rem] text-center font-text text-subtitle font-medium text-title">{titulo}</Titulo>
            <div className="mx-auto mb-[5.2rem] h-[0.2rem] w-[8rem] bg-separator-dark" aria-hidden="true" />
        </>
    );
}
