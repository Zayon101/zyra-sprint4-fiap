type MensagemRetornoProps = {
    tipo: 'sucesso' | 'erro';
    texto: string;
};

export default function MensagemRetorno({ tipo, texto }: MensagemRetornoProps) {
    const estilos =
        tipo === 'sucesso'
            ? 'border-[#c3e6cb] bg-[#d4edda] text-[#155724]'
            : 'border-[#f5c6cb] bg-[#f8d7da] text-[#721c24]';

    return (
        <div
            role="status"
            aria-live="polite"
            className={`mx-auto mb-[2.4rem] max-w-[76rem] rounded-[0.8rem] border-[1.5px] p-[1.4rem_2.4rem] text-center font-text text-[1.5rem] font-medium ${estilos}`}
        >
            {texto}
        </div>
    );
}
